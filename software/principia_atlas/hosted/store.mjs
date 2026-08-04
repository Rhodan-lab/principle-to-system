import { constants } from 'node:fs';
import { lstat, open, readdir, realpath } from 'node:fs/promises';
import { extname, join, relative, resolve, sep } from 'node:path';
import { verifyCatalog } from './catalog.mjs';
import { canonicalJson, exactKeys, fail, parseStrictJson, sha256Hex } from './strict_json.mjs';

export const STORE_CONTRACT = 'principia-atlas-hosted-store/0.1';
export const STORE_MANIFEST = 'HOSTED-STORE-MANIFEST.json';
const PRODUCT = 'Principia & Atlas';
const SHA = /^[0-9a-f]{64}$/;
const VERSION = /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-(alpha|beta)\.(0|[1-9][0-9]*))?$/;
const MAX_MANIFEST_BYTES = 8 * 1024 * 1024;
const MAX_FILE_BYTES = 64 * 1024 * 1024;
const MAX_TOTAL_BYTES = 512 * 1024 * 1024;
const MAX_FILES = 4096;
const BOUNDARIES = {
  archive_parsing_in_web_runtime: false,
  archives_verified_before_materialization: true,
  content_addressed: true,
  read_only_runtime: true,
  symlinks: false,
  tenant_authorization_required: true,
};

function safeRelative(value, label = 'hosted asset') {
  if (typeof value !== 'string' || value.length === 0 || value.startsWith('/') || value.includes('\\') || value.includes('\0')) fail(`${label} path is unsafe`);
  const parts = value.split('/');
  if (parts.some((part) => part.length === 0 || part === '.' || part === '..' || /[\u0000-\u001f\u007f]/.test(part))) fail(`${label} path is unsafe`);
  return value;
}

async function readBoundedRegular(path, limit, label) {
  const flags = constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0);
  let handle;
  try { handle = await open(path, flags); }
  catch { fail(`${label} must be a regular file`); }
  try {
    const before = await handle.stat();
    if (!before.isFile() || before.size > limit) fail(`${label} must be a bounded regular file`);
    const raw = await handle.readFile();
    const after = await handle.stat();
    if (!after.isFile() || after.size !== before.size || after.mtimeMs !== before.mtimeMs || raw.length !== before.size) fail(`${label} changed while reading`);
    return raw;
  } finally {
    await handle.close();
  }
}

function exactBoundary(value) {
  exactKeys(value, Object.keys(BOUNDARIES), 'hosted store boundaries');
  for (const [key, expected] of Object.entries(BOUNDARIES)) if (value[key] !== expected) fail('hosted store boundaries are invalid');
}

async function collectEntries(root) {
  const output = [];
  async function walk(directory) {
    const names = (await readdir(directory)).sort();
    for (const name of names) {
      const path = join(directory, name);
      const stats = await lstat(path);
      const item = relative(root, path).split(sep).join('/');
      if (stats.isSymbolicLink()) fail(`hosted store contains a symlink: ${item}`);
      if (stats.isDirectory()) await walk(path);
      else if (stats.isFile()) output.push(item);
      else fail(`hosted store contains a non-regular entry: ${item}`);
    }
  }
  await walk(root);
  return output;
}

async function readVerifiedFile(root, relativePath, metadata) {
  safeRelative(relativePath);
  const absolute = resolve(root, ...relativePath.split('/'));
  const rootReal = await realpath(root);
  const parentReal = await realpath(resolve(absolute, '..'));
  if (parentReal !== rootReal && !parentReal.startsWith(`${rootReal}${sep}`)) fail('hosted asset escapes store root');
  const raw = await readBoundedRegular(absolute, MAX_FILE_BYTES, 'hosted asset');
  if (raw.length !== metadata.size) fail('hosted asset metadata changed');
  if (sha256Hex(raw) !== metadata.sha256) fail('hosted asset digest is invalid');
  return raw;
}

function verifyManifest(value, catalog) {
  exactKeys(value, ['contract', 'product', 'catalog_id', 'release_count', 'releases', 'boundaries', 'store_id'], 'hosted store manifest');
  if (value.contract !== STORE_CONTRACT || value.product !== PRODUCT) fail('hosted store contract is invalid');
  const unsigned = structuredClone(value); delete unsigned.store_id;
  if (!SHA.test(value.store_id) || sha256Hex(canonicalJson(unsigned)) !== value.store_id) fail('hosted store seal is invalid');
  exactBoundary(value.boundaries);
  if (value.catalog_id !== catalog.catalog_id) fail('hosted store catalog identity is stale');
  if (!value.releases || typeof value.releases !== 'object' || Array.isArray(value.releases) || value.release_count !== Object.keys(value.releases).length) fail('hosted store release inventory is invalid');
  if (JSON.stringify(Object.keys(value.releases).sort()) !== JSON.stringify(Object.keys(catalog.releases).sort())) fail('hosted store release set does not match catalog');
  return value;
}

export async function loadHostedStore(rootInput, catalogInput) {
  const catalog = verifyCatalog(catalogInput);
  const root = resolve(rootInput);
  const rootStats = await lstat(root);
  if (rootStats.isSymbolicLink() || !rootStats.isDirectory()) fail('hosted store must be a regular directory');
  const manifestPath = join(root, STORE_MANIFEST);
  const manifest = verifyManifest(parseStrictJson(await readBoundedRegular(manifestPath, MAX_MANIFEST_BYTES, 'hosted store manifest'), 'hosted store manifest'), catalog);
  const expectedPaths = new Set([STORE_MANIFEST]);
  const releases = new Map();
  let totalFiles = 0;
  let totalBytes = 0;

  for (const [version, rawEntry] of Object.entries(manifest.releases)) {
    if (!VERSION.test(version)) fail('hosted store version is invalid');
    exactKeys(rawEntry, ['release_id', 'bundle_id', 'receipt_id', 'route_id', 'archive_sha256', 'object_root', 'entrypoint', 'file_count', 'total_bytes', 'files'], 'hosted store release');
    for (const key of ['release_id', 'bundle_id', 'receipt_id', 'archive_sha256']) if (!SHA.test(rawEntry[key])) fail('hosted store release identity is invalid');
    if (rawEntry.object_root !== `objects/${rawEntry.archive_sha256}/product` || rawEntry.entrypoint !== 'index.html') fail('hosted store object identity is invalid');
    const catalogRelease = catalog.releases[version]?.release;
    if (!catalogRelease) fail('hosted store release is absent from catalog');
    const identity = {
      release_id: catalogRelease.release_id,
      bundle_id: catalogRelease.bundle_id,
      receipt_id: catalogRelease.receipt_id,
      route_id: catalogRelease.route_id,
      archive_sha256: catalogRelease.archive.sha256,
    };
    for (const [key, expected] of Object.entries(identity)) if (rawEntry[key] !== expected) fail('hosted store release identity does not match catalog');
    if (!rawEntry.files || typeof rawEntry.files !== 'object' || Array.isArray(rawEntry.files) || rawEntry.file_count !== Object.keys(rawEntry.files).length || !Object.hasOwn(rawEntry.files, 'index.html')) fail('hosted store file inventory is invalid');
    const files = new Map();
    let releaseBytes = 0;
    for (const [assetPath, metadata] of Object.entries(rawEntry.files)) {
      safeRelative(assetPath);
      exactKeys(metadata, ['sha256', 'size'], 'hosted store file');
      if (!SHA.test(metadata.sha256) || !Number.isSafeInteger(metadata.size) || metadata.size < 0 || metadata.size > MAX_FILE_BYTES) fail('hosted store file metadata is invalid');
      const storePath = `${rawEntry.object_root}/${assetPath}`;
      expectedPaths.add(storePath);
      const raw = await readVerifiedFile(root, storePath, metadata);
      files.set(assetPath, { raw, sha256: metadata.sha256, size: metadata.size, contentType: contentType(assetPath) });
      releaseBytes += raw.length;
      totalBytes += raw.length;
      totalFiles += 1;
      if (totalFiles > MAX_FILES || totalBytes > MAX_TOTAL_BYTES) fail('hosted store exceeds runtime resource limits');
    }
    if (releaseBytes !== rawEntry.total_bytes) fail('hosted store release byte counter is invalid');
    releases.set(version, Object.freeze({
      version,
      releaseId: rawEntry.release_id,
      routeId: rawEntry.route_id,
      entrypoint: rawEntry.entrypoint,
      files,
    }));
  }
  const actualPaths = (await collectEntries(root)).sort();
  if (JSON.stringify(actualPaths) !== JSON.stringify([...expectedPaths].sort())) fail('hosted store file set does not match manifest');
  return Object.freeze({ root, manifest, catalog, releases });
}

export function parseHostedAssetPath(rawUrl) {
  const rawPath = String(rawUrl ?? '').split('?', 1)[0];
  if (!rawPath.startsWith('/app/')) return null;
  if (rawPath.includes('\\') || /%(?:2f|5c|00)/i.test(rawPath)) fail('hosted asset request path is unsafe');
  const segments = rawPath.split('/').slice(2);
  if (segments.length === 0 || segments[0] === '') fail('hosted release version is missing');
  const decoded = segments.map((segment) => {
    let value;
    try { value = decodeURIComponent(segment); } catch { fail('hosted asset request encoding is invalid'); }
    if (value.includes('/') || value.includes('\\') || value === '.' || value === '..' || /[\u0000-\u001f\u007f]/.test(value)) fail('hosted asset request path is unsafe');
    return value;
  });
  const version = decoded.shift();
  if (!VERSION.test(version)) fail('hosted release version is invalid');
  if (decoded.length === 0 || decoded.at(-1) === '') {
    if (decoded.at(-1) === '') decoded.pop();
    decoded.push('index.html');
  }
  if (decoded.some((part) => part.length === 0)) fail('hosted asset request path is unsafe');
  return { version, assetPath: safeRelative(decoded.join('/')) };
}

export function hostedAsset(store, version, assetPath) {
  return store.releases.get(version)?.files.get(assetPath) ?? null;
}

export function contentType(path) {
  switch (extname(path).toLowerCase()) {
    case '.html': return 'text/html; charset=utf-8';
    case '.css': return 'text/css; charset=utf-8';
    case '.js': case '.mjs': return 'text/javascript; charset=utf-8';
    case '.json': return 'application/json; charset=utf-8';
    case '.txt': case '.md': return 'text/plain; charset=utf-8';
    case '.svg': return 'image/svg+xml';
    case '.png': return 'image/png';
    case '.jpg': case '.jpeg': return 'image/jpeg';
    case '.webp': return 'image/webp';
    case '.ico': return 'image/x-icon';
    case '.wasm': return 'application/wasm';
    default: return 'application/octet-stream';
  }
}
