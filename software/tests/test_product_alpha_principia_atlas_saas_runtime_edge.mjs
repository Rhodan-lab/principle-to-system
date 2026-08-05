import assert from 'node:assert/strict';
import { createServer as createHttpServer } from 'node:http';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import { createBrowserOidcEdgeServer } from '../principia_atlas/hosted/browser_edge.mjs';
import {
  PRODUCT,
  TENANT_CONTRACT,
  sealTenantConfig,
} from '../principia_atlas/hosted/catalog.mjs';
import { createSaasHostedRuntimeServer } from '../principia_atlas/hosted/saas_runtime.mjs';
import { createMemoryAuthState } from '../principia_atlas/hosted/state.mjs';
import { exchangeIdentityAssertion, signIdentityAssertion } from '../principia_atlas/hosted/tokens.mjs';
import { createSaasApplicationApi } from '../principia_atlas/saas/application_api.mjs';
import { openSaasControlPlane } from '../principia_atlas/saas/store.mjs';

const now = 1_800_300_000;
const tenantId = 'runtime-tenant';
const identitySecret = Buffer.alloc(32, 51);
const sessionSecret = Buffer.alloc(32, 52);
const csrfSecret = Buffer.alloc(32, 53);
const subjectId = `oidc:${'T'.repeat(43)}`;
const releaseId = 'principia-atlas-release:0.5.0-beta.1';

async function freePort() {
  const server = createHttpServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;
  await new Promise((resolve) => server.close(resolve));
  return port;
}

function tenantConfig() {
  return sealTenantConfig({
    contract: TENANT_CONTRACT,
    product: PRODUCT,
    identity: {
      issuer: 'https://identity.example.test',
      audience: 'principia-atlas-runtime-test',
      max_assertion_ttl_seconds: 300,
    },
    session: {
      cookie_name: 'pa_session',
      ttl_seconds: 3600,
      secure: false,
    },
    tenants: {
      [tenantId]: {
        display_name: 'Runtime Tenant',
        allowed_channels: ['beta'],
        allowed_routes: ['refrigerator-v1'],
        pinned_versions: [],
      },
    },
  });
}

function registerSession(authState, config) {
  const assertion = signIdentityAssertion({
    iss: config.identity.issuer,
    aud: config.identity.audience,
    sub: subjectId,
    tenant_id: tenantId,
    roles: ['learner'],
    iat: now,
    exp: now + 300,
    jti: 'assertion_runtime_edge_0001',
  }, identitySecret, config);
  const exchanged = exchangeIdentityAssertion(
    assertion,
    identitySecret,
    sessionSecret,
    config,
    now,
    () => 'session_runtime_edge_000000000001',
  );
  assert.equal(authState.commitExchange({
    assertionId: exchanged.assertion.jti,
    assertionExpiresAt: exchanged.assertion.exp,
    session: exchanged.session,
  }, now), true);
  return `${config.session.cookie_name}=${exchanged.token}`;
}

function inertBrowserFlow(publicOrigin) {
  let closed = false;
  return {
    config: Object.freeze({
      public_origin: publicOrigin,
      config_id: 'a'.repeat(64),
      login_path: '/auth/login',
      callback_path: '/auth/callback',
    }),
    begin() { throw new Error('login flow is outside this runtime test'); },
    complete() { throw new Error('callback flow is outside this runtime test'); },
    clear_cookie() { return 'pa_oidc_flow=; Path=/; Max-Age=0'; },
    close() { closed = true; },
    get closed() { return closed; },
  };
}

test('trusted browser edge reaches the session-aware SaaS runtime with one bounded mutation path', async () => {
  const root = mkdtempSync(join(tmpdir(), 'principia-atlas-saas-runtime-'));
  const config = tenantConfig();
  const authState = createMemoryAuthState();
  const saasState = openSaasControlPlane(join(root, 'saas.sqlite'));
  const organization = {
    id: 'org_01RUNTIMEEDGEFOUNDATI',
    slug: 'runtime-edge-lab',
    display_name: 'Runtime Edge Lab',
  };
  const owner = {
    id: 'mem_01RUNTIMEEDGEOWNER000',
    organization_id: organization.id,
    subject_id: `oidc:${'U'.repeat(43)}`,
    role: 'owner',
  };
  const learner = {
    id: 'mem_01RUNTIMEEDGELEARNER0',
    organization_id: organization.id,
    subject_id: subjectId,
    role: 'learner',
  };
  saasState.bootstrapOrganization(organization, owner, now);
  saasState.bindHostedTenant(owner.id, {
    organization_id: organization.id,
    hosted_tenant_id: tenantId,
  }, now + 1);
  saasState.addMembership(owner.id, learner, now + 2);
  saasState.grantEntitlement(owner.id, {
    organization_id: organization.id,
    route_id: 'refrigerator-v1',
    release_id: releaseId,
    starts_at: now,
    ends_at: null,
  }, now + 3);
  const cookie = registerSession(authState, config);
  const applicationApi = createSaasApplicationApi({
    controlPlane: saasState,
    csrfSecret,
  });

  const runtimePort = await freePort();
  const runtimeOrigin = `http://127.0.0.1:${runtimePort}`;
  const runtime = createSaasHostedRuntimeServer({
    config,
    authState,
    sessionSecret,
    applicationApi,
    coreOrigin: 'http://127.0.0.1:9',
    now: () => now + 10,
  });
  await new Promise((resolve) => runtime.listen(runtimePort, '127.0.0.1', resolve));

  const edgePort = await freePort();
  const edgeOrigin = `http://127.0.0.1:${edgePort}`;
  const flow = inertBrowserFlow(edgeOrigin);
  const edge = createBrowserOidcEdgeServer({
    flow,
    upstreamOrigin: runtimeOrigin,
    now: () => now + 10,
  });
  await new Promise((resolve) => edge.listen(edgePort, '127.0.0.1', resolve));

  try {
    const meResponse = await fetch(`${edgeOrigin}/api/saas/me`, {
      headers: { Cookie: cookie },
    });
    assert.equal(meResponse.status, 200);
    const me = await meResponse.json();
    assert.equal(me.organization.id, organization.id);
    assert.equal(me.membership.id, learner.id);
    assert.match(me.csrf_token, /^[A-Za-z0-9_-]{43}$/);
    assert.equal(JSON.stringify(me).includes(subjectId), false);

    const mutation = {
      release_id: releaseId,
      status: 'completed',
      expected_revision: 0,
    };
    const headers = {
      Cookie: cookie,
      Origin: edgeOrigin,
      'Content-Type': 'application/json',
      'X-CSRF-Token': me.csrf_token,
      'Idempotency-Key': 'runtime_edge_progress_0001',
    };
    const first = await fetch(`${edgeOrigin}/api/saas/progress/refrigerator-v1/observe`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(mutation),
    });
    assert.equal(first.status, 200);
    assert.equal(first.headers.get('idempotency-replayed'), 'false');
    const firstBody = await first.json();
    assert.equal(firstBody.progress.revision, 1);

    const replay = await fetch(`${edgeOrigin}/api/saas/progress/refrigerator-v1/observe`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(mutation),
    });
    assert.equal(replay.status, 200);
    assert.equal(replay.headers.get('idempotency-replayed'), 'true');
    assert.deepEqual(await replay.json(), firstBody);

    const attacker = await fetch(`${edgeOrigin}/api/saas/progress/refrigerator-v1/map`, {
      method: 'PUT',
      headers: { ...headers, Origin: 'https://attacker.test', 'Idempotency-Key': 'runtime_edge_progress_0002' },
      body: JSON.stringify(mutation),
    });
    assert.equal(attacker.status, 403);
    assert.deepEqual(await attacker.json(), { error: 'origin_rejected' });

    const arbitraryPut = await fetch(`${edgeOrigin}/api/catalog`, {
      method: 'PUT',
      headers: { Origin: edgeOrigin },
    });
    assert.equal(arbitraryPut.status, 405);

    const oversized = await fetch(`${edgeOrigin}/api/saas/progress/refrigerator-v1/map`, {
      method: 'PUT',
      headers: { ...headers, 'Idempotency-Key': 'runtime_edge_progress_0003' },
      body: JSON.stringify({ ...mutation, padding: 'x'.repeat(17 * 1024) }),
    });
    assert.equal(oversized.status, 413);
    assert.deepEqual(await oversized.json(), { error: 'request_too_large' });

    const directWithoutSession = await fetch(`${runtimeOrigin}/api/saas/me`);
    assert.equal(directWithoutSession.status, 401);
    assert.deepEqual(await directWithoutSession.json(), { error: 'session_required' });
  } finally {
    await new Promise((resolve) => edge.close(resolve));
    await new Promise((resolve) => runtime.close(resolve));
    assert.equal(flow.closed, true);
    saasState.close();
    authState.close();
    rmSync(root, { recursive: true, force: true });
  }
});
