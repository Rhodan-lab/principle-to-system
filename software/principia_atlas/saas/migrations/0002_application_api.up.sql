-- Principia & Atlas SaaS application API state.
-- This migration is roll-forward only and must remain immutable after publication.

ALTER TABLE principia_atlas_saas_organizations
  ADD COLUMN hosted_tenant_id TEXT;

ALTER TABLE principia_atlas_saas_organizations
  ADD CONSTRAINT principia_atlas_saas_organizations_hosted_tenant_id_format
  CHECK (
    hosted_tenant_id IS NULL
    OR hosted_tenant_id ~ '^[a-z][a-z0-9-]{1,62}$'
  );

CREATE UNIQUE INDEX principia_atlas_saas_organizations_hosted_tenant_unique
  ON principia_atlas_saas_organizations(hosted_tenant_id)
  WHERE hosted_tenant_id IS NOT NULL;

CREATE INDEX principia_atlas_saas_memberships_subject_lookup
  ON principia_atlas_saas_memberships(subject_id, organization_id, status);

CREATE TABLE principia_atlas_saas_idempotency (
  organization_id TEXT NOT NULL,
  member_id TEXT NOT NULL,
  operation TEXT NOT NULL,
  idempotency_key TEXT NOT NULL,
  request_sha256 TEXT NOT NULL,
  response_status INTEGER NOT NULL,
  response_body TEXT NOT NULL,
  created_at BIGINT NOT NULL,
  expires_at BIGINT NOT NULL,
  PRIMARY KEY(organization_id, member_id, operation, idempotency_key),
  CONSTRAINT principia_atlas_saas_idempotency_member_fk
    FOREIGN KEY(member_id, organization_id)
    REFERENCES principia_atlas_saas_memberships(id, organization_id)
    ON DELETE CASCADE,
  CONSTRAINT principia_atlas_saas_idempotency_operation_format
    CHECK(operation ~ '^[a-z][a-z0-9._:-]{2,79}$'),
  CONSTRAINT principia_atlas_saas_idempotency_key_format
    CHECK(idempotency_key ~ '^[A-Za-z0-9_-]{16,128}$'),
  CONSTRAINT principia_atlas_saas_idempotency_request_digest_format
    CHECK(request_sha256 ~ '^[0-9a-f]{64}$'),
  CONSTRAINT principia_atlas_saas_idempotency_response_status_range
    CHECK(response_status BETWEEN 200 AND 599),
  CONSTRAINT principia_atlas_saas_idempotency_response_size
    CHECK(octet_length(response_body) BETWEEN 2 AND 16384),
  CONSTRAINT principia_atlas_saas_idempotency_time_order
    CHECK(expires_at > created_at)
);

CREATE INDEX principia_atlas_saas_idempotency_expiry
  ON principia_atlas_saas_idempotency(expires_at);

UPDATE principia_atlas_saas_metadata
SET value = 'principia-atlas-saas-state/0.2'
WHERE key = 'contract'
  AND value = 'principia-atlas-saas-state/0.1';
