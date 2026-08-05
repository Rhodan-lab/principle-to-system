import assert from 'node:assert/strict';
import { generateKeyPairSync, sign as signRaw } from 'node:crypto';
import test from 'node:test';

import {
  OIDC_POLICY_CONTRACT,
  PRODUCT,
  createOidcVerifier,
  createRemoteOidcJwksProvider,
  createStaticOidcJwksProvider,
  sealOidcPolicy,
  verifyOidcJwks,
} from '../principia_atlas/hosted/index.mjs';

const now = 1_800_000_000;
const issuer = 'https://identity.example.test';
const audience = 'principia-atlas-external';
const jwksUri = `${issuer}/.well-known/jwks.json`;
const rsa = generateKeyPairSync('rsa', { modulusLength: 2048 });
const rsa2 = generateKeyPairSync('rsa', { modulusLength: 2048 });
const ec = generateKeyPairSync('ec', { namedCurve: 'P-256' });

function policy(overrides = {}) {
  return sealOidcPolicy({
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
      tenant: { name: 'organization', values: { 'external-school': 'school-demo' } },
      roles: {
        name: 'groups',
        values: { students: 'learner', teachers: 'facilitator' },
        reject_unmapped: true,
      },
      required: { assurance: 'mfa' },
    },
    ...overrides,
  });
}

function rsaJwk(pair = rsa, kid = 'rsa-1') {
  const value = pair.publicKey.export({ format: 'jwk' });
  return { kty: 'RSA', kid, use: 'sig', key_ops: ['verify'], alg: 'RS256', n: value.n, e: value.e };
}

function ecJwk() {
  const value = ec.publicKey.export({ format: 'jwk' });
  return { kty: 'EC', kid: 'ec-1', use: 'sig', key_ops: ['verify'], alg: 'ES256', crv: value.crv, x: value.x, y: value.y };
}

function jwks(...keys) {
  return { keys: keys.length ? keys : [rsaJwk(), ecJwk()] };
}

function encode(value) {
  const raw = typeof value === 'string' ? value : JSON.stringify(value);
  return Buffer.from(raw, 'utf8').toString('base64url');
}

function payload(overrides = {}) {
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

function signJwt({
  claims = payload(),
  header = { alg: 'RS256', kid: 'rsa-1', typ: 'JWT' },
  privateKey = rsa.privateKey,
  rawHeader = null,
  rawPayload = null,
} = {}) {
  const head = encode(rawHeader ?? header);
  const body = encode(rawPayload ?? claims);
  const signing = `${head}.${body}`;
  const options = header.alg === 'ES256' ? { key: privateKey, dsaEncoding: 'ieee-p1363' } : privateKey;
  const signature = signRaw(header.alg === 'ES256' ? 'sha256' : 'RSA-SHA256', Buffer.from(signing, 'ascii'), options);
  return `${signing}.${signature.toString('base64url')}`;
}

async function verifierFor(policyInput = policy(), jwksInput = jwks()) {
  const provider = createStaticOidcJwksProvider(jwksInput, policyInput);
  const verifier = createOidcVerifier({ policy: policyInput, provider });
  await verifier.initialize();
  return verifier;
}

function response(body, {
  status = 200,
  url = jwksUri,
  redirected = false,
  contentType = 'application/jwk-set+json',
  contentLength = null,
} = {}) {
  const raw = Buffer.from(JSON.stringify(body));
  return {
    status,
    url,
    redirected,
    body: null,
    headers: {
      get(name) {
        const key = String(name).toLowerCase();
        if (key === 'content-type') return contentType;
        if (key === 'content-length') return contentLength ?? String(raw.length);
        if (key === 'cache-control') return 'max-age=60';
        return null;
      },
    },
    async arrayBuffer() { return raw; },
  };
}

test('signature tamper algorithm confusion unknown kid and dynamic JOSE headers fail closed', async () => {
  const verifier = await verifierFor();
  const token = signJwt();
  const parts = token.split('.');
  const replacement = parts[2].endsWith('A') ? 'B' : 'A';
  await assert.rejects(() => verifier.verify(`${parts[0]}.${parts[1]}.${parts[2].slice(0, -1)}${replacement}`, now), /signature|base64url/);
  await assert.rejects(() => verifier.verify(signJwt({ header: { alg: 'none', kid: 'rsa-1' } }), now), /algorithm/);
  await assert.rejects(() => verifier.verify(signJwt({ header: { alg: 'RS256', kid: 'missing' } }), now), /unavailable/);
  await assert.rejects(() => verifier.verify(signJwt({ header: { alg: 'RS256', kid: 'rsa-1', jku: 'https://attacker.example.test/jwks' } }), now), /header fields/);
  await assert.rejects(() => verifier.verify(signJwt({ rawHeader: '{"alg":"RS256","alg":"RS256","kid":"rsa-1"}' }), now), /duplicate key/);
});

test('issuer audience azp and temporal claims fail closed', async () => {
  const verifier = await verifierFor();
  await assert.rejects(() => verifier.verify(signJwt({ claims: payload({ iss: 'https://other.example.test' }) }), now), /issuer/);
  await assert.rejects(() => verifier.verify(signJwt({ claims: payload({ aud: 'other' }) }), now), /audience/);
  await assert.rejects(() => verifier.verify(signJwt({ claims: payload({ aud: [audience, 'other'], azp: 'wrong' }) }), now), /authorized party/);
  assert.equal((await verifier.verify(signJwt({ claims: payload({ aud: [audience, 'other'], azp: audience }) }), now)).tenant_id, 'school-demo');
  await assert.rejects(() => verifier.verify(signJwt({ claims: payload({ exp: now - 31 }) }), now), /expired/);
  await assert.rejects(() => verifier.verify(signJwt({ claims: payload({ nbf: now + 31 }) }), now), /not active/);
  await assert.rejects(() => verifier.verify(signJwt({ claims: payload({ iat: now + 31 }) }), now), /time boundary/);
  await assert.rejects(() => verifier.verify(signJwt({ claims: payload({ iat: now - 4000, exp: now + 1 }) }), now), /time boundary/);
});

test('required claims email tenant and role mapping never fall back', async () => {
  const verifier = await verifierFor();
  await assert.rejects(() => verifier.verify(signJwt({ claims: payload({ email_verified: false }) }), now), /email verification/);
  await assert.rejects(() => verifier.verify(signJwt({ claims: payload({ assurance: 'password' }) }), now), /required claim/);
  await assert.rejects(() => verifier.verify(signJwt({ claims: payload({ organization: 'unknown' }) }), now), /tenant claim/);
  await assert.rejects(() => verifier.verify(signJwt({ claims: payload({ groups: ['unknown'] }) }), now), /unmapped/);
  assert.deepEqual((await verifier.verify(signJwt({ claims: payload({ groups: ['teachers', 'students'] }) }), now)).roles, ['facilitator', 'learner']);
  const permissive = policy({
    claims: {
      tenant: { name: 'organization', values: { 'external-school': 'school-demo' } },
      roles: { name: 'groups', values: { students: 'learner' }, reject_unmapped: false },
      required: { assurance: 'mfa' },
    },
  });
  const permissiveVerifier = await verifierFor(permissive);
  assert.deepEqual((await permissiveVerifier.verify(signJwt({ claims: payload({ groups: ['unknown', 'students'] }) }), now)).roles, ['learner']);
});

test('JWKS rejects private weak duplicate and mismatched EC key material', () => {
  const activePolicy = policy();
  const privateJwk = rsa.privateKey.export({ format: 'jwk' });
  assert.throws(() => verifyOidcJwks({ keys: [{ ...rsaJwk(), d: privateJwk.d }] }, activePolicy), /private material|fields/);
  const weak = generateKeyPairSync('rsa', { modulusLength: 1024 }).publicKey.export({ format: 'jwk' });
  assert.throws(() => verifyOidcJwks({ keys: [{ kty: 'RSA', kid: 'weak', use: 'sig', alg: 'RS256', n: weak.n, e: weak.e }] }, activePolicy), /too weak/);
  assert.throws(() => verifyOidcJwks({ keys: [rsaJwk(), rsaJwk()] }, activePolicy), /duplicate/);
  assert.throws(() => verifyOidcJwks({ keys: [{ ...ecJwk(), crv: 'P-384' }] }, activePolicy), /boundary/);
});

test('remote provider caches and refreshes once when kid rotates', async () => {
  let calls = 0;
  const responses = [response(jwks(rsaJwk())), response(jwks(rsaJwk(rsa2, 'rsa-2')))];
  const provider = createRemoteOidcJwksProvider(policy(), {
    nowMs: () => 1000,
    fetchImpl: async (_url, options) => {
      assert.equal(options.redirect, 'error');
      const value = responses[Math.min(calls, responses.length - 1)];
      calls += 1;
      return value;
    },
  });
  const verifier = createOidcVerifier({ policy: policy(), provider });
  await verifier.initialize();
  assert.equal(calls, 1);
  assert.equal((await verifier.verify(signJwt(), now)).tenant_id, 'school-demo');
  assert.equal(calls, 1);
  const rotated = signJwt({ header: { alg: 'RS256', kid: 'rsa-2', typ: 'JWT' }, privateKey: rsa2.privateKey });
  assert.equal((await verifier.verify(rotated, now)).tenant_id, 'school-demo');
  assert.equal(calls, 2);
  assert.equal((await verifier.verify(rotated, now)).tenant_id, 'school-demo');
  assert.equal(calls, 2);
});

test('remote provider rejects redirects content type changed URL and oversized responses', async () => {
  const activePolicy = policy();
  await assert.rejects(
    () => createRemoteOidcJwksProvider(activePolicy, { fetchImpl: async () => response(jwks(), { redirected: true }) }).initialize(),
    /response/,
  );
  await assert.rejects(
    () => createRemoteOidcJwksProvider(activePolicy, { fetchImpl: async () => response(jwks(), { contentType: 'text/html' }) }).initialize(),
    /content type/,
  );
  await assert.rejects(
    () => createRemoteOidcJwksProvider(activePolicy, { fetchImpl: async () => response(jwks(), { url: 'https://other.example.test/jwks' }) }).initialize(),
    /URL changed/,
  );
  await assert.rejects(
    () => createRemoteOidcJwksProvider(activePolicy, { fetchImpl: async () => response(jwks(), { contentLength: '999999' }) }).initialize(),
    /resource limit/,
  );
});
