import { createServer as createHttpServer } from 'node:http';
import { catalogForSession, verifyTenantCatalogCompatibility } from './catalog.mjs';
import { authStateInfo, createMemoryAuthState } from './state.mjs';
import { hostedAsset, parseHostedAssetPath } from './store.mjs';
import { canonicalJson } from './strict_json.mjs';
import { exchangeIdentityAssertion, SESSION_CONTRACT, verifySession } from './tokens.mjs';

const MAX_URL_BYTES = 8192;
const HEALTH_CONTRACT = 'principia-atlas-hosted-health/0.3';

function securityHeaders(response) {
  response.setHeader('Content-Security-Policy', "default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'; object-src 'none'");
  response.setHeader('Referrer-Policy', 'no-referrer');
  response.setHeader('X-Content-Type-Options', 'nosniff');
  response.setHeader('X-Frame-Options', 'DENY');
  response.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
  response.setHeader('Cross-Origin-Resource-Policy', 'same-origin');
  response.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), payment=(), usb=(), serial=()');
  response.setHeader('Cache-Control', 'private, no-store');
}

function sendJson(response, status, value) {
  securityHeaders(response);
  response.statusCode = status;
  response.setHeader('Content-Type', 'application/json; charset=utf-8');
  response.end(canonicalJson(value));
}

function sendHtml(response, status, html) {
  securityHeaders(response);
  response.statusCode = status;
  response.setHeader('Content-Type', 'text/html; charset=utf-8');
  response.end(html);
}

function sendAsset(request, response, asset) {
  securityHeaders(response);
  response.statusCode = 200;
  response.setHeader('Content-Type', asset.contentType);
  response.setHeader('Content-Length', String(asset.size));
  response.setHeader('ETag', `"sha256-${asset.sha256}"`);
  response.setHeader('Content-Disposition', 'inline');
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

export function createControlPlaneServer({
  catalog: catalogInput,
  config: configInput,
  store = null,
  authState = createMemoryAuthState(),
  identitySecret,
  sessionSecret,
  now = () => Math.floor(Date.now() / 1000),
  exchangeLimit = 10,
}) {
  const verified = verifyTenantCatalogCompatibility(catalogInput, configInput);
  const catalog = verified.catalog;
  const config = verified.config;
  if (store && store.catalog.catalog_id !== catalog.catalog_id) throw new Error('hosted store catalog identity does not match control plane');
  const identityRaw = Buffer.from(String(identitySecret ?? ''), 'utf8');
  const sessionRaw = Buffer.from(String(sessionSecret ?? ''), 'utf8');
  if (identityRaw.length < 32 || sessionRaw.length < 32) throw new Error('identity and session secrets must be at least 32 bytes');
  if (identityRaw.equals(sessionRaw)) throw new Error('identity and session secrets must be distinct');
  if (!Number.isSafeInteger(exchangeLimit) || exchangeLimit < 1 || exchangeLimit > 10000) throw new Error('exchange limit is invalid');
  const stateInfo = authStateInfo(authState);

  const server = createHttpServer((request, response) => {
    const handle = async () => {
      if (Buffer.byteLength(request.url ?? '') > MAX_URL_BYTES) return sendJson(response, 414, { error: 'uri_too_long' });
      const getSession = () => {
        const token = parseCookies(request.headers.cookie)[config.session.cookie_name];
        if (!token) return { status: 'missing', session: null };
        const current = now();
        let session;
        try { session = verifySession(token, sessionSecret, config, current); }
        catch { return { status: 'invalid', session: null }; }
        try {
          if (!authState.validateSession(session, current)) return { status: 'invalid', session: null };
        } catch {
          return { status: 'unavailable', session: null };
        }
        return { status: 'ok', session };
      };

      let appRequest = null;
      try { appRequest = parseHostedAssetPath(request.url); }
      catch { return sendJson(response, 400, { error: 'invalid_asset_path' }); }
      if (appRequest) {
        if (!['GET', 'HEAD'].includes(request.method ?? '')) {
          response.setHeader('Allow', 'GET, HEAD');
          return sendJson(response, 405, { error: 'method_not_allowed' });
        }
        const resolved = getSession();
        if (resolved.status === 'unavailable') return sendJson(response, 503, { error: 'auth_state_unavailable' });
        if (!resolved.session) return sendJson(response, 401, { error: 'session_required' });
        if (!store) return sendJson(response, 503, { error: 'release_store_unavailable' });
        const view = catalogForSession(resolved.session, catalog, config);
        if (!view.releases.some((item) => item.version === appRequest.version)) return sendJson(response, 404, { error: 'not_found' });
        const asset = hostedAsset(store, appRequest.version, appRequest.assetPath);
        if (!asset) return sendJson(response, 404, { error: 'not_found' });
        return sendAsset(request, response, asset);
      }

      let url;
      try { url = new URL(request.url ?? '/', 'http://localhost'); }
      catch { return sendJson(response, 400, { error: 'invalid_request_url' }); }
      if (request.method === 'GET' && url.pathname === '/healthz') {
        return sendJson(response, 200, { status: 'ok', contract: HEALTH_CONTRACT, release_serving: store !== null, auth_state: stateInfo });
      }
      if (request.method === 'GET' && url.pathname === '/readyz') {
        try {
          const state = authState.health();
          return sendJson(response, 200, { status: 'ready', contract: HEALTH_CONTRACT, release_serving: store !== null, auth_state: state });
        } catch {
          return sendJson(response, 503, { status: 'not_ready', contract: HEALTH_CONTRACT, release_serving: store !== null, auth_state: stateInfo });
        }
      }
      if (request.method === 'GET' && url.pathname === '/') return sendHtml(response, 200, shellHtml());
      if (request.method === 'POST' && url.pathname === '/api/auth/exchange') {
        if (!sameOrigin(request)) return sendJson(response, 403, { error: 'origin_rejected' });
        const current = now();
        const address = request.socket.remoteAddress ?? 'unknown';
        const minuteStart = Math.floor(current / 60) * 60;
        let rate;
        try { rate = authState.consumeRateLimit(`identity-exchange:${address}`, minuteStart, 60, exchangeLimit, current); }
        catch { return sendJson(response, 503, { error: 'auth_state_unavailable' }); }
        if (!rate.allowed) {
          response.setHeader('Retry-After', String(Math.max(1, rate.reset_at - current)));
          return sendJson(response, 429, { error: 'rate_limited' });
        }
        const match = /^Bearer ([A-Za-z0-9_.-]+)$/.exec(request.headers.authorization ?? '');
        if (!match) return sendJson(response, 401, { error: 'identity_assertion_required' });
        let exchanged;
        try { exchanged = exchangeIdentityAssertion(match[1], identitySecret, sessionSecret, config, current); }
        catch { return sendJson(response, 401, { error: 'identity_assertion_invalid' }); }
        let committed;
        try {
          committed = authState.commitExchange({
            assertionId: exchanged.assertion.jti,
            assertionExpiresAt: exchanged.assertion.exp,
            session: exchanged.session,
          }, current);
        } catch {
          return sendJson(response, 503, { error: 'auth_state_unavailable' });
        }
        if (!committed) return sendJson(response, 401, { error: 'identity_assertion_invalid' });
        const attributes = [`${config.session.cookie_name}=${exchanged.token}`, 'Path=/', 'HttpOnly', 'SameSite=Lax', `Max-Age=${config.session.ttl_seconds}`];
        if (config.session.secure) attributes.push('Secure');
        response.setHeader('Set-Cookie', attributes.join('; '));
        return sendJson(response, 200, { contract: SESSION_CONTRACT, subject: exchanged.session.sub, tenant_id: exchanged.session.tenant_id, roles: exchanged.session.roles, expires_at: exchanged.session.exp });
      }
      if (request.method === 'POST' && url.pathname === '/api/logout') {
        if (!sameOrigin(request)) return sendJson(response, 403, { error: 'origin_rejected' });
        const resolved = getSession();
        if (resolved.status === 'unavailable') return sendJson(response, 503, { error: 'auth_state_unavailable' });
        if (resolved.session) {
          try { authState.revokeSession(resolved.session.sid, now()); }
          catch { return sendJson(response, 503, { error: 'auth_state_unavailable' }); }
        }
        clearSessionCookie(response, config);
        return sendJson(response, 200, { status: 'signed_out' });
      }
      if (request.method === 'GET' && (url.pathname === '/api/session' || url.pathname === '/api/catalog')) {
        const resolved = getSession();
        if (resolved.status === 'unavailable') return sendJson(response, 503, { error: 'auth_state_unavailable' });
        if (!resolved.session) return sendJson(response, 401, { error: 'session_required' });
        if (url.pathname === '/api/session') return sendJson(response, 200, { contract: SESSION_CONTRACT, subject: resolved.session.sub, tenant_id: resolved.session.tenant_id, roles: resolved.session.roles, expires_at: resolved.session.exp });
        return sendJson(response, 200, withLaunchPaths(catalogForSession(resolved.session, catalog, config), store));
      }
      return sendJson(response, 404, { error: 'not_found' });
    };
    handle().catch(() => {
      if (!response.headersSent) sendJson(response, 500, { error: 'internal_error' });
      else response.destroy();
    });
  });
  return server;
}
