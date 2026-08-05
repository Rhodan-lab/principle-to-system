# Hosted authenticated release runtime

This directory is the hosted/SaaS boundary for Principia & Atlas. It serves promoted immutable releases only after the release archive, hosted catalog, tenant policy, content store, authentication state, and deployment inputs have been verified.

It remains an authenticated read-only runtime, not a learner-data platform.

## Responsibilities

- accept short-lived assertions from an external identity adapter;
- claim each assertion once in shared durable state;
- register a revocable HttpOnly, SameSite session with an independent session identifier;
- derive tenant identity exclusively from the verified session;
- coordinate replay protection, session revocation, and exchange rate limits across processes using the same SQLite state file;
- filter promoted releases by tenant channel, route, and optional version pins;
- serve only entitled release files from a verified memory-resident store;
- expose liveness, readiness, protected aggregate metrics, and authenticated product routes;
- emit bounded structured audit events;
- support verified online backup and explicit offline restore of authentication state;
- retain no password database, learner records, billing data, or browser-storage profile.

The browser cannot submit a tenant identifier to switch workspaces. A session is bound to exactly one tenant.

## Build the hosted inputs

Build the sealed hosted catalog from verified promotion descriptors:

```bash
python3 software/principia_atlas/hosted_catalog.py build \
  --promotions /tmp/promotion-history \
  --output /tmp/hosted/catalog.json
```

Materialize the content-addressed release store from complete verified ZIP and checksum pairs:

```bash
python3 software/principia_atlas/hosted_store.py build \
  --catalog /tmp/hosted/catalog.json \
  --archives /tmp/hosted-archives \
  --output /tmp/hosted/store

python3 software/principia_atlas/hosted_store.py verify \
  --store /tmp/hosted/store \
  --catalog /tmp/hosted/catalog.json
```

ZIP parsing never occurs in Node.js. At startup, Node verifies the store manifest, exact file set, symlink boundary, catalog identities, sizes, and SHA-256 digests, then retains verified bytes in memory.

Seal tenant policy:

```bash
node software/principia_atlas/hosted/config.mjs seal \
  --input /tmp/tenants.unsigned.json \
  --output /tmp/hosted/tenants.json
```

For non-loopback hosting, `session.secure` must be `true`, durable multi-instance state is required, and the server must receive `--allow-network`. TLS termination remains the responsibility of a reviewed deployment edge.

## Secret files

The hosted server does not load production secrets from environment variables. Create separate regular files readable only by the runtime identity:

```bash
install -m 0400 /dev/null /tmp/hosted/identity.secret
install -m 0400 /dev/null /tmp/hosted/session.secret
install -m 0400 /dev/null /tmp/hosted/metrics.secret
```

Populate them using a controlled secret-management mechanism. Identity and session values must be distinct and at least 32 bytes. Secret files must not be symlinks, executable, group-writable, or accessible to other users.

The server copies credentials into process-owned buffers and clears those copies when the server closes.

## Start locally

```bash
node software/principia_atlas/hosted/server.mjs \
  --catalog /tmp/hosted/catalog.json \
  --tenants /tmp/hosted/tenants.json \
  --store /tmp/hosted/store \
  --state /tmp/hosted/auth-state.sqlite \
  --identity-secret-file /tmp/hosted/identity.secret \
  --session-secret-file /tmp/hosted/session.secret \
  --metrics-token-file /tmp/hosted/metrics.secret \
  --audit-log /tmp/hosted/audit.ndjson \
  --instance-id local-a \
  --host 127.0.0.1 \
  --port 8080
```

- `/healthz` reports process liveness.
- `/readyz` checks shared authentication-state readiness.
- `/metrics` requires the configured bearer token.
- `/app/<version>/...` serves entitled immutable release assets.

Every asset request rechecks the signed session, registered session state, and tenant entitlements. Anonymous or revoked sessions receive `401`; releases outside policy receive `404`. Only `GET` and `HEAD` are accepted.

## Durable authentication state

Contract `principia-atlas-hosted-auth-state/0.1` stores bounded authentication coordination data only:

- consumed assertion identifiers and expiry;
- registered session identity, subject, tenant, role set, issue time, expiry, and revocation time;
- exchange-rate counters and expiry.

The database uses WAL mode, full synchronous writes, bounded busy handling, strict tables, contract metadata, and restrictive permissions. Parallel server startup retries transient lock and metadata races, while structural errors remain fail-closed.

Operational commands do not list session contents:

```bash
node software/principia_atlas/hosted/auth_state_cli.mjs stats \
  --state /tmp/hosted/auth-state.sqlite

node software/principia_atlas/hosted/auth_state_cli.mjs prune \
  --state /tmp/hosted/auth-state.sqlite

node software/principia_atlas/hosted/auth_state_cli.mjs revoke-subject \
  --state /tmp/hosted/auth-state.sqlite \
  --tenant local-preview \
  --subject learner-1
```

## Audit and metrics

Audit contract `principia-atlas-hosted-audit-event/0.1` writes canonical JSON lines. Sensitive field names—including credentials, tokens, subjects, assertion identifiers, and session identifiers—are rejected.

Metrics contract `principia-atlas-hosted-metrics/0.1` exposes protected aggregate counters and gauges without tenant, subject, session, assertion, token, or release-path labels.

Audit files and metrics access tokens must be handled as operational security assets.

## Backup and restore

Create and verify an online SQLite backup while instances remain available:

```bash
node software/principia_atlas/hosted/auth_state_recovery.mjs backup \
  --state /tmp/hosted/auth-state.sqlite \
  --output /tmp/hosted/backups/auth-state.sqlite

node software/principia_atlas/hosted/auth_state_recovery.mjs verify \
  --backup /tmp/hosted/backups/auth-state.sqlite
```

The backup uses `VACUUM INTO`, database integrity checks, an exact SHA-256 sidecar, and atomic pair publication.

Restore is offline-only. Stop every instance first:

```bash
node software/principia_atlas/hosted/auth_state_recovery.mjs restore \
  --backup /tmp/hosted/backups/auth-state.sqlite \
  --state /tmp/hosted/auth-state.sqlite \
  --confirm-offline ALL_INSTANCES_STOPPED

node software/principia_atlas/hosted/auth_state_recovery.mjs integrity \
  --state /tmp/hosted/auth-state.sqlite
```

Active WAL or shared-memory files cause restore rejection. Replacement is staged, verified, atomically swapped, and rolled back on failure.

## Container and deployment

`Containerfile` is digest-pinned, non-root, and reproducibly exported as OCI bytes. The validated runtime uses:

- UID/GID `10001:10001`;
- root-owned application files;
- read-only root filesystem;
- all capabilities dropped;
- no privilege escalation;
- read-only catalog, policy, store, and secret mounts;
- writable state, audit, and bounded temporary mounts only;
- graceful `SIGTERM` drain with a bounded forced close.

The two-instance example, NetworkPolicy, rolling-restart procedure, and recovery instructions are under `deployment/`.

## Development identity adapter

Development assertion minting remains disabled unless explicitly enabled. It may use `PRINCIPIA_ATLAS_IDENTITY_SECRET` only for local test assertion generation; the hosted server itself does not read production secrets from environment variables.

```bash
export PRINCIPIA_ATLAS_DEV_AUTH=1
export PRINCIPIA_ATLAS_IDENTITY_SECRET='local-development-only-secret-at-least-32-bytes'
node software/principia_atlas/hosted/dev_identity.mjs \
  --tenants /tmp/hosted/tenants.json \
  --subject learner-1 \
  --tenant local-preview \
  --roles learner
```

## Current non-goals and limitations

- no anonymous or public release serving;
- no self-registration, passwords, or account recovery;
- no learner-event or facilitator-record persistence;
- no payments, subscriptions, or organization administration;
- no production identity-provider adapter or built-in TLS termination;
- no distributed database, cross-region consensus, or multi-region failover;
- no automatic backup scheduler, retention service, external audit collector, or alerting platform;
- SQLite coordination is limited to processes sharing one durable POSIX-locking filesystem;
- no claim of complete production SaaS readiness.
