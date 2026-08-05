# Hosted deployment and recovery plane

This directory contains the operational boundary for deploying the authenticated, read-only Principia & Atlas hosted runtime. It does not grant promotion authority, mutate release content, or introduce learner-data persistence.

## Image boundary

`../Containerfile` is the canonical image definition. It uses a digest-pinned Node.js base, fixed OCI metadata, UID/GID `10001`, read-only application files, `SIGTERM`, and no package installation during runtime.

A deployment must additionally enforce:

- a read-only root filesystem;
- no privilege escalation and all Linux capabilities dropped;
- read-only mounts for catalog, tenant config, release store, and secret files;
- writable mounts only for shared authentication state, audit output, and bounded temporary storage;
- a verified image digest rather than a mutable tag;
- external TLS termination before non-loopback traffic reaches the runtime.

## Two-instance boundary

`kubernetes.example.yaml` demonstrates two instances sharing one SQLite state volume. This is valid only when the volume provides correct POSIX file locking and durable local-filesystem semantics. It is not a distributed database, multi-region design, or automatic failover system.

Both instances must use the same:

- sealed hosted catalog;
- sealed tenant configuration;
- immutable release store;
- identity and session secret generation;
- shared SQLite authentication state.

Each instance uses a distinct audit instance identifier.

## Secret files

Runtime secrets are loaded from regular files and copied into process-owned buffers. Files must not be symlinks, executable, group-writable, or accessible to other users. Environment-variable secret loading is intentionally not supported by the hosted server.

Required files:

```text
/run/secrets/identity
/run/secrets/session
```

Optional protected metrics file:

```text
/run/secrets/metrics
```

Identity and session secrets must be distinct. Secret buffers are cleared when the server closes.

## Liveness, readiness, and metrics

- `/healthz` reports process liveness.
- `/readyz` verifies shared authentication-state readiness.
- `/metrics` is available only with the configured bearer token.

Metrics contain bounded aggregate counters and gauges only. They do not include tenant, subject, session, assertion, release path, or token labels.

## Audit boundary

Audit records use `principia-atlas-hosted-audit-event/0.1`, canonical JSON lines, bounded values, and per-process sequence numbers. Sensitive field names are rejected. Audit storage must be protected and collected outside the runtime for retention and alerting.

## Backup

An online backup can be created while instances are running:

```bash
node software/principia_atlas/hosted/auth_state_recovery.mjs backup \
  --state /state/auth-state.sqlite \
  --output /backup/auth-state.sqlite

node software/principia_atlas/hosted/auth_state_recovery.mjs verify \
  --backup /backup/auth-state.sqlite
```

The backup is created through SQLite `VACUUM INTO`, checked with both `quick_check` and `integrity_check`, sealed by an exact SHA-256 sidecar, and published as an atomic pair.

## Restore

Restore is offline-only. Stop every instance and verify that no WAL or shared-memory file remains:

```bash
node software/principia_atlas/hosted/auth_state_recovery.mjs restore \
  --backup /backup/auth-state.sqlite \
  --state /state/auth-state.sqlite \
  --confirm-offline ALL_INSTANCES_STOPPED

node software/principia_atlas/hosted/auth_state_recovery.mjs integrity \
  --state /state/auth-state.sqlite
```

Restore stages and validates the replacement, swaps it atomically, and restores the previous state on post-swap failure.

## Rolling restart

During a rolling restart:

1. remove one instance from readiness;
2. send `SIGTERM`;
3. allow in-flight requests to drain within the configured timeout;
4. confirm another instance can still validate an existing session;
5. start and verify the replacement before stopping the next instance.

The runtime stops accepting new connections before closing shared state and audit handles. A bounded timeout destroys remaining sockets rather than hanging indefinitely.

## Remaining non-goals

- no production identity-provider adapter;
- no distributed SQL or multi-region session coordination;
- no automated backup scheduler or retention service;
- no external metrics collector or alert policy;
- no audit retention service;
- no learner records, organization administration, billing, or account recovery;
- no claim of complete production SaaS readiness.
