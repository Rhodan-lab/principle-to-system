import assert from 'node:assert/strict';
import { generateKeyPairSync, sign as signRaw } from 'node:crypto';
import { mkdtemp, readFile, symlink, writeFile } from 'node:fs/promises';
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
  createStaticOidcJwksProvider,
  sealOidcPolicy,
  sealTenantConfig,
  sha256Hex,
  verifyOidcPolicy,
  verifyOidcTenantCompatibility,
} from '../principia_atlas/hosted/index.mjs';

const now = 1_800_000_000;
const issuer = 'https://identity.example.test';
const audience = 'principia-atlas-external';
const identitySecret = 'identity-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const sessionSecret = 'session-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const rsa = generateKeyPairSync('rsa', { modulusLength: 2048 });
const ec = generateKeyPairSync('ec', { namedCurve: 'P-256' });

function seal(unsigned, field) {
  return { ...unsigned, [field]: sha256Hex(canonicalJson(unsigned)) };
}

function config() {
  return sealTenantConfig({
    contract: TENANT_CONTRACT,
    product: PRODUCT,
    identity: { issuer: 'https://identity.internal.test', audience: 'principia-atlas-hosted', max_assertion_ttl_seconds: 300 },
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
      release_id: 'b'.repeat(64), bundle_id: 'c'.repeat(64), receipt_id: 'd'.repeat(64),
      route_id: 'distributed-information',
      archive: { name: `principia-atlas-${version}.zip`, sha256: 'e'.repeat(64), checksum_name: `principia-atlas-${version}.zip.sha256` },
    },
    sources: {
      principia: { repository: 'Rhodan-lab/principle-to-system', commit: '1'.repeat(40) },
      atlas: { repository: 'Rhodan-lab/Atlas', commit: '2'.repeat(40) },
    },
    compatibility: {
      release_contract: 'principia-atlas-release/0.1',
      route_id: 'distributed-information',
      entrypoints: { verify: 'launcher.py verify', run: 'launcher.py run', linux_macos: 'launch.sh', macos_double_click: 'launch.command', windows: 'launch.cmd' },
      runtime: { host: '127.0.0.1', external_network_required: false, python: '>=3.10' },
      boundaries: { authorities_separate: true, status_inheritance: 'prohibited', live_cross_repository_dependency: false, canonical_mutation: false },
    },
  };
  return seal({
    contract: CATALOG_CONTRACT,
    product: PRODUCT,
    release_count: 1,
    releases: { [version]: release },
    channels: { alpha: { version, tag: release.tag, promotion_id: release.promotion_id }, beta: null, stable: null },
  }, 'catalog_id');
}

function policy(overrides = {}) {
  return sealOidcPolicy({
    contract: OIDC_POLICY_CONTRACT,
    product: PRODUCT,
    issuer,
    audience,
    authorized_party: null,
    jwks: {
      uri: 'https://identity.example.test/.well-known/jwks.json',
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
      tenant: { name: 'organization', values: { 'external-school': 'school-demo' } },
      roles: { name: 'groups', values: { students: 'learner', teachers: 'facilitator' }, reject_unmapped: true },
      required: { assurance: 'mfa' },
    },
    ...overrides,
  });
}

function publicJwks() {
  const rsaJwk = rsa.publicKey.export({ format: 'jwk' });
  const ecJwk = ec.publicKey.export({ format: 'jwk' });
  return {
    keys: [
      { kty: 'RSA', kid: 'rsa-1', use: 'sig', key_ops: ['verify'], alg: 'RS256', n: rsaJwk.n, e: rsaJwk.e },
      { kty: 'EC', kid: 'ec-1', use: 'sig', key_ops: ['verify'], alg: 'ES256', crv: ecJwk.crv, x: ecJwk.x, y: ecJwk.y },
    ],
  };
}

function encode(value) {
  return Buffer.from(canonicalJson(value).trimEnd(), 'utf8').toString('base64url');
}

function signJwt(algorithm = 'RS256') {
  const header = { alg: algorithm, kid: algorithm === 'RS256' ? 'rsa-1' : 'ec-1', typ: 'JWT' };
  const payload = {
    iss: issuer,
    aud: audience,
    sub: 'learner-1',
    organization: 'external-school',
    groups: ['students'],
    assurance: 'mfa',
    email_verified: true,
    iat: now - 10,
    exp: now + 300,
  };
  const signing = `${encode(header)}.${encode(payload)}`;
  const signature = algorithm === 'RS256'
    ? signRaw('RSA-SHA256', Buffer.from(signing, 'ascii'), rsa.privateKey)
    : signRaw('sha256', Buffer.from(signing, 'ascii'), { key: ec.privateKey, dsaEncoding: 'ieee-p1363' });
  return `${signing}.${signature.toString('base64url')}`;
}

async function verifier() {
  const value = policy();
  const provider = createStaticOidcJwksProvider(publicJwks(), value);
  const output = createOidcVerifier({ policy: value, provider });
  await output.initialize();
  return output;
}

test('policy validation rejects invalid issuer after sealing and tenant drift', () => {
  const value = policy();
  assert.equal(verifyOidcPolicy(value).policy_id, value.policy_id);
  assert.equal(verifyOidcTenantCompatibility(value, config()).policy.policy_id, value.policy_id);
  assert.throws(() => verifyOidcPolicy(policy({ issuer: 'http://identity.example.test' })), /HTTPS/);
  const drift = policy({
    claims: {
      tenant: { name: 'organization', values: { 'external-school': 'missing-tenant' } },
      roles: { name: 'groups', values: { students: 'learner' }, reject_unmapped: true },
      required: { assurance: 'mfa' },
    },
  });
  assert.throws(() => verifyOidcTenantCompatibility(drift, config()), /unavailable tenant/);
});

test('ES256 verifier accepts fixed-width P-1363 signature and pairwise subject', async () => {
  const output = await verifier();
  const principal = await output.verify(signJwt('ES256'), now);
  assert.equal(principal.tenant_id, 'school-demo');
  assert.deepEqual(principal.roles, ['learner']);
  assert.match(principal.sub, /^oidc:[A-Za-z0-9_-]{43}$/);
  assert.equal(principal.sub.includes('learner-1'), false);
});

test('strict JSON rejects prototype-sensitive JWT payload keys', async () => {
  const output = await verifier();
  const header = encode({ alg: 'RS256', kid: 'rsa-1' });
  const payload = Buffer.from('{"iss":"https://identity.example.test","__proto__":{},"aud":"principia-atlas-external"}', 'utf8').toString('base64url');
  const signing = `${header}.${payload}`;
  const signature = signRaw('RSA-SHA256', Buffer.from(signing, 'ascii'), rsa.privateKey).toString('base64url');
  await assert.rejects(() => output.verify(`${signing}.${signature}`, now), /reserved object key/);
});

test('file JWKS provider rejects symlinks', async () => {
  const root = await mkdtemp(join(tmpdir(), 'principia-oidc-file-'));
  const path = join(root, 'jwks.json');
  await writeFile(path, canonicalJson(publicJwks()), { mode: 0o600 });
  const provider = await createFileOidcJwksProvider(path, policy());
  assert.equal((await provider.initialize()).kind, 'static');
  const linked = join(root, 'linked.json');
  try {
    await symlink(path, linked);
    await assert.rejects(() => createFileOidcJwksProvider(linked, policy()), /regular file/);
  } catch (error) {
    if (error?.code !== 'EPERM') throw error;
  }
});

test('OIDC endpoint creates one session and rejects replay without logging token', async () => {
  const oidcVerifier = await verifier();
  const authState = createMemoryAuthState();
  const root = await mkdtemp(join(tmpdir(), 'principia-oidc-audit-'));
  const auditPath = join(root, 'audit.ndjson');
  const audit = createAuditLogger({ path: auditPath, instanceId: 'oidc-runtime', now: () => now });
  const server = createControlPlaneServer({
    catalog: catalog(),
    config: config(),
    authState,
    identitySecret,
    sessionSecret,
    oidcVerifier,
    audit,
    now: () => now,
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const address = server.address();
  const base = `http://127.0.0.1:${address.port}`;
  const token = signJwt('RS256');
  try {
    const health = await (await fetch(`${base}/healthz`)).json();
    assert.equal(health.contract, 'principia-atlas-hosted-health/0.4');
    assert.equal(health.oidc.enabled, true);
    const ready = await fetch(`${base}/readyz`);
    assert.equal(ready.status, 200);
    assert.equal((await ready.json()).oidc.status, 'ok');
    const first = await fetch(`${base}/api/auth/oidc`, { method: 'POST', headers: { Authorization: `Bearer ${token}`, Origin: base } });
    assert.equal(first.status, 200);
    const cookie = first.headers.get('set-cookie').split(';')[0];
    assert.equal((await fetch(`${base}/api/session`, { headers: { Cookie: cookie } })).status, 200);
    const replay = await fetch(`${base}/api/auth/oidc`, { method: 'POST', headers: { Authorization: `Bearer ${token}`, Origin: base } });
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

test('OIDC route and health dependency are absent when no verifier is configured', async () => {
  const server = createControlPlaneServer({ catalog: catalog(), config: config(), identitySecret, sessionSecret, now: () => now });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  try {
    const address = server.address();
    const base = `http://127.0.0.1:${address.port}`;
    assert.equal((await fetch(`${base}/api/auth/oidc`, { method: 'POST', headers: { Origin: base } })).status, 404);
    assert.deepEqual((await (await fetch(`${base}/healthz`)).json()).oidc, { enabled: false });
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});
