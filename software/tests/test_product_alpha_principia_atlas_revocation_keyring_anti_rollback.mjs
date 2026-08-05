import assert from 'node:assert/strict';
import { generateKeyPairSync } from 'node:crypto';
import {
  chmodSync,
  lstatSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import { main as authStateCommand } from '../principia_atlas/hosted/auth_state_cli.mjs';
import {
  backupAuthState,
  restoreAuthState,
} from '../principia_atlas/hosted/auth_state_recovery.mjs';
import { main as revocationRequestCommand } from '../principia_atlas/hosted/revocation_request_cli.mjs';
import {
  canonicalJson,
  canonicalOidcSubject,
  SIGNED_OIDC_REVOCATION_KEYRING_DRAFT_CONTRACT,
  OIDC_REVOCATION_REQUEST_DRAFT_CONTRACT,
  openSqliteAuthState,
  readMinimumOidcRevocationKeyringGeneration,
  readOidcRevocationRequestWithSignedKeyring,
  revocationPublicKeyIdFromFile,
  signOidcRevocationRequest,
} from '../principia_atlas/hosted/index.mjs';

const now = 1_800_000_000;
const tenant = 'school-demo';
const issuer = 'https://identity.example.test';
const externalSubject = 'anti-rollback-learner';
const eventId = 'identity-disable-event-anti-rollback-0001';

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

function writeJson(root, name, value, mode) {
  const path = join(root, name);
  writeFileSync(path, canonicalJson(value), { mode });
  chmodSync(path, mode);
  return path;
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

function writeRequest(root, key, name, overrides = {}) {
  return writeJson(
    root,
    name,
    signOidcRevocationRequest(requestDraft(overrides), key.privateKey),
    0o600,
  );
}

function buildKeyring(root, rootKey, requestKeys, generation, name) {
  const draft = writeJson(root, `${name}.draft.json`, {
    contract: SIGNED_OIDC_REVOCATION_KEYRING_DRAFT_CONTRACT,
    generation,
    keys: requestKeys.map((key) => ({
      public_key_file: key.publicPath,
      not_before: now - 300,
      not_after: now + 7200,
    })),
    revoked_key_ids: [],
  }, 0o600);
  const output = join(root, `${name}.json`);
  let evidence = '';
  const result = revocationRequestCommand([
    'keyring',
    '--input', draft,
    '--root-private-key-file', rootKey.privatePath,
    '--output', output,
  ], (value) => { evidence += value; });
  return { draft, output, result, evidence };
}

function seedState(path, subject) {
  const state = openSqliteAuthState(path);
  const session = {
    sid: 'anti_rollback_session_identifier_0001',
    jti: 'anti_rollback_assertion_0001',
    sub: subject,
    tenant_id: tenant,
    roles: ['learner'],
    iat: now - 20,
    exp: now + 7200,
  };
  assert.equal(state.commitExchange({
    assertionId: session.jti,
    assertionExpiresAt: now + 300,
    session,
  }, now), true);
  state.close();
  return session;
}

test('signed keyring binds generation to a pinned root and rejects tamper', () => {
  const root = mkdtempSync(join(tmpdir(), 'principia-revocation-keyring-root-'));
  try {
    const rootKey = keyPair(root, 'root');
    const wrongRoot = keyPair(root, 'wrong-root');
    const requestKey = keyPair(root, 'request');
    const keyring = buildKeyring(root, rootKey, [requestKey], 7, 'generation-7');
    const request = writeRequest(root, requestKey, 'request.json');

    assert.equal(keyring.result.generation, 7);
    assert.equal(keyring.result.root_key_id, rootKey.keyId);
    assert.deepEqual(keyring.result.key_ids, [requestKey.keyId]);
    assert.equal(keyring.evidence.includes(externalSubject), false);
    assert.equal(keyring.evidence.includes(issuer), false);
    assert.equal(lstatSync(keyring.output).mode & 0o333, 0);

    const parsed = readOidcRevocationRequestWithSignedKeyring(
      request,
      keyring.output,
      rootKey.publicPath,
      now,
    );
    assert.equal(parsed.keyId, requestKey.keyId);
    assert.equal(parsed.keyringGeneration, 7);
    assert.equal(parsed.rootKeyId, rootKey.keyId);

    assert.throws(() => readOidcRevocationRequestWithSignedKeyring(
      request,
      keyring.output,
      wrongRoot.publicPath,
      now,
    ), /root key identifier/);

    const tampered = JSON.parse(readFileSync(keyring.output, 'utf8'));
    tampered.generation = 8;
    const tamperedPath = writeJson(root, 'tampered.json', tampered, 0o444);
    assert.throws(() => readOidcRevocationRequestWithSignedKeyring(
      request,
      tamperedPath,
      rootKey.publicPath,
      now,
    ), /signature verification/);

    const unsignedLegacy = writeJson(root, 'unsigned-legacy.json', {
      contract: 'principia-atlas-hosted-oidc-revocation-keyring/0.1',
      keys: [],
      revoked_key_ids: [],
    }, 0o444);
    assert.throws(() => readOidcRevocationRequestWithSignedKeyring(
      request,
      unsignedLegacy,
      rootKey.publicPath,
      now,
    ), /fields|contract/);

    chmodSync(keyring.output, 0o644);
    assert.throws(() => readOidcRevocationRequestWithSignedKeyring(
      request,
      keyring.output,
      rootKey.publicPath,
      now,
    ), /permissions/);
    chmodSync(keyring.output, 0o444);
    const rootLink = join(root, 'root-link.der');
    symlinkSync(rootKey.publicPath, rootLink);
    assert.throws(() => readOidcRevocationRequestWithSignedKeyring(
      request,
      keyring.output,
      rootLink,
      now,
    ), /regular file/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('state rejects keyring rollback and preserves the first authorization generation', () => {
  const root = mkdtempSync(join(tmpdir(), 'principia-revocation-keyring-generation-'));
  try {
    const rootKey = keyPair(root, 'root');
    const requestKey = keyPair(root, 'request');
    const generation1 = buildKeyring(root, rootKey, [requestKey], 1, 'generation-1');
    const generation2 = buildKeyring(root, rootKey, [requestKey], 2, 'generation-2');
    const generation3 = buildKeyring(root, rootKey, [requestKey], 3, 'generation-3');
    const request = writeRequest(root, requestKey, 'request.json');
    const statePath = join(root, 'auth-state.sqlite');
    const subject = canonicalOidcSubject(issuer, externalSubject);
    const session = seedState(statePath, subject);

    const command = (keyringPath, requestPath = request, targetState = statePath) => [
      'revoke-oidc-request',
      '--state', targetState,
      '--request-file', requestPath,
      '--request-keyring-file', keyringPath,
      '--keyring-root-key-file', rootKey.publicPath,
    ];
    const argvEvidence = command(generation1.output).join('\u0000');
    assert.equal(argvEvidence.includes(externalSubject), false);
    assert.equal(argvEvidence.includes(issuer), false);

    let firstOutput = '';
    const first = authStateCommand([
      ...command(generation1.output),
      '--now', String(now),
    ], (value) => { firstOutput += value; });
    assert.equal(first.verified_keyring_generation, 1);
    assert.equal(first.verified_keyring_root_id, rootKey.keyId);
    assert.equal(first.authorization_keyring_generation, 1);
    assert.equal(first.authorization_key_id, requestKey.keyId);
    assert.equal(first.replayed, false);
    assert.equal(first.revoked_sessions, 1);
    assert.equal(firstOutput.includes(externalSubject), false);
    assert.equal(firstOutput.includes(issuer), false);

    const retry = authStateCommand([
      ...command(generation2.output),
      '--now', String(now + 1),
    ], () => {});
    assert.equal(retry.verified_keyring_generation, 2);
    assert.equal(retry.authorization_keyring_generation, 1);
    assert.equal(retry.replayed, true);
    assert.equal(retry.created_at, first.created_at);
    assert.equal(retry.expires_at, first.expires_at);
    assert.equal(readMinimumOidcRevocationKeyringGeneration(statePath), 2);

    assert.throws(() => authStateCommand([
      ...command(generation1.output),
      '--now', String(now + 2),
    ], () => {}), /rollback detected/);
    assert.throws(() => authStateCommand([
      'revoke-oidc-request',
      '--state', statePath,
      '--request-file', request,
      '--request-key-file', requestKey.publicPath,
      '--now', String(now + 2),
    ], () => {}), /single-key trust source is disabled/);

    const mismatchedRequest = writeRequest(root, requestKey, 'mismatched.json', {
      external_subject: 'different-anti-rollback-learner',
      issued_at: now,
      expires_at: now + 120,
    });
    assert.throws(() => authStateCommand([
      ...command(generation3.output, mismatchedRequest),
      '--now', String(now + 2),
    ], () => {}), /target mismatch/);
    assert.equal(readMinimumOidcRevocationKeyringGeneration(statePath), 2);

    const generation3Retry = authStateCommand([
      ...command(generation3.output),
      '--now', String(now + 3),
    ], () => {});
    assert.equal(generation3Retry.verified_keyring_generation, 3);
    assert.equal(generation3Retry.authorization_keyring_generation, 1);
    assert.equal(readMinimumOidcRevocationKeyringGeneration(statePath), 3);

    const state = openSqliteAuthState(statePath);
    assert.equal(state.validateSession(session, now + 4), false);
    state.close();

    const backupPath = join(root, 'auth-state.backup.sqlite');
    backupAuthState(statePath, backupPath);
    const restoredPath = join(root, 'auth-state.restored.sqlite');
    restoreAuthState(backupPath, restoredPath, 'ALL_INSTANCES_STOPPED');
    assert.equal(readMinimumOidcRevocationKeyringGeneration(restoredPath), 3);
    assert.throws(() => authStateCommand([
      ...command(generation2.output, request, restoredPath),
      '--now', String(now + 4),
    ], () => {}), /rollback detected/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
