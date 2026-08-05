#!/usr/bin/env node
import { lstat, readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

import { verifyTenantConfig } from './catalog.mjs';
import { readSecretFile } from './secrets.mjs';
import { createSaasRuntimeProcess } from './saas_process.mjs';
import { openSqliteAuthState } from './state.mjs';
import { fail, parseStrictJson } from './strict_json.mjs';

const MAX_CONFIG_BYTES = 256 * 1024;
const MAX_CA_BYTES = 1024 * 1024;
const ALLOWED_FLAGS = new Set([
  '--tenants', '--state', '--session-secret-file', '--csrf-secret-file', '--database-url-file',
  '--postgres-driver-module', '--postgres-ca-file', '--core-origin', '--host', '--port',
  '--pool-max', '--connection-timeout-ms', '--idle-timeout-ms', '--upstream-timeout-ms',
  '--shutdown-timeout-ms', '--transaction-attempts',
]);

function number(value, label, minimum, maximum) {
  const output = Number(value);
  if (!Number.isInteger(output) || output < minimum || output > maximum) fail(`${label} is invalid`);
  return output;
}

export function parseSaasRuntimeArgs(argv) {
  const output = {
    host: '127.0.0.1',
    port: 8082,
    poolMax: 10,
    connectionTimeoutMs: 5000,
    idleTimeoutMs: 30000,
    upstreamTimeoutMs: 10000,
    shutdownTimeoutMs: 20000,
    transactionAttempts: 3,
  };
  const seen = new Set();
  for (let index = 0; index < argv.length; index += 1) {
    const flag = argv[index];
    if (!ALLOWED_FLAGS.has(flag) || seen.has(flag)) fail(`unknown or duplicate argument: ${flag}`);
    seen.add(flag);
    const value = argv[++index];
    if (!value) fail(`${flag} requires a value`);
    const key = flag.slice(2).replaceAll(/-([a-z])/g, (_, letter) => letter.toUpperCase());
    output[key] = value;
  }
  for (const required of [
    'tenants', 'state', 'sessionSecretFile', 'csrfSecretFile', 'databaseUrlFile',
    'postgresDriverModule', 'coreOrigin',
  ]) if (!output[required]) fail(`--${required.replaceAll(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)} is required`);
  output.port = number(output.port, '--port', 1, 65535);
  output.poolMax = number(output.poolMax, '--pool-max', 1, 50);
  output.connectionTimeoutMs = number(output.connectionTimeoutMs, '--connection-timeout-ms', 500, 30000);
  output.idleTimeoutMs = number(output.idleTimeoutMs, '--idle-timeout-ms', 1000, 300000);
  output.upstreamTimeoutMs = number(output.upstreamTimeoutMs, '--upstream-timeout-ms', 500, 30000);
  output.shutdownTimeoutMs = number(output.shutdownTimeoutMs, '--shutdown-timeout-ms', 1000, 120000);
  output.transactionAttempts = number(output.transactionAttempts, '--transaction-attempts', 1, 10);
  return Object.freeze(output);
}

async function readRegular(pathInput, label, maximum, { immutableCode = false } = {}) {
  const path = resolve(pathInput);
  const stats = await lstat(path);
  if (stats.isSymbolicLink() || !stats.isFile()) fail(`${label} must be a regular file`);
  if (stats.size < 1 || stats.size > maximum) fail(`${label} exceeds resource limit`);
  if (immutableCode && (stats.mode & 0o022) !== 0) fail(`${label} permissions are too broad`);
  return Object.freeze({ path, raw: await readFile(path) });
}

async function loadTenantConfig(pathInput) {
  const input = await readRegular(pathInput, 'SaaS tenant config', MAX_CONFIG_BYTES);
  return verifyTenantConfig(parseStrictJson(input.raw, 'SaaS tenant config'));
}

function validateDatabaseUrl(raw) {
  const value = raw.toString('utf8');
  let parsed;
  try { parsed = new URL(value); } catch { fail('PostgreSQL database URL is invalid'); }
  if (!['postgres:', 'postgresql:'].includes(parsed.protocol)
    || !parsed.hostname || parsed.pathname.length < 2 || parsed.hash) {
    fail('PostgreSQL database URL is invalid');
  }
  const sslModes = parsed.searchParams.getAll('sslmode');
  if (sslModes.length !== 1 || sslModes[0] !== 'verify-full') {
    fail('PostgreSQL database URL must use sslmode=verify-full');
  }
  return value;
}

async function loadDriver(pathInput) {
  const input = await readRegular(pathInput, 'PostgreSQL driver module', MAX_CONFIG_BYTES, { immutableCode: true });
  const module = await import(`${pathToFileURL(input.path).href}?v=${input.raw.byteLength}`);
  if (typeof module.createPostgresPool !== 'function') fail('PostgreSQL driver module is invalid');
  return module.createPostgresPool;
}

function installShutdown(handle) {
  let stopping = false;
  const stop = async () => {
    if (stopping) {
      handle.server.closeAllConnections?.();
      return;
    }
    stopping = true;
    try { await handle.stop(); process.exitCode = 0; }
    catch { process.exitCode = 1; }
  };
  process.once('SIGINT', stop);
  process.once('SIGTERM', stop);
}

export async function main(argv = process.argv.slice(2)) {
  const args = parseSaasRuntimeArgs(argv);
  const config = await loadTenantConfig(args.tenants);
  const sessionSecret = readSecretFile(args.sessionSecretFile, 'hosted session secret');
  const csrfSecret = readSecretFile(args.csrfSecretFile, 'SaaS CSRF secret');
  const databaseUrlRaw = readSecretFile(args.databaseUrlFile, 'PostgreSQL database URL', { minBytes: 24, maxBytes: 4096 });
  let ca = null;
  let authState = null;
  let pool = null;
  let handle = null;
  try {
    if (args.postgresCaFile) {
      const caInput = await readRegular(args.postgresCaFile, 'PostgreSQL CA bundle', MAX_CA_BYTES);
      const caText = caInput.raw.toString('utf8');
      if (!caText.includes('-----BEGIN CERTIFICATE-----') || !caText.includes('-----END CERTIFICATE-----')) {
        fail('PostgreSQL CA bundle is invalid');
      }
      ca = Buffer.from(caInput.raw);
    }
    const connectionString = validateDatabaseUrl(databaseUrlRaw);
    const createPool = await loadDriver(args.postgresDriverModule);
    pool = await createPool(Object.freeze({
      connectionString,
      max: args.poolMax,
      connectionTimeoutMillis: args.connectionTimeoutMs,
      idleTimeoutMillis: args.idleTimeoutMs,
      ssl: Object.freeze({
        rejectUnauthorized: true,
        ...(ca ? { ca: ca.toString('utf8') } : {}),
      }),
    }));
    authState = openSqliteAuthState(args.state);
    handle = await createSaasRuntimeProcess({
      config,
      authState,
      sessionSecret,
      csrfSecret,
      pool,
      coreOrigin: args.coreOrigin,
      host: args.host,
      port: args.port,
      timeoutMs: args.upstreamTimeoutMs,
      shutdownTimeoutMs: args.shutdownTimeoutMs,
      maxTransactionAttempts: args.transactionAttempts,
      closeAuthState: true,
      closePool: true,
    });
    sessionSecret.fill(0);
    csrfSecret.fill(0);
    databaseUrlRaw.fill(0);
    ca?.fill(0);
    await handle.start();
    installShutdown(handle);
    console.log(`Principia & Atlas SaaS runtime: http://${args.host}:${args.port}`);
    console.log(`Core upstream: ${args.coreOrigin}`);
    console.log(`Tenant config: ${config.config_id}`);
    return handle;
  } catch (error) {
    sessionSecret.fill(0);
    csrfSecret.fill(0);
    databaseUrlRaw.fill(0);
    ca?.fill(0);
    if (handle) {
      try { await handle.stop(); } catch {}
    } else {
      try { authState?.close(); } catch {}
      try { await pool?.end(); } catch {}
    }
    throw error;
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => { console.error(error.message); process.exitCode = 1; });
}
