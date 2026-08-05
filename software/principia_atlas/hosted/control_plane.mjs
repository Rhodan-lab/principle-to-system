import { timingSafeEqual } from 'node:crypto';
import { createServer as createHttpServer } from 'node:http';
import { catalogForSession, verifyTenantCatalogCompatibility } from './catalog.mjs';
import { createMetricsRegistry, createNullAuditLogger, newRequestId } from './observability.mjs';
import { authStateInfo, createMemoryAuthState } from './state.mjs';
import { hostedAsset, parseHostedAssetPath } from './store.mjs';
import { canonicalJson } from './strict_json.mjs';
import { exchangeIdentityAssertion, SESSION_CONTRACT, verifySession } from './tokens.mjs';

const MAX_URL_BYTES = 8192;
const HEALTH_CONTRACT = 'principia-atlas-hosted-health/0.3';

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

function sendRaw(response, status, contentType, raw, requestId) {
  const body = Buffer.isBuffer(raw) ? raw : Buffer.from(String(raw), 'utf8');
  securityHeaders(response, requestId);
  response.statusCode = status;
  response.setHeader('Content-Type', contentType);
  response.setHeader('Content-Length', String(body.length));
  response.__principiaAtlasBytes = body.length;
  response.end(body);
}

function sendJson(response, status, value, requestId) {
  sendRaw(response, status, 'application/json; charset=utf-8', canonicalJson(value), requestId);
}

function sendHtml(response, status, html, requestId) {
  sendRaw(response, status, 'text/html; charset=utf-8', html, requestId);
}

function sendAsset(request, response, asset, requestId, metrics) {
  securityHeaders(response, requestId);
  response.statusCode = 200;
  response.setHeader('Content-Type', asset.contentType);
  response.setHeader('Content-Length', String(asset.size));
  response.setHeader('ETag', `"sha256-${asset.sha256}"`);
  response.setHeader('Content-Disposition', 'inline');
  response.__principiaAtlasBytes = request.method === 'HEAD' ? 0 : asset.size;
  metrics.release(asset.size);
  if (request.method === 'HEAD') response.end();
  else response.end(asset.raw);
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

function sameOrigin(request) {
  const origin = request.headers.origin;
  if (!origin) return true;
  try { return new URL(origin).host === request.headers.host; }
  catch { return false; }
}

function shellHtml() {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Principia & Atlas</title><style>body{font:16px/1.55 system-ui;margin:0;background:#f5f7f4;color:#17221d}main{max-width:900px;margin:auto;padding:3rem 1rem}article{background:white;border:1px solid #d8e0db;border-radius:1rem;padding:1rem;margin:.75rem 0}a{color:#0f5c4d;font-weight:700}</style></head><body><main><p>Principia & Atlas</p><h1>Hosted verified releases</h1><p id="status">Checking session…</p><section id="catalog"></section></main><script>async function load(){const s=document.querySelector('#status');const c=document.querySelector('#catalog');const r=await fetch('/api/catalog',{credentials:'same-origin'});if(r.status===401){s.textContent='A trusted identity adapter must establish a session.';return;}if(!r.ok){s.textContent='Control plane unavailable.';return;}const d=await r.json();s.textContent=d.tenant.display_name+' · '+d.subject;c.replaceChildren();if(!d.releases.length){const p=document.createElement('p');p.textContent='No release is entitled for this tenant.';c.append(p);return;}const h=document.createElement('h2');h.textContent='Available verified releases';c.append(h);for(const item of d.releases){const a=document.createElement('article');const title=document.createElement('strong');title.textContent=item.version+' · '+item.channel+' · '+item.route_id;a.append(title);if(item.launch_path){a.append(document.createElement('br'));const link=document.createElement('a');link.href=item.launch_path;link.textContent='Open release';a.append(link);}c.append(a);}}load();</script></body></html>`;
}

function withLaunchPaths(view, store) {
  if (!store) return view;
  const releases = view.releases.map((item) => ({
    ...item,
    launch_path: store.releases.has(item.version) ? `/app/${encodeURIComponent(item.version)}/` : null,
  }));
  const channels = {};
  for (const channel of ['alpha', 'beta', 'stable']) channels[channel] = releases.find((item) => item.channel === channel) ?? null;
  return { ...view, releases, channels };
}

function clearSessionCookie(response, config) {
  const attributes = [`${config.session.cookie_name}=`, 'Path=/', 'HttpOnly', 'SameSite=Lax', 'Max-Age=0'];
  if (config.session.secure) attributes.push('Secure');
  response.setHeader('Set-Cookie', attributes.join('; '));
}

function normalizeMetricsToken(value) {
  if (value === null || value === undefined) return null;
  const raw = Buffer.isBuffer(value) ? Buffer.from(value) : Buffer.from(String(value), 'utf8');
  if (raw.length < 24 || raw.length > 4096) throw new Error('metrics token length is invalid');
  return raw;
}

function metricsAuthorized(request, expected) {
  if (expected === null) return false;
  const match = /^Bearer ([^\s]{1,4096})$/.exec(request.headers.authorization ?? '');
  if (!match) return false;
  const actual = Buffer.from(match[1], 'utf8');
  return actual.length === expected.length && timingSafeEqual(actual, expected);
}

export function createControlPlaneServer({
  catalog: catalogInput,
  config: configInput,
  store = null,
  authState = createMemoryAuthState(),
  identitySecret,
  sessionSecret,
  metricsToken = null,
  audit = createNullAuditLogger(),
  metrics = createMetricsRegistry(),
  now = () => Math.floor(Date.now() / 1000),
  exchangeLimit = 10,
}) {
  const verified = verifyTenantCatalogCompatibility(catalogInput, configInput);
  const catalog = verified.catalog;
  const config = verified.config;
  if (store && store.catalog.catalog_id !== catalog.catalog_id) throw new Error('hosted store catalog identity does not match control plane');
  const identityRaw = Buffer.isBuffer(identitySecret) ? Buffer.from(identitySecret) : Buffer.from(String(identitySecret ?? ''), 'utf8');
  const sessionRaw = Buffer.isBuffer(sessionSecret) ? Buffer.from(sessionSecret) : Buffer.from(String(sessionSecret ?? ''), 'utf8');
  if (identityRaw.length < 32 || sessionRaw.length < 32) throw new Error('identity and session secrets must be at least 32 bytes');
  if (identityRaw.equals(sessionRaw)) throw new Error('identity and session secrets must be distinct');
  if (!Number.isSafeInteger(exchangeLimit) || exchangeLimit < 1 || exchangeLimit > 10000) throw new Error('exchange limit is invalid');
  const stateInfo = authStateInfo(authState);
  const metricsSecret = normalizeMetricsToken(metricsToken);

  const server = createHttpServer((request, response) => {
    const requestId = newRequestId();
    metrics.beginRequest();
    response.once('finish', () => metrics.endRequest(response.statusCode, response.__principiaAtlasBytes ?? 0));
    const handle = async () => {
      if (Buffer.byteLength(request.url ?? '') > MAX_URL_BYTES) return sendJson(response, 414, { error: 'uri_too_long' }, requestId);
      const getSession = () => {
        const token = parseCookies(request.headers.cookie)[config.session.cookie_name];
        if (!token) return { status: 'missing', session: null };
        const current = now();
        let session;
        try { session = verifySession(token, sessionRaw, config, current); }
        catch {
          audit.event('session.reject', { request_id: requestId, reason: 'invalid_signature_or_time' });
          return { status: 'invalid', session: null };
        }
        try {
          if (!authState.validateSession(session, current)) {
            audit.event('session.reject', { request_id: requestId, reason: 'unregistered_or_revoked', tenant_id: session.tenant_id });
            return { status: 'invalid', session: null };
          }
        } catch {
          return { status: 'unavailable', session: null };
        }
        return { status: 'ok', session };
      };

      let appRequest = null;
      try { appRequest = parseHostedAssetPath(request.url); }
      catch { return sendJson(response, 400, { error: 'invalid_asset_path' }, requestId); }
      if (appRequest) {
        if (!['GET', 'HEAD'].includes(request.method ?? '')) {
          response.setHeader('Allow', 'GET, HEAD');
          return sendJson(response, 405, { error: 'method_not_allowed' }, requestId);
        }
        const resolved = getSession();
        if (resolved.status === 'unavailable') return sendJson(response, 503, { error: 'auth_state_unavailable' }, requestId);
        if (!resolved.session) return sendJson(response, 401, { error: 'session_required' }, requestId);
        if (!store) return sendJson(response, 503, { error: 'release_store_unavailable' }, requestId);
        const view = catalogForSession(resolved.session, catalog, config);
        if (!view.releases.some((item) => item.version === appRequest.version)) {
          audit.event('release.deny', { request_id: requestId, tenant_id: resolved.session.tenant_id, version: appRequest.version });
          return sendJson(response, 404, { error: 'not_found' }, requestId);
        }
        const asset = hostedAsset(store, appRequest.version, appRequest.assetPath);
        if (!asset) return sendJson(response, 404, { error: 'not_found' }, requestId);
        return sendAsset(request, response, asset, requestId, metrics);
      }

      let url;
      try { url = new URL(request.url ?? '/', 'http://localhost'); }
      catch { return sendJson(response, 400, { error: 'invalid_request_url' }, requestId); }
      if (request.method === 'GET' && url.pathname === '/healthz') {
        return sendJson(response, 200, { status: 'ok', contract: HEALTH_CONTRACT, release_serving: store !== null, auth_state: stateInfo }, requestId);
      }
      if (request.method === 'GET' && url.pathname === '/readyz') {
        try {
          const state = authState.health();
          metrics.setReady(true);
          return sendJson(response, 200, { status: 'ready', contract: HEALTH_CONTRACT, release_serving: store !== null, auth_state: state }, requestId);
        } catch {
          metrics.setReady(false);
          audit.event('readiness.fail', { request_id: requestId, reason: 'auth_state_unavailable' });
          return sendJson(response, 503, { status: 'not_ready', contract: HEALTH_CONTRACT, release_serving: store !== null, auth_state: stateInfo }, requestId);
        }
      }
      if (request.method === 'GET' && url.pathname === '/metrics') {
        if (!metricsAuthorized(request, metricsSecret)) return sendJson(response, 404, { error: 'not_found' }, requestId);
        return sendRaw(response, 200, 'text/plain; version=0.0.4; charset=utf-8', metrics.render(), requestId);
      }
      if (request.method === 'GET' && url.pathname === '/') return sendHtml(response, 200, shellHtml(), requestId);
      if (request.method === 'POST' && url.pathname === '/api/auth/exchange') {
        if (!sameOrigin(request)) return sendJson(response, 403, { error: 'origin_rejected' }, requestId);
        const current = now();
        const address = request.socket.remoteAddress ?? 'unknown';
        const minuteStart = Math.floor(current / 60) * 60;
        let rate;
        try { rate = authState.consumeRateLimit(`identity-exchange:${address}`, minuteStart, 60, exchangeLimit, current); }
        catch {
          audit.event('auth.exchange', { request_id: requestId, outcome: 'state_unavailable' });
          return sendJson(response, 503, { error: 'auth_state_unavailable' }, requestId);
        }
        if (!rate.allowed) {
          metrics.auth('rate_limited');
          audit.event('auth.exchange', { request_id: requestId, outcome: 'rate_limited', reset_at: rate.reset_at });
          response.setHeader('Retry-After', String(Math.max(1, rate.reset_at - current)));
          return sendJson(response, 429, { error: 'rate_limited' }, requestId);
        }
        const match = /^Bearer ([A-Za-z0-9_.-]+)$/.exec(request.headers.authorization ?? '');
        if (!match) {
          metrics.auth('invalid');
          audit.event('auth.exchange', { request_id: requestId, outcome: 'missing' });
          return sendJson(response, 401, { error: 'identity_assertion_required' }, requestId);
        }
        let exchanged;
        try { exchanged = exchangeIdentityAssertion(match[1], identityRaw, sessionRaw, config, current); }
        catch {
          metrics.auth('invalid');
          audit.event('auth.exchange', { request_id: requestId, outcome: 'invalid' });
          return sendJson(response, 401, { error: 'identity_assertion_invalid' }, requestId);
        }
        let committed;
        try {
          committed = authState.commitExchange({ assertionId: exchanged.assertion.jti, assertionExpiresAt: exchanged.assertion.exp, session: exchanged.session }, current);
        } catch {
          audit.event('auth.exchange', { request_id: requestId, outcome: 'state_unavailable' });
          return sendJson(response, 503, { error: 'auth_state_unavailable' }, requestId);
        }
        if (!committed) {
          metrics.auth('invalid');
          audit.event('auth.exchange', { request_id: requestId, outcome: 'replay' });
          return sendJson(response, 401, { error: 'identity_assertion_invalid' }, requestId);
        }
        audit.event('auth.exchange', { request_id: requestId, outcome: 'success', tenant_id: exchanged.session.tenant_id, roles_count: exchanged.session.roles.length });
        metrics.auth('success');
        const attributes = [`${config.session.cookie_name}=${exchanged.token}`, 'Path=/', 'HttpOnly', 'SameSite=Lax', `Max-Age=${config.session.ttl_seconds}`];
        if (config.session.secure) attributes.push('Secure');
        response.setHeader('Set-Cookie', attributes.join('; '));
        return sendJson(response, 200, { contract: SESSION_CONTRACT, subject: exchanged.session.sub, tenant_id: exchanged.session.tenant_id, roles: exchanged.session.roles, expires_at: exchanged.session.exp }, requestId);
      }
      if (request.method === 'POST' && url.pathname === '/api/logout') {
        if (!sameOrigin(request)) return sendJson(response, 403, { error: 'origin_rejected' }, requestId);
        const resolved = getSession();
        if (resolved.status === 'unavailable') return sendJson(response, 503, { error: 'auth_state_unavailable' }, requestId);
        let revoked = false;
        if (resolved.session) {
          try { revoked = authState.revokeSession(resolved.session.sid, now()); }
          catch { return sendJson(response, 503, { error: 'auth_state_unavailable' }, requestId); }
        }
        audit.event('auth.logout', { request_id: requestId, outcome: revoked ? 'revoked' : 'no_active_session', tenant_id: resolved.session?.tenant_id ?? null });
        if (revoked) metrics.auth('revoked');
        clearSessionCookie(response, config);
        return sendJson(response, 200, { status: 'signed_out' }, requestId);
      }
      if (request.method === 'GET' && (url.pathname === '/api/session' || url.pathname === '/api/catalog')) {
        const resolved = getSession();
        if (resolved.status === 'unavailable') return sendJson(response, 503, { error: 'auth_state_unavailable' }, requestId);
        if (!resolved.session) return sendJson(response, 401, { error: 'session_required' }, requestId);
        if (url.pathname === '/api/session') return sendJson(response, 200, { contract: SESSION_CONTRACT, subject: resolved.session.sub, tenant_id: resolved.session.tenant_id, roles: resolved.session.roles, expires_at: resolved.session.exp }, requestId);
        return sendJson(response, 200, withLaunchPaths(catalogForSession(resolved.session, catalog, config), store), requestId);
      }
      return sendJson(response, 404, { error: 'not_found' }, requestId);
    };
    handle().catch(() => {
      try { audit.event('request.error', { request_id: requestId, reason: 'unhandled' }); } catch {}
      if (!response.headersSent) sendJson(response, 500, { error: 'internal_error' }, requestId);
      else response.destroy();
    });
  });
  server.once('close', () => {
    identityRaw.fill(0);
    sessionRaw.fill(0);
    metricsSecret?.fill(0);
  });
  server.principiaAtlas = Object.freeze({ audit, metrics });
  return server;
}
