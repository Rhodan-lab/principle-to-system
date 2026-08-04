import { createServer as createHttpServer } from 'node:http';
import { catalogForSession, verifyTenantCatalogCompatibility } from './catalog.mjs';
import { canonicalJson } from './strict_json.mjs';
import { exchangeIdentityAssertion, SESSION_CONTRACT, verifySession } from './tokens.mjs';

function securityHeaders(response) {
  response.setHeader('Content-Security-Policy', "default-src 'self'; connect-src 'self'; img-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'");
  response.setHeader('Referrer-Policy', 'no-referrer');
  response.setHeader('X-Content-Type-Options', 'nosniff');
  response.setHeader('X-Frame-Options', 'DENY');
  response.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), payment=()');
  response.setHeader('Cache-Control', 'no-store');
}

function sendJson(response, status, value) {
  securityHeaders(response); response.statusCode = status;
  response.setHeader('Content-Type', 'application/json; charset=utf-8');
  response.end(canonicalJson(value));
}

function sendHtml(response, status, html) {
  securityHeaders(response); response.statusCode = status;
  response.setHeader('Content-Type', 'text/html; charset=utf-8'); response.end(html);
}

function parseCookies(header) {
  const output = {};
  for (const pair of String(header ?? '').split(';')) {
    const position = pair.indexOf('='); if (position < 1) continue;
    const key = pair.slice(0, position).trim(); const value = pair.slice(position + 1).trim();
    if (key && !(key in output)) output[key] = value;
  }
  return output;
}

function sameOrigin(request) {
  const origin = request.headers.origin;
  if (!origin) return true;
  try { return new URL(origin).host === request.headers.host; } catch { return false; }
}

function shellHtml() {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Principia & Atlas</title></head><body><main><p>Principia & Atlas</p><h1>Hosted control plane</h1><p id="status">Checking session…</p><section id="catalog"></section></main><script>async function load(){const s=document.querySelector('#status');const c=document.querySelector('#catalog');const r=await fetch('/api/catalog',{credentials:'same-origin'});if(r.status===401){s.textContent='A trusted identity adapter must establish a session.';return;}if(!r.ok){s.textContent='Control plane unavailable.';return;}const d=await r.json();s.textContent=d.tenant.display_name+' · '+d.subject;c.innerHTML=d.releases.length?'<h2>Available verified releases</h2><ul>'+d.releases.map(x=>'<li><strong>'+x.version+'</strong> · '+x.channel+' · '+x.route_id+'</li>').join('')+'</ul>':'<p>No release is entitled for this tenant.</p>';}load();</script></body></html>`;
}

export function createControlPlaneServer({ catalog: catalogInput, config: configInput, identitySecret, sessionSecret, now = () => Math.floor(Date.now() / 1000), exchangeLimit = 10 }) {
  const verified = verifyTenantCatalogCompatibility(catalogInput, configInput);
  const catalog = verified.catalog; const config = verified.config;
  const identityRaw = Buffer.from(String(identitySecret ?? ''), 'utf8');
  const sessionRaw = Buffer.from(String(sessionSecret ?? ''), 'utf8');
  if (identityRaw.length < 32 || sessionRaw.length < 32) throw new Error('identity and session secrets must be at least 32 bytes');
  if (identityRaw.equals(sessionRaw)) throw new Error('identity and session secrets must be distinct');
  const attempts = new Map();
  const usedAssertions = new Map();
  return createHttpServer((request, response) => {
    const url = new URL(request.url ?? '/', `http://${request.headers.host ?? 'localhost'}`);
    const getSession = () => {
      const token = parseCookies(request.headers.cookie)[config.session.cookie_name];
      if (!token) return null;
      try { return verifySession(token, sessionSecret, config, now()); } catch { return null; }
    };
    if (request.method === 'GET' && url.pathname === '/healthz') return sendJson(response, 200, { status: 'ok', contract: 'principia-atlas-hosted-health/0.1' });
    if (request.method === 'GET' && url.pathname === '/') return sendHtml(response, 200, shellHtml());
    if (request.method === 'POST' && url.pathname === '/api/auth/exchange') {
      if (!sameOrigin(request)) return sendJson(response, 403, { error: 'origin_rejected' });
      const address = request.socket.remoteAddress ?? 'unknown'; const minute = Math.floor(now() / 60);
      const previous = attempts.get(address);
      const count = previous?.minute === minute ? previous.count + 1 : 1;
      attempts.set(address, { minute, count });
      if (count > exchangeLimit) return sendJson(response, 429, { error: 'rate_limited' });
      const match = /^Bearer ([A-Za-z0-9_.-]+)$/.exec(request.headers.authorization ?? '');
      if (!match) return sendJson(response, 401, { error: 'identity_assertion_required' });
      try {
        const current = now();
        for (const [jti, expiry] of usedAssertions) if (expiry <= current) usedAssertions.delete(jti);
        const exchanged = exchangeIdentityAssertion(match[1], identitySecret, sessionSecret, config, current);
        if ((usedAssertions.get(exchanged.session.jti) ?? 0) > current) throw new Error('identity assertion replayed');
        usedAssertions.set(exchanged.session.jti, exchanged.session.exp);
        const attributes = [`${config.session.cookie_name}=${exchanged.token}`, 'Path=/', 'HttpOnly', 'SameSite=Lax', `Max-Age=${config.session.ttl_seconds}`];
        if (config.session.secure) attributes.push('Secure');
        response.setHeader('Set-Cookie', attributes.join('; '));
        return sendJson(response, 200, { contract: SESSION_CONTRACT, subject: exchanged.session.sub, tenant_id: exchanged.session.tenant_id, roles: exchanged.session.roles, expires_at: exchanged.session.exp });
      } catch { return sendJson(response, 401, { error: 'identity_assertion_invalid' }); }
    }
    if (request.method === 'POST' && url.pathname === '/api/logout') {
      if (!sameOrigin(request)) return sendJson(response, 403, { error: 'origin_rejected' });
      const attributes = [`${config.session.cookie_name}=`, 'Path=/', 'HttpOnly', 'SameSite=Lax', 'Max-Age=0'];
      if (config.session.secure) attributes.push('Secure');
      response.setHeader('Set-Cookie', attributes.join('; '));
      return sendJson(response, 200, { status: 'signed_out' });
    }
    if (request.method === 'GET' && (url.pathname === '/api/session' || url.pathname === '/api/catalog')) {
      const session = getSession();
      if (!session) return sendJson(response, 401, { error: 'session_required' });
      if (url.pathname === '/api/session') return sendJson(response, 200, { contract: SESSION_CONTRACT, subject: session.sub, tenant_id: session.tenant_id, roles: session.roles, expires_at: session.exp });
      return sendJson(response, 200, catalogForSession(session, catalog, config));
    }
    return sendJson(response, 404, { error: 'not_found' });
  });
}
