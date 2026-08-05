import { isIP } from 'node:net';

import { createSaasApplicationApi } from '../saas/application_api.mjs';
import { applyPostgresMigrations } from '../saas/postgres_migrations.mjs';
import { openPostgresSaasControlPlane } from '../saas/postgres_store.mjs';
import {
  createSaasHostedRuntimeServer,
  SAAS_HOSTED_RUNTIME_CONTRACT,
  SAAS_RUNTIME_HEALTH_PATH,
  SAAS_RUNTIME_READY_PATH,
} from './saas_runtime.mjs';
import { fail } from './strict_json.mjs';

export const SAAS_PROCESS_CONTRACT = 'principia-atlas-saas-process/0.1';
const LOOPBACK = new Set(['localhost', '127.0.0.1', '::1']);
const INTERNAL_PATHS = new Set([SAAS_RUNTIME_HEALTH_PATH, SAAS_RUNTIME_READY_PATH]);

function validatePool(pool) {
  if (!pool || typeof pool.connect !== 'function' || typeof pool.query !== 'function' || typeof pool.end !== 'function') {
    fail('SaaS PostgreSQL pool is invalid');
  }
  return pool;
}

function validateAuthState(value) {
  if (!value || typeof value.validateSession !== 'function' || typeof value.health !== 'function' || typeof value.close !== 'function') {
    fail('SaaS process auth state is invalid');
  }
  return value;
}

function validateHost(value) {
  if (typeof value !== 'string' || (isIP(value) === 0 && value !== 'localhost') || !LOOPBACK.has(value)) {
    fail('SaaS process host must be loopback');
  }
  return value;
}

function boundedInteger(value, label, minimum, maximum) {
  if (!Number.isSafeInteger(value) || value < minimum || value > maximum) fail(`${label} is invalid`);
  return value;
}

function hideInternalPathsFromProxy(server) {
  const listeners = server.listeners('request');
  if (listeners.length !== 1) fail('SaaS runtime request boundary is invalid');
  const runtimeHandler = listeners[0];
  server.removeAllListeners('request');
  server.on('request', (request, response) => {
    let pathname = null;
    try { pathname = new URL(request.url ?? '/', 'http://localhost').pathname; } catch {}
    if (pathname && INTERNAL_PATHS.has(pathname) && request.headers.origin !== undefined) {
      const raw = Buffer.from('{"error":"not_found"}\n', 'utf8');
      response.statusCode = 404;
      response.setHeader('Content-Type', 'application/json; charset=utf-8');
      response.setHeader('Content-Length', String(raw.length));
      response.setHeader('Cache-Control', 'private, no-store');
      response.setHeader('X-Content-Type-Options', 'nosniff');
      response.end(raw);
      return;
    }
    runtimeHandler(request, response);
  });
}

async function closeServer(server, timeoutMs) {
  if (!server.listening) return Object.freeze({ forced: false });
  return new Promise((resolve) => {
    let settled = false;
    const finish = (forced) => {
      if (settled) return;
      settled = true;
      resolve(Object.freeze({ forced }));
    };
    const timer = setTimeout(() => {
      server.closeAllConnections?.();
      finish(true);
    }, timeoutMs);
    timer.unref?.();
    server.close(() => {
      clearTimeout(timer);
      finish(false);
    });
    server.closeIdleConnections?.();
  });
}

function closeSyncResource(operation, errors) {
  try { operation(); } catch (error) { errors.push(error); }
}

async function closeAsyncResource(operation, errors) {
  try { await operation(); } catch (error) { errors.push(error); }
}

export async function createSaasRuntimeProcess({
  config,
  authState: authStateInput,
  sessionSecret,
  csrfSecret,
  pool: poolInput,
  coreOrigin,
  host = '127.0.0.1',
  port = 8082,
  timeoutMs = 10000,
  shutdownTimeoutMs = 20000,
  maxTransactionAttempts = 3,
  closeAuthState = false,
  closePool = false,
  fetchImpl = globalThis.fetch,
  now = () => Math.floor(Date.now() / 1000),
} = {}) {
  const authState = validateAuthState(authStateInput);
  const pool = validatePool(poolInput);
  const bindHost = validateHost(host);
  boundedInteger(port, 'SaaS process port', 1, 65535);
  boundedInteger(timeoutMs, 'SaaS process upstream timeout', 500, 30000);
  boundedInteger(shutdownTimeoutMs, 'SaaS process shutdown timeout', 1000, 120000);
  boundedInteger(maxTransactionAttempts, 'SaaS process transaction attempts', 1, 10);
  if (typeof closeAuthState !== 'boolean' || typeof closePool !== 'boolean') fail('SaaS process ownership flags are invalid');

  let controlPlane = null;
  let applicationApi = null;
  let server = null;
  let started = false;
  let stopped = false;
  let stopPromise = null;
  try {
    await applyPostgresMigrations(pool);
    controlPlane = openPostgresSaasControlPlane(pool, { maxTransactionAttempts });
    applicationApi = createSaasApplicationApi({ controlPlane, csrfSecret });
    server = createSaasHostedRuntimeServer({
      config,
      authState,
      sessionSecret,
      applicationApi,
      readiness: () => controlPlane.health(),
      coreOrigin,
      fetchImpl,
      now,
      timeoutMs,
    });
    hideInternalPathsFromProxy(server);
  } catch (error) {
    const errors = [];
    if (applicationApi) closeSyncResource(() => applicationApi.close(), errors);
    if (controlPlane) closeSyncResource(() => controlPlane.close(), errors);
    if (closePool) await closeAsyncResource(() => pool.end(), errors);
    if (closeAuthState) closeSyncResource(() => authState.close(), errors);
    throw error;
  }

  const processHandle = {
    descriptor: Object.freeze({
      contract: SAAS_PROCESS_CONTRACT,
      runtime_contract: SAAS_HOSTED_RUNTIME_CONTRACT,
      host: bindHost,
      port,
      database: 'postgresql',
      auth_state: authState.descriptor?.kind ?? 'unknown',
      health_path: SAAS_RUNTIME_HEALTH_PATH,
      readiness_path: SAAS_RUNTIME_READY_PATH,
      production_ready: false,
    }),
    get server() { return server; },
    async start() {
      if (stopped) fail('SaaS process is stopped');
      if (started) return processHandle;
      await new Promise((resolve, reject) => {
        const onError = (error) => { server.off('listening', onListen); reject(error); };
        const onListen = () => { server.off('error', onError); resolve(); };
        server.once('error', onError);
        server.once('listening', onListen);
        server.listen(port, bindHost);
      });
      started = true;
      return processHandle;
    },
    async stop() {
      if (stopPromise) return stopPromise;
      stopped = true;
      stopPromise = (async () => {
        const errors = [];
        let result = Object.freeze({ forced: false });
        await closeAsyncResource(async () => { result = await closeServer(server, shutdownTimeoutMs); }, errors);
        closeSyncResource(() => applicationApi.close(), errors);
        closeSyncResource(() => controlPlane.close(), errors);
        if (closePool) await closeAsyncResource(() => pool.end(), errors);
        if (closeAuthState) closeSyncResource(() => authState.close(), errors);
        if (errors.length) throw errors[0];
        return result;
      })();
      return stopPromise;
    },
  };
  return Object.freeze(processHandle);
}
