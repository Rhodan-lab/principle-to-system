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
const { fileKey, mergeFiles, clearWorkspaceState } = module.exports;

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
  assert.match(html, /id="chooseReplaceFiles" type="button">Replace workspace files/);
  assert.match(html, /id="replaceFiles"[^>]+multiple hidden/);
  assert.match(html, /q\("#chooseFiles"\)\.addEventListener\("click",\(\)=>q\("#files"\)\.click\(\)\)/);
  assert.match(html, /q\("#chooseReplaceFiles"\)\.addEventListener\("click",\(\)=>q\("#replaceFiles"\)\.click\(\)\)/);
  assert.match(html, /readFiles\(event\.target\.files,"add"\)/);
  assert.match(html, /readFiles\(event\.target\.files,"replace"\)/);
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
