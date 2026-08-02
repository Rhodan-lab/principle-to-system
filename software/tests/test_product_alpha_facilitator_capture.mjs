import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import vm from "node:vm";

const html = fs.readFileSync("software/product_alpha/facilitator.html", "utf8");
const match = html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match, "facilitator page must contain one script");
const sandbox = { module: { exports: {} }, exports: {} };
vm.runInNewContext(match[1], sandbox, { filename: "facilitator.html" });
const { createCaptureState, markCaptured, startNextSession, captureView } = sandbox.module.exports;

test("new recorder state is editable", () => {
  const state = createCaptureState();
  assert.deepEqual(JSON.parse(JSON.stringify(state)), {
    captured: false,
    sessionId: null,
    method: null,
  });
  assert.equal(captureView(state).locked, false);
  assert.equal(captureView(state).resetLabel, "Reset session");
});

test("first successful capture locks the original session", () => {
  const state = createCaptureState();
  assert.equal(markCaptured(state, "anonymous-a1", "download"), true);
  assert.equal(markCaptured(state, "anonymous-a1", "clipboard"), false);
  assert.equal(state.sessionId, "anonymous-a1");
  assert.equal(state.method, "download");
  assert.equal(captureView(state).locked, true);
  assert.equal(captureView(state).resetLabel, "Start next session");
  assert.match(captureView(state).boundary, /anonymous-a1/);
});

test("starting the next session clears the capture lock", () => {
  const state = createCaptureState();
  markCaptured(state, "anonymous-a1", "clipboard");
  startNextSession(state);
  assert.equal(state.captured, false);
  assert.equal(state.sessionId, null);
  assert.equal(state.method, null);
  assert.equal(captureView(state).locked, false);
});

test("recorder exposes the immutable capture boundary without persistence", () => {
  assert.match(html, /id="captureBoundary"/);
  assert.match(html, /Start next session/);
  assert.match(html, /if\(typeof document!=="undefined"\)init\(\)/);
  assert.doesNotMatch(html, /localStorage|sessionStorage|sendBeacon|XMLHttpRequest/);
});
