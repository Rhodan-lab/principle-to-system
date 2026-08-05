import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import { main as authStateCommand } from '../principia_atlas/hosted/auth_state_cli.mjs';
import {
  canonicalOidcSubject,
  createMemoryAuthState,
  openSqliteAuthState,
} from '../principia_atlas/hosted/index.mjs';

const now = 1_800_000_000;
const tenant = 'school-demo';
const issuer = 'https://identity.example.test';
const externalSubject = 'receipt-learner';
const subject = canonicalOidcSubject(issuer, externalSubject);
const otherSubject = canonicalOidcSubject(issuer, 'other-learner');

function session(index, sessionSubject = subject) {
  return {
    sid: `receipt_session_identifier_000${index}`,
    jti: `receipt_assertion_000${index}`,
    sub: sessionSubject,
    tenant_id: tenant,
    roles: ['learner'],
    iat: now - 10,
    exp: now + 7200,
  };
}

function seed(state) {
  const sessions = [session(1), session(2), session(3, otherSubject)];
  for (const value of sessions) {
    assert.equal(state.commitExchange({
      assertionId: value.jti,
      assertionExpiresAt: now + 300,
      session: value,
    }, now), true);
  }
  return sessions;
}

function verifyReceiptBackend(state) {
  const sessions = seed(state);
  const first = state.revokeSubjectOnce(
    'identity-disable-event-0001',
    tenant,
    subject,
    now,
    now + 3600,
  );
  assert.deepEqual(first, {
    event_id: 'identity-disable-event-0001',
    replayed: false,
    revoked_sessions: 2,
    created_at: now,
    expires_at: now + 3600,
  });
  const retry = state.revokeSubjectOnce(
    'identity-disable-event-0001',
    tenant,
    subject,
    now + 1,
    now + 3601,
  );
  assert.deepEqual(retry, {
    event_id: 'identity-disable-event-0001',
    replayed: true,
    revoked_sessions: 2,
    created_at: now,
    expires_at: now + 3600,
  });
  assert.throws(() => state.revokeSubjectOnce(
    'identity-disable-event-0001',
    tenant,
    otherSubject,
    now + 2,
    now + 3602,
  ), /target mismatch/);
  assert.equal(state.validateSession(sessions[0], now + 3), false);
  assert.equal(state.validateSession(sessions[1], now + 3), false);
  assert.equal(state.validateSession(sessions[2], now + 3), true);
}

test('memory and SQLite backends preserve atomic revocation receipts', async (context) => {
  await context.test('memory', () => {
    const state = createMemoryAuthState();
    try { verifyReceiptBackend(state); }
    finally { state.close(); }
  });
  await context.test('sqlite', () => {
    const root = mkdtempSync(join(tmpdir(), 'principia-revocation-receipt-'));
    const state = openSqliteAuthState(join(root, 'auth-state.sqlite'));
    try { verifyReceiptBackend(state); }
    finally {
      state.close();
      rmSync(root, { recursive: true, force: true });
    }
  });
});

test('operator CLI returns a replayable receipt without exposing subject identity', () => {
  const root = mkdtempSync(join(tmpdir(), 'principia-revocation-cli-'));
  const statePath = join(root, 'auth-state.sqlite');
  const state = openSqliteAuthState(statePath);
  const sessions = seed(state);
  state.close();
  const common = [
    'revoke-oidc-subject',
    '--state', statePath,
    '--tenant', tenant,
    '--issuer', issuer,
    '--external-subject', externalSubject,
    '--event-id', 'identity-disable-event-0002',
    '--receipt-ttl-seconds', '3600',
  ];
  try {
    let firstOutput = '';
    const first = authStateCommand([
      ...common,
      '--now', String(now),
    ], (value) => { firstOutput += value; });
    assert.equal(first.command, 'revoke-oidc-subject');
    assert.equal(first.event_id, 'identity-disable-event-0002');
    assert.equal(first.replayed, false);
    assert.equal(first.revoked_sessions, 2);
    assert.equal(first.created_at, now);
    assert.equal(first.expires_at, now + 3600);
    assert.equal(firstOutput.includes(externalSubject), false);
    assert.equal(firstOutput.includes(subject), false);

    let retryOutput = '';
    const retry = authStateCommand([
      ...common,
      '--now', String(now + 1),
    ], (value) => { retryOutput += value; });
    assert.equal(retry.replayed, true);
    assert.equal(retry.revoked_sessions, 2);
    assert.equal(retry.created_at, now);
    assert.equal(retry.expires_at, now + 3600);
    assert.equal(retryOutput.includes(externalSubject), false);
    assert.equal(retryOutput.includes(subject), false);

    assert.throws(() => authStateCommand([
      'revoke-oidc-subject',
      '--state', statePath,
      '--tenant', tenant,
      '--issuer', issuer,
      '--external-subject', 'other-learner',
      '--event-id', 'identity-disable-event-0002',
      '--receipt-ttl-seconds', '3600',
      '--now', String(now + 2),
    ], () => {}), /target mismatch/);

    const reopened = openSqliteAuthState(statePath);
    try {
      assert.equal(reopened.validateSession(sessions[0], now + 3), false);
      assert.equal(reopened.validateSession(sessions[1], now + 3), false);
      assert.equal(reopened.validateSession(sessions[2], now + 3), true);
    } finally { reopened.close(); }
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('operator CLI requires bounded receipt inputs', () => {
  assert.throws(() => authStateCommand([
    'revoke-oidc-subject',
    '--state', '/tmp/missing-state.sqlite',
    '--tenant', tenant,
    '--issuer', issuer,
    '--external-subject', externalSubject,
  ], () => {}), /event-id/);
  assert.throws(() => authStateCommand([
    'revoke-oidc-subject',
    '--state', '/tmp/missing-state.sqlite',
    '--tenant', tenant,
    '--issuer', issuer,
    '--external-subject', externalSubject,
    '--event-id', 'identity-disable-event-0003',
    '--receipt-ttl-seconds', '59',
  ], () => {}), /receipt-ttl-seconds/);
});
