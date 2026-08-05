import { chmodSync, lstatSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { DatabaseSync } from 'node:sqlite';

import { fail } from './strict_json.mjs';

const AUTH_STATE_CONTRACT = 'principia-atlas-hosted-auth-state/0.1';
const EVENT_ID = /^[A-Za-z0-9._:@+-]{16,200}$/;
const TENANT_ID = /^[a-z][a-z0-9-]{1,62}$/;
const SUBJECT = /^[A-Za-z0-9._:@+-]{1,200}$/;
const KEY_ID = /^ed25519:[A-Za-z0-9_-]{43}$/;
const MAX_RECEIPT_TTL_SECONDS = 365 * 24 * 60 * 60;
const GENERATION_METADATA_KEY = 'oidc_revocation_keyring_generation';

function integer(value, label, minimum = 0, maximum = Number.MAX_SAFE_INTEGER) {
  if (!Number.isSafeInteger(value) || value < minimum || value > maximum) fail(`${label} is invalid`);
  return value;
}

function identifier(value, pattern, label) {
  if (typeof value !== 'string' || !pattern.test(value)) fail(`${label} is invalid`);
  return value;
}

function statePath(pathInput) {
  if (typeof pathInput !== 'string' || pathInput.length === 0 || pathInput === ':memory:') fail('auth state path is invalid');
  const path = resolve(pathInput);
  const parent = dirname(path);
  mkdirSync(parent, { recursive: true, mode: 0o700 });
  const parentStat = lstatSync(parent);
  if (parentStat.isSymbolicLink() || !parentStat.isDirectory()) fail('auth state parent must be a regular directory');
  const stats = lstatSync(path);
  if (stats.isSymbolicLink() || !stats.isFile()) fail('auth state must be a regular file');
  return path;
}

function transaction(database, operation) {
  database.exec('BEGIN IMMEDIATE');
  try {
    const result = operation();
    database.exec('COMMIT');
    return result;
  } catch (error) {
    try { database.exec('ROLLBACK'); } catch {}
    throw error;
  }
}

function columns(database) {
  return database.prepare('PRAGMA table_info(revocation_receipts)').all().map((row) => row.name);
}

function ensureReceiptColumns(database) {
  let names = columns(database);
  if (!names.includes('authorization_key_id')) {
    try { database.exec('ALTER TABLE revocation_receipts ADD COLUMN authorization_key_id TEXT'); }
    catch (error) {
      names = columns(database);
      if (!names.includes('authorization_key_id')) throw error;
    }
  }
  names = columns(database);
  if (!names.includes('authorization_keyring_generation')) {
    try { database.exec('ALTER TABLE revocation_receipts ADD COLUMN authorization_keyring_generation INTEGER'); }
    catch (error) {
      names = columns(database);
      if (!names.includes('authorization_keyring_generation')) throw error;
    }
  }
}

function validateRequest(request, nowSeconds) {
  if (!request || typeof request !== 'object' || Array.isArray(request)) fail('OIDC revocation authorization is invalid');
  const eventId = identifier(request.eventId, EVENT_ID, 'revocation event identifier');
  const tenantId = identifier(request.tenantId, TENANT_ID, 'session tenant');
  const subject = identifier(request.subject, SUBJECT, 'session subject');
  const keyId = identifier(request.keyId, KEY_ID, 'revocation authorization key identifier');
  const now = integer(nowSeconds, 'current time');
  const receiptTtlSeconds = integer(request.receiptTtlSeconds, 'revocation receipt TTL', 60, MAX_RECEIPT_TTL_SECONDS);
  const keyringGeneration = request.keyringGeneration === null || request.keyringGeneration === undefined
    ? null
    : integer(request.keyringGeneration, 'OIDC revocation keyring generation', 1);
  return {
    eventId,
    tenantId,
    subject,
    keyId,
    now,
    receiptExpiresAt: now + receiptTtlSeconds,
    keyringGeneration,
  };
}

function receipt(row, eventId, replayed) {
  const result = {
    event_id: eventId,
    replayed,
    revoked_sessions: Number(row.revoked_sessions),
    created_at: Number(row.created_at),
    expires_at: Number(row.expires_at),
  };
  if (row.authorization_key_id !== null && row.authorization_key_id !== undefined) {
    result.authorization_key_id = row.authorization_key_id;
  }
  if (row.authorization_keyring_generation !== null && row.authorization_keyring_generation !== undefined) {
    result.authorization_keyring_generation = Number(row.authorization_keyring_generation);
  }
  return Object.freeze(result);
}

function currentGeneration(database) {
  const row = database.prepare('SELECT value FROM state_metadata WHERE key = ?').get(GENERATION_METADATA_KEY);
  if (!row) return 0;
  const value = Number(row.value);
  return integer(value, 'stored OIDC revocation keyring generation', 1);
}

function enforceTrustGeneration(database, generation) {
  const current = currentGeneration(database);
  if (generation === null) {
    if (current > 0) fail('single-key trust source is disabled after keyring activation');
    return current;
  }
  if (generation < current) fail('OIDC revocation keyring rollback detected');
  if (generation > current) {
    database.prepare(`
      INSERT INTO state_metadata(key, value) VALUES(?, ?)
      ON CONFLICT(key) DO UPDATE SET value = excluded.value
    `).run(GENERATION_METADATA_KEY, String(generation));
  }
  return Math.max(current, generation);
}

export function revokeSubjectOnceWithTrustState(statePathInput, requestInput, nowSeconds) {
  const request = validateRequest(requestInput, nowSeconds);
  const path = statePath(statePathInput);
  const database = new DatabaseSync(path);
  try {
    database.exec('PRAGMA busy_timeout=5000; PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA foreign_keys=ON; PRAGMA trusted_schema=OFF;');
    const metadata = database.prepare('SELECT value FROM state_metadata WHERE key = ?').get('contract');
    if (!metadata || metadata.value !== AUTH_STATE_CONTRACT) fail('auth state schema contract is incompatible');
    ensureReceiptColumns(database);
    chmodSync(path, 0o600);

    const deleteExpired = database.prepare('DELETE FROM revocation_receipts WHERE expires_at <= ?');
    const selectReceipt = database.prepare(`
      SELECT tenant_id, subject, revoked_sessions, created_at, expires_at,
             authorization_key_id, authorization_keyring_generation
      FROM revocation_receipts WHERE event_id = ?
    `);
    const revokeSubject = database.prepare(`
      UPDATE sessions SET revoked_at = ?
      WHERE tenant_id = ? AND subject = ? AND revoked_at IS NULL AND expires_at > ?
    `);
    const insertReceipt = database.prepare(`
      INSERT INTO revocation_receipts(
        event_id, tenant_id, subject, revoked_sessions, created_at, expires_at,
        authorization_key_id, authorization_keyring_generation
      ) VALUES(?, ?, ?, ?, ?, ?, ?, ?)
    `);

    return transaction(database, () => {
      deleteExpired.run(request.now);
      const existing = selectReceipt.get(request.eventId);
      if (existing && (existing.tenant_id !== request.tenantId || existing.subject !== request.subject)) {
        fail('revocation event target mismatch');
      }
      enforceTrustGeneration(database, request.keyringGeneration);
      if (existing) return receipt(existing, request.eventId, true);

      const revokedSessions = Number(
        revokeSubject.run(request.now, request.tenantId, request.subject, request.now).changes,
      );
      insertReceipt.run(
        request.eventId,
        request.tenantId,
        request.subject,
        revokedSessions,
        request.now,
        request.receiptExpiresAt,
        request.keyId,
        request.keyringGeneration,
      );
      return receipt({
        revoked_sessions: revokedSessions,
        created_at: request.now,
        expires_at: request.receiptExpiresAt,
        authorization_key_id: request.keyId,
        authorization_keyring_generation: request.keyringGeneration,
      }, request.eventId, false);
    });
  } finally {
    database.close();
  }
}

export function readMinimumOidcRevocationKeyringGeneration(statePathInput) {
  const path = statePath(statePathInput);
  const database = new DatabaseSync(path, { readOnly: true });
  try {
    const metadata = database.prepare('SELECT value FROM state_metadata WHERE key = ?').get('contract');
    if (!metadata || metadata.value !== AUTH_STATE_CONTRACT) fail('auth state schema contract is incompatible');
    return currentGeneration(database);
  } finally {
    database.close();
  }
}
