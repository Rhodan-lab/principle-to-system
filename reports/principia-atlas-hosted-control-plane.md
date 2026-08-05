---
title: Principia & Atlas hosted OIDC deployment and recovery runtime
status: implemented-production-oidc-read-only-runtime
scope: product-integration
---

# Principia & Atlas hosted OIDC deployment and recovery runtime

The hosted layer combines a verified external-identity boundary, durable authentication coordination, read-only serving of promoted Principia & Atlas releases, bounded observability, and explicit recovery operations. It does not change the immutable Principia learning package or Atlas knowledge-status authority.

## Architecture

- Python verifies promotion history and produces a sealed hosted release catalog.
- Python verifies catalog-referenced release archives and materializes only each `product/` subtree into a content-addressed store.
- Node.js verifies the catalog, tenant policy, store manifest, exact file set, symlink boundary, and every file digest at startup.
- Verified release bytes remain memory-resident; request handling does not parse ZIP archives or reopen release files.
- Identity enters through either the existing internal short-lived assertion contract or the optional production OIDC verifier.
- OIDC claims are mapped to a tenant and hosted roles only through a sealed local policy.
- Assertion claim and revocable session registration occur atomically in shared SQLite authentication state.
- Tenant identity comes only from the verified signed session and registered server-side session record.
- Catalog and asset access are filtered by release channel, route, and optional exact-version pins.

## Production OIDC boundary

Contracts `principia-atlas-hosted-oidc-policy/0.1`, `principia-atlas-hosted-oidc-principal/0.1`, and `principia-atlas-hosted-oidc-verifier/0.1` define the external identity adapter.

The verifier supports `RS256` and `ES256` with an explicit algorithm allowlist. It validates canonical base64url, strict UTF-8 JSON, duplicate and prototype-sensitive keys, issuer, audience, authorized party, issue/not-before/expiry boundaries, maximum token lifetime, required claims, verified-email policy, tenant mapping, and role mapping. Dynamic JOSE key references, redirects, private JWK material, weak RSA keys, unsupported curves, duplicate key identifiers, unknown algorithms, and unmapped values fail closed.

External subjects are transformed into pairwise internal identifiers. The raw subject and external JWT are not written to the authentication database, metrics, or audit output. A SHA-256 digest of the complete verified JWT becomes the replay identity; reuse of the same token therefore fails across processes sharing the same SQLite state.

The key provider is configured in exactly one mode:

- a verified read-only JWKS file; or
- explicit remote HTTPS retrieval using the exact sealed policy URI, bounded response size and timeout, no redirects, bounded caching, and one forced refresh for key rotation.

OIDC is disabled by default. When disabled, `/api/auth/oidc` is absent. When enabled, `/readyz` includes bounded provider readiness metadata. The operator CLI accepts external tokens only through stdin and loads internal signing credentials only from a restrictive secret file.

Browser authorization-code, PKCE, callback, login-page, and provider refresh-token handling remain responsibilities of a trusted reviewed edge. This runtime verifies the resulting identity token but does not implement the browser OAuth flow.

## Durable authentication coordination

Contract `principia-atlas-hosted-auth-state/0.1` has an in-memory implementation for loopback tests and a SQLite implementation for the hosted server.

The SQLite backend uses strict tables, WAL mode, full synchronous writes, bounded busy handling, restrictive file permissions, and a schema-contract row. It stores consumed assertion identifiers, registered sessions, revocation timestamps, and bounded exchange-rate windows. Replay protection, session validity, logout revocation, and rate limiting remain consistent across processes opening the same state file and across restarts.

Session contract `principia-atlas-hosted-session/0.2` uses a random session identifier independent of the assertion identifier. Logout persists revocation before clearing the cookie. Operators can prune expired state or revoke an exact session or all active sessions for one tenant-subject pair without listing session contents.

Parallel startup retries only transient SQLite `busy`, `locked`, or metadata uniqueness races. Schema mismatch, symlink, permission, and integrity errors remain fail-closed.

## Deployment boundary

The canonical Containerfile uses a digest-pinned Node.js base, fixed image metadata, root-owned application files, and numeric runtime identity `10001:10001`. The validated OCI export is reproduced twice with fixed build time and byte-for-byte comparison.

The runtime is validated with a read-only root filesystem, all Linux capabilities dropped, no privilege escalation, immutable catalog/tenant/store/secret mounts, writable mounts limited to shared authentication state/audit/bounded temporary storage, two instances sharing one POSIX-locking SQLite volume, and graceful `SIGTERM` drain with bounded forced socket closure.

The example policy denies network egress. Remote JWKS mode therefore requires a reviewed egress exception limited to the configured issuer infrastructure. Static JWKS mode preserves the no-egress runtime.

## Secret boundary

The hosted server loads identity, session, and optional metrics credentials only from bounded regular files. Symlinks, executable files, group-writable files, and files accessible to other users are rejected. Identity and session secrets must be distinct.

Secret contents are copied into process-owned buffers. Caller buffers are cleared after server construction and process-owned copies are cleared when the server closes. Environment-variable secret loading remains limited to the disabled-by-default development assertion helper.

## Authenticated serving boundary

Release assets are exposed only under `/app/<version>/...` after signed-token verification, registered-session validation, and entitlement evaluation. Anonymous, expired, unregistered, or revoked sessions receive `401`. A valid session requesting a release outside its tenant policy receives `404` to avoid cross-tenant discovery.

Only `GET` and `HEAD` are accepted. Raw and encoded path separators, dot segments, traversal, control characters, symlinks, unexpected files, catalog drift, archive drift, and digest drift are rejected. Responses include exact content lengths, SHA-256 ETags, private no-store caching, frame denial, same-origin resource policy, and content-sniffing protection.

## Observability boundary

Audit contract `principia-atlas-hosted-audit-event/0.1` emits canonical bounded JSON lines with per-instance sequence numbers and request identifiers. Sensitive field names—including credentials, tokens, raw subjects, assertion identifiers, and session identifiers—are rejected.

Metrics contract `principia-atlas-hosted-metrics/0.1` exposes a bearer-protected `/metrics` endpoint with aggregate liveness, readiness, request, authentication-outcome, and byte counters. Metrics contain no tenant, subject, session, assertion, external-token, signing-key, or release-path labels.

`/healthz` remains process liveness. Health contract `principia-atlas-hosted-health/0.4` adds bounded OIDC configuration metadata. `/readyz` checks shared authentication state and the configured OIDC provider.

## Recovery boundary

Contract `principia-atlas-hosted-auth-recovery/0.1` provides online `VACUUM INTO` backup, `quick_check` and `integrity_check`, exact SHA-256 sidecar verification, atomic backup publication with rollback, explicit offline-only restore requiring `ALL_INSTANCES_STOPPED`, and staged restore verification with rollback.

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
- `principia-atlas-hosted-oidc-policy/0.1`
- `principia-atlas-hosted-oidc-principal/0.1`
- `principia-atlas-hosted-oidc-verifier/0.1`
- `principia-atlas-identity-assertion/0.1`
- `principia-atlas-hosted-session/0.2`
- `principia-atlas-hosted-view/0.1`
- `principia-atlas-hosted-health/0.4`

## Authority preservation

The identity provider may attest an external identity and claims. The sealed local policy decides whether those claims map to a hosted tenant and role. Neither layer may promote a Principia claim, alter Atlas lifecycle state, inherit Atlas status into Principia, modify canonical content, mutate a release, or replace release verification.

## Current limitation

SQLite coordination applies only to processes sharing one durable filesystem with correct POSIX locking. This is not a distributed database, multi-region consensus system, automatic failover service, backup scheduler, retention service, external audit collector, or alerting platform. TLS termination and browser OAuth orchestration remain external reviewed boundaries. Learner-data persistence, organization administration, billing, and account recovery remain absent. Therefore this is not a complete production SaaS readiness claim.
