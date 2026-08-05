import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { chmod, lstat, mkdtemp, readFile, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import {
  CATALOG_CONTRACT,
  PRODUCT,
  TENANT_CONTRACT,
  canonicalJson,
  createControlPlaneServer,
  openSqliteAuthState,
  sealTenantConfig,
  sha256Hex,
  signIdentityAssertion,
} from '../principia_atlas/hosted/index.mjs';
import {
  backupAuthState,
  inspectAuthState,
  restoreAuthState,
  verifyAuthBackup,
} from '../principia_atlas/hosted/auth_state_recovery.mjs';
import {
  AUDIT_CONTRACT,
  createAuditLogger,
  createMetricsRegistry,
} from '../principia_atlas/hosted/observability.mjs';
import { readSecretFile } from '../principia_atlas/hosted/secrets.mjs';
import { gracefulShutdown } from '../principia_atlas/hosted/server.mjs';

const identitySecret = 'identity-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const sessionSecret = 'session-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const metricsToken = 'metrics-token-0123456789-abcdefghijklmnopqrstuvwxyz';
const now = 1_800_000_000;

function seal(unsigned, field) {
  return { ...unsigned, [field]: sha256Hex(canonicalJson(unsigned)) };
}

function catalog() {
  const version = '0.1.0-alpha.1';
  const boundaries = {
    authorities_separate: true,
    status_inheritance: 'prohibited',
    live_cross_repository_dependency: false,
    canonical_mutation: false,
  };
  const runtime = { host: '127.0.0.1', external_network_required: false, python: '>=3.10' };
  const entrypoints = {
    verify: 'launcher.py verify',
    run: 'launcher.py run',
    linux_macos: 'launch.sh',
    macos_double_click: 'launch.command',
    windows: 'launch.cmd',
  };
  const release = {
    tag: `principia-atlas-v${version}`,
    channel: 'alpha',
    promotion_id: 'a'.repeat(64),
    release: {
      release_id: 'b'.repeat(64),
      bundle_id: 'c'.repeat(64),
      receipt_id: 'd'.repeat(64),
      route_id: 'distributed-information',
      archive: {
        name: `principia-atlas-${version}.zip`,
        sha256: 'e'.repeat(64),
        checksum_name: `principia-atlas-${version}.zip.sha256`,
      },
    },
    sources: {
      principia: { repository: 'Rhodan-lab/principle-to-system', commit: '1'.repeat(40) },
      atlas: { repository: 'Rhodan-lab/Atlas', commit: '2'.repeat(40) },
    },
    compatibility: {
      release_contract: 'principia-atlas-release/0.1',
      route_id: 'distributed-information',
      entrypoints,
      runtime,
      boundaries,
    },
  };
  return seal({
    contract: CATALOG_CONTRACT,
    product: PRODUCT,
    release_count: 1,
    releases: { [version]: release },
    channels: {
      alpha: { version, tag: release.tag, promotion_id: release.promotion_id },
      beta: null,
      stable: null,
    },
  }, 'catalog_id');
}

function config() {
  return sealTenantConfig({
    contract: TENANT_CONTRACT,
    product: PRODUCT,
    identity: {
      issuer: 'https://identity.example.test',
      audience: 'principia-atlas-hosted',
      max_assertion_ttl_seconds: 300,
    },
    session: { cookie_name: 'pa_session', ttl_seconds: 3600, secure: false },
    tenants: {
      'school-demo': {
        display_name: 'School Demo',
        allowed_channels: ['alpha'],
        allowed_routes: ['distributed-information'],
        pinned_versions: [],
      },
    },
  });
}

function sessionRecord() {
  return {
    contract: 'principia-atlas-hosted-session/0.2',
    sub: 'learner-1',
    tenant_id: 'school-demo',
    roles: ['learner'],
    iat: now,
    exp: now + 3600,
    jti: 'assertion_identifier_1234',
    sid: 'session_identifier_1234567890',
  };
}

test('secret files are bounded regular files with restrictive permissions', async () => {
  const root = await mkdtemp(join(tmpdir(), 'principia-secrets-'));
  const secret = join(root, 'identity');
  await writeFile(secret, `${identitySecret}\n`, { mode: 0o600 });
  assert.equal(readSecretFile(secret, 'identity secret').toString('utf8'), identitySecret);
  await chmod(secret, 0o640);
  assert.equal(readSecretFile(secret, 'identity secret').toString('utf8'), identitySecret);
  await chmod(secret, 0o644);
  assert.throws(() => readSecretFile(secret, 'identity secret'), /permissions/);
  const linked = join(root, 'linked');
  try {
    await symlink(secret, linked);
    assert.throws(() => readSecretFile(linked, 'identity secret'), /regular file/);
  } catch (error) {
    if (error?.code !== 'EPERM') throw error;
  }
});

test('control plane owns secret copies after startup', async () => {
  const identity = Buffer.from(identitySecret);
  const session = Buffer.from(sessionSecret);
  const server = createControlPlaneServer({
    catalog: catalog(),
    config: config(),
    identitySecret: identity,
    sessionSecret: session,
    metricsToken,
    now: () => now,
  });
  identity.fill(0);
  session.fill(0);
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  try {
    const address = server.address();
    const base = `http://127.0.0.1:${address.port}`;
    const assertion = signIdentityAssertion({
      iss: 'https://identity.example.test',
      aud: 'principia-atlas-hosted',
      sub: 'learner-1',
      tenant_id: 'school-demo',
      roles: ['learner'],
      iat: now,
      exp: now + 180,
      jti: 'assertion_identifier_copy',
    }, identitySecret, config());
    const response = await fetch(`${base}/api/auth/exchange`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${assertion}`, Origin: base },
    });
    assert.equal(response.status, 200);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('audit records are canonical bounded and reject sensitive field names', async () => {
  const root = await mkdtemp(join(tmpdir(), 'principia-audit-'));
  const path = join(root, 'audit.ndjson');
  const audit = createAuditLogger({ path, instanceId: 'instance-a', now: () => now });
  const event = audit.event('auth.exchange', {
    outcome: 'success',
    request_id: 'request-1',
    tenant_id: 'school-demo',
  });
  assert.equal(event.contract, AUDIT_CONTRACT);
  assert.throws(() => audit.event('auth.exchange', { subject: 'learner-1' }), /field name/);
  assert.throws(() => audit.event('auth.exchange', { session_id: 'hidden' }), /field name/);
  audit.close();
  const lines = (await readFile(path, 'utf8')).trim().split('\n');
  assert.equal(lines.length, 1);
  assert.deepEqual(JSON.parse(lines[0]), event);
  assert.equal((await lstat(path)).mode & 0o077, 0);
});

test('metrics expose bounded aggregate data without tenant or subject labels', () => {
  const metrics = createMetricsRegistry({ startedAtMs: 1000 });
  metrics.setReady(true);
  metrics.beginRequest();
  metrics.endRequest(200, 42);
  metrics.auth('success');
  metrics.release(12);
  const output = metrics.render(4000);
  assert.match(output, /principia_atlas_ready 1/);
  assert.match(output, /principia_atlas_http_requests_total\{class="2xx"\} 1/);
  assert.match(output, /principia_atlas_auth_exchanges_total\{outcome="success"\} 1/);
  assert.equal(/tenant|subject|session|assertion/i.test(output), false);
});

test('auth state backup verifies and restores a registered session', async () => {
  const root = await mkdtemp(join(tmpdir(), 'principia-recovery-'));
  const source = join(root, 'state.sqlite');
  const backup = join(root, 'backup.sqlite');
  const restoredPath = join(root, 'restored.sqlite');
  const record = sessionRecord();
  const state = openSqliteAuthState(source);
  assert.equal(state.commitExchange({
    assertionId: record.jti,
    assertionExpiresAt: now + 180,
    session: record,
  }, now), true);
  state.close();

  assert.equal(inspectAuthState(source).status, 'ok');
  const created = backupAuthState(source, backup);
  assert.equal(created.status, 'ok');
  assert.equal(verifyAuthBackup(backup).sha256, created.sha256);
  assert.throws(() => restoreAuthState(backup, restoredPath, 'NOT_STOPPED'), /confirmation/);
  const restored = restoreAuthState(backup, restoredPath, 'ALL_INSTANCES_STOPPED');
  assert.equal(restored.status, 'ok');
  const reopened = openSqliteAuthState(restoredPath);
  try {
    assert.equal(reopened.validateSession(record, now + 1), true);
  } finally {
    reopened.close();
  }

  await writeFile(`${backup}.sha256`, `${'0'.repeat(64)}  backup.sqlite\n`, { mode: 0o600 });
  assert.throws(() => verifyAuthBackup(backup), /checksum/);
});

test('graceful shutdown is idempotent and closes state and audit once', async () => {
  const events = [];
  let stateClosed = 0;
  let auditClosed = 0;
  const server = createServer((_request, response) => response.end('ok'));
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const options = {
    server,
    authState: { close() { stateClosed += 1; } },
    audit: {
      event(name, fields) { events.push([name, fields]); },
      close() { auditClosed += 1; },
    },
    signal: 'SIGTERM',
    timeoutMs: 1000,
  };
  const first = gracefulShutdown(options);
  const second = gracefulShutdown(options);
  assert.equal(first, second);
  assert.deepEqual(await first, { forced: false, signal: 'SIGTERM' });
  assert.equal(stateClosed, 1);
  assert.equal(auditClosed, 1);
  assert.deepEqual(events.map(([name]) => name), ['server.drain', 'server.stop']);
});

test('canonical container and deployment manifests preserve trusted-edge boundaries', async () => {
  const container = await readFile('software/principia_atlas/hosted/Containerfile', 'utf8');
  assert.match(container, /^FROM node:24\.18\.0-bookworm-slim@sha256:[0-9a-f]{64}$/m);
  assert.match(container, /^USER 10001:10001$/m);
  assert.match(container, /^EXPOSE 8080 8081$/m);
  assert.match(container, /^STOPSIGNAL SIGTERM$/m);
  assert.equal(container.includes(':latest'), false);

  const deployment = await readFile('software/principia_atlas/hosted/deployment/kubernetes.example.yaml', 'utf8');
  assert.match(deployment, /name: principia-atlas-hosted-headless/);
  assert.match(deployment, /name: principia-atlas-browser-edge/);
  assert.match(deployment, /serviceName: principia-atlas-hosted-headless/);
  assert.match(deployment, /replicas: 2/);
  assert.match(deployment, /readOnlyRootFilesystem: true/);
  assert.match(deployment, /allowPrivilegeEscalation: false/);
  assert.match(deployment, /claimName: principia-atlas-auth-state/);

  const hosted = deployment.split('        - name: hosted\n')[1].split('        - name: browser-edge\n')[0];
  const edge = deployment.split('        - name: browser-edge\n')[1].split('      volumes:\n')[0];
  assert.match(hosted, /- --oidc-policy\n\s+- \/config\/oidc-policy\.json/);
  assert.match(hosted, /- --oidc-remote-jwks/);
  assert.match(hosted, /- --host\n\s+- 127\.0\.0\.1/);
  assert.match(hosted, /fetch\('http:\/\/127\.0\.0\.1:8080\/readyz'\)/);
  assert.match(hosted, /fetch\('http:\/\/127\.0\.0\.1:8080\/healthz'\)/);
  assert.equal(hosted.includes('--allow-network'), false);
  assert.equal(hosted.includes('containerPort: 8080'), false);

  assert.match(edge, /\/opt\/principia-atlas\/hosted\/browser_edge_cli\.mjs/);
  assert.match(edge, /- \/config\/browser-oidc\.json/);
  assert.match(edge, /- \/run\/secrets\/browser-flow/);
  assert.match(edge, /- \/run\/secrets\/browser-client/);
  assert.match(edge, /- http:\/\/127\.0\.0\.1:8080/);
  assert.match(edge, /- --host\n\s+- 0\.0\.0\.0/);
  assert.match(edge, /containerPort: 8081/);
  assert.match(edge, /path: \/edge\/healthz/);
  assert.match(edge, /- --allow-network/);

  assert.equal(deployment.includes('containerPort: 8080'), false);
  assert.match(deployment, /targetPort: edge-http/);
  assert.match(deployment, /port: 8081/);
  assert.match(deployment, /kubernetes\.io\/metadata\.name: kube-system/);
  assert.match(deployment, /k8s-app: kube-dns/);
  assert.match(deployment, /cidr: 203\.0\.113\.0\/24/);
  assert.equal(deployment.includes('egress: []'), false);
  const ingress = deployment.split('  ingress:\n')[1].split('  egress:\n')[0];
  assert.match(ingress, /port: 8081/);
  assert.equal(ingress.includes('port: 8080'), false);
});
