# Hosted authenticated release runtime

This directory is the hosted/SaaS boundary for Principia & Atlas. It serves promoted immutable releases only after the release archive, hosted catalog, tenant policy, content store, authentication state, identity inputs, and deployment inputs have been verified.

It remains an authenticated read-only runtime, not a learner-data platform.

## Responsibilities

- verify short-lived assertions from a trusted identity adapter or verify an explicitly configured external OIDC token;
- map external identity claims to one locally configured tenant and bounded hosted roles;
- claim each external token or internal assertion once in shared durable state;
- register a revocable HttpOnly, SameSite session with an independent session identifier;
- derive tenant identity exclusively from the verified session;
- coordinate replay protection, session revocation, and exchange rate limits across processes using the same SQLite state file;
- filter promoted releases by tenant channel, route, and optional version pins;
- serve only entitled release files from a verified memory-resident store;
- expose liveness, readiness, protected aggregate metrics, and authenticated product routes;
- emit bounded structured audit events;
- support verified online backup and explicit offline restore of authentication state;
- retain no password database, learner records, billing data, or browser-storage profile.

The browser cannot submit a tenant identifier to switch workspaces. An external identity provider supplies identity evidence, while the sealed local policy remains authoritative for tenant and role mapping.

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

## Production OIDC identity adapter

The optional OIDC boundary verifies a JWT issued by one configured HTTPS issuer and maps it through a sealed local policy. It supports `RS256` and `ES256`, canonical JOSE encoding, issuer/audience/authorized-party checks, bounded issue/not-before/expiry time, required claims, verified-email policy, explicit tenant mapping, and explicit role mapping.

The adapter rejects dynamic JOSE key references, redirects, private JWK material, weak RSA keys, unsupported curves, duplicate key identifiers, malformed UTF-8, duplicate JSON keys, prototype-sensitive keys, noncanonical base64url, unknown algorithms, and unmapped tenants or roles.

External subjects are transformed into pairwise internal identifiers. The raw external subject and JWT are not written to audit logs or authentication state. A SHA-256 digest of the complete verified external token becomes the assertion replay identifier, so the same token cannot establish a second session on another process sharing the SQLite state.

Create a sealed policy:

```bash
node software/principia_atlas/hosted/oidc_cli.mjs seal-policy \
  --input software/principia_atlas/hosted/example-oidc-policy.unsigned.json \
  --output /tmp/hosted/oidc-policy.json
```

Verify a static JWKS file and compatibility with tenant policy:

```bash
node software/principia_atlas/hosted/oidc_cli.mjs verify \
  --policy /tmp/hosted/oidc-policy.json \
  --jwks /tmp/hosted/jwks.json \
  --tenants /tmp/hosted/tenants.json
```

For an edge integration that needs to produce the existing internal assertion contract, provide the external JWT only through stdin. Never put a bearer token in process arguments:

```bash
printf '%s\n' "$OIDC_TOKEN" | \
node software/principia_atlas/hosted/oidc_cli.mjs adapt \
  --policy /tmp/hosted/oidc-policy.json \
  --jwks /tmp/hosted/jwks.json \
  --tenants /tmp/hosted/tenants.json \
  --identity-secret-file /tmp/hosted/identity.secret
```

The hosted server can use one of two provider modes:

- static/offline: `--oidc-policy ... --oidc-jwks-file ...`;
- remote rotation: `--oidc-policy ... --oidc-remote-jwks`.

Remote mode performs a bounded HTTPS fetch to the exact policy URI, refuses redirects, enforces content type and size, caches keys for a bounded interval, and performs one forced refresh for an unknown key identifier. OIDC remains disabled when no policy is supplied. `/api/auth/oidc` is absent in that state.

The trusted edge remains responsible for browser authorization-code and PKCE orchestration, callback validation, TLS, and obtaining the token. This runtime does not implement login redirects or store provider refresh tokens.

## Secret files

The hosted server does not load production secrets from environment variables. Create separate regular files readable only by the runtime identity:

```bash
install -m 0400 /dev/null /tmp/hosted/identity.secret
install -m 0400 /dev/null /tmp/hosted/session.secret
install -m 0400 /dev/null /tmp/hosted/metrics.secret
```

Populate them using a controlled secret-management mechanism. Identity and session values must be distinct and at least 32 bytes. Secret files must not be symlinks, executable, group-writable, or accessible to other users. The server copies credentials into process-owned buffers and clears those copies when the server closes.

## Start locally

Base runtime without OIDC:

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

Add static OIDC verification:

```bash
  --oidc-policy /tmp/hosted/oidc-policy.json \
  --oidc-jwks-file /tmp/hosted/jwks.json
```

Or explicitly allow remote JWKS retrieval:

```bash
  --oidc-policy /tmp/hosted/oidc-policy.json \
  --oidc-remote-jwks
```

- `/healthz` reports process liveness and bounded identity-provider metadata.
- `/readyz` checks shared authentication state and the configured OIDC key provider.
- `/metrics` requires the configured bearer token.
- `/api/auth/oidc` verifies the external token and establishes the standard hosted session when OIDC is enabled.
- `/app/<version>/...` serves entitled immutable release assets.

Every asset request rechecks the signed session, registered session state, and tenant entitlements. Anonymous or revoked sessions receive `401`; releases outside policy receive `404`. Only `GET` and `HEAD` are accepted.

## Durable authentication state

Contract `principia-atlas-hosted-auth-state/0.1` stores bounded authentication coordination data only:

- consumed assertion identifiers and expiry;
- registered session identity, pairwise subject, tenant, role set, issue time, expiry, and revocation time;
- exchange-rate counters and expiry.

The database uses WAL mode, full synchronous writes, bounded busy handling, strict tables, contract metadata, and restrictive permissions. Parallel server startup retries transient lock and metadata races, while structural errors remain fail-closed.

Operational commands do not list session contents:

```bash
node software/principia_atlas/hosted/auth_state_cli.mjs stats --state /tmp/hosted/auth-state.sqlite
node software/principia_atlas/hosted/auth_state_cli.mjs prune --state /tmp/hosted/auth-state.sqlite
node software/principia_atlas/hosted/auth_state_cli.mjs revoke-subject \
  --state /tmp/hosted/auth-state.sqlite \
  --tenant local-preview \
  --subject '<pairwise-subject>'
```

`revoke-subject` and `revoke-oidc-subject` are break-glass interfaces. They place target identity in process arguments and must not be used by normal automation.

### Signed OIDC subject revocation

Production automation uses a short-lived Ed25519-signed request. The request producer holds the private key; the networkless state operator receives only the immutable public key. The external issuer and subject remain inside private files and never appear in process arguments or command output.

Generate an Ed25519 key pair in DER form on the controlled signer host:

```bash
openssl genpkey -algorithm ED25519 -outform DER \
  -out /secure/revocation-private.der
openssl pkey -inform DER -in /secure/revocation-private.der \
  -pubout -outform DER -out /secure/revocation-public.der
chmod 0400 /secure/revocation-private.der
chmod 0444 /secure/revocation-public.der
```

Create a mode-`0600` draft containing exactly the `principia-atlas-hosted-oidc-revocation-request-draft/0.1` fields. `issued_at` and `expires_at` are Unix seconds, the request lifetime may not exceed 300 seconds, and `event_id` must remain stable across retries:

```json
{
  "contract": "principia-atlas-hosted-oidc-revocation-request-draft/0.1",
  "tenant_id": "local-preview",
  "issuer": "https://identity.example.test",
  "external_subject": "provider-subject",
  "event_id": "identity-disable-event-0004",
  "issued_at": 1800000000,
  "expires_at": 1800000300,
  "receipt_ttl_seconds": 2592000
}
```

Sign it offline. The signer refuses an existing output path and creates the authenticated request with mode `0600`:

```bash
node software/principia_atlas/hosted/revocation_request_cli.mjs sign \
  --input /secure/revocation-draft.json \
  --private-key-file /secure/revocation-private.der \
  --output /secure/revocation-request.json

node software/principia_atlas/hosted/revocation_request_cli.mjs key-id \
  --public-key-file /secure/revocation-public.der
```

Transfer only the signed request and public key to the isolated operator. Mount both read-only; the public key must have no write or execute bits. The request is verified before SQLite is opened:

```bash
node software/principia_atlas/hosted/auth_state_cli.mjs revoke-oidc-request \
  --state /state/auth-state.sqlite \
  --request-file /run/revocation-request.json \
  --request-key-file /run/revocation-public.der
```

The response contains `verified_key_id` and the retry-safe revocation receipt, but no issuer, external subject, pairwise subject, or session identifier. Reusing the same unexpired signed request returns the original receipt with `replayed: true`; reusing its event identifier for another target is rejected.

## Audit and metrics

Audit contract `principia-atlas-hosted-audit-event/0.1` writes canonical JSON lines. Sensitive field names—including credentials, tokens, raw subjects, assertion identifiers, and session identifiers—are rejected.

Metrics contract `principia-atlas-hosted-metrics/0.1` exposes protected aggregate counters and gauges without tenant, subject, session, assertion, token, provider key, or release-path labels.

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

`Containerfile` is digest-pinned, non-root, and reproducibly exported as OCI bytes. The validated runtime uses UID/GID `10001:10001`, root-owned application files, a read-only root filesystem, all capabilities dropped, no privilege escalation, read-only catalog/policy/store/secret mounts, writable state/audit/bounded temporary mounts only, and graceful `SIGTERM` drain.

The two-instance example, NetworkPolicy, rolling-restart procedure, and recovery instructions are under `deployment/`. Static OIDC deployments mount the sealed policy and JWKS read-only. Remote mode additionally requires reviewed egress policy restricted to the exact issuer infrastructure.

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
- no self-registration, passwords, account recovery, or provider refresh-token storage;
- no built-in browser OAuth authorization-code, PKCE, callback, or login-page orchestration;
- no learner-event or facilitator-record persistence;
- no payments, subscriptions, or organization administration;
- no built-in TLS termination;
- no distributed database, cross-region consensus, or multi-region failover;
- no automatic backup scheduler, retention service, external audit collector, or alerting platform;
- SQLite coordination is limited to processes sharing one durable POSIX-locking filesystem;
- no claim of complete production SaaS readiness.
