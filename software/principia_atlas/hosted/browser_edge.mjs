import { randomUUID } from 'node:crypto';
import { createServer as createHttpServer } from 'node:http';
import { isIP } from 'node:net';

import { createBrowserOidcFlow } from './browser_oidc.mjs';
import { canonicalJson, exactKeys, fail, parseStrictJson } from './strict_json.mjs';
import { SESSION_CONTRACT } from './tokens.mjs';

export const BROWSER_EDGE_CONTRACT = 'principia-atlas-browser-oidc-edge/0.1';
const MAX_URL_BYTES = 8192;
const MAX_UPSTREAM_BYTES = 64 * 1024 * 1024;
const LOOPBACK = new Set(['localhost', '127.0.0.1', '::1', '[::1]']);
const FORWARDED_REQUEST_HEADERS = new Set(['accept', 'accept-language', 'cookie', 'if-none-match', 'user-agent']);
const FORWARDED_RESPONSE_HEADERS = new Set([
  'cache-control', 'content-disposition', 'content-length', 'content-security-policy',
  'content-type', 'cross-origin-opener-policy', 'cross-origin-resource-policy', 'etag',
  'permissions-policy', 'referrer-policy', 'retry-after', 'set-cookie',
  'x-content-type-options', 'x-frame-options', 'x-request-id',
]);

function loopbackHost(hostname) {
  return LOOPBACK.has(hostname);
}

export function verifyBrowserEdgeUpstream(value) {
  if (typeof value !== 'string' || value.length < 8 || value.length > 2048) fail('browser edge upstream origin is invalid');
  let parsed;
  try { parsed = new URL(value); } catch { fail('browser edge upstream origin is invalid'); }
  if (!['http:', 'https:'].includes(parsed.protocol) || parsed.username || parsed.password || parsed.pathname !== '/' || parsed.search || parsed.hash) {
    fail('browser edge upstream must be an exact HTTP origin');
  }
  if (!loopbackHost(parsed.hostname)) fail('browser edge upstream must be loopback');
  return parsed.origin;
}

export function validateBrowserEdgeNetwork({ host, allowNetwork, publicOrigin }) {
  if (typeof host !== 'string' || (isIP(host) === 0 && host !== 'localhost')) fail('browser edge host must be an IP address or localhost');
  const local = loopbackHost(host);
  if (!local && allowNetwork !== true) fail('non-loopback browser edge requires explicit network opt-in');
  const origin = new URL(publicOrigin);
  if (!local && origin.protocol !== 'https:') fail('non-loopback browser edge requires an HTTPS public origin');
}

function securityHeaders(response, requestId) {
  response.setHeader('Content-Security-Policy', "default-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'");
  response.setHeader('Referrer-Policy', 'no-referrer');
  response.setHeader('X-Content-Type-Options', 'nosniff');
  response.setHeader('X-Frame-Options', 'DENY');
  response.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
  response.setHeader('Cross-Origin-Resource-Policy', 'same-origin');
  response.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), payment=(), usb=(), serial=()');
  response.setHeader('Cache-Control', 'private, no-store');
  response.setHeader('X-Request-ID', requestId);
}

function requestId() {
  return randomUUID();
}

function sendRaw(response, status, contentType, raw, id, extraHeaders = {}) {
  const body = Buffer.isBuffer(raw) ? raw : Buffer.from(String(raw), 'utf8');
  securityHeaders(response, id);
  response.statusCode = status;
  response.setHeader('Content-Type', contentType);
  response.setHeader('Content-Length', String(body.length));
  for (const [name, value] of Object.entries(extraHeaders)) response.setHeader(name, value);
  response.end(body);
}

function sendJson(response, status, value, id, extraHeaders = {}) {
  sendRaw(response, status, 'application/json; charset=utf-8', canonicalJson(value), id, extraHeaders);
}

function redirect(response, location, id, cookies = []) {
  securityHeaders(response, id);
  response.statusCode = 303;
  response.setHeader('Location', location);
  if (cookies.length) response.setHeader('Set-Cookie', cookies);
  response.setHeader('Content-Length', '0');
  response.end();
}

function samePublicOrigin(request, publicOrigin) {
  const origin = request.headers.origin;
  if (!origin) return request.method !== 'POST';
  try { return new URL(origin).origin === publicOrigin; } catch { return false; }
}

function oneQueryParameter(url, name) {
  const values = url.searchParams.getAll(name);
  if (values.length > 1) fail(`browser edge query contains duplicate ${name}`);
  return values[0] ?? null;
}

function hasRequestBody(request) {
  if (request.headers['transfer-encoding']) return true;
  const raw = request.headers['content-length'];
  if (raw === undefined) return false;
  return raw !== '0';
}

async function readBoundedResponse(response, limit = MAX_UPSTREAM_BYTES) {
  if (!response.body) return Buffer.alloc(0);
  const declared = response.headers.get('content-length');
  if (declared !== null && (!/^\d+$/.test(declared) || Number(declared) > limit)) fail('browser edge upstream response exceeds resource limit');
  const reader = response.body.getReader();
  const chunks = []; let total = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > limit) fail('browser edge upstream response exceeds resource limit');
      chunks.push(Buffer.from(value));
    }
  } finally { reader.releaseLock(); }
  return Buffer.concat(chunks, total);
}

function forwardedRequestHeaders(request, upstreamOrigin) {
  const headers = new Headers();
  for (const [name, value] of Object.entries(request.headers)) {
    if (!FORWARDED_REQUEST_HEADERS.has(name) || value === undefined) continue;
    headers.set(name, Array.isArray(value) ? value.join(', ') : value);
  }
  headers.set('Origin', upstreamOrigin);
  return headers;
}

function copyResponseHeaders(upstream, response) {
  for (const [name, value] of upstream.headers.entries()) {
    if (FORWARDED_RESPONSE_HEADERS.has(name) && name !== 'content-length' && name !== 'set-cookie') response.setHeader(name, value);
  }
  const setCookie = upstream.headers.getSetCookie?.() ?? [];
  if (setCookie.length) response.setHeader('Set-Cookie', setCookie);
  else {
    const cookie = upstream.headers.get('set-cookie');
    if (cookie) response.setHeader('Set-Cookie', cookie);
  }
}

async function upstreamFetch(fetchImpl, upstreamOrigin, path, options = {}, timeoutMs = 10000) {
  const target = new URL(path, upstreamOrigin);
  if (target.origin !== upstreamOrigin) fail('browser edge upstream path escaped its origin');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  timer.unref?.();
  try {
    return await fetchImpl(target, { ...options, redirect: 'manual', signal: controller.signal });
  } catch {
    fail('browser edge upstream request failed');
  } finally { clearTimeout(timer); }
}

export function createBrowserOidcEdgeServer({
  flow = null,
  config = null,
  flowSecret = null,
  clientSecret = null,
  upstreamOrigin,
  fetchImpl = globalThis.fetch,
  now = () => Math.floor(Date.now() / 1000),
  exchangeTimeoutMs = 10000,
} = {}) {
  const browserFlow = flow ?? createBrowserOidcFlow({ config, flowSecret, clientSecret, fetchImpl, now });
  if (!browserFlow || typeof browserFlow.begin !== 'function' || typeof browserFlow.complete !== 'function' || typeof browserFlow.close !== 'function') fail('browser edge flow is invalid');
  if (typeof fetchImpl !== 'function') fail('browser edge fetch implementation is invalid');
  const upstream = verifyBrowserEdgeUpstream(upstreamOrigin);
  const publicOrigin = browserFlow.config.public_origin;
  if (!Number.isSafeInteger(exchangeTimeoutMs) || exchangeTimeoutMs < 500 || exchangeTimeoutMs > 30000) fail('browser edge exchange timeout is invalid');

  const proxy = async (request, response, url, id) => {
    if (!['GET', 'HEAD', 'POST'].includes(request.method ?? '')) {
      response.setHeader('Allow', 'GET, HEAD, POST');
      return sendJson(response, 405, { error: 'method_not_allowed' }, id);
    }
    if (hasRequestBody(request)) return sendJson(response, 413, { error: 'request_body_not_allowed' }, id);
    if (['/api/auth/oidc', '/api/auth/exchange', '/metrics'].includes(url.pathname)) return sendJson(response, 404, { error: 'not_found' }, id);
    if (!samePublicOrigin(request, publicOrigin)) return sendJson(response, 403, { error: 'origin_rejected' }, id);
    const upstreamResponse = await upstreamFetch(fetchImpl, upstream, `${url.pathname}${url.search}`, {
      method: request.method,
      headers: forwardedRequestHeaders(request, upstream),
    }, exchangeTimeoutMs);
    const raw = await readBoundedResponse(upstreamResponse);
    securityHeaders(response, id);
    response.statusCode = upstreamResponse.status;
    copyResponseHeaders(upstreamResponse, response);
    const declared = upstreamResponse.headers.get('content-length');
    const responseLength = request.method === 'HEAD' && declared !== null && /^\d+$/.test(declared)
      ? declared
      : String(raw.length);
    response.setHeader('Content-Length', responseLength);
    if (request.method === 'HEAD') response.end();
    else response.end(raw);
  };

  const server = createHttpServer((request, response) => {
    const id = requestId();
    const handle = async () => {
      if (Buffer.byteLength(request.url ?? '', 'utf8') > MAX_URL_BYTES) return sendJson(response, 414, { error: 'uri_too_long' }, id);
      let url;
      try { url = new URL(request.url ?? '/', publicOrigin); } catch { return sendJson(response, 400, { error: 'invalid_request_url' }, id); }
      if (url.origin !== publicOrigin) return sendJson(response, 400, { error: 'invalid_request_url' }, id);

      if (request.method === 'GET' && url.pathname === '/edge/healthz') {
        return sendJson(response, 200, {
          status: 'ok', contract: BROWSER_EDGE_CONTRACT,
          config_id: browserFlow.config.config_id,
          upstream: 'configured-loopback',
        }, id);
      }

      if (request.method === 'GET' && url.pathname === browserFlow.config.login_path) {
        const returnTo = oneQueryParameter(url, 'return_to');
        const started = browserFlow.begin(returnTo);
        return redirect(response, started.location, id, [started.set_cookie]);
      }

      if (request.method === 'GET' && url.pathname === browserFlow.config.callback_path) {
        let completed;
        try { completed = await browserFlow.complete(url.toString(), request.headers.cookie); }
        catch {
          return sendJson(response, 401, { error: 'browser_login_failed' }, id, { 'Set-Cookie': browserFlow.clear_cookie() });
        }
        if (completed.status !== 'complete') {
          return redirect(response, completed.return_to, id, [completed.clear_cookie]);
        }
        let exchanged;
        try {
          exchanged = await upstreamFetch(fetchImpl, upstream, '/api/auth/oidc', {
            method: 'POST',
            headers: { Authorization: `Bearer ${completed.id_token}`, Origin: upstream },
          }, exchangeTimeoutMs);
        } catch {
          return sendJson(response, 503, { error: 'identity_exchange_unavailable' }, id, { 'Set-Cookie': completed.clear_cookie });
        }
        const raw = await readBoundedResponse(exchanged, 65536);
        if (exchanged.status !== 200) {
          return sendJson(response, 401, { error: 'browser_login_failed' }, id, { 'Set-Cookie': completed.clear_cookie });
        }
        const contentType = String(exchanged.headers.get('content-type') ?? '').toLowerCase();
        if (!/^application\/json(?:\s*;|$)/.test(contentType)) {
          return sendJson(response, 502, { error: 'identity_exchange_invalid' }, id, { 'Set-Cookie': completed.clear_cookie });
        }
        let exchangeBody;
        try { exchangeBody = parseStrictJson(raw, 'browser edge identity exchange'); }
        catch { return sendJson(response, 502, { error: 'identity_exchange_invalid' }, id, { 'Set-Cookie': completed.clear_cookie }); }
        try {
          exactKeys(exchangeBody, ['contract', 'subject', 'tenant_id', 'roles', 'expires_at'], 'browser edge identity exchange');
          if (exchangeBody.contract !== SESSION_CONTRACT
            || typeof exchangeBody.subject !== 'string' || !exchangeBody.subject
            || typeof exchangeBody.tenant_id !== 'string' || !exchangeBody.tenant_id
            || !Array.isArray(exchangeBody.roles) || !exchangeBody.roles.every((role) => typeof role === 'string' && role)
            || !Number.isSafeInteger(exchangeBody.expires_at)) fail('browser edge identity exchange contract is invalid');
        } catch {
          return sendJson(response, 502, { error: 'identity_exchange_invalid' }, id, { 'Set-Cookie': completed.clear_cookie });
        }
        const cookies = exchanged.headers.getSetCookie?.() ?? [];
        if (cookies.length === 0) {
          const cookie = exchanged.headers.get('set-cookie');
          if (cookie) cookies.push(cookie);
        }
        if (cookies.length !== 1) return sendJson(response, 502, { error: 'identity_exchange_invalid' }, id, { 'Set-Cookie': completed.clear_cookie });
        const sessionCookie = cookies[0];
        if (Buffer.byteLength(sessionCookie, 'utf8') > 8192 || /[\u0000-\u001f\u007f]/.test(sessionCookie)
          || !/;\s*Path=\//i.test(sessionCookie) || !/;\s*HttpOnly(?:;|$)/i.test(sessionCookie)
          || !/;\s*SameSite=Lax(?:;|$)/i.test(sessionCookie)
          || (new URL(publicOrigin).protocol === 'https:' && !/;\s*Secure(?:;|$)/i.test(sessionCookie))) {
          return sendJson(response, 502, { error: 'identity_exchange_invalid' }, id, { 'Set-Cookie': completed.clear_cookie });
        }
        return redirect(response, completed.return_to, id, [sessionCookie, completed.clear_cookie]);
      }

      if (request.method === 'GET' && url.pathname === '/') {
        const sessionCheck = await upstreamFetch(fetchImpl, upstream, '/api/session', {
          method: 'GET', headers: forwardedRequestHeaders(request, upstream),
        }, exchangeTimeoutMs);
        await readBoundedResponse(sessionCheck, 65536);
        if (sessionCheck.status === 401) {
          const started = browserFlow.begin(`${url.pathname}${url.search}`);
          return redirect(response, started.location, id, [started.set_cookie]);
        }
      }

      return proxy(request, response, url, id);
    };
    handle().catch(() => {
      if (!response.headersSent) sendJson(response, 500, { error: 'internal_error' }, id);
      else response.destroy();
    });
  });
  server.once('close', () => browserFlow.close());
  server.principiaAtlasBrowserEdge = Object.freeze({
    contract: BROWSER_EDGE_CONTRACT,
    config_id: browserFlow.config.config_id,
    upstream_kind: 'loopback',
  });
  return server;
}
