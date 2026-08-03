import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const html = readFileSync(
  new URL("../product_alpha/pilot-lab.html", import.meta.url),
  "utf8",
);
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.equal(scripts.length, 1, "Pilot Lab must contain one inline script");
const module = { exports: {} };
vm.runInNewContext(scripts[0][1], {
  module,
  exports: module.exports,
  Set,
  String,
});
const {
  fileKey,
  mergeFiles,
  clearWorkspaceState,
  stageReplacement,
  cancelReplacement,
  takeReplacement,
  pilotLabAvailability,
} = module.exports;

function file(
  name,
  size,
  lastModified,
  type = "application/x-ndjson",
  webkitRelativePath = "",
) {
  return { name, size, lastModified, type, webkitRelativePath };
}

test("file identity includes stable browser metadata", () => {
  const original = file("anonymous-a.jsonl", 120, 1);
  assert.equal(fileKey(original), fileKey(file("anonymous-a.jsonl", 120, 1)));

  const variants = [
    file("anonymous-b.jsonl", 120, 1),
    file("anonymous-a.jsonl", 121, 1),
    file("anonymous-a.jsonl", 120, 2),
    file("anonymous-a.jsonl", 120, 1, "application/json"),
    file(
      "anonymous-a.jsonl",
      120,
      1,
      "application/x-ndjson",
      "corrected/anonymous-a.jsonl",
    ),
  ];
  for (const variant of variants) {
    assert.notEqual(fileKey(original), fileKey(variant));
  }
});

test("add mode preserves existing batches and skips repeated files", () => {
  const first = file("anonymous-a.jsonl", 120, 1);
  const second = file("anonymous-b.jsonl", 130, 2);
  assert.deepEqual(
    Array.from(mergeFiles([first], [second, first], false), fileKey),
    [fileKey(first), fileKey(second)],
  );
});

test("a corrected export with the same filename is not discarded", () => {
  const original = file("anonymous-a.jsonl", 120, 1);
  const corrected = file("anonymous-a.jsonl", 132, 2);
  assert.deepEqual(
    Array.from(
      mergeFiles([original], [corrected, original, corrected], false),
      fileKey,
    ),
    [fileKey(original), fileKey(corrected)],
  );
});

test("replace mode discards the previous file set", () => {
  const first = file("anonymous-a.jsonl", 120, 1);
  const second = file("anonymous-b.jsonl", 130, 2);
  assert.deepEqual(
    Array.from(mergeFiles([first], [second], true), fileKey),
    [fileKey(second)],
  );
});

test("replacement staging leaves the current workspace untouched", () => {
  const current = file("anonymous-a.jsonl", 120, 1);
  const replacement = file("anonymous-b.jsonl", 130, 2);
  const state = {
    files: [current],
    pendingReplacement: [],
    clearArmed: true,
  };

  assert.equal(
    stageReplacement(state, [replacement, replacement]),
    "staged",
  );
  assert.deepEqual(Array.from(state.files, fileKey), [fileKey(current)]);
  assert.deepEqual(Array.from(state.pendingReplacement, fileKey), [
    fileKey(replacement),
  ]);
  assert.equal(state.clearArmed, false);
});

test("replacement can be cancelled or consumed exactly once", () => {
  const replacement = file("anonymous-b.jsonl", 130, 2);
  const state = { pendingReplacement: [] };

  stageReplacement(state, [replacement]);
  assert.equal(cancelReplacement(state), true);
  assert.deepEqual(Array.from(state.pendingReplacement), []);
  assert.equal(cancelReplacement(state), false);

  stageReplacement(state, [replacement]);
  assert.deepEqual(Array.from(takeReplacement(state), fileKey), [
    fileKey(replacement),
  ]);
  assert.deepEqual(Array.from(state.pendingReplacement), []);
  assert.deepEqual(Array.from(takeReplacement(state)), []);
});

test("clear requires a deliberate second action", () => {
  const state = {
    files: [file("anonymous-a.jsonl", 120, 1)],
    sessions: [{ session_id: "anonymous-a" }],
    errors: ["example"],
    duplicates: 1,
    summary: { sessions: 1 },
    clearArmed: false,
  };

  assert.equal(clearWorkspaceState(state), "armed");
  assert.equal(state.clearArmed, true);
  assert.equal(state.files.length, 1);
  assert.equal(clearWorkspaceState(state), "cleared");
  assert.deepEqual(Array.from(state.files), []);
  assert.deepEqual(Array.from(state.sessions), []);
  assert.deepEqual(Array.from(state.errors), []);
  assert.equal(state.duplicates, 0);
  assert.equal(state.summary, null);
  assert.equal(state.clearArmed, false);
});

test("empty workspaces do not arm destructive clear", () => {
  const state = { files: [], clearArmed: true };
  assert.equal(clearWorkspaceState(state), "empty");
  assert.equal(state.clearArmed, false);
});

test("interface exposes keyboard file pickers and live status", () => {
  assert.match(html, /id="chooseFiles" type="button">Add session files/);
  assert.match(html, /id="files"[^>]+multiple hidden/);
  assert.match(html, /id="chooseReplaceFiles" type="button" aria-pressed="false">Replace workspace files/);
  assert.match(html, /id="cancelReplace" type="button" hidden>Cancel replacement/);
  assert.match(html, /id="replaceFiles"[^>]+multiple hidden/);
  assert.match(html, /q\("#chooseFiles"\)\.addEventListener\("click",\(\)=>q\("#files"\)\.click\(\)\)/);
  assert.match(html, /q\("#chooseReplaceFiles"\)\.addEventListener\("click",chooseOrConfirmReplacement\)/);
  assert.match(html, /q\("#cancelReplace"\)\.addEventListener\("click",cancelReplacementSelection\)/);
  assert.match(html, /readFiles\(event\.target\.files,"add"\)/);
  assert.match(html, /stageReplacementFiles\(event\.target\.files\)/);
  assert.match(html, /takeReplacement\(state\)/);
  assert.match(html, /Replacement cancelled\. The current workspace is unchanged\./);
  assert.match(html, /readFiles\(event\.dataTransfer\.files,"add"\)/);
  assert.match(html, /id="workspaceStatus" role="status" aria-live="polite" aria-atomic="true"/);
  assert.match(html, /id="status" role="status" aria-live="polite" aria-atomic="true"/);
  assert.match(html, /id="errors" role="region"[^>]+aria-live="polite"/);
  assert.match(html, /\.button:focus-visible,a:focus-visible/);
  assert.doesNotMatch(html, /<label class="button [^"]+" for="(?:files|replaceFiles)"/);
});

test("clear control is announced and visually changes when armed", () => {
  assert.match(html, /id="clear" type="button" aria-pressed="false" aria-describedby="workspaceStatus"/);
  assert.match(html, /Confirm clear workspace/);
  assert.match(html, /clear\.classList\.toggle\("danger",state\.clearArmed\)/);
  assert.match(html, /q\("#chooseFiles"\)\.focus\(\)/);
});


test("replacement confirmation is explicit and cancellable", () => {
  assert.match(html, /Confirm replace with \${pending} file/);
  assert.match(html, /current workspace remains loaded until confirmation/);
  assert.match(html, /replace\.classList\.toggle\("danger",Boolean\(pending\)\)/);
  assert.match(html, /replace\.setAttribute\("aria-pressed",String\(Boolean\(pending\)\)\)/);
  assert.match(html, /cancel\.hidden=!pending/);
  assert.match(html, /Pending replacement cancelled\. Press Clear workspace again/);
});


test("dynamic tables expose captions and header relationships", () => {
  assert.match(html, /<caption>Loaded anonymous sessions<\/caption>/);
  assert.match(html, /<th scope="col">Session<\/th>/);
  assert.match(html, /<th scope="col">Progress<\/th>/);
  assert.match(html, /<th scope="col">Duration<\/th>/);
  assert.match(html, /<th scope="col">Continue<\/th>/);
  assert.match(html, /<caption>Cohort aggregate metrics<\/caption>/);
  assert.match(html, /<th scope="row">Started<\/th>/);
  assert.match(html, /<th scope="row">\${title\(key\)}<\/th>/);
  assert.match(html, /<th scope="row">Continue yes<\/th>/);
});

test("wide validation ledger is a keyboard-scrollable named region", () => {
  assert.match(html, /class="table-scroll" role="region" aria-label="Loaded session validation ledger" tabindex="0"/);
  assert.match(html, /\.table-scroll\{max-width:100%;overflow-x:auto\}/);
  assert.match(html, /\.table-scroll:focus-visible\{outline:3px solid var\(--accent\)/);
});

test("Pilot Lab availability requires an exact launcher build identity", () => {
  assert.deepEqual(
    JSON.parse(JSON.stringify(pilotLabAvailability("a".repeat(64)))),
    { ready: true, disabled: false },
  );
  for (const buildId of ["", "not-a-build-id", "A".repeat(64), "a".repeat(63)]) {
    assert.deepEqual(
      JSON.parse(JSON.stringify(pilotLabAvailability(buildId))),
      { ready: false, disabled: true },
    );
  }
});

test("missing or invalid build identity keeps Pilot Lab inert", () => {
  assert.match(html, /id="workspaceStatus" role="status" aria-live="polite" aria-atomic="true" tabindex="-1"/);
  assert.match(html, /function applyPilotLabAvailability\(buildId\)/);
  assert.match(html, /document\.querySelectorAll\("button,input"\)\.forEach\(node=>node\.disabled=view\.disabled\)/);
  assert.match(html, /q\("#drop"\)\.setAttribute\("aria-disabled",String\(view\.disabled\)\)/);

  const guardAt = html.indexOf("if(!applyPilotLabAvailability(EXPECTED_BUILD_ID)){");
  const statusAt = html.indexOf("Pilot build ID is missing or invalid", guardAt);
  const assertiveAt = html.indexOf('status.setAttribute("aria-live","assertive")', statusAt);
  const focusAt = html.indexOf("status.focus()", assertiveAt);
  const elseAt = html.indexOf("}else{", focusAt);
  const handlerAt = html.indexOf('q("#chooseFiles").addEventListener', elseAt);

  assert.notEqual(guardAt, -1);
  assert.ok(guardAt < statusAt, "invalid startup must announce a specific build error");
  assert.ok(statusAt < assertiveAt, "the build error must become assertive");
  assert.ok(assertiveAt < focusAt, "the error must be announced before focus moves");
  assert.ok(focusAt < elseAt, "invalid startup must stay outside the ready branch");
  assert.ok(elseAt < handlerAt, "file handlers must only install for a valid launcher build");
});
