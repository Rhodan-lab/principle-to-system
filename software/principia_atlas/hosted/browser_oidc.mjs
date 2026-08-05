import {
  createCipheriv,
  createDecipheriv,
  createHash,
  randomBytes,
  timingSafeEqual,
} from 'node:crypto';

import { PRODUCT } from './catalog.mjs';
import { canonicalJson, exactKeys, fail, parseStrictJson, sha256Hex } from './strict_json.mjs';

export const BROWSER_OIDC_CONTRACT = 'principia-atlas-browser-oidc/0.1';
export const BROWSER_OIDC_FLOW_CONTRACT = 'principia-atlas-browser-oidc-flow/0.1';
const SHA = /^[0-9a-f]{64}$/;
const TOKEN = /^[A-Za-z0-9._~-]{1,256}$/;
const COOKIE = /^(?:__Host-)?[A-Za-z0-9!#$%&'*+.^_`|~-]{1,120}$/;
const BASE64URL = /^[A-Za-z0-9_-]+$/;
const LOOPBACK = new Set(['localhost', '127.0.0.1', '[::1]']);
const MAX_COOKIE_BYTES = 8192;
const MAX_CALLBACK_BYTES = 8192;
const MAX_ID_TOKEN_BYTES = 65536;
const FLOW_AAD = Buffer.from('principia-atlas-browser-oidc-flow-v1', 'ascii');

function boundedInteger(value, label, minimum, maximum) {
  if (!Number.isSafeInteger(value) || value < minimum || value > maximum) fail(`${label} is invalid`);
  return value;
}

function exactOrigin(value, label, { httpsOnly = false } = {}) {
  if (typeof value !== 'string' || value.length < 8 || value.length > 2048) fail(`${label} is invalid`);
  let parsed;
  try { parsed = new URL(value); } catch { fail(`${label} is invalid`); }
  if (parsed.username || parsed.password || parsed.pathname !== '/' || parsed.search || parsed.hash) fail(`${label} must be an exact origin`);
  if (!['http:', 'https:'].includes(parsed.protocol)) fail(`${label} protocol is invalid`);
  if (httpsOnly && parsed.protocol !== 'https:') fail(`${label} must use HTTPS`);
  if (parsed.protocol === 'http:' && !LOOPBACK.has(parsed.hostname)) fail(`${label} HTTP is limited to loopback`);
  return parsed.origin;
}

function exactHttpsUrl(value, label) {
  if (typeof value !== 'string' || value.length < 8 || value.length > 2048) fail(`${label} is invalid`);
  let parsed;
  try { parsed = new URL(value); } catch { fail(`${label} is invalid`); }
  if (parsed.protocol !== 'https:' || parsed.username || parsed.password || parsed.search || parsed.hash) fail(`${label} must be an HTTPS URL without credentials, query, or fragment`);
  return parsed.toString();
}

function exactPath(value, label) {
  if (typeof value !== 'string' || value.length < 1 || value.length > 512 || !value.startsWith('/') || value.startsWith('//')) fail(`${label} is invalid`);
  let parsed;
  try { parsed = new URL(value, 'https://path.invalid'); } catch { fail(`${label} is invalid`); }
  if (parsed.origin !== 'https://path.invalid' || parsed.pathname !== value || parsed.search || parsed.hash || /[\\\u0000-\u001f\u007f]/.test(value)) fail(`${label} must be a normalized path`);
  return value;
}

function normalizeReturnTo(value, config) {
  const candidate = value === null || value === undefined || value === '' ? config.default_return_to : value;
  if (typeof candidate !== 'string' || candidate.length > 2048 || !candidate.startsWith('/') || candidate.startsWith('//')) fail('browser OIDC return path is invalid');
  let parsed;
  try { parsed = new URL(candidate, config.public_origin); } catch { fail('browser OIDC return path is invalid'); }
  if (parsed.origin !== config.public_origin || parsed.username || parsed.password || parsed.hash) fail('browser OIDC return path is cross-origin or malformed');
  if ([config.login_path, config.callback_path].includes(parsed.pathname)) fail('browser OIDC return path targets an authentication route');
  return `${parsed.pathname}${parsed.search}`;
}

function validateScopes(value) {
  if (!Array.isArray(value) || value.length < 1 || value.length > 16) fail('browser OIDC scopes are invalid');
  const seen = new Set();
  for (const scope of value) {
    if (typeof scope !== 'string' || !TOKEN.test(scope) || seen.has(scope)) fail('browser OIDC scope is invalid or duplicated');
    seen.add(scope);
  }
  if (!seen.has('openid')) fail('browser OIDC scopes must include openid');
  if (seen.has('offline_access')) fail('browser OIDC offline_access is prohibited');
}

export function verifyBrowserOidcConfig(input) {
  const value = typeof input === 'string' || Buffer.isBuffer(input) ? parseStrictJson(input, 'browser OIDC config') : structuredClone(input);
  exactKeys(value, [
    'contract', 'product', 'issuer', 'public_origin', 'authorization_endpoint', 'token_endpoint',
    'client_id', 'client_auth_method', 'scopes', 'login_path', 'callback_path',
    'default_return_to', 'flow_ttl_seconds', 'token_timeout_ms', 'token_max_bytes',
    'cookie', 'config_id',
  ], 'browser OIDC config');
  if (value.contract !== BROWSER_OIDC_CONTRACT || value.product !== PRODUCT) fail('browser OIDC contract is invalid');
  const unsigned = structuredClone(value); delete unsigned.config_id;
  if (!SHA.test(value.config_id) || sha256Hex(canonicalJson(unsigned)) !== value.config_id) fail('browser OIDC config seal is invalid');
  if (value.issuer.endsWith('/')) fail('browser OIDC issuer must not have a trailing slash');
  value.issuer = exactHttpsUrl(value.issuer, 'browser OIDC issuer').replace(/\/$/, '');
  value.public_origin = exactOrigin(value.public_origin, 'browser OIDC public origin');
  value.authorization_endpoint = exactHttpsUrl(value.authorization_endpoint, 'browser OIDC authorization endpoint');
  value.token_endpoint = exactHttpsUrl(value.token_endpoint, 'browser OIDC token endpoint');
  if (typeof value.client_id !== 'string' || !TOKEN.test(value.client_id)) fail('browser OIDC client ID is invalid');
  if (!['none', 'client_secret_post'].includes(value.client_auth_method)) fail('browser OIDC client authentication method is invalid');
  validateScopes(value.scopes);
  value.login_path = exactPath(value.login_path, 'browser OIDC login path');
  if (value.login_path === '/') fail('browser OIDC login path cannot be root');
  value.callback_path = exactPath(value.callback_path, 'browser OIDC callback path');
  if (value.callback_path === '/') fail('browser OIDC callback path cannot be root');
  if (value.login_path === value.callback_path) fail('browser OIDC routes must be distinct');
  value.default_return_to = exactPath(value.default_return_to, 'browser OIDC default return path');
  if ([value.login_path, value.callback_path].includes(value.default_return_to)) fail('browser OIDC default return path targets an authentication route');
  boundedInteger(value.flow_ttl_seconds, 'browser OIDC flow TTL', 60, 600);
  boundedInteger(value.token_timeout_ms, 'browser OIDC token timeout', 500, 15000);
  boundedInteger(value.token_max_bytes, 'browser OIDC token response limit', 1024, 262144);
  exactKeys(value.cookie, ['name', 'secure', 'same_site'], 'browser OIDC cookie');
  if (typeof value.cookie.name !== 'string' || !COOKIE.test(value.cookie.name)) fail('browser OIDC cookie name is invalid');
  if (typeof value.cookie.secure !== 'boolean' || value.cookie.same_site !== 'Lax') fail('browser OIDC cookie policy is invalid');
  const publicUrl = new URL(value.public_origin);
  if (publicUrl.protocol === 'https:' && value.cookie.secure !== true) fail('HTTPS browser OIDC origin requires a secure flow cookie');
  if (value.cookie.name.startsWith('__Host-') && value.cookie.secure !== true) fail('__Host browser OIDC cookie requires Secure');
  return Object.freeze(value);
}

export function sealBrowserOidcConfig(input) {
  const value = structuredClone(input);
  delete value.config_id;
  value.config_id = sha256Hex(canonicalJson(value));
  return verifyBrowserOidcConfig(value);
}

function normalizeSecret(value, label, { required = true } = {}) {
  if ((value === null || value === undefined) && !required) return null;
  const raw = Buffer.isBuffer(value) ? Buffer.from(value) : Buffer.from(String(value ?? ''), 'utf8');
  if (raw.length < 32 || raw.length > 4096 || raw.includes(0x00) || raw.includes(0x0a) || raw.includes(0x0d)) fail(`${label} is invalid`);
  return raw;
}

function flowKey(secret, configId) {
  return createHash('sha256').update(FLOW_AAD).update(secret).update(configId, 'ascii').digest();
}

function encodeFlow(payload, key, configId) {
  const iv = randomBytes(12);
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  cipher.setAAD(Buffer.from(configId, 'ascii'));
  const encrypted = Buffer.concat([cipher.update(canonicalJson(payload), 'utf8'), cipher.final()]);
  const tag = cipher.getAuthTag();
  return `v1.${iv.toString('base64url')}.${encrypted.toString('base64url')}.${tag.toString('base64url')}`;
}

function decodeBase64url(value, label, maxBytes) {
  if (typeof value !== 'string' || !BASE64URL.test(value) || value.length % 4 === 1) fail(`${label} is invalid`);
  const raw = Buffer.from(value, 'base64url');
  if (raw.length > maxBytes || raw.toString('base64url') !== value) fail(`${label} is invalid`);
  return raw;
}

function decodeFlow(value, key, configId) {
  if (typeof value !== 'string' || Buffer.byteLength(value, 'utf8') > MAX_COOKIE_BYTES) fail('browser OIDC flow cookie is invalid');
  const parts = value.split('.');
  if (parts.length !== 4 || parts[0] !== 'v1') fail('browser OIDC flow cookie is invalid');
  const iv = decodeBase64url(parts[1], 'browser OIDC flow IV', 12);
  const encrypted = decodeBase64url(parts[2], 'browser OIDC flow payload', 4096);
  const tag = decodeBase64url(parts[3], 'browser OIDC flow tag', 16);
  if (iv.length !== 12 || tag.length !== 16) fail('browser OIDC flow cookie is invalid');
  let raw;
  try {
    const decipher = createDecipheriv('aes-256-gcm', key, iv);
    decipher.setAAD(Buffer.from(configId, 'ascii'));
    decipher.setAuthTag(tag);
    raw = Buffer.concat([decipher.update(encrypted), decipher.final()]);
  } catch { fail('browser OIDC flow cookie authentication failed'); }
  const payload = parseStrictJson(raw, 'browser OIDC flow cookie');
  exactKeys(payload, ['contract', 'state', 'nonce', 'code_verifier', 'return_to', 'issued_at', 'expires_at'], 'browser OIDC flow cookie');
  if (payload.contract !== BROWSER_OIDC_FLOW_CONTRACT || !BASE64URL.test(payload.state) || !BASE64URL.test(payload.nonce)) fail('browser OIDC flow identity is invalid');
  if (typeof payload.code_verifier !== 'string' || payload.code_verifier.length < 43 || payload.code_verifier.length > 128 || !/^[A-Za-z0-9._~-]+$/.test(payload.code_verifier)) fail('browser OIDC PKCE verifier is invalid');
  if (!Number.isSafeInteger(payload.issued_at) || !Number.isSafeInteger(payload.expires_at) || payload.expires_at <= payload.issued_at) fail('browser OIDC flow time is invalid');
  return payload;
}

function parseCookies(header) {
  const output = new Map();
  for (const pair of String(header ?? '').split(';')) {
    const position = pair.indexOf('=');
    if (position < 1) continue;
    const key = pair.slice(0, position).trim();
    const value = pair.slice(position + 1).trim();
    if (!key) continue;
    if (output.has(key)) fail('browser OIDC cookie header contains a duplicate cookie');
    output.set(key, value);
  }
  return output;
}

function constantEquals(left, right) {
  if (typeof left !== 'string' || typeof right !== 'string') return false;
  const a = Buffer.from(left, 'utf8'); const b = Buffer.from(right, 'utf8');
  return a.length === b.length && timingSafeEqual(a, b);
}

function cookieAttributes(config, value, maxAge) {
  const attributes = [`${config.cookie.name}=${value}`, 'Path=/', 'HttpOnly', `SameSite=${config.cookie.same_site}`, `Max-Age=${maxAge}`];
  if (config.cookie.secure) attributes.push('Secure');
  return attributes.join('; ');
}

function singleParameter(searchParams, name, { required = false, maxLength = 4096 } = {}) {
  const values = searchParams.getAll(name);
  if (values.length > 1) fail(`browser OIDC callback contains duplicate ${name}`);
  if (values.length === 0) {
    if (required) fail(`browser OIDC callback is missing ${name}`);
    return null;
  }
  const value = values[0];
  if (!value || value.length > maxLength || /[\u0000-\u001f\u007f]/.test(value)) fail(`browser OIDC callback ${name} is invalid`);
  return value;
}

async function readBoundedBody(response, limit) {
  if (!response.body) return Buffer.alloc(0);
  const reader = response.body.getReader();
  const chunks = []; let total = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > limit) fail('browser OIDC token response exceeds resource limit');
      chunks.push(Buffer.from(value));
    }
  } finally { reader.releaseLock(); }
  return Buffer.concat(chunks, total);
}

function jwtPayload(token) {
  if (typeof token !== 'string' || token.length > MAX_ID_TOKEN_BYTES || !/^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/.test(token)) fail('browser OIDC ID token is invalid');
  const parts = token.split('.');
  return parseStrictJson(decodeBase64url(parts[1], 'browser OIDC JWT payload', MAX_ID_TOKEN_BYTES), 'browser OIDC JWT payload');
}

export function createBrowserOidcFlow({
  config: configInput,
  flowSecret,
  clientSecret = null,
  now = () => Math.floor(Date.now() / 1000),
  fetchImpl = globalThis.fetch,
  random = randomBytes,
} = {}) {
  const config = verifyBrowserOidcConfig(configInput);
  if (typeof fetchImpl !== 'function') fail('browser OIDC fetch implementation is invalid');
  if (typeof now !== 'function' || typeof random !== 'function') fail('browser OIDC runtime dependency is invalid');
  const flowRaw = normalizeSecret(flowSecret, 'browser OIDC flow secret');
  const clientRaw = normalizeSecret(clientSecret, 'browser OIDC client secret', { required: config.client_auth_method === 'client_secret_post' });
  if (config.client_auth_method === 'none' && clientRaw !== null) fail('browser OIDC client secret is not allowed for public client mode');
  const key = flowKey(flowRaw, config.config_id);
  flowRaw.fill(0);
  let closed = false;
  const ensureOpen = () => { if (closed) fail('browser OIDC flow is closed'); };

  const begin = (returnTo = null) => {
    ensureOpen();
    const current = now();
    if (!Number.isSafeInteger(current)) fail('browser OIDC clock is invalid');
    const state = random(32).toString('base64url');
    const nonce = random(32).toString('base64url');
    const codeVerifier = random(48).toString('base64url');
    if (!BASE64URL.test(state) || !BASE64URL.test(nonce) || codeVerifier.length < 43) fail('browser OIDC random source is invalid');
    const payload = {
      contract: BROWSER_OIDC_FLOW_CONTRACT,
      state,
      nonce,
      code_verifier: codeVerifier,
      return_to: normalizeReturnTo(returnTo, config),
      issued_at: current,
      expires_at: current + config.flow_ttl_seconds,
    };
    const authorization = new URL(config.authorization_endpoint);
    authorization.searchParams.set('response_type', 'code');
    authorization.searchParams.set('client_id', config.client_id);
    authorization.searchParams.set('redirect_uri', `${config.public_origin}${config.callback_path}`);
    authorization.searchParams.set('scope', config.scopes.join(' '));
    authorization.searchParams.set('state', state);
    authorization.searchParams.set('nonce', nonce);
    authorization.searchParams.set('code_challenge', createHash('sha256').update(codeVerifier, 'ascii').digest('base64url'));
    authorization.searchParams.set('code_challenge_method', 'S256');
    return Object.freeze({
      location: authorization.toString(),
      set_cookie: cookieAttributes(config, encodeFlow(payload, key, config.config_id), config.flow_ttl_seconds),
      expires_at: payload.expires_at,
    });
  };

  const complete = async (callbackUrl, cookieHeader) => {
    ensureOpen();
    if (typeof callbackUrl !== 'string' || Buffer.byteLength(callbackUrl, 'utf8') > MAX_CALLBACK_BYTES) fail('browser OIDC callback URL is invalid');
    let callback;
    try { callback = new URL(callbackUrl, config.public_origin); } catch { fail('browser OIDC callback URL is invalid'); }
    if (callback.origin !== config.public_origin || callback.pathname !== config.callback_path || callback.hash) fail('browser OIDC callback route is invalid');
    const cookies = parseCookies(cookieHeader);
    const encrypted = cookies.get(config.cookie.name);
    if (!encrypted) fail('browser OIDC flow cookie is missing');
    const flow = decodeFlow(encrypted, key, config.config_id);
    const current = now();
    if (!Number.isSafeInteger(current) || current < flow.issued_at - 30 || current > flow.expires_at) fail('browser OIDC flow expired');
    const state = singleParameter(callback.searchParams, 'state', { required: true, maxLength: 256 });
    if (!constantEquals(state, flow.state)) fail('browser OIDC state mismatch');
    const returnedIssuer = singleParameter(callback.searchParams, 'iss', { maxLength: 2048 });
    if (returnedIssuer !== null && returnedIssuer.replace(/\/$/, '') !== config.issuer) fail('browser OIDC callback issuer mismatch');
    const error = singleParameter(callback.searchParams, 'error', { maxLength: 256 });
    if (error !== null) {
      return Object.freeze({ status: 'authorization_error', return_to: flow.return_to, clear_cookie: cookieAttributes(config, '', 0) });
    }
    const code = singleParameter(callback.searchParams, 'code', { required: true, maxLength: 4096 });
    const body = new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      redirect_uri: `${config.public_origin}${config.callback_path}`,
      client_id: config.client_id,
      code_verifier: flow.code_verifier,
    });
    if (clientRaw !== null) body.set('client_secret', clientRaw.toString('utf8'));
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), config.token_timeout_ms);
    timer.unref?.();
    let response;
    try {
      response = await fetchImpl(config.token_endpoint, {
        method: 'POST',
        redirect: 'error',
        headers: { Accept: 'application/json', 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString(),
        signal: controller.signal,
      });
    } catch { fail('browser OIDC token exchange failed'); }
    finally { clearTimeout(timer); }
    const raw = await readBoundedBody(response, config.token_max_bytes);
    if (response.status !== 200) fail('browser OIDC token endpoint rejected the code');
    const contentType = String(response.headers.get('content-type') ?? '').toLowerCase();
    if (!/^application\/json(?:\s*;|$)/.test(contentType)) fail('browser OIDC token response content type is invalid');
    const tokenResponse = parseStrictJson(raw, 'browser OIDC token response');
    if (!tokenResponse || typeof tokenResponse !== 'object' || Array.isArray(tokenResponse)) fail('browser OIDC token response is invalid');
    if ('refresh_token' in tokenResponse) fail('browser OIDC refresh tokens are prohibited');
    if ('token_type' in tokenResponse && String(tokenResponse.token_type).toLowerCase() !== 'bearer') fail('browser OIDC token type is invalid');
    const idToken = tokenResponse.id_token;
    const payload = jwtPayload(idToken);
    if (!constantEquals(payload.nonce, flow.nonce)) fail('browser OIDC nonce mismatch');
    if (payload.iss !== config.issuer) fail('browser OIDC ID token issuer mismatch');
    return Object.freeze({
      status: 'complete',
      id_token: idToken,
      return_to: flow.return_to,
      clear_cookie: cookieAttributes(config, '', 0),
    });
  };

  const close = () => {
    if (closed) return;
    closed = true;
    key.fill(0);
    clientRaw?.fill(0);
  };

  return Object.freeze({
    config,
    descriptor: Object.freeze({
      contract: BROWSER_OIDC_CONTRACT,
      config_id: config.config_id,
      issuer: config.issuer,
      login_path: config.login_path,
      callback_path: config.callback_path,
      client_auth_method: config.client_auth_method,
    }),
    begin,
    complete,
    clear_cookie: () => cookieAttributes(config, '', 0),
    close,
  });
}
