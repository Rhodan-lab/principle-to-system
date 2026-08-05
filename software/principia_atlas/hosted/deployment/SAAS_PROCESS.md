---
title: Principia & Atlas SaaS runtime process and readiness
status: implemented-contract-not-packaged
last_reviewed: 2026-08-05
content_license: CC-BY-4.0
---

# Principia & Atlas SaaS runtime process and readiness

This runbook defines the bounded process that owns PostgreSQL migration, the SaaS control plane, the application API, the loopback runtime facade, readiness, and graceful shutdown. It does not claim that the current OCI image or Kubernetes example contains the final production PostgreSQL driver.

## Process contracts

```text
principia-atlas-saas-process/0.1
  -> principia-atlas-saas-hosted-runtime/0.2
  -> principia-atlas-saas-application-api/0.1
  -> principia-atlas-saas-control-plane/0.1
  -> principia-atlas-saas-postgres-migrations/0.1
```

The startup sequence is intentionally ordered:

1. read and verify the sealed tenant configuration;
2. read the hosted session secret, SaaS CSRF secret, and PostgreSQL URL from restrictive regular files;
3. require `sslmode=verify-full` in the PostgreSQL URL;
4. load a read-only PostgreSQL driver module;
5. open the durable SQLite hosted-auth state;
6. create the bounded PostgreSQL pool;
7. acquire the migration advisory lock and verify/apply every immutable migration;
8. create the PostgreSQL SaaS control plane;
9. create the same-origin application API;
10. create the loopback runtime facade;
11. bind the listening socket only after every previous step succeeds.

A migration, configuration, TLS, driver, auth-state, or pool failure occurs before the runtime begins accepting requests.

## Secret-file boundary

The CLI is:

```text
software/principia_atlas/hosted/saas_runtime_cli.mjs
```

It accepts paths rather than secret values:

```bash
node software/principia_atlas/hosted/saas_runtime_cli.mjs \
  --tenants /run/config/tenants.json \
  --state /var/lib/principia-atlas/auth.sqlite \
  --session-secret-file /run/secrets/session \
  --csrf-secret-file /run/secrets/saas-csrf \
  --database-url-file /run/secrets/database-url \
  --postgres-driver-module /opt/principia-atlas/drivers/postgres.mjs \
  --postgres-ca-file /run/config/postgres-ca.pem \
  --core-origin http://127.0.0.1:8080 \
  --host 127.0.0.1 \
  --port 8082
```

The session secret, CSRF secret, database URL, database credentials, and CA contents are never printed. The CLI does not accept a database URL value in argv. Secret buffers are overwritten after construction or after a failed startup.

The PostgreSQL URL must contain exactly one:

```text
sslmode=verify-full
```

The PostgreSQL driver module must be a bounded regular file with no write bits. Its import identity is bound to the SHA-256 of the bytes inspected before import. The final image must place the driver and its locked dependencies on a read-only root filesystem.

## Liveness and readiness

The loopback facade exposes:

```text
GET|HEAD /saas/healthz
GET|HEAD /saas/readyz
```

`/saas/healthz` proves only that the facade process can answer. It does not query PostgreSQL or the immutable release core. A database outage must not create an automatic restart loop that hides the dependency failure.

`/saas/readyz` succeeds only when all of these conditions hold:

- hosted auth state reports healthy;
- PostgreSQL migration ledger and SaaS control plane report healthy;
- the immutable hosted core returns a successful bounded response from `/readyz`.

The response is deliberately generic. It does not expose tenant identifiers, migration versions, database endpoints, release identities, auth statistics, or internal topology.

The production process hides both readiness paths from browser-proxied requests. The trusted browser edge always sets an `Origin` header on upstream requests; an internal readiness request carrying `Origin` receives `404`. Kubernetes probes call the loopback port directly without `Origin`.

## Ownership and shutdown

The process owner can own the PostgreSQL pool and SQLite auth state. Graceful shutdown follows this sequence:

1. stop accepting new connections;
2. close idle connections;
3. force-close remaining sockets only after the bounded timeout;
4. overwrite the application CSRF secret copy;
5. close the SaaS control plane;
6. end the PostgreSQL pool;
7. close the hosted auth state.

Cleanup attempts continue even when an earlier cleanup operation fails. The first failure is reported after every owned resource has received a close attempt.

## Scaling boundary

The SaaS business state is PostgreSQL-backed and multi-instance capable. Hosted session/revocation state is still SQLite-backed. The existing Kubernetes StatefulSet must therefore not be scaled as a general-availability SaaS deployment without a reviewed shared-auth-state design.

A bounded public beta may use one pod with a persistent auth-state volume and external PostgreSQL, provided operational availability limitations are explicit. Horizontal scaling and zero-downtime failover remain blocked until the auth-state authority is moved to a genuinely shared transactional backend or otherwise proven safe.

## Driver and image boundary

This change does not install `pg` dynamically in the Containerfile. A network-time `npm install pg@...` without a committed lockfile would make identical source commits produce different images.

The next packaging unit must provide:

- an exact dependency lockfile;
- a reproducible driver layer;
- a read-only driver module;
- image verification proving the driver and transitive dependencies are identical across builds;
- a three-process pod topology: immutable core, SaaS facade, and public browser edge;
- PostgreSQL TLS CA, database URL, CSRF secret, and session secret mounts;
- loopback probes for the core and facade;
- NetworkPolicy egress limited to DNS, the identity provider, and PostgreSQL;
- backup and restore evidence before public beta.

Until that unit is complete:

```json
{
  "startup_contract_ready": true,
  "readiness_contract_ready": true,
  "postgres_driver_packaged": false,
  "deployment_manifest_ready": false,
  "public_deployment_ready": false,
  "production_ready": false
}
```
