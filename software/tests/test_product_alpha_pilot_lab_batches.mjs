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

test("interface exposes explicit add and replace controls", () => {
  assert.match(html, /for="files">Add session files/);
  assert.match(html, /for="replaceFiles">Replace workspace files/);
  assert.match(html, /readFiles\(event\.target\.files,"add"\)/);
  assert.match(html, /readFiles\(event\.target\.files,"replace"\)/);
  assert.match(html, /readFiles\(event\.dataTransfer\.files,"add"\)/);
  assert.match(html, /id="workspaceStatus" aria-live="polite"/);
});
