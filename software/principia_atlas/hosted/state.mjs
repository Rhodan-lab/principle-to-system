import { chmodSync, lstatSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { canonicalJson, fail } from './strict_json.mjs';

export const AUTH_STATE_CONTRACT = 'principia-atlas-hosted-auth-state/0.1';
const ASSERTION_ID = /^[A-Za-z0-9_-]{16,128}$/;
const SESSION_ID = /^[A-Za-z0-9_-]{24,128}$/;
const SUBJECT = /^[A-Za-z0-9._:@+-]{1,200}$/;
const TENANT_ID = /^[a-z][a-z0-9-]{1,62}$/;
const REVOCATION_EVENT_ID = /^[A-Za-z0-9._:@+-]{16,200}$/;
const MAX_SCOPE_BYTES = 512;
const MAX_REVOCATION_RECEIPT_TTL_SECONDS = 365 * 24 * 60 * 60;

function integer(value, label, minimum = 0) {
  if (!Number.isSafeInteger(value) || value < minimum) fail(`${label} is invalid`);
  return value;
}

function identifier(value, pattern, label) {
  if (typeof value !== 'string' || !pattern.test(value)) fail(`${label} is invalid`);
  return value;
}

function validateSessionRecord(session, nowSeconds) {
  if (!session || typeof session !== 'object' || Array.isArray(session)) fail('session record is invalid');
  identifier(session.sid, SESSION_ID, 'session identifier');
  identifier(session.jti, ASSERTION_ID, 'session assertion identifier');
  identifier(session.sub, SUBJECT, 'session subject');
  identifier(session.tenant_id, TENANT_ID, 'session tenant');
  if (!Array.isArray(session.roles) || session.roles.length === 0 || session.roles.some((item) => typeof item !== 'string')) fail('session roles are invalid');
  integer(session.iat, 'session issued time');
  integer(session.exp, 'session expiry');
  integer(nowSeconds, 'current time');
  if (session.exp <= session.iat || session.exp <= nowSeconds) fail('session record is expired');
  return {
    sid: session.sid,
    assertionId: session.jti,
    subject: session.sub,
    tenantId: session.tenant_id,
    rolesJson: canonicalJson([...session.roles]),
    issuedAt: session.iat,
    expiresAt: session.exp,
  };
}

function validateExchange(input, nowSeconds) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) fail('auth exchange state is invalid');
  identifier(input.assertionId, ASSERTION_ID, 'assertion identifier');
  integer(input.assertionExpiresAt, 'assertion expiry');
  if (input.assertionExpiresAt <= nowSeconds) fail('assertion is expired');
  const session = validateSessionRecord(input.session, nowSeconds);
  if (session.assertionId !== input.assertionId) fail('session assertion identity is invalid');
  return { assertionId: input.assertionId, assertionExpiresAt: input.assertionExpiresAt, session };
}

function validateRevocationReceipt(eventId, tenantId, subject, nowSeconds, receiptExpiresAt) {
  identifier(eventId, REVOCATION_EVENT_ID, 'revocation event identifier');
  identifier(tenantId, TENANT_ID, 'session tenant');
  identifier(subject, SUBJECT, 'session subject');
  integer(nowSeconds, 'current time');
  integer(receiptExpiresAt, 'revocation receipt expiry');
  if (receiptExpiresAt <= nowSeconds || receiptExpiresAt - nowSeconds > MAX_REVOCATION_RECEIPT_TTL_SECONDS) fail('revocation receipt TTL is invalid');
  return { eventId, tenantId, subject, nowSeconds, receiptExpiresAt };
}

function revocationReceipt(value, replayed) {
  return Object.freeze({
    event_id: value.eventId,
    replayed,
    revoked_sessions: value.revokedSessions,
    created_at: value.createdAt,
    expires_at: value.expiresAt,
  });
}

function validateRate(scope, windowStart, windowSeconds, limit, nowSeconds) {
  if (typeof scope !== 'string' || scope.length === 0 || Buffer.byteLength(scope) > MAX_SCOPE_BYTES || /[\u0000-\u001f\u007f]/.test(scope)) fail('rate-limit scope is invalid');
  integer(windowStart, 'rate-limit window');
  integer(windowSeconds, 'rate-limit duration', 1);
  integer(limit, 'rate-limit threshold', 1);
  integer(nowSeconds, 'current time');
  if (windowStart > nowSeconds || nowSeconds >= windowStart + windowSeconds) fail('rate-limit window is inactive');
  return { scope, windowStart, limit, expiresAt: windowStart + windowSeconds };
}

function descriptor(kind, durable, multiInstance) {
  return Object.freeze({ contract: AUTH_STATE_CONTRACT, kind, durable, multi_instance: multiInstance });
}

function interfaceCheck(state) {
  const methods = ['commitExchange', 'validateSession', 'revokeSession', 'revokeSubject', 'revokeSubjectOnce', 'consumeRateLimit', 'prune', 'stats', 'health', 'close'];
  if (!state || typeof state !== 'object' || !state.descriptor) fail('auth state backend is invalid');
  for (const method of methods) if (typeof state[method] !== 'function') fail('auth state backend is invalid');
  const value = state.descriptor;
  if (value.contract !== AUTH_STATE_CONTRACT || typeof value.kind !== 'string' || typeof value.durable !== 'boolean' || typeof value.multi_instance !== 'boolean') fail('auth state descriptor is invalid');
  return state;
}

export function authStateInfo(state) {
  return interfaceCheck(state).descriptor;
}

export function createMemoryAuthState() {
  const assertions = new Map();
  const sessions = new Map();
  const revocationReceipts = new Map();
  const rates = new Map();
  let closed = false;
  const ensureOpen = () => { if (closed) fail('auth state backend is closed'); };
  const prune = (nowSeconds) => {
    ensureOpen(); integer(nowSeconds, 'current time');
    for (const [key, expiry] of assertions) if (expiry <= nowSeconds) assertions.delete(key);
    for (const [key, value] of sessions) if (value.expiresAt <= nowSeconds) sessions.delete(key);
    for (const [key, value] of revocationReceipts) if (value.expiresAt <= nowSeconds) revocationReceipts.delete(key);
    for (const [key, value] of rates) if (value.expiresAt <= nowSeconds) rates.delete(key);
  };
  const state = {
    descriptor: descriptor('memory', false, false),
    commitExchange(input, nowSeconds) {
      ensureOpen(); const value = validateExchange(input, nowSeconds); prune(nowSeconds);
      if ((assertions.get(value.assertionId) ?? 0) > nowSeconds) return false;
      if (sessions.has(value.session.sid)) fail('session identifier collision');
      assertions.set(value.assertionId, value.assertionExpiresAt);
      sessions.set(value.session.sid, { ...value.session, revokedAt: null });
      return true;
    },
    validateSession(session, nowSeconds) {
      ensureOpen(); const value = validateSessionRecord(session, nowSeconds); prune(nowSeconds);
      const stored = sessions.get(value.sid);
      return Boolean(stored && stored.revokedAt === null && stored.subject === value.subject && stored.tenantId === value.tenantId && stored.rolesJson === value.rolesJson && stored.issuedAt === value.issuedAt && stored.expiresAt === value.expiresAt && stored.assertionId === value.assertionId);
    },
    revokeSession(sid, nowSeconds) {
      ensureOpen(); identifier(sid, SESSION_ID, 'session identifier'); prune(nowSeconds);
      const stored = sessions.get(sid);
      if (!stored || stored.revokedAt !== null) return false;
      stored.revokedAt = nowSeconds;
      return true;
    },
    revokeSubject(tenantId, subject, nowSeconds) {
      ensureOpen(); identifier(tenantId, TENANT_ID, 'session tenant'); identifier(subject, SUBJECT, 'session subject'); prune(nowSeconds);
      let count = 0;
      for (const stored of sessions.values()) {
        if (stored.tenantId === tenantId && stored.subject === subject && stored.revokedAt === null) {
          stored.revokedAt = nowSeconds;
          count += 1;
        }
      }
      return count;
    },
    revokeSubjectOnce(eventId, tenantId, subject, nowSeconds, receiptExpiresAt) {
      ensureOpen();
      const value = validateRevocationReceipt(eventId, tenantId, subject, nowSeconds, receiptExpiresAt);
      prune(nowSeconds);
      const existing = revocationReceipts.get(value.eventId);
      if (existing) {
        if (existing.tenantId !== value.tenantId || existing.subject !== value.subject) fail('revocation event target mismatch');
        return revocationReceipt(existing, true);
      }
      let count = 0;
      for (const stored of sessions.values()) {
        if (stored.tenantId === value.tenantId && stored.subject === value.subject && stored.revokedAt === null) {
          stored.revokedAt = value.nowSeconds;
          count += 1;
        }
      }
      const stored = {
        eventId: value.eventId,
        tenantId: value.tenantId,
        subject: value.subject,
        revokedSessions: count,
        createdAt: value.nowSeconds,
        expiresAt: value.receiptExpiresAt,
      };
      revocationReceipts.set(value.eventId, stored);
      return revocationReceipt(stored, false);
    },
    consumeRateLimit(scope, windowStart, windowSeconds, limit, nowSeconds) {
      ensureOpen(); const value = validateRate(scope, windowStart, windowSeconds, limit, nowSeconds); prune(nowSeconds);
      const key = `${value.scope}\u0000${value.windowStart}`;
      const previous = rates.get(key);
      const count = (previous?.count ?? 0) + 1;
      rates.set(key, { count, expiresAt: value.expiresAt });
      return Object.freeze({ allowed: count <= value.limit, count, reset_at: value.expiresAt });
    },
    prune,
    stats(nowSeconds) {
      prune(nowSeconds);
      let active = 0;
      let revoked = 0;
      for (const value of sessions.values()) {
        if (value.revokedAt === null) active += 1;
        else revoked += 1;
      }
      return Object.freeze({ contract: AUTH_STATE_CONTRACT, backend: 'memory', assertions: assertions.size, active_sessions: active, revoked_sessions: revoked, rate_limit_buckets: rates.size });
    },
    health() { ensureOpen(); return Object.freeze({ status: 'ok', ...state.descriptor }); },
    close() { closed = true; assertions.clear(); sessions.clear(); revocationReceipts.clear(); rates.clear(); },
  };
  return interfaceCheck(state);
}

function sqlitePath(pathInput) {
  if (typeof pathInput !== 'string' || pathInput.length === 0 || pathInput === ':memory:') fail('auth state path is invalid');
  const path = resolve(pathInput);
  const parent = dirname(path);
  mkdirSync(parent, { recursive: true, mode: 0o700 });
  const parentStat = lstatSync(parent);
  if (parentStat.isSymbolicLink() || !parentStat.isDirectory()) fail('auth state parent must be a regular directory');
  try {
    const stats = lstatSync(path);
    if (stats.isSymbolicLink() || !stats.isFile()) fail('auth state must be a regular file');
  } catch (error) {
    if (error?.code !== 'ENOENT') throw error;
  }
  return path;
}

function transaction(database, operation) {
  database.exec('BEGIN IMMEDIATE');
  try {
    const value = operation();
    database.exec('COMMIT');
    return value;
  } catch (error) {
    try { database.exec('ROLLBACK'); } catch {}
    throw error;
  }
}

export function openSqliteAuthState(pathInput, { busyTimeoutMs = 5000 } = {}) {
  integer(busyTimeoutMs, 'SQLite busy timeout', 1);
  const path = sqlitePath(pathInput);
  const database = new DatabaseSync(path);
  let closed = false;
  const ensureOpen = () => { if (closed) fail('auth state backend is closed'); };
  try {
    database.exec(`PRAGMA busy_timeout=${busyTimeoutMs}; PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA foreign_keys=ON; PRAGMA trusted_schema=OFF;`);
    database.exec(`
      CREATE TABLE IF NOT EXISTS state_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL) STRICT;
      CREATE TABLE IF NOT EXISTS used_assertions (jti TEXT PRIMARY KEY, claimed_at INTEGER NOT NULL, expires_at INTEGER NOT NULL) STRICT;
      CREATE INDEX IF NOT EXISTS used_assertions_expiry ON used_assertions(expires_at);
      CREATE TABLE IF NOT EXISTS sessions (
        sid TEXT PRIMARY KEY,
        assertion_jti TEXT NOT NULL,
        subject TEXT NOT NULL,
        tenant_id TEXT NOT NULL,
        roles_json TEXT NOT NULL,
        issued_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL,
        revoked_at INTEGER
      ) STRICT;
      CREATE INDEX IF NOT EXISTS sessions_expiry ON sessions(expires_at);
      CREATE INDEX IF NOT EXISTS sessions_subject ON sessions(tenant_id, subject, expires_at);
      CREATE TABLE IF NOT EXISTS revocation_receipts (
        event_id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        subject TEXT NOT NULL,
        revoked_sessions INTEGER NOT NULL,
        created_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL
      ) STRICT;
      CREATE INDEX IF NOT EXISTS revocation_receipts_expiry ON revocation_receipts(expires_at);
      CREATE TABLE IF NOT EXISTS rate_limits (
        scope TEXT NOT NULL,
        window_start INTEGER NOT NULL,
        count INTEGER NOT NULL,
        expires_at INTEGER NOT NULL,
        PRIMARY KEY(scope, window_start)
      ) STRICT;
      CREATE INDEX IF NOT EXISTS rate_limits_expiry ON rate_limits(expires_at);
    `);
    const metadata = database.prepare('SELECT value FROM state_metadata WHERE key = ?').get('contract');
    if (!metadata) database.prepare('INSERT INTO state_metadata(key, value) VALUES(?, ?)').run('contract', AUTH_STATE_CONTRACT);
    else if (metadata.value !== AUTH_STATE_CONTRACT) fail('auth state schema contract is incompatible');
    chmodSync(path, 0o600);
  } catch (error) {
    database.close();
    throw error;
  }

  const deleteAssertions = database.prepare('DELETE FROM used_assertions WHERE expires_at <= ?');
  const deleteSessions = database.prepare('DELETE FROM sessions WHERE expires_at <= ?');
  const deleteRevocationReceipts = database.prepare('DELETE FROM revocation_receipts WHERE expires_at <= ?');
  const deleteRates = database.prepare('DELETE FROM rate_limits WHERE expires_at <= ?');
  const insertAssertion = database.prepare('INSERT INTO used_assertions(jti, claimed_at, expires_at) VALUES(?, ?, ?) ON CONFLICT(jti) DO NOTHING');
  const insertSession = database.prepare('INSERT INTO sessions(sid, assertion_jti, subject, tenant_id, roles_json, issued_at, expires_at, revoked_at) VALUES(?, ?, ?, ?, ?, ?, ?, NULL)');
  const selectSession = database.prepare('SELECT assertion_jti, subject, tenant_id, roles_json, issued_at, expires_at, revoked_at FROM sessions WHERE sid = ?');
  const revokeSessionStatement = database.prepare('UPDATE sessions SET revoked_at = ? WHERE sid = ? AND revoked_at IS NULL AND expires_at > ?');
  const revokeSubjectStatement = database.prepare('UPDATE sessions SET revoked_at = ? WHERE tenant_id = ? AND subject = ? AND revoked_at IS NULL AND expires_at > ?');
  const selectRevocationReceipt = database.prepare('SELECT tenant_id, subject, revoked_sessions, created_at, expires_at FROM revocation_receipts WHERE event_id = ?');
  const insertRevocationReceipt = database.prepare('INSERT INTO revocation_receipts(event_id, tenant_id, subject, revoked_sessions, created_at, expires_at) VALUES(?, ?, ?, ?, ?, ?)');
  const upsertRate = database.prepare('INSERT INTO rate_limits(scope, window_start, count, expires_at) VALUES(?, ?, 1, ?) ON CONFLICT(scope, window_start) DO UPDATE SET count = count + 1, expires_at = excluded.expires_at');
  const selectRate = database.prepare('SELECT count FROM rate_limits WHERE scope = ? AND window_start = ?');
  const countAssertions = database.prepare('SELECT COUNT(*) AS count FROM used_assertions');
  const countActiveSessions = database.prepare('SELECT COUNT(*) AS count FROM sessions WHERE revoked_at IS NULL');
  const countRevokedSessions = database.prepare('SELECT COUNT(*) AS count FROM sessions WHERE revoked_at IS NOT NULL');
  const countRates = database.prepare('SELECT COUNT(*) AS count FROM rate_limits');
  const healthStatement = database.prepare('SELECT value FROM state_metadata WHERE key = ?');

  const prune = (nowSeconds) => {
    ensureOpen(); integer(nowSeconds, 'current time');
    transaction(database, () => {
      deleteAssertions.run(nowSeconds);
      deleteSessions.run(nowSeconds);
      deleteRevocationReceipts.run(nowSeconds);
      deleteRates.run(nowSeconds);
    });
  };
  const state = {
    descriptor: descriptor('sqlite', true, true),
    commitExchange(input, nowSeconds) {
      ensureOpen(); const value = validateExchange(input, nowSeconds);
      return transaction(database, () => {
        deleteAssertions.run(nowSeconds);
        deleteSessions.run(nowSeconds);
        deleteRates.run(nowSeconds);
        const claimed = insertAssertion.run(value.assertionId, nowSeconds, value.assertionExpiresAt);
        if (Number(claimed.changes) !== 1) return false;
        insertSession.run(value.session.sid, value.session.assertionId, value.session.subject, value.session.tenantId, value.session.rolesJson, value.session.issuedAt, value.session.expiresAt);
        return true;
      });
    },
    validateSession(session, nowSeconds) {
      ensureOpen(); const value = validateSessionRecord(session, nowSeconds);
      const stored = selectSession.get(value.sid);
      return Boolean(stored && stored.revoked_at === null && stored.assertion_jti === value.assertionId && stored.subject === value.subject && stored.tenant_id === value.tenantId && stored.roles_json === value.rolesJson && stored.issued_at === value.issuedAt && stored.expires_at === value.expiresAt && stored.expires_at > nowSeconds);
    },
    revokeSession(sid, nowSeconds) {
      ensureOpen(); identifier(sid, SESSION_ID, 'session identifier'); integer(nowSeconds, 'current time');
      return Number(revokeSessionStatement.run(nowSeconds, sid, nowSeconds).changes) === 1;
    },
    revokeSubject(tenantId, subject, nowSeconds) {
      ensureOpen(); identifier(tenantId, TENANT_ID, 'session tenant'); identifier(subject, SUBJECT, 'session subject'); integer(nowSeconds, 'current time');
      return Number(revokeSubjectStatement.run(nowSeconds, tenantId, subject, nowSeconds).changes);
    },
    revokeSubjectOnce(eventId, tenantId, subject, nowSeconds, receiptExpiresAt) {
      ensureOpen();
      const value = validateRevocationReceipt(eventId, tenantId, subject, nowSeconds, receiptExpiresAt);
      return transaction(database, () => {
        deleteRevocationReceipts.run(value.nowSeconds);
        const existing = selectRevocationReceipt.get(value.eventId);
        if (existing) {
          if (existing.tenant_id !== value.tenantId || existing.subject !== value.subject) fail('revocation event target mismatch');
          return revocationReceipt({
            eventId: value.eventId,
            revokedSessions: Number(existing.revoked_sessions),
            createdAt: Number(existing.created_at),
            expiresAt: Number(existing.expires_at),
          }, true);
        }
        const count = Number(revokeSubjectStatement.run(value.nowSeconds, value.tenantId, value.subject, value.nowSeconds).changes);
        insertRevocationReceipt.run(value.eventId, value.tenantId, value.subject, count, value.nowSeconds, value.receiptExpiresAt);
        return revocationReceipt({
          eventId: value.eventId,
          revokedSessions: count,
          createdAt: value.nowSeconds,
          expiresAt: value.receiptExpiresAt,
        }, false);
      });
    },
    consumeRateLimit(scope, windowStart, windowSeconds, limit, nowSeconds) {
      ensureOpen(); const value = validateRate(scope, windowStart, windowSeconds, limit, nowSeconds);
      return transaction(database, () => {
        deleteRates.run(nowSeconds);
        upsertRate.run(value.scope, value.windowStart, value.expiresAt);
        const count = Number(selectRate.get(value.scope, value.windowStart).count);
        return Object.freeze({ allowed: count <= value.limit, count, reset_at: value.expiresAt });
      });
    },
    prune,
    stats(nowSeconds) {
      prune(nowSeconds);
      return Object.freeze({
        contract: AUTH_STATE_CONTRACT,
        backend: 'sqlite',
        assertions: Number(countAssertions.get().count),
        active_sessions: Number(countActiveSessions.get().count),
        revoked_sessions: Number(countRevokedSessions.get().count),
        rate_limit_buckets: Number(countRates.get().count),
      });
    },
    health() {
      ensureOpen();
      const row = healthStatement.get('contract');
      if (!row || row.value !== AUTH_STATE_CONTRACT) fail('auth state health check failed');
      return Object.freeze({ status: 'ok', ...state.descriptor });
    },
    close() {
      if (!closed) {
        closed = true;
        database.close();
      }
    },
  };
  return interfaceCheck(state);
}
