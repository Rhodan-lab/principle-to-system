import { createServer as createHttpServer } from 'node:http';
import { randomUUID } from 'node:crypto';

import { verifyTenantConfig } from './catalog.mjs';
import { canonicalJson, fail } from './strict_json.mjs';
import { verifySession } from './tokens.mjs';

export const SAAS_HOSTED_RUNTIME_CONTRACT = 'principia-atlas-saas-hosted-runtime/0.1';
const MAX_URL_BYTES = 8192;
const MAX_UPSTREAM_BYTES = 64 * 1024 * 1024;
const LOOPBACK = new Set(['localhost', '127.0.0.1', '::1', '[::1]']);
const PROGRESS_MUTATION = /^\/api\/saas\/progress\/[a-z0-9-]{2,64}\/[a-z_]{2,32}$/;
const FORWARDED_REQUEST_HEADERS = new Set([
  'accept', 'accept-language', 'authorization', 'cookie', 'if-none-match', 'user-agent',
]);
const FORWARDED_RESPONSE_HEADERS = new Set([
  'allow', 'cache-control', 'content-disposition', 'content-security-policy', 'content-type',
  'cross-origin-opener-policy', 'cross-origin-resource-policy', 'etag', 'permissions-policy',
  'referrer-policy', 'retry-after', 'set-cookie', 'x-content-type-options', 'x-frame-options',
  'x-request-id',
]);
const APPLICATION_RESPONSE_HEADERS = new Set(['allow', 'idempotency-replayed', 'retry-after']);

function verifyCoreOrigin(value) {
  if (typeof value !== 'string' || value.length < 8 || value.length > 2048) fail('SaaS hosted core origin is invalid');
  let parsed;
  try { parsed = new URL(value); } catch { fail('SaaS hosted core origin is invalid'); }
  if (!['http:', 'https:'].includes(parsed.protocol)
    || parsed.username || parsed.password || parsed.pathname !== '/' || parsed.search || parsed.hash
    || !LOOPBACK.has(parsed.hostname)) {
    fail('SaaS hosted core must be an exact loopback HTTP origin');
  }
  return parsed.origin;
}

function validateApplicationApi(value) {
  if (!value || typeof value.handle !== 'function' || typeof value.close !== 'function'
    || !value.descriptor || typeof value.descriptor.contract !== 'string') {
    fail('SaaS application API is invalid');
  }
  return value;
}

function validateAuthState(value) {
  if (!value || typeof value.validateSession !== 'function' || typeof value.health !== 'function') {
    fail('SaaS hosted auth state is invalid');
  }
  return value;
}

function securityHeaders(response, requestId) {
  response.setHeader('Content-Security-Policy', "default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'; object-src 'none'");
  response.setHeader('Referrer-Policy', 'no-referrer');
  response.setHeader('X-Content-Type-Options', 'nosniff');
  response.setHeader('X-Frame-Options', 'DENY');
  response.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
  response.setHeader('Cross-Origin-Resource-Policy', 'same-origin');
  response.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), payment=(), usb=(), serial=()');
  response.setHeader('Cache-Control', 'private, no-store');
  response.setHeader('X-Request-ID', requestId);
}

function sendRaw(response, status, contentType, raw, requestId, extraHeaders = {}) {
  const body = Buffer.isBuffer(raw) ? raw : Buffer.from(String(raw), 'utf8');
  securityHeaders(response, requestId);
  response.statusCode = status;
  response.setHeader('Content-Type', contentType);
  response.setHeader('Content-Length', String(body.length));
  for (const [name, value] of Object.entries(extraHeaders)) {
    if (APPLICATION_RESPONSE_HEADERS.has(name.toLowerCase())) response.setHeader(name, value);
  }
  response.end(body);
}

function sendJson(response, status, value, requestId, extraHeaders = {}) {
  sendRaw(response, status, 'application/json; charset=utf-8', canonicalJson(value), requestId, extraHeaders);
}

function parseCookies(header) {
  const output = {};
  for (const pair of String(header ?? '').split(';')) {
    const position = pair.indexOf('=');
    if (position < 1) continue;
    const key = pair.slice(0, position).trim();
    const value = pair.slice(position + 1).trim();
    if (key && !(key in output)) output[key] = value;
  }
  return output;
}

function hasRequestBody(request) {
  if (request.headers['transfer-encoding']) return true;
  const raw = request.headers['content-length'];
  if (raw === undefined) return false;
  return raw !== '0';
}

function forwardedRequestHeaders(request, coreOrigin) {
  const headers = new Headers();
  for (const [name, value] of Object.entries(request.headers)) {
    if (!FORWARDED_REQUEST_HEADERS.has(name) || value === undefined) continue;
    headers.set(name, Array.isArray(value) ? value.join(', ') : value);
  }
  headers.set('Origin', coreOrigin);
  return headers;
}

function copyResponseHeaders(upstream, response) {
  for (const [name, value] of upstream.headers.entries()) {
    if (FORWARDED_RESPONSE_HEADERS.has(name) && name !== 'set-cookie') response.setHeader(name, value);
  }
  const setCookie = upstream.headers.getSetCookie?.() ?? [];
  if (setCookie.length) response.setHeader('Set-Cookie', setCookie);
  else {
    const cookie = upstream.headers.get('set-cookie');
    if (cookie) response.setHeader('Set-Cookie', cookie);
  }
}

async function readBoundedResponse(response, limit = MAX_UPSTREAM_BYTES) {
  if (!response.body) return Buffer.alloc(0);
  const declared = response.headers.get('content-length');
  if (declared !== null && (!/^\d+$/.test(declared) || Number(declared) > limit)) {
    fail('SaaS hosted core response exceeds resource limit');
  }
  const reader = response.body.getReader();
  const chunks = [];
  let total = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > limit) fail('SaaS hosted core response exceeds resource limit');
      chunks.push(Buffer.from(value));
    }
  } finally {
    reader.releaseLock();
  }
  return Buffer.concat(chunks, total);
}

async function upstreamFetch(fetchImpl, coreOrigin, path, options, timeoutMs) {
  const target = new URL(path, coreOrigin);
  if (target.origin !== coreOrigin) fail('SaaS hosted core path escaped its origin');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  timer.unref?.();
  try {
    return await fetchImpl(target, { ...options, redirect: 'manual', signal: controller.signal });
  } catch {
    fail('SaaS hosted core request failed');
  } finally {
    clearTimeout(timer);
  }
}

export function createSaasHostedRuntimeServer({
  config: configInput,
  authState: authStateInput,
  sessionSecret,
  applicationApi: applicationApiInput,
  coreOrigin,
  fetchImpl = globalThis.fetch,
  now = () => Math.floor(Date.now() / 1000),
  timeoutMs = 10000,
} = {}) {
  const config = verifyTenantConfig(configInput);
  const authState = validateAuthState(authStateInput);
  const applicationApi = validateApplicationApi(applicationApiInput);
  const core = verifyCoreOrigin(coreOrigin);
  const sessionRaw = Buffer.isBuffer(sessionSecret)
    ? Buffer.from(sessionSecret)
    : Buffer.from(String(sessionSecret ?? ''), 'utf8');
  if (sessionRaw.length < 32 || sessionRaw.length > 4096) fail('SaaS hosted session secret length is invalid');
  if (typeof fetchImpl !== 'function') fail('SaaS hosted fetch implementation is invalid');
  if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 500 || timeoutMs > 30000) fail('SaaS hosted timeout is invalid');

  const resolveSession = (request, current) => {
    const token = parseCookies(request.headers.cookie)[config.session.cookie_name];
    if (!token) return { status: 'missing', session: null };
    let session;
    try { session = verifySession(token, sessionRaw, config, current); }
    catch { return { status: 'invalid', session: null }; }
    try {
      if (!authState.validateSession(session, current)) return { status: 'invalid', session: null };
    } catch {
      return { status: 'unavailable', session: null };
    }
    return { status: 'ok', session };
  };

  const proxyCore = async (request, response, url, requestId) => {
    if (!['GET', 'HEAD', 'POST'].includes(request.method ?? '')) {
      response.setHeader('Allow', 'GET, HEAD, POST');
      return sendJson(response, 405, { error: 'method_not_allowed' }, requestId);
    }
    if (hasRequestBody(request)) return sendJson(response, 413, { error: 'request_body_not_allowed' }, requestId);
    const upstream = await upstreamFetch(fetchImpl, core, `${url.pathname}${url.search}`, {
      method: request.method,
      headers: forwardedRequestHeaders(request, core),
    }, timeoutMs);
    const raw = await readBoundedResponse(upstream);
    securityHeaders(response, requestId);
    response.statusCode = upstream.status;
    copyResponseHeaders(upstream, response);
    const declared = upstream.headers.get('content-length');
    response.setHeader('Content-Length', request.method === 'HEAD' && declared !== null && /^\d+$/.test(declared)
      ? declared
      : String(raw.length));
    if (request.method === 'HEAD') response.end();
    else response.end(raw);
  };

  const server = createHttpServer((request, response) => {
    const requestId = randomUUID();
    const handle = async () => {
      if (Buffer.byteLength(request.url ?? '', 'utf8') > MAX_URL_BYTES) {
        return sendJson(response, 414, { error: 'uri_too_long' }, requestId);
      }
      let url;
      try { url = new URL(request.url ?? '/', 'http://localhost'); }
      catch { return sendJson(response, 400, { error: 'invalid_request_url' }, requestId); }

      if (url.pathname.startsWith('/api/saas/')) {
        const bodyAllowed = request.method === 'PUT' && PROGRESS_MUTATION.test(url.pathname);
        if (hasRequestBody(request) && !bodyAllowed) {
          return sendJson(response, 413, { error: 'request_body_not_allowed' }, requestId);
        }
        const current = now();
        const resolved = resolveSession(request, current);
        if (resolved.status === 'unavailable') return sendJson(response, 503, { error: 'auth_state_unavailable' }, requestId);
        if (!resolved.session) return sendJson(response, 401, { error: 'session_required' }, requestId);
        const output = await applicationApi.handle({ request, url, session: resolved.session, nowSeconds: current, requestId });
        if (!output) return sendJson(response, 404, { error: 'not_found' }, requestId);
        return sendJson(response, output.status, output.body, requestId, output.headers);
      }

      return proxyCore(request, response, url, requestId);
    };
    handle().catch(() => {
      if (!response.headersSent) sendJson(response, 500, { error: 'internal_error' }, requestId);
      else response.destroy();
    });
  });

  server.once('close', () => {
    sessionRaw.fill(0);
    applicationApi.close();
  });
  server.principiaAtlasSaasRuntime = Object.freeze({
    contract: SAAS_HOSTED_RUNTIME_CONTRACT,
    application_api_contract: applicationApi.descriptor.contract,
    core_kind: 'loopback',
    production_ready: false,
  });
  return server;
}
