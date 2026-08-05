import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

import { fail } from '../hosted/strict_json.mjs';
import { SAAS_STATE_CONTRACT } from './domain.mjs';

export const POSTGRES_MIGRATION_LEDGER_CONTRACT = 'principia-atlas-saas-postgres-migrations/0.1';
const MIGRATION_LOCK_ID = '730861210504746119';

function migration(version, name, relativePath) {
  const sql = readFileSync(fileURLToPath(new URL(relativePath, import.meta.url)), 'utf8');
  if (!sql.endsWith('\n') || sql.trim().length === 0) fail(`PostgreSQL migration ${version} is invalid`);
  return Object.freeze({
    version,
    name,
    sql,
    sha256: createHash('sha256').update(sql, 'utf8').digest('hex'),
  });
}

const MIGRATIONS = Object.freeze([
  migration(1, 'control-plane', './migrations/0001_control_plane.up.sql'),
  migration(2, 'application-api', './migrations/0002_application_api.up.sql'),
]);

function validatePool(pool) {
  if (!pool || typeof pool.connect !== 'function' || typeof pool.query !== 'function') {
    fail('PostgreSQL pool is invalid');
  }
  return pool;
}

async function withClient(pool, operation) {
  const client = await validatePool(pool).connect();
  if (!client || typeof client.query !== 'function' || typeof client.release !== 'function') {
    try { client?.release?.(); } catch {}
    fail('PostgreSQL client is invalid');
  }
  try { return await operation(client); }
  finally { client.release(); }
}

function asVersion(value) {
  const version = Number(value);
  if (!Number.isSafeInteger(version) || version < 1) fail('PostgreSQL migration ledger is invalid');
  return version;
}

export function postgresMigrationPlan() {
  return Object.freeze({
    contract: POSTGRES_MIGRATION_LEDGER_CONTRACT,
    migrations: MIGRATIONS.map(({ version, name, sha256 }) => Object.freeze({ version, name, sha256 })),
  });
}

export async function applyPostgresMigrations(pool) {
  return withClient(pool, async (client) => {
    await client.query('BEGIN');
    try {
      await client.query('SELECT pg_advisory_xact_lock($1::bigint)', [MIGRATION_LOCK_ID]);
      await client.query(`
        CREATE TABLE IF NOT EXISTS principia_atlas_saas_migrations (
          version bigint PRIMARY KEY CHECK (version > 0),
          name text NOT NULL,
          sha256 text NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
          applied_at bigint NOT NULL CHECK (applied_at >= 0)
        )
      `);

      const applied = await client.query(`
        SELECT version, name, sha256
        FROM principia_atlas_saas_migrations
        ORDER BY version
      `);
      const expectedVersions = new Set(MIGRATIONS.map((item) => item.version));
      for (const row of applied.rows) {
        const version = asVersion(row.version);
        if (!expectedVersions.has(version)) fail('PostgreSQL migration ledger contains an unknown version');
        const expected = MIGRATIONS.find((item) => item.version === version);
        if (row.name !== expected.name || row.sha256 !== expected.sha256) {
          fail(`PostgreSQL migration ${version} digest does not match source`);
        }
      }

      const appliedVersions = new Set(applied.rows.map((row) => asVersion(row.version)));
      for (const item of MIGRATIONS) {
        if (appliedVersions.has(item.version)) continue;
        await client.query(item.sql);
        await client.query(`
          INSERT INTO principia_atlas_saas_migrations(version, name, sha256, applied_at)
          VALUES($1, $2, $3, EXTRACT(EPOCH FROM clock_timestamp())::bigint)
        `, [item.version, item.name, item.sha256]);
      }

      const contract = await client.query(`
        SELECT value FROM principia_atlas_saas_metadata WHERE key = 'contract'
      `);
      if (contract.rowCount !== 1 || contract.rows[0].value !== SAAS_STATE_CONTRACT) {
        fail('PostgreSQL SaaS state contract is incompatible');
      }
      await client.query('COMMIT');
      return postgresMigrationPlan();
    } catch (error) {
      try { await client.query('ROLLBACK'); } catch {}
      throw error;
    }
  });
}

export async function verifyPostgresMigrations(pool) {
  const plan = postgresMigrationPlan();
  const rows = await validatePool(pool).query(`
    SELECT version, name, sha256
    FROM principia_atlas_saas_migrations
    ORDER BY version
  `);
  if (rows.rowCount !== plan.migrations.length) fail('PostgreSQL migration set is incomplete');
  for (let index = 0; index < plan.migrations.length; index += 1) {
    const expected = plan.migrations[index];
    const actual = rows.rows[index];
    if (asVersion(actual.version) !== expected.version || actual.name !== expected.name || actual.sha256 !== expected.sha256) {
      fail('PostgreSQL migration set does not match source');
    }
  }
  const contract = await validatePool(pool).query(`
    SELECT value FROM principia_atlas_saas_metadata WHERE key = 'contract'
  `);
  if (contract.rowCount !== 1 || contract.rows[0].value !== SAAS_STATE_CONTRACT) {
    fail('PostgreSQL SaaS state contract is incompatible');
  }
  return plan;
}
