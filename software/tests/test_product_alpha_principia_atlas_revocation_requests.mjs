import assert from 'node:assert/strict';
import { generateKeyPairSync } from 'node:crypto';
import {
  chmodSync,
  existsSync,
  lstatSync,
  mkdtempSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import { main as authStateCommand } from '../principia_atlas/hosted/auth_state_cli.mjs';
import { main as revocationRequestCommand } from '../principia_atlas/hosted/revocation_request_cli.mjs';
import {
  canonicalJson,
  canonicalOidcSubject,
  OIDC_REVOCATION_REQUEST_CONTRACT,
  OIDC_REVOCATION_REQUEST_DRAFT_CONTRACT,
  openSqliteAuthState,
  readOidcRevocationRequest,
  revocationPublicKeyIdFromFile,
  signOidcRevocationRequest,
} from '../principia_atlas/hosted/index.mjs';

const now = 1_800_000_000;
const tenant = 'school-demo';
const issuer = 'https://identity.example.test';
const externalSubject = 'envelope-learner';
const eventId = 'identity-disable-event-0004';
const subject = canonicalOidcSubject(issuer, externalSubject);
const otherSubject = canonicalOidcSubject(issuer, 'other-envelope-learner');

function draft(overrides = {}) {
  return {
    contract: OIDC_REVOCATION_REQUEST_DRAFT_CONTRACT,
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

function keyPair(root, prefix = 'revocation') {
  const { privateKey, publicKey } = generateKeyPairSync('ed25519');
  const privatePath = join(root, `${prefix}-private.der`);
  const publicPath = join(root, `${prefix}-public.der`);
  writeFileSync(privatePath, privateKey.export({ format: 'der', type: 'pkcs8' }), { mode: 0o400 });
  chmodSync(privatePath, 0o400);
  writeFileSync(publicPath, publicKey.export({ format: 'der', type: 'spki' }), { mode: 0o444 });
  chmodSync(publicPath, 0o444);
  return {
    privateKey,
    publicKey,
    privatePath,
    publicPath,
    keyId: revocationPublicKeyIdFromFile(publicPath),
  };
}

function signedRequest(keys, overrides = {}) {
  return signOidcRevocationRequest(draft(overrides), keys.privateKey);
}

function writeJson(root, value, name, mode = 0o600) {
  const path = join(root, name);
  writeFileSync(path, canonicalJson(value), { mode });
  chmodSync(path, mode);
  return path;
}

function writeRequest(root, keys, overrides = {}, name = 'revocation-request.json', mode = 0o600) {
  return writeJson(root, signedRequest(keys, overrides), name, mode);
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

test('signed OIDC revocation request has strict file, key, signature, and time boundaries', () => {
  const root = mkdtempSync(join(tmpdir(), 'principia-signed-revocation-request-'));
  try {
    const keys = keyPair(root);
    const wrongKeys = keyPair(root, 'wrong');
    const request = signedRequest(keys);
    const path = writeJson(root, request, 'request.json');
    assert.equal(request.contract, OIDC_REVOCATION_REQUEST_CONTRACT);
    assert.deepEqual(readOidcRevocationRequest(path, keys.publicPath, now), {
      tenantId: tenant,
      subject,
      eventId,
      issuedAt: now - 10,
      expiresAt: now + 120,
      receiptTtlSeconds: 3600,
      keyId: keys.keyId,
    });

    assert.throws(() => readOidcRevocationRequest(
      writeJson(root, { ...request, unexpected: true }, 'extra.json'),
      keys.publicPath,
      now,
    ), /fields/);
    assert.throws(() => readOidcRevocationRequest(
      writeJson(root, request, 'broad.json', 0o644),
      keys.publicPath,
      now,
    ), /permissions/);

    const requestLink = join(root, 'request-link.json');
    symlinkSync(path, requestLink);
    assert.throws(() => readOidcRevocationRequest(requestLink, keys.publicPath, now), /regular file/);

    assert.throws(() => readOidcRevocationRequest(
      writeJson(root, { ...request, external_subject: 'tampered-learner' }, 'tampered.json'),
      keys.publicPath,
      now,
    ), /signature verification failed/);
    assert.throws(() => readOidcRevocationRequest(path, wrongKeys.publicPath, now), /key identifier does not match/);

    chmodSync(keys.publicPath, 0o644);
    assert.throws(() => readOidcRevocationRequest(path, keys.publicPath, now), /public key permissions/);
    chmodSync(keys.publicPath, 0o444);
    const publicLink = join(root, 'public-link.der');
    symlinkSync(keys.publicPath, publicLink);
    assert.throws(() => readOidcRevocationRequest(path, publicLink, now), /public key must be a regular file/);

    assert.throws(() => readOidcRevocationRequest(
      writeRequest(root, keys, { expires_at: now }, 'expired.json'),
      keys.publicPath,
      now,
    ), /expired/);
    assert.throws(() => readOidcRevocationRequest(
      writeRequest(root, keys, { issued_at: now + 31, expires_at: now + 100 }, 'future.json'),
      keys.publicPath,
      now,
    ), /not yet valid/);
    assert.throws(() => signOidcRevocationRequest(
      draft({ issued_at: now, expires_at: now + 301 }),
      keys.privateKey,
    ), /lifetime/);
    assert.throws(() => signOidcRevocationRequest(
      draft({ receipt_ttl_seconds: 59 }),
      keys.privateKey,
    ), /receipt TTL/);

    const unsigned = writeJson(root, {
      contract: 'principia-atlas-hosted-oidc-revocation-request/0.1',
      tenant_id: tenant,
      issuer,
      external_subject: externalSubject,
      event_id: eventId,
      issued_at: now - 10,
      expires_at: now + 120,
      receipt_ttl_seconds: 3600,
    }, 'unsigned.json');
    assert.throws(() => readOidcRevocationRequest(unsigned, keys.publicPath, now), /fields/);

    const oversized = join(root, 'oversized.json');
    writeFileSync(oversized, 'x'.repeat(8193), { mode: 0o600 });
    chmodSync(oversized, 0o600);
    assert.throws(() => readOidcRevocationRequest(oversized, keys.publicPath, now), /size/);

    const missingState = join(root, 'must-not-exist.sqlite');
    assert.throws(() => authStateCommand([
      'revoke-oidc-request',
      '--state', missingState,
      '--request-file', writeRequest(root, keys, { expires_at: now }, 'expired-cli.json'),
      '--request-key-file', keys.publicPath,
      '--now', String(now),
    ], () => {}), /expired/);
    assert.equal(existsSync(missingState), false);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('offline signer keeps identity out of argv and emits a private authenticated request', () => {
  const root = mkdtempSync(join(tmpdir(), 'principia-revocation-signer-'));
  try {
    const keys = keyPair(root);
    const draftPath = writeJson(root, draft(), 'request-draft.json');
    const requestPath = join(root, 'signed-request.json');
    const signArgs = [
      'sign',
      '--input', draftPath,
      '--private-key-file', keys.privatePath,
      '--output', requestPath,
    ];
    assert.equal(signArgs.join('\u0000').includes(externalSubject), false);
    assert.equal(signArgs.join('\u0000').includes(issuer), false);

    let signOutput = '';
    const signed = revocationRequestCommand(signArgs, (value) => { signOutput += value; });
    assert.equal(signed.command, 'sign');
    assert.equal(signed.event_id, eventId);
    assert.equal(signed.key_id, keys.keyId);
    assert.equal(signOutput.includes(externalSubject), false);
    assert.equal(signOutput.includes(issuer), false);
    assert.equal(lstatSync(requestPath).mode & 0o777, 0o600);
    assert.equal(readOidcRevocationRequest(requestPath, keys.publicPath, now).subject, subject);
    assert.throws(() => revocationRequestCommand(signArgs, () => {}), /EEXIST/);

    let keyOutput = '';
    const identified = revocationRequestCommand([
      'key-id',
      '--public-key-file', keys.publicPath,
    ], (value) => { keyOutput += value; });
    assert.equal(identified.key_id, keys.keyId);
    assert.equal(keyOutput.includes(keys.keyId), true);
    assert.throws(() => revocationRequestCommand([
      'key-id',
      '--public-key-file', keys.publicPath,
      '--output', join(root, 'invalid'),
    ], () => {}), /only accepts/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('operator CLI verifies a signed request before retry-safe subject revocation', () => {
  const root = mkdtempSync(join(tmpdir(), 'principia-signed-revocation-request-cli-'));
  const keys = keyPair(root);
  const statePath = join(root, 'auth-state.sqlite');
  const requestPath = writeRequest(root, keys);
  const state = openSqliteAuthState(statePath);
  const sessions = seed(state);
  state.close();
  const common = [
    'revoke-oidc-request',
    '--state', statePath,
    '--request-file', requestPath,
    '--request-key-file', keys.publicPath,
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
    assert.equal(first.verified_key_id, keys.keyId);
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
    assert.equal(retry.verified_key_id, keys.keyId);
    assert.equal(retry.replayed, true);
    assert.equal(retry.revoked_sessions, 2);
    assert.equal(retry.created_at, now);
    assert.equal(retry.expires_at, now + 3600);
    assert.equal(retryOutput.includes(externalSubject), false);
    assert.equal(retryOutput.includes(subject), false);

    assert.throws(() => authStateCommand([
      'revoke-oidc-request',
      '--state', statePath,
      '--request-file', requestPath,
      '--now', String(now + 1),
    ], () => {}), /request-key-file/);
    assert.throws(() => authStateCommand([
      ...common,
      '--external-subject', externalSubject,
      '--now', String(now + 1),
    ], () => {}), /unknown or duplicate argument/);

    writeFileSync(requestPath, canonicalJson(signedRequest(keys, {
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
