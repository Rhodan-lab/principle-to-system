import assert from 'node:assert/strict';
import { chmodSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { createServer as createHttpServer } from 'node:http';
import { createRequire } from 'node:module';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import { PRODUCT, TENANT_CONTRACT, sealTenantConfig } from '../principia_atlas/hosted/catalog.mjs';
import { createSaasRuntimeProcess } from '../principia_atlas/hosted/saas_process.mjs';
import { parseSaasRuntimeArgs, main as runtimeMain } from '../principia_atlas/hosted/saas_runtime_cli.mjs';
import { openSqliteAuthState } from '../principia_atlas/hosted/state.mjs';

const databaseUrl = process.env.DATABASE_URL;
const clientRoot = process.env.PG_CLIENT_ROOT;

function postgresDriver() {
  if (!clientRoot) throw new Error('PG_CLIENT_ROOT is required');
  const require = createRequire(join(clientRoot, 'package.json'));
  return require('pg');
}

async function freePort() {
  const server = createHttpServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;
  await new Promise((resolve) => server.close(resolve));
  return port;
}

function config() {
  return sealTenantConfig({
    contract: TENANT_CONTRACT,
    product: PRODUCT,
    identity: {
      issuer: 'https://identity.example.test',
      audience: 'principia-atlas-process-test',
      max_assertion_ttl_seconds: 300,
    },
    session: {
      cookie_name: 'pa_session',
      ttl_seconds: 3600,
      secure: false,
    },
    tenants: {
      'process-tenant': {
        display_name: 'Process Tenant',
        allowed_channels: ['beta'],
        allowed_routes: ['refrigerator-v1'],
        pinned_versions: [],
      },
    },
  });
}

test('SaaS process migrates before listen and aggregates readiness', { skip: !databaseUrl || !clientRoot }, async () => {
  const { Pool } = postgresDriver();
  const admin = new Pool({ connectionString: databaseUrl, max: 2 });
  await admin.query('DROP SCHEMA IF EXISTS saas_process_test CASCADE');
  await admin.query('CREATE SCHEMA saas_process_test');
  const pool = new Pool({
    connectionString: databaseUrl,
    max: 4,
    options: '-c search_path=saas_process_test',
  });
  const root = mkdtempSync(join(tmpdir(), 'principia-atlas-saas-process-'));
  const authState = openSqliteAuthState(join(root, 'auth.sqlite'));
  let coreReady = true;
  const corePort = await freePort();
  const core = createHttpServer((request, response) => {
    if (request.url === '/readyz') {
      response.statusCode = coreReady ? 200 : 503;
      response.setHeader('content-type', 'application/json');
      return response.end(coreReady ? '{"status":"ready"}' : '{"error":"not_ready"}');
    }
    response.statusCode = 404;
    response.end();
  });
  await new Promise((resolve) => core.listen(corePort, '127.0.0.1', resolve));
  const runtimePort = await freePort();
  let processHandle = null;
  try {
    processHandle = await createSaasRuntimeProcess({
      config: config(),
      authState,
      sessionSecret: Buffer.alloc(32, 61),
      csrfSecret: Buffer.alloc(32, 62),
      pool,
      coreOrigin: `http://127.0.0.1:${corePort}`,
      host: '127.0.0.1',
      port: runtimePort,
      closeAuthState: true,
      closePool: true,
    });
    assert.equal(processHandle.server.listening, false);
    const migrationCount = await pool.query('SELECT COUNT(*)::int AS count FROM principia_atlas_saas_migrations');
    assert.equal(migrationCount.rows[0].count, 2);

    await processHandle.start();
    const health = await fetch(`http://127.0.0.1:${runtimePort}/saas/healthz`);
    assert.equal(health.status, 200);
    assert.equal((await health.json()).status, 'ok');

    const ready = await fetch(`http://127.0.0.1:${runtimePort}/saas/readyz`);
    assert.equal(ready.status, 200);
    assert.equal((await ready.json()).status, 'ready');

    coreReady = false;
    const unavailable = await fetch(`http://127.0.0.1:${runtimePort}/saas/readyz`);
    assert.equal(unavailable.status, 503);
    assert.deepEqual(await unavailable.json(), { error: 'not_ready' });
    const stillAlive = await fetch(`http://127.0.0.1:${runtimePort}/saas/healthz`);
    assert.equal(stillAlive.status, 200);

    const stopped = await processHandle.stop();
    assert.equal(typeof stopped.forced, 'boolean');
    await assert.rejects(() => pool.query('SELECT 1'), /ended|closed/i);
    assert.throws(() => authState.health(), /closed/);
  } finally {
    if (processHandle) {
      try { await processHandle.stop(); } catch {}
    } else {
      try { authState.close(); } catch {}
      try { await pool.end(); } catch {}
    }
    await new Promise((resolve) => core.close(resolve));
    await admin.query('DROP SCHEMA IF EXISTS saas_process_test CASCADE');
    await admin.end();
    rmSync(root, { recursive: true, force: true });
  }
});

test('SaaS startup accepts only secret-file database URLs with verified TLS', async () => {
  assert.throws(() => parseSaasRuntimeArgs(['--database-url', 'postgres://secret']), /unknown/);
  const root = mkdtempSync(join(tmpdir(), 'principia-atlas-saas-cli-'));
  try {
    const tenantPath = join(root, 'tenants.json');
    const sessionPath = join(root, 'session');
    const csrfPath = join(root, 'csrf');
    const databasePath = join(root, 'database-url');
    const driverPath = join(root, 'driver.mjs');
    writeFileSync(tenantPath, JSON.stringify(config()), { mode: 0o400 });
    writeFileSync(sessionPath, 's'.repeat(32), { mode: 0o400 });
    writeFileSync(csrfPath, 'c'.repeat(32), { mode: 0o400 });
    writeFileSync(databasePath, 'postgres://user:password@db.internal/app', { mode: 0o400 });
    writeFileSync(driverPath, 'export async function createPostgresPool(){ throw new Error("driver must not load"); }\n', { mode: 0o400 });
    for (const path of [tenantPath, sessionPath, csrfPath, databasePath, driverPath]) chmodSync(path, 0o400);
    await assert.rejects(() => runtimeMain([
      '--tenants', tenantPath,
      '--state', join(root, 'auth.sqlite'),
      '--session-secret-file', sessionPath,
      '--csrf-secret-file', csrfPath,
      '--database-url-file', databasePath,
      '--postgres-driver-module', driverPath,
      '--core-origin', 'http://127.0.0.1:8080',
    ]), /sslmode=verify-full/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
