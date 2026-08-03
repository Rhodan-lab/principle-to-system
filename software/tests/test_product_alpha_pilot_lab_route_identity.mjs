import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import vm from "node:vm";

const html = fs.readFileSync("software/product_alpha/pilot-lab.html", "utf8");
const match = html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match, "Pilot Lab must contain one inline script");
const sandbox = { module: { exports: {} }, exports: {} };
vm.runInNewContext(match[1], sandbox, { filename: "pilot-lab.html" });
const { routeIdentityLabel, pilotLabExportName, buildBoundToolUrl } = sandbox.module.exports;

test("Pilot Lab visibly identifies Product Alpha 0.2 and its route", () => {
  assert.match(html, /Principia Product Alpha 0\.2 — Pilot Lab/);
  assert.match(html, /Product Alpha 0\.2 Pilot Lab/);
  assert.match(
    html,
    /id="routeIdentity" role="status" aria-live="polite" aria-atomic="true"/,
  );
  assert.match(html, /Bound route:/);
  assert.doesNotMatch(html, /Product Alpha 0\.1/);
});

test("Pilot Lab exposes stable labels for both evidence routes", () => {
  assert.equal(routeIdentityLabel("refrigerator-v1"), "Refrigerator");
  assert.equal(
    routeIdentityLabel("distributed-information-v1"),
    "Distributed information",
  );
  assert.throws(
    () => routeIdentityLabel("unknown-v1"),
    /unsupported Pilot Lab route identity/,
  );
});

test("Pilot Lab export names preserve the packaged route", () => {
  assert.equal(
    pilotLabExportName("refrigerator-v1", "summary-markdown"),
    "product-alpha-refrigerator-pilot-summary.md",
  );
  assert.equal(
    pilotLabExportName("distributed-information-v1", "summary-json"),
    "product-alpha-distributed-information-pilot-summary.json",
  );
  assert.equal(
    pilotLabExportName("distributed-information-v1", "sessions-jsonl"),
    "product-alpha-distributed-information-validated-sessions.jsonl",
  );
  assert.throws(
    () => pilotLabExportName("refrigerator-v1", "unknown"),
    /unsupported Pilot Lab export kind/,
  );
});

test("all download handlers use route-specific filenames", () => {
  assert.match(
    html,
    /download\(pilotLabExportName\(ROUTE_ID,"summary-markdown"\),markdown\(state\.summary\)/,
  );
  assert.match(
    html,
    /download\(pilotLabExportName\(ROUTE_ID,"summary-json"\),JSON\.stringify\(state\.summary/,
  );
  assert.match(
    html,
    /download\(pilotLabExportName\(ROUTE_ID,"sessions-jsonl"\),state\.sessions/,
  );
  assert.doesNotMatch(html, /download\("product-alpha-pilot-summary/);
  assert.doesNotMatch(html, /download\("product-alpha-validated-sessions/);
});

test("Pilot Lab recorder navigation preserves launcher build identity", () => {
  const buildId = "a".repeat(64);
  assert.equal(
    buildBoundToolUrl("facilitator.html", buildId),
    `facilitator.html?build_id=${buildId}`,
  );
  assert.throws(
    () => buildBoundToolUrl("facilitator.html", "not-a-build-id"),
    /invalid Pilot build identity/,
  );
  assert.throws(
    () => buildBoundToolUrl("unknown.html", buildId),
    /unsupported Product Alpha tool path/,
  );
  assert.match(
    html,
    /id="recorderLink" href="#" aria-disabled="true" tabindex="-1">Recorder/,
  );
  assert.match(html, /a\[aria-disabled="true"\]\{pointer-events:none;opacity:\.55\}/);
  assert.match(
    html,
    /link\.href=buildBoundToolUrl\("facilitator\.html",buildId\)/,
  );
  assert.match(html, /link\.removeAttribute\("tabindex"\)/);
  assert.match(html, /link\.setAttribute\("tabindex","-1"\)/);
});
