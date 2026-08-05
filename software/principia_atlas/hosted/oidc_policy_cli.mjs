#!/usr/bin/env node
import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import {
  canonicalJson,
  createFileOidcJwksProvider,
  parseStrictJson,
  sealOidcPolicy,
  verifyOidcPolicy,
} from './index.mjs';

function parseArgs(argv) {
  const command = argv[0];
  const output = { command };
  for (let index = 1; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith('--') || !value) throw new Error('invalid OIDC policy arguments');
    output[key.slice(2)] = value;
  }
  return output;
}

async function load(path, label) {
  return parseStrictJson(await readFile(resolve(path)), label);
}

export async function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  let result;
  if (args.command === 'seal' && args.input && args.output) {
    const unsigned = await load(args.input, 'OIDC policy unsigned input');
    const policy = sealOidcPolicy(unsigned);
    await writeFile(resolve(args.output), canonicalJson(policy), { mode: 0o600, flag: 'wx' });
    result = { contract: policy.contract, operation: 'seal', output: resolve(args.output), policy_id: policy.policy_id, status: 'ok' };
  } else if (args.command === 'verify' && args.policy) {
    const policy = verifyOidcPolicy(await load(args.policy, 'OIDC policy'));
    if (args.jwks) {
      const provider = await createFileOidcJwksProvider(args.jwks, policy);
      await provider.initialize();
      result = { contract: policy.contract, operation: 'verify', policy_id: policy.policy_id, jwks: provider.health(), status: 'ok' };
    } else {
      result = { contract: policy.contract, operation: 'verify', policy_id: policy.policy_id, status: 'ok' };
    }
  } else {
    throw new Error('usage: seal --input FILE --output FILE | verify --policy FILE [--jwks FILE]');
  }
  process.stdout.write(canonicalJson(result));
  return result;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => { console.error(error.message); process.exitCode = 1; });
}
