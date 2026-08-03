#!/usr/bin/env python3
"""Make invalid Product Alpha recorder build identity fail closed at startup."""
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


facilitator = Path("software/product_alpha/facilitator.html")
replace_once(
    facilitator,
    'q("#sessionId").value=anonymousId();if(!BUILD_ID_PATTERN.test(pilotBuildId))setStatus("Pilot build ID is missing. Open this recorder from the launcher URL.","error");[q("#sessionId")',
    'q("#sessionId").value=anonymousId();if(!BUILD_ID_PATTERN.test(pilotBuildId)){applyRecorderAvailability("error");setStatus("Pilot build ID is missing or invalid. Open this recorder from the launcher URL.","error");q("#status").focus();return}[q("#sessionId")',
    "recorder build identity startup guard",
)

tests = Path("software/tests/test_product_alpha_facilitator_capture.mjs")
replace_once(
    tests,
    '  const errorAt = body.indexOf(\'applyRecorderAvailability("error")\');',
    '  const errorAt = body.lastIndexOf(\'applyRecorderAvailability("error")\');',
    "asset failure branch selector",
)

text = tests.read_text(encoding="utf-8")
addition = r'''

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
'''
if 'test("missing or invalid build identity keeps the recorder inert"' in text:
    raise SystemExit("build identity startup test already exists")
tests.write_text(text.rstrip() + addition, encoding="utf-8")
