import assert from 'node:assert/strict';
import { generateKeyPairSync, sign as signRaw } from 'node:crypto';
import { spawn } from 'node:child_process';
import { chmod, mkdtemp, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import {
  OIDC_POLICY_CONTRACT,
  createMemoryAuthState,
  createOidcVerifier,
  createRemoteOidcJwksProvider,
  createStaticOidcJwksProvider,
  exchangeIdentityAssertion,
  mintOidcIdentityAssertion,
  sealOidcPolicy,
  sealTenantConfig,
  verifyOidcJwks,
  verifyOidcPolicy,
  verifyOidcTenantCompatibility,
} from '../principia_atlas/hosted/index.mjs';

const fixedNow = 1_800_000_000;
const identitySecret = 'identity-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const sessionSecret = 'session-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const issuer = 'https://identity.example.test';
const audience = 'principia-atlas-external';
const keyPair = generateKeyPairSync('rsa', { modulusLength: 2048 });
const publicJwk = keyPair.publicKey.export({ format: 'jwk' });

function tenantConfig() {
  return sealTenantConfig({
    contract: 'principia-atlas-hosted-tenants/0.1',
    product: 'Principia & Atlas',
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

function unsignedPolicy(overrides = {}) {
  return {
    contract: OIDC_POLICY_CONTRACT,
    product: 'Principia & Atlas',
    issuer,
    audience,
    authorized_party: null,
    jwks: {
      uri: `${issuer}/.well-known/jwks.json`,
      allowed_algorithms: ['RS256'],
      cache_ttl_seconds: 300,
      fetch_timeout_ms: 3000,
      max_bytes: 262144,
    },
    token: {
      max_ttl_seconds: 3600,
      clock_skew_seconds: 30,
      internal_assertion_ttl_seconds: 180,
      require_iat: true,
      require_email_verified: false,
    },
    claims: {
      tenant: { name: 'organization', values: { 'external-school': 'school-demo' } },
      roles: {
        name: 'groups',
        values: { students: 'learner', teachers: 'facilitator' },
        reject_unmapped: true,
      },
      required: {},
    },
    ...overrides,
  };
}

function policy(overrides = {}) {
  return sealOidcPolicy(unsignedPolicy(overrides));
}

function jwk(kid = 'rsa-key-1', pair = keyPair) {
  const value = pair.publicKey.export({ format: 'jwk' });
  return {
    kty: 'RSA',
    kid,
    use: 'sig',
    key_ops: ['verify'],
    alg: 'RS256',
    n: value.n,
    e: value.e,
  };
}

function jwks(entries = [jwk()]) {
  return { keys: entries };
}

function base64urlJson(value) {
  const raw = typeof value === 'string' ? value : JSON.stringify(value);
  return Buffer.from(raw, 'utf8').toString('base64url');
}

function signJwt({ payload = {}, header = {}, pair = keyPair, rawHeader = null } = {}) {
  const encodedHeader = base64urlJson(rawHeader ?? { alg: 'RS256', kid: 'rsa-key-1', typ: 'JWT', ...header });
  const encodedPayload = base64urlJson({
    iss: issuer,
    aud: audience,
    sub: 'learner-1',
    organization: 'external-school',
    groups: ['students'],
    iat: fixedNow - 10,
    exp: fixedNow + 300,
    ...payload,
  });
  const signingInput = `${encodedHeader}.${encodedPayload}`;
  const signature = signRaw('RSA-SHA256', Buffer.from(signingInput, 'ascii'), pair.privateKey).toString('base64url');
  return `${signingInput}.${signature}`;
}

async function verifierFor(policyInput = policy(), jwksInput = jwks()) {
  const provider = createStaticOidcJwksProvider(jwksInput, policyInput);
  const verifier = createOidcVerifier({ policy: policyInput, provider });
  await verifier.initialize();
  return { provider, verifier };
}

async function runCli(args, stdinValue = '') {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, ['software/principia_atlas/hosted/oidc_cli.mjs', ...args], {
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    const stdout = [];
    const stderr = [];
    child.stdout.on('data', (chunk) => stdout.push(chunk));
    child.stderr.on('data', (chunk) => stderr.push(chunk));
    child.on('error', reject);
    child.on('close', (code) => resolve({
      code,
      stdout: Buffer.concat(stdout).toString('utf8'),
      stderr: Buffer.concat(stderr).toString('utf8'),
    }));
    child.stdin.end(stdinValue);
  });
}

test('OIDC verifier maps a signed JWT and mints a bounded hosted assertion', async () => {
  const activePolicy = policy();
  const config = tenantConfig();
  verifyOidcTenantCompatibility(activePolicy, config);
  const { verifier } = await verifierFor(activePolicy);
  const principal = await verifier.verify(signJwt(), fixedNow);
  assert.match(principal.sub, /^oidc:[A-Za-z0-9_-]{43}$/);
  assert.equal(principal.tenant_id, 'school-demo');
  assert.deepEqual(principal.roles, ['learner']);
  const assertion = mintOidcIdentityAssertion(principal, identitySecret, config, activePolicy, fixedNow);
  const exchange = exchangeIdentityAssertion(assertion, identitySecret, sessionSecret, config, fixedNow, () => 'session_identifier_1234567890');
  assert.equal(exchange.session.sub, principal.sub);
  assert.equal(exchange.session.tenant_id, 'school-demo');
  assert.deepEqual(exchange.session.roles, ['learner']);
  assert.equal(exchange.assertion.exp, fixedNow + 180);
});

test('same external JWT yields one durable replay identity', async () => {
  const activePolicy = policy();
  const config = tenantConfig();
  const { verifier } = await verifierFor(activePolicy);
  const token = signJwt();
  const firstPrincipal = await verifier.verify(token, fixedNow);
  const secondPrincipal = await verifier.verify(token, fixedNow);
  assert.equal(firstPrincipal.token_id, secondPrincipal.token_id);
  const firstAssertion = mintOidcIdentityAssertion(firstPrincipal, identitySecret, config, activePolicy, fixedNow);
  const secondAssertion = mintOidcIdentityAssertion(secondPrincipal, identitySecret, config, activePolicy, fixedNow);
  assert.equal(firstAssertion, secondAssertion);
  const first = exchangeIdentityAssertion(firstAssertion, identitySecret, sessionSecret, config, fixedNow, () => 'session_identifier_1234567890');
  const second = exchangeIdentityAssertion(secondAssertion, identitySecret, sessionSecret, config, fixedNow, () => 'session_identifier_abcdefghij');
  const state = createMemoryAuthState();
  assert.equal(state.commitExchange({ assertionId: first.assertion.jti, assertionExpiresAt: first.assertion.exp, session: first.session }, fixedNow), true);
  assert.equal(state.commitExchange({ assertionId: second.assertion.jti, assertionExpiresAt: second.assertion.exp, session: second.session }, fixedNow), false);
  state.close();
});

test('JOSE algorithm key and header confusion fail closed', async () => {
  const { verifier } = await verifierFor();
  const valid = signJwt();
  const parts = valid.split('.');
  const tampered = `${parts[0]}.${parts[1]}.${parts[2].slice(0, -1)}${parts[2].endsWith('A') ? 'B' : 'A'}`;
  await assert.rejects(() => verifier.verify(tampered, fixedNow), /signature|base64url/);
  await assert.rejects(() => verifier.verify(signJwt({ header: { alg: 'none' } }), fixedNow), /algorithm/);
  await assert.rejects(() => verifier.verify(signJwt({ header: { kid: 'unknown' } }), fixedNow), /unavailable/);
  await assert.rejects(() => verifier.verify(signJwt({ header: { jku: 'https://evil.example.test/jwks' } }), fixedNow), /header fields/);
  await assert.rejects(() => verifier.verify(signJwt({ rawHeader: '{"alg":"RS256","alg":"RS256","kid":"rsa-key-1"}' }), fixedNow), /duplicate key/);
});

test('issuer audience authorized-party and time claims fail closed', async () => {
  const { verifier } = await verifierFor();
  await assert.rejects(() => verifier.verify(signJwt({ payload: { iss: 'https://other.example.test' } }), fixedNow), /issuer/);
  await assert.rejects(() => verifier.verify(signJwt({ payload: { aud: 'other' } }), fixedNow), /audience/);
  await assert.rejects(() => verifier.verify(signJwt({ payload: { aud: [audience, 'other'], azp: 'wrong' } }), fixedNow), /authorized party/);
  assert.equal((await verifier.verify(signJwt({ payload: { aud: [audience, 'other'], azp: audience } }), fixedNow)).tenant_id, 'school-demo');
  await assert.rejects(() => verifier.verify(signJwt({ payload: { exp: fixedNow - 31 } }), fixedNow), /expired/);
  await assert.rejects(() => verifier.verify(signJwt({ payload: { nbf: fixedNow + 31 } }), fixedNow), /not active/);
  await assert.rejects(() => verifier.verify(signJwt({ payload: { iat: fixedNow + 31 } }), fixedNow), /time boundary/);
  await assert.rejects(() => verifier.verify(signJwt({ payload: { iat: fixedNow - 4000, exp: fixedNow + 1 } }), fixedNow), /time boundary/);
});

test('tenant role required-claim and email boundaries are policy controlled', async () => {
  const requiredPolicy = policy({
    token: { ...unsignedPolicy().token, require_email_verified: true },
    claims: { ...unsignedPolicy().claims, required: { token_use: 'id' } },
  });
  const { verifier } = await verifierFor(requiredPolicy);
  await assert.rejects(() => verifier.verify(signJwt({ payload: { token_use: 'id' } }), fixedNow), /email verification/);
  await assert.rejects(() => verifier.verify(signJwt({ payload: { email_verified: true } }), fixedNow), /required claim/);
  const accepted = await verifier.verify(signJwt({ payload: { email_verified: true, token_use: 'id', groups: ['teachers', 'students'] } }), fixedNow);
  assert.deepEqual(accepted.roles, ['facilitator', 'learner']);
  await assert.rejects(() => verifier.verify(signJwt({ payload: { email_verified: true, token_use: 'id', organization: 'unknown' } }), fixedNow), /tenant claim/);
  await assert.rejects(() => verifier.verify(signJwt({ payload: { email_verified: true, token_use: 'id', groups: ['unknown'] } }), fixedNow), /unmapped/);
});

test('policy tenant compatibility and JWK material fail closed', () => {
  const activePolicy = policy();
  const config = tenantConfig();
  assert.equal(verifyOidcPolicy(activePolicy).policy_id, activePolicy.policy_id);
  assert.throws(() => verifyOidcPolicy({ ...activePolicy, audience: 'changed' }), /seal/);
  const unavailable = sealOidcPolicy({
    ...unsignedPolicy(),
    claims: {
      ...unsignedPolicy().claims,
      tenant: { name: 'organization', values: { 'external-school': 'missing-tenant' } },
    },
  });
  assert.throws(() => verifyOidcTenantCompatibility(unavailable, config), /unavailable tenant/);
  const privateJwk = keyPair.privateKey.export({ format: 'jwk' });
  assert.throws(() => verifyOidcJwks({ keys: [{ ...jwk(), d: privateJwk.d }] }, activePolicy), /private material/);
  const weak = generateKeyPairSync('rsa', { modulusLength: 1024 });
  assert.throws(() => verifyOidcJwks(jwks([jwk('weak', weak)]), activePolicy), /too weak/);
  assert.throws(() => verifyOidcJwks(jwks([jwk('same'), jwk('same')]), activePolicy), /duplicate/);
});

test('remote JWKS provider caches keys and refreshes once for rotation', async () => {
  const rotated = generateKeyPairSync('rsa', { modulusLength: 2048 });
  const activePolicy = policy();
  const responses = [jwks(), jwks([jwk('rsa-key-2', rotated)])];
  let calls = 0;
  const provider = createRemoteOidcJwksProvider(activePolicy, {
    nowMs: () => 10_000,
    fetchImpl: async () => {
      const body = responses[Math.min(calls, responses.length - 1)];
      calls += 1;
      return new Response(JSON.stringify(body), {
        status: 200,
        headers: { 'content-type': 'application/jwk-set+json', 'cache-control': 'max-age=60' },
      });
    },
  });
  const verifier = createOidcVerifier({ policy: activePolicy, provider });
  await verifier.initialize();
  assert.equal(calls, 1);
  assert.equal((await verifier.verify(signJwt(), fixedNow)).tenant_id, 'school-demo');
  assert.equal(calls, 1);
  const rotatedToken = signJwt({ header: { kid: 'rsa-key-2' }, pair: rotated });
  assert.equal((await verifier.verify(rotatedToken, fixedNow)).tenant_id, 'school-demo');
  assert.equal(calls, 2);
});

test('stdin-only CLI verifies policy and adapts JWT into an internal assertion', async () => {
  const root = await mkdtemp(join(tmpdir(), 'principia-oidc-cli-'));
  const policyPath = join(root, 'policy.json');
  const jwksPath = join(root, 'jwks.json');
  const tenantsPath = join(root, 'tenants.json');
  const secretPath = join(root, 'identity.secret');
  const activePolicy = policy();
  const config = tenantConfig();
  await writeFile(policyPath, JSON.stringify(activePolicy));
  await writeFile(jwksPath, JSON.stringify(jwks()));
  await writeFile(tenantsPath, JSON.stringify(config));
  await writeFile(secretPath, identitySecret, { mode: 0o600 });
  await chmod(secretPath, 0o600);
  const verified = await runCli(['verify', '--policy', policyPath, '--jwks', jwksPath, '--tenants', tenantsPath]);
  assert.equal(verified.code, 0, verified.stderr);
  assert.equal(JSON.parse(verified.stdout).policy_id, activePolicy.policy_id);

  const liveNow = Math.floor(Date.now() / 1000);
  const token = signJwt({ payload: { iat: liveNow - 5, exp: liveNow + 300 } });
  const adapted = await runCli([
    'adapt', '--policy', policyPath, '--jwks', jwksPath, '--tenants', tenantsPath,
    '--identity-secret-file', secretPath,
  ], `${token}\n`);
  assert.equal(adapted.code, 0, adapted.stderr);
  const assertion = adapted.stdout.trim();
  assert.equal(assertion.split('.').length, 3);
  const exchange = exchangeIdentityAssertion(assertion, identitySecret, sessionSecret, config, liveNow, () => 'session_identifier_cli_12345');
  assert.equal(exchange.session.tenant_id, 'school-demo');
  assert.equal(adapted.stderr.includes(token), false);
});
