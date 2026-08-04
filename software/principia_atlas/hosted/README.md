# Hosted authenticated release runtime

This directory is the hosted/SaaS boundary for Principia & Atlas. It serves already promoted releases only after the release archive, hosted catalog, tenant policy, content store, and authentication state have been verified.

It remains an authenticated read-only runtime, not a learner-data platform.

## Responsibilities

- accept a short-lived signed identity assertion from an external identity adapter;
- claim that assertion once in shared durable state;
- register a revocable HttpOnly, SameSite session with an independent session identifier;
- derive tenant identity exclusively from the verified session;
- coordinate assertion replay protection, session revocation, and exchange rate limits across processes using the same SQLite state file;
- filter immutable promoted releases by tenant channel, route, and optional version pins;
- serve only the entitled release files from a verified memory-resident store;
- expose liveness, readiness, session, catalog, logout, and authenticated release routes;
- retain no password database, learner records, billing data, or browser-storage profile.

The browser cannot submit a tenant identifier to switch workspaces. A session is bound to exactly one tenant. Identity and session secrets must be distinct and at least 32 bytes.

## Build the hosted catalog

Collect verified `principia-atlas-promotion.json` files under one directory, then run:

```bash
python3 software/principia_atlas/hosted_catalog.py build \
  --promotions /tmp/promotion-history \
  --output /tmp/hosted/catalog.json
```

The catalog contract `principia-atlas-hosted-catalog/0.1` preserves exact release, route, archive, source, compatibility, and channel-pointer identities.

## Materialize the immutable release store

Place every catalog-referenced release ZIP and its `.sha256` sidecar in one archive directory. The Python materializer verifies each complete release before extracting only its `product/` subtree:

```bash
python3 software/principia_atlas/hosted_store.py build \
  --catalog /tmp/hosted/catalog.json \
  --archives /tmp/hosted-archives \
  --output /tmp/hosted/store
```

Verify or reproduce the store:

```bash
python3 software/principia_atlas/hosted_store.py verify \
  --store /tmp/hosted/store \
  --catalog /tmp/hosted/catalog.json

python3 software/principia_atlas/hosted_store.py check \
  --catalog /tmp/hosted/catalog.json \
  --archives /tmp/hosted-archives
```

Store contract `principia-atlas-hosted-store/0.1` binds the catalog ID, release and bundle identities, archive SHA-256, content-addressed object root, and every hosted file path, size, and digest. Publication replaces the complete directory atomically and restores the previous verified store if post-swap verification fails.

ZIP parsing never occurs in Node.js. At startup, Node validates the store manifest, exact file set, symlink boundary, catalog identities, sizes, and SHA-256 digests, then keeps verified bytes in memory. Requests do not reopen release files from disk.

## Seal tenant configuration

Copy `example-tenants.unsigned.json`, edit it, then seal it:

```bash
node software/principia_atlas/hosted/config.mjs seal \
  --input /tmp/tenants.unsigned.json \
  --output /tmp/hosted/tenants.json
```

For non-loopback hosting, `session.secure` must be `true`, durable multi-instance auth state is required, and the server must be started with `--allow-network`. The runtime does not terminate TLS; that remains the responsibility of a reviewed deployment edge.

## Durable authentication state

Contract `principia-atlas-hosted-auth-state/0.1` stores only bounded authentication coordination data:

- consumed assertion identifiers and their expiry;
- registered session identifiers, subject, tenant, role set, issue time, expiry, and revocation time;
- exchange rate-limit counters and expiry.

Assertion claim and session registration occur in one `BEGIN IMMEDIATE` transaction. A second process opening the same SQLite file cannot accept the same assertion. Logout records session revocation before clearing the browser cookie, so the token is rejected by every process sharing that state.

The database uses WAL mode, full synchronous writes, a bounded busy timeout, strict tables, contract metadata, and restrictive file permissions. Existing symlink or non-regular database paths are rejected.

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

`revoke-session` is also available when an operator has an exact session identifier from a separately controlled operational channel.

## Start locally

Use separate high-entropy secrets and a state path outside the source checkout:

```bash
export PRINCIPIA_ATLAS_IDENTITY_SECRET='replace-with-at-least-32-random-bytes'
export PRINCIPIA_ATLAS_SESSION_SECRET='replace-with-a-different-32-byte-secret'
node software/principia_atlas/hosted/server.mjs \
  --catalog /tmp/hosted/catalog.json \
  --tenants /tmp/hosted/tenants.json \
  --store /tmp/hosted/store \
  --state /tmp/hosted/auth-state.sqlite \
  --host 127.0.0.1 \
  --port 8080
```

`/healthz` is process liveness. `/readyz` verifies that the authentication state backend is available and returns `503` when it is not ready.

Authenticated release URLs use:

```text
/app/<version>/
/app/<version>/principia/
/app/<version>/atlas/
```

Every asset request rechecks the signed session, registered session state, and tenant entitlements. Anonymous or revoked sessions return `401`; releases outside the tenant's channel, route, or exact-version policy return `404` rather than revealing availability. Only `GET` and `HEAD` are accepted. Traversal, encoded separators, symlinks, extra files, and digest drift are rejected.

## Development identity adapter

Development assertion minting is disabled unless explicitly enabled:

```bash
export PRINCIPIA_ATLAS_DEV_AUTH=1
assertion=$(node software/principia_atlas/hosted/dev_identity.mjs \
  --tenants /tmp/hosted/tenants.json \
  --subject learner-1 \
  --tenant local-preview \
  --roles learner)

curl -i -X POST \
  -H "Authorization: Bearer $assertion" \
  -H "Origin: http://127.0.0.1:8080" \
  http://127.0.0.1:8080/api/auth/exchange
```

This development adapter is not a password system and is not enabled by the server. Production identity integration must issue the same short-lived assertion contract from a separately reviewed adapter.

## Current non-goals and limitations

- no anonymous or public release serving;
- no self-registration or password recovery;
- no learner-event or facilitator-record persistence;
- no payments, subscriptions, or organization administration;
- no production identity-provider adapter or TLS termination;
- no distributed database, cross-region consensus, automatic backup, or failover orchestration;
- SQLite coordination is for processes sharing one durable filesystem location;
- no claim of complete production SaaS readiness.
