---
title: Principia & Atlas trusted browser OIDC and SaaS edge
status: implemented-browser-oidc-and-bounded-saas-edge
scope: product-integration
---

# Principia & Atlas trusted browser OIDC and SaaS edge

The hosted product has a bounded browser-facing login component for the production OIDC verifier and a narrowly scoped path for learner-progress synchronization. Authentication, SaaS state, and immutable release serving remain separate authorities.

## Implemented contracts

- `principia-atlas-browser-oidc/0.1` seals issuer, endpoints, public origin, client mode, scopes, routes, limits, and flow-cookie policy.
- `principia-atlas-browser-oidc-flow/0.1` binds state, nonce, PKCE verifier, same-origin return path, and bounded lifetime inside an authenticated encrypted cookie.
- `principia-atlas-browser-oidc-edge/0.2` defines the public edge, loopback-only upstream, hidden internal auth endpoints, bounded health metadata, and one body-bearing SaaS route.
- `principia-atlas-saas-hosted-runtime/0.1` verifies the existing hosted session against the shared auth state before dispatching SaaS requests.
- `principia-atlas-saas-application-api/0.1` resolves membership from hosted tenant plus pairwise subject and authorizes learner-progress writes.

## Runtime result

The browser starts an Authorization Code flow with PKCE `S256`. The edge validates callback state and optional issuer, exchanges the code at the exact sealed token endpoint, rejects refresh tokens, checks ID-token structure, issuer, and nonce, then sends only the ID token through an exact loopback chain.

The hosted authentication runtime remains authoritative for cryptographic verification, tenant and role mapping, pairwise subject derivation, replay protection, session registration, and revocation. The browser edge relays the resulting hosted session cookie and never creates its own product identity.

For normal proxy routes, request bodies remain prohibited. The only public body-bearing route is:

```text
PUT /api/saas/progress/:route/:stage
```

The edge accepts at most 16 KiB and forwards only:

```text
Content-Type
Idempotency-Key
X-CSRF-Token
```

It validates the exact public origin before reading or forwarding the body. It rewrites the origin to the exact loopback runtime origin. The runtime then independently verifies the hosted session, shared auth-state registration, organization binding, membership, CSRF, exact release entitlement, idempotency receipt, and expected progress revision.

## Preserved boundaries

- Principia remains the learning authority.
- Atlas remains a read-only research and provenance substrate.
- The identity provider supplies external identity evidence only.
- Sealed hosted policy remains authoritative for tenant and role mapping.
- The SaaS control plane owns organization, membership, entitlement, and learner-progress state.
- The immutable hosted release core remains separate from the SaaS runtime facade.
- The public edge stores no learner record, browser token, refresh token, password, billing state, or organization-administration state.
- No Principia or Atlas status inheritance is introduced.
- No live repository dependency or repository mutation is introduced.

## Validation

Focused Node.js regressions cover configuration sealing, PKCE generation, encrypted flow cookies, state and nonce enforcement, same-origin return paths, confidential and public clients, token-response limits, refresh-token rejection, callback-to-hosted-session exchange, hidden internal endpoints, origin rejection, default body rejection, the 16 KiB progress boundary, mutation-header whitelisting, session verification, tenant and membership resolution, CSRF, entitlement checks, transactional idempotency replay, stale-revision rejection, and bounded health output.

The runtime-edge smoke signs and registers a real hosted session, binds a SaaS organization to the hosted tenant, calls the public edge, stores one progress revision, and proves an identical idempotency retry returns the committed result without a second write.

## Remaining production boundary

The runtime and edge contract are wired, but production process composition still needs the PostgreSQL client, secret-file startup, health/readiness aggregation, deployment manifests, backup-and-restore evidence, rate limiting, and public-beta operations. This work does not claim a public production SaaS deployment.
