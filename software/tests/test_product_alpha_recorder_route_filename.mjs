import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import vm from "node:vm";

const html = fs.readFileSync("software/product_alpha/facilitator.html", "utf8");
const match = html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match, "facilitator page must contain one script");
const sandbox = { module: { exports: {} }, exports: {} };
vm.runInNewContext(match[1], sandbox, { filename: "facilitator.html" });
const { recorderExportName } = sandbox.module.exports;

test("recorder export filenames preserve the packaged route", () => {
  assert.equal(
    recorderExportName("refrigerator-v1", "anonymous-a1b2c3d4"),
    "product-alpha-refrigerator-anonymous-a1b2c3d4.jsonl",
  );
  assert.equal(
    recorderExportName(
      "distributed-information-v1",
      "anonymous-session-002",
    ),
    "product-alpha-distributed-information-anonymous-session-002.jsonl",
  );
});

test("recorder filename helper fails closed for unknown routes or invalid labels", () => {
  assert.throws(
    () => recorderExportName("unknown-v1", "anonymous-a1b2c3d4"),
    /unsupported recorder route identity/,
  );
  assert.throws(
    () => recorderExportName("refrigerator-v1", "learner-name"),
    /invalid anonymous session label/,
  );
  assert.throws(
    () => recorderExportName("refrigerator-v1", "anonymous-name.jsonl"),
    /invalid anonymous session label/,
  );
});

test("download handler uses the route-specific filename helper", () => {
  assert.match(
    html,
    /link\.download=recorderExportName\(value\.route_id,value\.session_id\)/,
  );
  assert.doesNotMatch(html, /link\.download=`\$\{value\.session_id\}\.jsonl`/);
  assert.match(
    html,
    /The downloaded filename includes the bound route and anonymous session label\./,
  );
});
