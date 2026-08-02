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
const { fileKey, mergeFiles } = module.exports;

function file(name, size, lastModified, type = "application/x-ndjson") {
  return { name, size, lastModified, type, webkitRelativePath: "" };
}

test("file identity includes stable browser metadata", () => {
  assert.equal(
    fileKey(file("anonymous-a.jsonl", 120, 1)),
    fileKey(file("anonymous-a.jsonl", 120, 1)),
  );
  assert.notEqual(
    fileKey(file("anonymous-a.jsonl", 120, 1)),
    fileKey(file("anonymous-b.jsonl", 120, 1)),
  );
});

test("add mode preserves existing batches and skips repeated files", () => {
  const first = file("anonymous-a.jsonl", 120, 1);
  const second = file("anonymous-b.jsonl", 130, 2);
  assert.deepEqual(
    Array.from(mergeFiles([first], [second, first], false), fileKey),
    [fileKey(first), fileKey(second)],
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

test("interface exposes explicit add and replace controls", () => {
  assert.match(html, /for="files">Add session files/);
  assert.match(html, /for="replaceFiles">Replace workspace files/);
  assert.match(html, /readFiles\(event\.target\.files,"add"\)/);
  assert.match(html, /readFiles\(event\.target\.files,"replace"\)/);
  assert.match(html, /readFiles\(event\.dataTransfer\.files,"add"\)/);
  assert.match(html, /id="workspaceStatus" aria-live="polite"/);
});
