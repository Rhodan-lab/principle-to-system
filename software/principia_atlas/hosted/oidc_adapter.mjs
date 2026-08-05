import { createPublicKey, verify as verifySignature } from 'node:crypto';
import { verifyTenantConfig } from './catalog.mjs';
import { signIdentityAssertion } from './tokens.mjs';
import { canonicalJson, exactKeys, fail, parseStrictJson, sha256Hex } from './strict_json.mjs';

export const OIDC_ADAPTER_CONTRACT = 'principia-atlas-oidc-adapter/0.1';
export const OIDC_JWKS_CONTRACT = 'principia-atlas-oidc-jwks-snapshot/0.1';
const CLAIM = /^[A-Za-z_][A-Za-z0-9_.-]{0,63}$/;
const EXTERNAL_VALUE = /^[A-Za-z0-9._:@+/-]{1,200}$/;
const INTERNAL_TENANT = /^[a-z][a-z0-9-]{1,62}$/;
const INTERNAL_ROLE = /^[a-z][a-z0-9_-]{0,31}$/;
const KID = /^[A-Za-z0-9._:-]{1,128}$/;
const BASE64URL = /^[A-Za-z0-9_-]+$/;
const SUBJECT_PREFIX = /^[A-Za-z0-9._:@+-]{1,40}$/;
const MAX_TOKEN_BYTES = 16 * 1024;

function integer(value, label, minimum, maximum) {
  if (!Number.isSafeInteger(value) || value < minimum || value > maximum) fail(`${label} is invalid`);
  return value;
}

function string(value, pattern, label) {
  if (typeof value !== 'string' || !pattern.test(value)) fail(`${label} is invalid`);
  return value;
}

function sortedUniqueStrings(value, pattern, label, maximum = 64) {
  if (!Array.isArray(value) || value.length === 0 || value.length > maximum) fail(`${label} is invalid`);
  const output = value.map((item) => string(item, pattern, label));
  if (new Set(output).size !== output.length) fail(`${label} contains duplicates`);
  return [...output].sort();
}

function mapping(value, sourcePattern, targetPattern, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail(`${label} is invalid`);
  const entries = Object.entries(value);
  if (entries.length === 0 || entries.length > 1024) fail(`${label} is invalid`);
  const output = {};
  for (const [source, target] of entries.sort(([left], [right]) => left.localeCompare(right))) {
    string(source, sourcePattern, `${label} source`);
    string(target, targetPattern, `${label} target`);
    output[source] = target;
  }
  return output;
}

export function sealOidcAdapterConfig(unsignedInput) {
  const unsigned = { ...unsignedInput };
  delete unsigned.config_id;
  return verifyOidcAdapterConfig({ ...unsigned, config_id: sha256Hex(canonicalJson(unsigned)) });
}

export function verifyOidcAdapterConfig(input) {
  exactKeys(input, [
    'contract', 'issuer', 'audience', 'algorithms', 'max_token_ttl_seconds',
    'clock_skew_seconds', 'subject_claim', 'subject_prefix', 'tenant_claim',
    'roles_claim', 'tenants', 'roles', 'config_id',
  ], 'OIDC adapter config');
  if (input.contract !== OIDC_ADAPTER_CONTRACT) fail('OIDC adapter config contract is invalid');
  if (typeof input.issuer !== 'string' || !/^https:\/\/[A-Za-z0-9.-]+(?::\d+)?(?:\/[^\s]*)?$/.test(input.issuer) || input.issuer.endsWith('/')) fail('OIDC issuer is invalid');
  if (typeof input.audience !== 'string' || input.audience.length === 0 || input.audience.length > 256 || /[\u0000-\u001f\u007f]/.test(input.audience)) fail('OIDC audience is invalid');
  const algorithms = sortedUniqueStrings(input.algorithms, /^RS256$/, 'OIDC algorithms', 1);
  integer(input.max_token_ttl_seconds, 'OIDC maximum token TTL', 60, 86400);
  integer(input.clock_skew_seconds, 'OIDC clock skew', 0, 300);
  string(input.subject_claim, CLAIM, 'OIDC subject claim');
  string(input.subject_prefix, SUBJECT_PREFIX, 'OIDC subject prefix');
  string(input.tenant_claim, CLAIM, 'OIDC tenant claim');
  string(input.roles_claim, CLAIM, 'OIDC roles claim');
  if (new Set([input.subject_claim, input.tenant_claim, input.roles_claim]).size !== 3) fail('OIDC claim names must be distinct');
  const tenants = mapping(input.tenants, EXTERNAL_VALUE, INTERNAL_TENANT, 'OIDC tenant mapping');
  const roles = mapping(input.roles, EXTERNAL_VALUE, INTERNAL_ROLE, 'OIDC role mapping');
  const unsigned = {
    contract: input.contract,
    issuer: input.issuer,
    audience: input.audience,
    algorithms,
    max_token_ttl_seconds: input.max_token_ttl_seconds,
    clock_skew_seconds: input.clock_skew_seconds,
    subject_claim: input.subject_claim,
    subject_prefix: input.subject_prefix,
    tenant_claim: input.tenant_claim,
    roles_claim: input.roles_claim,
    tenants,
    roles,
  };
  if (!/^[0-9a-f]{64}$/.test(input.config_id ?? '') || input.config_id !== sha256Hex(canonicalJson(unsigned))) fail('OIDC adapter config seal is invalid');
  return Object.freeze({ ...unsigned, config_id: input.config_id });
}

function decodeBase64url(value, label) {
  if (typeof value !== 'string' || !BASE64URL.test(value)) fail(`${label} is not base64url`);
  const raw = Buffer.from(value, 'base64url');
  if (raw.toString('base64url') !== value) fail(`${label} is not canonical base64url`);
  return raw;
}

function normalizeJwk(input) {
  exactKeys(input, ['kty', 'use', 'alg', 'kid', 'n', 'e'], 'OIDC JWK');
  if (input.kty !== 'RSA' || input.use !== 'sig' || input.alg !== 'RS256') fail('OIDC JWK boundary is invalid');
  string(input.kid, KID, 'OIDC JWK identifier');
  decodeBase64url(input.n, 'OIDC JWK modulus');
  decodeBase64url(input.e, 'OIDC JWK exponent');
  let publicKey;
  try { publicKey = createPublicKey({ key: input, format: 'jwk' }); }
  catch { fail('OIDC JWK public key is invalid'); }
  if (publicKey.asymmetricKeyType !== 'rsa' || (publicKey.asymmetricKeyDetails?.modulusLength ?? 0) < 2048) fail('OIDC JWK RSA key is too small');
  return { jwk: Object.freeze({ ...input }), publicKey };
}

export function verifyOidcJwksSnapshot(input) {
  exactKeys(input, ['contract', 'issuer', 'keys', 'snapshot_id'], 'OIDC JWKS snapshot');
  if (input.contract !== OIDC_JWKS_CONTRACT) fail('OIDC JWKS snapshot contract is invalid');
  if (typeof input.issuer !== 'string' || input.issuer.length === 0) fail('OIDC JWKS issuer is invalid');
  if (!Array.isArray(input.keys) || input.keys.length === 0 || input.keys.length > 32) fail('OIDC JWKS key set is invalid');
  const normalized = input.keys.map(normalizeJwk).sort((left, right) => left.jwk.kid.localeCompare(right.jwk.kid));
  const identifiers = normalized.map((item) => item.jwk.kid);
  if (new Set(identifiers).size !== identifiers.length) fail('OIDC JWKS contains duplicate key identifiers');
  const unsigned = { contract: input.contract, issuer: input.issuer, keys: normalized.map((item) => item.jwk) };
  if (!/^[0-9a-f]{64}$/.test(input.snapshot_id ?? '') || input.snapshot_id !== sha256Hex(canonicalJson(unsigned))) fail('OIDC JWKS snapshot seal is invalid');
  const keysById = Object.freeze(Object.fromEntries(normalized.map((item) => [item.jwk.kid, item.publicKey])));
  return Object.freeze({ ...unsigned, snapshot_id: input.snapshot_id, keys_by_id: keysById });
}

export function sealOidcJwksSnapshot(unsignedInput) {
  const normalized = {
    contract: unsignedInput.contract,
    issuer: unsignedInput.issuer,
    keys: [...unsignedInput.keys].sort((left, right) => String(left.kid).localeCompare(String(right.kid))),
  };
  return verifyOidcJwksSnapshot({ ...normalized, snapshot_id: sha256Hex(canonicalJson(normalized)) });
}

function verifyAudience(payload, config) {
  if (typeof payload.aud === 'string') {
    if (payload.aud !== config.audience) fail('OIDC token audience is invalid');
    return;
  }
  if (!Array.isArray(payload.aud) || payload.aud.length === 0 || payload.aud.length > 16 || payload.aud.some((item) => typeof item !== 'string') || new Set(payload.aud).size !== payload.aud.length || !payload.aud.includes(config.audience)) fail('OIDC token audience is invalid');
  if (payload.aud.length > 1 && payload.azp !== config.audience) fail('OIDC token authorized party is invalid');
}

function verifyTime(payload, config, nowSeconds) {
  integer(nowSeconds, 'OIDC current time', 0, Number.MAX_SAFE_INTEGER);
  integer(payload.iat, 'OIDC token issued time', 0, Number.MAX_SAFE_INTEGER);
  integer(payload.exp, 'OIDC token expiry', 0, Number.MAX_SAFE_INTEGER);
  if (payload.nbf !== undefined) integer(payload.nbf, 'OIDC token not-before time', 0, Number.MAX_SAFE_INTEGER);
  if (payload.exp <= payload.iat || payload.exp - payload.iat > config.max_token_ttl_seconds) fail('OIDC token TTL is invalid');
  if (payload.iat > nowSeconds + config.clock_skew_seconds) fail('OIDC token is issued in the future');
  if (payload.nbf !== undefined && payload.nbf > nowSeconds + config.clock_skew_seconds) fail('OIDC token is not active');
  if (payload.exp <= nowSeconds - config.clock_skew_seconds) fail('OIDC token is expired');
}

function verifyJwt(token, jwks, config, nowSeconds) {
  if (typeof token !== 'string' || Buffer.byteLength(token) > MAX_TOKEN_BYTES) fail('OIDC token is invalid');
  const parts = token.split('.');
  if (parts.length !== 3) fail('OIDC token is invalid');
  const header = parseStrictJson(decodeBase64url(parts[0], 'OIDC token header'), 'OIDC token header');
  const headerKeys = Object.keys(header).sort();
  if (JSON.stringify(headerKeys) !== JSON.stringify(['alg', 'kid']) && JSON.stringify(headerKeys) !== JSON.stringify(['alg', 'kid', 'typ'])) fail('OIDC token header fields are invalid');
  if (!config.algorithms.includes(header.alg) || header.alg !== 'RS256') fail('OIDC token algorithm is invalid');
  string(header.kid, KID, 'OIDC token key identifier');
  if (header.typ !== undefined && !['JWT', 'at+jwt'].includes(header.typ)) fail('OIDC token type is invalid');
  const key = jwks.keys_by_id[header.kid];
  if (!key) fail('OIDC token key identifier is unknown');
  const signature = decodeBase64url(parts[2], 'OIDC token signature');
  if (!verifySignature('RSA-SHA256', Buffer.from(`${parts[0]}.${parts[1]}`, 'ascii'), key, signature)) fail('OIDC token signature is invalid');
  const payload = parseStrictJson(decodeBase64url(parts[1], 'OIDC token payload'), 'OIDC token payload');
  if (payload.iss !== config.issuer || jwks.issuer !== config.issuer) fail('OIDC token issuer is invalid');
  verifyAudience(payload, config);
  verifyTime(payload, config, nowSeconds);
  return payload;
}

export function adaptOidcJwt({ token, jwks: jwksInput, adapterConfig: adapterConfigInput, tenantConfig: tenantConfigInput, identitySecret, nowSeconds = Math.floor(Date.now() / 1000) }) {
  const config = verifyOidcAdapterConfig(adapterConfigInput);
  const jwks = verifyOidcJwksSnapshot(jwksInput);
  const tenantConfig = verifyTenantConfig(tenantConfigInput);
  const payload = verifyJwt(token, jwks, config, nowSeconds);
  const externalSubject = string(payload[config.subject_claim], EXTERNAL_VALUE, 'OIDC subject');
  const externalTenant = string(payload[config.tenant_claim], EXTERNAL_VALUE, 'OIDC tenant value');
  const tenantId = config.tenants[externalTenant];
  if (!tenantId || !tenantConfig.tenants[tenantId]) fail('OIDC tenant is not entitled');
  const externalRoles = sortedUniqueStrings(payload[config.roles_claim], EXTERNAL_VALUE, 'OIDC roles', 32);
  const roles = externalRoles.map((role) => config.roles[role]);
  if (roles.some((role) => !role)) fail('OIDC role is not mapped');
  const normalizedRoles = [...new Set(roles)].sort();
  if (normalizedRoles.length === 0) fail('OIDC principal has no mapped role');
  const subject = `${config.subject_prefix}${externalSubject}`;
  if (subject.length > 200) fail('OIDC mapped subject is too long');
  const expiresAt = Math.min(payload.exp, nowSeconds + tenantConfig.identity.max_assertion_ttl_seconds);
  const assertion = signIdentityAssertion({
    iss: tenantConfig.identity.issuer,
    aud: tenantConfig.identity.audience,
    sub: subject,
    tenant_id: tenantId,
    roles: normalizedRoles,
    iat: nowSeconds,
    exp: expiresAt,
    jti: `oidc_${sha256Hex(token)}`,
  }, identitySecret, tenantConfig);
  return Object.freeze({
    assertion,
    subject,
    tenant_id: tenantId,
    roles: Object.freeze(normalizedRoles),
    expires_at: expiresAt,
    adapter_config_id: config.config_id,
    jwks_snapshot_id: jwks.snapshot_id,
  });
}
