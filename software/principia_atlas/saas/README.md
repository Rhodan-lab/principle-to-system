---
title: Principia & Atlas public SaaS control plane
status: in-development
last_reviewed: 2026-08-05
content_license: CC-BY-4.0
---

# Principia & Atlas public SaaS control plane

This directory is the beginning of the public SaaS product layer. It does not replace the existing deterministic learner packages, Atlas exact-revision workspace, release pipeline, hosted content runtime, or browser OIDC edge.

The public product is split deliberately:

```text
public web experience
  -> browser OIDC edge
  -> SaaS control plane
      -> organizations, memberships, entitlements, learner progress
  -> immutable hosted release plane
      -> Principia Learn and Atlas Research assets
```

The hosted release plane remains read-only and provenance-bound. Learner and organization state belongs to the SaaS control plane instead of being added to the immutable content server.

## Current implemented unit

The current control-plane kernel implements:

- organization bootstrap with exactly one initial owner;
- pairwise OIDC subject to internal membership mapping;
- roles `owner`, `admin`, `facilitator`, and `learner`;
- tenant-isolated route entitlements bound to an exact release identifier;
- learner-owned progress for the five stages `observe`, `map`, `model`, `diagnose`, and `redesign`;
- optimistic revision checks so stale devices cannot silently overwrite newer progress;
- sanitized dashboard output that excludes pairwise subject identifiers;
- durable local restart behavior through a restrictive SQLite reference database;
- an stdin-only mutation CLI so identity-bearing input does not enter process arguments.

The reference backend reports:

```json
{
  "kind": "sqlite-reference",
  "production_ready": false
}
```

SQLite is used to freeze domain behavior and provide deterministic local tests. It is not the selected public production database.

## Local reference workflow

Create a private bootstrap document:

```json
{
  "organization": {
    "id": "org_01PUBLICSAASFOUNDATION",
    "slug": "principia-lab",
    "display_name": "Principia Lab"
  },
  "owner": {
    "id": "mem_01PUBLICSAASOWNER000",
    "organization_id": "org_01PUBLICSAASFOUNDATION",
    "subject_id": "oidc:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "role": "owner"
  }
}
```

Bootstrap the reference state without placing the subject in argv:

```bash
cat /private/bootstrap.json | \
node software/principia_atlas/saas/cli.mjs bootstrap \
  --state /private/principia-atlas-saas.sqlite
```

Add a member:

```bash
cat /private/member.json | \
node software/principia_atlas/saas/cli.mjs add-member \
  --state /private/principia-atlas-saas.sqlite \
  --actor mem_01PUBLICSAASOWNER000
```

Grant one exact route release:

```json
{
  "organization_id": "org_01PUBLICSAASFOUNDATION",
  "route_id": "refrigerator-v1",
  "release_id": "principia-atlas-release:0.2.0-beta.1",
  "starts_at": 1800000000,
  "ends_at": null
}
```

```bash
cat /private/entitlement.json | \
node software/principia_atlas/saas/cli.mjs grant-entitlement \
  --state /private/principia-atlas-saas.sqlite \
  --actor mem_01PUBLICSAASOWNER000
```

Read a sanitized learner dashboard:

```bash
node software/principia_atlas/saas/cli.mjs dashboard \
  --state /private/principia-atlas-saas.sqlite \
  --actor mem_01PUBLICSAASLEARNER0
```

## Security and privacy boundary

- Raw external OIDC subjects do not belong in this database.
- The `subject_id` field accepts only the pairwise identifier emitted by the existing hosted identity boundary.
- Mutation payloads are read from stdin rather than command arguments.
- Dashboard and mutation results omit the pairwise subject.
- A member may update only their own progress.
- A route must be actively entitled for the exact release before progress can be written.
- Learners and facilitators cannot grant entitlements or add members.
- Organization and membership status must both be active for normal operations.
- The database file is created with mode `0600`; symlink state paths and irregular parents are rejected.

## Public SaaS sequence

The work proceeds in bounded vertical slices:

1. **Control-plane kernel** — organization, membership, entitlement, progress, authorization, and privacy invariants. This directory now contains the first implementation.
2. **PostgreSQL production adapter** — explicit migrations, transaction equivalence, tenant isolation, backup/restore, and migration rollback tests.
3. **Same-origin application API** — session-to-membership resolution through the existing OIDC boundary, CSRF and origin enforcement, idempotent mutations, and audit-safe errors.
4. **Public product shell** — landing page, login, organization onboarding, Learn/Research dashboard, progress synchronization, and facilitator administration.
5. **Operational beta** — deployment, domains, TLS, secrets, email delivery, rate limits, monitoring, alerts, retention, and incident procedures.
6. **Commercial boundary** — plan catalog, subscription provider adapter, webhook replay protection, grace periods, and entitlement reconciliation.
7. **Public beta** — a limited cohort with measured usability, accessibility, privacy, reliability, and learning evidence.
8. **General availability** — only after beta exit criteria and operational ownership are satisfied.

The sequence intentionally does not begin with billing or visual polish. Identity, tenant isolation, exact release entitlement, data minimization, and recovery must be correct first.

## Not yet claimed

This kernel does not yet provide:

- a public URL;
- PostgreSQL or multi-region persistence;
- self-registration or invitations;
- a browser dashboard;
- email delivery;
- subscriptions or billing;
- production monitoring or support operations;
- measured human usability or accessibility results;
- a public-beta or production-readiness claim.
