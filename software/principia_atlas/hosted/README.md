# Hosted control-plane foundation

This directory is the first hosted/SaaS boundary for Principia & Atlas. It is intentionally a **catalog-only authenticated control plane**, not a public learner runtime.

## Responsibilities

- accept a short-lived signed identity assertion from an external identity adapter;
- exchange it for an HttpOnly, SameSite session cookie;
- derive tenant identity exclusively from the verified session;
- filter immutable promoted releases by tenant channel, route, and optional version pins;
- expose health, session, catalog, and logout endpoints;
- retain no password database, learner records, billing data, or browser-storage profile.

The browser cannot submit a tenant identifier to switch workspaces. A session is bound to exactly one tenant. Identity and session secrets must be distinct and at least 32 bytes.

## Build the hosted catalog

Collect verified `principia-atlas-promotion.json` files under one directory, then run:

```bash
python3 software/principia_atlas/hosted_catalog.py build \
  --promotions /tmp/promotion-history \
  --output /tmp/principia-atlas-hosted-catalog.json
```

The catalog contract `principia-atlas-hosted-catalog/0.1` preserves exact release, route, archive, source, compatibility, and channel-pointer identities.

## Seal tenant configuration

Copy `example-tenants.unsigned.json`, edit it, then seal it:

```bash
node software/principia_atlas/hosted/config.mjs seal \
  --input /tmp/tenants.unsigned.json \
  --output /tmp/tenants.json
```

For non-loopback hosting, `session.secure` must be `true` and the server must be started with `--allow-network`. The foundation does not terminate TLS; that remains the responsibility of a reviewed deployment edge.

## Start locally

Use separate high-entropy secrets:

```bash
export PRINCIPIA_ATLAS_IDENTITY_SECRET='replace-with-at-least-32-random-bytes'
export PRINCIPIA_ATLAS_SESSION_SECRET='replace-with-a-different-32-byte-secret'
node software/principia_atlas/hosted/server.mjs \
  --catalog /tmp/principia-atlas-hosted-catalog.json \
  --tenants /tmp/tenants.json \
  --host 127.0.0.1 \
  --port 8080
```

## Development identity adapter

Development assertion minting is disabled unless explicitly enabled:

```bash
export PRINCIPIA_ATLAS_DEV_AUTH=1
assertion=$(node software/principia_atlas/hosted/dev_identity.mjs \
  --tenants /tmp/tenants.json \
  --subject learner-1 \
  --tenant local-preview \
  --roles learner)

curl -i -X POST \
  -H "Authorization: Bearer $assertion" \
  -H "Origin: http://127.0.0.1:8080" \
  http://127.0.0.1:8080/api/auth/exchange
```

This development adapter is not a password system and is not enabled by the server. Production identity integration must issue the same short-lived assertion contract from a separately reviewed adapter.

## Current non-goals

- no public serving of learner release bytes;
- no self-registration or password recovery;
- no learner-event or facilitator-record persistence;
- no payments, subscriptions, or organization administration;
- no claim of production authentication or SaaS readiness.
