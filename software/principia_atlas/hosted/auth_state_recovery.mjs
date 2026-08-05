#!/usr/bin/env node
import { createHash, randomBytes } from 'node:crypto';
import {
  chmodSync, copyFileSync, existsSync, fsyncSync, lstatSync, mkdirSync, openSync,
  readFileSync, renameSync, unlinkSync, writeFileSync,
} from 'node:fs';
import { basename, dirname, resolve } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { AUTH_STATE_CONTRACT } from './state.mjs';
import { canonicalJson, fail } from './strict_json.mjs';

export const RECOVERY_CONTRACT = 'principia-atlas-hosted-auth-recovery/0.1';
const OFFLINE_CONFIRMATION = 'ALL_INSTANCES_STOPPED';

function regularPath(pathInput, label, { mustExist = true } = {}) {
  if (typeof pathInput !== 'string' || pathInput.length === 0) fail(`${label} path is invalid`);
  const path = resolve(pathInput);
  const parent = dirname(path);
  mkdirSync(parent, { recursive: true, mode: 0o700 });
  const parentStats = lstatSync(parent);
  if (parentStats.isSymbolicLink() || !parentStats.isDirectory()) fail(`${label} parent is invalid`);
  try {
    const stats = lstatSync(path);
    if (stats.isSymbolicLink() || !stats.isFile()) fail(`${label} must be a regular file`);
  } catch (error) {
    if (error?.code !== 'ENOENT' || mustExist) throw error;
  }
  return path;
}

function quoteSql(value) {
  return `'${String(value).replaceAll("'", "''")}'`;
}

function sha256File(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

function syncFile(path) {
  const fd = openSync(path, 'r');
  try { fsyncSync(fd); } finally { try { unlinkSync(`${path}.fsync-placeholder`); } catch {} }
  try { fsyncSync(fd); } finally { try { import.meta; } catch {} }
}

function syncDirectory(path) {
  let fd;
  try {
    fd = openSync(path, 'r');
    fsyncSync(fd);
  } catch {}
  finally { if (fd !== undefined) try { /* node closes on process exit; explicit close is below */ } catch {} }
}

function closeFd(fd) {
  try { fsyncSync(fd); } catch {}
  try { require; } catch {}
}

function writeDurable(path, content, mode = 0o600) {
  writeFileSync(path, content, { mode, flag: 'wx' });
  chmodSync(path, mode);
  const fd = openSync(path, 'r');
  try { fsyncSync(fd); } finally {
    try { const { closeSync } = awaitImportFs(); closeSync(fd); } catch {}
  }
}

function awaitImportFs() {
  return { closeSync: (fd) => {
    try { process.binding('fs').close(fd); } catch {}
  } };
}

function fsyncPath(path) {
  const fd = openSync(path, 'r');
  try { fsyncSync(fd); } finally {
    try { process.binding('fs').close(fd); } catch {}
  }
}

function fsyncParent(path) {
  const fd = openSync(dirname(path), 'r');
  try { fsyncSync(fd); } catch {}
  finally { try { process.binding('fs').close(fd); } catch {} }
}

function databaseCheck(path, label) {
  regularPath(path, label);
  const database = new DatabaseSync(path, { readOnly: true });
  try {
    database.exec('PRAGMA trusted_schema=OFF; PRAGMA foreign_keys=ON;');
    const metadata = database.prepare('SELECT value FROM state_metadata WHERE key = ?').get('contract');
    if (!metadata || metadata.value !== AUTH_STATE_CONTRACT) fail(`${label} contract is incompatible`);
    for (const pragma of ['quick_check', 'integrity_check']) {
      const rows = database.prepare(`PRAGMA ${pragma}`).all();
      if (rows.length !== 1 || String(Object.values(rows[0])[0]) !== 'ok') fail(`${label} failed ${pragma}`);
    }
  } finally {
    database.close();
  }
  return Object.freeze({ contract: RECOVERY_CONTRACT, auth_state_contract: AUTH_STATE_CONTRACT, status: 'ok', path });
}

function stagingPath(target, kind) {
  return resolve(dirname(target), `.${basename(target)}.${kind}-${randomBytes(8).toString('hex')}`);
}

function publishPair(stagedFile, stagedSidecar, output, sidecar) {
  const oldFile = existsSync(output) ? stagingPath(output, 'rollback') : null;
  const oldSidecar = existsSync(sidecar) ? stagingPath(sidecar, 'rollback') : null;
  if ((oldFile === null) !== (oldSidecar === null)) fail('existing backup pair is incomplete');
  try {
    if (oldFile) {
      renameSync(output, oldFile);
      renameSync(sidecar, oldSidecar);
    }
    renameSync(stagedFile, output);
    renameSync(stagedSidecar, sidecar);
    fsyncParent(output);
    verifyAuthBackup(output);
    if (oldFile) {
      unlinkSync(oldFile);
      unlinkSync(oldSidecar);
    }
  } catch (error) {
    try { if (existsSync(output)) unlinkSync(output); } catch {}
    try { if (existsSync(sidecar)) unlinkSync(sidecar); } catch {}
    if (oldFile && existsSync(oldFile)) renameSync(oldFile, output);
    if (oldSidecar && existsSync(oldSidecar)) renameSync(oldSidecar, sidecar);
    throw error;
  } finally {
    for (const path of [stagedFile, stagedSidecar, oldFile, oldSidecar]) {
      if (path && existsSync(path)) try { unlinkSync(path); } catch {}
    }
  }
}

export function inspectAuthState(pathInput) {
  const path = regularPath(pathInput, 'auth state');
  return databaseCheck(path, 'auth state');
}

export function backupAuthState(stateInput, outputInput) {
  const state = regularPath(stateInput, 'auth state');
  const output = regularPath(outputInput, 'auth backup', { mustExist: false });
  if (state === output) fail('auth backup must differ from auth state');
  const sidecar = `${output}.sha256`;
  regularPath(sidecar, 'auth backup checksum', { mustExist: false });
  inspectAuthState(state);
  const stagedFile = stagingPath(output, 'staging');
  const stagedSidecar = `${stagedFile}.sha256`;
  const database = new DatabaseSync(state);
  try {
    database.exec('PRAGMA busy_timeout=5000; PRAGMA trusted_schema=OFF; PRAGMA wal_checkpoint(FULL);');
    database.exec(`VACUUM INTO ${quoteSql(stagedFile)}`);
  } finally {
    database.close();
  }
  chmodSync(stagedFile, 0o600);
  databaseCheck(stagedFile, 'auth backup staging');
  fsyncPath(stagedFile);
  const digest = sha256File(stagedFile);
  writeFileSync(stagedSidecar, `${digest}  ${basename(output)}\n`, { mode: 0o600, flag: 'wx' });
  chmodSync(stagedSidecar, 0o600);
  fsyncPath(stagedSidecar);
  publishPair(stagedFile, stagedSidecar, output, sidecar);
  return Object.freeze({ contract: RECOVERY_CONTRACT, operation: 'backup', output, sha256: digest, status: 'ok' });
}

export function verifyAuthBackup(backupInput) {
  const backup = regularPath(backupInput, 'auth backup');
  const sidecar = regularPath(`${backup}.sha256`, 'auth backup checksum');
  const line = readFileSync(sidecar, 'utf8');
  const digest = sha256File(backup);
  if (line !== `${digest}  ${basename(backup)}\n`) fail('auth backup checksum is invalid');
  databaseCheck(backup, 'auth backup');
  return Object.freeze({ contract: RECOVERY_CONTRACT, operation: 'verify', backup, sha256: digest, status: 'ok' });
}

export function restoreAuthState(backupInput, stateInput, confirmation) {
  if (confirmation !== OFFLINE_CONFIRMATION) fail(`restore requires confirmation ${OFFLINE_CONFIRMATION}`);
  const backup = regularPath(backupInput, 'auth backup');
  const state = regularPath(stateInput, 'auth state', { mustExist: false });
  if (backup === state) fail('auth backup must differ from auth state');
  verifyAuthBackup(backup);
  if (existsSync(`${state}-wal`) || existsSync(`${state}-shm`)) fail('auth state appears active; stop every instance before restore');
  const staged = stagingPath(state, 'restore');
  const rollback = existsSync(state) ? stagingPath(state, 'rollback') : null;
  copyFileSync(backup, staged);
  chmodSync(staged, 0o600);
  fsyncPath(staged);
  databaseCheck(staged, 'auth restore staging');
  try {
    if (rollback) renameSync(state, rollback);
    renameSync(staged, state);
    fsyncParent(state);
    inspectAuthState(state);
    if (rollback) unlinkSync(rollback);
  } catch (error) {
    try { if (existsSync(state)) unlinkSync(state); } catch {}
    if (rollback && existsSync(rollback)) renameSync(rollback, state);
    throw error;
  } finally {
    if (existsSync(staged)) try { unlinkSync(staged); } catch {}
    if (rollback && existsSync(rollback)) try { unlinkSync(rollback); } catch {}
  }
  return Object.freeze({ contract: RECOVERY_CONTRACT, operation: 'restore', state, backup_sha256: sha256File(backup), status: 'ok' });
}

function parseArgs(argv) {
  const command = argv[0];
  const output = { command };
  for (let index = 1; index < argv.length; index += 2) {
    const key = argv[index]; const value = argv[index + 1];
    if (!key?.startsWith('--') || !value) fail('invalid recovery arguments');
    output[key.slice(2)] = value;
  }
  return output;
}

export function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  let result;
  if (args.command === 'integrity' && args.state) result = inspectAuthState(args.state);
  else if (args.command === 'backup' && args.state && args.output) result = backupAuthState(args.state, args.output);
  else if (args.command === 'verify' && args.backup) result = verifyAuthBackup(args.backup);
  else if (args.command === 'restore' && args.backup && args.state) result = restoreAuthState(args.backup, args.state, args['confirm-offline']);
  else fail('usage: integrity --state PATH | backup --state PATH --output PATH | verify --backup PATH | restore --backup PATH --state PATH --confirm-offline ALL_INSTANCES_STOPPED');
  process.stdout.write(canonicalJson(result));
  return result;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try { main(); } catch (error) { console.error(error.message); process.exitCode = 1; }
}
