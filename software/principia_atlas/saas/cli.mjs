#!/usr/bin/env node
import { readFileSync } from 'node:fs';

import { canonicalJson, exactKeys, fail, parseStrictJson } from '../hosted/strict_json.mjs';
import { openSaasControlPlane } from './store.mjs';

const COMMAND_CONTRACT = 'principia-atlas-saas-control-plane-command/0.1';
const COMMANDS = new Set([
  'bootstrap', 'bind-tenant', 'add-member', 'grant-entitlement',
  'record-progress', 'dashboard', 'health',
]);
const FLAGS = new Set(['--state', '--actor', '--now']);
const INPUT_COMMANDS = new Set(['bootstrap', 'bind-tenant', 'add-member', 'grant-entitlement', 'record-progress']);
const MAX_INPUT_BYTES = 32 * 1024;

function parseArgs(argv) {
  const [command, ...rest] = argv;
  if (!COMMANDS.has(command)) fail('SaaS command is invalid');
  const output = { command, now: Math.floor(Date.now() / 1000) };
  const seen = new Set();
  for (let index = 0; index < rest.length; index += 1) {
    const flag = rest[index];
    if (!FLAGS.has(flag) || seen.has(flag)) fail(`unknown or duplicate argument: ${flag}`);
    seen.add(flag);
    const value = rest[++index];
    if (!value) fail(`${flag} requires a value`);
    output[flag.slice(2)] = value;
  }
  if (!output.state) fail('--state is required');
  output.now = Number(output.now);
  if (!Number.isSafeInteger(output.now) || output.now < 0) fail('--now is invalid');
  if (command !== 'bootstrap' && command !== 'health' && !output.actor) fail('--actor is required');
  if ((command === 'bootstrap' || command === 'health') && output.actor) fail(`${command} does not accept --actor`);
  return output;
}

function readInput(read = () => readFileSync(0)) {
  const raw = read();
  if (!Buffer.isBuffer(raw) && !(raw instanceof Uint8Array)) fail('SaaS command input is invalid');
  if (raw.byteLength < 2 || raw.byteLength > MAX_INPUT_BYTES) fail('SaaS command input size is invalid');
  return parseStrictJson(raw, 'SaaS command input');
}

export function main(
  argv = process.argv.slice(2),
  read = () => readFileSync(0),
  write = (value) => process.stdout.write(value),
) {
  const args = parseArgs(argv);
  const input = INPUT_COMMANDS.has(args.command) ? readInput(read) : null;
  const state = openSaasControlPlane(args.state);
  try {
    let result;
    if (args.command === 'bootstrap') {
      exactKeys(input, ['organization', 'owner'], 'SaaS bootstrap input');
      result = state.bootstrapOrganization(input.organization, input.owner, args.now);
    } else if (args.command === 'bind-tenant') {
      result = state.bindHostedTenant(args.actor, input, args.now);
    } else if (args.command === 'add-member') {
      result = state.addMembership(args.actor, input, args.now);
    } else if (args.command === 'grant-entitlement') {
      result = state.grantEntitlement(args.actor, input, args.now);
    } else if (args.command === 'record-progress') {
      result = state.recordProgress(args.actor, input, args.now);
    } else if (args.command === 'dashboard') {
      result = state.dashboard(args.actor, args.now);
    } else {
      result = state.health();
    }
    const output = Object.freeze({ contract: COMMAND_CONTRACT, command: args.command, result });
    write(canonicalJson(output));
    return output;
  } finally {
    state.close();
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try { main(); }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
