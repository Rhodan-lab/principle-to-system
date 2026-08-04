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
  recorderAvailability,
  validationFocusSelector,
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

test("operational checklist keeps capture controls visible and state-bound", () => {
  assert.match(html, /class="skip-link" href="#recorder"/);
  assert.equal((html.match(/class="section-number"/g) || []).length, 6);
  assert.match(html, /<details class="card preview">/);
  assert.match(html, /id="download"[^>]*type="submit"[^>]*>Validate and download JSONL<\/button>/);
  assert.match(html, /id="download"[^>]*disabled/);
  assert.match(html, /id="copy"[^>]*disabled/);
  assert.match(html, /id="reset"[^>]*disabled/);
  assert.match(html, /q\("#download"\)\.disabled=view\.locked/);
  assert.match(html, /q\("#copy"\)\.disabled=view\.locked/);
  assert.match(html, /\[q\("#download"\),q\("#copy"\),q\("#reset"\)\]\.forEach\(node=>node\.disabled=view\.disabled\)/);
});

test("validation directs facilitators to the field that needs correction", () => {
  const valid = {
    session_id: "anonymous-a1",
    completed_steps: [],
    started: true,
    duration_minutes: 10,
    facilitator_notes: "",
  };
  assert.equal(
    validationFocusSelector({ ...valid, session_id: "learner-a1" }, ["label"]),
    "#sessionId",
  );
  assert.equal(
    validationFocusSelector(
      { ...valid, completed_steps: ["observe"], started: false },
      ["started"],
    ),
    "#started",
  );
  assert.equal(
    validationFocusSelector({ ...valid, duration_minutes: 181 }, ["duration"]),
    "#duration",
  );
  assert.equal(
    validationFocusSelector(
      { ...valid, facilitator_notes: "email: learner@example.com" },
      ["identity"],
    ),
    "#notes",
  );
  assert.equal(validationFocusSelector(valid, ["Pilot build ID is invalid"]), "#status");
  assert.equal(validationFocusSelector(valid, []), null);
});

test("score controls are named fieldsets with described rubric evidence", () => {
  assert.match(html, /document\.createElement\("fieldset"\)/);
  assert.match(html, /document\.createElement\("legend"\)/);
  assert.match(html, /card\.setAttribute\("aria-describedby",`\$\{promptId\} \$\{evidenceId\}`\)/);
  assert.match(html, /\.measure legend\{/);
  assert.doesNotMatch(html, /document\.createElement\("section"\),title=document\.createElement\("h3"\)/);
});

test("validation errors are announced, marked, and focused", () => {
  assert.match(html, /id="status" role="status" aria-live="polite" aria-atomic="true" tabindex="-1"/);
  assert.equal((html.match(/reportValidation\(errors,lastRecord\)/g) || []).length, 2);
  assert.match(html, /target\.setAttribute\("aria-invalid","true"\)/);
  assert.match(html, /target\.setAttribute\("aria-describedby","status"\)/);
  assert.match(html, /target\.focus\(\)/);
  assert.match(html, /kind==="error"\?"assertive":"polite"/);
  assert.match(html, /a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible/);
});

test("clipboard failure restores the download fallback", () => {
  assert.match(html, /id="download"[^>]*type="submit"[^>]*>Validate and download JSONL<\/button>/);
  const source = html.match(
    /async function copyRecord\(\)\{([\s\S]*?)\}\nfunction resetForm/,
  );
  assert.ok(source, "copyRecord source must be testable");
  const body = source[1];
  const cancelAt = body.indexOf("cancelCapture(captureState)");
  const applyAt = body.indexOf("applyCaptureState()", cancelAt);
  const statusAt = body.indexOf("Clipboard access is unavailable", cancelAt);
  const focusAt = body.indexOf('q("#download").focus()', cancelAt);

  assert.notEqual(cancelAt, -1);
  assert.notEqual(applyAt, -1);
  assert.notEqual(statusAt, -1);
  assert.notEqual(focusAt, -1);
  assert.ok(cancelAt < applyAt, "failed copy must release the reservation first");
  assert.ok(applyAt < statusAt, "controls must be re-enabled before fallback guidance");
  assert.ok(statusAt < focusAt, "fallback guidance must be set before focus moves");
});

test("recorder availability distinguishes loading, ready, and error", () => {
  assert.deepEqual(plain(recorderAvailability("loading")), {
    busy: true,
    disabled: true,
  });
  assert.deepEqual(plain(recorderAvailability("ready")), {
    busy: false,
    disabled: false,
  });
  assert.deepEqual(plain(recorderAvailability("error")), {
    busy: false,
    disabled: true,
  });
  assert.throws(() => recorderAvailability("unknown"), /invalid recorder availability/);
});

test("recorder load failure disables inert controls and focuses the error", () => {
  assert.match(html, /function applyRecorderAvailability\(state\)/);
  assert.match(html, /form\.setAttribute\("aria-busy",String\(view\.busy\)\)/);
  assert.match(html, /form\.setAttribute\("aria-disabled","true"\)/);
  assert.match(html, /form\.querySelectorAll\("input,select,textarea,button"\)\.forEach\(node=>node\.disabled=view\.disabled\)/);

  const source = html.match(/async function init\(\)\{([\s\S]*?)\}\nif\(typeof document/);
  assert.ok(source, "init source must be testable");
  const body = source[1];
  const loadingAt = body.indexOf('applyRecorderAvailability("loading")');
  const fetchAt = body.indexOf("await Promise.all(");
  const readyAt = body.indexOf('applyRecorderAvailability("ready")');
  const captureAt = body.indexOf("applyCaptureState()", readyAt);
  const errorAt = body.lastIndexOf('applyRecorderAvailability("error")');
  const statusAt = body.indexOf("Serve the Product Alpha build", errorAt);
  const focusAt = body.indexOf('q("#status").focus()', errorAt);

  assert.ok(loadingAt < fetchAt, "controls must lock before asset loading begins");
  assert.ok(fetchAt < readyAt, "controls become ready only after assets load");
  assert.ok(readyAt < captureAt, "capture state applies after controls become available");
  assert.ok(errorAt < statusAt, "inert controls must disable before the error is announced");
  assert.ok(statusAt < focusAt, "the error must be announced before focus moves");
});

test("missing or invalid build identity keeps the recorder inert", () => {
  const source = html.match(/async function init\(\)\{([\s\S]*?)\}\nif\(typeof document/);
  assert.ok(source, "init source must be testable");
  const body = source[1];
  const guardAt = body.indexOf("if(!BUILD_ID_PATTERN.test(pilotBuildId)){");
  const errorAt = body.indexOf('applyRecorderAvailability("error")', guardAt);
  const statusAt = body.indexOf("Pilot build ID is missing or invalid", errorAt);
  const focusAt = body.indexOf('q("#status").focus()', statusAt);
  const returnAt = body.indexOf("return}", focusAt);
  const listenersAt = body.indexOf('[q("#sessionId")', guardAt);
  const readyAt = body.indexOf('applyRecorderAvailability("ready")', guardAt);

  assert.notEqual(guardAt, -1);
  assert.ok(guardAt < errorAt, "invalid build identity must enter the inert state");
  assert.ok(errorAt < statusAt, "controls must disable before the error is announced");
  assert.ok(statusAt < focusAt, "the build identity error must be announced before focus moves");
  assert.ok(focusAt < returnAt, "startup must stop after focusing the persistent error");
  assert.ok(returnAt < listenersAt, "invalid startup must stop before handlers are installed");
  assert.ok(returnAt < readyAt, "invalid startup must never enable recorder controls");
});
