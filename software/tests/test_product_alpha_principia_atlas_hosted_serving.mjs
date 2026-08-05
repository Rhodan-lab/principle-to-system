import assert from 'node:assert/strict';
import { mkdtemp, mkdir, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import test from 'node:test';
import {
  CATALOG_CONTRACT, TENANT_CONTRACT, PRODUCT, canonicalJson, sha256Hex,
  sealTenantConfig, signIdentityAssertion, createControlPlaneServer,
  loadHostedStore, STORE_CONTRACT, STORE_MANIFEST,
} from '../principia_atlas/hosted/index.mjs';

const identitySecret = 'identity-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const sessionSecret = 'session-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const version = '0.1.0-alpha.1';
const archiveSha = 'e'.repeat(64);

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
  const release = {
    tag: `principia-atlas-v${version}`, channel: 'alpha', promotion_id: 'a'.repeat(64),
    release: {
      release_id: 'b'.repeat(64), bundle_id: 'c'.repeat(64), receipt_id: 'd'.repeat(64),
      route_id: 'distributed-information',
      archive: { name: `principia-atlas-${version}.zip`, sha256: archiveSha, checksum_name: `principia-atlas-${version}.zip.sha256` },
    },
    sources: {
      principia: { repository: 'Rhodan-lab/principle-to-system', commit: '1'.repeat(40) },
      atlas: { repository: 'Rhodan-lab/Atlas', commit: '2'.repeat(40) },
    },
    compatibility: { release_contract: 'principia-atlas-release/0.1', route_id: 'distributed-information', entrypoints, runtime, boundaries },
  };
  return seal({
    contract: CATALOG_CONTRACT, product: PRODUCT, release_count: 1,
    releases: { [version]: release },
    channels: { alpha: { version, tag: release.tag, promotion_id: release.promotion_id }, beta: null, stable: null },
  }, 'catalog_id');
}

function config() {
  return sealTenantConfig({
    contract: TENANT_CONTRACT, product: PRODUCT,
    identity: { issuer: 'https://identity.example.test', audience: 'principia-atlas-hosted', max_assertion_ttl_seconds: 300 },
    session: { cookie_name: 'pa_session', ttl_seconds: 3600, secure: false },
    tenants: {
      'alpha-school': { display_name: '<Alpha School>', allowed_channels: ['alpha'], allowed_routes: ['distributed-information'], pinned_versions: [] },
      'beta-school': { display_name: 'Beta School', allowed_channels: ['beta'], allowed_routes: ['distributed-information'], pinned_versions: [] },
    },
  });
}

function claims(now, tenant = 'alpha-school', jti = 'assertion_identifier_1234') {
  return { iss: 'https://identity.example.test', aud: 'principia-atlas-hosted', sub: 'learner-1', tenant_id: tenant, roles: ['learner'], iat: now, exp: now + 180, jti };
}

async function makeStore() {
  const root = await mkdtemp(join(tmpdir(), 'principia-atlas-store-'));
  const objectRoot = `objects/${archiveSha}/product`;
  const files = {
    'index.html': Buffer.from('<h1>home</h1>\n'),
    'principia/index.html': Buffer.from('<h1>learn</h1>\n'),
    'principia/app.js': Buffer.from("console.log('learn')\n"),
    'atlas/index.html': Buffer.from('<h1>research</h1>\n'),
  };
  const inventory = {};
  for (const [path, raw] of Object.entries(files)) {
    const destination = join(root, ...objectRoot.split('/'), ...path.split('/'));
    await mkdir(dirname(destination), { recursive: true });
    await writeFile(destination, raw);
    inventory[path] = { sha256: sha256Hex(raw), size: raw.length };
  }
  const unsigned = {
    contract: STORE_CONTRACT, product: PRODUCT, catalog_id: catalog().catalog_id, release_count: 1,
    releases: {
      [version]: {
        release_id: 'b'.repeat(64), bundle_id: 'c'.repeat(64), receipt_id: 'd'.repeat(64),
        route_id: 'distributed-information', archive_sha256: archiveSha, object_root: objectRoot,
        entrypoint: 'index.html', file_count: Object.keys(files).length,
        total_bytes: Object.values(files).reduce((sum, raw) => sum + raw.length, 0), files: inventory,
      },
    },
    boundaries: {
      archive_parsing_in_web_runtime: false,
      archives_verified_before_materialization: true,
      content_addressed: true,
      read_only_runtime: true,
      symlinks: false,
      tenant_authorization_required: true,
    },
  };
  const manifest = seal(unsigned, 'store_id');
  await writeFile(join(root, STORE_MANIFEST), canonicalJson(manifest));
  return { root, objectRoot, files, manifest };
}

async function authenticate(base, now, tenant = 'alpha-school', jti = 'assertion_identifier_1234') {
  const assertion = signIdentityAssertion(claims(now, tenant, jti), identitySecret, config());
  const response = await fetch(`${base}/api/auth/exchange`, {
    method: 'POST', headers: { Authorization: `Bearer ${assertion}`, Origin: base },
  });
  assert.equal(response.status, 200);
  return response.headers.get('set-cookie').split(';')[0];
}

async function withServer(run) {
  const now = 1_800_000_000;
  const fixture = await makeStore();
  const store = await loadHostedStore(fixture.root, catalog());
  const server = createControlPlaneServer({ catalog: catalog(), config: config(), store, identitySecret, sessionSecret, now: () => now });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  try {
    const address = server.address();
    await run({ base: `http://127.0.0.1:${address.port}`, now, fixture, store });
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
}

test('verified store serves only entitled immutable release assets', async () => {
  await withServer(async ({ base, now }) => {
    const cookie = await authenticate(base, now);
    const home = await fetch(`${base}/app/${version}/`, { headers: { Cookie: cookie } });
    assert.equal(home.status, 200);
    assert.equal(await home.text(), '<h1>home</h1>\n');
    assert.equal(home.headers.get('content-type'), 'text/html; charset=utf-8');
    assert.match(home.headers.get('etag'), /^"sha256-[0-9a-f]{64}"$/);
    const nested = await fetch(`${base}/app/${version}/principia/`, { headers: { Cookie: cookie } });
    assert.equal(await nested.text(), '<h1>learn</h1>\n');
    const head = await fetch(`${base}/app/${version}/principia/app.js`, { method: 'HEAD', headers: { Cookie: cookie } });
    assert.equal(head.status, 200);
    assert.equal(await head.text(), '');
    const view = await fetch(`${base}/api/catalog`, { headers: { Cookie: cookie } });
    const body = await view.json();
    assert.equal(body.releases[0].launch_path, `/app/${version}/`);
  });
});

test('anonymous and non-entitled tenants cannot discover release bytes', async () => {
  await withServer(async ({ base, now }) => {
    assert.equal((await fetch(`${base}/app/${version}/`)).status, 401);
    const betaCookie = await authenticate(base, now, 'beta-school', 'assertion_identifier_beta');
    const denied = await fetch(`${base}/app/${version}/`, { headers: { Cookie: betaCookie } });
    assert.equal(denied.status, 404);
    assert.deepEqual(await denied.json(), { error: 'not_found' });
  });
});

test('asset route rejects traversal, encoded separators, and mutation methods', async () => {
  await withServer(async ({ base, now }) => {
    const cookie = await authenticate(base, now);
    for (const path of [
      `/app/${version}/%2e%2e/index.html`,
      `/app/${version}/principia%2findex.html`,
      `/app/${version}/principia%5cindex.html`,
    ]) assert.equal((await fetch(`${base}${path}`, { headers: { Cookie: cookie } })).status, 400);
    assert.equal((await fetch(`${base}/app/${version}/missing.txt`, { headers: { Cookie: cookie } })).status, 404);
    const post = await fetch(`${base}/app/${version}/`, { method: 'POST', headers: { Cookie: cookie } });
    assert.equal(post.status, 405);
    assert.equal(post.headers.get('allow'), 'GET, HEAD');
  });
});

test('store loader rejects tamper, extra files, symlinks, and catalog drift', async () => {
  const tampered = await makeStore();
  await writeFile(join(tampered.root, ...tampered.objectRoot.split('/'), 'index.html'), 'changed\n');
  await assert.rejects(() => loadHostedStore(tampered.root, catalog()), /digest|metadata/);

  const extra = await makeStore();
  await writeFile(join(extra.root, 'extra.txt'), 'extra\n');
  await assert.rejects(() => loadHostedStore(extra.root, catalog()), /file set/);

  const linked = await makeStore();
  const target = join(linked.root, ...linked.objectRoot.split('/'), 'index.html');
  try {
    await symlink(target, join(linked.root, 'linked.html'));
    await assert.rejects(() => loadHostedStore(linked.root, catalog()), /symlink/);
  } catch (error) {
    if (error?.code !== 'EPERM') throw error;
  }

  const drift = await makeStore();
  const changedCatalog = structuredClone(catalog());
  changedCatalog.catalog_id = 'f'.repeat(64);
  await assert.rejects(() => loadHostedStore(drift.root, changedCatalog), /seal|catalog/);
});

test('served bytes are memory-resident after verified startup', async () => {
  await withServer(async ({ base, now, fixture }) => {
    const cookie = await authenticate(base, now);
    await writeFile(join(fixture.root, ...fixture.objectRoot.split('/'), 'index.html'), 'changed after startup\n');
    const response = await fetch(`${base}/app/${version}/`, { headers: { Cookie: cookie } });
    assert.equal(await response.text(), '<h1>home</h1>\n');
  });
});

test('hosted shell uses DOM text APIs and health reports release serving', async () => {
  await withServer(async ({ base }) => {
    const shell = await fetch(`${base}/`);
    const html = await shell.text();
    assert.equal(html.includes('innerHTML'), false);
    assert.equal(html.includes('textContent'), true);
    const health = await fetch(`${base}/healthz`);
    assert.deepEqual(await health.json(), {
      status: 'ok',
      contract: 'principia-atlas-hosted-health/0.4',
      release_serving: true,
      auth_state: {
        contract: 'principia-atlas-hosted-auth-state/0.1',
        kind: 'memory',
        durable: false,
        multi_instance: false,
      },
      oidc: { enabled: false },
    });
  });
});
