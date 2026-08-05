import { exactKeys, fail } from '../hosted/strict_json.mjs';

export const SAAS_CONTROL_PLANE_CONTRACT = 'principia-atlas-saas-control-plane/0.1';
export const SAAS_DASHBOARD_CONTRACT = 'principia-atlas-saas-dashboard/0.1';
export const SAAS_STATE_CONTRACT = 'principia-atlas-saas-state/0.1';

const ORGANIZATION_ID = /^org_[A-Za-z0-9_-]{16,64}$/;
const MEMBER_ID = /^mem_[A-Za-z0-9_-]{16,64}$/;
const SUBJECT_ID = /^oidc:[A-Za-z0-9_-]{43}$/;
const ORGANIZATION_SLUG = /^[a-z][a-z0-9-]{1,62}$/;
const RELEASE_ID = /^[A-Za-z0-9][A-Za-z0-9._:@+-]{7,199}$/;
const DISPLAY_NAME_CONTROL = /[\u0000-\u001f\u007f]/;
const ROLES = new Set(['owner', 'admin', 'facilitator', 'learner']);
const ORGANIZATION_STATUSES = new Set(['active', 'suspended']);
const MEMBERSHIP_STATUSES = new Set(['active', 'disabled']);
const ROUTES = new Set(['refrigerator-v1', 'distributed-information-v1']);
const STAGES = new Set(['observe', 'map', 'model', 'diagnose', 'redesign']);
const PROGRESS_STATUSES = new Set(['in_progress', 'completed']);

function identifier(value, pattern, label) {
  if (typeof value !== 'string' || !pattern.test(value)) fail(`${label} is invalid`);
  return value;
}

function enumValue(value, allowed, label) {
  if (typeof value !== 'string' || !allowed.has(value)) fail(`${label} is invalid`);
  return value;
}

export function integer(value, label, minimum = 0) {
  if (!Number.isSafeInteger(value) || value < minimum) fail(`${label} is invalid`);
  return value;
}

function displayName(value) {
  if (typeof value !== 'string' || value.trim() !== value || value.length < 2 || value.length > 120 || DISPLAY_NAME_CONTROL.test(value)) {
    fail('organization display name is invalid');
  }
  return value;
}

export function validateOrganizationDraft(value) {
  exactKeys(value, ['id', 'slug', 'display_name'], 'organization');
  return Object.freeze({
    id: identifier(value.id, ORGANIZATION_ID, 'organization identifier'),
    slug: identifier(value.slug, ORGANIZATION_SLUG, 'organization slug'),
    displayName: displayName(value.display_name),
  });
}

export function validateMembershipDraft(value) {
  exactKeys(value, ['id', 'organization_id', 'subject_id', 'role'], 'membership');
  return Object.freeze({
    id: identifier(value.id, MEMBER_ID, 'membership identifier'),
    organizationId: identifier(value.organization_id, ORGANIZATION_ID, 'organization identifier'),
    subjectId: identifier(value.subject_id, SUBJECT_ID, 'membership subject'),
    role: enumValue(value.role, ROLES, 'membership role'),
  });
}

export function validateEntitlementDraft(value) {
  exactKeys(value, ['organization_id', 'route_id', 'release_id', 'starts_at', 'ends_at'], 'entitlement');
  const startsAt = integer(value.starts_at, 'entitlement start time');
  const endsAt = value.ends_at === null ? null : integer(value.ends_at, 'entitlement end time');
  if (endsAt !== null && endsAt <= startsAt) fail('entitlement window is invalid');
  return Object.freeze({
    organizationId: identifier(value.organization_id, ORGANIZATION_ID, 'organization identifier'),
    routeId: enumValue(value.route_id, ROUTES, 'route identifier'),
    releaseId: identifier(value.release_id, RELEASE_ID, 'release identifier'),
    startsAt,
    endsAt,
  });
}

export function validateProgressDraft(value) {
  exactKeys(value, [
    'organization_id', 'member_id', 'route_id', 'release_id', 'stage', 'status', 'expected_revision',
  ], 'learner progress');
  return Object.freeze({
    organizationId: identifier(value.organization_id, ORGANIZATION_ID, 'organization identifier'),
    memberId: identifier(value.member_id, MEMBER_ID, 'membership identifier'),
    routeId: enumValue(value.route_id, ROUTES, 'route identifier'),
    releaseId: identifier(value.release_id, RELEASE_ID, 'release identifier'),
    stage: enumValue(value.stage, STAGES, 'learner stage'),
    status: enumValue(value.status, PROGRESS_STATUSES, 'learner progress status'),
    expectedRevision: integer(value.expected_revision, 'learner progress expected revision'),
  });
}

export function validateNow(value) {
  return integer(value, 'current time');
}

export function organizationStatus(value) {
  return enumValue(value, ORGANIZATION_STATUSES, 'organization status');
}

export function membershipStatus(value) {
  return enumValue(value, MEMBERSHIP_STATUSES, 'membership status');
}

export function role(value) {
  return enumValue(value, ROLES, 'membership role');
}

export function publicOrganization(row) {
  return Object.freeze({
    id: row.id,
    slug: row.slug,
    display_name: row.display_name,
    status: row.status,
    created_at: Number(row.created_at),
    updated_at: Number(row.updated_at),
  });
}

export function publicMembership(row) {
  return Object.freeze({
    id: row.id,
    organization_id: row.organization_id,
    role: row.role,
    status: row.status,
    created_at: Number(row.created_at),
    updated_at: Number(row.updated_at),
  });
}
