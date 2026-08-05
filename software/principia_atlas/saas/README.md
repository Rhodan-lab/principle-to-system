---
title: Principia & Atlas public SaaS control plane
status: in-development
last_reviewed: 2026-08-05
content_license: CC-BY-4.0
---

# Principia & Atlas public SaaS control plane

This directory is the beginning of the public SaaS product layer. It does not replace the deterministic learner packages, Atlas exact-revision workspace, release pipeline, hosted content runtime, or browser OIDC edge.

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

## Implemented control-plane kernel

The shared domain implements:

- organization bootstrap with exactly one initial owner;
- pairwise OIDC subject to internal membership mapping;
- roles `owner`, `admin`, `facilitator`, and `learner`;
- tenant-isolated route entitlements bound to an exact release identifier;
- learner-owned progress for `observe`, `map`, `model`, `diagnose`, and `redesign`;
- optimistic revision checks so stale devices cannot silently overwrite newer progress;
- sanitized dashboard output that excludes pairwise subject identifiers;
- an stdin-only local mutation CLI so identity-bearing input does not enter process arguments.

## Storage adapters

### SQLite reference

The restrictive SQLite backend freezes domain behavior and supports deterministic local tests. It reports:

```json
{
  "kind": "sqlite-reference",
  "production_ready": false
}
```

It is not the selected public production database.

### PostgreSQL multi-instance adapter

The PostgreSQL adapter implements the same domain operations through an injected connection pool. It provides:

- digest-locked, ordered SQL migrations;
- a durable migration ledger;
- one transaction-scoped advisory lock for migration application;
- idempotent concurrent startup migration attempts;
- serializable mutation transactions;
- bounded retry for serialization failures and deadlocks;
- repeatable-read dashboard snapshots;
- composite tenant/member foreign keys;
- exact active route-release entitlement checks;
- atomic optimistic progress revisions;
- multi-instance concurrency semantics.

It reports:

```json
{
  "kind": "postgresql",
  "durable": true,
  "multi_instance": true,
  "database_ready": true,
  "production_ready": false
}
```

`database_ready` means the persistence adapter has passed real PostgreSQL migration, parity, isolation, and concurrency tests. It does not mean the full SaaS product is ready for public use.

## Migration policy

Migrations are roll-forward and immutable. The migration ledger stores each exact source digest. Startup fails when an applied version is unknown or its digest differs from the repository.

The migration runner applies schema and ledger updates inside one transaction. A failed migration must leave no partially created accepted objects. Destructive down-migrations are intentionally not supplied for databases containing customer data.

Before production deployment:

1. run migrations as a dedicated migration identity;
2. remove schema-creation privileges from the normal application identity;
3. verify the migration ledger against repository source;
4. run a backup and restore drill against a separate database;
5. deploy application instances only after migration verification succeeds.

## PostgreSQL connection boundary

The adapter accepts a pool compatible with the `node-postgres` query and connection interface but does not import one vendor-specific cloud SDK. The future application layer owns pool construction and secret loading.

Operational requirements:

- credentials must come from a secret manager or protected file, not command arguments or committed configuration;
- TLS certificate verification is required outside a reviewed private network;
- the application role receives only required DML privileges;
- the migration role is separate and not used for web requests;
- connection pools must have bounded size, acquisition timeout, statement timeout, and idle timeout;
- database URLs must never appear in audit events or learner-visible errors;
- production backups must be encrypted, access-controlled, retained by policy, and restore-tested.

## Local SQLite reference workflow

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

Bootstrap without placing the subject in argv:

```bash
cat /private/bootstrap.json | \
node software/principia_atlas/saas/cli.mjs bootstrap \
  --state /private/principia-atlas-saas.sqlite
```

Read a sanitized learner dashboard:

```bash
node software/principia_atlas/saas/cli.mjs dashboard \
  --state /private/principia-atlas-saas.sqlite \
  --actor mem_01PUBLICSAASLEARNER0
```

## Security and privacy boundary

- Raw external OIDC subjects do not belong in SaaS state.
- `subject_id` accepts only the pairwise identifier emitted by the hosted identity boundary.
- Dashboard and mutation results omit the pairwise subject.
- A member may update only their own progress.
- A route must be actively entitled for the exact release before progress can be written.
- Learners and facilitators cannot grant entitlements or add members.
- Organization and membership status must both be active for normal operations.
- Tenant checks and writes execute in the same database transaction.
- Database constraint errors are converted into bounded domain errors rather than exposing SQL or credentials.

## Public SaaS sequence

The work proceeds in bounded vertical slices:

1. **Control-plane kernel — complete.** Organization, membership, entitlement, progress, authorization, and privacy invariants.
2. **PostgreSQL adapter — implemented and under validation.** Migrations, transaction parity, tenant isolation, concurrency, and operational boundaries.
3. **Same-origin application API.** Session-to-membership resolution through the existing OIDC boundary, origin and CSRF enforcement, idempotent mutations, request limits, and audit-safe errors.
4. **Public product shell.** Landing page, login, organization onboarding, Learn/Research dashboard, progress synchronization, and facilitator administration.
5. **Operational beta.** Deployment, domains, TLS, secrets, email delivery, rate limits, monitoring, alerts, retention, backup/restore drills, and incident procedures.
6. **Commercial boundary.** Plan catalog, subscription provider adapter, webhook replay protection, grace periods, and entitlement reconciliation.
7. **Public beta.** A limited cohort with measured usability, accessibility, privacy, reliability, and learning evidence.
8. **General availability.** Only after beta exit criteria and operational ownership are satisfied.

The sequence intentionally does not begin with billing or visual polish. Identity, tenant isolation, exact release entitlement, data minimization, transaction behavior, and recovery must be correct first.

## Not yet claimed

The project still does not provide:

- a public URL;
- a same-origin SaaS application API;
- self-registration or invitations;
- a public browser dashboard;
- email delivery;
- subscriptions or billing;
- production monitoring or support operations;
- a completed production backup and restore drill;
- measured human usability or accessibility results;
- a public-beta or production-readiness claim.
