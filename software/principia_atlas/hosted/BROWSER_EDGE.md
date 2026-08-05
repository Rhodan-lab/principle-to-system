---
title: Principia & Atlas trusted browser OIDC and SaaS edge
status: implemented-contract-not-production-deployed
authority: hosted-product-integration
---

# Trusted browser OIDC and SaaS edge

The browser edge provides Authorization Code with PKCE and a narrowly bounded learner-progress mutation path. It does not become an identity, tenant, content, or learner-state authority.

The runtime boundary is now:

```text
browser
  -> HTTPS browser edge
      -> identity provider authorization and token endpoints
      -> loopback SaaS runtime facade
          -> SaaS application API and control-plane state
          -> loopback immutable hosted release core
```

The hosted authentication runtime remains the only component that cryptographically accepts the returned ID token, maps external claims through sealed tenant policy, claims replay identity, registers the session, and issues the hosted session cookie.

## Security boundary

The edge:

- uses Authorization Code with PKCE `S256`, random state, and random nonce;
- stores short-lived flow state only in an authenticated AES-256-GCM HttpOnly cookie;
- permits only same-origin relative return paths and rejects authentication routes as return targets;
- sends the code verifier and optional client secret only to the exact sealed HTTPS token endpoint;
- refuses token-endpoint redirects, oversized responses, non-JSON responses, duplicate callback parameters, issuer mismatch, nonce mismatch, and malformed JWT structure;
- rejects `offline_access` and any returned refresh token;
- forwards only the returned ID token to the loopback `/api/auth/oidc` chain;
- validates the exact hosted-session response contract before relaying its cookie;
- clears the one-time browser flow cookie after success and on callback or upstream exchange failure;
- never exposes `/api/auth/oidc`, `/api/auth/exchange`, or `/metrics` through the public proxy;
- rewrites browser-origin requests to the exact loopback upstream origin;
- requires the exact public origin for POST and PUT requests and rejects originless mutations;
- rejects request bodies by default;
- permits a body only for `PUT /api/saas/progress/:route/:stage`;
- reads at most 16 KiB before starting the upstream request;
- forwards only `Content-Type`, `Idempotency-Key`, and `X-CSRF-Token` for that mutation;
- does not persist authorization codes, tokens, external subjects, client secrets, or learner records.

The edge performs structural issuer and nonce checks before the ID token reaches the hosted runtime. Those checks do not replace signature verification. The hosted OIDC verifier remains authoritative for signature, algorithm, key, issuer, audience, authorized-party, time, required-claim, tenant, and role validation.

## SaaS runtime facade

`saas_runtime.mjs` is a loopback-only facade in front of the immutable hosted release core. It shares the hosted session secret and auth-state instance with the core deployment boundary.

For `/api/saas/*`, the facade:

1. verifies the signed hosted session cookie;
2. verifies that the session is still registered and not revoked;
3. passes the trusted session object to the SaaS application API;
4. emits a canonical bounded JSON response.

For all other paths, it forwards only bodyless GET, HEAD, and POST requests to the exact loopback core origin. It rewrites `Origin` to the core origin and forwards a narrow header allowlist. This preserves existing login, catalog, release, logout, readiness, and health behavior without moving those responsibilities into the SaaS layer.

The application API independently resolves organization and membership using the hosted tenant plus pairwise subject. Browser bodies never select tenant, organization, member, subject, or role.

## Create a sealed browser configuration

```bash
node software/principia_atlas/hosted/browser_edge_cli.mjs seal \
  --input software/principia_atlas/hosted/example-browser-oidc.unsigned.json \
  --output /tmp/hosted/browser-oidc.json

node software/principia_atlas/hosted/browser_edge_cli.mjs verify \
  --config /tmp/hosted/browser-oidc.json
```

The registered callback URI must exactly equal:

```text
<public_origin><callback_path>
```

The scope set must contain `openid` and must not contain `offline_access`.

## Secret files

The browser flow secret encrypts flow cookies. A confidential OIDC client also requires a separate client secret. Both use restrictive regular-file boundaries:

```bash
install -m 0400 /dev/null /tmp/hosted/browser-flow.secret
install -m 0400 /dev/null /tmp/hosted/browser-client.secret
```

The SaaS runtime additionally requires the existing hosted session secret and a distinct CSRF secret. Production startup composition must load those from restrictive secret files; they must not be passed through argv or ordinary environment variables.

## Edge startup boundary

The edge CLI still accepts one exact loopback upstream origin. For the SaaS composition, that origin must point to the runtime facade rather than directly to the release core:

```text
browser edge upstream -> loopback SaaS runtime facade
SaaS runtime core     -> loopback hosted release core
```

The facade currently exists as a tested library boundary. Production CLI composition, PostgreSQL pool startup, aggregated readiness, and deployment manifest changes remain separate work and are not claimed by this document.

TLS termination must be provided by a reviewed deployment boundary. Non-loopback edge binding requires explicit `--allow-network`, and the sealed public origin must use HTTPS.

## Health boundary

The public edge health endpoint remains:

```text
/edge/healthz
```

It exposes only the edge contract, sealed configuration ID, and a generic loopback-upstream status. It does not expose endpoints, secrets, tokens, subjects, tenants, database state, or release identities.

The tested runtime facade does not yet add a public health endpoint. Production composition must aggregate auth-state, PostgreSQL migration, SaaS database, hosted core, and OIDC provider readiness without exposing private topology.

## Deployment status

The existing Kubernetes example represents the earlier direct browser-edge-to-hosted-core topology. It must not be described as the completed SaaS deployment. A future bounded change will add:

- a PostgreSQL-backed runtime process;
- restrictive secret-file loading;
- the facade and core loopback ports;
- browser-edge upstream rewiring;
- readiness aggregation;
- database NetworkPolicy egress;
- backup and restore procedures;
- rollout and rollback evidence.

## Validation

The runtime-edge smoke:

- signs a real hosted identity assertion;
- creates and registers a hosted session;
- binds a SaaS organization to the hosted tenant;
- reaches `/api/saas/me` through the browser edge and runtime facade;
- receives a session-bound CSRF token without exposing the pairwise subject;
- stores one entitled learner-progress revision;
- proves an identical idempotency retry returns the committed result;
- rejects an attacker origin before forwarding;
- rejects arbitrary PUT routes;
- rejects a progress body larger than 16 KiB;
- rejects direct SaaS access without a hosted session.

## Non-goals

This boundary does not add self-registration, passwords, account recovery, refresh-token storage, browser token storage, organization administration, billing, identity-provider discovery, dynamic client registration, logout propagation to the identity provider, TLS termination, production PostgreSQL startup, or a complete public SaaS claim.
