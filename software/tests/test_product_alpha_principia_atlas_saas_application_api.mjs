import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { Readable } from 'node:stream';
import test from 'node:test';

import { createSaasApplicationApi } from '../principia_atlas/saas/application_api.mjs';
import { openSaasControlPlane } from '../principia_atlas/saas/store.mjs';

const now = 1_800_200_000;
const hostedTenant = 'public-science-tenant';
const organization = {
  id: 'org_01APPLICATIONAPIFOUND',
  slug: 'application-lab',
  display_name: 'Application Lab',
};
const owner = {
  id: 'mem_01APPLICATIONAPIOWNER',
  organization_id: organization.id,
  subject_id: `oidc:${'R'.repeat(43)}`,
  role: 'owner',
};
const learner = {
  id: 'mem_01APPLICATIONAPILEARN',
  organization_id: organization.id,
  subject_id: `oidc:${'S'.repeat(43)}`,
  role: 'learner',
};
const releaseId = 'principia-atlas-release:0.4.0-beta.1';
const session = Object.freeze({
  sid: 'sid_application_api_0001',
  sub: learner.subject_id,
  tenant_id: hostedTenant,
  exp: now + 3600,
});

function request(method, path, { headers = {}, body = null } = {}) {
  const raw = body === null ? null : Buffer.from(typeof body === 'string' ? body : JSON.stringify(body));
  const stream = Readable.from(raw === null ? [] : [raw]);
  stream.method = method;
  stream.headers = {};
  for (const [name, value] of Object.entries(headers)) stream.headers[name.toLowerCase()] = String(value);
  if (raw !== null && stream.headers['content-length'] === undefined) stream.headers['content-length'] = String(raw.length);
  return {
    request: stream,
    url: new URL(path, 'http://app.test'),
    session,
    nowSeconds: now + 10,
    requestId: 'request_application_api_test',
  };
}

async function seed(state) {
  state.bootstrapOrganization(organization, owner, now);
  state.bindHostedTenant(owner.id, {
    organization_id: organization.id,
    hosted_tenant_id: hostedTenant,
  }, now + 1);
  state.addMembership(owner.id, learner, now + 2);
  state.grantEntitlement(owner.id, {
    organization_id: organization.id,
    route_id: 'refrigerator-v1',
    release_id: releaseId,
    starts_at: now,
    ends_at: null,
  }, now + 3);
}

test('same-origin API derives tenant and member from the trusted session', async () => {
  const root = mkdtempSync(join(tmpdir(), 'principia-atlas-saas-api-'));
  const state = openSaasControlPlane(join(root, 'saas.sqlite'));
  const api = createSaasApplicationApi({
    controlPlane: state,
    csrfSecret: Buffer.alloc(32, 41),
  });
  try {
    await seed(state);

    const resolved = state.resolveSession(hostedTenant, learner.subject_id, now + 4);
    assert.equal(resolved.membership.id, learner.id);
    assert.equal(JSON.stringify(resolved).includes(learner.subject_id), false);
    assert.equal(state.resolveSession('other-tenant', learner.subject_id, now + 4), null);

    const me = await api.handle(request('GET', '/api/saas/me'));
    assert.equal(me.status, 200);
    assert.equal(me.body.organization.id, organization.id);
    assert.equal(me.body.membership.id, learner.id);
    assert.match(me.body.csrf_token, /^[A-Za-z0-9_-]{43}$/);
    assert.equal(JSON.stringify(me.body).includes(learner.subject_id), false);

    const dashboard = await api.handle(request('GET', '/api/saas/dashboard'));
    assert.equal(dashboard.status, 200);
    assert.equal(dashboard.body.entitlements.length, 1);
    assert.equal(dashboard.body.progress.length, 0);

    const mutationBody = {
      release_id: releaseId,
      status: 'completed',
      expected_revision: 0,
    };
    const mutationHeaders = {
      host: 'app.test',
      origin: 'http://app.test',
      'content-type': 'application/json',
      'x-csrf-token': me.body.csrf_token,
      'idempotency-key': 'progress_write_000001',
    };
    const first = await api.handle(request(
      'PUT',
      '/api/saas/progress/refrigerator-v1/observe',
      { headers: mutationHeaders, body: mutationBody },
    ));
    assert.equal(first.status, 200);
    assert.equal(first.body.progress.revision, 1);
    assert.equal(first.headers['Idempotency-Replayed'], 'false');

    const replay = await api.handle(request(
      'PUT',
      '/api/saas/progress/refrigerator-v1/observe',
      { headers: mutationHeaders, body: mutationBody },
    ));
    assert.equal(replay.status, 200);
    assert.deepEqual(replay.body, first.body);
    assert.equal(replay.headers['Idempotency-Replayed'], 'true');

    const conflictingKey = await api.handle(request(
      'PUT',
      '/api/saas/progress/refrigerator-v1/observe',
      {
        headers: mutationHeaders,
        body: { ...mutationBody, status: 'in_progress' },
      },
    ));
    assert.deepEqual(conflictingKey.body, { error: 'idempotency_conflict' });
    assert.equal(conflictingKey.status, 409);

    const stale = await api.handle(request(
      'PUT',
      '/api/saas/progress/refrigerator-v1/observe',
      {
        headers: { ...mutationHeaders, 'idempotency-key': 'progress_write_000002' },
        body: mutationBody,
      },
    ));
    assert.equal(stale.status, 409);
    assert.deepEqual(stale.body, { error: 'progress_revision_conflict' });

    const originless = await api.handle(request(
      'PUT',
      '/api/saas/progress/refrigerator-v1/map',
      {
        headers: {
          host: 'app.test',
          'content-type': 'application/json',
          'x-csrf-token': me.body.csrf_token,
          'idempotency-key': 'progress_write_000003',
        },
        body: mutationBody,
      },
    ));
    assert.equal(originless.status, 403);
    assert.deepEqual(originless.body, { error: 'origin_rejected' });

    const badCsrf = await api.handle(request(
      'PUT',
      '/api/saas/progress/refrigerator-v1/map',
      {
        headers: {
          ...mutationHeaders,
          'x-csrf-token': 'A'.repeat(43),
          'idempotency-key': 'progress_write_000004',
        },
        body: mutationBody,
      },
    ));
    assert.equal(badCsrf.status, 403);
    assert.deepEqual(badCsrf.body, { error: 'csrf_rejected' });

    const oversized = request(
      'PUT',
      '/api/saas/progress/refrigerator-v1/map',
      {
        headers: {
          ...mutationHeaders,
          'idempotency-key': 'progress_write_000005',
          'content-length': '20000',
        },
        body: mutationBody,
      },
    );
    oversized.request.headers['content-length'] = '20000';
    const tooLarge = await api.handle(oversized);
    assert.equal(tooLarge.status, 413);
    assert.deepEqual(tooLarge.body, { error: 'request_too_large' });

    const unboundSession = { ...session, tenant_id: 'unbound-tenant' };
    const missing = await api.handle({
      ...request('GET', '/api/saas/me'),
      session: unboundSession,
    });
    assert.equal(missing.status, 403);
    assert.deepEqual(missing.body, { error: 'saas_membership_required' });

    assert.throws(() => state.bindHostedTenant(owner.id, {
      organization_id: organization.id,
      hosted_tenant_id: 'replacement-tenant',
    }, now + 20), /immutable/);
  } finally {
    api.close();
    state.close();
    rmSync(root, { recursive: true, force: true });
  }
});
