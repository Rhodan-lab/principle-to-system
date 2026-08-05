import assert from 'node:assert/strict';
import {
  generateKeyPairSync,
  sign as signRaw,
} from 'node:crypto';
import {
  chmod,
  mkdtemp,
  readFile,
  symlink,
  writeFile,
} from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import {
  CATALOG_CONTRACT,
  OIDC_POLICY_CONTRACT,
  PRODUCT,
  TENANT_CONTRACT,
  canonicalJson,
  createAuditLogger,
  createControlPlaneServer,
  createFileOidcJwksProvider,
  createMemoryAuthState,
  createOidcVerifier,
  createRemoteOidcJwksProvider,
  createStaticOidcJwksProvider,
  exchangeIdentityAssertion,
  mintOidcIdentityAssertion,
  sealOidcPolicy,
  sealTenantConfig,
  sha256Hex,
  verifyOidcJwks,
  verifyOidcPolicy,
  verifyOidcTenantCompatibility,
} from '../principia_atlas/hosted/index.mjs';

const now = 1_800_000_000;
const identitySecret = 'identity-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const sessionSecret = 'session-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const issuer = 'https://identity.example.test';
const audience = 'principia-atlas-external';
const jwksUri = 'https://identity.example.test/.well-known/jwks.json';
const rsa = generateKeyPairSync('rsa', { modulusLength: 2048 });
const rsa2 = generateKeyPairSync('rsa', { modulusLength: 2048 });
const ec = generateKeyPairSync('ec', { namedCurve: 'P-256' });

function seal(unsigned, field) {
  return { ...unsigned, [field]: sha256Hex(canonicalJson(unsigned)) };
}

function tenantConfig() {
  return sealTenantConfig({
    contract: TENANT_CONTRACT,
    product: PRODUCT,
    identity: {
      issuer: 'https://identity.internal.test',
      audience: 'principia-atlas-hosted',
      max_assertion_ttl_seconds: 300,
    },
    session: { cookie_name: 'pa_session', ttl_seconds: 3600, secure: false },
    tenants: {
      'school-demo': {
        display_name: 'School Demo',
        allowed_channels: ['alpha'],
        allowed_routes: ['distributed-information'],
        pinned_versions: [],
      },
    },
  });
}

function catalog() {
  const version = '0.1.0-alpha.1';
  const release = {
    tag: `principia-atlas-v${version}`,
    channel: 'alpha',
    promotion_id: 'a'.repeat(64),
    release: {
      release_id: 'b'.repeat(64),
      bundle_id: 'c'.repeat(64),
      receipt_id: 'd'.repeat(64),
      route_id: 'distributed-information',
      archive: {
        name: `principia-atlas-${version}.zip`,
        sha256: 'e'.repeat(64),
        checksum_name: `principia-atlas-${version}.zip.sha256`,
      },
    },
    sources: {
      principia: { repository: 'Rhodan-lab/principle-to-system', commit: '1'.repeat(40) },
      atlas: { repository: 'Rhodan-lab/Atlas', commit: '2'.repeat(40) },
    },
    compatibility: {
      release_contract: 'principia-atlas-release/0.1',
      route_id: 'distributed-information',
      entrypoints: {
        verify: 'launcher.py verify',
        run: 'launcher.py run',
        linux_macos: 'launch.sh',
        macos_double_click: 'launch.command',
        windows: 'launch.cmd',
      },
      runtime: { host: '127.0.0.1', external_network_required: false, python: '>=3.10' },
      boundaries: {
        authorities_separate: true,
        status_inheritance: 'prohibited',
        live_cross_repository_dependency: false,
        canonical_mutation: false,
      },
    },
  };
  return seal({
    contract: CATALOG_CONTRACT,
    product: PRODUCT,
    release_count: 1,
    releases: { [version]: release },
    channels: {
      alpha: { version, tag: release.tag, promotion_id: release.promotion_id },
      beta: null,
      stable: null,
    },
  }, 'catalog_id');
}

function policy(overrides = {}) {
  const unsigned = {
    contract: OIDC_POLICY_CONTRACT,
    product: PRODUCT,
    issuer,
    audience,
    authorized_party: null,
    jwks: {
      uri: jwksUri,
      allowed_algorithms: ['RS256', 'ES256'],
      cache_ttl_seconds: 300,
      fetch_timeout_ms: 2000,
      max_bytes: 65536,
    },
    token: {
      max_ttl_seconds: 3600,
      clock_skew_seconds: 30,
      internal_assertion_ttl_seconds: 180,
      require_iat: true,
      require_email_verified: true,
    },
    claims: {
      tenant: {
        name: 'organization',
        values: { 'external-school': 'school-demo' },
      },
      roles: {
        name: 'groups',
        values: { students: 'learner', teachers: 'facilitator' },
        reject_unmapped: true,
      },
      required: { assurance: 'mfa' },
    },
    ...overrides,
  };
  return sealOidcPolicy(unsigned);
}

function publicRsaJwk(pair = rsa, kid = 'rsa-1') {
  const value = pair.publicKey.export({ format: 'jwk' });
  return { kty: 'RSA', kid, use: 'sig', key_ops: ['verify'], alg: 'RS256', n: value.n, e: value.e };
}

function publicEcJwk() {
  const value = ec.publicKey.export({ format: 'jwk' });
  return { kty: 'EC', kid: 'ec-1', use: 'sig', key_ops: ['verify'], alg: 'ES256', crv: value.crv, x: value.x, y: value.y };
}

function jwks(...keys) {
  return { keys: keys.length ? keys : [publicRsaJwk(), publicEcJwk()] };
}

function encode(value) {
  const raw = typeof value === 'string' ? value : canonicalJson(value).trimEnd();
  return Buffer.from(raw, 'utf8').toString('base64url');
}

function tokenPayload(overrides = {}) {
  return {
    iss: issuer,
    aud: audience,
    sub: 'learner-1',
    organization: 'external-school',
    groups: ['students'],
    assurance: 'mfa',
    email_verified: true,
    iat: now - 10,
    exp: now + 300,
    ...overrides,
  };
}

function signJwt({ payload = tokenPayload(), header = { alg: 'RS256', kid: 'rsa-1', typ: 'JWT' }, privateKey = rsa.privateKey, rawHeader = null, rawPayload = null } = {}) {
  const head = encode(rawHeader ?? header);
  const body = encode(rawPayload ?? payload);
  const signing = `${head}.${body}`;
  const options = header.alg === 'ES256'
    ? { key: privateKey, dsaEncoding: 'ieee-p1363' }
    : privateKey;
  const signature = signRaw(header.alg === 'ES256' ? 'sha256' : 'RSA-SHA256', Buffer.from(signing, 'ascii'), options).toString('base64url');
  return `${signing}.${signature}`;
}

async function verifierFor(jwksInput = jwks(), policyInput = policy()) {
  const provider = createStaticOidcJwksProvider(jwksInput, policyInput);
  const verifier = createOidcVerifier({ policy: policyInput, provider });
  await verifier.initialize();
  return verifier;
}

function mockResponse(body, { url = jwksUri, status = 200, contentType = 'application/jwk-set+json', cacheControl = 'max-age=60', redirected = false } = {}) {
  const raw = Buffer.from(canonicalJson(body));
  return {
    status,
    url,
    redirected,
    body: null,
    headers: {
      get(name) {
        const key = String(name).toLowerCase();
        if (key === 'content-type') return contentType;
        if (key === 'content-length') return String(raw.length);
        if (key === 'cache-control') return cacheControl;
        return null;
      },
    },
    async arrayBuffer() { return raw; },
  };
}

test('sealed OIDC policy is tenant compatible and tamper evident', () => {
  const value = policy();
  assert.equal(verifyOidcPolicy(value).policy_id, value.policy_id);
  assert.equal(verifyOidcTenantCompatibility(value, tenantConfig()).policy.policy_id, value.policy_id);
  assert.throws(() => verifyOidcPolicy({ ...value, audience: 'changed' }), /seal/);
  assert.throws(() => policy({ issuer: 'http://identity.example.test' }), /HTTPS/);
  assert.throws(() => policy({ issuer: 'https://127.0.0.1' }), /host/);
  const unavailable = policy({
    claims: {
      tenant: { name: 'organization', values: { 'external-school': 'missing-tenant' } },
      roles: { name: 'groups', values: { students: 'learner' }, reject_unmapped: true },
      required: { assurance: 'mfa' },
    },
  });
  assert.throws(() => verifyOidcTenantCompatibility(unavailable, tenantConfig()), /unavailable tenant/);
});

test('RS256 token maps to pairwise tenant principal and valid internal assertion', async () => {
  const verifier = await verifierFor();
  const token = signJwt();
  const principal = await verifier.verify(token, now);
  assert.equal(principal.tenant_id, 'school-demo');
  assert.deepEqual(principal.roles, ['learner']);
  assert.match(principal.sub, /^oidc:[A-Za-z0-9_-]{43}$/);
  assert.equal(principal.sub.includes('learner-1'), false);
  assert.match(principal.token_id, /^[A-Za-z0-9_-]{43}$/);
  const assertion = mintOidcIdentityAssertion(principal, identitySecret, tenantConfig(), verifier.policy, now);
  const exchanged = exchangeIdentityAssertion(assertion, identitySecret, sessionSecret, tenantConfig(), now, () => 'session_identifier_1234567890');
  assert.equal(exchanged.session.sub, principal.sub);
  assert.equal(exchanged.session.tenant_id, 'school-demo');
  assert.deepEqual(exchanged.session.roles, ['learner']);
  assert.equal(exchanged.assertion.jti, principal.token_id);
});

test('ES256 token uses fixed-width P-1363 signatures', async () => {
  const verifier = await verifierFor();
  const token = signJwt({
    header: { alg: 'ES256', kid: 'ec-1', typ: 'JWT' },
    privateKey: ec.privateKey,
  });
  const principal = await verifier.verify(token, now);
  assert.equal(principal.tenant_id, 'school-demo');
  assert.deepEqual(principal.roles, ['learner']);
  const parts = token.split('.');
  assert.equal(Buffer.from(parts[2], 'base64url').length, 64);
});

test('signature algorithm key identifier and canonical JSON fail closed', async () => {
  const verifier = await verifierFor();
  const token = signJwt();
  const parts = token.split('.');
  const replacement = parts[2].endsWith('A') ? 'B' : 'A';
  await assert.rejects(() => verifier.verify(`${parts[0]}.${parts[1]}.${parts[2].slice(0, -1)}${replacement}`, now), /signature|base64url/);
  await assert.rejects(() => verifier.verify(signJwt({ header: { alg: 'none', kid: 'rsa-1' } }), now), /algorithm/);
  await assert.rejects(() => verifier.verify(signJwt({ header: { alg: 'RS256', kid: 'unknown' } }), now), /unavailable/);
  await assert.rejects(() => verifier.verify(signJwt({ rawHeader: '{"alg":"RS256","alg":"RS256","kid":"rsa-1"}' }), now), /duplicate key/);
  await assert.rejects(() => verifier.verify(signJwt({ header: { alg: 'RS256', kid: 'rsa-1', jku: 'https://attacker.test/jwks' } }), now), /header fields/);
  await assert.rejects(() => verifier.verify(signJwt({ rawPayload: '{"iss":"https://identity.example.test","__proto__":{},"aud":"principia-atlas-external"}' }), now), /reserved object key/);
});

test('issuer audience authorized-party time and required claims fail closed', async () => {
  const verifier = await verifierFor();
  await assert.rejects(() => verifier.verify(signJwt({ payload: tokenPayload({ iss: 'https://other.example.test' }) }), now), /issuer/);
  await assert.rejects(() => verifier.verify(signJwt({ payload: tokenPayload({ aud: 'other' }) }), now), /audience/);
  await assert.rejects(() => verifier.verify(signJwt({ payload: tokenPayload({ aud: [audience, 'other'], azp: 'wrong' }) }), now), /authorized party/);
  assert.equal((await verifier.verify(signJwt({ payload: tokenPayload({ aud: [audience, 'other'], azp: audience }) }), now)).tenant_id, 'school-demo');
  await assert.rejects(() => verifier.verify(signJwt({ payload: tokenPayload({ exp: now - 31 }) }), now), /expired/);
  await assert.rejects(() => verifier.verify(signJwt({ payload: tokenPayload({ nbf: now + 31 }) }), now), /not active/);
  await assert.rejects(() => verifier.verify(signJwt({ payload: tokenPayload({ iat: now - 4000, exp: now + 1 }) }), now), /time boundary/);
  await assert.rejects(() => verifier.verify(signJwt({ payload: tokenPayload({ email_verified: false }) }), now), /email verification/);
  await assert.rejects(() => verifier.verify(signJwt({ payload: tokenPayload({ assurance: 'password' }) }), now), /required claim/);
});

test('tenant and role mappings never trust unmapped external values', async () => {
  const verifier = await verifierFor();
  await assert.rejects(() => verifier.verify(signJwt({ payload: tokenPayload({ organization: 'unknown' }) }), now), /tenant claim/);
  await assert.rejects(() => verifier.verify(signJwt({ payload: tokenPayload({ groups: ['unknown'] }) }), now), /unmapped/);
  const principal = await verifier.verify(signJwt({ payload: tokenPayload({ groups: ['teachers', 'students'] }) }), now);
  assert.deepEqual(principal.roles, ['facilitator', 'learner']);
  const permissive = policy({
    claims: {
      tenant: { name: 'organization', values: { 'external-school': 'school-demo' } },
      roles: { name: 'groups', values: { students: 'learner' }, reject_unmapped: false },
      required: { assurance: 'mfa' },
    },
  });
  const permissiveVerifier = await verifierFor(jwks(), permissive);
  assert.deepEqual((await permissiveVerifier.verify(signJwt({ payload: tokenPayload({ groups: ['unknown', 'students'] }) }), now)).roles, ['learner']);
});

test('JWKS validation rejects private weak ambiguous and duplicate keys', () => {
  const value = policy();
  const privateJwk = rsa.privateKey.export({ format: 'jwk' });
  assert.throws(() => verifyOidcJwks({ keys: [{ ...publicRsaJwk(), d: privateJwk.d }] }, value), /private material|fields/);
  const weak = generateKeyPairSync('rsa', { modulusLength: 1024 }).publicKey.export({ format: 'jwk' });
  assert.throws(() => verifyOidcJwks({ keys: [{ kty: 'RSA', kid: 'weak', use: 'sig', alg: 'RS256', n: weak.n, e: weak.e }] }, value), /too weak/);
  assert.throws(() => verifyOidcJwks({ keys: [publicRsaJwk(), publicRsaJwk()] }, value), /duplicate/);
  assert.throws(() => verifyOidcJwks({ keys: [{ ...publicEcJwk(), crv: 'P-384' }] }, value), /boundary/);
});

test('remote JWKS provider caches and refreshes once for key rotation', async () => {
  let calls = 0;
  let clock = 1000;
  const responses = [
    mockResponse(jwks(publicRsaJwk(rsa, 'rsa-1'))),
    mockResponse(jwks(publicRsaJwk(rsa2, 'rsa-2'))),
  ];
  const provider = createRemoteOidcJwksProvider(policy(), {
    nowMs: () => clock,
    fetchImpl: async (_url, options) => {
      assert.equal(options.redirect, 'error');
      const response = responses[Math.min(calls, responses.length - 1)];
      calls += 1;
      return response;
    },
  });
  const verifier = createOidcVerifier({ policy: policy(), provider });
  await verifier.initialize();
  assert.equal(calls, 1);
  const rotated = signJwt({ header: { alg: 'RS256', kid: 'rsa-2', typ: 'JWT' }, privateKey: rsa2.privateKey });
  assert.equal((await verifier.verify(rotated, now)).tenant_id, 'school-demo');
  assert.equal(calls, 2);
  assert.equal((await verifier.verify(rotated, now)).tenant_id, 'school-demo');
  assert.equal(calls, 2);
  clock += 61_000;
  assert.equal(provider.health().status, 'not_ready');
});

test('remote JWKS provider rejects redirects content type and oversized bodies', async () => {
  const base = policy();
  const redirect = createRemoteOidcJwksProvider(base, { fetchImpl: async () => mockResponse(jwks(), { redirected: true }) });
  await assert.rejects(() => redirect.initialize(), /response/);
  const html = createRemoteOidcJwksProvider(base, { fetchImpl: async () => mockResponse(jwks(), { contentType: 'text/html' }) });
  await assert.rejects(() => html.initialize(), /content type/);
  const small = policy({ jwks: { ...base.jwks, max_bytes: 1024 } });
  const oversized = createRemoteOidcJwksProvider(small, {
    fetchImpl: async () => ({
      ...mockResponse(jwks()),
      headers: { get(name) { return String(name).toLowerCase() === 'content-length' ? '2048' : 'application/json'; } },
    }),
  });
  await assert.rejects(() => oversized.initialize(), /resource limit/);
});

test('file JWKS provider rejects symlinks and respects policy resource limits', async () => {
  const root = await mkdtemp(join(tmpdir(), 'principia-oidc-jwks-'));
  const path = join(root, 'jwks.json');
  await writeFile(path, canonicalJson(jwks()), { mode: 0o600 });
  const provider = await createFileOidcJwksProvider(path, policy());
  assert.equal((await provider.initialize()).kind, 'static');
  const linked = join(root, 'linked.json');
  try {
    await symlink(path, linked);
    await assert.rejects(() => createFileOidcJwksProvider(linked, policy()), /regular file/);
  } catch (error) {
    if (error?.code !== 'EPERM') throw error;
  }
  await chmod(path, 0o600);
  const constrained = policy({ jwks: { ...policy().jwks, max_bytes: 1024 } });
  await writeFile(path, 'x'.repeat(2048), { mode: 0o600 });
  await assert.rejects(() => createFileOidcJwksProvider(path, constrained), /resource limit/);
});

test('OIDC endpoint creates revocable session and rejects token replay', async () => {
  const verifier = await verifierFor();
  const root = await mkdtemp(join(tmpdir(), 'principia-oidc-audit-'));
  const auditPath = join(root, 'audit.ndjson');
  const audit = createAuditLogger({ path: auditPath, instanceId: 'oidc-test', now: () => now });
  const authState = createMemoryAuthState();
  const server = createControlPlaneServer({
    catalog: catalog(),
    config: tenantConfig(),
    authState,
    identitySecret,
    sessionSecret,
    oidcVerifier: verifier,
    audit,
    now: () => now,
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const address = server.address();
  const base = `http://127.0.0.1:${address.port}`;
  const token = signJwt();
  try {
    const health = await fetch(`${base}/healthz`);
    assert.equal(health.status, 200);
    assert.deepEqual((await health.json()).oidc, {
      enabled: true,
      contract: 'principia-atlas-hosted-oidc-verifier/0.1',
      policy_id: verifier.policy.policy_id,
      jwks_kind: 'static',
    });
    const ready = await fetch(`${base}/readyz`);
    assert.equal(ready.status, 200);
    assert.equal((await ready.json()).oidc.status, 'ok');
    const exchange = await fetch(`${base}/api/auth/oidc`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, Origin: base },
    });
    assert.equal(exchange.status, 200);
    const cookie = exchange.headers.get('set-cookie').split(';')[0];
    const session = await fetch(`${base}/api/session`, { headers: { Cookie: cookie } });
    assert.equal(session.status, 200);
    assert.equal((await session.json()).tenant_id, 'school-demo');
    const replay = await fetch(`${base}/api/auth/oidc`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, Origin: base },
    });
    assert.equal(replay.status, 401);
  } finally {
    await new Promise((resolve) => server.close(resolve));
    authState.close();
    audit.close();
  }
  const log = await readFile(auditPath, 'utf8');
  assert.equal(log.includes(token), false);
  assert.equal(log.includes('learner-1'), false);
  assert.match(log, /"event":"auth\.oidc"/);
});

test('OIDC endpoint is absent unless an initialized verifier is configured', async () => {
  const server = createControlPlaneServer({
    catalog: catalog(),
    config: tenantConfig(),
    identitySecret,
    sessionSecret,
    now: () => now,
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  try {
    const address = server.address();
    const base = `http://127.0.0.1:${address.port}`;
    const response = await fetch(`${base}/api/auth/oidc`, { method: 'POST', headers: { Origin: base } });
    assert.equal(response.status, 404);
    assert.deepEqual((await (await fetch(`${base}/healthz`)).json()).oidc, { enabled: false });
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});
