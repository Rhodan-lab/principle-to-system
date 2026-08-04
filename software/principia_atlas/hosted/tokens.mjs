import { createHmac, timingSafeEqual } from 'node:crypto';
import { verifyTenantConfig } from './catalog.mjs';
import { canonicalJson, fail, parseStrictJson } from './strict_json.mjs';

export const IDENTITY_CONTRACT = 'principia-atlas-identity-assertion/0.1';
export const SESSION_CONTRACT = 'principia-atlas-hosted-session/0.1';
const SUBJECT = /^[A-Za-z0-9._:@+-]{1,200}$/;
const TENANT_ID = /^[a-z][a-z0-9-]{1,62}$/;
const ROLE = /^[a-z][a-z0-9_-]{0,31}$/;
const TOKEN_HEADER = Object.freeze({ alg: 'HS256', typ: 'PAJ' });

function requireSecret(secret, label) {
  const raw = Buffer.isBuffer(secret) ? secret : Buffer.from(String(secret ?? ''), 'utf8');
  if (raw.length < 32) fail(`${label} must be at least 32 bytes`);
  return raw;
}

function base64url(raw) { return Buffer.from(raw).toString('base64url'); }
function decodePart(raw, label) {
  if (!/^[A-Za-z0-9_-]+$/.test(raw)) fail(`${label} is not base64url`);
  const decoded = Buffer.from(raw, 'base64url');
  if (decoded.toString('base64url') !== raw) fail(`${label} is not canonical base64url`);
  return decoded;
}

function signToken(payload, secret) {
  const header = base64url(canonicalJson(TOKEN_HEADER).trimEnd());
  const body = base64url(canonicalJson(payload).trimEnd());
  const signing = `${header}.${body}`;
  const signature = createHmac('sha256', secret).update(signing).digest('base64url');
  return `${signing}.${signature}`;
}

function verifyToken(token, secret, expectedContract, nowSeconds) {
  if (typeof token !== 'string' || token.length > 8192) fail('signed token is invalid');
  const parts = token.split('.');
  if (parts.length !== 3) fail('signed token is invalid');
  const signing = `${parts[0]}.${parts[1]}`;
  const expected = createHmac('sha256', secret).update(signing).digest();
  const actual = decodePart(parts[2], 'token signature');
  if (actual.length !== expected.length || !timingSafeEqual(actual, expected)) fail('signed token signature is invalid');
  const header = parseStrictJson(decodePart(parts[0], 'token header'), 'token header');
  if (canonicalJson(header) !== canonicalJson(TOKEN_HEADER)) fail('signed token header is invalid');
  const payload = parseStrictJson(decodePart(parts[1], 'token payload'), 'token payload');
  if (payload.contract !== expectedContract) fail('signed token contract is invalid');
  if (!Number.isInteger(payload.iat) || !Number.isInteger(payload.exp) || payload.iat > nowSeconds + 30 || payload.exp <= nowSeconds) fail('signed token time boundary is invalid');
  return payload;
}

function validatePrincipal(payload, config, label) {
  if (!SUBJECT.test(payload.sub ?? '') || !TENANT_ID.test(payload.tenant_id ?? '') || !config.tenants[payload.tenant_id]) fail(`${label} principal is invalid`);
  if (!Array.isArray(payload.roles) || payload.roles.length === 0 || payload.roles.some((item) => typeof item !== 'string' || !ROLE.test(item)) || new Set(payload.roles).size !== payload.roles.length) fail(`${label} roles are invalid`);
  if (typeof payload.jti !== 'string' || !/^[A-Za-z0-9_-]{16,128}$/.test(payload.jti)) fail(`${label} identifier is invalid`);
}

export function signIdentityAssertion(claims, secret, configInput) {
  const config = verifyTenantConfig(configInput); const key = requireSecret(secret, 'identity secret');
  validatePrincipal(claims, config, 'identity assertion');
  if (claims.iss !== config.identity.issuer || claims.aud !== config.identity.audience) fail('identity assertion issuer or audience is invalid');
  if (!Number.isInteger(claims.iat) || !Number.isInteger(claims.exp) || claims.exp <= claims.iat || claims.exp - claims.iat > config.identity.max_assertion_ttl_seconds) fail('identity assertion TTL is invalid');
  const payload = { contract: IDENTITY_CONTRACT, iss: claims.iss, aud: claims.aud, sub: claims.sub, tenant_id: claims.tenant_id, roles: [...claims.roles], iat: claims.iat, exp: claims.exp, jti: claims.jti };
  return signToken(payload, key);
}

export function exchangeIdentityAssertion(token, identitySecret, sessionSecret, configInput, nowSeconds = Math.floor(Date.now() / 1000)) {
  const config = verifyTenantConfig(configInput);
  const identityKey = requireSecret(identitySecret, 'identity secret'); const sessionKey = requireSecret(sessionSecret, 'session secret');
  const assertion = verifyToken(token, identityKey, IDENTITY_CONTRACT, nowSeconds);
  validatePrincipal(assertion, config, 'identity assertion');
  if (assertion.iss !== config.identity.issuer || assertion.aud !== config.identity.audience || assertion.exp - assertion.iat > config.identity.max_assertion_ttl_seconds) fail('identity assertion boundary is invalid');
  const session = { contract: SESSION_CONTRACT, sub: assertion.sub, tenant_id: assertion.tenant_id, roles: [...assertion.roles], iat: nowSeconds, exp: nowSeconds + config.session.ttl_seconds, jti: assertion.jti };
  return { token: signToken(session, sessionKey), session };
}

export function verifySession(token, sessionSecret, configInput, nowSeconds = Math.floor(Date.now() / 1000)) {
  const config = verifyTenantConfig(configInput); const key = requireSecret(sessionSecret, 'session secret');
  const session = verifyToken(token, key, SESSION_CONTRACT, nowSeconds); validatePrincipal(session, config, 'session');
  if (session.exp - session.iat !== config.session.ttl_seconds) fail('session TTL is invalid');
  return session;
}
