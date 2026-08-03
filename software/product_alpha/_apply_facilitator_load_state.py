#!/usr/bin/env python3
"""Apply bounded facilitator initialization-state recovery once."""
from pathlib import Path

HTML_PATH = Path("software/product_alpha/facilitator.html")
TEST_PATH = Path("software/tests/test_product_alpha_facilitator_capture.mjs")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


html = HTML_PATH.read_text(encoding="utf-8")
html = replace_once(
    html,
    'function captureView(state){const pending=state.pending===true;return{locked:state.captured||pending,resetDisabled:pending,resetLabel:pending?"Copying record…":state.captured?"Start next session":"Reset session",boundary:pending?`Copying ${state.sessionId}. This form is locked until clipboard access finishes.`:state.captured?`Captured ${state.sessionId}. This record is locked in this tab.`:"After a successful download or copy, this record locks in the current tab. Start the next session to generate a fresh anonymous label."}}\nconst captureState=createCaptureState(),captureStateApi={createCaptureState,reserveCapture,commitCapture,cancelCapture,markCaptured,startNextSession,captureView,validationFocusSelector};',
    'function captureView(state){const pending=state.pending===true;return{locked:state.captured||pending,resetDisabled:pending,resetLabel:pending?"Copying record…":state.captured?"Start next session":"Reset session",boundary:pending?`Copying ${state.sessionId}. This form is locked until clipboard access finishes.`:state.captured?`Captured ${state.sessionId}. This record is locked in this tab.`:"After a successful download or copy, this record locks in the current tab. Start the next session to generate a fresh anonymous label."}}\nfunction recorderAvailability(state){if(!["loading","ready","error"].includes(state))throw new Error("invalid recorder availability");return{busy:state==="loading",disabled:state!=="ready"}}\nconst captureState=createCaptureState(),captureStateApi={createCaptureState,reserveCapture,commitCapture,cancelCapture,markCaptured,startNextSession,captureView,recorderAvailability,validationFocusSelector};',
    "recorder availability contract",
)
html = replace_once(
    html,
    'function applyCaptureState(){const view=captureView(captureState);q("#recorder").querySelectorAll(\'input,select,textarea,button[type="submit"],#copy\').forEach(node=>node.disabled=view.locked);q("#reset").disabled=view.resetDisabled;q("#reset").textContent=view.resetLabel;q("#captureBoundary").textContent=view.boundary}',
    'function applyCaptureState(){const view=captureView(captureState);q("#recorder").querySelectorAll(\'input,select,textarea,button[type="submit"],#copy\').forEach(node=>node.disabled=view.locked);q("#reset").disabled=view.resetDisabled;q("#reset").textContent=view.resetLabel;q("#captureBoundary").textContent=view.boundary}\nfunction applyRecorderAvailability(state){const view=recorderAvailability(state),form=q("#recorder");form.setAttribute("aria-busy",String(view.busy));if(view.disabled)form.setAttribute("aria-disabled","true");else form.removeAttribute("aria-disabled");form.querySelectorAll("input,select,textarea,button").forEach(node=>node.disabled=view.disabled)}',
    "recorder availability application",
)
old_init = 'async function init(){try{[rubric,template]=await Promise.all([fetch("evaluation/rubric.json").then(r=>{if(!r.ok)throw new Error("rubric");return r.json()}),fetch("evaluation/session-template.json").then(r=>{if(!r.ok)throw new Error("template");return r.json()})]);renderSteps();renderMeasures();renderTags();q("#sessionId").value=anonymousId();[q("#sessionId"),q("#duration"),q("#started"),q("#continueAnswer"),q("#notes")].forEach(node=>node.addEventListener("input",refresh));q("#recorder").addEventListener("submit",event=>{event.preventDefault();if(captureState.captured||captureState.pending){captureConflict();return}refresh();const errors=validate(lastRecord);if(errors.length){reportValidation(errors,lastRecord);return}download(lastRecord);completeCapture("download")});q("#copy").addEventListener("click",copyRecord);q("#reset").addEventListener("click",resetForm);applyCaptureState();refresh()}catch{q("#preview").textContent="Recorder assets could not be loaded.";setStatus("Serve the Product Alpha build through a local HTTP server before using the recorder.","error")}}'
new_init = 'async function init(){applyRecorderAvailability("loading");try{[rubric,template]=await Promise.all([fetch("evaluation/rubric.json").then(r=>{if(!r.ok)throw new Error("rubric");return r.json()}),fetch("evaluation/session-template.json").then(r=>{if(!r.ok)throw new Error("template");return r.json()})]);renderSteps();renderMeasures();renderTags();q("#sessionId").value=anonymousId();[q("#sessionId"),q("#duration"),q("#started"),q("#continueAnswer"),q("#notes")].forEach(node=>node.addEventListener("input",refresh));q("#recorder").addEventListener("submit",event=>{event.preventDefault();if(captureState.captured||captureState.pending){captureConflict();return}refresh();const errors=validate(lastRecord);if(errors.length){reportValidation(errors,lastRecord);return}download(lastRecord);completeCapture("download")});q("#copy").addEventListener("click",copyRecord);q("#reset").addEventListener("click",resetForm);applyRecorderAvailability("ready");applyCaptureState();refresh()}catch{applyRecorderAvailability("error");q("#preview").textContent="Recorder assets could not be loaded.";setStatus("Serve the Product Alpha build through a local HTTP server before using the recorder.","error");q("#status").focus()}}'
html = replace_once(html, old_init, new_init, "recorder initialization states")
HTML_PATH.write_text(html, encoding="utf-8")

test_text = TEST_PATH.read_text(encoding="utf-8")
test_text = replace_once(
    test_text,
    '  captureView,\n  validationFocusSelector,',
    '  captureView,\n  recorderAvailability,\n  validationFocusSelector,',
    "recorder availability test import",
)
addition = r'''

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
  const errorAt = body.indexOf('applyRecorderAvailability("error")');
  const statusAt = body.indexOf("Serve the Product Alpha build", errorAt);
  const focusAt = body.indexOf('q("#status").focus()', errorAt);

  assert.ok(loadingAt < fetchAt, "controls must lock before asset loading begins");
  assert.ok(fetchAt < readyAt, "controls become ready only after assets load");
  assert.ok(readyAt < captureAt, "capture state applies after controls become available");
  assert.ok(errorAt < statusAt, "inert controls must disable before the error is announced");
  assert.ok(statusAt < focusAt, "the error must be announced before focus moves");
});
'''
if addition.strip() in test_text:
    raise SystemExit("facilitator load-state tests already present")
TEST_PATH.write_text(test_text.rstrip() + addition, encoding="utf-8")
