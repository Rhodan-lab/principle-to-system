#!/usr/bin/env node
import { lstat, open, readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import { createBrowserOidcEdgeServer, validateBrowserEdgeNetwork, verifyBrowserEdgeUpstream } from './browser_edge.mjs';
import { sealBrowserOidcConfig, verifyBrowserOidcConfig } from './browser_oidc.mjs';
import { readSecretFile } from './secrets.mjs';
import { canonicalJson, parseStrictJson } from './strict_json.mjs';

const MAX_CONFIG_BYTES = 256 * 1024;

function parseArgs(argv) {
  const command = argv[0];
  if (!['seal', 'verify', 'serve'].includes(command)) throw new Error('expected seal, verify, or serve command');
  const output = { command, host: '127.0.0.1', port: 8081, allowNetwork: false, shutdownTimeoutMs: 10000 };
  const seen = new Set();
  for (let index = 1; index < argv.length; index += 1) {
    const item = argv[index];
    if (item === '--allow-network') {
      if (seen.has(item)) throw new Error(`${item} may only be supplied once`);
      seen.add(item); output.allowNetwork = true; continue;
    }
    if (!['--input', '--output', '--config', '--flow-secret-file', '--client-secret-file', '--upstream-origin', '--host', '--port', '--shutdown-timeout-ms'].includes(item)) {
      throw new Error(`unknown argument: ${item}`);
    }
    if (seen.has(item)) throw new Error(`${item} may only be supplied once`);
    seen.add(item);
    const value = argv[++index];
    if (!value) throw new Error(`${item} requires a value`);
    const key = item.slice(2).replaceAll(/-([a-z])/g, (_, letter) => letter.toUpperCase());
    output[key] = value;
  }
  if (command === 'seal' && (!output.input || !output.output)) throw new Error('seal requires --input and --output');
  if (command === 'verify' && !output.config) throw new Error('verify requires --config');
  if (command === 'serve' && (!output.config || !output.flowSecretFile || !output.upstreamOrigin)) {
    throw new Error('serve requires --config, --flow-secret-file, and --upstream-origin');
  }
  output.port = Number(output.port);
  output.shutdownTimeoutMs = Number(output.shutdownTimeoutMs);
  if (!Number.isInteger(output.port) || output.port < 1 || output.port > 65535) throw new Error('--port is invalid');
  if (!Number.isInteger(output.shutdownTimeoutMs) || output.shutdownTimeoutMs < 1000 || output.shutdownTimeoutMs > 120000) throw new Error('--shutdown-timeout-ms is invalid');
  return output;
}

async function readRegular(pathInput, label) {
  const path = resolve(pathInput);
  const stats = await lstat(path);
  if (stats.isSymbolicLink() || !stats.isFile()) throw new Error(`${label} must be a regular file`);
  if (stats.size > MAX_CONFIG_BYTES) throw new Error(`${label} exceeds resource limit`);
  return readFile(path);
}

async function loadConfig(path, label = 'browser OIDC config') {
  return verifyBrowserOidcConfig(parseStrictJson(await readRegular(path, label), label));
}

async function writeExclusive(pathInput, raw) {
  const path = resolve(pathInput);
  const handle = await open(path, 'wx', 0o600);
  try {
    await handle.writeFile(raw, 'utf8');
    await handle.sync();
  } catch (error) {
    try { await handle.close(); } catch {}
    throw error;
  }
  await handle.close();
}

function installShutdown(server, timeoutMs) {
  let stopping = null;
  const stop = (signal) => {
    if (stopping) {
      server.closeAllConnections?.();
      return stopping;
    }
    stopping = new Promise((resolveStop) => {
      const timer = setTimeout(() => {
        server.closeAllConnections?.();
        resolveStop({ signal, forced: true });
      }, timeoutMs);
      timer.unref?.();
      server.close(() => {
        clearTimeout(timer);
        resolveStop({ signal, forced: false });
      });
      server.closeIdleConnections?.();
    });
    stopping.then(() => { process.exitCode = 0; });
    return stopping;
  };
  process.once('SIGINT', () => stop('SIGINT'));
  process.once('SIGTERM', () => stop('SIGTERM'));
  return stop;
}

export async function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  if (args.command === 'seal') {
    const unsigned = parseStrictJson(await readRegular(args.input, 'unsigned browser OIDC config'), 'unsigned browser OIDC config');
    const sealed = sealBrowserOidcConfig(unsigned);
    await writeExclusive(args.output, canonicalJson(sealed));
    console.log(`Sealed browser OIDC config: ${sealed.config_id}`);
    return sealed;
  }
  if (args.command === 'verify') {
    const config = await loadConfig(args.config);
    console.log(`Verified browser OIDC config: ${config.config_id}`);
    return config;
  }

  const config = await loadConfig(args.config);
  const upstreamOrigin = verifyBrowserEdgeUpstream(args.upstreamOrigin);
  validateBrowserEdgeNetwork({ host: args.host, allowNetwork: args.allowNetwork, publicOrigin: config.public_origin });
  const flowSecret = readSecretFile(args.flowSecretFile, 'browser OIDC flow secret');
  let clientSecret = null;
  let server = null;
  try {
    if (config.client_auth_method === 'client_secret_post') {
      if (!args.clientSecretFile) throw new Error('confidential browser OIDC client requires --client-secret-file');
      clientSecret = readSecretFile(args.clientSecretFile, 'browser OIDC client secret');
    } else if (args.clientSecretFile) {
      throw new Error('public browser OIDC client must not receive --client-secret-file');
    }
    server = createBrowserOidcEdgeServer({ config, flowSecret, clientSecret, upstreamOrigin });
    flowSecret.fill(0); clientSecret?.fill(0);
    await new Promise((resolveListen, reject) => {
      server.once('error', reject);
      server.listen(args.port, args.host, resolveListen);
    });
    installShutdown(server, args.shutdownTimeoutMs);
    console.log(`Principia & Atlas browser OIDC edge: ${config.public_origin}`);
    console.log(`Login route: ${config.login_path}`);
    console.log(`Upstream: ${upstreamOrigin}`);
    console.log(`Config: ${config.config_id}`);
    return server;
  } catch (error) {
    flowSecret.fill(0); clientSecret?.fill(0);
    try { server?.close(); } catch {}
    throw error;
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => { console.error(error.message); process.exitCode = 1; });
}
