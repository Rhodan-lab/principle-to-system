import { chmodSync, lstatSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { DatabaseSync } from 'node:sqlite';

import { fail } from '../hosted/strict_json.mjs';
import {
  SAAS_CONTROL_PLANE_CONTRACT,
  SAAS_DASHBOARD_CONTRACT,
  SAAS_STATE_CONTRACT,
  publicMembership,
  publicOrganization,
  validateEntitlementDraft,
  validateMembershipDraft,
  validateNow,
  validateOrganizationDraft,
  validateProgressDraft,
} from './domain.mjs';

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

export function openSaasControlPlane(pathInput, { busyTimeoutMs = 5000 } = {}) {
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
        UNIQUE(organization_id, subject_id)
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
        member_id TEXT NOT NULL REFERENCES memberships(id) ON DELETE CASCADE,
        route_id TEXT NOT NULL,
        release_id TEXT NOT NULL,
        stage TEXT NOT NULL CHECK(stage IN ('observe', 'map', 'model', 'diagnose', 'redesign')),
        status TEXT NOT NULL CHECK(status IN ('in_progress', 'completed')),
        revision INTEGER NOT NULL,
        updated_at INTEGER NOT NULL,
        PRIMARY KEY(organization_id, member_id, route_id, release_id, stage)
      ) STRICT;
    `);
    const metadata = database.prepare('SELECT value FROM metadata WHERE key = ?').get('contract');
    if (!metadata) database.prepare('INSERT INTO metadata(key, value) VALUES(?, ?)').run('contract', SAAS_STATE_CONTRACT);
    else if (metadata.value !== SAAS_STATE_CONTRACT) fail('SaaS state schema contract is incompatible');
    chmodSync(path, 0o600);
  } catch (error) {
    database.close();
    throw error;
  }

  const selectOrganization = database.prepare('SELECT * FROM organizations WHERE id = ?');
  const selectMembership = database.prepare('SELECT * FROM memberships WHERE id = ?');
  const selectMembershipBySubject = database.prepare('SELECT * FROM memberships WHERE organization_id = ? AND subject_id = ?');
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

  const requireActor = (actorMemberId, organizationId, allowedRoles = null) => {
    const actor = selectMembership.get(actorMemberId);
    if (!actor || actor.organization_id !== organizationId || actor.status !== 'active') fail('SaaS actor is not an active organization member');
    const organization = selectOrganization.get(organizationId);
    if (!organization || organization.status !== 'active') fail('SaaS organization is not active');
    if (allowedRoles && !allowedRoles.has(actor.role)) fail('SaaS actor is not authorized');
    return { actor, organization };
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
    addMembership(actorMemberId, memberInput, nowSeconds) {
      ensureOpen();
      const member = validateMembershipDraft(memberInput);
      const now = validateNow(nowSeconds);
      const { actor } = requireActor(actorMemberId, member.organizationId, new Set(['owner', 'admin']));
      if (member.role === 'owner' && actor.role !== 'owner') fail('only an owner may add another owner');
      if (selectMembershipBySubject.get(member.organizationId, member.subjectId)) fail('membership subject already exists in organization');
      database.prepare('INSERT INTO memberships(id, organization_id, subject_id, role, status, created_at, updated_at) VALUES(?, ?, ?, ?, ?, ?, ?)')
        .run(member.id, member.organizationId, member.subjectId, member.role, 'active', now, now);
      return publicMembership(selectMembership.get(member.id));
    },
    grantEntitlement(actorMemberId, entitlementInput, nowSeconds) {
      ensureOpen();
      const entitlement = validateEntitlementDraft(entitlementInput);
      const now = validateNow(nowSeconds);
      requireActor(actorMemberId, entitlement.organizationId, new Set(['owner', 'admin']));
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
    },
    recordProgress(actorMemberId, progressInput, nowSeconds) {
      ensureOpen();
      const progress = validateProgressDraft(progressInput);
      const now = validateNow(nowSeconds);
      requireActor(actorMemberId, progress.organizationId);
      if (actorMemberId !== progress.memberId) fail('members may only update their own learner progress');
      if (!selectActiveEntitlement.get(progress.organizationId, progress.routeId, progress.releaseId, now, now)) {
        fail('learner route is not entitled');
      }
      return transaction(database, () => {
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
