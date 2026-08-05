#!/usr/bin/env node
import { readFile } from 'node:fs/promises';
import { isIP } from 'node:net';
import { resolve } from 'node:path';
import { verifyTenantCatalogCompatibility } from './catalog.mjs';
import { createControlPlaneServer } from './control_plane.mjs';
import { createAuditLogger, createMetricsRegistry } from './observability.mjs';
import { readSecretFile } from './secrets.mjs';
import { authStateInfo, openSqliteAuthState } from './state.mjs';
import { loadHostedStore } from './store.mjs';
import { parseStrictJson } from './strict_json.mjs';

function parseArgs(argv) {
  const output = {
    host: '127.0.0.1',
    port: 8080,
    allowNetwork: false,
    instanceId: process.env.HOSTNAME || 'local',
    shutdownTimeoutMs: 10000,
  };
  for (let index = 0; index < argv.length; index += 1) {
    const item = argv[index];
    if (item === '--allow-network') output.allowNetwork = true;
    else if ([
      '--catalog', '--tenants', '--store', '--state', '--host', '--port',
      '--identity-secret-file', '--session-secret-file', '--metrics-token-file',
      '--audit-log', '--instance-id', '--shutdown-timeout-ms',
    ].includes(item)) {
      const value = argv[++index];
      if (!value) throw new Error(`${item} requires a value`);
      const key = item.slice(2).replaceAll(/-([a-z])/g, (_, letter) => letter.toUpperCase());
      output[key] = value;
    } else throw new Error(`unknown argument: ${item}`);
  }
  if (!output.catalog || !output.tenants || !output.store || !output.state || !output.identitySecretFile || !output.sessionSecretFile) {
    throw new Error('--catalog, --tenants, --store, --state, --identity-secret-file, and --session-secret-file are required');
  }
  output.port = Number(output.port);
  output.shutdownTimeoutMs = Number(output.shutdownTimeoutMs);
  if (!Number.isInteger(output.port) || output.port < 0 || output.port > 65535) throw new Error('--port is invalid');
  if (!Number.isInteger(output.shutdownTimeoutMs) || output.shutdownTimeoutMs < 1000 || output.shutdownTimeoutMs > 120000) throw new Error('--shutdown-timeout-ms is invalid');
  return output;
}

function loopback(host) {
  return host === 'localhost' || host === '127.0.0.1' || host === '::1';
}

export function validateNetworkBoundary(args, config, authState = null) {
  if (isIP(args.host) === 0 && args.host !== 'localhost') throw new Error('--host must be an IP address or localhost');
  if (!loopback(args.host) && !args.allowNetwork) throw new Error('non-loopback hosting requires --allow-network');
  if (!loopback(args.host) && config.session.secure !== true) throw new Error('non-loopback hosting requires secure session cookies');
  if (!loopback(args.host)) {
    const info = authStateInfo(authState);
    if (!info.durable || !info.multi_instance) throw new Error('non-loopback hosting requires durable multi-instance auth state');
  }
}

async function loadJson(path, label) {
  const raw = await readFile(resolve(path));
  return parseStrictJson(raw, label);
}

export function gracefulShutdown({ server, authState, audit, signal = 'SIGTERM', timeoutMs = 10000 }) {
  if (server.__principiaAtlasShutdown) return server.__principiaAtlasShutdown;
  server.__principiaAtlasShutdown = new Promise((resolveShutdown) => {
    let finished = false;
    let timer = null;
    const finish = (forced) => {
      if (finished) return;
      finished = true;
      if (timer) clearTimeout(timer);
      try { authState.close(); } catch {}
      try { audit.event('server.stop', { forced, signal }); } catch {}
      try { audit.close(); } catch {}
      resolveShutdown({ forced, signal });
    };
    try { audit.event('server.drain', { signal, timeout_ms: timeoutMs }); } catch {}
    server.close(() => finish(false));
    server.closeIdleConnections?.();
    timer = setTimeout(() => {
      try { audit.event('server.drain_timeout', { signal, timeout_ms: timeoutMs }); } catch {}
      server.closeAllConnections?.();
      finish(true);
    }, timeoutMs);
    timer.unref?.();
  });
  return server.__principiaAtlasShutdown;
}

export async function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  const verified = verifyTenantCatalogCompatibility(
    await loadJson(args.catalog, 'hosted catalog'),
    await loadJson(args.tenants, 'tenant config'),
  );
  const store = await loadHostedStore(args.store, verified.catalog);
  const identitySecret = readSecretFile(args.identitySecretFile, 'identity secret');
  const sessionSecret = readSecretFile(args.sessionSecretFile, 'session secret');
  const metricsToken = args.metricsTokenFile ? readSecretFile(args.metricsTokenFile, 'metrics token', { minBytes: 24 }) : null;
  if (identitySecret.equals(sessionSecret)) throw new Error('identity and session secrets must be distinct');
  const audit = createAuditLogger({ path: args.auditLog ?? null, instanceId: args.instanceId });
  const metrics = createMetricsRegistry();
  const authState = openSqliteAuthState(args.state);
  let server;
  try {
    validateNetworkBoundary(args, verified.config, authState);
    authState.health();
    metrics.setReady(true);
    server = createControlPlaneServer({
      catalog: verified.catalog,
      config: verified.config,
      store,
      authState,
      identitySecret,
      sessionSecret,
      metricsToken,
      audit,
      metrics,
    });
    identitySecret.fill(0);
    sessionSecret.fill(0);
    metricsToken?.fill(0);
    await new Promise((resolveListen, reject) => {
      server.once('error', reject);
      server.listen(args.port, args.host, resolveListen);
    });
  } catch (error) {
    identitySecret.fill(0);
    sessionSecret.fill(0);
    metricsToken?.fill(0);
    try { authState.close(); } catch {}
    try { audit.event('server.start_fail', { reason: 'initialization' }); } catch {}
    try { audit.close(); } catch {}
    throw error;
  }
  const address = server.address();
  const actualPort = typeof address === 'object' && address ? address.port : args.port;
  const stateInfo = authStateInfo(authState);
  audit.event('server.start', {
    host: args.host,
    port: actualPort,
    release_count: store.releases.size,
    state_backend: stateInfo.kind,
  });
  console.log(`Principia & Atlas hosted control plane: http://${args.host}:${actualPort}/`);
  console.log(`Hosted store: ${store.manifest.store_id}`);
  console.log(`Auth state: ${stateInfo.kind} durable=${stateInfo.durable} multi-instance=${stateInfo.multi_instance}`);
  console.log(`Metrics: ${metricsToken ? 'protected /metrics' : 'disabled'}`);
  console.log('Release serving: authenticated immutable content store');
  let signalCount = 0;
  const stop = (signal) => {
    signalCount += 1;
    if (signalCount > 1) server.closeAllConnections?.();
    gracefulShutdown({ server, authState, audit, signal, timeoutMs: args.shutdownTimeoutMs })
      .then(() => { process.exitCode = 0; });
  };
  process.once('SIGINT', () => stop('SIGINT'));
  process.once('SIGTERM', () => stop('SIGTERM'));
  server.principiaAtlasRuntime = Object.freeze({ args, authState, audit, metrics });
  return server;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => { console.error(error.message); process.exitCode = 1; });
}
