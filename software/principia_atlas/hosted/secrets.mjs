import { lstatSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fail } from './strict_json.mjs';

function boundedInteger(value, label, minimum, maximum) {
  if (!Number.isSafeInteger(value) || value < minimum || value > maximum) fail(`${label} is invalid`);
  return value;
}

export function readSecretFile(pathInput, label, { minBytes = 32, maxBytes = 4096 } = {}) {
  boundedInteger(minBytes, `${label} minimum length`, 1, 65536);
  boundedInteger(maxBytes, `${label} maximum length`, minBytes, 65536);
  if (typeof pathInput !== 'string' || pathInput.length === 0) fail(`${label} path is required`);
  const path = resolve(pathInput);
  const stats = lstatSync(path);
  if (stats.isSymbolicLink() || !stats.isFile()) fail(`${label} must be a regular file`);
  if ((stats.mode & 0o111) !== 0 || (stats.mode & 0o027) !== 0) fail(`${label} permissions are too broad`);
  const raw = readFileSync(path);
  if (raw.length > maxBytes + 2) fail(`${label} exceeds resource limit`);
  let end = raw.length;
  if (end > 0 && raw[end - 1] === 0x0a) {
    end -= 1;
    if (end > 0 && raw[end - 1] === 0x0d) end -= 1;
  }
  const value = raw.subarray(0, end);
  if (value.length < minBytes || value.length > maxBytes) fail(`${label} length is invalid`);
  if (value.includes(0x00) || value.includes(0x0a) || value.includes(0x0d)) fail(`${label} contains an invalid byte`);
  return Buffer.from(value);
}
