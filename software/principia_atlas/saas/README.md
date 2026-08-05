---
title: Principia & Atlas public SaaS control plane
status: in-development
last_reviewed: 2026-08-05
content_license: CC-BY-4.0
---

# Principia & Atlas public SaaS control plane

This directory is the public SaaS product layer. It does not replace the deterministic learner packages, Atlas exact-revision workspace, immutable release pipeline, hosted content runtime, or browser OIDC edge.

```text
public browser
  -> trusted browser OIDC edge
  -> hosted session verifier
  -> same-origin SaaS application API
      -> organization and membership authority
      -> exact release entitlements
      -> learner progress
      -> PostgreSQL
  -> immutable hosted release plane
      -> Principia Learn and Atlas Research assets
```

The release plane remains read-only and provenance-bound. Organization and learner state belongs to the SaaS control plane.

## Implemented control-plane semantics

The control plane implements:

- organizations and active/suspended status;
- pairwise OIDC subject to internal membership mapping;
- roles `owner`, `admin`, `facilitator`, and `learner`;
- tenant-isolated route entitlements bound to an exact release identifier;
- learner-owned progress for `observe`, `map`, `model`, `diagnose`, and `redesign`;
- optimistic revisions that reject stale-device overwrites;
- sanitized dashboard output without pairwise subjects;
- SQLite reference persistence for deterministic local semantics;
- PostgreSQL persistence with immutable migrations, serializable mutations, and repeatable-read dashboards.

## Hosted tenant binding

A hosted session contains a trusted `tenant_id` and a canonical pairwise OIDC subject. A SaaS organization is not inferred from its slug or internal identifier. An owner must create one explicit immutable binding:

```json
{
  "organization_id": "org_01PUBLICSAASFOUNDATION",
  "hosted_tenant_id": "principia-school"
}
```

```bash
cat /private/tenant-binding.json | \
node software/principia_atlas/saas/cli.mjs bind-tenant \
  --state /private/principia-atlas-saas.sqlite \
  --actor mem_01PUBLICSAASOWNER000
```

Rules:

- one hosted tenant may bind to only one SaaS organization;
- only an active owner may create the binding;
- repeating the same binding is idempotent;
- replacing an established binding is rejected;
- session resolution requires both the hosted tenant and pairwise subject;
- browser payloads never choose an organization or membership.

## Same-origin application API contract

`application_api.mjs` defines the first browser application API:

```text
GET /api/saas/me
GET /api/saas/dashboard
PUT /api/saas/progress/:route/:stage
```

`GET /api/saas/me` returns the sanitized organization, sanitized membership, session expiry, and a session-bound CSRF token. It does not return the pairwise subject.

A progress request body contains only:

```json
{
  "release_id": "principia-atlas-release:0.4.0-beta.1",
  "status": "completed",
  "expected_revision": 0
}
```

The API derives these fields from the trusted session and URL rather than the browser body:

```text
hosted tenant
organization
membership
member role
route
stage
```

### Mutation requirements

Every progress mutation requires:

- exact same-origin `Origin` and `Host` agreement;
- `Content-Type: application/json`;
- a session-bound `X-CSRF-Token`;
- an `Idempotency-Key` of 16–128 URL-safe characters;
- a body no larger than 16 KiB;
- exact JSON keys with no extras;
- an active membership and organization;
- an active entitlement for the exact route and release;
- the current expected progress revision.

The browser cannot provide `organization_id`, `member_id`, `subject_id`, or a role.

### Transactional idempotency

The request digest binds route, release, stage, status, and expected revision. The database stores the digest and canonical result in the same transaction as the progress write.

- first use of a key commits one progress mutation and one receipt;
- same key plus same request returns the stored result without writing again;
- same key plus different request is rejected;
- failed progress writes do not leave accepted idempotency receipts;
- concurrent PostgreSQL replicas converge on one committed result;
- receipts expire after a bounded TTL and are scoped to organization, member, operation, and key.

## PostgreSQL migration boundary

The migration sequence is roll-forward only:

```text
0001_control_plane.up.sql
0002_application_api.up.sql
```

Migration 2 adds:

- immutable hosted tenant bindings;
- subject-resolution index;
- transactional idempotency receipts;
- state contract `principia-atlas-saas-state/0.2`.

Every migration is SHA-256 locked in the migration ledger and applied under a transaction-scoped PostgreSQL advisory lock. Unknown versions, changed migration bytes, incomplete migrations, and contract mismatch are rejected.

## Current runtime boundary

The application API module is intentionally separated from network composition. This unit freezes and tests the API contract against both storage adapters. The next bounded change connects it to the hosted session verifier and trusted browser edge.

Until that composition is merged:

```json
{
  "application_api_contract_ready": true,
  "public_network_path_ready": false,
  "production_ready": false
}
```

The product must not be described as publicly deployed yet.

## Security and privacy invariants

- Raw external OIDC subjects never enter this database.
- Pairwise subjects are accepted only from the trusted identity boundary.
- Pairwise subjects never appear in application responses.
- Membership roles, not browser claims, authorize SaaS operations.
- Tenant and membership resolution occurs before every API response.
- A member may update only their own progress.
- Exact release entitlement is checked inside the write transaction.
- CSRF tokens are HMAC-bound to session ID, tenant, and session expiry.
- Originless mutation requests are rejected.
- Database errors are mapped to bounded public error codes.
- Mutation payloads and operator identity documents are not passed through argv.

## Public SaaS sequence

1. **Control-plane kernel** — implemented.
2. **PostgreSQL production adapter** — implemented and tested against PostgreSQL.
3. **Application API semantics** — implemented in this unit.
4. **Hosted runtime and browser-edge composition** — next.
5. **Public product shell** — landing, login, Learn/Research dashboard, and progress UI.
6. **Organization onboarding and invitations** — token lifecycle, email delivery, and owner safety.
7. **Operational beta** — deployment, TLS, secrets, rate limits, monitoring, restore drill, and incident procedures.
8. **Commercial boundary** — subscription adapter and entitlement reconciliation.
9. **Public beta and general availability** — only after measured exit criteria.

## Not yet claimed

This layer does not yet provide:

- a public URL or domain;
- runtime wiring from the browser edge to this API;
- self-registration or invitations;
- a browser dashboard;
- email delivery;
- subscriptions or billing;
- production monitoring and support operations;
- a completed backup-and-restore drill;
- measured accessibility, usability, reliability, or learning evidence;
- public-beta or production readiness.
