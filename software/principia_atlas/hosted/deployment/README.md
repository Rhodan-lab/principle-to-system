# Hosted deployment and recovery plane

This directory contains the operational boundary for deploying the authenticated, read-only Principia & Atlas hosted runtime. It does not grant promotion authority, mutate release content, or introduce learner-data persistence.

## Image boundary

`../Containerfile` is the canonical image definition for both processes in the hosted pod. It uses a digest-pinned Node.js base, fixed OCI metadata, UID/GID `10001`, read-only application files, `SIGTERM`, and no package installation during runtime.

A deployment must additionally enforce:

- a read-only root filesystem;
- no privilege escalation and all Linux capabilities dropped;
- read-only mounts for catalog, tenant config, OIDC policies, release store, and secret files;
- writable mounts only for shared authentication state, audit output, and bounded temporary storage;
- a verified image digest rather than a mutable tag;
- external TLS termination before non-loopback traffic reaches the browser edge.

## Trusted-edge pod boundary

`kubernetes.example.yaml` runs two containers from the same verified image inside each pod:

- `hosted` binds only to `127.0.0.1:8080` and owns OIDC signature verification, tenant mapping, replay protection, durable sessions, release entitlement, audit, and metrics;
- `browser-edge` binds to `0.0.0.0:8081`, performs Authorization Code with PKCE, and is the only network-visible HTTP process.

The public `principia-atlas-browser-edge` Service targets port `8081`. No Service, container port, or NetworkPolicy ingress rule exposes the hosted control plane on port `8080`. The edge forwards only the returned ID token to the exact loopback hosted origin.

Because containers in one Kubernetes pod share a network namespace, the edge can use `http://127.0.0.1:8080` without making the control plane reachable from another pod. Hosted liveness and readiness checks use in-container `exec` probes for the same reason.

TLS remains an external deployment responsibility. A reviewed ingress controller or gateway must terminate HTTPS and forward to the edge Service without exposing the hosted port.

## Two-instance boundary

The example runs two pods sharing one SQLite state volume. This is valid only when the volume provides correct POSIX file locking and durable local-filesystem semantics. It is not a distributed database, multi-region design, or automatic failover system.

Both pods must use the same:

- sealed hosted catalog;
- sealed tenant configuration;
- sealed hosted OIDC policy;
- sealed browser OIDC configuration;
- immutable release store;
- identity and session secret generation;
- browser flow secret and OIDC client secret;
- shared SQLite authentication state.

Each hosted container uses a distinct audit instance identifier. The browser flow is self-contained in an authenticated encrypted cookie, so callbacks can reach either pod when every replica shares the same sealed browser configuration and flow secret. Sticky sessions are not required.

## Configuration files

The `principia-atlas-hosted-config` ConfigMap must contain reviewed, sealed files at these paths:

```text
/config/catalog.json
/config/tenants.json
/config/oidc-policy.json
/config/browser-oidc.json
```

The browser configuration issuer must match the hosted OIDC policy issuer. Its public origin must be the externally visible HTTPS origin, not the internal Service address. Register the exact `<public_origin><callback_path>` URI with the identity provider.

Create and verify the browser configuration before publishing the ConfigMap:

```bash
node software/principia_atlas/hosted/browser_edge_cli.mjs seal \
  --input software/principia_atlas/hosted/example-browser-oidc.unsigned.json \
  --output /tmp/browser-oidc.json

node software/principia_atlas/hosted/browser_edge_cli.mjs verify \
  --config /tmp/browser-oidc.json
```

The hosted OIDC policy must likewise be sealed and verified with the OIDC operator tooling before deployment.

## Secret files

Runtime secrets are loaded from regular files and copied into process-owned buffers. Files must not be symlinks, executable, group-writable, or accessible to other users. Environment-variable secret loading is intentionally not supported.

The `principia-atlas-hosted-secrets` Secret must provide:

```text
/run/secrets/identity
/run/secrets/session
/run/secrets/browser-flow
/run/secrets/browser-client
```

The protected metrics token is optional:

```text
/run/secrets/metrics
```

Identity and session secrets must be distinct. The browser-flow secret must be shared across replicas but distinct from identity, session, metrics, and client secrets. Secret buffers are cleared when each process closes.

A public OIDC client configured with `client_auth_method: none` must remove both `--client-secret-file` and the `browser-client` Secret entry.

## Identity-provider egress

The pod requires DNS plus HTTPS egress to the exact identity-provider authorization, token, and JWKS endpoints. Kubernetes NetworkPolicy applies to the whole pod rather than one container, so the hosted verifier and browser edge share this bounded egress allowance.

The example uses the documentation-only CIDR `203.0.113.0/24`. This is intentionally fail-closed and must be replaced with reviewed identity-provider CIDRs before deployment. Do not replace it with unrestricted `0.0.0.0/0` egress. When the provider does not publish stable CIDRs, enforce exact hostnames and TLS policy in an egress proxy or equivalent network boundary.

## Liveness, readiness, and metrics

- browser-edge liveness and readiness use `/edge/healthz` on port `8081`;
- hosted liveness uses loopback `/healthz` through an `exec` probe;
- hosted readiness uses loopback `/readyz` through an `exec` probe;
- `/metrics` remains available only on the loopback hosted process with its configured bearer token.

Metrics contain bounded aggregate counters and gauges only. They do not include tenant, subject, session, assertion, release path, or token labels. A metrics collector must run in the same pod or use another explicitly reviewed loopback-access mechanism; the public edge never proxies `/metrics`.

## Audit boundary

Audit records use `principia-atlas-hosted-audit-event/0.1`, canonical JSON lines, bounded values, and per-process sequence numbers. Sensitive field names are rejected. Audit storage must be protected and collected outside the runtime for retention and alerting.

## Backup

An online backup can be created while instances are running:

```bash
node software/principia_atlas/hosted/auth_state_recovery.mjs backup \
  --state /state/auth-state.sqlite \
  --output /backup/auth-state.sqlite

node software/principia_atlas/hosted/auth_state_recovery.mjs verify \
  --backup /backup/auth-state.sqlite
```

The backup is created through SQLite `VACUUM INTO`, checked with both `quick_check` and `integrity_check`, sealed by an exact SHA-256 sidecar, and published as an atomic pair.

## Restore

Restore is offline-only. Stop every pod and verify that no WAL or shared-memory file remains:

```bash
node software/principia_atlas/hosted/auth_state_recovery.mjs restore \
  --backup /backup/auth-state.sqlite \
  --state /state/auth-state.sqlite \
  --confirm-offline ALL_INSTANCES_STOPPED

node software/principia_atlas/hosted/auth_state_recovery.mjs integrity \
  --state /state/auth-state.sqlite
```

Restore stages and validates the replacement, swaps it atomically, and restores the previous state on post-swap failure.

## Rolling restart

During a rolling restart:

1. remove one pod from edge readiness;
2. send `SIGTERM` to both containers;
3. allow in-flight requests to drain within the configured timeout;
4. confirm another pod can still validate an existing hosted session and complete a fresh browser login;
5. start and verify the replacement before stopping the next pod.

Both processes stop accepting new connections before closing their owned state. A bounded timeout destroys remaining sockets rather than hanging indefinitely.

## Remaining non-goals

- no identity-provider discovery or dynamic client registration;
- no identity-provider logout propagation or account recovery;
- no distributed SQL or multi-region session coordination;
- no automated backup scheduler or retention service;
- no external metrics collector or alert policy;
- no audit retention service;
- no learner records, organization administration, billing, or self-registration;
- no claim of complete production SaaS readiness.
