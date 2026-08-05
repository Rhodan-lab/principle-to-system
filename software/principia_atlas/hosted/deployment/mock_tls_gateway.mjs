#!/usr/bin/env node
import http from 'node:http';
import https from 'node:https';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import { fail } from '../strict_json.mjs';

const MAX_REQUEST_BYTES = 8192;
const MAX_RESPONSE_BYTES = 64 * 1024 * 1024;
const HOP_BY_HOP = new Set([
  'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
  'te', 'trailer', 'transfer-encoding', 'upgrade',
]);

function parseArgs(argv) {
  const output = { host: '127.0.0.1', port: 18443, upstreamOrigin: 'http://127.0.0.1:8081' };
  const seen = new Set();
  for (let index = 0; index < argv.length; index += 2) {
    const name = argv[index];
    const value = argv[index + 1];
    if (!name?.startsWith('--') || !value || seen.has(name)) fail('TLS gateway arguments are invalid');
    seen.add(name);
    output[name.slice(2).replaceAll(/-([a-z])/g, (_, letter) => letter.toUpperCase())] = value;
  }
  output.port = Number(output.port);
  return output;
}

function validateOptions(options) {
  const value = { host: '127.0.0.1', port: 18443, upstreamOrigin: 'http://127.0.0.1:8081', ...options };
  if (!value.tlsKey || !value.tlsCert) fail('TLS gateway key and certificate are required');
  if (!Number.isInteger(value.port) || value.port < 1 || value.port > 65535) fail('TLS gateway port is invalid');
  let upstream;
  try { upstream = new URL(value.upstreamOrigin); } catch { fail('TLS gateway upstream origin is invalid'); }
  if (upstream.origin !== value.upstreamOrigin || upstream.protocol !== 'http:'
    || upstream.hostname !== '127.0.0.1' || upstream.pathname !== '/'
    || upstream.username || upstream.password || upstream.search || upstream.hash) {
    fail('TLS gateway upstream must be an exact loopback HTTP origin');
  }
  value.upstreamOrigin = upstream.origin;
  return value;
}

function requestHeaders(request) {
  const headers = {};
  for (const [name, value] of Object.entries(request.headers)) {
    if (value === undefined || HOP_BY_HOP.has(name)) continue;
    headers[name] = value;
  }
  headers['x-forwarded-proto'] = 'https';
  return headers;
}

function responseHeaders(upstream, response) {
  for (const [name, value] of Object.entries(upstream.headers)) {
    if (value === undefined || HOP_BY_HOP.has(name)) continue;
    response.setHeader(name, value);
  }
}

export async function createMockTlsGateway(options = {}) {
  const config = validateOptions(options);
  const [key, cert] = await Promise.all([
    readFile(resolve(config.tlsKey)),
    readFile(resolve(config.tlsCert)),
  ]);
  const upstream = new URL(config.upstreamOrigin);
  const server = https.createServer({ key, cert }, (request, response) => {
    if (!['GET', 'HEAD', 'POST'].includes(request.method ?? '')) {
      response.statusCode = 405;
      response.setHeader('Allow', 'GET, HEAD, POST');
      response.setHeader('Content-Length', '0');
      response.end();
      return;
    }
    let target;
    try { target = new URL(request.url ?? '/', upstream); } catch {
      response.statusCode = 400;
      response.setHeader('Content-Length', '0');
      response.end();
      return;
    }
    if (target.origin !== upstream.origin) {
      response.statusCode = 400;
      response.setHeader('Content-Length', '0');
      response.end();
      return;
    }
    let requestBytes = 0;
    const proxy = http.request(target, {
      method: request.method,
      headers: requestHeaders(request),
      timeout: 5000,
    }, (upstreamResponse) => {
      response.statusCode = upstreamResponse.statusCode ?? 502;
      responseHeaders(upstreamResponse, response);
      let responseBytes = 0;
      upstreamResponse.on('data', (chunk) => {
        responseBytes += chunk.length;
        if (responseBytes > MAX_RESPONSE_BYTES) {
          upstreamResponse.destroy(new Error('TLS gateway upstream response exceeds resource limit'));
          response.destroy();
          return;
        }
        if (request.method !== 'HEAD') response.write(chunk);
      });
      upstreamResponse.on('end', () => response.end());
      upstreamResponse.on('error', () => response.destroy());
    });
    proxy.once('timeout', () => proxy.destroy(new Error('TLS gateway upstream timed out')));
    proxy.once('error', () => {
      if (response.headersSent) response.destroy();
      else {
        response.statusCode = 502;
        response.setHeader('Content-Length', '0');
        response.end();
      }
    });
    request.on('data', (chunk) => {
      requestBytes += chunk.length;
      if (requestBytes > MAX_REQUEST_BYTES) {
        request.destroy(new Error('TLS gateway request exceeds resource limit'));
        proxy.destroy();
        return;
      }
      proxy.write(chunk);
    });
    request.on('end', () => proxy.end());
    request.on('error', () => proxy.destroy());
  });
  server.once('close', () => {
    key.fill(0);
  });
  return server;
}

export async function main(argv = process.argv.slice(2)) {
  const args = validateOptions(parseArgs(argv));
  const server = await createMockTlsGateway(args);
  await new Promise((resolveListen, reject) => {
    server.once('error', reject);
    server.listen(args.port, args.host, resolveListen);
  });
  console.log(`Mock TLS gateway: https://${args.host}:${args.port}`);
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
