import assert from 'node:assert/strict';
import { mkdtempSync, symlinkSync } from 'node:fs';
import { rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import test from 'node:test';
import { main as authStateCommand } from '../principia_atlas/hosted/auth_state_cli.mjs';
import {
  AUTH_STATE_CONTRACT,
  CATALOG_CONTRACT,
  PRODUCT,
  TENANT_CONTRACT,
  canonicalJson,
  canonicalOidcSubject,
  createControlPlaneServer,
  exchangeIdentityAssertion,
  openSqliteAuthState,
  sealTenantConfig,
  sha256Hex,
  signIdentityAssertion,
} from '../principia_atlas/hosted/index.mjs';

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
    verify: 'launcher.py verify',
    run: 'launcher.py run',
    linux_macos: 'launch.sh',
    macos_double_click: 'launch.command',
    windows: 'launch.cmd',
  };
  const release = {
    tag: 'principia-atlas-v0.1.0-alpha.1',
    channel: 'alpha',
    promotion_id: 'a'.repeat(64),
    release: {
      release_id: 'b'.repeat(64),
      bundle_id: 'c'.repeat(64),
      receipt_id: 'd'.repeat(64),
      route_id: 'distributed-information',
      archive: {
        name: 'principia-atlas-0.1.0-alpha.1.zip',
        sha256: 'e'.repeat(64),
        checksum_name: 'principia-atlas-0.1.0-alpha.1.zip.sha256',
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
    releases: { '0.1.0-alpha.1': release },
    channels: {
      alpha: { version: '0.1.0-alpha.1', tag: release.tag, promotion_id: release.promotion_id },
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

function claims(now, jti, subject = 'learner-1') {
  return {
    iss: 'https://identity.example.test',
    aud: 'principia-atlas-hosted',
    sub: subject,
    tenant_id: 'school-demo',
    roles: ['learner'],
    iat: now,
    exp: now + 180,
    jti,
  };
}

async function listen(server) {
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const address = server.address();
  return `http://127.0.0.1:${address.port}`;
}

async function close(server) {
  await new Promise((resolve) => server.close(resolve));
}

function temporaryState() {
  const directory = mkdtempSync(join(tmpdir(), 'principia-atlas-auth-state-'));
  return { directory, path: join(directory, 'auth-state.sqlite') };
}

test('SQLite state persists assertion claims and registered sessions', async () => {
  const fixture = temporaryState();
  try {
    const now = 1_800_000_000;
    const assertionToken = signIdentityAssertion(claims(now, 'persistent_assertion_0001'), identitySecret, config());
    const exchanged = exchangeIdentityAssertion(assertionToken, identitySecret, sessionSecret, config(), now, () => 'persistent_session_identifier_0001');
    const stateA = openSqliteAuthState(fixture.path);
    const stateB = openSqliteAuthState(fixture.path);
    assert.equal(stateA.commitExchange({ assertionId: exchanged.assertion.jti, assertionExpiresAt: exchanged.assertion.exp, session: exchanged.session }, now), true);
    assert.equal(stateB.validateSession(exchanged.session, now + 1), true);
    const replay = exchangeIdentityAssertion(assertionToken, identitySecret, sessionSecret, config(), now + 1, () => 'persistent_session_identifier_0002');
    assert.equal(stateB.commitExchange({ assertionId: replay.assertion.jti, assertionExpiresAt: replay.assertion.exp, session: replay.session }, now + 1), false);
    stateA.close();
    stateB.close();
    const reopened = openSqliteAuthState(fixture.path);
    assert.equal(reopened.validateSession(exchanged.session, now + 2), true);
    assert.equal(reopened.health().contract, AUTH_STATE_CONTRACT);
    reopened.close();
  } finally {
    await rm(fixture.directory, { recursive: true, force: true });
  }
});

test('two control-plane instances share replay protection and logout revocation', async () => {
  const fixture = temporaryState();
  const stateA = openSqliteAuthState(fixture.path);
  const stateB = openSqliteAuthState(fixture.path);
  const now = 1_800_000_000;
  const serverA = createControlPlaneServer({ catalog: catalog(), config: config(), authState: stateA, identitySecret, sessionSecret, now: () => now });
  const serverB = createControlPlaneServer({ catalog: catalog(), config: config(), authState: stateB, identitySecret, sessionSecret, now: () => now });
  try {
    const baseA = await listen(serverA);
    const baseB = await listen(serverB);
    const assertion = signIdentityAssertion(claims(now, 'shared_assertion_identifier_0001'), identitySecret, config());
    const first = await fetch(`${baseA}/api/auth/exchange`, { method: 'POST', headers: { Authorization: `Bearer ${assertion}`, Origin: baseA } });
    assert.equal(first.status, 200);
    const cookie = first.headers.get('set-cookie').split(';')[0];
    const replay = await fetch(`${baseB}/api/auth/exchange`, { method: 'POST', headers: { Authorization: `Bearer ${assertion}`, Origin: baseB } });
    assert.equal(replay.status, 401);
    const crossInstanceSession = await fetch(`${baseB}/api/session`, { headers: { Cookie: cookie } });
    assert.equal(crossInstanceSession.status, 200);
    const ready = await fetch(`${baseB}/readyz`);
    assert.equal(ready.status, 200);
    const readyBody = await ready.json();
    assert.equal(readyBody.auth_state.kind, 'sqlite');
    assert.equal(readyBody.auth_state.multi_instance, true);
    const logout = await fetch(`${baseB}/api/logout`, { method: 'POST', headers: { Cookie: cookie, Origin: baseB } });
    assert.equal(logout.status, 200);
    const revokedOnOtherInstance = await fetch(`${baseA}/api/session`, { headers: { Cookie: cookie } });
    assert.equal(revokedOnOtherInstance.status, 401);
  } finally {
    await close(serverA);
    await close(serverB);
    stateA.close();
    stateB.close();
    await rm(fixture.directory, { recursive: true, force: true });
  }
});

test('exchange rate limits are shared across instances', async () => {
  const fixture = temporaryState();
  const stateA = openSqliteAuthState(fixture.path);
  const stateB = openSqliteAuthState(fixture.path);
  const now = 1_800_000_000;
  const serverA = createControlPlaneServer({ catalog: catalog(), config: config(), authState: stateA, identitySecret, sessionSecret, now: () => now, exchangeLimit: 1 });
  const serverB = createControlPlaneServer({ catalog: catalog(), config: config(), authState: stateB, identitySecret, sessionSecret, now: () => now, exchangeLimit: 1 });
  try {
    const baseA = await listen(serverA);
    const baseB = await listen(serverB);
    const firstAssertion = signIdentityAssertion(claims(now, 'rate_limit_assertion_0001'), identitySecret, config());
    const secondAssertion = signIdentityAssertion(claims(now, 'rate_limit_assertion_0002'), identitySecret, config());
    const first = await fetch(`${baseA}/api/auth/exchange`, { method: 'POST', headers: { Authorization: `Bearer ${firstAssertion}`, Origin: baseA } });
    assert.equal(first.status, 200);
    const second = await fetch(`${baseB}/api/auth/exchange`, { method: 'POST', headers: { Authorization: `Bearer ${secondAssertion}`, Origin: baseB } });
    assert.equal(second.status, 429);
    assert.ok(Number(second.headers.get('retry-after')) > 0);
  } finally {
    await close(serverA);
    await close(serverB);
    stateA.close();
    stateB.close();
    await rm(fixture.directory, { recursive: true, force: true });
  }
});

test('operator revocation invalidates every active subject session', async () => {
  const fixture = temporaryState();
  try {
    const state = openSqliteAuthState(fixture.path);
    const now = 1_800_000_000;
    const sessions = [];
    for (const [index, subject] of ['learner-1', 'learner-1', 'learner-2'].entries()) {
      const assertion = signIdentityAssertion(claims(now, `operator_assertion_000${index + 1}`, subject), identitySecret, config());
      const exchanged = exchangeIdentityAssertion(assertion, identitySecret, sessionSecret, config(), now, () => `operator_session_identifier_000${index + 1}`);
      assert.equal(state.commitExchange({ assertionId: exchanged.assertion.jti, assertionExpiresAt: exchanged.assertion.exp, session: exchanged.session }, now), true);
      sessions.push(exchanged.session);
    }
    assert.equal(state.revokeSubject('school-demo', 'learner-1', now + 1), 2);
    assert.equal(state.validateSession(sessions[0], now + 2), false);
    assert.equal(state.validateSession(sessions[1], now + 2), false);
    assert.equal(state.validateSession(sessions[2], now + 2), true);
    const stats = state.stats(now + 2);
    assert.equal(stats.active_sessions, 1);
    assert.equal(stats.revoked_sessions, 2);
    state.prune(now + 4000);
    assert.equal(state.stats(now + 4000).active_sessions, 0);
    state.close();
  } finally {
    await rm(fixture.directory, { recursive: true, force: true });
  }
});

test('operator CLI revokes an external OIDC subject without exposing canonical identity', async () => {
  const fixture = temporaryState();
  try {
    const state = openSqliteAuthState(fixture.path);
    const now = 1_800_000_000;
    const issuer = 'https://identity.external.test';
    const externalSubject = 'external-learner';
    const canonicalSubject = canonicalOidcSubject(issuer, externalSubject);
    const otherSubject = canonicalOidcSubject(issuer, 'other-learner');
    assert.match(canonicalSubject, /^oidc:[A-Za-z0-9_-]{43}$/);
    assert.notEqual(canonicalSubject, canonicalOidcSubject('https://other-identity.external.test', externalSubject));
    assert.throws(() => canonicalOidcSubject('http://identity.external.test', externalSubject), /HTTPS/);
    assert.throws(() => canonicalOidcSubject(issuer, 'bad\u0000subject'), /subject claim/);

    const sessions = [];
    for (const [index, subject] of [canonicalSubject, canonicalSubject, otherSubject].entries()) {
      const assertion = signIdentityAssertion(claims(now, `external_operator_assertion_000${index + 1}`, subject), identitySecret, config());
      const exchanged = exchangeIdentityAssertion(assertion, identitySecret, sessionSecret, config(), now, () => `external_operator_session_000${index + 1}`);
      assert.equal(state.commitExchange({ assertionId: exchanged.assertion.jti, assertionExpiresAt: exchanged.assertion.exp, session: exchanged.session }, now), true);
      sessions.push(exchanged.session);
    }

    let output = '';
    const result = authStateCommand([
      'revoke-oidc-subject',
      '--state', fixture.path,
      '--tenant', 'school-demo',
      '--issuer', issuer,
      '--external-subject', externalSubject,
      '--event-id', 'external-operator-disable-event-0001',
      '--receipt-ttl-seconds', '3600',
      '--now', String(now + 1),
    ], (value) => { output += value; });
    assert.equal(result.contract, 'principia-atlas-hosted-auth-state-command/0.1');
    assert.equal(result.command, 'revoke-oidc-subject');
    assert.equal(result.event_id, 'external-operator-disable-event-0001');
    assert.equal(result.replayed, false);
    assert.equal(result.revoked_sessions, 2);
    assert.equal(result.created_at, now + 1);
    assert.equal(result.expires_at, now + 3601);
    assert.equal(output.includes(externalSubject), false);
    assert.equal(output.includes(canonicalSubject), false);
    assert.equal(state.validateSession(sessions[0], now + 2), false);
    assert.equal(state.validateSession(sessions[1], now + 2), false);
    assert.equal(state.validateSession(sessions[2], now + 2), true);
    state.close();
  } finally {
    await rm(fixture.directory, { recursive: true, force: true });
  }
});

test('SQLite schema and symlink boundaries fail closed', async () => {
  const fixture = temporaryState();
  const linkDirectory = mkdtempSync(join(tmpdir(), 'principia-atlas-auth-link-'));
  try {
    const state = openSqliteAuthState(fixture.path);
    state.close();
    const database = new DatabaseSync(fixture.path);
    database.prepare('UPDATE state_metadata SET value = ? WHERE key = ?').run('unsupported-contract/9.9', 'contract');
    database.close();
    assert.throws(() => openSqliteAuthState(fixture.path), /schema contract/);
    const target = join(linkDirectory, 'target.sqlite');
    const targetState = openSqliteAuthState(target);
    targetState.close();
    const link = join(linkDirectory, 'linked.sqlite');
    symlinkSync(target, link);
    assert.throws(() => openSqliteAuthState(link), /regular file/);
  } finally {
    await rm(fixture.directory, { recursive: true, force: true });
    await rm(linkDirectory, { recursive: true, force: true });
  }
});
