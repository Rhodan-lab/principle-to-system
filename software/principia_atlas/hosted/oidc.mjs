import {
  createHash,
  createPublicKey,
  verify as verifySignature,
} from 'node:crypto';
import { lstat, readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { PRODUCT, verifyTenantConfig } from './catalog.mjs';
import { signIdentityAssertion } from './tokens.mjs';
import {
  canonicalJson,
  exactKeys,
  fail,
  parseStrictJson,
  sha256Hex,
} from './strict_json.mjs';

export const OIDC_POLICY_CONTRACT = 'principia-atlas-hosted-oidc-policy/0.1';
export const OIDC_PRINCIPAL_CONTRACT = 'principia-atlas-hosted-oidc-principal/0.1';
export const OIDC_VERIFIER_CONTRACT = 'principia-atlas-hosted-oidc-verifier/0.1';
const SHA = /^[0-9a-f]{64}$/;
const TENANT_ID = /^[a-z][a-z0-9-]{1,62}$/;
const ROLE = /^[a-z][a-z0-9_-]{0,31}$/;
const SUBJECT = /^[A-Za-z0-9._:@+-]{1,200}$/;
const CLAIM = /^[A-Za-z_][A-Za-z0-9_.:-]{0,127}$/;
const KID = /^[\x21-\x7e]{1,128}$/;
const ALGORITHMS = new Set(['RS256', 'ES256']);
const MAX_TOKEN_BYTES = 32768;
const MAX_JWKS_KEYS = 64;
const SENSITIVE_JOSE_HEADERS = new Set(['jku', 'jwk', 'x5u', 'x5c', 'crit']);
const RESERVED_OBJECT_KEYS = new Set(['__proto__', 'prototype', 'constructor']);

function integer(value, label, minimum, maximum) {
  if (!Number.isSafeInteger(value) || value < minimum || value > maximum) fail(`${label} is invalid`);
  return value;
}

function scalar(value, label) {
  if (value === null || typeof value === 'boolean' || typeof value === 'string' || Number.isSafeInteger(value)) return value;
  fail(`${label} must be a JSON scalar`);
}

function stringMap(value, label, valuePattern) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail(`${label} must be an object`);
  const entries = Object.entries(value);
  if (entries.length === 0 || entries.length > 256) fail(`${label} size is invalid`);
  const output = {};
  for (const [external, internal] of entries) {
    if (typeof external !== 'string' || external.length === 0 || Buffer.byteLength(external) > 256 || RESERVED_OBJECT_KEYS.has(external)) fail(`${label} key is invalid`);
    if (typeof internal !== 'string' || !valuePattern.test(internal)) fail(`${label} value is invalid`);
    output[external] = internal;
  }
  return output;
}

function httpsUrl(value, label, { issuer = false } = {}) {
  let url;
  try { url = new URL(value); } catch { fail(`${label} is invalid`); }
  if (url.protocol !== 'https:' || url.username || url.password || url.hash) fail(`${label} must be an HTTPS URL without credentials or fragment`);
  if (issuer && (url.search || (url.pathname.length > 1 && url.pathname.endsWith('/')))) fail(`${label} boundary is invalid`);
  if (!issuer && url.search) fail(`${label} query is not permitted`);
  if (url.hostname === 'localhost' || url.hostname.endsWith('.localhost') || /^\d+\.\d+\.\d+\.\d+$/.test(url.hostname) || url.hostname.includes(':')) fail(`${label} host is invalid`);
  return value;
}

export function sealOidcPolicy(unsigned) {
  const value = structuredClone(unsigned);
  value.policy_id = sha256Hex(canonicalJson(unsigned));
  return value;
}

export function verifyOidcPolicy(input) {
  const value = typeof input === 'string' || Buffer.isBuffer(input)
    ? parseStrictJson(input, 'OIDC policy')
    : structuredClone(input);
  exactKeys(value, [
    'contract', 'product', 'issuer', 'audience', 'authorized_party',
    'jwks', 'token', 'claims', 'policy_id',
  ], 'OIDC policy');
  if (value.contract !== OIDC_POLICY_CONTRACT || value.product !== PRODUCT) fail('OIDC policy contract is invalid');
  const unsigned = structuredClone(value); delete unsigned.policy_id;
  if (!SHA.test(value.policy_id) || sha256Hex(canonicalJson(unsigned)) !== value.policy_id) fail('OIDC policy seal is invalid');
  value.issuer = httpsUrl(value.issuer, 'OIDC issuer', { issuer: true });
  if (typeof value.audience !== 'string' || value.audience.length === 0 || value.audience.length > 200) fail('OIDC audience is invalid');
  if (value.authorized_party !== null && (typeof value.authorized_party !== 'string' || value.authorized_party.length === 0 || value.authorized_party.length > 200)) fail('OIDC authorized party is invalid');

  exactKeys(value.jwks, [
    'uri', 'allowed_algorithms', 'cache_ttl_seconds', 'fetch_timeout_ms', 'max_bytes',
  ], 'OIDC JWKS policy');
  value.jwks.uri = httpsUrl(value.jwks.uri, 'OIDC JWKS URI');
  if (!Array.isArray(value.jwks.allowed_algorithms) || value.jwks.allowed_algorithms.length === 0 || value.jwks.allowed_algorithms.length > ALGORITHMS.size) fail('OIDC algorithms are invalid');
  if (value.jwks.allowed_algorithms.some((algorithm) => !ALGORITHMS.has(algorithm)) || new Set(value.jwks.allowed_algorithms).size !== value.jwks.allowed_algorithms.length) fail('OIDC algorithms are invalid');
  integer(value.jwks.cache_ttl_seconds, 'OIDC JWKS cache TTL', 30, 86400);
  integer(value.jwks.fetch_timeout_ms, 'OIDC JWKS fetch timeout', 100, 30000);
  integer(value.jwks.max_bytes, 'OIDC JWKS resource limit', 1024, 2 * 1024 * 1024);

  exactKeys(value.token, [
    'max_ttl_seconds', 'clock_skew_seconds', 'internal_assertion_ttl_seconds',
    'require_iat', 'require_email_verified',
  ], 'OIDC token policy');
  integer(value.token.max_ttl_seconds, 'OIDC token TTL', 30, 86400);
  integer(value.token.clock_skew_seconds, 'OIDC clock skew', 0, 120);
  integer(value.token.internal_assertion_ttl_seconds, 'OIDC internal assertion TTL', 30, 300);
  if (typeof value.token.require_iat !== 'boolean' || typeof value.token.require_email_verified !== 'boolean') fail('OIDC token flags are invalid');

  exactKeys(value.claims, ['tenant', 'roles', 'required'], 'OIDC claim policy');
  exactKeys(value.claims.tenant, ['name', 'values'], 'OIDC tenant claim policy');
  if (typeof value.claims.tenant.name !== 'string' || !CLAIM.test(value.claims.tenant.name)) fail('OIDC tenant claim name is invalid');
  value.claims.tenant.values = stringMap(value.claims.tenant.values, 'OIDC tenant claim mapping', TENANT_ID);
  exactKeys(value.claims.roles, ['name', 'values', 'reject_unmapped'], 'OIDC role claim policy');
  if (typeof value.claims.roles.name !== 'string' || !CLAIM.test(value.claims.roles.name)) fail('OIDC role claim name is invalid');
  value.claims.roles.values = stringMap(value.claims.roles.values, 'OIDC role claim mapping', ROLE);
  if (typeof value.claims.roles.reject_unmapped !== 'boolean') fail('OIDC role mapping mode is invalid');
  if (!value.claims.required || typeof value.claims.required !== 'object' || Array.isArray(value.claims.required) || Object.keys(value.claims.required).length > 32) fail('OIDC required claims are invalid');
  for (const [name, expected] of Object.entries(value.claims.required)) {
    if (!CLAIM.test(name) || RESERVED_OBJECT_KEYS.has(name)) fail('OIDC required claim name is invalid');
    value.claims.required[name] = scalar(expected, `OIDC required claim ${name}`);
  }
  return value;
}

export function verifyOidcTenantCompatibility(policyInput, configInput) {
  const policy = verifyOidcPolicy(policyInput);
  const config = verifyTenantConfig(configInput);
  if (policy.token.internal_assertion_ttl_seconds > config.identity.max_assertion_ttl_seconds) fail('OIDC internal assertion TTL exceeds tenant identity boundary');
  for (const tenantId of Object.values(policy.claims.tenant.values)) {
    if (!config.tenants[tenantId]) fail(`OIDC policy maps unavailable tenant ${tenantId}`);
  }
  return { policy, config };
}

function decodeCanonicalBase64url(value, label, maximum = MAX_TOKEN_BYTES) {
  if (typeof value !== 'string' || value.length === 0 || value.length > maximum * 2 || !/^[A-Za-z0-9_-]+$/.test(value)) fail(`${label} is not canonical base64url`);
  const raw = Buffer.from(value, 'base64url');
  if (raw.length > maximum || raw.toString('base64url') !== value) fail(`${label} is not canonical base64url`);
  return raw;
}

function jwtParts(token) {
  if (typeof token !== 'string' || Buffer.byteLength(token) > MAX_TOKEN_BYTES) fail('OIDC token exceeds resource limit');
  const parts = token.split('.');
  if (parts.length !== 3) fail('OIDC token is invalid');
  const headerRaw = decodeCanonicalBase64url(parts[0], 'OIDC header', 8192);
  const payloadRaw = decodeCanonicalBase64url(parts[1], 'OIDC payload', 24576);
  const signature = decodeCanonicalBase64url(parts[2], 'OIDC signature', 8192);
  const header = parseStrictJson(headerRaw, 'OIDC header');
  const payload = parseStrictJson(payloadRaw, 'OIDC payload');
  if (!header || typeof header !== 'object' || Array.isArray(header) || !payload || typeof payload !== 'object' || Array.isArray(payload)) fail('OIDC token JSON is invalid');
  const keys = Object.keys(header);
  if (!keys.includes('alg') || !keys.includes('kid') || keys.some((key) => !['alg', 'kid', 'typ'].includes(key) || SENSITIVE_JOSE_HEADERS.has(key))) fail('OIDC JOSE header fields are invalid');
  if (header.typ !== undefined && header.typ !== 'JWT') fail('OIDC token type is invalid');
  if (typeof header.alg !== 'string' || typeof header.kid !== 'string' || !KID.test(header.kid)) fail('OIDC JOSE header identity is invalid');
  return {
    token,
    header,
    payload,
    signingInput: Buffer.from(`${parts[0]}.${parts[1]}`, 'ascii'),
    signature,
  };
}

function publicKeyFromJwk(input, policy) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) fail('OIDC JWK must be an object');
  const forbidden = ['d', 'p', 'q', 'dp', 'dq', 'qi', 'oth'];
  if (forbidden.some((field) => field in input)) fail('OIDC JWK contains private material');
  const allowed = new Set(['kty', 'kid', 'use', 'key_ops', 'alg', 'n', 'e', 'crv', 'x', 'y']);
  if (Object.keys(input).some((field) => !allowed.has(field))) fail('OIDC JWK fields are invalid');
  if (typeof input.kid !== 'string' || !KID.test(input.kid)) fail('OIDC JWK identifier is invalid');
  if (input.use !== undefined && input.use !== 'sig') fail('OIDC JWK use is invalid');
  if (input.key_ops !== undefined) {
    if (!Array.isArray(input.key_ops) || input.key_ops.length !== 1 || input.key_ops[0] !== 'verify') fail('OIDC JWK operations are invalid');
  }
  if (input.alg !== undefined && !policy.jwks.allowed_algorithms.includes(input.alg)) fail('OIDC JWK algorithm is not allowed');
  let algorithm;
  let material;
  if (input.kty === 'RSA') {
    algorithm = input.alg ?? 'RS256';
    if (algorithm !== 'RS256' || !policy.jwks.allowed_algorithms.includes(algorithm)) fail('OIDC RSA key algorithm is invalid');
    decodeCanonicalBase64url(input.n, 'OIDC RSA modulus', 4096);
    decodeCanonicalBase64url(input.e, 'OIDC RSA exponent', 16);
    material = { kty: 'RSA', n: input.n, e: input.e };
  } else if (input.kty === 'EC') {
    algorithm = input.alg ?? 'ES256';
    if (algorithm !== 'ES256' || input.crv !== 'P-256' || !policy.jwks.allowed_algorithms.includes(algorithm)) fail('OIDC EC key boundary is invalid');
    if (decodeCanonicalBase64url(input.x, 'OIDC EC x', 64).length !== 32 || decodeCanonicalBase64url(input.y, 'OIDC EC y', 64).length !== 32) fail('OIDC EC coordinate length is invalid');
    material = { kty: 'EC', crv: 'P-256', x: input.x, y: input.y };
  } else fail('OIDC JWK key type is invalid');
  let key;
  try { key = createPublicKey({ key: material, format: 'jwk' }); }
  catch { fail('OIDC JWK public key is invalid'); }
  if (algorithm === 'RS256') {
    if (key.asymmetricKeyType !== 'rsa' || (key.asymmetricKeyDetails?.modulusLength ?? 0) < 2048) fail('OIDC RSA key is too weak');
  } else if (key.asymmetricKeyType !== 'ec' || key.asymmetricKeyDetails?.namedCurve !== 'prime256v1') fail('OIDC EC key is invalid');
  return Object.freeze({ kid: input.kid, algorithm, key });
}

export function verifyOidcJwks(input, policyInput) {
  const policy = verifyOidcPolicy(policyInput);
  const value = typeof input === 'string' || Buffer.isBuffer(input)
    ? parseStrictJson(input, 'OIDC JWKS')
    : structuredClone(input);
  exactKeys(value, ['keys'], 'OIDC JWKS');
  if (!Array.isArray(value.keys) || value.keys.length === 0 || value.keys.length > MAX_JWKS_KEYS) fail('OIDC JWKS key count is invalid');
  const keys = new Map();
  for (const entry of value.keys) {
    const parsed = publicKeyFromJwk(entry, policy);
    if (keys.has(parsed.kid)) fail('OIDC JWKS contains duplicate key identifiers');
    keys.set(parsed.kid, parsed);
  }
  return keys;
}

function keyFor(keys, kid, algorithm) {
  const entry = keys.get(kid);
  if (!entry || entry.algorithm !== algorithm) return null;
  return entry.key;
}

export function createStaticOidcJwksProvider(jwksInput, policyInput) {
  const policy = verifyOidcPolicy(policyInput);
  const keys = verifyOidcJwks(jwksInput, policy);
  const descriptor = Object.freeze({ kind: 'static', network: false, policy_id: policy.policy_id });
  return Object.freeze({
    descriptor,
    async initialize() { return descriptor; },
    async getKey(kid, algorithm) {
      const key = keyFor(keys, kid, algorithm);
      if (!key) fail('OIDC signing key is unavailable');
      return key;
    },
    health() { return Object.freeze({ status: 'ok', ...descriptor, key_count: keys.size }); },
  });
}

export async function createFileOidcJwksProvider(pathInput, policyInput) {
  if (typeof pathInput !== 'string' || pathInput.length === 0) fail('OIDC JWKS file path is invalid');
  const path = resolve(pathInput);
  const stats = await lstat(path);
  if (stats.isSymbolicLink() || !stats.isFile()) fail('OIDC JWKS file must be a regular file');
  const policy = verifyOidcPolicy(policyInput);
  if (stats.size > policy.jwks.max_bytes) fail('OIDC JWKS exceeds resource limit');
  const raw = await readFile(path);
  return createStaticOidcJwksProvider(raw, policy);
}

function boundedCacheTtl(response, policy) {
  const header = response.headers?.get?.('cache-control') ?? '';
  const match = /(?:^|,)\s*max-age=(\d+)(?:\s*(?:,|$))/i.exec(header);
  if (!match) return policy.jwks.cache_ttl_seconds;
  const value = Number(match[1]);
  if (!Number.isSafeInteger(value) || value < 0) return policy.jwks.cache_ttl_seconds;
  return Math.max(1, Math.min(value, policy.jwks.cache_ttl_seconds));
}

async function boundedResponseBytes(response, maximum) {
  const declared = Number(response.headers?.get?.('content-length'));
  if (Number.isFinite(declared) && declared > maximum) fail('OIDC JWKS exceeds resource limit');
  if (!response.body?.getReader) {
    const raw = Buffer.from(await response.arrayBuffer());
    if (raw.length > maximum) fail('OIDC JWKS exceeds resource limit');
    return raw;
  }
  const reader = response.body.getReader();
  const chunks = [];
  let total = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.byteLength;
    if (total > maximum) {
      try { await reader.cancel(); } catch {}
      fail('OIDC JWKS exceeds resource limit');
    }
    chunks.push(Buffer.from(value));
  }
  return Buffer.concat(chunks, total);
}

export function createRemoteOidcJwksProvider(policyInput, {
  fetchImpl = globalThis.fetch,
  nowMs = () => Date.now(),
} = {}) {
  const policy = verifyOidcPolicy(policyInput);
  if (typeof fetchImpl !== 'function') fail('OIDC JWKS fetch implementation is unavailable');
  let keys = null;
  let expiresAtMs = 0;
  let inFlight = null;
  const descriptor = Object.freeze({ kind: 'remote', network: true, policy_id: policy.policy_id, uri: policy.jwks.uri });
  const load = async (force = false) => {
    const current = nowMs();
    if (!force && keys && current < expiresAtMs) return keys;
    if (inFlight) return inFlight;
    inFlight = (async () => {
      let response;
      try {
        response = await fetchImpl(policy.jwks.uri, {
          method: 'GET',
          redirect: 'error',
          headers: { Accept: 'application/jwk-set+json, application/json' },
          signal: AbortSignal.timeout(policy.jwks.fetch_timeout_ms),
        });
      } catch { fail('OIDC JWKS fetch failed'); }
      if (!response || response.status !== 200 || response.redirected === true) fail('OIDC JWKS response is invalid');
      if (response.url && response.url !== policy.jwks.uri) fail('OIDC JWKS response URL changed');
      const contentType = String(response.headers?.get?.('content-type') ?? '').toLowerCase();
      if (!contentType.includes('application/json') && !contentType.includes('application/jwk-set+json')) fail('OIDC JWKS content type is invalid');
      const raw = await boundedResponseBytes(response, policy.jwks.max_bytes);
      const next = verifyOidcJwks(raw, policy);
      keys = next;
      expiresAtMs = nowMs() + boundedCacheTtl(response, policy) * 1000;
      return keys;
    })();
    try { return await inFlight; }
    finally { inFlight = null; }
  };
  return Object.freeze({
    descriptor,
    async initialize() { await load(true); return descriptor; },
    async getKey(kid, algorithm) {
      let current = await load(false);
      let key = keyFor(current, kid, algorithm);
      if (key) return key;
      current = await load(true);
      key = keyFor(current, kid, algorithm);
      if (!key) fail('OIDC signing key is unavailable');
      return key;
    },
    health() {
      const current = nowMs();
      const ready = Boolean(keys && current < expiresAtMs);
      return Object.freeze({ status: ready ? 'ok' : 'not_ready', ...descriptor, key_count: keys?.size ?? 0, expires_at_ms: expiresAtMs });
    },
  });
}

function verifyJwtSignature(parts, key) {
  if (parts.header.alg === 'RS256') {
    if (!verifySignature('RSA-SHA256', parts.signingInput, key, parts.signature)) fail('OIDC token signature is invalid');
    return;
  }
  if (parts.header.alg === 'ES256') {
    if (parts.signature.length !== 64 || !verifySignature('sha256', parts.signingInput, { key, dsaEncoding: 'ieee-p1363' }, parts.signature)) fail('OIDC token signature is invalid');
    return;
  }
  fail('OIDC token algorithm is invalid');
}

function audiences(value) {
  if (typeof value === 'string' && value.length > 0) return [value];
  if (Array.isArray(value) && value.length > 0 && value.every((item) => typeof item === 'string' && item.length > 0) && new Set(value).size === value.length) return value;
  fail('OIDC audience claim is invalid');
}

function rolesClaim(value) {
  if (typeof value === 'string' && value.length > 0) return [value];
  if (Array.isArray(value) && value.length > 0 && value.length <= 64 && value.every((item) => typeof item === 'string' && item.length > 0 && Buffer.byteLength(item) <= 256) && new Set(value).size === value.length) return value;
  fail('OIDC role claim is invalid');
}

function validateOidcClaims(payload, policy, nowSeconds, token) {
  if (payload.iss !== policy.issuer) fail('OIDC issuer claim is invalid');
  const aud = audiences(payload.aud);
  if (!aud.includes(policy.audience)) fail('OIDC audience claim is invalid');
  const expectedAzp = policy.authorized_party ?? policy.audience;
  if (aud.length > 1 && payload.azp !== expectedAzp) fail('OIDC authorized party claim is invalid');
  if (payload.azp !== undefined && payload.azp !== expectedAzp) fail('OIDC authorized party claim is invalid');
  if (typeof payload.sub !== 'string' || payload.sub.length === 0 || Buffer.byteLength(payload.sub) > 512 || /[\u0000-\u001f\u007f]/.test(payload.sub)) fail('OIDC subject claim is invalid');
  const skew = policy.token.clock_skew_seconds;
  if (!Number.isSafeInteger(payload.exp) || payload.exp + skew <= nowSeconds) fail('OIDC token is expired');
  if (payload.nbf !== undefined && (!Number.isSafeInteger(payload.nbf) || payload.nbf - skew > nowSeconds)) fail('OIDC token is not active');
  if (policy.token.require_iat && !Number.isSafeInteger(payload.iat)) fail('OIDC issued-at claim is required');
  if (payload.iat !== undefined) {
    if (!Number.isSafeInteger(payload.iat) || payload.iat - skew > nowSeconds || payload.exp <= payload.iat || payload.exp - payload.iat > policy.token.max_ttl_seconds) fail('OIDC token time boundary is invalid');
  }
  if (policy.token.require_email_verified && payload.email_verified !== true) fail('OIDC email verification claim is invalid');
  for (const [name, expected] of Object.entries(policy.claims.required)) {
    if (!(name in payload) || canonicalJson(payload[name]) !== canonicalJson(expected)) fail(`OIDC required claim ${name} is invalid`);
  }
  const externalTenant = payload[policy.claims.tenant.name];
  if (typeof externalTenant !== 'string') fail('OIDC tenant claim is invalid');
  const tenantId = policy.claims.tenant.values[externalTenant];
  if (!tenantId) fail('OIDC tenant claim is not mapped');
  const externalRoles = rolesClaim(payload[policy.claims.roles.name]);
  const mapped = [];
  for (const externalRole of externalRoles) {
    const internal = policy.claims.roles.values[externalRole];
    if (!internal) {
      if (policy.claims.roles.reject_unmapped) fail('OIDC role claim contains an unmapped value');
      continue;
    }
    mapped.push(internal);
  }
  const roles = [...new Set(mapped)].sort();
  if (roles.length === 0) fail('OIDC role claim maps no hosted role');
  return Object.freeze({
    contract: OIDC_PRINCIPAL_CONTRACT,
    policy_id: policy.policy_id,
    sub: `oidc:${createHash('sha256').update(`${policy.issuer}\u0000${payload.sub}`).digest('base64url')}`,
    tenant_id: tenantId,
    roles,
    token_id: createHash('sha256').update(token).digest('base64url'),
    issued_at: payload.iat ?? nowSeconds,
    expires_at: payload.exp,
  });
}

export function createOidcVerifier({ policy: policyInput, provider }) {
  const policy = verifyOidcPolicy(policyInput);
  if (!provider || typeof provider.initialize !== 'function' || typeof provider.getKey !== 'function' || typeof provider.health !== 'function' || !provider.descriptor) fail('OIDC JWKS provider is invalid');
  const descriptor = Object.freeze({
    contract: OIDC_VERIFIER_CONTRACT,
    policy_id: policy.policy_id,
    issuer: policy.issuer,
    audience: policy.audience,
    algorithms: [...policy.jwks.allowed_algorithms],
    jwks: provider.descriptor,
  });
  return Object.freeze({
    policy,
    descriptor,
    async initialize() { await provider.initialize(); return descriptor; },
    health() { return Object.freeze({ ...descriptor, provider: provider.health() }); },
    async verify(token, nowSeconds = Math.floor(Date.now() / 1000)) {
      integer(nowSeconds, 'OIDC current time', 0, Number.MAX_SAFE_INTEGER);
      const parts = jwtParts(token);
      if (!policy.jwks.allowed_algorithms.includes(parts.header.alg)) fail('OIDC token algorithm is not allowed');
      const key = await provider.getKey(parts.header.kid, parts.header.alg);
      verifyJwtSignature(parts, key);
      return validateOidcClaims(parts.payload, policy, nowSeconds, token);
    },
  });
}

export function mintOidcIdentityAssertion(principalInput, identitySecret, configInput, policyInput, nowSeconds = Math.floor(Date.now() / 1000)) {
  const { policy, config } = verifyOidcTenantCompatibility(policyInput, configInput);
  const principal = structuredClone(principalInput);
  exactKeys(principal, ['contract', 'policy_id', 'sub', 'tenant_id', 'roles', 'token_id', 'issued_at', 'expires_at'], 'OIDC principal');
  if (principal.contract !== OIDC_PRINCIPAL_CONTRACT || principal.policy_id !== policy.policy_id || !SUBJECT.test(principal.sub ?? '') || !config.tenants[principal.tenant_id]) fail('OIDC principal identity is invalid');
  if (!Array.isArray(principal.roles) || principal.roles.length === 0 || principal.roles.some((role) => !ROLE.test(role)) || new Set(principal.roles).size !== principal.roles.length) fail('OIDC principal roles are invalid');
  if (typeof principal.token_id !== 'string' || !/^[A-Za-z0-9_-]{43}$/.test(principal.token_id)) fail('OIDC principal token identity is invalid');
  integer(nowSeconds, 'OIDC current time', 0, Number.MAX_SAFE_INTEGER);
  integer(principal.expires_at, 'OIDC principal expiry', 1, Number.MAX_SAFE_INTEGER);
  const expiresAt = Math.min(principal.expires_at, nowSeconds + policy.token.internal_assertion_ttl_seconds);
  if (expiresAt <= nowSeconds) fail('OIDC principal is expired');
  return signIdentityAssertion({
    iss: config.identity.issuer,
    aud: config.identity.audience,
    sub: principal.sub,
    tenant_id: principal.tenant_id,
    roles: [...principal.roles],
    iat: nowSeconds,
    exp: expiresAt,
    jti: principal.token_id,
  }, identitySecret, config);
}
