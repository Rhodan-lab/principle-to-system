---
title: Principia & Atlas trusted browser OIDC edge
status: implemented-browser-authorization-code-pkce-edge
scope: product-integration
---

# Principia & Atlas trusted browser OIDC edge

The hosted product now has a bounded browser-facing login component for the already implemented production OIDC verifier. It closes the usability gap between an external identity provider and the authenticated read-only runtime while preserving the existing authority model.

## Implemented contracts

- `principia-atlas-browser-oidc/0.1` seals issuer, endpoints, public origin, client mode, scopes, routes, limits, and flow-cookie policy.
- `principia-atlas-browser-oidc-flow/0.1` binds state, nonce, PKCE verifier, same-origin return path, and bounded lifetime inside an authenticated encrypted cookie.
- `principia-atlas-browser-oidc-edge/0.1` defines the public edge, loopback-only upstream, hidden internal auth endpoints, and bounded health metadata.

## Runtime result

The browser starts an Authorization Code flow with PKCE `S256`. The edge validates callback state and optional issuer, exchanges the code at the exact sealed token endpoint, rejects refresh tokens, checks ID-token structure, issuer, and nonce, then sends only the ID token to the hosted runtime over an exact loopback origin.

The hosted runtime remains authoritative for cryptographic verification, tenant and role mapping, pairwise subject derivation, replay protection, session registration, revocation, audit, metrics, and release entitlement. The browser edge relays the resulting hosted session cookie and never creates its own product identity.

## Preserved boundaries

- Principia remains the learning authority.
- Atlas remains a read-only research and provenance substrate.
- The identity provider supplies external identity evidence only.
- Sealed local policy remains authoritative for tenant and role mapping.
- No Principia or Atlas status inheritance is introduced.
- No live repository dependency or repository mutation is introduced.
- No learner record, browser token, refresh token, password, billing state, or organization-administration state is stored.

## Validation

Focused Node.js regressions cover configuration sealing, PKCE generation, encrypted flow cookies, state and nonce enforcement, same-origin return paths, confidential and public clients, token-response limits, refresh-token rejection, root login initiation, successful callback-to-hosted-session exchange, proxy behavior, hidden internal endpoints, origin rejection, body rejection, tampered cookies, and bounded health output.
