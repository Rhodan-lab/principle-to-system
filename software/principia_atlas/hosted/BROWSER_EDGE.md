# Trusted browser OIDC edge

The hosted control plane already verifies external OIDC ID tokens and creates durable Principia & Atlas sessions. The browser edge adds the missing browser-facing Authorization Code flow with PKCE without moving identity, tenant, content, or status authority into the browser layer.

The edge is a separate process in front of the existing hosted runtime:

```text
browser
  -> HTTPS browser edge
      -> identity provider authorization and token endpoints
      -> loopback-only Principia & Atlas hosted runtime
```

The hosted runtime remains the only component that cryptographically accepts the returned ID token, maps external claims through the sealed tenant policy, claims token replay identity, registers the session, and issues the hosted session cookie.

## Security boundary

The edge:

- uses Authorization Code with PKCE `S256`, random state, and random nonce;
- stores the short-lived flow state only in an authenticated AES-256-GCM HttpOnly cookie;
- permits only same-origin relative return paths and rejects authentication routes as return targets;
- sends the code verifier and optional client secret only to the exact sealed HTTPS token endpoint;
- refuses token-endpoint redirects, oversized responses, non-JSON responses, duplicate callback parameters, issuer mismatch, nonce mismatch, and malformed JWT structure;
- rejects `offline_access` and any returned refresh token;
- forwards only the returned ID token to the loopback hosted `/api/auth/oidc` endpoint;
- never exposes `/api/auth/oidc`, `/api/auth/exchange`, or `/metrics` through the public proxy;
- rewrites browser-origin requests to the exact loopback upstream origin;
- accepts no request body on proxied routes;
- does not persist authorization codes, tokens, external subjects, client secrets, or learner records.

The edge performs structural issuer and nonce checks before the ID token reaches the hosted runtime. Those checks do not replace signature verification. The existing hosted OIDC verifier remains authoritative for signature, algorithm, key, issuer, audience, authorized-party, time, required-claim, tenant, and role validation.

## Create a sealed configuration

Start from the example and replace the issuer, endpoints, public origin, client ID, scopes, and routes with reviewed deployment values:

```bash
node software/principia_atlas/hosted/browser_edge_cli.mjs seal \
  --input software/principia_atlas/hosted/example-browser-oidc.unsigned.json \
  --output /tmp/hosted/browser-oidc.json

node software/principia_atlas/hosted/browser_edge_cli.mjs verify \
  --config /tmp/hosted/browser-oidc.json
```

The browser configuration issuer must match the issuer in the hosted OIDC policy. The identity-provider client must register the exact callback URI:

```text
<public_origin><callback_path>
```

For the example, that is:

```text
https://learn.example.test/auth/callback
```

The scope set must contain `openid` and must not contain `offline_access`.

## Secret files

The flow secret encrypts browser flow cookies. A confidential OIDC client also requires a separate client secret. Both use the existing restrictive regular-file boundary:

```bash
install -m 0400 /dev/null /tmp/hosted/browser-flow.secret
install -m 0400 /dev/null /tmp/hosted/browser-client.secret
```

Populate them through a controlled secret manager. Do not use command-line values or environment variables. A public client configured with `client_auth_method: none` must not receive a client-secret file.

## Run the edge

Run the existing hosted server on loopback, for example `127.0.0.1:8080`, with its production OIDC verifier enabled. Then run the browser edge:

```bash
node software/principia_atlas/hosted/browser_edge_cli.mjs serve \
  --config /tmp/hosted/browser-oidc.json \
  --flow-secret-file /tmp/hosted/browser-flow.secret \
  --client-secret-file /tmp/hosted/browser-client.secret \
  --upstream-origin http://127.0.0.1:8080 \
  --host 0.0.0.0 \
  --port 8443 \
  --allow-network
```

TLS termination must be provided by a reviewed deployment boundary. Non-loopback binding requires explicit `--allow-network`, and the sealed public origin must use HTTPS. The upstream origin is restricted to an exact loopback HTTP or HTTPS origin.

A request to `/` without a valid hosted session starts the login flow. After callback completion, the edge forwards the ID token to the hosted runtime, relays the hosted session cookie, clears the flow cookie, and redirects only to the encrypted same-origin return path.

The edge health endpoint is:

```text
/edge/healthz
```

It exposes only the edge contract, sealed configuration ID, and a generic loopback-upstream status. It does not expose endpoints, secrets, tokens, subjects, tenants, or release identities.

## Non-goals

This edge does not add self-registration, passwords, account recovery, refresh-token storage, browser token storage, learner-event persistence, organization administration, billing, identity-provider discovery, dynamic client registration, logout propagation to the identity provider, TLS termination, or a complete production SaaS claim.
