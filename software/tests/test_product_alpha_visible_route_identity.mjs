import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import vm from "node:vm";

const learnerHtml = fs.readFileSync("software/product_alpha/index.html", "utf8");
const facilitatorHtml = fs.readFileSync(
  "software/product_alpha/facilitator.html",
  "utf8",
);
const match = facilitatorHtml.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match, "facilitator page must contain one script");
const sandbox = { module: { exports: {} }, exports: {} };
vm.runInNewContext(match[1], sandbox, { filename: "facilitator.html" });
const { routeIdentityLabel, assertRecorderRouteIdentity } = sandbox.module.exports;

function plain(value) {
  return JSON.parse(JSON.stringify(value));
}

test("learner and recorder visibly identify Product Alpha 0.2", () => {
  assert.match(learnerHtml, /<small>Product Alpha 0\.2<\/small>/);
  assert.match(facilitatorHtml, /Product Alpha 0\.2/);
  assert.doesNotMatch(learnerHtml, /Product Alpha 0\.1/);
  assert.doesNotMatch(facilitatorHtml, /Product Alpha 0\.1/);
});

test("recorder exposes an accessible packaged-route status", () => {
  assert.match(
    facilitatorHtml,
    /id="routeIdentity" role="status" aria-live="polite" aria-atomic="true"/,
  );
  assert.match(facilitatorHtml, /Loading packaged route…/);
  assert.match(facilitatorHtml, /Bound route:/);
  assert.match(facilitatorHtml, /Route identity unavailable\./);
});

test("known evidence routes have stable human labels", () => {
  assert.equal(routeIdentityLabel("refrigerator-v1"), "Refrigerator");
  assert.equal(
    routeIdentityLabel("distributed-information-v1"),
    "Distributed information",
  );
  assert.throws(
    () => routeIdentityLabel("unknown-v1"),
    /unsupported recorder route identity/,
  );
});

test("recorder route assets must match before controls become ready", () => {
  const template = {
    route_id: "distributed-information-v1",
    supported_route_ids: ["refrigerator-v1", "distributed-information-v1"],
  };
  const rubric = { route_id: "distributed-information-v1" };
  assert.equal(
    assertRecorderRouteIdentity(rubric, template),
    "distributed-information-v1",
  );
  assert.throws(
    () =>
      assertRecorderRouteIdentity(
        { route_id: "refrigerator-v1" },
        template,
      ),
    /recorder route assets do not match/,
  );
  assert.throws(
    () =>
      assertRecorderRouteIdentity(
        rubric,
        plain({ ...template, route_id: "unknown-v1" }),
      ),
    /unsupported recorder route identity/,
  );

  const source = facilitatorHtml.match(
    /async function init\(\)\{([\s\S]*?)\}\nif\(typeof document/,
  );
  assert.ok(source, "init source must be testable");
  const body = source[1];
  const fetchAt = body.indexOf("await Promise.all(");
  const assertAt = body.indexOf("assertRecorderRouteIdentity(");
  const routeAt = body.indexOf('q("#routeIdentity").textContent=`Bound route:');
  const readyAt = body.indexOf('applyRecorderAvailability("ready")');

  assert.ok(fetchAt < assertAt, "assets must load before identity validation");
  assert.ok(assertAt < routeAt, "identity must validate before it is displayed");
  assert.ok(routeAt < readyAt, "route identity must be visible before controls unlock");
});
