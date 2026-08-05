#!/usr/bin/env node
import { writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

import {
  revocationPublicKeyIdFromFile,
  signOidcRevocationRequestFile,
} from './revocation_request.mjs';
import { signOidcRevocationKeyringDraftFile } from './revocation_keyring.mjs';
import { canonicalJson, fail } from './strict_json.mjs';

const COMMAND_CONTRACT = 'principia-atlas-hosted-oidc-revocation-request-command/0.1';
const COMMANDS = new Set(['sign', 'key-id', 'keyring']);
const FLAGS = new Set([
  '--input',
  '--private-key-file',
  '--public-key-file',
  '--root-private-key-file',
  '--output',
]);

function parseArgs(argv) {
  const [command, ...rest] = argv;
  if (!COMMANDS.has(command)) fail('command must be sign, key-id, or keyring');
  const output = { command };
  const seen = new Set();
  for (let index = 0; index < rest.length; index += 1) {
    const item = rest[index];
    if (!FLAGS.has(item) || seen.has(item)) fail(`unknown or duplicate argument: ${item}`);
    seen.add(item);
    const value = rest[++index];
    if (!value) fail(`${item} requires a value`);
    output[item.slice(2)] = value;
  }
  if (command === 'sign') {
    if (!output.input || !output['private-key-file'] || !output.output) fail('sign requires --input, --private-key-file, and --output');
    if (output['public-key-file'] || output['root-private-key-file']) fail('sign only accepts --input, --private-key-file, and --output');
  } else if (command === 'key-id') {
    if (!output['public-key-file']) fail('key-id requires --public-key-file');
    if (output.input || output['private-key-file'] || output['root-private-key-file'] || output.output) fail('key-id only accepts --public-key-file');
  } else {
    if (!output.input || !output['root-private-key-file'] || !output.output) {
      fail('keyring requires --input, --root-private-key-file, and --output');
    }
    if (output['private-key-file'] || output['public-key-file']) {
      fail('keyring only accepts --input, --root-private-key-file, and --output');
    }
  }
  return output;
}

export function main(argv = process.argv.slice(2), write = (value) => process.stdout.write(value)) {
  const args = parseArgs(argv);
  if (args.command === 'key-id') {
    const result = {
      contract: COMMAND_CONTRACT,
      command: args.command,
      key_id: revocationPublicKeyIdFromFile(args['public-key-file']),
    };
    write(canonicalJson(result));
    return Object.freeze(result);
  }

  if (args.command === 'keyring') {
    const keyring = signOidcRevocationKeyringDraftFile(args.input, args['root-private-key-file']);
    writeFileSync(resolve(args.output), canonicalJson(keyring), { flag: 'wx', mode: 0o444 });
    const result = {
      contract: COMMAND_CONTRACT,
      command: args.command,
      generation: keyring.generation,
      root_key_id: keyring.root_key_id,
      key_ids: keyring.keys.map((entry) => entry.key_id),
      revoked_key_ids: keyring.revoked_key_ids,
    };
    write(canonicalJson(result));
    return Object.freeze(result);
  }

  const request = signOidcRevocationRequestFile(args.input, args['private-key-file']);
  writeFileSync(resolve(args.output), canonicalJson(request), { flag: 'wx', mode: 0o600 });
  const result = {
    contract: COMMAND_CONTRACT,
    command: args.command,
    event_id: request.event_id,
    key_id: request.key_id,
  };
  write(canonicalJson(result));
  return Object.freeze(result);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try { main(); }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
