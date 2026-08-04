#!/usr/bin/env node
import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { sealTenantConfig, verifyTenantConfig } from './catalog.mjs';
import { canonicalJson, parseStrictJson } from './strict_json.mjs';

function args(argv) {
  const [command, ...rest] = argv;
  const result = { command };
  for (let index = 0; index < rest.length; index += 2) {
    const key = rest[index]; const value = rest[index + 1];
    if (!['--input', '--output'].includes(key) || !value) throw new Error('expected --input and optional --output');
    result[key.slice(2)] = value;
  }
  if (!['seal', 'verify'].includes(command) || !result.input) throw new Error('usage: config.mjs seal|verify --input FILE [--output FILE]');
  return result;
}

export async function main(argv = process.argv.slice(2)) {
  const options = args(argv);
  const value = parseStrictJson(await readFile(resolve(options.input)), 'tenant config');
  if (options.command === 'verify') {
    const verified = verifyTenantConfig(value);
    console.log(`Verified tenant config ${verified.config_id}`);
    return verified;
  }
  if ('config_id' in value) throw new Error('unsigned tenant config must not contain config_id');
  const sealed = verifyTenantConfig(sealTenantConfig(value));
  const output = resolve(options.output ?? `${options.input}.sealed.json`);
  await writeFile(output, canonicalJson(sealed), { flag: 'wx' });
  console.log(`Sealed tenant config ${sealed.config_id} -> ${output}`);
  return sealed;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => { console.error(error.message); process.exitCode = 1; });
}
