import assert from 'node:assert/strict';
import test from 'node:test';
import {
  CATALOG_CONTRACT, TENANT_CONTRACT, PRODUCT, canonicalJson, sha256Hex,
  parseStrictJson, verifyCatalog, sealTenantConfig, verifyTenantConfig,
  signIdentityAssertion, exchangeIdentityAssertion, verifySession,
  catalogForSession, createControlPlaneServer, createMemoryAuthState,
} from '../principia_atlas/hosted/index.mjs';
import { validateNetworkBoundary } from '../principia_atlas/hosted/server.mjs';

const identitySecret = 'identity-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const sessionSecret = 'session-secret-0123456789-abcdefghijklmnopqrstuvwxyz';

function seal(unsigned, field) {
  return { ...unsigned, [field]: sha256Hex(canonicalJson(unsigned)) };
}

function catalog() {
  const boundaries = {
    authorities_separate: true,
    status_inheritance: 'prohibited',
    live_cross_repository_dependency: false,
    canonical_mutation: false,
  };
  const runtime = { host: '127.0.0.1', external_network_required: false, python: '>=3.10' };
  const entrypoints = {
    verify: 'launcher.py verify', run: 'launcher.py run', linux_macos: 'launch.sh',
    macos_double_click: 'launch.command', windows: 'launch.cmd',
  };
  const releases = {
    '0.1.0-alpha.1': {
      tag: 'principia-atlas-v0.1.0-alpha.1', channel: 'alpha', promotion_id: 'a'.repeat(64),
      release: { release_id: 'b'.repeat(64), bundle_id: 'c'.repeat(64), receipt_id: 'd'.repeat(64), route_id: 'distributed-information', archive: { name: 'principia-atlas-0.1.0-alpha.1.zip', sha256: 'e'.repeat(64), checksum_name: 'principia-atlas-0.1.0-alpha.1.zip.sha256' } },
      sources: { principia: { repository: 'Rhodan-lab/principle-to-system', commit: '1'.repeat(40) }, atlas: { repository: 'Rhodan-lab/Atlas', commit: '2'.repeat(40) } },
      compatibility: { release_contract: 'principia-atlas-release/0.1', route_id: 'distributed-information', entrypoints, runtime, boundaries },
    },
    '0.1.0-beta.1': {
      tag: 'principia-atlas-v0.1.0-beta.1', channel: 'beta', promotion_id: 'f'.repeat(64),
      release: { release_id: '1'.repeat(64), bundle_id: '2'.repeat(64), receipt_id: '3'.repeat(64), route_id: 'distributed-information', archive: { name: 'principia-atlas-0.1.0-beta.1.zip', sha256: '4'.repeat(64), checksum_name: 'principia-atlas-0.1.0-beta.1.zip.sha256' } },
      sources: { principia: { repository: 'Rhodan-lab/principle-to-system', commit: '3'.repeat(40) }, atlas: { repository: 'Rhodan-lab/Atlas', commit: '4'.repeat(40) } },
      compatibility: { release_contract: 'principia-atlas-release/0.1', route_id: 'distributed-information', entrypoints, runtime, boundaries },
    },
  };
  return seal({
    contract: CATALOG_CONTRACT, product: PRODUCT, release_count: 2, releases,
    channels: {
      alpha: { version: '0.1.0-alpha.1', tag: releases['0.1.0-alpha.1'].tag, promotion_id: releases['0.1.0-alpha.1'].promotion_id },
      beta: { version: '0.1.0-beta.1', tag: releases['0.1.0-beta.1'].tag, promotion_id: releases['0.1.0-beta.1'].promotion_id },
      stable: null,
    },
  }, 'catalog_id');
}

function config() {
  return sealTenantConfig({
    contract: TENANT_CONTRACT, product: PRODUCT,
    identity: { issuer: 'https://identity.example.test', audience: 'principia-atlas-hosted', max_assertion_ttl_seconds: 300 },
    session: { cookie_name: 'pa_session', ttl_seconds: 3600, secure: false },
    tenants: {
      'school-demo': { display_name: 'School Demo', allowed_channels: ['alpha'], allowed_routes: ['distributed-information'], pinned_versions: [] },
      'beta-lab': { display_name: 'Beta Lab', allowed_channels: ['beta'], allowed_routes: ['distributed-information'], pinned_versions: ['0.1.0-beta.1'] },
    },
  });
}

function claims(now = 1_800_000_000, tenant = 'school-demo') {
  return { iss: 'https://identity.example.test', aud: 'principia-atlas-hosted', sub: 'learner-1', tenant_id: tenant, roles: ['learner'], iat: now, exp: now + 180, jti: 'assertion_identifier_1234' };
}

test('strict JSON rejects duplicate keys and malformed UTF-8', () => {
  assert.throws(() => parseStrictJson('{"a":1,"a":2}', 'fixture'), /duplicate key/);
  assert.throws(() => parseStrictJson(Buffer.from([0xff]), 'fixture'), /valid UTF-8/);
});

test('catalog and tenant seals detect tamper', () => {
  const cat = verifyCatalog(catalog());
  assert.equal(cat.release_count, 2);
  const changed = structuredClone(cat);
  changed.release_count = 9;
  assert.throws(() => verifyCatalog(changed), /seal/);
  const tenants = verifyTenantConfig(config());
  tenants.session.ttl_seconds = 30;
  assert.throws(() => verifyTenantConfig(tenants), /seal/);
});

test('identity exchange creates tenant-bound short session', () => {
  const now = 1_800_000_000;
  const assertion = signIdentityAssertion(claims(now), identitySecret, config());
  const exchanged = exchangeIdentityAssertion(assertion, identitySecret, sessionSecret, config(), now + 1);
  const session = verifySession(exchanged.token, sessionSecret, config(), now + 2);
  assert.equal(session.tenant_id, 'school-demo');
  assert.equal(session.sub, 'learner-1');
  assert.equal(session.exp, now + 1 + 3600);
  assert.match(session.sid, /^[A-Za-z0-9_-]{24,128}$/);
  const tampered = `${exchanged.token.slice(0, -1)}x`;
  assert.throws(() => verifySession(tampered, sessionSecret, config(), now + 2), /signature/);
});

test('expired and unknown-tenant assertions are rejected', () => {
  const now = 1_800_000_000;
  const assertion = signIdentityAssertion(claims(now), identitySecret, config());
  assert.throws(() => exchangeIdentityAssertion(assertion, identitySecret, sessionSecret, config(), now + 181), /time boundary/);
  assert.throws(() => signIdentityAssertion(claims(now, 'other-tenant'), identitySecret, config()), /principal/);
});

test('catalog is filtered only by session tenant entitlements', () => {
  const view = catalogForSession({ sub: 'learner-1', tenant_id: 'school-demo', roles: ['learner'] }, catalog(), config());
  assert.deepEqual(view.releases.map((item) => item.version), ['0.1.0-alpha.1']);
  assert.equal(view.channels.alpha.version, '0.1.0-alpha.1');
  assert.equal(view.channels.beta, null);
  const beta = catalogForSession({ sub: 'tester', tenant_id: 'beta-lab', roles: ['learner'] }, catalog(), config());
  assert.deepEqual(beta.releases.map((item) => item.version), ['0.1.0-beta.1']);
});

test('server rejects an unavailable tenant version pin', () => {
  const unsigned = config();
  delete unsigned.config_id;
  unsigned.tenants['school-demo'].pinned_versions = ['0.1.0-alpha.9'];
  const invalid = sealTenantConfig(unsigned);
  assert.throws(() => createControlPlaneServer({ catalog: catalog(), config: invalid, identitySecret, sessionSecret }), /unavailable release/);
});

test('HTTP control plane exchanges assertion and returns tenant catalog', async () => {
  const now = 1_800_000_000;
  const server = createControlPlaneServer({ catalog: catalog(), config: config(), identitySecret, sessionSecret, now: () => now });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  try {
    const address = server.address();
    const base = `http://127.0.0.1:${address.port}`;
    const anonymous = await fetch(`${base}/api/catalog`);
    assert.equal(anonymous.status, 401);
    assert.equal(anonymous.headers.get('x-frame-options'), 'DENY');
    const assertion = signIdentityAssertion(claims(now), identitySecret, config());
    const exchange = await fetch(`${base}/api/auth/exchange`, { method: 'POST', headers: { Authorization: `Bearer ${assertion}`, Origin: base } });
    assert.equal(exchange.status, 200);
    const cookie = exchange.headers.get('set-cookie');
    assert.match(cookie, /HttpOnly/);
    assert.match(cookie, /SameSite=Lax/);
    const replay = await fetch(`${base}/api/auth/exchange`, { method: 'POST', headers: { Authorization: `Bearer ${assertion}`, Origin: base } });
    assert.equal(replay.status, 401);
    const authenticated = await fetch(`${base}/api/catalog`, { headers: { Cookie: cookie.split(';')[0] } });
    assert.equal(authenticated.status, 200);
    const body = await authenticated.json();
    assert.equal(body.tenant.id, 'school-demo');
    assert.deepEqual(body.releases.map((item) => item.version), ['0.1.0-alpha.1']);
    assert.equal(Object.hasOwn(body, 'tenants'), false);
    assert.equal(Object.hasOwn(body.releases[0], 'artifact_path'), false);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('exchange enforces same-origin and rate limit', async () => {
  const now = 1_800_000_000;
  const server = createControlPlaneServer({ catalog: catalog(), config: config(), identitySecret, sessionSecret, now: () => now, exchangeLimit: 1 });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  try {
    const address = server.address(); const base = `http://127.0.0.1:${address.port}`;
    const assertion = signIdentityAssertion(claims(now), identitySecret, config());
    const cross = await fetch(`${base}/api/auth/exchange`, { method: 'POST', headers: { Authorization: `Bearer ${assertion}`, Origin: 'https://evil.example' } });
    assert.equal(cross.status, 403);
    const first = await fetch(`${base}/api/auth/exchange`, { method: 'POST', headers: { Authorization: `Bearer ${assertion}`, Origin: base } });
    assert.equal(first.status, 200);
    const second = await fetch(`${base}/api/auth/exchange`, { method: 'POST', headers: { Authorization: `Bearer ${assertion}`, Origin: base } });
    assert.equal(second.status, 429);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('network boundary requires explicit opt-in, secure cookies, and durable state', () => {
  const secure = config(); secure.session.secure = true; delete secure.config_id;
  const sealed = sealTenantConfig(secure);
  const memory = createMemoryAuthState();
  assert.throws(() => validateNetworkBoundary({ host: '0.0.0.0', allowNetwork: false }, sealed, memory), /allow-network/);
  assert.throws(() => validateNetworkBoundary({ host: '0.0.0.0', allowNetwork: true }, config(), memory), /secure session/);
  assert.throws(() => validateNetworkBoundary({ host: '0.0.0.0', allowNetwork: true }, sealed, memory), /durable multi-instance/);
  assert.throws(() => validateNetworkBoundary({ host: '0.0.0.0', allowNetwork: true }, sealed), /auth state backend/);
  assert.doesNotThrow(() => validateNetworkBoundary({ host: '127.0.0.1', allowNetwork: false }, config()));
  memory.close();
});
