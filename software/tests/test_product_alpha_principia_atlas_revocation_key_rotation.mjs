import assert from 'node:assert/strict';
import { generateKeyPairSync } from 'node:crypto';
import {
  chmodSync,
  lstatSync,
  mkdtempSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import test from 'node:test';

import { main as authStateCommand } from '../principia_atlas/hosted/auth_state_cli.mjs';
import {
  backupAuthState,
  restoreAuthState,
} from '../principia_atlas/hosted/auth_state_recovery.mjs';
import { main as revocationRequestCommand } from '../principia_atlas/hosted/revocation_request_cli.mjs';
import {
  canonicalJson,
  createMemoryAuthState,
  createOidcRevocationKeyring,
  OIDC_REVOCATION_KEYRING_DRAFT_CONTRACT,
  OIDC_REVOCATION_REQUEST_DRAFT_CONTRACT,
  openSqliteAuthState,
  readOidcRevocationRequestWithKeyring,
  revocationPublicKeyIdFromFile,
  signOidcRevocationRequest,
} from '../principia_atlas/hosted/index.mjs';

const now = 1_800_000_000;
const tenant = 'school-demo';
const issuer = 'https://identity.example.test';
const externalSubject = 'rotation-learner';
const eventId = 'identity-disable-event-rotation-0001';

function keyPair(root, name) {
  const pair = generateKeyPairSync('ed25519');
  const privatePath = join(root, `${name}-private.der`);
  const publicPath = join(root, `${name}-public.der`);
  writeFileSync(privatePath, pair.privateKey.export({ format: 'der', type: 'pkcs8' }), { mode: 0o400 });
  chmodSync(privatePath, 0o400);
  writeFileSync(publicPath, pair.publicKey.export({ format: 'der', type: 'spki' }), { mode: 0o444 });
  chmodSync(publicPath, 0o444);
  return {
    ...pair,
    privatePath,
    publicPath,
    keyId: revocationPublicKeyIdFromFile(publicPath),
  };
}

function requestDraft(overrides = {}) {
  return {
    contract: OIDC_REVOCATION_REQUEST_DRAFT_CONTRACT,
    tenant_id: tenant,
    issuer,
    external_subject: externalSubject,
    event_id: eventId,
    issued_at: now - 5,
    expires_at: now + 120,
    receipt_ttl_seconds: 3600,
    ...overrides,
  };
}

function writeJson(root, value, name, mode) {
  const path = join(root, name);
  writeFileSync(path, canonicalJson(value), { mode });
  chmodSync(path, mode);
  return path;
}

function writeRequest(root, keys, name, overrides = {}) {
  return writeJson(
    root,
    signOidcRevocationRequest(requestDraft(overrides), keys.privateKey),
    name,
    0o600,
  );
}

function buildKeyring(root, entries, revokedKeyIds = [], name = 'revocation-keyring.json') {
  const draftPath = writeJson(root, {
    contract: OIDC_REVOCATION_KEYRING_DRAFT_CONTRACT,
    keys: entries.map(({ publicPath, notBefore = now - 300, notAfter = now + 7200 }) => ({
      public_key_file: publicPath,
      not_before: notBefore,
      not_after: notAfter,
    })),
    revoked_key_ids: revokedKeyIds,
  }, `${name}.draft`, 0o600);
  const output = join(root, name);
  let evidence = '';
  const result = revocationRequestCommand([
    'keyring',
    '--input', draftPath,
    '--output', output,
  ], (value) => { evidence += value; });
  return { path: output, result, evidence };
}

function session(subject, index = 1) {
  return {
    sid: `rotation_session_identifier_000${index}`,
    jti: `rotation_assertion_000${index}`,
    sub: subject,
    tenant_id: tenant,
    roles: ['learner'],
    iat: now - 20,
    exp: now + 7200,
  };
}

test('revocation keyring enforces overlap, validity windows, revocation, and immutable files', () => {
  const root = mkdtempSync(join(tmpdir(), 'principia-revocation-keyring-'));
  try {
    const keyA = keyPair(root, 'key-a');
    const keyB = keyPair(root, 'key-b');
    const keyC = keyPair(root, 'key-c');
    const keyring = buildKeyring(root, [keyA, keyB]);
    assert.deepEqual(keyring.result.key_ids, [...keyring.result.key_ids].sort());
    assert.deepEqual(keyring.result.revoked_key_ids, []);
    assert.equal(keyring.evidence.includes(externalSubject), false);
    assert.equal(keyring.evidence.includes(issuer), false);
    assert.equal(lstatSync(keyring.path).mode & 0o333, 0);

    const requestA = writeRequest(root, keyA, 'request-a.json');
    const requestB = writeRequest(root, keyB, 'request-b.json');
    const requestC = writeRequest(root, keyC, 'request-c.json');
    assert.equal(readOidcRevocationRequestWithKeyring(requestA, keyring.path, now).keyId, keyA.keyId);
    assert.equal(readOidcRevocationRequestWithKeyring(requestB, keyring.path, now).keyId, keyB.keyId);
    assert.throws(() => readOidcRevocationRequestWithKeyring(requestC, keyring.path, now), /not trusted/);

    const revoked = buildKeyring(root, [keyA, keyB], [keyA.keyId], 'revoked-keyring.json');
    assert.throws(() => readOidcRevocationRequestWithKeyring(requestA, revoked.path, now), /signing key is revoked/);
    assert.equal(readOidcRevocationRequestWithKeyring(requestB, revoked.path, now).keyId, keyB.keyId);

    const future = buildKeyring(root, [{ ...keyB, notBefore: now + 1 }], [], 'future-keyring.json');
    assert.throws(() => readOidcRevocationRequestWithKeyring(requestB, future.path, now), /validity window/);
    const expired = buildKeyring(root, [{ ...keyB, notAfter: now - 4 }], [], 'expired-keyring.json');
    assert.throws(() => readOidcRevocationRequestWithKeyring(requestB, expired.path, now), /validity window/);

    assert.throws(() => createOidcRevocationKeyring({
      contract: OIDC_REVOCATION_KEYRING_DRAFT_CONTRACT,
      keys: [
        { public_key_file: keyA.publicPath, not_before: now - 1, not_after: now + 1 },
        { public_key_file: keyA.publicPath, not_before: now - 1, not_after: now + 1 },
      ],
      revoked_key_ids: [],
    }), /duplicate keys/);
    assert.throws(() => createOidcRevocationKeyring({
      contract: OIDC_REVOCATION_KEYRING_DRAFT_CONTRACT,
      keys: [{ public_key_file: keyA.publicPath, not_before: now - 1, not_after: now + 1 }],
      revoked_key_ids: [keyA.keyId, keyA.keyId],
    }), /duplicates/);

    chmodSync(keyring.path, 0o644);
    assert.throws(() => readOidcRevocationRequestWithKeyring(requestA, keyring.path, now), /permissions/);
    chmodSync(keyring.path, 0o444);
    const link = join(root, 'keyring-link.json');
    symlinkSync(keyring.path, link);
    assert.throws(() => readOidcRevocationRequestWithKeyring(requestA, link, now), /regular file/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('rotated retry preserves the first authorization key through SQLite backup and restore', () => {
  const root = mkdtempSync(join(tmpdir(), 'principia-revocation-rotation-state-'));
  try {
    const keyA = keyPair(root, 'key-a');
    const keyB = keyPair(root, 'key-b');
    const keyring = buildKeyring(root, [keyA, keyB]);
    const requestA = writeRequest(root, keyA, 'request-a.json');
    const requestB = writeRequest(root, keyB, 'request-b.json');
    const statePath = join(root, 'auth-state.sqlite');
    const parsed = readOidcRevocationRequestWithKeyring(requestA, keyring.path, now);
    const storedSession = session(parsed.subject);
    const state = openSqliteAuthState(statePath);
    assert.equal(state.commitExchange({
      assertionId: storedSession.jti,
      assertionExpiresAt: now + 300,
      session: storedSession,
    }, now), true);
    state.close();

    const common = (requestPath, targetState = statePath) => [
      'revoke-oidc-request',
      '--state', targetState,
      '--request-file', requestPath,
      '--request-keyring-file', keyring.path,
    ];
    const argvEvidence = common(requestA).join('\u0000');
    assert.equal(argvEvidence.includes(externalSubject), false);
    assert.equal(argvEvidence.includes(issuer), false);

    let firstOutput = '';
    const first = authStateCommand([
      ...common(requestA),
      '--now', String(now),
    ], (value) => { firstOutput += value; });
    assert.equal(first.verified_key_id, keyA.keyId);
    assert.equal(first.authorization_key_id, keyA.keyId);
    assert.equal(first.replayed, false);
    assert.equal(first.revoked_sessions, 1);
    assert.equal(firstOutput.includes(externalSubject), false);
    assert.equal(firstOutput.includes(issuer), false);

    const backupPath = join(root, 'auth-state.backup.sqlite');
    backupAuthState(statePath, backupPath);
    const restoredPath = join(root, 'auth-state.restored.sqlite');
    restoreAuthState(backupPath, restoredPath, 'ALL_INSTANCES_STOPPED');

    let retryOutput = '';
    const retry = authStateCommand([
      ...common(requestB, restoredPath),
      '--now', String(now + 1),
    ], (value) => { retryOutput += value; });
    assert.equal(retry.verified_key_id, keyB.keyId);
    assert.equal(retry.authorization_key_id, keyA.keyId);
    assert.equal(retry.replayed, true);
    assert.equal(retry.revoked_sessions, 1);
    assert.equal(retry.created_at, first.created_at);
    assert.equal(retry.expires_at, first.expires_at);
    assert.equal(retryOutput.includes(externalSubject), false);
    assert.equal(retryOutput.includes(issuer), false);

    const restored = openSqliteAuthState(restoredPath);
    assert.equal(restored.validateSession(storedSession, now + 2), false);
    restored.close();

    const changedTarget = writeRequest(root, keyB, 'changed-target.json', {
      external_subject: 'different-rotation-learner',
      issued_at: now,
      expires_at: now + 120,
    });
    assert.throws(() => authStateCommand([
      ...common(changedTarget, restoredPath),
      '--now', String(now + 2),
    ], () => {}), /target mismatch/);
    assert.throws(() => authStateCommand([
      ...common(requestA, restoredPath),
      '--request-key-file', keyA.publicPath,
      '--now', String(now + 2),
    ], () => {}), /exactly one/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('legacy authentication databases migrate authorization receipts without changing their contract', () => {
  const root = mkdtempSync(join(tmpdir(), 'principia-revocation-receipt-migration-'));
  const statePath = join(root, 'legacy-auth-state.sqlite');
  try {
    const database = new DatabaseSync(statePath);
    database.exec(`
      CREATE TABLE state_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL) STRICT;
      INSERT INTO state_metadata(key, value) VALUES('contract', 'principia-atlas-hosted-auth-state/0.1');
      CREATE TABLE used_assertions (jti TEXT PRIMARY KEY, claimed_at INTEGER NOT NULL, expires_at INTEGER NOT NULL) STRICT;
      CREATE TABLE sessions (
        sid TEXT PRIMARY KEY,
        assertion_jti TEXT NOT NULL,
        subject TEXT NOT NULL,
        tenant_id TEXT NOT NULL,
        roles_json TEXT NOT NULL,
        issued_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL,
        revoked_at INTEGER
      ) STRICT;
      CREATE TABLE revocation_receipts (
        event_id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        subject TEXT NOT NULL,
        revoked_sessions INTEGER NOT NULL,
        created_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL
      ) STRICT;
      CREATE TABLE rate_limits (
        scope TEXT NOT NULL,
        window_start INTEGER NOT NULL,
        count INTEGER NOT NULL,
        expires_at INTEGER NOT NULL,
        PRIMARY KEY(scope, window_start)
      ) STRICT;
    `);
    database.close();
    chmodSync(statePath, 0o600);

    const migrated = openSqliteAuthState(statePath);
    assert.equal(migrated.health().contract, 'principia-atlas-hosted-auth-state/0.1');
    migrated.close();

    const inspected = new DatabaseSync(statePath, { readOnly: true });
    const columns = inspected.prepare('PRAGMA table_info(revocation_receipts)').all().map((row) => row.name);
    const contract = inspected.prepare('SELECT value FROM state_metadata WHERE key = ?').get('contract').value;
    inspected.close();
    assert.equal(columns.includes('authorization_key_id'), true);
    assert.equal(contract, 'principia-atlas-hosted-auth-state/0.1');

    const memory = createMemoryAuthState();
    const authorizationKey = `ed25519:${'a'.repeat(43)}`;
    const first = memory.revokeSubjectOnce(
      'memory-rotation-event-0001',
      tenant,
      'oidc:memory-rotation-subject',
      now,
      now + 3600,
      authorizationKey,
    );
    const retry = memory.revokeSubjectOnce(
      'memory-rotation-event-0001',
      tenant,
      'oidc:memory-rotation-subject',
      now + 1,
      now + 3601,
      `ed25519:${'b'.repeat(43)}`,
    );
    assert.equal(first.authorization_key_id, authorizationKey);
    assert.equal(retry.authorization_key_id, authorizationKey);
    assert.equal(retry.replayed, true);
    memory.close();
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
