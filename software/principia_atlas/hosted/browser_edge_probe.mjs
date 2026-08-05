#!/usr/bin/env node
import { isIP } from 'node:net';

import { BROWSER_EDGE_CONTRACT } from './browser_edge.mjs';
import { canonicalJson, exactKeys, fail, parseStrictJson } from './strict_json.mjs';

export const BROWSER_EDGE_PROBE_CONTRACT = 'principia-atlas-browser-edge-readiness/0.1';
const HOSTED_HEALTH_CONTRACT = 'principia-atlas-hosted-health/0.4';
const MAX_BODY_BYTES = 16384;
const LOOPBACK = new Set(['localhost', '127.0.0.1', '::1', '[::1]']);

function exactLoopbackOrigin(value, label) {
  if (typeof value !== 'string' || value.length < 8 || value.length > 2048) fail(`${label} is invalid`);
  let parsed;
  try { parsed = new URL(value); } catch { fail(`${label} is invalid`); }
  if (!['http:', 'https:'].includes(parsed.protocol)
    || parsed.username || parsed.password || parsed.pathname !== '/'
    || parsed.search || parsed.hash || !LOOPBACK.has(parsed.hostname)) {
    fail(`${label} must be an exact loopback HTTP origin`);
  }
  return parsed.origin;
}

async function readBoundedJson(response, label) {
  const contentType = String(response.headers.get('content-type') ?? '').toLowerCase();
  if (!/^application\/json(?:\s*;|$)/.test(contentType)) fail(`${label} content type is invalid`);
  const declared = response.headers.get('content-length');
  if (declared !== null && (!/^\d+$/.test(declared) || Number(declared) > MAX_BODY_BYTES)) {
    fail(`${label} response exceeds resource limit`);
  }
  if (!response.body) fail(`${label} response body is missing`);
  const reader = response.body.getReader();
  const chunks = [];
  let total = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > MAX_BODY_BYTES) fail(`${label} response exceeds resource limit`);
      chunks.push(Buffer.from(value));
    }
  } finally {
    reader.releaseLock();
  }
  return parseStrictJson(Buffer.concat(chunks, total), label);
}

async function fetchDependency(fetchImpl, url, label, timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  timer.unref?.();
  let response;
  try {
    response = await fetchImpl(url, {
      method: 'GET',
      redirect: 'error',
      headers: { Accept: 'application/json' },
      signal: controller.signal,
    });
  } catch {
    fail(`${label} is unavailable`);
  } finally {
    clearTimeout(timer);
  }
  if (response.status !== 200) fail(`${label} is not ready`);
  return readBoundedJson(response, label);
}

export async function checkBrowserEdgeReadiness({
  edgeOrigin,
  upstreamOrigin,
  fetchImpl = globalThis.fetch,
  timeoutMs = 1500,
} = {}) {
  if (typeof fetchImpl !== 'function') fail('browser edge readiness fetch implementation is invalid');
  if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 200 || timeoutMs > 10000) fail('browser edge readiness timeout is invalid');
  const edge = exactLoopbackOrigin(edgeOrigin, 'browser edge readiness edge origin');
  const upstream = exactLoopbackOrigin(upstreamOrigin, 'browser edge readiness upstream origin');
  if (edge === upstream) fail('browser edge readiness origins must be distinct');

  const edgeHealth = await fetchDependency(fetchImpl, `${edge}/edge/healthz`, 'browser edge health', timeoutMs);
  exactKeys(edgeHealth, ['status', 'contract', 'config_id', 'upstream'], 'browser edge health');
  if (edgeHealth.status !== 'ok'
    || edgeHealth.contract !== BROWSER_EDGE_CONTRACT
    || typeof edgeHealth.config_id !== 'string'
    || !/^[0-9a-f]{64}$/.test(edgeHealth.config_id)
    || edgeHealth.upstream !== 'configured-loopback') {
    fail('browser edge health contract is invalid');
  }

  const hostedReadiness = await fetchDependency(fetchImpl, `${upstream}/readyz`, 'hosted readiness', timeoutMs);
  if (!hostedReadiness || typeof hostedReadiness !== 'object' || Array.isArray(hostedReadiness)) {
    fail('hosted readiness contract is invalid');
  }
  if (hostedReadiness.status !== 'ready'
    || hostedReadiness.contract !== HOSTED_HEALTH_CONTRACT
    || hostedReadiness.release_serving !== true) {
    fail('hosted readiness contract is invalid');
  }

  return Object.freeze({
    status: 'ready',
    contract: BROWSER_EDGE_PROBE_CONTRACT,
    edge_contract: edgeHealth.contract,
    hosted_contract: hostedReadiness.contract,
    config_id: edgeHealth.config_id,
  });
}

function parseArgs(argv) {
  const output = {
    edgeOrigin: 'http://127.0.0.1:8081',
    upstreamOrigin: 'http://127.0.0.1:8080',
    timeoutMs: 1500,
  };
  const seen = new Set();
  for (let index = 0; index < argv.length; index += 2) {
    const name = argv[index];
    const value = argv[index + 1];
    if (!['--edge-origin', '--upstream-origin', '--timeout-ms'].includes(name)
      || !value || seen.has(name)) fail('browser edge readiness arguments are invalid');
    seen.add(name);
    if (name === '--edge-origin') output.edgeOrigin = value;
    else if (name === '--upstream-origin') output.upstreamOrigin = value;
    else output.timeoutMs = Number(value);
  }
  return output;
}

export async function main(argv = process.argv.slice(2)) {
  const result = await checkBrowserEdgeReadiness(parseArgs(argv));
  process.stdout.write(`${canonicalJson(result)}\n`);
  return result;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}
