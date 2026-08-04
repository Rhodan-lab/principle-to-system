---
title: Principia & Atlas hosted control-plane foundation
status: implemented-foundation
scope: product-integration
---

# Principia & Atlas hosted control-plane foundation

The hosted layer introduces an authenticated tenant boundary without changing the immutable Principia learning package or Atlas knowledge-status authority.

## Architecture

- Python verifies promotion history and produces a sealed hosted release catalog.
- Node.js verifies the catalog and a separately sealed tenant policy.
- A trusted external identity adapter issues a short-lived signed assertion.
- The control plane exchanges that assertion once for a short-lived HttpOnly session.
- Tenant identity comes only from the verified session; the browser cannot select another tenant.
- Catalog results are filtered by allowed release channel, route, and optional exact-version pins.

## Security and privacy boundary

The foundation includes strict JSON parsing, canonical seals, HMAC-SHA256 assertion and session contracts, canonical base64url checks, issuer and audience validation, bounded TTLs, single-use assertion identifiers per process, same-origin state-changing requests, an exchange rate limit, security headers, and explicit non-loopback opt-in.

It intentionally includes no password database, self-registration, account recovery, payment state, learner-event storage, facilitator-record storage, organization administration, or browser-storage profile. Release archives are not served by the control plane in this phase.

## Contracts

- `principia-atlas-hosted-catalog/0.1`
- `principia-atlas-hosted-tenants/0.1`
- `principia-atlas-identity-assertion/0.1`
- `principia-atlas-hosted-session/0.1`
- `principia-atlas-hosted-view/0.1`

## Authority preservation

The control plane may decide which already promoted release metadata a tenant can see. It cannot promote a Principia claim, alter Atlas lifecycle state, inherit Atlas status into Principia, modify canonical content, or replace release verification.

## Current limitation

Replay protection and rate limiting are process-local. TLS termination, production identity-provider integration, durable session revocation, release-byte serving, observability, backups, and multi-instance coordination remain outside this foundation. Therefore this work is not a production authentication or public SaaS readiness claim.
