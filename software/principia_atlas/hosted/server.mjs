#!/usr/bin/env node
import { readFile } from 'node:fs/promises';
import { isIP } from 'node:net';
import { resolve } from 'node:path';
import { verifyTenantCatalogCompatibility } from './catalog.mjs';
import { createControlPlaneServer } from './control_plane.mjs';
import { authStateInfo, openSqliteAuthState } from './state.mjs';
import { loadHostedStore } from './store.mjs';
import { parseStrictJson } from './strict_json.mjs';

function parseArgs(argv) {
  const output = { host: '127.0.0.1', port: 8080, allowNetwork: false };
  for (let index = 0; index < argv.length; index += 1) {
    const item = argv[index];
    if (item === '--allow-network') output.allowNetwork = true;
    else if (['--catalog', '--tenants', '--store', '--state', '--host', '--port'].includes(item)) {
      const value = argv[++index];
      if (!value) throw new Error(`${item} requires a value`);
      output[item.slice(2)] = value;
    } else throw new Error(`unknown argument: ${item}`);
  }
  if (!output.catalog || !output.tenants || !output.store || !output.state) throw new Error('--catalog, --tenants, --store, and --state are required');
  output.port = Number(output.port);
  if (!Number.isInteger(output.port) || output.port < 0 || output.port > 65535) throw new Error('--port is invalid');
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

export async function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  const verified = verifyTenantCatalogCompatibility(
    await loadJson(args.catalog, 'hosted catalog'),
    await loadJson(args.tenants, 'tenant config'),
  );
  const store = await loadHostedStore(args.store, verified.catalog);
  const identitySecret = process.env.PRINCIPIA_ATLAS_IDENTITY_SECRET;
  const sessionSecret = process.env.PRINCIPIA_ATLAS_SESSION_SECRET;
  if (!identitySecret || !sessionSecret) throw new Error('identity and session secrets are required');
  if (identitySecret === sessionSecret) throw new Error('identity and session secrets must be distinct');
  const authState = openSqliteAuthState(args.state);
  let server;
  try {
    validateNetworkBoundary(args, verified.config, authState);
    server = createControlPlaneServer({ catalog: verified.catalog, config: verified.config, store, authState, identitySecret, sessionSecret });
    await new Promise((resolveListen, reject) => {
      server.once('error', reject);
      server.listen(args.port, args.host, resolveListen);
    });
  } catch (error) {
    authState.close();
    throw error;
  }
  const address = server.address();
  const actualPort = typeof address === 'object' && address ? address.port : args.port;
  const stateInfo = authStateInfo(authState);
  console.log(`Principia & Atlas hosted control plane: http://${args.host}:${actualPort}/`);
  console.log(`Hosted store: ${store.manifest.store_id}`);
  console.log(`Auth state: ${stateInfo.kind} durable=${stateInfo.durable} multi-instance=${stateInfo.multi_instance}`);
  console.log('Release serving: authenticated immutable content store');
  let stopping = false;
  const stop = () => {
    if (stopping) return;
    stopping = true;
    server.close(() => {
      authState.close();
      process.exitCode = 0;
    });
  };
  process.once('SIGINT', stop);
  process.once('SIGTERM', stop);
  return server;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => { console.error(error.message); process.exitCode = 1; });
}
