CREATE TABLE principia_atlas_saas_metadata (
  key text PRIMARY KEY,
  value text NOT NULL
);

INSERT INTO principia_atlas_saas_metadata(key, value)
VALUES ('contract', 'principia-atlas-saas-state/0.1');

CREATE TABLE principia_atlas_saas_organizations (
  id text PRIMARY KEY,
  slug text NOT NULL UNIQUE,
  display_name text NOT NULL,
  status text NOT NULL CHECK (status IN ('active', 'suspended')),
  created_at bigint NOT NULL CHECK (created_at >= 0),
  updated_at bigint NOT NULL CHECK (updated_at >= created_at)
);

CREATE TABLE principia_atlas_saas_memberships (
  id text PRIMARY KEY,
  organization_id text NOT NULL REFERENCES principia_atlas_saas_organizations(id) ON DELETE CASCADE,
  subject_id text NOT NULL,
  role text NOT NULL CHECK (role IN ('owner', 'admin', 'facilitator', 'learner')),
  status text NOT NULL CHECK (status IN ('active', 'disabled')),
  created_at bigint NOT NULL CHECK (created_at >= 0),
  updated_at bigint NOT NULL CHECK (updated_at >= created_at),
  UNIQUE (organization_id, subject_id),
  UNIQUE (id, organization_id)
);

CREATE INDEX principia_atlas_saas_memberships_org
ON principia_atlas_saas_memberships(organization_id, status, role);

CREATE TABLE principia_atlas_saas_entitlements (
  organization_id text NOT NULL REFERENCES principia_atlas_saas_organizations(id) ON DELETE CASCADE,
  route_id text NOT NULL CHECK (route_id IN ('refrigerator-v1', 'distributed-information-v1')),
  release_id text NOT NULL,
  starts_at bigint NOT NULL CHECK (starts_at >= 0),
  ends_at bigint CHECK (ends_at IS NULL OR ends_at > starts_at),
  created_at bigint NOT NULL CHECK (created_at >= 0),
  updated_at bigint NOT NULL CHECK (updated_at >= created_at),
  PRIMARY KEY (organization_id, route_id, release_id)
);

CREATE INDEX principia_atlas_saas_entitlements_active
ON principia_atlas_saas_entitlements(organization_id, starts_at, ends_at);

CREATE TABLE principia_atlas_saas_learner_progress (
  organization_id text NOT NULL REFERENCES principia_atlas_saas_organizations(id) ON DELETE CASCADE,
  member_id text NOT NULL,
  route_id text NOT NULL CHECK (route_id IN ('refrigerator-v1', 'distributed-information-v1')),
  release_id text NOT NULL,
  stage text NOT NULL CHECK (stage IN ('observe', 'map', 'model', 'diagnose', 'redesign')),
  status text NOT NULL CHECK (status IN ('in_progress', 'completed')),
  revision bigint NOT NULL CHECK (revision > 0),
  updated_at bigint NOT NULL CHECK (updated_at >= 0),
  PRIMARY KEY (organization_id, member_id, route_id, release_id, stage),
  FOREIGN KEY (member_id, organization_id)
    REFERENCES principia_atlas_saas_memberships(id, organization_id)
    ON DELETE CASCADE
);
