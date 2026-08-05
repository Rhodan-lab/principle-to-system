import assert from 'node:assert/strict';
import { createServer as createHttpServer } from 'node:http';
import test from 'node:test';

import { BROWSER_OIDC_CONTRACT, sealBrowserOidcConfig } from '../principia_atlas/hosted/browser_oidc.mjs';
import {
  BROWSER_EDGE_CONTRACT,
  createBrowserOidcEdgeServer,
  validateBrowserEdgeNetwork,
  verifyBrowserEdgeUpstream,
} from '../principia_atlas/hosted/browser_edge.mjs';
import { PRODUCT, } from '../principia_atlas/hosted/catalog.mjs';

const issuer = 'https://identity.example.test';
const now = 1_800_000_000;
const flowSecret = 'flow-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const clientSecret = 'client-secret-0123456789-abcdefghijklmnopqrstuvwxyz';

async function freePort() {
  const server = createHttpServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;
  await new Promise((resolve) => server.close(resolve));
  return port;
}

function config(publicOrigin) {
  return sealBrowserOidcConfig({
    contract: BROWSER_OIDC_CONTRACT,
    product: PRODUCT,
    issuer,
    public_origin: publicOrigin,
    authorization_endpoint: `${issuer}/authorize`,
    token_endpoint: `${issuer}/token`,
    client_id: 'principia-atlas-browser',
    client_auth_method: 'client_secret_post',
    scopes: ['openid', 'profile'],
    login_path: '/auth/login',
    callback_path: '/auth/callback',
    default_return_to: '/',
    flow_ttl_seconds: 300,
    token_timeout_ms: 2000,
    token_max_bytes: 65536,
    cookie: { name: 'pa_oidc_flow', secure: false, same_site: 'Lax' },
  });
}

function jwt(payload) {
  return `${Buffer.from('{"alg":"RS256"}').toString('base64url')}.${Buffer.from(JSON.stringify(payload)).toString('base64url')}.c2ln`;
}

function cookiePair(header) {
  return header.split(';')[0];
}

function router({ tokenResponse = null, exchangeUnavailable = false } = {}) {
  const calls = [];
  const fetchImpl = async (input, options = {}) => {
    const url = new URL(input);
    calls.push({ url: url.toString(), options });
    if (url.origin === issuer && url.pathname === '/token') {
      const body = new URLSearchParams(options.body);
      const nonce = router.currentNonce;
      const response = tokenResponse ?? { id_token: jwt({ iss: issuer, nonce }), token_type: 'Bearer' };
      return new Response(JSON.stringify(response), { status: 200, headers: { 'content-type': 'application/json' } });
    }
    if (url.origin === 'http://127.0.0.1:9099' && url.pathname === '/api/session') {
      const cookie = options.headers instanceof Headers ? options.headers.get('cookie') : options.headers?.Cookie;
      return new Response(cookie?.includes('pa_session=ok') ? '{"status":"ok"}' : '{"error":"session_required"}', {
        status: cookie?.includes('pa_session=ok') ? 200 : 401,
        headers: { 'content-type': 'application/json' },
      });
    }
    if (url.origin === 'http://127.0.0.1:9099' && url.pathname === '/api/auth/oidc') {
      if (exchangeUnavailable) throw new Error('upstream unavailable');
      assert.match(options.headers.Authorization, /^Bearer [A-Za-z0-9_.-]+$/);
      assert.equal(options.headers.Origin, 'http://127.0.0.1:9099');
      return new Response('{"contract":"principia-atlas-hosted-session/0.1","subject":"user","tenant_id":"local-preview","roles":["learner"],"expires_at":1800003600}', {
        status: 200,
        headers: { 'content-type': 'application/json', 'set-cookie': 'pa_session=ok; Path=/; HttpOnly; SameSite=Lax' },
      });
    }
    if (url.origin === 'http://127.0.0.1:9099' && url.pathname === '/') {
      return new Response('<h1>upstream</h1>', { status: 200, headers: { 'content-type': 'text/html; charset=utf-8' } });
    }
    if (url.origin === 'http://127.0.0.1:9099' && url.pathname === '/api/logout') {
      return new Response('{"status":"signed_out"}', { status: 200, headers: { 'content-type': 'application/json' } });
    }
    return new Response('{"error":"not_found"}', { status: 404, headers: { 'content-type': 'application/json' } });
  };
  fetchImpl.calls = calls;
  return fetchImpl;
}

test('edge accepts only an exact loopback upstream and explicit network opt-in', () => {
  assert.equal(verifyBrowserEdgeUpstream('http://127.0.0.1:9099'), 'http://127.0.0.1:9099');
  assert.throws(() => verifyBrowserEdgeUpstream('https://upstream.example.test'), /loopback/);
  assert.throws(() => verifyBrowserEdgeUpstream('http://127.0.0.1:9099/path'), /exact HTTP origin/);
  validateBrowserEdgeNetwork({ host: '127.0.0.1', allowNetwork: false, publicOrigin: 'http://127.0.0.1:8080' });
  assert.throws(() => validateBrowserEdgeNetwork({ host: '0.0.0.0', allowNetwork: false, publicOrigin: 'https://edge.example.test' }), /network opt-in/);
  assert.throws(() => validateBrowserEdgeNetwork({ host: '0.0.0.0', allowNetwork: true, publicOrigin: 'http://127.0.0.1:8080' }), /HTTPS public origin/);
});

test('unauthenticated root starts PKCE and callback exchanges only the ID token upstream', async () => {
  const port = await freePort();
  const origin = `http://127.0.0.1:${port}`;
  const fetchImpl = router();
  const server = createBrowserOidcEdgeServer({
    config: config(origin), flowSecret, clientSecret,
    upstreamOrigin: 'http://127.0.0.1:9099', fetchImpl, now: () => now,
  });
  await new Promise((resolve) => server.listen(port, '127.0.0.1', resolve));
  try {
    const start = await fetch(`${origin}/`, { redirect: 'manual' });
    assert.equal(start.status, 303);
    const authorization = new URL(start.headers.get('location'));
    assert.equal(authorization.origin, issuer);
    assert.equal(authorization.searchParams.get('code_challenge_method'), 'S256');
    assert.ok(authorization.searchParams.get('code_challenge'));
    router.currentNonce = authorization.searchParams.get('nonce');
    const flowCookie = cookiePair(start.headers.get('set-cookie'));
    const callback = new URL('/auth/callback', origin);
    callback.searchParams.set('code', 'authorization-code');
    callback.searchParams.set('state', authorization.searchParams.get('state'));
    callback.searchParams.set('iss', issuer);
    const completed = await fetch(callback, { headers: { Cookie: flowCookie }, redirect: 'manual' });
    assert.equal(completed.status, 303);
    assert.equal(completed.headers.get('location'), '/');
    const cookies = completed.headers.get('set-cookie');
    assert.match(cookies, /pa_session=ok/);
    assert.match(cookies, /pa_oidc_flow=/);
    const tokenCall = fetchImpl.calls.find((item) => item.url === `${issuer}/token`);
    const tokenBody = new URLSearchParams(tokenCall.options.body);
    assert.equal(tokenBody.get('grant_type'), 'authorization_code');
    assert.ok(tokenBody.get('code_verifier'));
    assert.equal(tokenBody.get('client_secret'), clientSecret);
    const exchange = fetchImpl.calls.find((item) => item.url === 'http://127.0.0.1:9099/api/auth/oidc');
    assert.ok(exchange);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('authenticated root proxies content and protected internal auth routes stay hidden', async () => {
  const port = await freePort();
  const origin = `http://127.0.0.1:${port}`;
  const fetchImpl = router();
  const server = createBrowserOidcEdgeServer({ config: config(origin), flowSecret, clientSecret, upstreamOrigin: 'http://127.0.0.1:9099', fetchImpl, now: () => now });
  await new Promise((resolve) => server.listen(port, '127.0.0.1', resolve));
  try {
    const root = await fetch(`${origin}/`, { headers: { Cookie: 'pa_session=ok' }, redirect: 'manual' });
    assert.equal(root.status, 200);
    assert.match(await root.text(), /upstream/);
    assert.equal((await fetch(`${origin}/api/auth/oidc`, { method: 'POST' })).status, 404);
    assert.equal((await fetch(`${origin}/metrics`)).status, 404);
    assert.equal((await fetch(`${origin}/api/logout`, { method: 'POST' })).status, 403);
    const logout = await fetch(`${origin}/api/logout`, { method: 'POST', headers: { Origin: origin } });
    assert.equal(logout.status, 200);
    assert.equal((await fetch(`${origin}/api/logout`, { method: 'POST', headers: { Origin: 'https://attacker.test' } })).status, 403);
    assert.equal((await fetch(`${origin}/api/logout`, { method: 'POST', body: 'x', headers: { Origin: origin } })).status, 413);
  } finally { await new Promise((resolve) => server.close(resolve)); }
});

test('refresh tokens and tampered flow cookies fail closed and clear browser state', async () => {
  const port = await freePort();
  const origin = `http://127.0.0.1:${port}`;
  const fetchImpl = router({ tokenResponse: { id_token: jwt({ iss: issuer, nonce: 'wrong' }), token_type: 'Bearer', refresh_token: 'forbidden' } });
  const server = createBrowserOidcEdgeServer({ config: config(origin), flowSecret, clientSecret, upstreamOrigin: 'http://127.0.0.1:9099', fetchImpl, now: () => now });
  await new Promise((resolve) => server.listen(port, '127.0.0.1', resolve));
  try {
    const start = await fetch(`${origin}/auth/login`, { redirect: 'manual' });
    const authorization = new URL(start.headers.get('location'));
    router.currentNonce = authorization.searchParams.get('nonce');
    const flowCookie = cookiePair(start.headers.get('set-cookie'));
    const callback = new URL('/auth/callback', origin);
    callback.searchParams.set('code', 'code');
    callback.searchParams.set('state', authorization.searchParams.get('state'));
    const failed = await fetch(callback, { headers: { Cookie: flowCookie }, redirect: 'manual' });
    assert.equal(failed.status, 401);
    assert.match(failed.headers.get('set-cookie'), /Max-Age=0/);
    const tampered = await fetch(callback, { headers: { Cookie: `${flowCookie}x` }, redirect: 'manual' });
    assert.equal(tampered.status, 401);
    assert.match(tampered.headers.get('set-cookie'), /Max-Age=0/);
  } finally { await new Promise((resolve) => server.close(resolve)); }
});


test('upstream identity exchange failure clears the one-time browser flow', async () => {
  const port = await freePort();
  const origin = `http://127.0.0.1:${port}`;
  const fetchImpl = router({ exchangeUnavailable: true });
  const server = createBrowserOidcEdgeServer({ config: config(origin), flowSecret, clientSecret, upstreamOrigin: 'http://127.0.0.1:9099', fetchImpl, now: () => now });
  await new Promise((resolve) => server.listen(port, '127.0.0.1', resolve));
  try {
    const start = await fetch(`${origin}/auth/login`, { redirect: 'manual' });
    const authorization = new URL(start.headers.get('location'));
    router.currentNonce = authorization.searchParams.get('nonce');
    const callback = new URL('/auth/callback', origin);
    callback.searchParams.set('code', 'code');
    callback.searchParams.set('state', authorization.searchParams.get('state'));
    const failed = await fetch(callback, { headers: { Cookie: cookiePair(start.headers.get('set-cookie')) }, redirect: 'manual' });
    assert.equal(failed.status, 503);
    assert.match(failed.headers.get('set-cookie'), /Max-Age=0/);
  } finally { await new Promise((resolve) => server.close(resolve)); }
});

test('edge health exposes only bounded configuration identity', async () => {
  const port = await freePort();
  const origin = `http://127.0.0.1:${port}`;
  const server = createBrowserOidcEdgeServer({ config: config(origin), flowSecret, clientSecret, upstreamOrigin: 'http://127.0.0.1:9099', fetchImpl: router(), now: () => now });
  await new Promise((resolve) => server.listen(port, '127.0.0.1', resolve));
  try {
    const response = await fetch(`${origin}/edge/healthz`);
    const value = await response.json();
    assert.equal(value.contract, BROWSER_EDGE_CONTRACT);
    assert.match(value.config_id, /^[0-9a-f]{64}$/);
    assert.equal(JSON.stringify(value).includes(clientSecret), false);
    assert.equal(JSON.stringify(value).includes('127.0.0.1:9099'), false);
  } finally { await new Promise((resolve) => server.close(resolve)); }
});
