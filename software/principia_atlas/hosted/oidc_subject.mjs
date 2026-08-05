import { createHash } from 'node:crypto';

import { fail } from './strict_json.mjs';

const MAX_EXTERNAL_SUBJECT_BYTES = 512;
const CONTROL_CHARACTERS = /[\u0000-\u001f\u007f]/;

function canonicalIssuer(value) {
  let url;
  try { url = new URL(value); } catch { fail('OIDC issuer is invalid'); }
  if (url.protocol !== 'https:' || url.username || url.password || url.hash || url.search) fail('OIDC issuer must be an HTTPS URL without credentials, query, or fragment');
  if (url.pathname.length > 1 && url.pathname.endsWith('/')) fail('OIDC issuer boundary is invalid');
  if (url.hostname === 'localhost' || url.hostname.endsWith('.localhost') || /^\d+\.\d+\.\d+\.\d+$/.test(url.hostname) || url.hostname.includes(':')) fail('OIDC issuer host is invalid');
  return value;
}

export function canonicalOidcSubject(issuerInput, subjectInput) {
  const issuer = canonicalIssuer(issuerInput);
  if (typeof subjectInput !== 'string' || subjectInput.length === 0 || Buffer.byteLength(subjectInput) > MAX_EXTERNAL_SUBJECT_BYTES || CONTROL_CHARACTERS.test(subjectInput)) fail('OIDC subject claim is invalid');
  return `oidc:${createHash('sha256').update(`${issuer}\u0000${subjectInput}`).digest('base64url')}`;
}
