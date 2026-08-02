import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import vm from "node:vm";

const html = fs.readFileSync("software/product_alpha/facilitator.html", "utf8");
const match = html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match, "facilitator page must contain one script");
const sandbox = { module: { exports: {} }, exports: {} };
vm.runInNewContext(match[1], sandbox, { filename: "facilitator.html" });
const {
  createCaptureState,
  reserveCapture,
  commitCapture,
  cancelCapture,
  markCaptured,
  startNextSession,
  captureView,
} = sandbox.module.exports;

function plain(value) {
  return JSON.parse(JSON.stringify(value));
}

test("new recorder state is editable", () => {
  const state = createCaptureState();
  assert.deepEqual(plain(state), {
    captured: false,
    pending: false,
    sessionId: null,
    method: null,
  });
  assert.equal(captureView(state).locked, false);
  assert.equal(captureView(state).resetDisabled, false);
  assert.equal(captureView(state).resetLabel, "Reset session");
});

test("first successful capture locks the original session", () => {
  const state = createCaptureState();
  assert.equal(markCaptured(state, "anonymous-a1", "download"), true);
  assert.equal(markCaptured(state, "anonymous-a1", "clipboard"), false);
  assert.equal(state.sessionId, "anonymous-a1");
  assert.equal(state.method, "download");
  assert.equal(state.pending, false);
  assert.equal(captureView(state).locked, true);
  assert.equal(captureView(state).resetDisabled, false);
  assert.equal(captureView(state).resetLabel, "Start next session");
  assert.match(captureView(state).boundary, /anonymous-a1/);
});

test("a later session cannot replace the captured state", () => {
  const state = createCaptureState();
  assert.equal(markCaptured(state, "anonymous-a1", "download"), true);
  const original = plain(state);

  assert.equal(markCaptured(state, "anonymous-b2", "clipboard"), false);
  assert.deepEqual(plain(state), original);
  assert.match(captureView(state).boundary, /anonymous-a1/);
  assert.doesNotMatch(captureView(state).boundary, /anonymous-b2/);
});

test("clipboard reservation locks before asynchronous work begins", () => {
  const state = createCaptureState();
  assert.equal(reserveCapture(state, "anonymous-a1", "clipboard"), true);
  assert.equal(reserveCapture(state, "anonymous-b2", "clipboard"), false);
  assert.equal(markCaptured(state, "anonymous-b2", "download"), false);
  assert.deepEqual(plain(state), {
    captured: false,
    pending: true,
    sessionId: "anonymous-a1",
    method: "clipboard",
  });
  assert.equal(captureView(state).locked, true);
  assert.equal(captureView(state).resetDisabled, true);
  assert.equal(captureView(state).resetLabel, "Copying record…");
  assert.match(captureView(state).boundary, /anonymous-a1/);
});

test("pending clipboard capture cannot be reset or replaced", () => {
  const state = createCaptureState();
  reserveCapture(state, "anonymous-a1", "clipboard");
  const original = plain(state);

  assert.equal(startNextSession(state), false);
  assert.equal(reserveCapture(state, "anonymous-b2", "clipboard"), false);
  assert.deepEqual(plain(state), original);
});

test("successful clipboard completion commits the reservation", () => {
  const state = createCaptureState();
  reserveCapture(state, "anonymous-a1", "clipboard");

  assert.equal(commitCapture(state), true);
  assert.equal(commitCapture(state), false);
  assert.deepEqual(plain(state), {
    captured: true,
    pending: false,
    sessionId: "anonymous-a1",
    method: "clipboard",
  });
});

test("failed clipboard completion releases the reservation", () => {
  const state = createCaptureState();
  reserveCapture(state, "anonymous-a1", "clipboard");

  assert.equal(cancelCapture(state), true);
  assert.equal(cancelCapture(state), false);
  assert.deepEqual(plain(state), {
    captured: false,
    pending: false,
    sessionId: null,
    method: null,
  });
  assert.equal(reserveCapture(state, "anonymous-a1", "clipboard"), true);
});

test("starting the next session clears a completed capture", () => {
  const state = createCaptureState();
  markCaptured(state, "anonymous-a1", "clipboard");
  assert.equal(startNextSession(state), true);
  assert.equal(state.captured, false);
  assert.equal(state.pending, false);
  assert.equal(state.sessionId, null);
  assert.equal(state.method, null);
  assert.equal(captureView(state).locked, false);
});

test("copy handler reserves before awaiting clipboard access", () => {
  const source = html.match(
    /async function copyRecord\(\)\{([\s\S]*?)\}\nfunction resetForm/,
  );
  assert.ok(source, "copyRecord source must be testable");
  const body = source[1];
  const reserveAt = body.indexOf("reserveCapture(");
  const clipboardAt = body.indexOf("await navigator.clipboard.writeText(");
  const cancelAt = body.indexOf("cancelCapture(");

  assert.notEqual(reserveAt, -1);
  assert.notEqual(clipboardAt, -1);
  assert.notEqual(cancelAt, -1);
  assert.ok(reserveAt < clipboardAt, "capture must be reserved before clipboard write");
  assert.ok(clipboardAt < cancelAt, "failed clipboard writes must release reservation");
});

test("recorder exposes the immutable capture boundary without persistence", () => {
  assert.match(html, /id="captureBoundary"/);
  assert.match(html, /Start next session/);
  assert.match(html, /if\(typeof document!=="undefined"\)init\(\)/);
  assert.doesNotMatch(html, /localStorage|sessionStorage|sendBeacon|XMLHttpRequest/);
});
