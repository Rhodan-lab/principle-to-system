#!/usr/bin/env node
import { canonicalJson } from './strict_json.mjs';
import { openSqliteAuthState } from './state.mjs';

const COMMAND_CONTRACT = 'principia-atlas-hosted-auth-state-command/0.1';

function parseArgs(argv) {
  const [command, ...rest] = argv;
  if (!['stats', 'prune', 'revoke-session', 'revoke-subject'].includes(command)) throw new Error('command must be stats, prune, revoke-session, or revoke-subject');
  const output = { command, now: Math.floor(Date.now() / 1000) };
  for (let index = 0; index < rest.length; index += 1) {
    const item = rest[index];
    if (!['--state', '--sid', '--tenant', '--subject', '--now'].includes(item)) throw new Error(`unknown argument: ${item}`);
    const value = rest[++index];
    if (!value) throw new Error(`${item} requires a value`);
    output[item.slice(2)] = value;
  }
  if (!output.state) throw new Error('--state is required');
  output.now = Number(output.now);
  if (!Number.isSafeInteger(output.now) || output.now < 0) throw new Error('--now is invalid');
  if (command === 'revoke-session' && !output.sid) throw new Error('--sid is required');
  if (command === 'revoke-subject' && (!output.tenant || !output.subject)) throw new Error('--tenant and --subject are required');
  return output;
}

export function main(argv = process.argv.slice(2), write = (value) => process.stdout.write(value)) {
  const args = parseArgs(argv);
  const state = openSqliteAuthState(args.state);
  try {
    let result;
    if (args.command === 'stats') {
      result = { contract: COMMAND_CONTRACT, command: args.command, result: state.stats(args.now) };
    } else if (args.command === 'prune') {
      state.prune(args.now);
      result = { contract: COMMAND_CONTRACT, command: args.command, result: state.stats(args.now) };
    } else if (args.command === 'revoke-session') {
      result = { contract: COMMAND_CONTRACT, command: args.command, revoked: state.revokeSession(args.sid, args.now) };
    } else {
      result = { contract: COMMAND_CONTRACT, command: args.command, revoked_sessions: state.revokeSubject(args.tenant, args.subject, args.now) };
    }
    write(canonicalJson(result));
    return result;
  } finally {
    state.close();
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try { main(); }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
