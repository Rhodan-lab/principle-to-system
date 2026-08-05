#!/usr/bin/env node
import { readFile, writeFile } from 'node:fs/promises';
import { stdin, stdout } from 'node:process';
import { resolve } from 'node:path';
import {
  createStaticOidcJwksProvider,
  createOidcVerifier,
  mintOidcIdentityAssertion,
  sealOidcPolicy,
  verifyOidcPolicy,
  verifyOidcTenantCompatibility,
} from './oidc.mjs';
import { readSecretFile } from './secrets.mjs';
import { canonicalJson, fail, parseStrictJson } from './strict_json.mjs';

const MAX_STDIN_BYTES = 32770;

function parseArgs(argv) {
  const output = { command: argv[0] };
  for (let index = 1; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith('--') || !value || key in output) fail('OIDC CLI arguments are invalid');
    output[key.slice(2)] = value;
  }
  return output;
}

async function jsonFile(pathInput, label) {
  if (typeof pathInput !== 'string' || pathInput.length === 0) fail(`${label} path is required`);
  return parseStrictJson(await readFile(resolve(pathInput)), label);
}

async function readTokenFromStdin() {
  const chunks = [];
  let total = 0;
  for await (const chunk of stdin) {
    total += chunk.length;
    if (total > MAX_STDIN_BYTES) fail('OIDC token exceeds resource limit');
    chunks.push(Buffer.from(chunk));
  }
  let value = Buffer.concat(chunks).toString('utf8');
  if (value.endsWith('\r\n')) value = value.slice(0, -2);
  else if (value.endsWith('\n')) value = value.slice(0, -1);
  if (!value || /[\u0000-\u001f\u007f]/.test(value)) fail('OIDC token stdin is invalid');
  return value;
}

export async function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  if (args.command === 'seal-policy') {
    const unsigned = await jsonFile(args.input, 'OIDC unsigned policy');
    const sealed = sealOidcPolicy(unsigned);
    verifyOidcPolicy(sealed);
    const raw = canonicalJson(sealed);
    if (args.output) await writeFile(resolve(args.output), raw, { flag: 'wx', mode: 0o600 });
    else stdout.write(raw);
    return Object.freeze({ operation: 'seal-policy', policy_id: sealed.policy_id });
  }
  if (!['verify', 'adapt'].includes(args.command)) fail('usage: seal-policy --input PATH [--output PATH] | verify --policy PATH --jwks PATH --tenants PATH | adapt --policy PATH --jwks PATH --tenants PATH --identity-secret-file PATH');
  const policy = await jsonFile(args.policy, 'OIDC policy');
  const jwks = await jsonFile(args.jwks, 'OIDC JWKS');
  const tenants = await jsonFile(args.tenants, 'tenant config');
  const compatible = verifyOidcTenantCompatibility(policy, tenants);
  const provider = createStaticOidcJwksProvider(jwks, compatible.policy);
  const verifier = createOidcVerifier({ policy: compatible.policy, provider });
  await verifier.initialize();
  if (args.command === 'verify') {
    const result = {
      status: 'ok',
      policy_id: compatible.policy.policy_id,
      provider: provider.health(),
      tenant_count: Object.keys(compatible.config.tenants).length,
    };
    stdout.write(canonicalJson(result));
    return Object.freeze(result);
  }
  if (!args['identity-secret-file']) fail('OIDC identity secret file is required');
  const identitySecret = readSecretFile(args['identity-secret-file'], 'identity secret');
  try {
    const principal = await verifier.verify(await readTokenFromStdin());
    const assertion = mintOidcIdentityAssertion(principal, identitySecret, compatible.config, compatible.policy);
    stdout.write(`${assertion}\n`);
    return Object.freeze({ operation: 'adapt', policy_id: compatible.policy.policy_id });
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
