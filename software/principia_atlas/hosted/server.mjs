#!/usr/bin/env node
import { readFile } from 'node:fs/promises';
import { isIP } from 'node:net';
import { resolve } from 'node:path';
import { createControlPlaneServer } from './control_plane.mjs';
import { verifyCatalog, verifyTenantConfig } from './catalog.mjs';
import { parseStrictJson } from './strict_json.mjs';

function parseArgs(argv) {
  const output = { host: '127.0.0.1', port: 8080, allowNetwork: false };
  for (let index = 0; index < argv.length; index += 1) {
    const item = argv[index];
    if (item === '--allow-network') output.allowNetwork = true;
    else if (['--catalog', '--tenants', '--host', '--port'].includes(item)) {
      const value = argv[++index];
      if (!value) throw new Error(`${item} requires a value`);
      output[item.slice(2)] = value;
    } else throw new Error(`unknown argument: ${item}`);
  }
  if (!output.catalog || !output.tenants) throw new Error('--catalog and --tenants are required');
  output.port = Number(output.port);
  if (!Number.isInteger(output.port) || output.port < 0 || output.port > 65535) throw new Error('--port is invalid');
  return output;
}

function loopback(host) {
  return host === 'localhost' || host === '127.0.0.1' || host === '::1';
}

export function validateNetworkBoundary(args, config) {
  if (isIP(args.host) === 0 && args.host !== 'localhost') throw new Error('--host must be an IP address or localhost');
  if (!loopback(args.host) && !args.allowNetwork) throw new Error('non-loopback hosting requires --allow-network');
  if (!loopback(args.host) && config.session.secure !== true) throw new Error('non-loopback hosting requires secure session cookies');
}

async function loadJson(path, label) {
  const raw = await readFile(resolve(path));
  return parseStrictJson(raw, label);
}

export async function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  const catalog = verifyCatalog(await loadJson(args.catalog, 'hosted catalog'));
  const config = verifyTenantConfig(await loadJson(args.tenants, 'tenant config'));
  validateNetworkBoundary(args, config);
  const identitySecret = process.env.PRINCIPIA_ATLAS_IDENTITY_SECRET;
  const sessionSecret = process.env.PRINCIPIA_ATLAS_SESSION_SECRET;
  if (!identitySecret || !sessionSecret) throw new Error('identity and session secrets are required');
  if (identitySecret === sessionSecret) throw new Error('identity and session secrets must be distinct');
  const server = createControlPlaneServer({ catalog, config, identitySecret, sessionSecret });
  await new Promise((resolveListen, reject) => {
    server.once('error', reject);
    server.listen(args.port, args.host, resolveListen);
  });
  const address = server.address();
  const actualPort = typeof address === 'object' && address ? address.port : args.port;
  console.log(`Principia & Atlas hosted control plane: http://${args.host}:${actualPort}/`);
  console.log('Persistence: disabled');
  console.log('Release serving: disabled (catalog-only foundation)');
  const stop = () => server.close(() => process.exit(0));
  process.once('SIGINT', stop); process.once('SIGTERM', stop);
  return server;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => { console.error(error.message); process.exitCode = 1; });
}
