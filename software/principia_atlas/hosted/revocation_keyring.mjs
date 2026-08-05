import {
  createHash,
  createPrivateKey,
  createPublicKey,
  sign,
  verify,
} from 'node:crypto';
import {
  closeSync,
  constants,
  fstatSync,
  lstatSync,
  openSync,
  readFileSync,
} from 'node:fs';
import { resolve } from 'node:path';

import { canonicalOidcSubject } from './oidc_subject.mjs';
import { canonicalJson, exactKeys, fail, parseStrictJson } from './strict_json.mjs';

export const OIDC_REVOCATION_KEYRING_DRAFT_CONTRACT = 'principia-atlas-hosted-oidc-revocation-keyring-draft/0.2';
export const OIDC_REVOCATION_KEYRING_CONTRACT = 'principia-atlas-hosted-oidc-revocation-keyring/0.2';
const OIDC_REVOCATION_REQUEST_CONTRACT = 'principia-atlas-hosted-oidc-revocation-request/0.2';
const KEYRING_SIGNATURE_DOMAIN = Buffer.from('principia-atlas-hosted-oidc-revocation-keyring-signature/0.1\u0000', 'utf8');
const REQUEST_SIGNATURE_DOMAIN = Buffer.from('principia-atlas-hosted-oidc-revocation-signature/0.1\u0000', 'utf8');
const KEYRING_DRAFT_FIELDS = ['contract', 'generation', 'keys', 'revoked_key_ids'];
const KEYRING_FIELDS = ['contract', 'generation', 'root_key_id', 'keys', 'revoked_key_ids', 'signature'];
const KEYRING_ENTRY_FIELDS = ['key_id', 'public_key_spki', 'not_before', 'not_after'];
const KEYRING_DRAFT_ENTRY_FIELDS = ['public_key_file', 'not_before', 'not_after'];
const REQUEST_FIELDS = [
  'contract', 'key_id', 'tenant_id', 'issuer', 'external_subject', 'event_id',
  'issued_at', 'expires_at', 'receipt_ttl_seconds', 'signature',
];
const KEY_ID = /^ed25519:[A-Za-z0-9_-]{43}$/;
const TENANT_ID = /^[a-z][a-z0-9-]{1,62}$/;
const EVENT_ID = /^[A-Za-z0-9._:@+-]{16,200}$/;
const SIGNATURE = /^[A-Za-z0-9_-]{86}$/;
const MAX_KEY_BYTES = 4096;
const MAX_KEYRING_BYTES = 65536;
const MAX_REQUEST_BYTES = 8192;
const MAX_KEYRING_KEYS = 16;
const MAX_REVOKED_KEYS = 64;
const MAX_KEY_LIFETIME_SECONDS = 5 * 366 * 24 * 60 * 60;
const MAX_REQUEST_LIFETIME_SECONDS = 300;
const MAX_FUTURE_SKEW_SECONDS = 30;
const MIN_RECEIPT_TTL_SECONDS = 60;
const MAX_RECEIPT_TTL_SECONDS = 365 * 24 * 60 * 60;

function integer(value, label, minimum, maximum = Number.MAX_SAFE_INTEGER) {
  if (!Number.isSafeInteger(value) || value < minimum || value > maximum) fail(`${label} is invalid`);
  return value;
}

function identifier(value, pattern, label) {
  if (typeof value !== 'string' || !pattern.test(value)) fail(`${label} is invalid`);
  return value;
}

function compareAscii(left, right) {
  if (left < right) return -1;
  if (left > right) return 1;
  return 0;
}

function privateFilePermissions(mode) {
  return (mode & 0o111n) === 0n && (mode & 0o027n) === 0n;
}

function publicConfigPermissions(mode) {
  return (mode & 0o333n) === 0n;
}

function metadataChanged(before, after) {
  return before.dev !== after.dev
    || before.ino !== after.ino
    || before.uid !== after.uid
    || before.gid !== after.gid
    || before.size !== after.size
    || before.mode !== after.mode
    || before.mtimeNs !== after.mtimeNs
    || before.ctimeNs !== after.ctimeNs;
}

function readSecureFile(pathInput, label, { minimum, maximum, permissions }) {
  if (typeof pathInput !== 'string' || pathInput.length === 0) fail(`${label} path is required`);
  const path = resolve(pathInput);
  const before = lstatSync(path, { bigint: true });
  if (before.isSymbolicLink() || !before.isFile()) fail(`${label} must be a regular file`);
  if (!permissions(before.mode)) fail(`${label} permissions are too broad`);
  if (before.size < BigInt(minimum) || before.size > BigInt(maximum)) fail(`${label} size is invalid`);
  let descriptor;
  try {
    descriptor = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
    const opened = fstatSync(descriptor, { bigint: true });
    if (!opened.isFile() || opened.dev !== before.dev || opened.ino !== before.ino) fail(`${label} file changed during validation`);
    if (!permissions(opened.mode)) fail(`${label} permissions are too broad`);
    if (opened.size < BigInt(minimum) || opened.size > BigInt(maximum)) fail(`${label} size is invalid`);
    const raw = readFileSync(descriptor);
    const after = fstatSync(descriptor, { bigint: true });
    if (raw.length !== Number(opened.size) || metadataChanged(opened, after)) fail(`${label} file changed during read`);
    return raw;
  } catch (error) {
    if (error?.code === 'ELOOP') fail(`${label} must be a regular file`);
    throw error;
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
  }
}

function privateJsonFile(pathInput, label, maximum = MAX_KEYRING_BYTES) {
  return readSecureFile(pathInput, label, { minimum: 2, maximum, permissions: privateFilePermissions });
}

function publicJsonFile(pathInput, label) {
  return readSecureFile(pathInput, label, { minimum: 2, maximum: MAX_KEYRING_BYTES, permissions: publicConfigPermissions });
}

function privateKeyFile(pathInput, label) {
  return readSecureFile(pathInput, label, { minimum: 32, maximum: MAX_KEY_BYTES, permissions: privateFilePermissions });
}

function publicKeyFile(pathInput, label) {
  return readSecureFile(pathInput, label, { minimum: 32, maximum: MAX_KEY_BYTES, permissions: publicConfigPermissions });
}

function ed25519PrivateKey(raw, label) {
  let key;
  try { key = createPrivateKey({ key: raw, format: 'der', type: 'pkcs8' }); }
  catch { fail(`${label} is invalid`); }
  if (key.asymmetricKeyType !== 'ed25519') fail(`${label} must use Ed25519`);
  return key;
}

function ed25519PublicKey(raw, label) {
  let key;
  try { key = createPublicKey({ key: raw, format: 'der', type: 'spki' }); }
  catch { fail(`${label} is invalid`); }
  if (key.asymmetricKeyType !== 'ed25519') fail(`${label} must use Ed25519`);
  return key;
}

function publicKeyId(key) {
  const raw = key.export({ format: 'der', type: 'spki' });
  return `ed25519:${createHash('sha256').update(raw).digest('base64url')}`;
}

function strictSignature(value, label) {
  identifier(value, SIGNATURE, `${label} signature`);
  const raw = Buffer.from(value, 'base64url');
  if (raw.length !== 64 || raw.toString('base64url') !== value) fail(`${label} signature is invalid`);
  return raw;
}

function strictPublicKeySpki(value, label) {
  if (typeof value !== 'string' || value.length === 0 || value.length > 1024 || !/^[A-Za-z0-9_-]+$/.test(value)) fail(`${label} public key is invalid`);
  const raw = Buffer.from(value, 'base64url');
  if (raw.length < 32 || raw.length > MAX_KEY_BYTES || raw.toString('base64url') !== value) fail(`${label} public key is invalid`);
  return { raw, key: ed25519PublicKey(raw, `${label} public key`) };
}

function validateKeyWindow(entry, label) {
  const notBefore = integer(entry.not_before, `${label} not-before`, 0);
  const notAfter = integer(entry.not_after, `${label} not-after`, 0);
  if (notAfter <= notBefore || notAfter - notBefore > MAX_KEY_LIFETIME_SECONDS) fail(`${label} validity window is invalid`);
  return { notBefore, notAfter };
}

function keyringUnsigned(value) {
  return {
    contract: OIDC_REVOCATION_KEYRING_CONTRACT,
    generation: value.generation,
    root_key_id: value.root_key_id,
    keys: value.keys,
    revoked_key_ids: value.revoked_key_ids,
  };
}

function keyringSignatureMessage(value) {
  return Buffer.concat([KEYRING_SIGNATURE_DOMAIN, Buffer.from(canonicalJson(keyringUnsigned(value)), 'utf8')]);
}

function requestUnsigned(value) {
  return {
    contract: OIDC_REVOCATION_REQUEST_CONTRACT,
    key_id: value.key_id,
    tenant_id: value.tenant_id,
    issuer: value.issuer,
    external_subject: value.external_subject,
    event_id: value.event_id,
    issued_at: value.issued_at,
    expires_at: value.expires_at,
    receipt_ttl_seconds: value.receipt_ttl_seconds,
  };
}

function requestSignatureMessage(value) {
  return Buffer.concat([REQUEST_SIGNATURE_DOMAIN, Buffer.from(canonicalJson(requestUnsigned(value)), 'utf8')]);
}

function validateRequestCore(value, now) {
  const tenantId = identifier(value.tenant_id, TENANT_ID, 'OIDC revocation request tenant');
  const eventId = identifier(value.event_id, EVENT_ID, 'OIDC revocation request event identifier');
  const issuedAt = integer(value.issued_at, 'OIDC revocation request issued time', 0);
  const expiresAt = integer(value.expires_at, 'OIDC revocation request expiry', 0);
  const receiptTtlSeconds = integer(
    value.receipt_ttl_seconds,
    'OIDC revocation request receipt TTL',
    MIN_RECEIPT_TTL_SECONDS,
    MAX_RECEIPT_TTL_SECONDS,
  );
  if (expiresAt <= issuedAt || expiresAt - issuedAt > MAX_REQUEST_LIFETIME_SECONDS) fail('OIDC revocation request lifetime is invalid');
  if (issuedAt > now + MAX_FUTURE_SKEW_SECONDS) fail('OIDC revocation request is not yet valid');
  if (expiresAt <= now) fail('OIDC revocation request is expired');
  return {
    tenantId,
    subject: canonicalOidcSubject(value.issuer, value.external_subject),
    eventId,
    issuedAt,
    expiresAt,
    receiptTtlSeconds,
  };
}

function buildKeyEntries(entries) {
  if (!Array.isArray(entries) || entries.length < 1 || entries.length > MAX_KEYRING_KEYS) fail('OIDC revocation keyring draft keys are invalid');
  const seen = new Set();
  return entries.map((entry, index) => {
    const label = `OIDC revocation keyring draft key ${index}`;
    exactKeys(entry, KEYRING_DRAFT_ENTRY_FIELDS, label);
    const window = validateKeyWindow(entry, label);
    const raw = publicKeyFile(entry.public_key_file, `${label} file`);
    const key = ed25519PublicKey(raw, label);
    const keyId = publicKeyId(key);
    if (seen.has(keyId)) fail('OIDC revocation keyring draft contains duplicate keys');
    seen.add(keyId);
    return {
      key_id: keyId,
      public_key_spki: Buffer.from(raw).toString('base64url'),
      not_before: window.notBefore,
      not_after: window.notAfter,
    };
  }).sort((left, right) => compareAscii(left.key_id, right.key_id));
}

function buildRevoked(values, label) {
  if (!Array.isArray(values) || values.length > MAX_REVOKED_KEYS) fail(`${label} revoked keys are invalid`);
  const revoked = values.map((value) => identifier(value, KEY_ID, `${label} revoked key identifier`));
  if (new Set(revoked).size !== revoked.length) fail(`${label} revoked keys contain duplicates`);
  return [...revoked].sort(compareAscii);
}

export function signOidcRevocationKeyringDraftFile(draftPath, rootPrivateKeyPath) {
  const draft = parseStrictJson(privateJsonFile(draftPath, 'OIDC revocation keyring draft'), 'OIDC revocation keyring draft');
  exactKeys(draft, KEYRING_DRAFT_FIELDS, 'OIDC revocation keyring draft');
  if (draft.contract !== OIDC_REVOCATION_KEYRING_DRAFT_CONTRACT) fail('OIDC revocation keyring draft contract is incompatible');
  const generation = integer(draft.generation, 'OIDC revocation keyring generation', 1);
  const keys = buildKeyEntries(draft.keys);
  const revokedKeyIds = buildRevoked(draft.revoked_key_ids, 'OIDC revocation keyring draft');
  const rootRaw = privateKeyFile(rootPrivateKeyPath, 'OIDC revocation keyring root private key');
  try {
    const rootPrivateKey = ed25519PrivateKey(rootRaw, 'OIDC revocation keyring root private key');
    const rootKeyId = publicKeyId(createPublicKey(rootPrivateKey));
    const unsigned = {
      contract: OIDC_REVOCATION_KEYRING_CONTRACT,
      generation,
      root_key_id: rootKeyId,
      keys,
      revoked_key_ids: revokedKeyIds,
    };
    return Object.freeze({
      ...unsigned,
      signature: sign(null, keyringSignatureMessage(unsigned), rootPrivateKey).toString('base64url'),
    });
  } finally {
    rootRaw.fill(0);
  }
}

export function readSignedOidcRevocationKeyring(keyringPath, rootPublicKeyPath) {
  const value = parseStrictJson(publicJsonFile(keyringPath, 'OIDC revocation keyring'), 'OIDC revocation keyring');
  exactKeys(value, KEYRING_FIELDS, 'OIDC revocation keyring');
  if (value.contract !== OIDC_REVOCATION_KEYRING_CONTRACT) fail('OIDC revocation keyring contract is incompatible');
  const generation = integer(value.generation, 'OIDC revocation keyring generation', 1);
  const rootKeyId = identifier(value.root_key_id, KEY_ID, 'OIDC revocation keyring root key identifier');
  const signature = strictSignature(value.signature, 'OIDC revocation keyring');
  const rootKey = ed25519PublicKey(
    publicKeyFile(rootPublicKeyPath, 'OIDC revocation keyring root public key'),
    'OIDC revocation keyring root public key',
  );
  if (rootKeyId !== publicKeyId(rootKey)) fail('OIDC revocation keyring root key identifier does not match pinned key');
  if (!verify(null, keyringSignatureMessage(value), rootKey, signature)) fail('OIDC revocation keyring signature verification failed');
  if (!Array.isArray(value.keys) || value.keys.length < 1 || value.keys.length > MAX_KEYRING_KEYS) fail('OIDC revocation keyring keys are invalid');
  const revoked = buildRevoked(value.revoked_key_ids, 'OIDC revocation keyring');
  const seen = new Set();
  const keys = new Map();
  for (let index = 0; index < value.keys.length; index += 1) {
    const entry = value.keys[index];
    const label = `OIDC revocation keyring key ${index}`;
    exactKeys(entry, KEYRING_ENTRY_FIELDS, label);
    const keyId = identifier(entry.key_id, KEY_ID, `${label} identifier`);
    const { key } = strictPublicKeySpki(entry.public_key_spki, label);
    if (keyId !== publicKeyId(key)) fail(`${label} identifier does not match public key`);
    const window = validateKeyWindow(entry, label);
    if (seen.has(keyId)) fail('OIDC revocation keyring contains duplicate keys');
    seen.add(keyId);
    keys.set(keyId, Object.freeze({ key, ...window }));
  }
  return Object.freeze({ generation, rootKeyId, keys, revoked: new Set(revoked) });
}

export function readOidcRevocationRequestWithSignedKeyring(
  requestPath,
  keyringPath,
  rootPublicKeyPath,
  nowSeconds = Math.floor(Date.now() / 1000),
) {
  const now = integer(nowSeconds, 'current time', 0);
  const value = parseStrictJson(
    privateJsonFile(requestPath, 'OIDC revocation request', MAX_REQUEST_BYTES),
    'OIDC revocation request',
  );
  exactKeys(value, REQUEST_FIELDS, 'OIDC revocation request');
  if (value.contract !== OIDC_REVOCATION_REQUEST_CONTRACT) fail('OIDC revocation request contract is incompatible');
  const keyId = identifier(value.key_id, KEY_ID, 'OIDC revocation request key identifier');
  const requestSignature = strictSignature(value.signature, 'OIDC revocation request');
  const keyring = readSignedOidcRevocationKeyring(keyringPath, rootPublicKeyPath);
  if (keyring.revoked.has(keyId)) fail('OIDC revocation request signing key is revoked');
  const trusted = keyring.keys.get(keyId);
  if (!trusted) fail('OIDC revocation request signing key is not trusted');
  const core = validateRequestCore(value, now);
  if (core.issuedAt < trusted.notBefore || core.issuedAt >= trusted.notAfter) fail('OIDC revocation request signing key is outside its validity window');
  if (!verify(null, requestSignatureMessage(value), trusted.key, requestSignature)) fail('OIDC revocation request signature verification failed');
  return Object.freeze({
    ...core,
    keyId,
    keyringGeneration: keyring.generation,
    rootKeyId: keyring.rootKeyId,
  });
}
