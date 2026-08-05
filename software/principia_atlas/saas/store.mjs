import { chmodSync, lstatSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { DatabaseSync } from 'node:sqlite';

import { canonicalJson, fail, parseStrictJson } from '../hosted/strict_json.mjs';
import {
  PREVIOUS_SAAS_STATE_CONTRACT,
  SAAS_CONTROL_PLANE_CONTRACT,
  SAAS_DASHBOARD_CONTRACT,
  SAAS_STATE_CONTRACT,
  publicMembership,
  publicOrganization,
  integer,
  validateEntitlementDraft,
  validateHostedTenantBinding,
  validateIdempotencyInput,
  validateMembershipDraft,
  validateNow,
  validateOrganizationDraft,
  validateProgressDraft,
  validateSessionIdentity,
} from './domain.mjs';

const ADMIN_ROLES = new Set(['owner', 'admin']);
const OWNER_ROLES = new Set(['owner']);

function databasePath(pathInput) {
  if (typeof pathInput !== 'string' || pathInput.length === 0 || pathInput === ':memory:') fail('SaaS state path is invalid');
  const path = resolve(pathInput);
  const parent = dirname(path);
  mkdirSync(parent, { recursive: true, mode: 0o700 });
  const parentStat = lstatSync(parent);
  if (parentStat.isSymbolicLink() || !parentStat.isDirectory()) fail('SaaS state parent must be a regular directory');
  try {
    const stat = lstatSync(path);
    if (stat.isSymbolicLink() || !stat.isFile()) fail('SaaS state must be a regular file');
  } catch (error) {
    if (error?.code !== 'ENOENT') throw error;
  }
  return path;
}

function transaction(database, operation) {
  database.exec('BEGIN IMMEDIATE');
  try {
    const result = operation();
    database.exec('COMMIT');
    return result;
  } catch (error) {
    try { database.exec('ROLLBACK'); } catch {}
    throw error;
  }
}

function ensureApplicationSchema(database) {
  const metadata = database.prepare('SELECT value FROM metadata WHERE key = ?').get('contract');
  if (metadata && ![PREVIOUS_SAAS_STATE_CONTRACT, SAAS_STATE_CONTRACT].includes(metadata.value)) {
    fail('SaaS state schema contract is incompatible');
  }
  transaction(database, () => {
    const columns = database.prepare('PRAGMA table_info(organizations)').all();
    if (!columns.some((column) => column.name === 'hosted_tenant_id')) {
      database.exec('ALTER TABLE organizations ADD COLUMN hosted_tenant_id TEXT');
    }
    database.exec(`
      CREATE UNIQUE INDEX IF NOT EXISTS organizations_hosted_tenant_unique
        ON organizations(hosted_tenant_id)
        WHERE hosted_tenant_id IS NOT NULL;
      CREATE INDEX IF NOT EXISTS memberships_subject_lookup
        ON memberships(subject_id, organization_id, status);
      CREATE TABLE IF NOT EXISTS idempotency (
        organization_id TEXT NOT NULL,
        member_id TEXT NOT NULL,
        operation TEXT NOT NULL,
        idempotency_key TEXT NOT NULL,
        request_sha256 TEXT NOT NULL,
        response_status INTEGER NOT NULL CHECK(response_status BETWEEN 200 AND 599),
        response_body TEXT NOT NULL CHECK(length(response_body) BETWEEN 2 AND 16384),
        created_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL CHECK(expires_at > created_at),
        PRIMARY KEY(organization_id, member_id, operation, idempotency_key),
        FOREIGN KEY(member_id, organization_id) REFERENCES memberships(id, organization_id) ON DELETE CASCADE
      ) STRICT;
      CREATE INDEX IF NOT EXISTS idempotency_expiry ON idempotency(expires_at);
    `);
    if (!metadata) database.prepare('INSERT INTO metadata(key, value) VALUES(?, ?)').run('contract', SAAS_STATE_CONTRACT);
    else if (metadata.value === PREVIOUS_SAAS_STATE_CONTRACT) {
      database.prepare('UPDATE metadata SET value = ? WHERE key = ?').run(SAAS_STATE_CONTRACT, 'contract');
    }
  });
}

export function openSaasControlPlane(pathInput, { busyTimeoutMs = 5000 } = {}) {
  integer(busyTimeoutMs, 'SQLite busy timeout', 1);
  const path = databasePath(pathInput);
  const database = new DatabaseSync(path);
  let closed = false;
  const ensureOpen = () => { if (closed) fail('SaaS control plane is closed'); };
  try {
    database.exec(`PRAGMA busy_timeout=${busyTimeoutMs}; PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA foreign_keys=ON; PRAGMA trusted_schema=OFF;`);
    database.exec(`
      CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL) STRICT;
      CREATE TABLE IF NOT EXISTS organizations (
        id TEXT PRIMARY KEY,
        slug TEXT NOT NULL UNIQUE,
        display_name TEXT NOT NULL,
        hosted_tenant_id TEXT,
        status TEXT NOT NULL CHECK(status IN ('active', 'suspended')),
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL
      ) STRICT;
      CREATE TABLE IF NOT EXISTS memberships (
        id TEXT PRIMARY KEY,
        organization_id TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        subject_id TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('owner', 'admin', 'facilitator', 'learner')),
        status TEXT NOT NULL CHECK(status IN ('active', 'disabled')),
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL,
        UNIQUE(organization_id, subject_id),
        UNIQUE(id, organization_id)
      ) STRICT;
      CREATE INDEX IF NOT EXISTS memberships_org ON memberships(organization_id, status, role);
      CREATE TABLE IF NOT EXISTS entitlements (
        organization_id TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        route_id TEXT NOT NULL,
        release_id TEXT NOT NULL,
        starts_at INTEGER NOT NULL,
        ends_at INTEGER,
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL,
        PRIMARY KEY(organization_id, route_id, release_id)
      ) STRICT;
      CREATE INDEX IF NOT EXISTS entitlements_active ON entitlements(organization_id, starts_at, ends_at);
      CREATE TABLE IF NOT EXISTS learner_progress (
        organization_id TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
        member_id TEXT NOT NULL,
        route_id TEXT NOT NULL,
        release_id TEXT NOT NULL,
        stage TEXT NOT NULL CHECK(stage IN ('observe', 'map', 'model', 'diagnose', 'redesign')),
        status TEXT NOT NULL CHECK(status IN ('in_progress', 'completed')),
        revision INTEGER NOT NULL,
        updated_at INTEGER NOT NULL,
        PRIMARY KEY(organization_id, member_id, route_id, release_id, stage),
        FOREIGN KEY(member_id, organization_id) REFERENCES memberships(id, organization_id) ON DELETE CASCADE
      ) STRICT;
    `);
    ensureApplicationSchema(database);
    chmodSync(path, 0o600);
  } catch (error) {
    database.close();
    throw error;
  }

  const selectOrganization = database.prepare('SELECT * FROM organizations WHERE id = ?');
  const selectMembership = database.prepare('SELECT * FROM memberships WHERE id = ?');
  const selectMembershipBySubject = database.prepare('SELECT * FROM memberships WHERE organization_id = ? AND subject_id = ?');
  const selectSessionMembership = database.prepare(`
    SELECT
      m.id, m.organization_id, m.role, m.status, m.created_at, m.updated_at,
      o.slug, o.display_name, o.status AS organization_status,
      o.created_at AS organization_created_at, o.updated_at AS organization_updated_at
    FROM memberships m
    JOIN organizations o ON o.id = m.organization_id
    WHERE o.hosted_tenant_id = ? AND m.subject_id = ?
      AND o.status = 'active' AND m.status = 'active'
  `);
  const selectEntitlements = database.prepare(`
    SELECT organization_id, route_id, release_id, starts_at, ends_at
    FROM entitlements
    WHERE organization_id = ? AND starts_at <= ? AND (ends_at IS NULL OR ends_at > ?)
    ORDER BY route_id, release_id
  `);
  const selectProgress = database.prepare(`
    SELECT organization_id, member_id, route_id, release_id, stage, status, revision, updated_at
    FROM learner_progress
    WHERE organization_id = ? AND member_id = ?
    ORDER BY route_id, release_id, CASE stage
      WHEN 'observe' THEN 1 WHEN 'map' THEN 2 WHEN 'model' THEN 3 WHEN 'diagnose' THEN 4 ELSE 5 END
  `);
  const selectOneProgress = database.prepare(`
    SELECT status, revision, updated_at FROM learner_progress
    WHERE organization_id = ? AND member_id = ? AND route_id = ? AND release_id = ? AND stage = ?
  `);
  const selectActiveEntitlement = database.prepare(`
    SELECT 1 AS allowed FROM entitlements
    WHERE organization_id = ? AND route_id = ? AND release_id = ? AND starts_at <= ? AND (ends_at IS NULL OR ends_at > ?)
  `);
  const selectIdempotency = database.prepare(`
    SELECT request_sha256, response_status, response_body, expires_at
    FROM idempotency
    WHERE organization_id = ? AND member_id = ? AND operation = ? AND idempotency_key = ?
  `);

  const requireActor = (actorMemberId, organizationId, allowedRoles = null) => {
    const actor = selectMembership.get(actorMemberId);
    if (!actor || actor.organization_id !== organizationId || actor.status !== 'active') fail('SaaS actor is not an active organization member');
    const organization = selectOrganization.get(organizationId);
    if (!organization || organization.status !== 'active') fail('SaaS organization is not active');
    if (allowedRoles && !allowedRoles.has(actor.role)) fail('SaaS actor is not authorized');
    return { actor, organization };
  };

  const writeProgress = (actorMemberId, progress, now) => {
    requireActor(actorMemberId, progress.organizationId);
    if (actorMemberId !== progress.memberId) fail('members may only update their own learner progress');
    if (!selectActiveEntitlement.get(progress.organizationId, progress.routeId, progress.releaseId, now, now)) {
      fail('learner route is not entitled');
    }
    const existing = selectOneProgress.get(
      progress.organizationId,
      progress.memberId,
      progress.routeId,
      progress.releaseId,
      progress.stage,
    );
    const currentRevision = existing ? Number(existing.revision) : 0;
    if (currentRevision !== progress.expectedRevision) fail('learner progress revision conflict');
    const nextRevision = currentRevision + 1;
    if (existing) {
      database.prepare(`
        UPDATE learner_progress SET status = ?, revision = ?, updated_at = ?
        WHERE organization_id = ? AND member_id = ? AND route_id = ? AND release_id = ? AND stage = ?
      `).run(
        progress.status,
        nextRevision,
        now,
        progress.organizationId,
        progress.memberId,
        progress.routeId,
        progress.releaseId,
        progress.stage,
      );
    } else {
      database.prepare(`
        INSERT INTO learner_progress(organization_id, member_id, route_id, release_id, stage, status, revision, updated_at)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
      `).run(
        progress.organizationId,
        progress.memberId,
        progress.routeId,
        progress.releaseId,
        progress.stage,
        progress.status,
        nextRevision,
        now,
      );
    }
    return Object.freeze({
      organization_id: progress.organizationId,
      member_id: progress.memberId,
      route_id: progress.routeId,
      release_id: progress.releaseId,
      stage: progress.stage,
      status: progress.status,
      revision: nextRevision,
      updated_at: now,
    });
  };

  const state = {
    descriptor: Object.freeze({ contract: SAAS_CONTROL_PLANE_CONTRACT, kind: 'sqlite-reference', production_ready: false }),
    bootstrapOrganization(organizationInput, ownerInput, nowSeconds) {
      ensureOpen();
      const organization = validateOrganizationDraft(organizationInput);
      const owner = validateMembershipDraft(ownerInput);
      const now = validateNow(nowSeconds);
      if (owner.organizationId !== organization.id || owner.role !== 'owner') fail('bootstrap owner is invalid');
      return transaction(database, () => {
        database.prepare('INSERT INTO organizations(id, slug, display_name, status, created_at, updated_at) VALUES(?, ?, ?, ?, ?, ?)')
          .run(organization.id, organization.slug, organization.displayName, 'active', now, now);
        database.prepare('INSERT INTO memberships(id, organization_id, subject_id, role, status, created_at, updated_at) VALUES(?, ?, ?, ?, ?, ?, ?)')
          .run(owner.id, owner.organizationId, owner.subjectId, owner.role, 'active', now, now);
        return Object.freeze({
          organization: publicOrganization(selectOrganization.get(organization.id)),
          membership: publicMembership(selectMembership.get(owner.id)),
        });
      });
    },
    bindHostedTenant(actorMemberId, bindingInput, nowSeconds) {
      ensureOpen();
      const binding = validateHostedTenantBinding(bindingInput);
      const now = validateNow(nowSeconds);
      return transaction(database, () => {
        const { organization } = requireActor(actorMemberId, binding.organizationId, OWNER_ROLES);
        if (organization.hosted_tenant_id !== null && organization.hosted_tenant_id !== binding.hostedTenantId) {
          fail('hosted tenant binding is immutable');
        }
        if (organization.hosted_tenant_id === null) {
          try {
            database.prepare('UPDATE organizations SET hosted_tenant_id = ?, updated_at = ? WHERE id = ?')
              .run(binding.hostedTenantId, now, binding.organizationId);
          } catch (error) {
            if (/UNIQUE constraint failed/.test(String(error?.message ?? error))) fail('hosted tenant is already bound');
            throw error;
          }
        }
        return Object.freeze({ organization_id: binding.organizationId, hosted_tenant_id: binding.hostedTenantId });
      });
    },
    resolveSession(hostedTenantInput, subjectInput, nowSeconds) {
      ensureOpen();
      validateNow(nowSeconds);
      const identity = validateSessionIdentity(hostedTenantInput, subjectInput);
      const row = selectSessionMembership.get(identity.hostedTenantId, identity.subjectId);
      if (!row) return null;
      return Object.freeze({
        organization: publicOrganization({
          id: row.organization_id,
          slug: row.slug,
          display_name: row.display_name,
          status: row.organization_status,
          created_at: row.organization_created_at,
          updated_at: row.organization_updated_at,
        }),
        membership: publicMembership(row),
      });
    },
    addMembership(actorMemberId, memberInput, nowSeconds) {
      ensureOpen();
      const member = validateMembershipDraft(memberInput);
      const now = validateNow(nowSeconds);
      return transaction(database, () => {
        const { actor } = requireActor(actorMemberId, member.organizationId, ADMIN_ROLES);
        if (member.role === 'owner' && actor.role !== 'owner') fail('only an owner may add another owner');
        if (selectMembershipBySubject.get(member.organizationId, member.subjectId)) fail('membership subject already exists in organization');
        database.prepare('INSERT INTO memberships(id, organization_id, subject_id, role, status, created_at, updated_at) VALUES(?, ?, ?, ?, ?, ?, ?)')
          .run(member.id, member.organizationId, member.subjectId, member.role, 'active', now, now);
        return publicMembership(selectMembership.get(member.id));
      });
    },
    grantEntitlement(actorMemberId, entitlementInput, nowSeconds) {
      ensureOpen();
      const entitlement = validateEntitlementDraft(entitlementInput);
      const now = validateNow(nowSeconds);
      return transaction(database, () => {
        requireActor(actorMemberId, entitlement.organizationId, ADMIN_ROLES);
        database.prepare(`
          INSERT INTO entitlements(organization_id, route_id, release_id, starts_at, ends_at, created_at, updated_at)
          VALUES(?, ?, ?, ?, ?, ?, ?)
          ON CONFLICT(organization_id, route_id, release_id) DO UPDATE SET
            starts_at = excluded.starts_at,
            ends_at = excluded.ends_at,
            updated_at = excluded.updated_at
        `).run(
          entitlement.organizationId,
          entitlement.routeId,
          entitlement.releaseId,
          entitlement.startsAt,
          entitlement.endsAt,
          now,
          now,
        );
        return Object.freeze({
          organization_id: entitlement.organizationId,
          route_id: entitlement.routeId,
          release_id: entitlement.releaseId,
          starts_at: entitlement.startsAt,
          ends_at: entitlement.endsAt,
        });
      });
    },
    recordProgress(actorMemberId, progressInput, nowSeconds) {
      ensureOpen();
      const progress = validateProgressDraft(progressInput);
      const now = validateNow(nowSeconds);
      return transaction(database, () => writeProgress(actorMemberId, progress, now));
    },
    recordProgressIdempotent(actorMemberId, progressInput, idempotencyInput, nowSeconds) {
      ensureOpen();
      const progress = validateProgressDraft(progressInput);
      const idempotency = validateIdempotencyInput(idempotencyInput);
      const now = validateNow(nowSeconds);
      return transaction(database, () => {
        requireActor(actorMemberId, progress.organizationId);
        database.prepare(`
          DELETE FROM idempotency
          WHERE organization_id = ? AND member_id = ? AND operation = ? AND idempotency_key = ? AND expires_at <= ?
        `).run(progress.organizationId, actorMemberId, idempotency.operation, idempotency.key, now);
        const replay = selectIdempotency.get(progress.organizationId, actorMemberId, idempotency.operation, idempotency.key);
        if (replay) {
          if (replay.request_sha256 !== idempotency.requestSha256) fail('idempotency key conflict');
          const parsed = parseStrictJson(replay.response_body, 'stored SaaS idempotency response');
          return Object.freeze({ replayed: true, progress: Object.freeze(parsed) });
        }
        const stored = writeProgress(actorMemberId, progress, now);
        const responseBody = canonicalJson(stored);
        database.prepare(`
          INSERT INTO idempotency(
            organization_id, member_id, operation, idempotency_key, request_sha256,
            response_status, response_body, created_at, expires_at
          ) VALUES(?, ?, ?, ?, ?, 200, ?, ?, ?)
        `).run(
          progress.organizationId,
          actorMemberId,
          idempotency.operation,
          idempotency.key,
          idempotency.requestSha256,
          responseBody,
          now,
          now + idempotency.ttlSeconds,
        );
        return Object.freeze({ replayed: false, progress: stored });
      });
    },
    dashboard(actorMemberId, nowSeconds) {
      ensureOpen();
      const now = validateNow(nowSeconds);
      const actor = selectMembership.get(actorMemberId);
      if (!actor) fail('SaaS actor is not an active organization member');
      const { organization } = requireActor(actorMemberId, actor.organization_id);
      const entitlements = selectEntitlements.all(actor.organization_id, now, now).map((row) => Object.freeze({
        organization_id: row.organization_id,
        route_id: row.route_id,
        release_id: row.release_id,
        starts_at: Number(row.starts_at),
        ends_at: row.ends_at === null ? null : Number(row.ends_at),
      }));
      const progress = selectProgress.all(actor.organization_id, actor.id).map((row) => Object.freeze({
        organization_id: row.organization_id,
        member_id: row.member_id,
        route_id: row.route_id,
        release_id: row.release_id,
        stage: row.stage,
        status: row.status,
        revision: Number(row.revision),
        updated_at: Number(row.updated_at),
      }));
      return Object.freeze({
        contract: SAAS_DASHBOARD_CONTRACT,
        generated_at: now,
        organization: publicOrganization(organization),
        membership: publicMembership(actor),
        entitlements,
        progress,
      });
    },
    health() {
      ensureOpen();
      const metadata = database.prepare('SELECT value FROM metadata WHERE key = ?').get('contract');
      if (!metadata || metadata.value !== SAAS_STATE_CONTRACT) fail('SaaS state health check failed');
      const columns = database.prepare('PRAGMA table_info(organizations)').all();
      if (!columns.some((column) => column.name === 'hosted_tenant_id')) fail('SaaS state health check failed');
      return Object.freeze({ status: 'ok', ...state.descriptor });
    },
    close() {
      if (!closed) {
        closed = true;
        database.close();
      }
    },
  };
  return Object.freeze(state);
}
