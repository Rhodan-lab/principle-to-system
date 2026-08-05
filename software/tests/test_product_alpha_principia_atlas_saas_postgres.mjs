import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import {
  applyPostgresMigrations,
  postgresMigrationPlan,
  verifyPostgresMigrations,
} from '../principia_atlas/saas/postgres_migrations.mjs';
import { openPostgresSaasControlPlane } from '../principia_atlas/saas/postgres_store.mjs';
import { openSaasControlPlane } from '../principia_atlas/saas/store.mjs';

const databaseUrl = process.env.DATABASE_URL;
const clientRoot = process.env.PG_CLIENT_ROOT;

function postgresDriver() {
  if (!clientRoot) throw new Error('PG_CLIENT_ROOT is required');
  const require = createRequire(join(clientRoot, 'package.json'));
  return require('pg');
}

const now = 1_800_100_000;
const hostedTenant = 'postgres-public-tenant';
const organization = {
  id: 'org_01POSTGRESSAASFOUNDAT',
  slug: 'public-science-lab',
  display_name: 'Public Science Lab',
};
const owner = {
  id: 'mem_01POSTGRESSAASOWNER00',
  organization_id: organization.id,
  subject_id: `oidc:${'P'.repeat(43)}`,
  role: 'owner',
};
const learner = {
  id: 'mem_01POSTGRESSAASLEARNER',
  organization_id: organization.id,
  subject_id: `oidc:${'Q'.repeat(43)}`,
  role: 'learner',
};
const releaseId = 'principia-atlas-release:0.3.0-beta.1';

async function populate(state) {
  await state.bootstrapOrganization(organization, owner, now);
  await state.bindHostedTenant(owner.id, {
    organization_id: organization.id,
    hosted_tenant_id: hostedTenant,
  }, now + 1);
  await state.addMembership(owner.id, learner, now + 2);
  await state.grantEntitlement(owner.id, {
    organization_id: organization.id,
    route_id: 'refrigerator-v1',
    release_id: releaseId,
    starts_at: now,
    ends_at: null,
  }, now + 3);
  await state.recordProgress(learner.id, {
    organization_id: organization.id,
    member_id: learner.id,
    route_id: 'refrigerator-v1',
    release_id: releaseId,
    stage: 'observe',
    status: 'completed',
    expected_revision: 0,
  }, now + 4);
  return state.dashboard(learner.id, now + 5);
}

test('PostgreSQL SaaS adapter preserves reference semantics', { skip: !databaseUrl || !clientRoot }, async () => {
  const { Pool } = postgresDriver();
  const pool = new Pool({ connectionString: databaseUrl, max: 8 });
  const replicaPool = new Pool({ connectionString: databaseUrl, max: 4 });
  const root = mkdtempSync(join(tmpdir(), 'principia-atlas-saas-pg-parity-'));
  const sqlite = openSaasControlPlane(join(root, 'reference.sqlite'));
  try {
    const [firstPlan, secondPlan] = await Promise.all([
      applyPostgresMigrations(pool),
      applyPostgresMigrations(replicaPool),
    ]);
    assert.deepEqual(firstPlan, secondPlan);
    assert.deepEqual(await verifyPostgresMigrations(pool), postgresMigrationPlan());
    assert.equal(firstPlan.migrations.length, 2);

    const postgres = openPostgresSaasControlPlane(pool, { maxTransactionAttempts: 5 });
    const referenceDashboard = await populate(sqlite);
    const postgresDashboard = await populate(postgres);
    assert.deepEqual(postgresDashboard, referenceDashboard);
    assert.equal(JSON.stringify(postgresDashboard).includes(owner.subject_id), false);
    assert.equal(JSON.stringify(postgresDashboard).includes(learner.subject_id), false);

    const referenceSession = await sqlite.resolveSession(hostedTenant, learner.subject_id, now + 5);
    const postgresSession = await postgres.resolveSession(hostedTenant, learner.subject_id, now + 5);
    assert.deepEqual(postgresSession, referenceSession);
    assert.equal(await postgres.resolveSession('wrong-tenant', learner.subject_id, now + 5), null);

    const replica = openPostgresSaasControlPlane(replicaPool, { maxTransactionAttempts: 5 });
    const progressInput = {
      organization_id: organization.id,
      member_id: learner.id,
      route_id: 'refrigerator-v1',
      release_id: releaseId,
      stage: 'map',
      status: 'in_progress',
      expected_revision: 0,
    };
    const concurrent = await Promise.allSettled([
      postgres.recordProgress(learner.id, progressInput, now + 6),
      replica.recordProgress(learner.id, progressInput, now + 6),
    ]);
    assert.equal(concurrent.filter((item) => item.status === 'fulfilled').length, 1);
    const rejected = concurrent.find((item) => item.status === 'rejected');
    assert.match(rejected.reason.message, /revision conflict/);

    const idempotentProgress = {
      organization_id: organization.id,
      member_id: learner.id,
      route_id: 'refrigerator-v1',
      release_id: releaseId,
      stage: 'diagnose',
      status: 'completed',
      expected_revision: 0,
    };
    const idempotency = {
      operation: 'progress.write',
      key: 'postgres_idempotent_0001',
      request_sha256: '1'.repeat(64),
      ttl_seconds: 3600,
    };
    const duplicate = await Promise.all([
      postgres.recordProgressIdempotent(learner.id, idempotentProgress, idempotency, now + 7),
      replica.recordProgressIdempotent(learner.id, idempotentProgress, idempotency, now + 7),
    ]);
    assert.deepEqual(duplicate[0].progress, duplicate[1].progress);
    assert.deepEqual(duplicate.map((item) => item.replayed).sort(), [false, true]);
    const receipts = await pool.query(`
      SELECT COUNT(*)::int AS count
      FROM principia_atlas_saas_idempotency
      WHERE organization_id = $1 AND member_id = $2 AND operation = $3 AND idempotency_key = $4
    `, [organization.id, learner.id, idempotency.operation, idempotency.key]);
    assert.equal(receipts.rows[0].count, 1);

    await assert.rejects(
      () => postgres.recordProgressIdempotent(learner.id, idempotentProgress, {
        ...idempotency,
        request_sha256: '2'.repeat(64),
      }, now + 8),
      /idempotency key conflict/,
    );

    await assert.rejects(
      () => postgres.addMembership(owner.id, {
        id: 'mem_01POSTGRESDUPLICATE00',
        organization_id: organization.id,
        subject_id: learner.subject_id,
        role: 'learner',
      }, now + 9),
      /already exists/,
    );
    const membershipCount = await pool.query(`
      SELECT COUNT(*)::int AS count
      FROM principia_atlas_saas_memberships
      WHERE organization_id = $1
    `, [organization.id]);
    assert.equal(membershipCount.rows[0].count, 2);

    const plan = postgresMigrationPlan();
    await pool.query(`
      UPDATE principia_atlas_saas_migrations SET sha256 = $1 WHERE version = 1
    `, ['0'.repeat(64)]);
    await assert.rejects(() => verifyPostgresMigrations(pool), /does not match source/);
    await pool.query(`
      UPDATE principia_atlas_saas_migrations SET sha256 = $1 WHERE version = 1
    `, [plan.migrations[0].sha256]);
    assert.equal((await postgres.health()).multi_instance, true);
    assert.equal((await postgres.health()).production_ready, false);

    postgres.close();
    replica.close();
  } finally {
    sqlite.close();
    rmSync(root, { recursive: true, force: true });
    await replicaPool.end();
    await pool.end();
  }
});

test('failed PostgreSQL migration rolls back every partial object', { skip: !databaseUrl || !clientRoot }, async () => {
  const { Pool } = postgresDriver();
  const admin = new Pool({ connectionString: databaseUrl, max: 2 });
  await admin.query('CREATE SCHEMA saas_migration_failure');
  await admin.query(`
    CREATE TABLE saas_migration_failure.principia_atlas_saas_memberships(id text PRIMARY KEY)
  `);
  const failurePool = new Pool({
    connectionString: databaseUrl,
    max: 2,
    options: '-c search_path=saas_migration_failure',
  });
  try {
    await assert.rejects(() => applyPostgresMigrations(failurePool), /already exists/);
    const objects = await admin.query(`
      SELECT
        to_regclass('saas_migration_failure.principia_atlas_saas_migrations') AS ledger,
        to_regclass('saas_migration_failure.principia_atlas_saas_metadata') AS metadata,
        to_regclass('saas_migration_failure.principia_atlas_saas_organizations') AS organizations,
        to_regclass('saas_migration_failure.principia_atlas_saas_memberships') AS preexisting,
        to_regclass('saas_migration_failure.principia_atlas_saas_idempotency') AS idempotency
    `);
    assert.equal(objects.rows[0].ledger, null);
    assert.equal(objects.rows[0].metadata, null);
    assert.equal(objects.rows[0].organizations, null);
    assert.equal(objects.rows[0].preexisting, 'saas_migration_failure.principia_atlas_saas_memberships');
    assert.equal(objects.rows[0].idempotency, null);
  } finally {
    await failurePool.end();
    await admin.end();
  }
});
