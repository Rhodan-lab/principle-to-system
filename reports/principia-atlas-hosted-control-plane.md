---
title: Principia & Atlas durable authenticated hosted runtime
status: implemented-durable-auth-read-only-runtime
scope: product-integration
---

# Principia & Atlas durable authenticated hosted runtime

The hosted layer combines an authenticated tenant boundary, durable authentication coordination, and read-only serving of already promoted Principia & Atlas releases. It does not change the immutable Principia learning package or Atlas knowledge-status authority.

## Architecture

- Python verifies promotion history and produces a sealed hosted release catalog.
- Python verifies every catalog-referenced release archive and materializes only its `product/` subtree into a content-addressed store.
- Store contract `principia-atlas-hosted-store/0.1` seals catalog identity, release identities, archive digest, object root, and every file path, size, and SHA-256 digest.
- Store publication is atomic and rollback-capable.
- Node.js verifies the catalog, tenant policy, store manifest, exact file set, symlink boundary, and every file digest at startup.
- Verified file bytes are retained in memory; request handling does not reopen release files or parse ZIP archives.
- A trusted external identity adapter issues a short-lived signed assertion.
- Assertion claim and revocable session registration occur atomically in shared authentication state.
- Tenant identity comes only from the verified signed session and registered server-side session record.
- Catalog and asset access are filtered by allowed release channel, route, and optional exact-version pins.

## Durable authentication coordination

Contract `principia-atlas-hosted-auth-state/0.1` has an in-memory implementation for programmatic loopback tests and a SQLite implementation for the hosted server.

The SQLite backend uses strict tables, WAL mode, full synchronous writes, a bounded busy timeout, restrictive file permissions, and a sealed schema-contract row. It stores consumed assertion identifiers, registered sessions, revocation timestamps, and bounded exchange-rate windows. Assertion replay protection, session validity, logout revocation, and rate limiting therefore remain consistent across processes opening the same state file and across process restarts.

Session contract `principia-atlas-hosted-session/0.2` introduces a random session identifier independent from the identity assertion identifier. Logout persists revocation before clearing the browser cookie. Operators can prune expired state or revoke an exact session or all active sessions for one tenant-subject pair through a bounded CLI that does not list session contents.

`/healthz` reports process liveness. `/readyz` checks the authentication state backend and fails with `503` when shared state is unavailable.

## Authenticated serving boundary

Release assets are exposed only under `/app/<version>/...` after signed-token verification, registered-session validation, and entitlement evaluation. Anonymous, expired, unregistered, or revoked sessions receive `401`. A valid session requesting a release outside its tenant policy receives `404`, avoiding cross-tenant release discovery.

Only `GET` and `HEAD` are accepted. Raw and encoded path separators, dot segments, traversal, control characters, symlinks, unexpected files, catalog drift, archive drift, and file digest drift are rejected. Responses include content types, exact content lengths, SHA-256 ETags, private no-store caching, frame denial, same-origin resource policy, and content-sniffing protection.

The hosted shell renders release metadata with DOM text APIs rather than HTML string interpolation.

## Security and privacy boundary

The runtime includes strict JSON parsing, canonical seals, HMAC-SHA256 assertion and session contracts, canonical base64url checks, issuer and audience validation, bounded TTLs, durable single-use assertion identifiers, same-origin state-changing requests, shared rate limiting, security headers, explicit non-loopback opt-in, secure-cookie enforcement outside loopback, and durable logout revocation.

It intentionally includes no password database, self-registration, account recovery, payment state, learner-event storage, facilitator-record storage, organization administration, or browser-storage profile.

## Contracts

- `principia-atlas-hosted-catalog/0.1`
- `principia-atlas-hosted-tenants/0.1`
- `principia-atlas-hosted-store/0.1`
- `principia-atlas-hosted-auth-state/0.1`
- `principia-atlas-hosted-auth-state-command/0.1`
- `principia-atlas-identity-assertion/0.1`
- `principia-atlas-hosted-session/0.2`
- `principia-atlas-hosted-view/0.1`
- `principia-atlas-hosted-health/0.3`

## Authority preservation

The control plane may decide which already promoted release a tenant can inspect and run. It cannot promote a Principia claim, alter Atlas lifecycle state, inherit Atlas status into Principia, modify canonical content, mutate a release, or replace release verification.

## Current limitation

SQLite coordinates processes that share one durable filesystem location; it is not a distributed database, cross-region consensus system, or automatic backup and failover layer. TLS termination, production identity-provider integration, observability, operational backup, learner-data persistence, organization administration, and billing remain outside this runtime. Therefore this work is not a complete production SaaS readiness claim.
