#!/usr/bin/env node
import {
  createHash,
  createSign,
  randomBytes,
  timingSafeEqual,
} from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { createServer } from 'node:https';
import { resolve } from 'node:path';

import { readSecretFile } from '../secrets.mjs';
import { canonicalJson, fail, parseStrictJson } from '../strict_json.mjs';

const MAX_BODY_BYTES = 8192;
const MAX_CODES = 256;
const TOKEN = /^[A-Za-z0-9._~-]{1,256}$/;
const BASE64URL = /^[A-Za-z0-9_-]+$/;

function parseArgs(argv) {
  const output = { host: '127.0.0.1', port: 9443, codeTtlSeconds: 120 };
  const seen = new Set();
  for (let index = 0; index < argv.length; index += 2) {
    const name = argv[index];
    const value = argv[index + 1];
    if (!name?.startsWith('--') || !value || seen.has(name)) fail('mock OIDC arguments are invalid');
    seen.add(name);
    output[name.slice(2).replaceAll(/-([a-z])/g, (_, letter) => letter.toUpperCase())] = value;
  }
  for (const required of [
    'issuer', 'clientId', 'clientSecretFile', 'audience', 'redirectUri',
    'tlsKey', 'tlsCert', 'signingKey', 'jwks',
  ]) {
    if (!output[required]) fail(`mock OIDC --${required.replaceAll(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)} is required`);
  }
  output.port = Number(output.port);
  output.codeTtlSeconds = Number(output.codeTtlSeconds);
  if (!Number.isInteger(output.port) || output.port < 1 || output.port > 65535) fail('mock OIDC port is invalid');
  if (!Number.isInteger(output.codeTtlSeconds) || output.codeTtlSeconds < 30 || output.codeTtlSeconds > 300) fail('mock OIDC code TTL is invalid');
  return output;
}

function exactHttpsUrl(value, label) {
  let parsed;
  try { parsed = new URL(value); } catch { fail(`${label} is invalid`); }
  if (parsed.protocol !== 'https:' || parsed.username || parsed.password || parsed.search || parsed.hash) fail(`${label} is invalid`);
  return parsed.toString().replace(/\/$/, '');
}

function exactCallback(value) {
  let parsed;
  try { parsed = new URL(value); } catch { fail('mock OIDC redirect URI is invalid'); }
  if (!['http:', 'https:'].includes(parsed.protocol) || parsed.username || parsed.password || parsed.hash) fail('mock OIDC redirect URI is invalid');
  return parsed.toString();
}

function one(params, name, { required = true, max = 4096 } = {}) {
  const values = params.getAll(name);
  if (values.length > 1) fail(`mock OIDC duplicate ${name}`);
  if (values.length === 0) {
    if (required) fail(`mock OIDC missing ${name}`);
    return null;
  }
  const value = values[0];
  if (!value || value.length > max || /[\u0000-\u001f\u007f]/.test(value)) fail(`mock OIDC invalid ${name}`);
  return value;
}

function constantEquals(left, right) {
  if (typeof left !== 'string' || typeof right !== 'string') return false;
  const a = Buffer.from(left, 'utf8');
  const b = Buffer.from(right, 'utf8');
  return a.length === b.length && timingSafeEqual(a, b);
}

function base64urlJson(value) {
  return Buffer.from(canonicalJson(value), 'utf8').toString('base64url');
}

function signJwt(payload, privateKey, kid) {
  const header = base64urlJson({ alg: 'RS256', kid, typ: 'JWT' });
  const body = base64urlJson(payload);
  const input = `${header}.${body}`;
  const signer = createSign('RSA-SHA256');
  signer.update(input, 'ascii');
  signer.end();
  return `${input}.${signer.sign(privateKey).toString('base64url')}`;
}

async function readBody(request) {
  const chunks = [];
  let total = 0;
  for await (const chunk of request) {
    total += chunk.length;
    if (total > MAX_BODY_BYTES) fail('mock OIDC request body exceeds resource limit');
    chunks.push(Buffer.from(chunk));
  }
  return Buffer.concat(chunks).toString('utf8');
}

function sendJson(response, status, value) {
  const raw = Buffer.from(canonicalJson(value), 'utf8');
  response.statusCode = status;
  response.setHeader('Content-Type', 'application/json; charset=utf-8');
  response.setHeader('Content-Length', String(raw.length));
  response.setHeader('Cache-Control', 'no-store');
  response.setHeader('X-Content-Type-Options', 'nosniff');
  response.end(raw);
}

function sendEmpty(response, status, location = null) {
  response.statusCode = status;
  response.setHeader('Cache-Control', 'no-store');
  if (location !== null) response.setHeader('Location', location);
  response.setHeader('Content-Length', '0');
  response.end();
}

export async function createMockOidcProvider(options = {}) {
  const args = { ...parseArgs([]), ...options };
  const issuer = exactHttpsUrl(args.issuer, 'mock OIDC issuer');
  const redirectUri = exactCallback(args.redirectUri);
  if (typeof args.clientId !== 'string' || !TOKEN.test(args.clientId)) fail('mock OIDC client ID is invalid');
  if (typeof args.audience !== 'string' || !TOKEN.test(args.audience)) fail('mock OIDC audience is invalid');
  const clientSecret = readSecretFile(args.clientSecretFile, 'mock OIDC client secret');
  const [tlsKey, tlsCert, signingKey, jwksRaw] = await Promise.all([
    readFile(resolve(args.tlsKey)),
    readFile(resolve(args.tlsCert)),
    readFile(resolve(args.signingKey)),
    readFile(resolve(args.jwks)),
  ]);
  const jwks = parseStrictJson(jwksRaw, 'mock OIDC JWKS');
  if (!jwks || !Array.isArray(jwks.keys) || jwks.keys.length !== 1) fail('mock OIDC JWKS must contain exactly one key');
  const kid = jwks.keys[0]?.kid;
  if (typeof kid !== 'string' || !TOKEN.test(kid)) fail('mock OIDC JWKS kid is invalid');
  const codes = new Map();
  let closed = false;

  const purge = (current) => {
    for (const [code, record] of codes) {
      if (record.expiresAt < current) codes.delete(code);
    }
  };

  const server = createServer({ key: tlsKey, cert: tlsCert }, (request, response) => {
    const handle = async () => {
      const url = new URL(request.url ?? '/', issuer);
      if (url.origin !== issuer) return sendJson(response, 400, { error: 'invalid_request' });
      if (request.method === 'GET' && url.pathname === '/healthz') return sendJson(response, 200, { status: 'ok' });
      if (request.method === 'GET' && url.pathname === '/jwks') return sendJson(response, 200, jwks);

      if (request.method === 'GET' && url.pathname === '/authorize') {
        const responseType = one(url.searchParams, 'response_type');
        const clientId = one(url.searchParams, 'client_id');
        const callback = one(url.searchParams, 'redirect_uri');
        const scope = one(url.searchParams, 'scope');
        const state = one(url.searchParams, 'state', { max: 256 });
        const nonce = one(url.searchParams, 'nonce', { max: 256 });
        const challenge = one(url.searchParams, 'code_challenge', { max: 256 });
        const challengeMethod = one(url.searchParams, 'code_challenge_method');
        if (responseType !== 'code' || clientId !== args.clientId || callback !== redirectUri) fail('mock OIDC authorization request is invalid');
        if (!scope.split(/\s+/).includes('openid')) fail('mock OIDC openid scope is required');
        if (!BASE64URL.test(state) || !BASE64URL.test(nonce) || !BASE64URL.test(challenge) || challengeMethod !== 'S256') fail('mock OIDC PKCE request is invalid');
        const current = Math.floor(Date.now() / 1000);
        purge(current);
        if (codes.size >= MAX_CODES) fail('mock OIDC authorization code capacity exceeded');
        const code = randomBytes(32).toString('base64url');
        codes.set(code, { nonce, challenge, expiresAt: current + args.codeTtlSeconds });
        const location = new URL(redirectUri);
        location.searchParams.set('code', code);
        location.searchParams.set('state', state);
        location.searchParams.set('iss', issuer);
        return sendEmpty(response, 302, location.toString());
      }

      if (request.method === 'POST' && url.pathname === '/token') {
        const contentType = String(request.headers['content-type'] ?? '').toLowerCase();
        if (!/^application\/x-www-form-urlencoded(?:\s*;|$)/.test(contentType)) fail('mock OIDC token content type is invalid');
        const form = new URLSearchParams(await readBody(request));
        const grantType = one(form, 'grant_type');
        const code = one(form, 'code');
        const callback = one(form, 'redirect_uri');
        const clientId = one(form, 'client_id');
        const verifier = one(form, 'code_verifier', { max: 256 });
        const suppliedSecret = one(form, 'client_secret');
        if (grantType !== 'authorization_code' || callback !== redirectUri || clientId !== args.clientId) fail('mock OIDC token request is invalid');
        if (!constantEquals(suppliedSecret, clientSecret.toString('utf8'))) return sendJson(response, 401, { error: 'invalid_client' });
        const current = Math.floor(Date.now() / 1000);
        purge(current);
        const record = codes.get(code);
        codes.delete(code);
        if (!record || record.expiresAt < current) return sendJson(response, 400, { error: 'invalid_grant' });
        const expected = createHash('sha256').update(verifier, 'ascii').digest('base64url');
        if (!constantEquals(expected, record.challenge)) return sendJson(response, 400, { error: 'invalid_grant' });
        const idToken = signJwt({
          iss: issuer,
          aud: args.audience,
          sub: 'browser-smoke-learner',
          organization: 'external-school',
          groups: ['students'],
          email_verified: true,
          nonce: record.nonce,
          iat: current,
          exp: current + 300,
          jti: randomBytes(24).toString('base64url'),
        }, signingKey, kid);
        return sendJson(response, 200, {
          token_type: 'Bearer',
          expires_in: 300,
          id_token: idToken,
        });
      }

      return sendJson(response, 404, { error: 'not_found' });
    };
    handle().catch(() => sendJson(response, 400, { error: 'invalid_request' }));
  });

  server.once('close', () => {
    if (closed) return;
    closed = true;
    clientSecret.fill(0);
    signingKey.fill(0);
    tlsKey.fill(0);
    codes.clear();
  });
  return server;
}

export async function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  const server = await createMockOidcProvider(args);
  await new Promise((resolveListen, reject) => {
    server.once('error', reject);
    server.listen(args.port, args.host, resolveListen);
  });
  console.log(`Mock OIDC provider: ${args.issuer}`);
  let stopping = false;
  const stop = () => {
    if (stopping) return server.closeAllConnections?.();
    stopping = true;
    server.close();
    server.closeIdleConnections?.();
  };
  process.once('SIGINT', stop);
  process.once('SIGTERM', stop);
  return server;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}
