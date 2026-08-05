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

export const OIDC_REVOCATION_REQUEST_DRAFT_CONTRACT = 'principia-atlas-hosted-oidc-revocation-request-draft/0.1';
export const OIDC_REVOCATION_REQUEST_CONTRACT = 'principia-atlas-hosted-oidc-revocation-request/0.2';
export const OIDC_REVOCATION_KEYRING_DRAFT_CONTRACT = 'principia-atlas-hosted-oidc-revocation-keyring-draft/0.1';
export const OIDC_REVOCATION_KEYRING_CONTRACT = 'principia-atlas-hosted-oidc-revocation-keyring/0.1';
const SIGNATURE_DOMAIN = Buffer.from('principia-atlas-hosted-oidc-revocation-signature/0.1\u0000', 'utf8');
const CORE_FIELDS = [
  'tenant_id',
  'issuer',
  'external_subject',
  'event_id',
  'issued_at',
  'expires_at',
  'receipt_ttl_seconds',
];
const DRAFT_FIELDS = ['contract', ...CORE_FIELDS];
const SIGNED_FIELDS = ['contract', 'key_id', ...CORE_FIELDS, 'signature'];
const KEYRING_FIELDS = ['contract', 'keys', 'revoked_key_ids'];
const KEYRING_ENTRY_FIELDS = ['key_id', 'public_key_spki', 'not_before', 'not_after'];
const KEYRING_DRAFT_ENTRY_FIELDS = ['public_key_file', 'not_before', 'not_after'];
const TENANT_ID = /^[a-z][a-z0-9-]{1,62}$/;
const EVENT_ID = /^[A-Za-z0-9._:@+-]{16,200}$/;
const KEY_ID = /^ed25519:[A-Za-z0-9_-]{43}$/;
const SIGNATURE = /^[A-Za-z0-9_-]{86}$/;
const MAX_REQUEST_BYTES = 8192;
const MAX_KEY_BYTES = 4096;
const MAX_KEYRING_BYTES = 65536;
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

function requestFile(pathInput, label = 'OIDC revocation request') {
  return readSecureFile(pathInput, label, {
    minimum: 2,
    maximum: MAX_REQUEST_BYTES,
    permissions: privateFilePermissions,
  });
}

function privateKeyFile(pathInput) {
  return readSecureFile(pathInput, 'OIDC revocation private key', {
    minimum: 32,
    maximum: MAX_KEY_BYTES,
    permissions: privateFilePermissions,
  });
}

function publicKeyFile(pathInput) {
  return readSecureFile(pathInput, 'OIDC revocation public key', {
    minimum: 32,
    maximum: MAX_KEY_BYTES,
    permissions: publicConfigPermissions,
  });
}

function keyringFile(pathInput, label = 'OIDC revocation keyring') {
  return readSecureFile(pathInput, label, {
    minimum: 2,
    maximum: MAX_KEYRING_BYTES,
    permissions: publicConfigPermissions,
  });
}

function ed25519PrivateKey(raw) {
  let key;
  try { key = createPrivateKey({ key: raw, format: 'der', type: 'pkcs8' }); }
  catch { fail('OIDC revocation private key is invalid'); }
  if (key.asymmetricKeyType !== 'ed25519') fail('OIDC revocation private key must use Ed25519');
  return key;
}

function ed25519PublicKey(raw) {
  let key;
  try { key = createPublicKey({ key: raw, format: 'der', type: 'spki' }); }
  catch { fail('OIDC revocation public key is invalid'); }
  if (key.asymmetricKeyType !== 'ed25519') fail('OIDC revocation public key must use Ed25519');
  return key;
}

function publicKeyId(key) {
  const raw = key.export({ format: 'der', type: 'spki' });
  return `ed25519:${createHash('sha256').update(raw).digest('base64url')}`;
}

function signedPayload(value) {
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

function signatureMessage(value) {
  return Buffer.concat([SIGNATURE_DOMAIN, Buffer.from(canonicalJson(signedPayload(value)), 'utf8')]);
}

function validateCore(value, label, now = null) {
  const tenantId = identifier(value.tenant_id, TENANT_ID, `${label} tenant`);
  const eventId = identifier(value.event_id, EVENT_ID, `${label} event identifier`);
  const issuedAt = integer(value.issued_at, `${label} issued time`, 0);
  const expiresAt = integer(value.expires_at, `${label} expiry`, 0);
  const receiptTtlSeconds = integer(
    value.receipt_ttl_seconds,
    `${label} receipt TTL`,
    MIN_RECEIPT_TTL_SECONDS,
    MAX_RECEIPT_TTL_SECONDS,
  );
  if (expiresAt <= issuedAt || expiresAt - issuedAt > MAX_REQUEST_LIFETIME_SECONDS) fail(`${label} lifetime is invalid`);
  if (now !== null) {
    if (issuedAt > now + MAX_FUTURE_SKEW_SECONDS) fail(`${label} is not yet valid`);
    if (expiresAt <= now) fail(`${label} is expired`);
  }
  return Object.freeze({
    tenantId,
    subject: canonicalOidcSubject(value.issuer, value.external_subject),
    eventId,
    issuedAt,
    expiresAt,
    receiptTtlSeconds,
  });
}

function strictSignature(value) {
  identifier(value, SIGNATURE, 'OIDC revocation request signature');
  const raw = Buffer.from(value, 'base64url');
  if (raw.length !== 64 || raw.toString('base64url') !== value) fail('OIDC revocation request signature is invalid');
  return raw;
}

function parseSignedRequest(pathInput) {
  const value = parseStrictJson(requestFile(pathInput), 'OIDC revocation request');
  exactKeys(value, SIGNED_FIELDS, 'OIDC revocation request');
  if (value.contract !== OIDC_REVOCATION_REQUEST_CONTRACT) fail('OIDC revocation request contract is incompatible');
  identifier(value.key_id, KEY_ID, 'OIDC revocation request key identifier');
  return { value, signature: strictSignature(value.signature) };
}

function verifySignedRequest(parsed, publicKey, now) {
  if (parsed.value.key_id !== publicKeyId(publicKey)) fail('OIDC revocation request key identifier does not match verification key');
  if (!verify(null, signatureMessage(parsed.value), publicKey, parsed.signature)) fail('OIDC revocation request signature verification failed');
  return Object.freeze({
    ...validateCore(parsed.value, 'OIDC revocation request', now),
    keyId: parsed.value.key_id,
  });
}

function strictPublicKeySpki(value, label) {
  if (typeof value !== 'string' || value.length === 0 || value.length > 1024 || !/^[A-Za-z0-9_-]+$/.test(value)) fail(`${label} public key is invalid`);
  const raw = Buffer.from(value, 'base64url');
  if (raw.length < 32 || raw.length > MAX_KEY_BYTES || raw.toString('base64url') !== value) fail(`${label} public key is invalid`);
  return { raw, key: ed25519PublicKey(raw) };
}

function validateKeyWindow(entry, label) {
  const notBefore = integer(entry.not_before, `${label} not-before`, 0);
  const notAfter = integer(entry.not_after, `${label} not-after`, 0);
  if (notAfter <= notBefore || notAfter - notBefore > MAX_KEY_LIFETIME_SECONDS) fail(`${label} validity window is invalid`);
  return { notBefore, notAfter };
}

export function readOidcRevocationRequestDraft(pathInput) {
  const value = parseStrictJson(requestFile(pathInput, 'OIDC revocation request draft'), 'OIDC revocation request draft');
  exactKeys(value, DRAFT_FIELDS, 'OIDC revocation request draft');
  if (value.contract !== OIDC_REVOCATION_REQUEST_DRAFT_CONTRACT) fail('OIDC revocation request draft contract is incompatible');
  validateCore(value, 'OIDC revocation request draft');
  return Object.freeze(value);
}

export function signOidcRevocationRequest(draftInput, privateKeyInput) {
  exactKeys(draftInput, DRAFT_FIELDS, 'OIDC revocation request draft');
  if (draftInput.contract !== OIDC_REVOCATION_REQUEST_DRAFT_CONTRACT) fail('OIDC revocation request draft contract is incompatible');
  validateCore(draftInput, 'OIDC revocation request draft');
  const privateKey = Buffer.isBuffer(privateKeyInput) || privateKeyInput instanceof Uint8Array
    ? ed25519PrivateKey(privateKeyInput)
    : privateKeyInput;
  if (!privateKey || privateKey.asymmetricKeyType !== 'ed25519' || privateKey.type !== 'private') fail('OIDC revocation private key must use Ed25519');
  const keyId = publicKeyId(createPublicKey(privateKey));
  const unsigned = {
    contract: OIDC_REVOCATION_REQUEST_CONTRACT,
    key_id: keyId,
    tenant_id: draftInput.tenant_id,
    issuer: draftInput.issuer,
    external_subject: draftInput.external_subject,
    event_id: draftInput.event_id,
    issued_at: draftInput.issued_at,
    expires_at: draftInput.expires_at,
    receipt_ttl_seconds: draftInput.receipt_ttl_seconds,
  };
  return Object.freeze({
    ...unsigned,
    signature: sign(null, signatureMessage(unsigned), privateKey).toString('base64url'),
  });
}

export function signOidcRevocationRequestFile(draftPath, privateKeyPath) {
  const raw = privateKeyFile(privateKeyPath);
  try { return signOidcRevocationRequest(readOidcRevocationRequestDraft(draftPath), raw); }
  finally { raw.fill(0); }
}

export function revocationPublicKeyIdFromFile(publicKeyPath) {
  return publicKeyId(ed25519PublicKey(publicKeyFile(publicKeyPath)));
}

export function readOidcRevocationRequest(pathInput, publicKeyPath, nowSeconds = Math.floor(Date.now() / 1000)) {
  const now = integer(nowSeconds, 'current time', 0);
  return verifySignedRequest(parseSignedRequest(pathInput), ed25519PublicKey(publicKeyFile(publicKeyPath)), now);
}

export function createOidcRevocationKeyring(draftInput) {
  exactKeys(draftInput, KEYRING_FIELDS, 'OIDC revocation keyring draft');
  if (draftInput.contract !== OIDC_REVOCATION_KEYRING_DRAFT_CONTRACT) fail('OIDC revocation keyring draft contract is incompatible');
  if (!Array.isArray(draftInput.keys) || draftInput.keys.length < 1 || draftInput.keys.length > MAX_KEYRING_KEYS) fail('OIDC revocation keyring draft keys are invalid');
  if (!Array.isArray(draftInput.revoked_key_ids) || draftInput.revoked_key_ids.length > MAX_REVOKED_KEYS) fail('OIDC revocation keyring draft revoked keys are invalid');
  const revoked = draftInput.revoked_key_ids.map((value) => identifier(value, KEY_ID, 'OIDC revocation revoked key identifier'));
  if (new Set(revoked).size !== revoked.length) fail('OIDC revocation keyring draft revoked keys contain duplicates');
  const seen = new Set();
  const keys = draftInput.keys.map((entry, index) => {
    const label = `OIDC revocation keyring draft key ${index}`;
    exactKeys(entry, KEYRING_DRAFT_ENTRY_FIELDS, label);
    const window = validateKeyWindow(entry, label);
    const raw = publicKeyFile(entry.public_key_file);
    const key = ed25519PublicKey(raw);
    const keyId = publicKeyId(key);
    if (seen.has(keyId)) fail('OIDC revocation keyring draft contains duplicate keys');
    seen.add(keyId);
    return {
      key_id: keyId,
      public_key_spki: Buffer.from(raw).toString('base64url'),
      not_before: window.notBefore,
      not_after: window.notAfter,
    };
  }).sort((left, right) => left.key_id.localeCompare(right.key_id));
  return Object.freeze({
    contract: OIDC_REVOCATION_KEYRING_CONTRACT,
    keys,
    revoked_key_ids: [...revoked].sort(),
  });
}

export function readOidcRevocationKeyringDraft(pathInput) {
  const value = parseStrictJson(requestFile(pathInput, 'OIDC revocation keyring draft'), 'OIDC revocation keyring draft');
  return createOidcRevocationKeyring(value);
}

export function readOidcRevocationKeyring(pathInput) {
  const value = parseStrictJson(keyringFile(pathInput), 'OIDC revocation keyring');
  exactKeys(value, KEYRING_FIELDS, 'OIDC revocation keyring');
  if (value.contract !== OIDC_REVOCATION_KEYRING_CONTRACT) fail('OIDC revocation keyring contract is incompatible');
  if (!Array.isArray(value.keys) || value.keys.length < 1 || value.keys.length > MAX_KEYRING_KEYS) fail('OIDC revocation keyring keys are invalid');
  if (!Array.isArray(value.revoked_key_ids) || value.revoked_key_ids.length > MAX_REVOKED_KEYS) fail('OIDC revocation keyring revoked keys are invalid');
  const revoked = value.revoked_key_ids.map((item) => identifier(item, KEY_ID, 'OIDC revocation revoked key identifier'));
  if (new Set(revoked).size !== revoked.length) fail('OIDC revocation keyring revoked keys contain duplicates');
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
  return Object.freeze({ keys, revoked: new Set(revoked) });
}

export function readOidcRevocationRequestWithKeyring(pathInput, keyringPath, nowSeconds = Math.floor(Date.now() / 1000)) {
  const now = integer(nowSeconds, 'current time', 0);
  const parsed = parseSignedRequest(pathInput);
  const keyring = readOidcRevocationKeyring(keyringPath);
  if (keyring.revoked.has(parsed.value.key_id)) fail('OIDC revocation request signing key is revoked');
  const trusted = keyring.keys.get(parsed.value.key_id);
  if (!trusted) fail('OIDC revocation request signing key is not trusted');
  const issuedAt = integer(parsed.value.issued_at, 'OIDC revocation request issued time', 0);
  if (issuedAt < trusted.notBefore || issuedAt >= trusted.notAfter) fail('OIDC revocation request signing key is outside its validity window');
  return verifySignedRequest(parsed, trusted.key, now);
}
