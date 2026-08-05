import { createHash } from 'node:crypto';

const MAX_JSON_BYTES = 2 * 1024 * 1024;
const UTF8 = new TextDecoder('utf-8', { fatal: true });
const RESERVED_KEYS = new Set(['__proto__', 'prototype', 'constructor']);

export function fail(message) {
  throw new Error(message);
}

export function sha256Hex(raw) {
  return createHash('sha256').update(raw).digest('hex');
}

function canonicalValue(value) {
  if (value === null || typeof value === 'boolean' || typeof value === 'string') return value;
  if (typeof value === 'number') {
    if (!Number.isSafeInteger(value)) fail('canonical JSON only permits safe integers');
    return value;
  }
  if (Array.isArray(value)) return value.map(canonicalValue);
  if (typeof value === 'object') {
    const output = {};
    for (const key of Object.keys(value).sort()) {
      if (RESERVED_KEYS.has(key)) fail('canonical JSON contains a reserved object key');
      output[key] = canonicalValue(value[key]);
    }
    return output;
  }
  fail('canonical JSON contains an unsupported value');
}

export function canonicalJson(value) {
  return `${JSON.stringify(canonicalValue(value))}\n`;
}

export function parseStrictJson(raw, label = 'JSON') {
  let text;
  try {
    if (Buffer.isBuffer(raw) || raw instanceof Uint8Array) {
      if (raw.byteLength > MAX_JSON_BYTES) fail(`${label} exceeds resource limit`);
      text = UTF8.decode(raw);
    } else {
      text = String(raw);
      if (Buffer.byteLength(text, 'utf8') > MAX_JSON_BYTES) fail(`${label} exceeds resource limit`);
    }
  } catch (error) {
    if (error instanceof Error && error.message.includes('resource limit')) throw error;
    fail(`${label} is not valid UTF-8`);
  }
  let index = 0;
  const whitespace = () => { while (/\s/.test(text[index] ?? '')) index += 1; };
  const parseString = () => {
    if (text[index] !== '"') fail(`${label} contains invalid JSON`);
    const start = index++;
    while (index < text.length) {
      const char = text[index++];
      if (char === '"') {
        try { return JSON.parse(text.slice(start, index)); }
        catch { fail(`${label} contains invalid JSON string`); }
      }
      if (char === '\\') {
        if (index >= text.length) fail(`${label} contains invalid JSON escape`);
        const escaped = text[index++];
        if (escaped === 'u') {
          const digits = text.slice(index, index + 4);
          if (!/^[0-9a-fA-F]{4}$/.test(digits)) fail(`${label} contains invalid Unicode escape`);
          index += 4;
        } else if (!'"\\/bfnrt'.includes(escaped)) fail(`${label} contains invalid JSON escape`);
      } else if (char.charCodeAt(0) < 0x20) fail(`${label} contains a control character`);
    }
    fail(`${label} contains an unterminated string`);
  };
  const parseNumber = () => {
    const match = text.slice(index).match(/^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/);
    if (!match) fail(`${label} contains invalid number`);
    index += match[0].length;
    const value = Number(match[0]);
    if (!Number.isFinite(value)) fail(`${label} contains non-finite number`);
    return value;
  };
  const parseValue = () => {
    whitespace();
    const char = text[index];
    if (char === '"') return parseString();
    if (char === '{') {
      index += 1; whitespace();
      const object = {}; const keys = new Set();
      if (text[index] === '}') { index += 1; return object; }
      while (true) {
        whitespace(); const key = parseString();
        if (RESERVED_KEYS.has(key)) fail(`${label} contains reserved object key: ${key}`);
        if (keys.has(key)) fail(`${label} contains duplicate key: ${key}`);
        keys.add(key); whitespace();
        if (text[index++] !== ':') fail(`${label} contains invalid object separator`);
        object[key] = parseValue(); whitespace();
        if (text[index] === '}') { index += 1; return object; }
        if (text[index++] !== ',') fail(`${label} contains invalid object delimiter`);
      }
    }
    if (char === '[') {
      index += 1; whitespace(); const array = [];
      if (text[index] === ']') { index += 1; return array; }
      while (true) {
        array.push(parseValue()); whitespace();
        if (text[index] === ']') { index += 1; return array; }
        if (text[index++] !== ',') fail(`${label} contains invalid array delimiter`);
      }
    }
    if (text.startsWith('true', index)) { index += 4; return true; }
    if (text.startsWith('false', index)) { index += 5; return false; }
    if (text.startsWith('null', index)) { index += 4; return null; }
    if (char === '-' || /\d/.test(char ?? '')) return parseNumber();
    fail(`${label} contains invalid JSON token`);
  };
  const value = parseValue(); whitespace();
  if (index !== text.length) fail(`${label} contains trailing content`);
  return value;
}

export function exactKeys(value, expected, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail(`${label} must be an object`);
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (JSON.stringify(actual) !== JSON.stringify(wanted)) fail(`${label} fields are invalid`);
}
