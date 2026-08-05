import { fail } from '../hosted/strict_json.mjs';
import {
  SAAS_CONTROL_PLANE_CONTRACT,
  SAAS_DASHBOARD_CONTRACT,
  publicMembership,
  publicOrganization,
  integer,
  validateEntitlementDraft,
  validateMembershipDraft,
  validateNow,
  validateOrganizationDraft,
  validateProgressDraft,
} from './domain.mjs';
import { verifyPostgresMigrations } from './postgres_migrations.mjs';

const TRANSIENT_TRANSACTION_CODES = new Set(['40001', '40P01']);
const ADMIN_ROLES = new Set(['owner', 'admin']);

function validatePool(pool) {
  if (!pool || typeof pool.connect !== 'function' || typeof pool.query !== 'function') {
    fail('PostgreSQL pool is invalid');
  }
  return pool;
}

function safeInteger(value, label) {
  const output = Number(value);
  if (!Number.isSafeInteger(output) || output < 0) fail(`${label} is invalid`);
  return output;
}

function isUniqueViolation(error) {
  return error?.code === '23505';
}

async function withSerializableTransaction(pool, operation, maxAttempts) {
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    const client = await pool.connect();
    if (!client || typeof client.query !== 'function' || typeof client.release !== 'function') {
      try { client?.release?.(); } catch {}
      fail('PostgreSQL client is invalid');
    }
    try {
      await client.query('BEGIN ISOLATION LEVEL SERIALIZABLE');
      const output = await operation(client);
      await client.query('COMMIT');
      return output;
    } catch (error) {
      try { await client.query('ROLLBACK'); } catch {}
      if (TRANSIENT_TRANSACTION_CODES.has(error?.code) && attempt < maxAttempts) continue;
      throw error;
    } finally {
      client.release();
    }
  }
  fail('PostgreSQL transaction retry limit exceeded');
}

async function withReadSnapshot(pool, operation) {
  const client = await pool.connect();
  if (!client || typeof client.query !== 'function' || typeof client.release !== 'function') {
    try { client?.release?.(); } catch {}
    fail('PostgreSQL client is invalid');
  }
  try {
    await client.query('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY');
    const output = await operation(client);
    await client.query('COMMIT');
    return output;
  } catch (error) {
    try { await client.query('ROLLBACK'); } catch {}
    throw error;
  } finally {
    client.release();
  }
}

async function requireActor(
  client,
  actorMemberId,
  { organizationId = null, allowedRoles = null, lock = true } = {},
) {
  const parameters = [actorMemberId];
  let organizationClause = '';
  if (organizationId !== null) {
    parameters.push(organizationId);
    organizationClause = 'AND m.organization_id = $2';
  }
  const lockClause = lock ? 'FOR SHARE OF m, o' : '';
  const result = await client.query(`
    SELECT
      m.id, m.organization_id, m.role, m.status, m.created_at, m.updated_at,
      o.slug, o.display_name, o.status AS organization_status,
      o.created_at AS organization_created_at, o.updated_at AS organization_updated_at
    FROM principia_atlas_saas_memberships m
    JOIN principia_atlas_saas_organizations o ON o.id = m.organization_id
    WHERE m.id = $1 ${organizationClause}
    ${lockClause}
  `, parameters);
  if (result.rowCount !== 1 || result.rows[0].status !== 'active') {
    fail('SaaS actor is not an active organization member');
  }
  const row = result.rows[0];
  if (row.organization_status !== 'active') fail('SaaS organization is not active');
  if (allowedRoles && !allowedRoles.has(row.role)) fail('SaaS actor is not authorized');
  return row;
}

function organizationFromActor(row) {
  return publicOrganization({
    id: row.organization_id,
    slug: row.slug,
    display_name: row.display_name,
    status: row.organization_status,
    created_at: row.organization_created_at,
    updated_at: row.organization_updated_at,
  });
}

function membershipFromActor(row) {
  return publicMembership({
    id: row.id,
    organization_id: row.organization_id,
    role: row.role,
    status: row.status,
    created_at: row.created_at,
    updated_at: row.updated_at,
  });
}

export function openPostgresSaasControlPlane(poolInput, { maxTransactionAttempts = 3 } = {}) {
  const pool = validatePool(poolInput);
  integer(maxTransactionAttempts, 'PostgreSQL transaction retry limit', 1);
  let closed = false;
  const ensureOpen = () => { if (closed) fail('SaaS control plane is closed'); };

  const state = {
    descriptor: Object.freeze({
      contract: SAAS_CONTROL_PLANE_CONTRACT,
      kind: 'postgresql',
      durable: true,
      multi_instance: true,
      database_ready: true,
      production_ready: false,
    }),
    async bootstrapOrganization(organizationInput, ownerInput, nowSeconds) {
      ensureOpen();
      const organization = validateOrganizationDraft(organizationInput);
      const owner = validateMembershipDraft(ownerInput);
      const now = validateNow(nowSeconds);
      if (owner.organizationId !== organization.id || owner.role !== 'owner') fail('bootstrap owner is invalid');
      try {
        return await withSerializableTransaction(pool, async (client) => {
          await client.query(`
            INSERT INTO principia_atlas_saas_organizations(
              id, slug, display_name, status, created_at, updated_at
            ) VALUES($1, $2, $3, 'active', $4, $4)
          `, [organization.id, organization.slug, organization.displayName, now]);
          await client.query(`
            INSERT INTO principia_atlas_saas_memberships(
              id, organization_id, subject_id, role, status, created_at, updated_at
            ) VALUES($1, $2, $3, 'owner', 'active', $4, $4)
          `, [owner.id, owner.organizationId, owner.subjectId, now]);
          return Object.freeze({
            organization: Object.freeze({
              id: organization.id,
              slug: organization.slug,
              display_name: organization.displayName,
              status: 'active',
              created_at: now,
              updated_at: now,
            }),
            membership: Object.freeze({
              id: owner.id,
              organization_id: owner.organizationId,
              role: owner.role,
              status: 'active',
              created_at: now,
              updated_at: now,
            }),
          });
        }, maxTransactionAttempts);
      } catch (error) {
        if (isUniqueViolation(error)) fail('organization or bootstrap owner already exists');
        throw error;
      }
    },
    async addMembership(actorMemberId, memberInput, nowSeconds) {
      ensureOpen();
      const member = validateMembershipDraft(memberInput);
      const now = validateNow(nowSeconds);
      try {
        return await withSerializableTransaction(pool, async (client) => {
          const actor = await requireActor(client, actorMemberId, {
            organizationId: member.organizationId,
            allowedRoles: ADMIN_ROLES,
          });
          if (member.role === 'owner' && actor.role !== 'owner') fail('only an owner may add another owner');
          const inserted = await client.query(`
            INSERT INTO principia_atlas_saas_memberships(
              id, organization_id, subject_id, role, status, created_at, updated_at
            ) VALUES($1, $2, $3, $4, 'active', $5, $5)
            RETURNING id, organization_id, role, status, created_at, updated_at
          `, [member.id, member.organizationId, member.subjectId, member.role, now]);
          return publicMembership(inserted.rows[0]);
        }, maxTransactionAttempts);
      } catch (error) {
        if (isUniqueViolation(error)) fail('membership identifier or subject already exists');
        throw error;
      }
    },
    async grantEntitlement(actorMemberId, entitlementInput, nowSeconds) {
      ensureOpen();
      const entitlement = validateEntitlementDraft(entitlementInput);
      const now = validateNow(nowSeconds);
      return withSerializableTransaction(pool, async (client) => {
        await requireActor(client, actorMemberId, {
          organizationId: entitlement.organizationId,
          allowedRoles: ADMIN_ROLES,
        });
        const updated = await client.query(`
          INSERT INTO principia_atlas_saas_entitlements(
            organization_id, route_id, release_id, starts_at, ends_at, created_at, updated_at
          ) VALUES($1, $2, $3, $4, $5, $6, $6)
          ON CONFLICT(organization_id, route_id, release_id) DO UPDATE SET
            starts_at = EXCLUDED.starts_at,
            ends_at = EXCLUDED.ends_at,
            updated_at = EXCLUDED.updated_at
          RETURNING organization_id, route_id, release_id, starts_at, ends_at
        `, [
          entitlement.organizationId,
          entitlement.routeId,
          entitlement.releaseId,
          entitlement.startsAt,
          entitlement.endsAt,
          now,
        ]);
        const row = updated.rows[0];
        return Object.freeze({
          organization_id: row.organization_id,
          route_id: row.route_id,
          release_id: row.release_id,
          starts_at: safeInteger(row.starts_at, 'entitlement start time'),
          ends_at: row.ends_at === null ? null : safeInteger(row.ends_at, 'entitlement end time'),
        });
      }, maxTransactionAttempts);
    },
    async recordProgress(actorMemberId, progressInput, nowSeconds) {
      ensureOpen();
      const progress = validateProgressDraft(progressInput);
      const now = validateNow(nowSeconds);
      if (actorMemberId !== progress.memberId) fail('members may only update their own learner progress');
      return withSerializableTransaction(pool, async (client) => {
        await requireActor(client, actorMemberId, { organizationId: progress.organizationId });
        const entitlement = await client.query(`
          SELECT 1 AS allowed
          FROM principia_atlas_saas_entitlements
          WHERE organization_id = $1
            AND route_id = $2
            AND release_id = $3
            AND starts_at <= $4
            AND (ends_at IS NULL OR ends_at > $4)
          FOR SHARE
        `, [progress.organizationId, progress.routeId, progress.releaseId, now]);
        if (entitlement.rowCount !== 1) fail('learner route is not entitled');

        let stored;
        if (progress.expectedRevision === 0) {
          stored = await client.query(`
            INSERT INTO principia_atlas_saas_learner_progress(
              organization_id, member_id, route_id, release_id, stage, status, revision, updated_at
            ) VALUES($1, $2, $3, $4, $5, $6, 1, $7)
            ON CONFLICT DO NOTHING
            RETURNING organization_id, member_id, route_id, release_id, stage, status, revision, updated_at
          `, [
            progress.organizationId,
            progress.memberId,
            progress.routeId,
            progress.releaseId,
            progress.stage,
            progress.status,
            now,
          ]);
        } else {
          stored = await client.query(`
            UPDATE principia_atlas_saas_learner_progress
            SET status = $1, revision = revision + 1, updated_at = $2
            WHERE organization_id = $3
              AND member_id = $4
              AND route_id = $5
              AND release_id = $6
              AND stage = $7
              AND revision = $8
            RETURNING organization_id, member_id, route_id, release_id, stage, status, revision, updated_at
          `, [
            progress.status,
            now,
            progress.organizationId,
            progress.memberId,
            progress.routeId,
            progress.releaseId,
            progress.stage,
            progress.expectedRevision,
          ]);
        }
        if (stored.rowCount !== 1) fail('learner progress revision conflict');
        const row = stored.rows[0];
        return Object.freeze({
          organization_id: row.organization_id,
          member_id: row.member_id,
          route_id: row.route_id,
          release_id: row.release_id,
          stage: row.stage,
          status: row.status,
          revision: safeInteger(row.revision, 'learner progress revision'),
          updated_at: safeInteger(row.updated_at, 'learner progress update time'),
        });
      }, maxTransactionAttempts);
    },
    async dashboard(actorMemberId, nowSeconds) {
      ensureOpen();
      const now = validateNow(nowSeconds);
      return withReadSnapshot(pool, async (client) => {
        const actor = await requireActor(client, actorMemberId, { lock: false });
        const entitlements = await client.query(`
          SELECT organization_id, route_id, release_id, starts_at, ends_at
          FROM principia_atlas_saas_entitlements
          WHERE organization_id = $1
            AND starts_at <= $2
            AND (ends_at IS NULL OR ends_at > $2)
          ORDER BY route_id, release_id
        `, [actor.organization_id, now]);
        const progress = await client.query(`
          SELECT organization_id, member_id, route_id, release_id, stage, status, revision, updated_at
          FROM principia_atlas_saas_learner_progress
          WHERE organization_id = $1 AND member_id = $2
          ORDER BY route_id, release_id, CASE stage
            WHEN 'observe' THEN 1 WHEN 'map' THEN 2 WHEN 'model' THEN 3 WHEN 'diagnose' THEN 4 ELSE 5 END
        `, [actor.organization_id, actor.id]);
        return Object.freeze({
          contract: SAAS_DASHBOARD_CONTRACT,
          generated_at: now,
          organization: organizationFromActor(actor),
          membership: membershipFromActor(actor),
          entitlements: entitlements.rows.map((row) => Object.freeze({
            organization_id: row.organization_id,
            route_id: row.route_id,
            release_id: row.release_id,
            starts_at: safeInteger(row.starts_at, 'entitlement start time'),
            ends_at: row.ends_at === null ? null : safeInteger(row.ends_at, 'entitlement end time'),
          })),
          progress: progress.rows.map((row) => Object.freeze({
            organization_id: row.organization_id,
            member_id: row.member_id,
            route_id: row.route_id,
            release_id: row.release_id,
            stage: row.stage,
            status: row.status,
            revision: safeInteger(row.revision, 'learner progress revision'),
            updated_at: safeInteger(row.updated_at, 'learner progress update time'),
          })),
        });
      });
    },
    async health() {
      ensureOpen();
      await verifyPostgresMigrations(pool);
      const result = await pool.query('SELECT 1 AS healthy');
      if (result.rowCount !== 1 || Number(result.rows[0].healthy) !== 1) fail('PostgreSQL SaaS state health check failed');
      return Object.freeze({ status: 'ok', ...state.descriptor });
    },
    close() { closed = true; },
  };
  return Object.freeze(state);
}
