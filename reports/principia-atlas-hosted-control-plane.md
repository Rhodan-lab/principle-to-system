---
title: Principia & Atlas authenticated hosted release runtime
status: implemented-read-only-runtime
scope: product-integration
---

# Principia & Atlas authenticated hosted release runtime

The hosted layer now combines an authenticated tenant boundary with read-only serving of already promoted Principia & Atlas releases. It does not change the immutable Principia learning package or Atlas knowledge-status authority.

## Architecture

- Python verifies promotion history and produces a sealed hosted release catalog.
- Python verifies every catalog-referenced release archive and materializes only its `product/` subtree into a content-addressed store.
- Store contract `principia-atlas-hosted-store/0.1` seals catalog identity, release identities, archive digest, object root, and every file path, size, and SHA-256 digest.
- Store publication is atomic and rollback-capable.
- Node.js verifies the catalog, tenant policy, store manifest, exact file set, symlink boundary, and every file digest at startup.
- Verified file bytes are retained in memory; request handling does not reopen release files or parse ZIP archives.
- A trusted external identity adapter issues a short-lived signed assertion.
- The control plane exchanges that assertion once for a short-lived HttpOnly session.
- Tenant identity comes only from the verified session; the browser cannot select another tenant.
- Catalog and asset access are filtered by allowed release channel, route, and optional exact-version pins.

## Authenticated serving boundary

Release assets are exposed only under `/app/<version>/...` after session verification and entitlement evaluation. Anonymous requests receive `401`. A valid session requesting a release outside its tenant policy receives `404`, avoiding cross-tenant release discovery.

Only `GET` and `HEAD` are accepted. Raw and encoded path separators, dot segments, traversal, control characters, symlinks, unexpected files, catalog drift, archive drift, and file digest drift are rejected. Responses include content types, exact content lengths, SHA-256 ETags, private no-store caching, frame denial, same-origin resource policy, and content-sniffing protection.

The hosted shell renders release metadata with DOM text APIs rather than HTML string interpolation.

## Security and privacy boundary

The runtime includes strict JSON parsing, canonical seals, HMAC-SHA256 assertion and session contracts, canonical base64url checks, issuer and audience validation, bounded TTLs, single-use assertion identifiers per process, same-origin state-changing requests, an exchange rate limit, security headers, explicit non-loopback opt-in, and secure-cookie enforcement outside loopback.

It intentionally includes no password database, self-registration, account recovery, payment state, learner-event storage, facilitator-record storage, organization administration, or browser-storage profile.

## Contracts

- `principia-atlas-hosted-catalog/0.1`
- `principia-atlas-hosted-tenants/0.1`
- `principia-atlas-hosted-store/0.1`
- `principia-atlas-identity-assertion/0.1`
- `principia-atlas-hosted-session/0.1`
- `principia-atlas-hosted-view/0.1`
- `principia-atlas-hosted-health/0.2`

## Authority preservation

The control plane may decide which already promoted release a tenant can inspect and run. It cannot promote a Principia claim, alter Atlas lifecycle state, inherit Atlas status into Principia, modify canonical content, mutate a release, or replace release verification.

## Current limitation

Replay protection and rate limiting are process-local. TLS termination, production identity-provider integration, durable session revocation, observability, backups, multi-instance coordination, learner-data persistence, organization administration, and billing remain outside this runtime. Therefore this work is not a complete production SaaS readiness claim.
