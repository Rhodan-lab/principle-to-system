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
import { exactKeys, fail, parseStrictJson } from './strict_json.mjs';

export const OIDC_REVOCATION_REQUEST_CONTRACT = 'principia-atlas-hosted-oidc-revocation-request/0.1';
const REQUEST_FIELDS = [
  'contract',
  'tenant_id',
  'issuer',
  'external_subject',
  'event_id',
  'issued_at',
  'expires_at',
  'receipt_ttl_seconds',
];
const TENANT_ID = /^[a-z][a-z0-9-]{1,62}$/;
const EVENT_ID = /^[A-Za-z0-9._:@+-]{16,200}$/;
const MAX_REQUEST_BYTES = 8192;
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

function permissionsAreBroad(mode) {
  return (mode & 0o111n) !== 0n || (mode & 0o027n) !== 0n;
}

function metadataChanged(before, after) {
  return before.dev !== after.dev
    || before.ino !== after.ino
    || before.size !== after.size
    || before.mode !== after.mode
    || before.mtimeNs !== after.mtimeNs
    || before.ctimeNs !== after.ctimeNs;
}

function readRequestFile(pathInput) {
  if (typeof pathInput !== 'string' || pathInput.length === 0) fail('OIDC revocation request path is required');
  const path = resolve(pathInput);
  const before = lstatSync(path, { bigint: true });
  if (before.isSymbolicLink() || !before.isFile()) fail('OIDC revocation request must be a regular file');
  if (permissionsAreBroad(before.mode)) fail('OIDC revocation request permissions are too broad');
  if (before.size < 2n || before.size > BigInt(MAX_REQUEST_BYTES)) fail('OIDC revocation request size is invalid');

  let descriptor;
  try {
    descriptor = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
    const opened = fstatSync(descriptor, { bigint: true });
    if (!opened.isFile() || opened.dev !== before.dev || opened.ino !== before.ino) fail('OIDC revocation request file changed during validation');
    if (permissionsAreBroad(opened.mode)) fail('OIDC revocation request permissions are too broad');
    if (opened.size < 2n || opened.size > BigInt(MAX_REQUEST_BYTES)) fail('OIDC revocation request size is invalid');
    const raw = readFileSync(descriptor);
    const after = fstatSync(descriptor, { bigint: true });
    if (raw.length !== Number(opened.size) || metadataChanged(opened, after)) fail('OIDC revocation request file changed during read');
    return raw;
  } catch (error) {
    if (error?.code === 'ELOOP') fail('OIDC revocation request must be a regular file');
    throw error;
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
  }
}

export function readOidcRevocationRequest(pathInput, nowSeconds = Math.floor(Date.now() / 1000)) {
  const now = integer(nowSeconds, 'current time', 0);
  const value = parseStrictJson(readRequestFile(pathInput), 'OIDC revocation request');
  exactKeys(value, REQUEST_FIELDS, 'OIDC revocation request');
  if (value.contract !== OIDC_REVOCATION_REQUEST_CONTRACT) fail('OIDC revocation request contract is incompatible');

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

  return Object.freeze({
    tenantId,
    subject: canonicalOidcSubject(value.issuer, value.external_subject),
    eventId,
    issuedAt,
    expiresAt,
    receiptTtlSeconds,
  });
}
