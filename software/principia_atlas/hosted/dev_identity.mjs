#!/usr/bin/env node
import { randomBytes } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { verifyTenantConfig } from './catalog.mjs';
import { parseStrictJson } from './strict_json.mjs';
import { signIdentityAssertion } from './tokens.mjs';

function parseArgs(argv) {
  const result = { roles: 'learner', ttl: 180 };
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index]; const value = argv[index + 1];
    if (!['--tenants', '--subject', '--tenant', '--roles', '--ttl'].includes(key) || !value) throw new Error('invalid development identity arguments');
    result[key.slice(2)] = value;
  }
  if (!result.tenants || !result.subject || !result.tenant) throw new Error('--tenants, --subject, and --tenant are required');
  result.ttl = Number(result.ttl);
  return result;
}

export async function main(argv = process.argv.slice(2), now = Math.floor(Date.now() / 1000)) {
  if (process.env.PRINCIPIA_ATLAS_DEV_AUTH !== '1') throw new Error('development assertion minting is disabled');
  const secret = process.env.PRINCIPIA_ATLAS_IDENTITY_SECRET;
  if (!secret) throw new Error('PRINCIPIA_ATLAS_IDENTITY_SECRET is required');
  const options = parseArgs(argv);
  const config = verifyTenantConfig(parseStrictJson(await readFile(resolve(options.tenants)), 'tenant config'));
  if (!Number.isInteger(options.ttl) || options.ttl < 30 || options.ttl > config.identity.max_assertion_ttl_seconds) throw new Error('development assertion TTL is invalid');
  const token = signIdentityAssertion({
    iss: config.identity.issuer, aud: config.identity.audience, sub: options.subject,
    tenant_id: options.tenant, roles: options.roles.split(',').filter(Boolean),
    iat: now, exp: now + options.ttl, jti: randomBytes(18).toString('base64url'),
  }, secret, config);
  process.stdout.write(`${token}\n`);
  return token;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => { console.error(error.message); process.exitCode = 1; });
}
