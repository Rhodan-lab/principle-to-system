#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import http from 'node:http';
import https from 'node:https';
import { isIP } from 'node:net';

import { canonicalJson, fail, parseStrictJson } from '../strict_json.mjs';

const MAX_RESPONSE_BYTES = 4 * 1024 * 1024;

function parseArgs(argv) {
  const output = { maxRedirects: 10, sessionCookie: 'principia_atlas_session' };
  const seen = new Set();
  for (let index = 0; index < argv.length; index += 2) {
    const name = argv[index];
    const value = argv[index + 1];
    if (!name?.startsWith('--') || !value || seen.has(name)) fail('browser smoke arguments are invalid');
    seen.add(name);
    output[name.slice(2).replaceAll(/-([a-z])/g, (_, letter) => letter.toUpperCase())] = value;
  }
  for (const required of ['origin', 'originAddress', 'issuer', 'issuerAddress', 'ca', 'version']) {
    if (!output[required]) fail(`browser smoke --${required.replaceAll(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)} is required`);
  }
  output.maxRedirects = Number(output.maxRedirects);
  if (!Number.isInteger(output.maxRedirects) || output.maxRedirects < 1 || output.maxRedirects > 20) fail('browser smoke redirect limit is invalid');
  if (isIP(output.originAddress) === 0 || isIP(output.issuerAddress) === 0) fail('browser smoke address is invalid');
  if (typeof output.sessionCookie !== 'string' || !/^[A-Za-z0-9!#$%&'*+.^_`|~-]{1,120}$/.test(output.sessionCookie)) fail('browser smoke session cookie name is invalid');
  return output;
}

function exactOrigin(value, label, protocols) {
  let parsed;
  try { parsed = new URL(value); } catch { fail(`${label} is invalid`); }
  if (!protocols.includes(parsed.protocol) || parsed.username || parsed.password || parsed.pathname !== '/' || parsed.search || parsed.hash) fail(`${label} must be an exact origin`);
  return parsed.origin;
}

function hostCookies(jar, url, create = false) {
  let cookies = jar.get(url.hostname);
  if (!cookies && create) {
    cookies = new Map();
    jar.set(url.hostname, cookies);
  }
  return cookies ?? new Map();
}

function cookieHeader(jar, url) {
  return [...hostCookies(jar, url)].map(([name, value]) => `${name}=${value}`).join('; ');
}

function updateCookies(jar, url, response) {
  const values = response.headers['set-cookie'] ?? [];
  const cookies = hostCookies(jar, url, true);
  for (const raw of Array.isArray(values) ? values : [values]) {
    const parts = raw.split(';').map((part) => part.trim());
    const position = parts[0].indexOf('=');
    if (position < 1) fail('browser smoke received a malformed cookie');
    const name = parts[0].slice(0, position);
    const value = parts[0].slice(position + 1);
    const expired = parts.some((part) => /^Max-Age=0$/i.test(part));
    if (expired || value === '') cookies.delete(name);
    else cookies.set(name, value);
  }
}

function addressLookup(address) {
  const family = isIP(address);
  return (_hostname, options, callback) => {
    if (options?.all) callback(null, [{ address, family }]);
    else callback(null, address, family);
  };
}

async function request(urlInput, {
  ca,
  jar,
  origin,
  originAddress,
  issuer,
  issuerAddress,
  method = 'GET',
  originHeader = null,
  cookieHeaderOverride = null,
} = {}) {
  const url = new URL(urlInput);
  const transport = url.protocol === 'https:' ? https : http;
  if (!transport) fail('browser smoke protocol is invalid');
  const resolvedAddress = url.origin === origin
    ? originAddress
    : url.origin === issuer
      ? issuerAddress
      : null;
  return new Promise((resolveRequest, reject) => {
    const headers = { Accept: 'text/html, application/json' };
    const cookie = cookieHeaderOverride ?? cookieHeader(jar, url);
    if (cookie) headers.Cookie = cookie;
    if (originHeader !== null) headers.Origin = originHeader;
    const requestHandle = transport.request(url, {
      method,
      headers,
      ca: url.protocol === 'https:' ? ca : undefined,
      rejectUnauthorized: true,
      timeout: 5000,
      lookup: resolvedAddress ? addressLookup(resolvedAddress) : undefined,
    }, (response) => {
      const chunks = [];
      let total = 0;
      response.on('data', (chunk) => {
        total += chunk.length;
        if (total > MAX_RESPONSE_BYTES) {
          response.destroy(new Error('browser smoke response exceeds resource limit'));
          return;
        }
        chunks.push(Buffer.from(chunk));
      });
      response.on('end', () => resolveRequest({
        status: response.statusCode ?? 0,
        headers: response.headers,
        body: Buffer.concat(chunks, total),
      }));
    });
    requestHandle.once('timeout', () => requestHandle.destroy(new Error('browser smoke request timed out')));
    requestHandle.once('error', reject);
    requestHandle.end();
  });
}

async function follow(start, options) {
  let current = new URL(start);
  for (let count = 0; count <= options.maxRedirects; count += 1) {
    if (![options.origin, options.issuer].includes(current.origin)) fail('browser smoke redirect escaped trusted origins');
    const response = await request(current, options);
    updateCookies(options.jar, current, response);
    if (![301, 302, 303, 307, 308].includes(response.status)) return { ...response, url: current };
    const location = response.headers.location;
    if (typeof location !== 'string' || !location) fail('browser smoke redirect is missing Location');
    current = new URL(location, current);
  }
  fail('browser smoke redirect limit exceeded');
}

export async function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  const origin = exactOrigin(args.origin, 'browser smoke origin', ['https:']);
  const issuer = exactOrigin(args.issuer, 'browser smoke issuer', ['https:']);
  const ca = await readFile(args.ca);
  const jar = new Map();
  const requestOptions = {
    ca,
    jar,
    origin,
    originAddress: args.originAddress,
    issuer,
    issuerAddress: args.issuerAddress,
    maxRedirects: args.maxRedirects,
  };

  const landing = await follow(`${origin}/`, requestOptions);
  assert.equal(landing.status, 200);
  assert.match(String(landing.headers['content-type'] ?? ''), /^text\/html/i);
  assert.ok(landing.body.length > 100);
  const edgeCookies = hostCookies(jar, new URL(origin));
  assert.ok(edgeCookies.has(args.sessionCookie));
  const revokedCookieValue = edgeCookies.get(args.sessionCookie);
  assert.equal(typeof revokedCookieValue, 'string');
  assert.ok(revokedCookieValue.length > 32);
  const revokedCookieHeader = `${args.sessionCookie}=${revokedCookieValue}`;
  assert.equal(edgeCookies.has('__Host-pa_oidc_flow'), false);
  assert.equal(hostCookies(jar, new URL(issuer)).has('__Host-pa_oidc_flow'), false);

  const sessionResponse = await request(`${origin}/api/session`, requestOptions);
  assert.equal(sessionResponse.status, 200);
  const session = parseStrictJson(sessionResponse.body, 'browser smoke session');
  assert.equal(session.tenant_id, 'local-preview');
  assert.deepEqual(session.roles, ['learner']);
  assert.equal(typeof session.subject, 'string');
  assert.ok(session.subject.length > 8);

  const releaseResponse = await request(`${origin}/app/${encodeURIComponent(args.version)}/`, requestOptions);
  assert.equal(releaseResponse.status, 200);
  assert.match(String(releaseResponse.headers['content-type'] ?? ''), /^text\/html/i);
  assert.ok(releaseResponse.body.length > 100);

  const hiddenOidc = await request(`${origin}/api/auth/oidc`, { ...requestOptions, method: 'POST' });
  assert.equal(hiddenOidc.status, 404);
  const hiddenMetrics = await request(`${origin}/metrics`, requestOptions);
  assert.equal(hiddenMetrics.status, 404);

  const logoutResponse = await request(`${origin}/api/logout`, {
    ...requestOptions,
    method: 'POST',
    originHeader: origin,
  });
  updateCookies(jar, new URL(origin), logoutResponse);
  assert.equal(logoutResponse.status, 200);
  const logout = parseStrictJson(logoutResponse.body, 'browser smoke logout');
  assert.equal(logout.status, 'signed_out');
  assert.equal(edgeCookies.has(args.sessionCookie), false);

  const sessionAfterLogout = await request(`${origin}/api/session`, requestOptions);
  assert.equal(sessionAfterLogout.status, 401);
  const revokedSessionReplay = await request(`${origin}/api/session`, {
    ...requestOptions,
    cookieHeaderOverride: revokedCookieHeader,
  });
  assert.equal(revokedSessionReplay.status, 401);
  const revokedReleaseReplay = await request(`${origin}/app/${encodeURIComponent(args.version)}/`, {
    ...requestOptions,
    cookieHeaderOverride: revokedCookieHeader,
  });
  assert.equal(revokedReleaseReplay.status, 401);

  const result = {
    status: 'ok',
    login: 'authorization-code-pkce',
    logout: 'durable-session-revocation',
    tls_gateway: true,
    tenant_id: session.tenant_id,
    roles: session.roles,
    release_version: args.version,
    post_logout_session_status: sessionAfterLogout.status,
    revoked_session_replay_status: revokedSessionReplay.status,
    revoked_release_replay_status: revokedReleaseReplay.status,
    hidden_routes: ['/api/auth/oidc', '/metrics'],
  };
  process.stdout.write(`${canonicalJson(result)}\n`);
  return result;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}
