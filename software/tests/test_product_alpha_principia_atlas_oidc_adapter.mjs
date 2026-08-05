import assert from 'node:assert/strict';
import { generateKeyPairSync, sign as signRaw } from 'node:crypto';
import test from 'node:test';

import {
  OIDC_ADAPTER_CONTRACT,
  OIDC_JWKS_CONTRACT,
  adaptOidcJwt,
  canonicalJson,
  createMemoryAuthState,
  exchangeIdentityAssertion,
  sealOidcAdapterConfig,
  sealOidcJwksSnapshot,
  sealTenantConfig,
} from '../principia_atlas/hosted/index.mjs';

const now = 1_800_000_000;
const identitySecret = 'identity-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const sessionSecret = 'session-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const issuer = 'https://identity.example.test';
const audience = 'principia-atlas-external';
const { publicKey, privateKey } = generateKeyPairSync('rsa', { modulusLength: 2048 });
const publicJwk = publicKey.export({ format: 'jwk' });

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

function adapterConfig() {
  return sealOidcAdapterConfig({
    contract: OIDC_ADAPTER_CONTRACT,
    issuer,
    audience,
    algorithms: ['RS256'],
    max_token_ttl_seconds: 3600,
    clock_skew_seconds: 30,
    subject_claim: 'sub',
    subject_prefix: 'oidc:',
    tenant_claim: 'organization',
    roles_claim: 'groups',
    tenants: { 'external-school': 'school-demo' },
    roles: { students: 'learner', teachers: 'facilitator' },
  });
}

function jwks() {
  return sealOidcJwksSnapshot({
    contract: OIDC_JWKS_CONTRACT,
    issuer,
    keys: [{
      kty: 'RSA',
      use: 'sig',
      alg: 'RS256',
      kid: 'key-1',
      n: publicJwk.n,
      e: publicJwk.e,
    }],
  });
}

function base64url(value) {
  return Buffer.from(typeof value === 'string' ? value : JSON.stringify(value), 'utf8').toString('base64url');
}

function signJwt(payload = {}, header = { alg: 'RS256', kid: 'key-1', typ: 'JWT' }, rawHeader = null, rawPayload = null) {
  const head = base64url(rawHeader ?? header);
  const body = base64url(rawPayload ?? {
    iss: issuer,
    aud: audience,
    sub: 'learner-1',
    organization: 'external-school',
    groups: ['students'],
    iat: now - 10,
    exp: now + 300,
    ...payload,
  });
  const signing = `${head}.${body}`;
  const signature = signRaw('RSA-SHA256', Buffer.from(signing, 'ascii'), privateKey).toString('base64url');
  return `${signing}.${signature}`;
}

function adapt(token = signJwt(), overrides = {}) {
  return adaptOidcJwt({
    token,
    jwks: overrides.jwks ?? jwks(),
    adapterConfig: overrides.adapterConfig ?? adapterConfig(),
    tenantConfig: overrides.tenantConfig ?? tenantConfig(),
    identitySecret,
    nowSeconds: overrides.nowSeconds ?? now,
  });
}

test('OIDC JWT maps to a valid internal tenant assertion', () => {
  const adapted = adapt();
  assert.equal(adapted.subject, 'oidc:learner-1');
  assert.equal(adapted.tenant_id, 'school-demo');
  assert.deepEqual(adapted.roles, ['learner']);
  assert.equal(adapted.expires_at, now + 300);
  const exchanged = exchangeIdentityAssertion(
    adapted.assertion,
    identitySecret,
    sessionSecret,
    tenantConfig(),
    now,
    () => 'session_identifier_1234567890',
  );
  assert.equal(exchanged.session.sub, 'oidc:learner-1');
  assert.equal(exchanged.session.tenant_id, 'school-demo');
  assert.deepEqual(exchanged.session.roles, ['learner']);
});

test('same external JWT produces one deterministic replay identity', () => {
  const token = signJwt();
  const first = adapt(token);
  const second = adapt(token);
  assert.equal(first.assertion, second.assertion);
  const state = createMemoryAuthState();
  const firstExchange = exchangeIdentityAssertion(first.assertion, identitySecret, sessionSecret, tenantConfig(), now, () => 'session_identifier_1234567890');
  const secondExchange = exchangeIdentityAssertion(second.assertion, identitySecret, sessionSecret, tenantConfig(), now, () => 'session_identifier_abcdefghij');
  assert.equal(state.commitExchange({ assertionId: firstExchange.assertion.jti, assertionExpiresAt: firstExchange.assertion.exp, session: firstExchange.session }, now), true);
  assert.equal(state.commitExchange({ assertionId: secondExchange.assertion.jti, assertionExpiresAt: secondExchange.assertion.exp, session: secondExchange.session }, now), false);
  state.close();
});

test('signature algorithm key identifier and canonical encoding fail closed', () => {
  const token = signJwt();
  const parts = token.split('.');
  const tampered = `${parts[0]}.${parts[1]}.${parts[2].slice(0, -1)}${parts[2].endsWith('A') ? 'B' : 'A'}`;
  assert.throws(() => adapt(tampered), /signature|base64url/);
  assert.throws(() => adapt(signJwt({}, { alg: 'none', kid: 'key-1' })), /algorithm/);
  assert.throws(() => adapt(signJwt({}, { alg: 'RS256', kid: 'unknown' })), /unknown/);
  assert.throws(() => adapt(signJwt({}, undefined, '{"alg":"RS256","alg":"RS256","kid":"key-1"}')), /duplicate key/);
});

test('issuer audience lifetime and not-before boundaries fail closed', () => {
  assert.throws(() => adapt(signJwt({ iss: 'https://other.example.test' })), /issuer/);
  assert.throws(() => adapt(signJwt({ aud: 'other-audience' })), /audience/);
  assert.throws(() => adapt(signJwt({ iat: now - 100, exp: now - 31 })), /expired/);
  assert.throws(() => adapt(signJwt({ iat: now + 31, exp: now + 100 })), /future/);
  assert.throws(() => adapt(signJwt({ nbf: now + 31 })), /not active/);
  assert.throws(() => adapt(signJwt({ iat: now - 4000, exp: now + 1 })), /TTL/);
  assert.throws(() => adapt(signJwt({ aud: [audience, 'another'], azp: 'wrong' })), /authorized party/);
  assert.doesNotThrow(() => adapt(signJwt({ aud: [audience, 'another'], azp: audience })));
});

test('tenant and role mappings never fall back to browser claims', () => {
  assert.throws(() => adapt(signJwt({ organization: 'unknown-school' })), /tenant/);
  assert.throws(() => adapt(signJwt({ groups: ['unknown-role'] })), /role/);
  assert.throws(() => adapt(signJwt({ groups: [] })), /roles/);
  assert.deepEqual(adapt(signJwt({ groups: ['teachers', 'students'] })).roles, ['facilitator', 'learner']);
});

test('sealed policy and sanitized JWKS snapshots reject tamper and private keys', () => {
  const config = adapterConfig();
  assert.throws(() => adapt(signJwt(), { adapterConfig: { ...config, audience: 'changed' } }), /seal/);
  const snapshot = jwks();
  assert.throws(() => adapt(signJwt(), { jwks: { ...snapshot, issuer: 'https://changed.example.test' } }), /seal|issuer/);
  const privateJwk = privateKey.export({ format: 'jwk' });
  assert.throws(() => sealOidcJwksSnapshot({
    contract: OIDC_JWKS_CONTRACT,
    issuer,
    keys: [{ ...snapshot.keys[0], d: privateJwk.d }],
  }), /fields/);
  const tooSmall = generateKeyPairSync('rsa', { modulusLength: 1024 }).publicKey.export({ format: 'jwk' });
  assert.throws(() => sealOidcJwksSnapshot({
    contract: OIDC_JWKS_CONTRACT,
    issuer,
    keys: [{ kty: 'RSA', use: 'sig', alg: 'RS256', kid: 'small', n: tooSmall.n, e: tooSmall.e }],
  }), /too small/);
});

test('config seal is canonical regardless of mapping input order', () => {
  const left = adapterConfig();
  const right = sealOidcAdapterConfig({
    contract: OIDC_ADAPTER_CONTRACT,
    issuer,
    audience,
    algorithms: ['RS256'],
    max_token_ttl_seconds: 3600,
    clock_skew_seconds: 30,
    subject_claim: 'sub',
    subject_prefix: 'oidc:',
    tenant_claim: 'organization',
    roles_claim: 'groups',
    tenants: { 'external-school': 'school-demo' },
    roles: { teachers: 'facilitator', students: 'learner' },
  });
  assert.equal(left.config_id, right.config_id);
  assert.equal(canonicalJson(left), canonicalJson(right));
});
