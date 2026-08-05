import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { main as runSaasCli } from '../principia_atlas/saas/cli.mjs';
import { openSaasControlPlane } from '../principia_atlas/saas/store.mjs';

const root = mkdtempSync(join(tmpdir(), 'principia-atlas-saas-'));
const statePath = join(root, 'state', 'saas.sqlite');
const now = 1_800_000_000;
const org = {
  id: 'org_01PUBLICSAASFOUNDATION',
  slug: 'principia-lab',
  display_name: 'Principia Lab',
};
const owner = {
  id: 'mem_01PUBLICSAASOWNER000',
  organization_id: org.id,
  subject_id: `oidc:${'A'.repeat(43)}`,
  role: 'owner',
};
const learner = {
  id: 'mem_01PUBLICSAASLEARNER0',
  organization_id: org.id,
  subject_id: `oidc:${'B'.repeat(43)}`,
  role: 'learner',
};
const releaseId = 'principia-atlas-release:0.2.0-beta.1';

try {
  let state = openSaasControlPlane(statePath);
  const bootstrapped = state.bootstrapOrganization(org, owner, now);
  assert.equal(bootstrapped.membership.role, 'owner');
  assert.equal(JSON.stringify(bootstrapped).includes(owner.subject_id), false);

  const added = state.addMembership(owner.id, learner, now + 1);
  assert.equal(added.role, 'learner');
  assert.equal(JSON.stringify(added).includes(learner.subject_id), false);

  assert.throws(
    () => state.grantEntitlement(learner.id, {
      organization_id: org.id,
      route_id: 'refrigerator-v1',
      release_id: releaseId,
      starts_at: now,
      ends_at: null,
    }, now + 2),
    /not authorized/,
  );

  state.grantEntitlement(owner.id, {
    organization_id: org.id,
    route_id: 'refrigerator-v1',
    release_id: releaseId,
    starts_at: now,
    ends_at: null,
  }, now + 2);

  const first = state.recordProgress(learner.id, {
    organization_id: org.id,
    member_id: learner.id,
    route_id: 'refrigerator-v1',
    release_id: releaseId,
    stage: 'observe',
    status: 'completed',
    expected_revision: 0,
  }, now + 3);
  assert.equal(first.revision, 1);

  assert.throws(
    () => state.recordProgress(learner.id, {
      organization_id: org.id,
      member_id: learner.id,
      route_id: 'refrigerator-v1',
      release_id: releaseId,
      stage: 'observe',
      status: 'completed',
      expected_revision: 0,
    }, now + 4),
    /revision conflict/,
  );

  assert.throws(
    () => state.recordProgress(learner.id, {
      organization_id: org.id,
      member_id: owner.id,
      route_id: 'refrigerator-v1',
      release_id: releaseId,
      stage: 'map',
      status: 'in_progress',
      expected_revision: 0,
    }, now + 4),
    /only update their own/,
  );

  assert.throws(
    () => state.recordProgress(learner.id, {
      organization_id: org.id,
      member_id: learner.id,
      route_id: 'distributed-information-v1',
      release_id: releaseId,
      stage: 'observe',
      status: 'in_progress',
      expected_revision: 0,
    }, now + 4),
    /not entitled/,
  );

  let dashboard = state.dashboard(learner.id, now + 5);
  assert.equal(dashboard.contract, 'principia-atlas-saas-dashboard/0.1');
  assert.equal(dashboard.entitlements.length, 1);
  assert.equal(dashboard.progress.length, 1);
  assert.equal(JSON.stringify(dashboard).includes('subject_id'), false);
  assert.equal(JSON.stringify(dashboard).includes(learner.subject_id), false);
  assert.equal(state.health().production_ready, false);
  state.close();

  state = openSaasControlPlane(statePath);
  dashboard = state.dashboard(learner.id, now + 6);
  assert.equal(dashboard.progress[0].revision, 1);
  assert.equal(dashboard.organization.slug, 'principia-lab');
  state.close();

  const cliState = join(root, 'state', 'cli.sqlite');
  let cliOutput = '';
  runSaasCli(
    ['bootstrap', '--state', cliState, '--now', String(now)],
    () => Buffer.from(JSON.stringify({ organization: org, owner })),
    (value) => { cliOutput += value; },
  );
  assert.equal(cliOutput.includes(owner.subject_id), false);
  cliOutput = '';
  runSaasCli(
    ['health', '--state', cliState, '--now', String(now + 1)],
    () => Buffer.alloc(0),
    (value) => { cliOutput += value; },
  );
  assert.match(cliOutput, /sqlite-reference/);

  console.log('Principia Atlas SaaS control-plane kernel tests passed');
} finally {
  rmSync(root, { recursive: true, force: true });
}
