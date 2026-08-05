---
title: Principia & Atlas hosted deployment and recovery runtime
status: implemented-deployment-recovery-read-only-runtime
scope: product-integration
---

# Principia & Atlas hosted deployment and recovery runtime

The hosted layer combines an authenticated tenant boundary, durable authentication coordination, read-only serving of promoted Principia & Atlas releases, bounded observability, and explicit recovery operations. It does not change the immutable Principia learning package or Atlas knowledge-status authority.

## Architecture

- Python verifies promotion history and produces a sealed hosted release catalog.
- Python verifies catalog-referenced release archives and materializes only each `product/` subtree into a content-addressed store.
- Node.js verifies the catalog, tenant policy, store manifest, exact file set, symlink boundary, and every file digest at startup.
- Verified release bytes remain memory-resident; request handling does not parse ZIP archives or reopen release files.
- A trusted external identity adapter issues a short-lived assertion.
- Assertion claim and revocable session registration occur atomically in shared SQLite authentication state.
- Tenant identity comes only from the verified signed session and registered server-side session record.
- Catalog and asset access are filtered by allowed release channel, route, and optional exact-version pins.

## Durable authentication coordination

Contract `principia-atlas-hosted-auth-state/0.1` has an in-memory implementation for loopback tests and a SQLite implementation for the hosted server.

The SQLite backend uses strict tables, WAL mode, full synchronous writes, bounded busy handling, restrictive file permissions, and a schema-contract row. It stores consumed assertion identifiers, registered sessions, revocation timestamps, and bounded exchange-rate windows. Replay protection, session validity, logout revocation, and rate limiting remain consistent across processes opening the same state file and across process restarts.

Session contract `principia-atlas-hosted-session/0.2` uses a random session identifier independent of the assertion identifier. Logout persists revocation before clearing the cookie. Operators can prune expired state or revoke an exact session or all active sessions for one tenant-subject pair without listing session contents.

Parallel startup retries only transient SQLite `busy`, `locked`, or metadata uniqueness races. Schema mismatch, symlink, permission, and integrity errors remain fail-closed.

## Deployment boundary

The canonical Containerfile uses a digest-pinned Node.js base, fixed image metadata, root-owned application files, and numeric runtime identity `10001:10001`. The validated OCI distribution export is reproduced twice with `SOURCE_DATE_EPOCH=0`, provenance and SBOM disabled, timestamp rewriting enabled, and byte-for-byte comparison.

The runtime is validated with:

- read-only root filesystem;
- all Linux capabilities dropped;
- privilege escalation disabled;
- immutable catalog, tenant configuration, and release-store mounts;
- writable mounts limited to shared authentication state, audit output, and bounded temporary storage;
- no network egress in the example policy;
- two instances sharing one POSIX-locking SQLite volume;
- graceful `SIGTERM` drain with bounded forced socket closure.

The example StatefulSet and its operational constraints are documented under `software/principia_atlas/hosted/deployment/`.

## Secret boundary

The hosted server loads identity, session, and optional metrics credentials only from bounded regular files. Symlinks, executable files, group-writable files, and files accessible to other users are rejected. Identity and session secrets must be distinct.

Secret contents are copied into process-owned buffers. Caller buffers are cleared after server construction and process-owned copies are cleared when the server closes. Environment-variable secret loading is not supported by the production hosted server; it remains limited to the explicitly disabled-by-default development assertion helper.

## Authenticated serving boundary

Release assets are exposed only under `/app/<version>/...` after signed-token verification, registered-session validation, and entitlement evaluation. Anonymous, expired, unregistered, or revoked sessions receive `401`. A valid session requesting a release outside its tenant policy receives `404` to avoid cross-tenant release discovery.

Only `GET` and `HEAD` are accepted. Raw and encoded path separators, dot segments, traversal, control characters, symlinks, unexpected files, catalog drift, archive drift, and digest drift are rejected. Responses include exact content lengths, SHA-256 ETags, private no-store caching, frame denial, same-origin resource policy, and content-sniffing protection.

## Observability boundary

Audit contract `principia-atlas-hosted-audit-event/0.1` emits canonical bounded JSON lines with per-instance sequence numbers and request identifiers. Sensitive field names—including credentials, tokens, subjects, assertion identifiers, and session identifiers—are rejected by the logger.

Metrics contract `principia-atlas-hosted-metrics/0.1` exposes a bearer-protected `/metrics` endpoint with aggregate liveness, readiness, request, authentication-outcome, and byte counters. Metrics contain no tenant, subject, session, assertion, token, or release-path labels.

`/healthz` remains process liveness. `/readyz` checks shared authentication state and fails with `503` when that state is unavailable.

## Recovery boundary

Contract `principia-atlas-hosted-auth-recovery/0.1` provides:

- online backup using SQLite `VACUUM INTO`;
- `quick_check` and `integrity_check` validation;
- exact SHA-256 sidecar verification;
- atomic backup-pair publication with rollback;
- explicit offline-only restore requiring `ALL_INSTANCES_STOPPED`;
- staged restore verification, atomic swap, and rollback of the previous state.

Restore rejects active WAL or shared-memory files. CI validates online backup while one hosted instance remains available, then stops all instances and verifies offline restore using the same non-root, read-only runtime image.

## Contracts

- `principia-atlas-hosted-catalog/0.1`
- `principia-atlas-hosted-tenants/0.1`
- `principia-atlas-hosted-store/0.1`
- `principia-atlas-hosted-auth-state/0.1`
- `principia-atlas-hosted-auth-state-command/0.1`
- `principia-atlas-hosted-auth-recovery/0.1`
- `principia-atlas-hosted-audit-event/0.1`
- `principia-atlas-hosted-metrics/0.1`
- `principia-atlas-identity-assertion/0.1`
- `principia-atlas-hosted-session/0.2`
- `principia-atlas-hosted-view/0.1`
- `principia-atlas-hosted-health/0.3`

## Authority preservation

The control plane may decide which promoted release a tenant can inspect and run. It cannot promote a Principia claim, alter Atlas lifecycle state, inherit Atlas status into Principia, modify canonical content, mutate a release, or replace release verification.

## Current limitation

SQLite coordination applies only to processes sharing one durable filesystem with correct POSIX locking. This is not a distributed database, multi-region consensus system, automatic failover service, backup scheduler, retention service, external audit collector, or alerting platform. TLS termination and production identity-provider integration remain external reviewed boundaries. Learner-data persistence, organization administration, billing, and account recovery remain absent. Therefore this is not a complete production SaaS readiness claim.
