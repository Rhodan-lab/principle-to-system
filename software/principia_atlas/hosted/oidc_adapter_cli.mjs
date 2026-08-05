#!/usr/bin/env node
import { readFile } from 'node:fs/promises';
import { stdin, stdout } from 'node:process';
import { adaptOidcJwt, verifyOidcAdapterConfig, verifyOidcJwksSnapshot } from './oidc_adapter.mjs';
import { readSecretFile } from './secrets.mjs';
import { fail, parseStrictJson } from './strict_json.mjs';

const MAX_STDIN_BYTES = 16 * 1024 + 2;

function parseArgs(argv) {
  const command = argv[0];
  const output = { command };
  for (let index = 1; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith('--') || !value) fail('OIDC adapter arguments are invalid');
    output[key.slice(2)] = value;
  }
  return output;
}

async function jsonFile(path, label) {
  if (!path) fail(`${label} path is required`);
  return parseStrictJson(await readFile(path), label);
}

async function stdinToken() {
  const chunks = [];
  let size = 0;
  for await (const chunk of stdin) {
    size += chunk.length;
    if (size > MAX_STDIN_BYTES) fail('OIDC token exceeds resource limit');
    chunks.push(chunk);
  }
  let token = Buffer.concat(chunks).toString('utf8');
  if (token.endsWith('\r\n')) token = token.slice(0, -2);
  else if (token.endsWith('\n')) token = token.slice(0, -1);
  if (!token || /[\r\n\u0000]/.test(token)) fail('OIDC token stdin is invalid');
  return token;
}

export async function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  const config = await jsonFile(args.config, 'OIDC adapter config');
  const jwks = await jsonFile(args.jwks, 'OIDC JWKS snapshot');
  if (args.command === 'verify') {
    const verifiedConfig = verifyOidcAdapterConfig(config);
    const verifiedJwks = verifyOidcJwksSnapshot(jwks);
    stdout.write(`${JSON.stringify({ status: 'ok', config_id: verifiedConfig.config_id, snapshot_id: verifiedJwks.snapshot_id })}\n`);
    return;
  }
  if (args.command !== 'adapt' || !args.tenants || !args['identity-secret-file']) {
    fail('usage: verify --config PATH --jwks PATH | adapt --config PATH --jwks PATH --tenants PATH --identity-secret-file PATH');
  }
  const tenantConfig = await jsonFile(args.tenants, 'tenant config');
  const identitySecret = readSecretFile(args['identity-secret-file'], 'identity secret');
  try {
    const adapted = adaptOidcJwt({
      token: await stdinToken(),
      jwks,
      adapterConfig: config,
      tenantConfig,
      identitySecret,
    });
    stdout.write(`${adapted.assertion}\n`);
  } finally {
    identitySecret.fill(0);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}
