import assert from 'node:assert/strict';
import { generateKeyPairSync, sign as signRaw } from 'node:crypto';
import { spawn } from 'node:child_process';
import { chmod, mkdtemp, readFile, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import {
  OIDC_POLICY_CONTRACT,
  PRODUCT,
  TENANT_CONTRACT,
  canonicalJson,
  exchangeIdentityAssertion,
  sealOidcPolicy,
  sealTenantConfig,
} from '../principia_atlas/hosted/index.mjs';

const identitySecret = 'identity-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const sessionSecret = 'session-secret-0123456789-abcdefghijklmnopqrstuvwxyz';
const issuer = 'https://identity.example.test';
const audience = 'principia-atlas-external';
const pair = generateKeyPairSync('rsa', { modulusLength: 2048 });

function unsignedPolicy() {
  return {
    contract: OIDC_POLICY_CONTRACT,
    product: PRODUCT,
    issuer,
    audience,
    authorized_party: null,
    jwks: {
      uri: `${issuer}/.well-known/jwks.json`,
      allowed_algorithms: ['RS256'],
      cache_ttl_seconds: 300,
      fetch_timeout_ms: 3000,
      max_bytes: 65536,
    },
    token: {
      max_ttl_seconds: 3600,
      clock_skew_seconds: 30,
      internal_assertion_ttl_seconds: 180,
      require_iat: true,
      require_email_verified: false,
    },
    claims: {
      tenant: { name: 'organization', values: { 'external-school': 'school-demo' } },
      roles: { name: 'groups', values: { students: 'learner' }, reject_unmapped: true },
      required: {},
    },
  };
}

function tenantConfig() {
  return sealTenantConfig({
    contract: TENANT_CONTRACT,
    product: PRODUCT,
    identity: {
      issuer: 'https://identity.internal.test',
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

function jwks() {
  const publicJwk = pair.publicKey.export({ format: 'jwk' });
  return {
    keys: [{
      kty: 'RSA', kid: 'rsa-1', use: 'sig', key_ops: ['verify'], alg: 'RS256',
      n: publicJwk.n, e: publicJwk.e,
    }],
  };
}

function signJwt(nowSeconds) {
  const encode = (value) => Buffer.from(JSON.stringify(value), 'utf8').toString('base64url');
  const header = encode({ alg: 'RS256', kid: 'rsa-1', typ: 'JWT' });
  const payload = encode({
    iss: issuer,
    aud: audience,
    sub: 'learner-1',
    organization: 'external-school',
    groups: ['students'],
    iat: nowSeconds - 5,
    exp: nowSeconds + 300,
  });
  const signing = `${header}.${payload}`;
  const signature = signRaw('RSA-SHA256', Buffer.from(signing, 'ascii'), pair.privateKey).toString('base64url');
  return `${signing}.${signature}`;
}

function runCli(args, input = '') {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, ['software/principia_atlas/hosted/oidc_cli.mjs', ...args], {
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    const stdout = [];
    const stderr = [];
    child.stdout.on('data', (chunk) => stdout.push(chunk));
    child.stderr.on('data', (chunk) => stderr.push(chunk));
    child.on('error', reject);
    child.on('close', (code) => resolve({
      code,
      stdout: Buffer.concat(stdout).toString('utf8'),
      stderr: Buffer.concat(stderr).toString('utf8'),
    }));
    child.stdin.end(input);
  });
}

test('OIDC CLI seals policy verifies static JWKS and adapts token only from stdin', async () => {
  const root = await mkdtemp(join(tmpdir(), 'principia-oidc-cli-'));
  const unsignedPath = join(root, 'policy.unsigned.json');
  const policyPath = join(root, 'policy.json');
  const jwksPath = join(root, 'jwks.json');
  const tenantsPath = join(root, 'tenants.json');
  const secretPath = join(root, 'identity.secret');
  await writeFile(unsignedPath, canonicalJson(unsignedPolicy()));
  await writeFile(jwksPath, canonicalJson(jwks()));
  await writeFile(tenantsPath, canonicalJson(tenantConfig()));
  await writeFile(secretPath, identitySecret, { mode: 0o600 });
  await chmod(secretPath, 0o600);

  const sealed = await runCli(['seal-policy', '--input', unsignedPath, '--output', policyPath]);
  assert.equal(sealed.code, 0, sealed.stderr);
  const policy = JSON.parse(await readFile(policyPath, 'utf8'));
  assert.equal(policy.policy_id, sealOidcPolicy(unsignedPolicy()).policy_id);

  const verified = await runCli(['verify', '--policy', policyPath, '--jwks', jwksPath, '--tenants', tenantsPath]);
  assert.equal(verified.code, 0, verified.stderr);
  assert.equal(JSON.parse(verified.stdout).provider.network, false);

  const nowSeconds = Math.floor(Date.now() / 1000);
  const externalToken = signJwt(nowSeconds);
  const args = [
    'adapt', '--policy', policyPath, '--jwks', jwksPath, '--tenants', tenantsPath,
    '--identity-secret-file', secretPath,
  ];
  assert.equal(args.includes(externalToken), false);
  const adapted = await runCli(args, `${externalToken}\n`);
  assert.equal(adapted.code, 0, adapted.stderr);
  assert.equal(adapted.stderr.includes(externalToken), false);
  const assertion = adapted.stdout.trim();
  assert.equal(assertion.split('.').length, 3);
  const exchange = exchangeIdentityAssertion(
    assertion,
    identitySecret,
    sessionSecret,
    tenantConfig(),
    nowSeconds,
    () => 'session_identifier_cli_12345',
  );
  assert.equal(exchange.session.tenant_id, 'school-demo');
  assert.deepEqual(exchange.session.roles, ['learner']);
});

test('OIDC CLI rejects embedded newlines and does not echo external tokens', async () => {
  const result = await runCli(['adapt'], 'token\nsecond-line');
  assert.notEqual(result.code, 0);
  assert.equal(result.stdout, '');
  assert.equal(result.stderr.includes('token\nsecond-line'), false);
});
