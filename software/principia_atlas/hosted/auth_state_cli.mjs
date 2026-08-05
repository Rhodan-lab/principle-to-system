#!/usr/bin/env node
import { canonicalOidcSubject } from './oidc_subject.mjs';
import { readOidcRevocationRequest } from './revocation_request.mjs';
import { canonicalJson } from './strict_json.mjs';
import { openSqliteAuthState } from './state.mjs';

const COMMAND_CONTRACT = 'principia-atlas-hosted-auth-state-command/0.1';
const COMMANDS = new Set([
  'stats',
  'prune',
  'revoke-session',
  'revoke-subject',
  'revoke-oidc-subject',
  'revoke-oidc-request',
]);
const FLAGS = new Set([
  '--state',
  '--sid',
  '--tenant',
  '--subject',
  '--issuer',
  '--external-subject',
  '--event-id',
  '--receipt-ttl-seconds',
  '--request-file',
  '--now',
]);
const REQUEST_FLAGS = new Set(['--state', '--request-file', '--now']);

function parseArgs(argv) {
  const [command, ...rest] = argv;
  if (!COMMANDS.has(command)) throw new Error('command must be stats, prune, revoke-session, revoke-subject, revoke-oidc-subject, or revoke-oidc-request');
  const output = { command, now: Math.floor(Date.now() / 1000), receiptTtlSeconds: 30 * 24 * 60 * 60 };
  const seen = new Set();
  for (let index = 0; index < rest.length; index += 1) {
    const item = rest[index];
    if (!FLAGS.has(item) || seen.has(item) || (command === 'revoke-oidc-request' && !REQUEST_FLAGS.has(item))) throw new Error(`unknown or duplicate argument: ${item}`);
    seen.add(item);
    const value = rest[++index];
    if (!value) throw new Error(`${item} requires a value`);
    output[item.slice(2)] = value;
  }
  if (!output.state) throw new Error('--state is required');
  output.now = Number(output.now);
  output.receiptTtlSeconds = Number(output['receipt-ttl-seconds'] ?? output.receiptTtlSeconds);
  if (!Number.isSafeInteger(output.now) || output.now < 0) throw new Error('--now is invalid');
  if (!Number.isSafeInteger(output.receiptTtlSeconds) || output.receiptTtlSeconds < 60 || output.receiptTtlSeconds > 365 * 24 * 60 * 60) throw new Error('--receipt-ttl-seconds is invalid');
  if (command === 'revoke-session' && !output.sid) throw new Error('--sid is required');
  if (command === 'revoke-subject' && (!output.tenant || !output.subject)) throw new Error('--tenant and --subject are required');
  if (command === 'revoke-oidc-subject' && (!output.tenant || !output.issuer || !output['external-subject'] || !output['event-id'])) {
    throw new Error('--tenant, --issuer, --external-subject, and --event-id are required');
  }
  if (command === 'revoke-oidc-request' && !output['request-file']) throw new Error('--request-file is required');
  return output;
}

export function main(argv = process.argv.slice(2), write = (value) => process.stdout.write(value)) {
  const args = parseArgs(argv);
  const request = args.command === 'revoke-oidc-request'
    ? readOidcRevocationRequest(args['request-file'], args.now)
    : null;
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
    } else if (args.command === 'revoke-oidc-subject') {
      const receipt = state.revokeSubjectOnce(
        args['event-id'],
        args.tenant,
        canonicalOidcSubject(args.issuer, args['external-subject']),
        args.now,
        args.now + args.receiptTtlSeconds,
      );
      result = { contract: COMMAND_CONTRACT, command: args.command, ...receipt };
    } else if (args.command === 'revoke-oidc-request') {
      const receipt = state.revokeSubjectOnce(
        request.eventId,
        request.tenantId,
        request.subject,
        args.now,
        args.now + request.receiptTtlSeconds,
      );
      result = { contract: COMMAND_CONTRACT, command: args.command, ...receipt };
    } else {
      result = {
        contract: COMMAND_CONTRACT,
        command: args.command,
        revoked_sessions: state.revokeSubject(args.tenant, args.subject, args.now),
      };
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
