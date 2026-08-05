import assert from 'node:assert/strict';
import test from 'node:test';

import {
  BROWSER_OIDC_CONTRACT,
  createBrowserOidcFlow,
  sealBrowserOidcConfig,
  verifyBrowserOidcConfig,
} from '../principia_atlas/hosted/browser_oidc.mjs';

const now = 1_800_000_000;
const flowSecret = 'flow-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const clientSecret = 'client-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const issuer = 'https://identity.example.test';

function config(overrides = {}) {
  return sealBrowserOidcConfig({
    contract: BROWSER_OIDC_CONTRACT,
    product: 'Principia & Atlas',
    issuer,
    public_origin: 'https://learn.example.test',
    authorization_endpoint: `${issuer}/authorize`,
    token_endpoint: `${issuer}/token`,
    client_id: 'principia-atlas-browser',
    client_auth_method: 'client_secret_post',
    scopes: ['openid', 'email'],
    login_path: '/auth/login',
    callback_path: '/auth/callback',
    default_return_to: '/',
    flow_ttl_seconds: 300,
    token_timeout_ms: 2000,
    token_max_bytes: 65536,
    cookie: { name: '__Host-pa_oidc_flow', secure: true, same_site: 'Lax' },
    ...overrides,
  });
}

function jwt(payload) {
  const encode = (value) => Buffer.from(JSON.stringify(value), 'utf8').toString('base64url');
  return `${encode({ alg: 'RS256', kid: 'test' })}.${encode(payload)}.${Buffer.alloc(64, 7).toString('base64url')}`;
}

function cookieHeader(setCookie) {
  return setCookie.split(';')[0];
}

test('sealed browser OIDC config rejects offline access and insecure HTTPS cookies', () => {
  const value = config();
  assert.equal(verifyBrowserOidcConfig(value).config_id, value.config_id);
  assert.throws(() => config({ scopes: ['openid', 'offline_access'] }), /offline_access/);
  assert.throws(() => config({ cookie: { name: 'pa_flow', secure: false, same_site: 'Lax' } }), /secure flow cookie/);
});

test('begin creates bounded state, nonce, PKCE and encrypted flow cookie', () => {
  let counter = 0;
  const flow = createBrowserOidcFlow({
    config: config(),
    flowSecret,
    clientSecret,
    now: () => now,
    random: (size) => Buffer.alloc(size, ++counter),
  });
  const started = flow.begin('/app/0.1.0-alpha.1/?tab=learn');
  const location = new URL(started.location);
  assert.equal(location.origin, issuer);
  assert.equal(location.searchParams.get('response_type'), 'code');
  assert.equal(location.searchParams.get('code_challenge_method'), 'S256');
  assert.equal(location.searchParams.get('redirect_uri'), 'https://learn.example.test/auth/callback');
  assert.equal(location.searchParams.get('scope'), 'openid email');
  assert.match(location.searchParams.get('state'), /^[A-Za-z0-9_-]{43}$/);
  assert.match(location.searchParams.get('nonce'), /^[A-Za-z0-9_-]{43}$/);
  assert.match(location.searchParams.get('code_challenge'), /^[A-Za-z0-9_-]{43}$/);
  assert.match(started.set_cookie, /^__Host-pa_oidc_flow=v1\./);
  assert.match(started.set_cookie, /; Path=\/; HttpOnly; SameSite=Lax; Max-Age=300; Secure$/);
  assert.equal(started.set_cookie.includes(location.searchParams.get('nonce')), false);
  flow.close();
});

test('complete exchanges code with PKCE, verifies nonce and returns ID token', async () => {
  let tokenRequest;
  let nonce;
  const flow = createBrowserOidcFlow({
    config: config(),
    flowSecret,
    clientSecret,
    now: () => now,
    random: (size) => Buffer.alloc(size, 9),
    fetchImpl: async (url, options) => {
      tokenRequest = { url, options, params: new URLSearchParams(options.body) };
      const idToken = jwt({ iss: issuer, nonce, sub: 'external-learner' });
      return new Response(JSON.stringify({ token_type: 'Bearer', id_token: idToken }), {
        status: 200,
        headers: { 'content-type': 'application/json; charset=utf-8' },
      });
    },
  });
  const started = flow.begin('/app/0.1.0-alpha.1/');
  const authorization = new URL(started.location);
  nonce = authorization.searchParams.get('nonce');
  const callback = new URL('https://learn.example.test/auth/callback');
  callback.searchParams.set('code', 'authorization-code');
  callback.searchParams.set('state', authorization.searchParams.get('state'));
  callback.searchParams.set('iss', issuer);
  const result = await flow.complete(callback.toString(), cookieHeader(started.set_cookie));
  assert.equal(result.status, 'complete');
  assert.equal(result.return_to, '/app/0.1.0-alpha.1/');
  assert.equal(result.id_token.split('.').length, 3);
  assert.equal(tokenRequest.url, `${issuer}/token`);
  assert.equal(tokenRequest.options.redirect, 'error');
  assert.equal(tokenRequest.params.get('grant_type'), 'authorization_code');
  assert.equal(tokenRequest.params.get('code'), 'authorization-code');
  assert.equal(tokenRequest.params.get('client_id'), 'principia-atlas-browser');
  assert.equal(tokenRequest.params.get('client_secret'), clientSecret);
  assert.match(tokenRequest.params.get('code_verifier'), /^[A-Za-z0-9_-]{64}$/);
  assert.match(result.clear_cookie, /Max-Age=0/);
  flow.close();
});

test('callback rejects tampering, duplicate state, nonce mismatch and refresh tokens', async () => {
  let nonce;
  let mode = 'nonce';
  const flow = createBrowserOidcFlow({
    config: config(),
    flowSecret,
    clientSecret,
    now: () => now,
    fetchImpl: async () => {
      const payload = mode === 'nonce'
        ? { token_type: 'Bearer', id_token: jwt({ iss: issuer, nonce: 'wrong' }) }
        : { token_type: 'Bearer', id_token: jwt({ iss: issuer, nonce }), refresh_token: 'prohibited' };
      return new Response(JSON.stringify(payload), { status: 200, headers: { 'content-type': 'application/json' } });
    },
  });
  const started = flow.begin('/');
  const authorization = new URL(started.location);
  nonce = authorization.searchParams.get('nonce');
  const state = authorization.searchParams.get('state');
  const valid = `https://learn.example.test/auth/callback?code=x&state=${state}`;
  await assert.rejects(() => flow.complete(valid, `${cookieHeader(started.set_cookie)}x`), /(?:cookie|flow tag)/);
  await assert.rejects(() => flow.complete(`${valid}&state=${state}`, cookieHeader(started.set_cookie)), /duplicate state/);
  await assert.rejects(() => flow.complete(valid, cookieHeader(started.set_cookie)), /nonce mismatch/);
  mode = 'refresh';
  await assert.rejects(() => flow.complete(valid, cookieHeader(started.set_cookie)), /refresh tokens/);
  flow.close();
});

test('return targets remain same-origin and authentication routes are rejected', () => {
  const flow = createBrowserOidcFlow({ config: config(), flowSecret, clientSecret, now: () => now });
  assert.throws(() => flow.begin('https://evil.example/'), /return path/);
  assert.throws(() => flow.begin('//evil.example/'), /return path/);
  assert.throws(() => flow.begin('/auth/callback'), /authentication route/);
  flow.close();
});

test('public clients cannot carry a client secret', () => {
  const publicConfig = config({ client_auth_method: 'none' });
  assert.throws(() => createBrowserOidcFlow({ config: publicConfig, flowSecret, clientSecret }), /not allowed/);
  const flow = createBrowserOidcFlow({ config: publicConfig, flowSecret });
  flow.close();
});
