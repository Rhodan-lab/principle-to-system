import assert from 'node:assert/strict';
import { createServer as createHttpServer } from 'node:http';
import test from 'node:test';

import { createBrowserOidcEdgeServer } from '../principia_atlas/hosted/browser_edge.mjs';

async function freePort() {
  const server = createHttpServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;
  await new Promise((resolve) => server.close(resolve));
  return port;
}

function inertFlow(publicOrigin) {
  return {
    config: Object.freeze({
      public_origin: publicOrigin,
      config_id: 'b'.repeat(64),
      login_path: '/auth/login',
      callback_path: '/auth/callback',
    }),
    begin() { throw new Error('login is outside this test'); },
    complete() { throw new Error('callback is outside this test'); },
    clear_cookie() { return 'flow=; Path=/; Max-Age=0'; },
    close() {},
  };
}

test('browser edge requires a literal public Origin and advertises PUT for progress routes', async () => {
  const port = await freePort();
  const publicOrigin = `http://127.0.0.1:${port}`;
  let upstreamCalls = 0;
  const fetchImpl = async () => {
    upstreamCalls += 1;
    return new Response('{"unexpected":true}', {
      status: 200,
      headers: { 'content-type': 'application/json' },
    });
  };
  const server = createBrowserOidcEdgeServer({
    flow: inertFlow(publicOrigin),
    upstreamOrigin: 'http://127.0.0.1:9099',
    fetchImpl,
  });
  await new Promise((resolve) => server.listen(port, '127.0.0.1', resolve));
  try {
    const progressPath = '/api/saas/progress/refrigerator-v1/observe';
    const badOrigin = await fetch(`${publicOrigin}${progressPath}`, {
      method: 'PUT',
      headers: {
        Origin: `${publicOrigin}/not-an-origin`,
        'Content-Type': 'application/json',
        'X-CSRF-Token': 'A'.repeat(43),
        'Idempotency-Key': 'literal_origin_test_0001',
      },
      body: '{"release_id":"principia-atlas-release:0.5.0-beta.1","status":"completed","expected_revision":0}',
    });
    assert.equal(badOrigin.status, 403);
    assert.deepEqual(await badOrigin.json(), { error: 'origin_rejected' });
    assert.equal(upstreamCalls, 0);

    const unsupported = await fetch(`${publicOrigin}${progressPath}`, {
      method: 'DELETE',
      headers: { Origin: publicOrigin },
    });
    assert.equal(unsupported.status, 405);
    assert.equal(unsupported.headers.get('allow'), 'GET, HEAD, POST, PUT');
    assert.deepEqual(await unsupported.json(), { error: 'method_not_allowed' });
    assert.equal(upstreamCalls, 0);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});
