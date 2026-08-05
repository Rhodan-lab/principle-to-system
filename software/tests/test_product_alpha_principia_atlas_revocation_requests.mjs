import assert from 'node:assert/strict';
import {
  chmodSync,
  existsSync,
  mkdtempSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import { main as authStateCommand } from '../principia_atlas/hosted/auth_state_cli.mjs';
import {
  canonicalJson,
  canonicalOidcSubject,
  OIDC_REVOCATION_REQUEST_CONTRACT,
  openSqliteAuthState,
  readOidcRevocationRequest,
} from '../principia_atlas/hosted/index.mjs';

const now = 1_800_000_000;
const tenant = 'school-demo';
const issuer = 'https://identity.example.test';
const externalSubject = 'envelope-learner';
const eventId = 'identity-disable-event-0004';
const subject = canonicalOidcSubject(issuer, externalSubject);
const otherSubject = canonicalOidcSubject(issuer, 'other-envelope-learner');

function request(overrides = {}) {
  return {
    contract: OIDC_REVOCATION_REQUEST_CONTRACT,
    tenant_id: tenant,
    issuer,
    external_subject: externalSubject,
    event_id: eventId,
    issued_at: now - 10,
    expires_at: now + 120,
    receipt_ttl_seconds: 3600,
    ...overrides,
  };
}

function writeRequest(root, value = request(), name = 'revocation-request.json', mode = 0o600) {
  const path = join(root, name);
  writeFileSync(path, canonicalJson(value), { mode });
  chmodSync(path, mode);
  return path;
}

function session(index, sessionSubject = subject) {
  return {
    sid: `revocation_request_session_000${index}`,
    jti: `revocation_assertion_000${index}`,
    sub: sessionSubject,
    tenant_id: tenant,
    roles: ['learner'],
    iat: now - 20,
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

test('OIDC revocation request file has a strict short-lived security boundary', () => {
  const root = mkdtempSync(join(tmpdir(), 'principia-revocation-request-'));
  try {
    const path = writeRequest(root);
    assert.deepEqual(readOidcRevocationRequest(path, now), {
      tenantId: tenant,
      subject,
      eventId,
      issuedAt: now - 10,
      expiresAt: now + 120,
      receiptTtlSeconds: 3600,
    });

    assert.throws(() => readOidcRevocationRequest(
      writeRequest(root, request({ unexpected: true }), 'extra.json'),
      now,
    ), /fields/);
    assert.throws(() => readOidcRevocationRequest(
      writeRequest(root, request(), 'broad.json', 0o644),
      now,
    ), /permissions/);

    const link = join(root, 'request-link.json');
    symlinkSync(path, link);
    assert.throws(() => readOidcRevocationRequest(link, now), /regular file/);

    assert.throws(() => readOidcRevocationRequest(
      writeRequest(root, request({ expires_at: now }), 'expired.json'),
      now,
    ), /expired/);
    assert.throws(() => readOidcRevocationRequest(
      writeRequest(root, request({ issued_at: now + 31, expires_at: now + 100 }), 'future.json'),
      now,
    ), /not yet valid/);
    assert.throws(() => readOidcRevocationRequest(
      writeRequest(root, request({ issued_at: now, expires_at: now + 301 }), 'long-lived.json'),
      now,
    ), /lifetime/);
    assert.throws(() => readOidcRevocationRequest(
      writeRequest(root, request({ receipt_ttl_seconds: 59 }), 'short-receipt.json'),
      now,
    ), /receipt TTL/);

    const oversized = join(root, 'oversized.json');
    writeFileSync(oversized, 'x'.repeat(8193), { mode: 0o600 });
    chmodSync(oversized, 0o600);
    assert.throws(() => readOidcRevocationRequest(oversized, now), /size/);

    const missingState = join(root, 'must-not-exist.sqlite');
    assert.throws(() => authStateCommand([
      'revoke-oidc-request',
      '--state', missingState,
      '--request-file', writeRequest(root, request({ expires_at: now }), 'expired-cli.json'),
      '--now', String(now),
    ], () => {}), /expired/);
    assert.equal(existsSync(missingState), false);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('operator CLI revokes from a private request file without subject identity in argv or output', () => {
  const root = mkdtempSync(join(tmpdir(), 'principia-revocation-request-cli-'));
  const statePath = join(root, 'auth-state.sqlite');
  const requestPath = writeRequest(root);
  const state = openSqliteAuthState(statePath);
  const sessions = seed(state);
  state.close();
  const common = [
    'revoke-oidc-request',
    '--state', statePath,
    '--request-file', requestPath,
  ];
  try {
    const argvEvidence = common.join('\u0000');
    assert.equal(argvEvidence.includes(externalSubject), false);
    assert.equal(argvEvidence.includes(subject), false);
    assert.equal(argvEvidence.includes(issuer), false);

    let firstOutput = '';
    const first = authStateCommand([
      ...common,
      '--now', String(now),
    ], (value) => { firstOutput += value; });
    assert.equal(first.command, 'revoke-oidc-request');
    assert.equal(first.event_id, eventId);
    assert.equal(first.replayed, false);
    assert.equal(first.revoked_sessions, 2);
    assert.equal(first.created_at, now);
    assert.equal(first.expires_at, now + 3600);
    assert.equal(firstOutput.includes(externalSubject), false);
    assert.equal(firstOutput.includes(subject), false);
    assert.equal(firstOutput.includes(issuer), false);

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
      ...common,
      '--external-subject', externalSubject,
      '--now', String(now + 1),
    ], () => {}), /unknown or duplicate argument/);

    writeFileSync(requestPath, canonicalJson(request({
      external_subject: 'other-envelope-learner',
      issued_at: now,
      expires_at: now + 120,
    })));
    chmodSync(requestPath, 0o600);
    assert.throws(() => authStateCommand([
      ...common,
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
