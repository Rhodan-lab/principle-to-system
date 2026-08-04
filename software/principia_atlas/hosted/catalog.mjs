import { canonicalJson, exactKeys, fail, parseStrictJson, sha256Hex } from './strict_json.mjs';

export const CATALOG_CONTRACT = 'principia-atlas-hosted-catalog/0.1';
export const TENANT_CONTRACT = 'principia-atlas-hosted-tenants/0.1';
export const PRODUCT = 'Principia & Atlas';
const SHA = /^[0-9a-f]{64}$/;
const VERSION = /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-(alpha|beta)\.(0|[1-9][0-9]*))?$/;
const TENANT_ID = /^[a-z][a-z0-9-]{1,62}$/;

function versionInfo(version) {
  const match = VERSION.exec(version);
  if (!match) fail('catalog version is invalid');
  return {
    major: Number(match[1]), minor: Number(match[2]), patch: Number(match[3]),
    rank: match[4] === 'alpha' ? 0 : match[4] === 'beta' ? 1 : 2,
    sequence: match[5] === undefined ? 0 : Number(match[5]),
    channel: match[4] ?? 'stable',
  };
}

function compareVersions(left, right) {
  const a = versionInfo(left); const b = versionInfo(right);
  for (const key of ['major', 'minor', 'patch', 'rank', 'sequence']) {
    if (a[key] !== b[key]) return a[key] - b[key];
  }
  return 0;
}

function validateArchive(value) {
  exactKeys(value, ['name', 'sha256', 'checksum_name'], 'catalog archive');
  if (typeof value.name !== 'string' || !value.name.endsWith('.zip') || /[\\/]/.test(value.name)) fail('catalog archive name is invalid');
  if (!SHA.test(value.sha256) || value.checksum_name !== `${value.name}.sha256`) fail('catalog archive identity is invalid');
}

function validateSource(value) {
  exactKeys(value, ['repository', 'commit'], 'catalog source');
  if (typeof value.repository !== 'string' || !/^[^/\s]+\/[^/\s]+$/.test(value.repository)) fail('catalog source repository is invalid');
  if (typeof value.commit !== 'string' || !/^(?:[0-9a-f]{40}|[0-9a-f]{64})$/.test(value.commit)) fail('catalog source commit is invalid');
}

export function verifyCatalog(input) {
  const value = typeof input === 'string' || Buffer.isBuffer(input) ? parseStrictJson(input, 'hosted catalog') : structuredClone(input);
  exactKeys(value, ['contract', 'product', 'release_count', 'releases', 'channels', 'catalog_id'], 'hosted catalog');
  if (value.contract !== CATALOG_CONTRACT || value.product !== PRODUCT) fail('hosted catalog contract is invalid');
  const unsigned = structuredClone(value); delete unsigned.catalog_id;
  if (!SHA.test(value.catalog_id) || sha256Hex(canonicalJson(unsigned)) !== value.catalog_id) fail('hosted catalog seal is invalid');
  if (!value.releases || typeof value.releases !== 'object' || Array.isArray(value.releases)) fail('hosted catalog releases are invalid');
  if (!value.channels || typeof value.channels !== 'object' || Array.isArray(value.channels)) fail('hosted catalog channels are invalid');
  if (value.release_count !== Object.keys(value.releases).length) fail('hosted catalog release counter is invalid');
  exactKeys(value.channels, ['alpha', 'beta', 'stable'], 'hosted catalog channels');
  const grouped = { alpha: [], beta: [], stable: [] };
  const tags = new Set(); const promotions = new Set();
  for (const [version, entry] of Object.entries(value.releases)) {
    const info = versionInfo(version);
    exactKeys(entry, ['tag', 'channel', 'promotion_id', 'release', 'sources', 'compatibility'], 'hosted catalog release');
    if (entry.channel !== info.channel || entry.tag !== `principia-atlas-v${version}` || !SHA.test(entry.promotion_id)) fail('hosted catalog release identity is invalid');
    if (tags.has(entry.tag) || promotions.has(entry.promotion_id)) fail('hosted catalog contains duplicate identities');
    tags.add(entry.tag); promotions.add(entry.promotion_id);
    exactKeys(entry.release, ['release_id', 'bundle_id', 'receipt_id', 'route_id', 'archive'], 'catalog release identity');
    for (const key of ['release_id', 'bundle_id', 'receipt_id']) if (!SHA.test(entry.release[key])) fail('catalog release digest is invalid');
    if (typeof entry.release.route_id !== 'string' || !entry.release.route_id) fail('catalog route is invalid');
    validateArchive(entry.release.archive);
    exactKeys(entry.sources, ['principia', 'atlas'], 'catalog sources');
    validateSource(entry.sources.principia); validateSource(entry.sources.atlas);
    exactKeys(entry.compatibility, ['release_contract', 'route_id', 'entrypoints', 'runtime', 'boundaries'], 'catalog compatibility');
    if (entry.compatibility.route_id !== entry.release.route_id) fail('catalog route identities are inconsistent');
    if (entry.compatibility.release_contract !== 'principia-atlas-release/0.1') fail('catalog release contract is unsupported');
    if (!entry.compatibility.runtime || entry.compatibility.runtime.host !== '127.0.0.1' || entry.compatibility.runtime.external_network_required !== false) fail('catalog runtime boundary is invalid');
    const boundary = entry.compatibility.boundaries;
    if (!boundary || boundary.authorities_separate !== true || boundary.status_inheritance !== 'prohibited' || boundary.live_cross_repository_dependency !== false || boundary.canonical_mutation !== false) fail('catalog authority boundary is invalid');
    grouped[entry.channel].push(version);
  }
  for (const channel of Object.keys(grouped)) {
    const versions = grouped[channel]; const pointer = value.channels[channel];
    if (versions.length === 0) {
      if (pointer !== null) fail('empty hosted channel has a pointer');
      continue;
    }
    const latest = versions.sort(compareVersions).at(-1);
    const entry = value.releases[latest];
    exactKeys(pointer, ['version', 'tag', 'promotion_id'], 'hosted channel pointer');
    if (pointer.version !== latest || pointer.tag !== entry.tag || pointer.promotion_id !== entry.promotion_id) fail('hosted channel pointer is stale');
  }
  return value;
}

export function sealTenantConfig(unsigned) {
  const value = structuredClone(unsigned);
  value.config_id = sha256Hex(canonicalJson(unsigned));
  return value;
}

export function verifyTenantConfig(input) {
  const value = typeof input === 'string' || Buffer.isBuffer(input) ? parseStrictJson(input, 'tenant config') : structuredClone(input);
  exactKeys(value, ['contract', 'product', 'identity', 'session', 'tenants', 'config_id'], 'tenant config');
  if (value.contract !== TENANT_CONTRACT || value.product !== PRODUCT) fail('tenant config contract is invalid');
  const unsigned = structuredClone(value); delete unsigned.config_id;
  if (!SHA.test(value.config_id) || sha256Hex(canonicalJson(unsigned)) !== value.config_id) fail('tenant config seal is invalid');
  exactKeys(value.identity, ['issuer', 'audience', 'max_assertion_ttl_seconds'], 'identity config');
  if (typeof value.identity.issuer !== 'string' || !value.identity.issuer || typeof value.identity.audience !== 'string' || !value.identity.audience) fail('identity config is invalid');
  if (!Number.isInteger(value.identity.max_assertion_ttl_seconds) || value.identity.max_assertion_ttl_seconds < 30 || value.identity.max_assertion_ttl_seconds > 900) fail('identity assertion TTL is invalid');
  exactKeys(value.session, ['cookie_name', 'ttl_seconds', 'secure'], 'session config');
  if (typeof value.session.cookie_name !== 'string' || !/^[A-Za-z_][A-Za-z0-9_]{0,63}$/.test(value.session.cookie_name)) fail('session cookie name is invalid');
  if (!Number.isInteger(value.session.ttl_seconds) || value.session.ttl_seconds < 60 || value.session.ttl_seconds > 28800 || typeof value.session.secure !== 'boolean') fail('session config is invalid');
  if (!value.tenants || typeof value.tenants !== 'object' || Array.isArray(value.tenants) || Object.keys(value.tenants).length === 0) fail('tenant config must contain tenants');
  for (const [tenantId, tenant] of Object.entries(value.tenants)) {
    if (!TENANT_ID.test(tenantId)) fail('tenant identifier is invalid');
    exactKeys(tenant, ['display_name', 'allowed_channels', 'allowed_routes', 'pinned_versions'], 'tenant');
    if (typeof tenant.display_name !== 'string' || tenant.display_name.length < 1 || tenant.display_name.length > 100) fail('tenant display name is invalid');
    if (!Array.isArray(tenant.allowed_channels) || tenant.allowed_channels.length === 0 || tenant.allowed_channels.some((item) => !['alpha', 'beta', 'stable'].includes(item)) || new Set(tenant.allowed_channels).size !== tenant.allowed_channels.length) fail('tenant allowed channels are invalid');
    if (!Array.isArray(tenant.allowed_routes) || tenant.allowed_routes.length === 0 || tenant.allowed_routes.some((item) => typeof item !== 'string' || !/^[a-z][a-z0-9-]{1,100}$/.test(item)) || new Set(tenant.allowed_routes).size !== tenant.allowed_routes.length) fail('tenant allowed routes are invalid');
    if (!Array.isArray(tenant.pinned_versions) || tenant.pinned_versions.some((item) => typeof item !== 'string' || !VERSION.test(item)) || new Set(tenant.pinned_versions).size !== tenant.pinned_versions.length) fail('tenant pinned versions are invalid');
  }
  return value;
}

export function catalogForSession(session, catalogInput, configInput) {
  const catalog = verifyCatalog(catalogInput); const config = verifyTenantConfig(configInput);
  const tenant = config.tenants[session.tenant_id];
  if (!tenant) fail('session tenant is unavailable');
  const pinned = new Set(tenant.pinned_versions);
  const releases = [];
  for (const [version, entry] of Object.entries(catalog.releases)) {
    if (!tenant.allowed_channels.includes(entry.channel) || !tenant.allowed_routes.includes(entry.release.route_id) || (pinned.size > 0 && !pinned.has(version))) continue;
    releases.push({
      version, tag: entry.tag, channel: entry.channel, route_id: entry.release.route_id,
      release_id: entry.release.release_id, archive: structuredClone(entry.release.archive),
    });
  }
  releases.sort((a, b) => compareVersions(b.version, a.version));
  const channels = {};
  for (const channel of ['alpha', 'beta', 'stable']) channels[channel] = releases.find((item) => item.channel === channel) ?? null;
  return { contract: 'principia-atlas-hosted-view/0.1', product: PRODUCT, tenant: { id: session.tenant_id, display_name: tenant.display_name }, subject: session.sub, roles: [...session.roles], releases, channels };
}
