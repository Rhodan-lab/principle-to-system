---
title: Principia & Atlas public SaaS control plane
status: in-development
last_reviewed: 2026-08-05
content_license: CC-BY-4.0
---

# Principia & Atlas public SaaS control plane

This directory is the public SaaS product layer. It does not replace deterministic learner packages, the Atlas exact-revision workspace, immutable release pipeline, hosted content runtime, or browser OIDC edge.

```text
public browser
  -> trusted browser OIDC edge
      -> loopback SaaS runtime facade
          -> hosted session verifier and shared auth state
          -> same-origin SaaS application API
              -> organizations and memberships
              -> exact release entitlements
              -> learner progress
              -> PostgreSQL
          -> loopback immutable hosted release core
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

A hosted session contains a trusted `tenant_id` and canonical pairwise OIDC subject. A SaaS organization is never inferred from its slug or internal identifier. An owner creates one explicit immutable binding:

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

## Same-origin application API

```text
GET /api/saas/me
GET /api/saas/dashboard
PUT /api/saas/progress/:route/:stage
```

`GET /api/saas/me` returns sanitized organization and membership data, session expiry, and a session-bound CSRF token. It never returns the pairwise subject.

A progress body contains only:

```json
{
  "release_id": "principia-atlas-release:0.5.0-beta.1",
  "status": "completed",
  "expected_revision": 0
}
```

Tenant, organization, membership, role, route, and stage are derived from the trusted session and URL rather than accepted from browser JSON.

### Mutation requirements

Every progress mutation requires:

- exact same-origin `Origin` and `Host` agreement at the application API;
- exact public-origin validation at the browser edge;
- `Content-Type: application/json`;
- a session-bound `X-CSRF-Token`;
- an `Idempotency-Key` of 16–128 URL-safe characters;
- a body no larger than 16 KiB;
- exact JSON keys with no extras;
- an active hosted session and auth-state registration;
- an active SaaS organization and membership;
- an active entitlement for the exact route and release;
- the current expected progress revision.

The browser cannot provide `organization_id`, `member_id`, `subject_id`, or a role.

### Transactional idempotency

The request digest binds route, release, stage, status, and expected revision. The database stores the digest and canonical result in the same transaction as the progress write.

- first use commits one progress mutation and one receipt;
- same key plus same request returns the stored result;
- same key plus different request is rejected;
- failed writes do not leave accepted receipts;
- concurrent PostgreSQL replicas converge on one committed result;
- receipts expire after a bounded TTL and are scoped to organization, member, operation, and key.

## PostgreSQL migration boundary

```text
0001_control_plane.up.sql
0002_application_api.up.sql
```

Migration 2 adds immutable hosted tenant bindings, subject-resolution indexing, transactional idempotency receipts, and state contract `principia-atlas-saas-state/0.2`.

Every migration is SHA-256 locked in the ledger and applied under a transaction-scoped PostgreSQL advisory lock. Unknown versions, changed migration bytes, incomplete migrations, and contract mismatch are rejected.

## Wired runtime boundary

`hosted/saas_runtime.mjs` now composes the application API with the existing hosted session verifier and auth-state authority.

For `/api/saas/*`, it:

1. verifies the signed hosted session cookie;
2. verifies registration and revocation state;
3. passes the trusted session object to the application API;
4. returns canonical bounded JSON.

For all other routes, it forwards only bodyless GET, HEAD, and POST requests to the exact loopback immutable hosted core.

`hosted/browser_edge.mjs` contract `/0.2` now permits one body-bearing route:

```text
PUT /api/saas/progress/:route/:stage
```

Every other proxied request remains bodyless. The edge reads at most 16 KiB and forwards only `Content-Type`, `Idempotency-Key`, and `X-CSRF-Token` for this route.

The runtime-edge smoke signs and registers a real hosted session, resolves a tenant-bound learner through the public edge, writes one progress revision, and proves an identical idempotency retry does not write twice.

Current status:

```json
{
  "application_api_contract_ready": true,
  "runtime_edge_contract_ready": true,
  "production_process_composition_ready": false,
  "public_deployment_ready": false,
  "production_ready": false
}
```

## Security and privacy invariants

- Raw external OIDC subjects never enter the SaaS database.
- Pairwise subjects are accepted only from the trusted identity boundary.
- Pairwise subjects never appear in application responses.
- Membership roles, not browser claims, authorize SaaS operations.
- Tenant and membership resolution occurs before every API response.
- A member may update only their own progress.
- Exact release entitlement is checked inside the write transaction.
- CSRF tokens are HMAC-bound to session ID, tenant, and session expiry.
- Originless mutation requests are rejected at the public edge and runtime API.
- The public edge persists no learner state.
- Database errors are mapped to bounded public error codes.
- Mutation payloads and operator identity documents are not passed through argv.

## Public SaaS sequence

1. **Control-plane kernel** — implemented.
2. **PostgreSQL adapter** — implemented and tested against PostgreSQL.
3. **Application API semantics** — implemented.
4. **Hosted runtime and browser-edge contract composition** — implemented and end-to-end tested.
5. **Production process and deployment composition** — next: PostgreSQL pool startup, secret files, aggregated readiness, manifests, NetworkPolicy, backup and restore.
6. **Public product shell** — landing, login, Learn/Research dashboard, and progress UI.
7. **Organization onboarding and invitations** — token lifecycle, email delivery, and owner safety.
8. **Operational beta** — TLS, rate limits, monitoring, restore drill, and incident procedures.
9. **Commercial boundary** — subscription adapter and entitlement reconciliation.
10. **Public beta and general availability** — only after measured exit criteria.

## Not yet claimed

This layer does not yet provide:

- a public URL or domain;
- a production PostgreSQL runtime process;
- production secret-file composition;
- aggregated SaaS readiness and monitoring;
- updated Kubernetes deployment manifests;
- self-registration or invitations;
- a browser product dashboard;
- email delivery;
- subscriptions or billing;
- a completed backup-and-restore drill;
- measured accessibility, usability, reliability, or learning evidence;
- public-beta or production readiness.
