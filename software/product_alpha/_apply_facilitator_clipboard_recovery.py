#!/usr/bin/env python3
"""Apply bounded facilitator clipboard-failure recovery semantics once."""
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
    '<button class="button primary" type="submit">Validate and download JSONL</button>',
    '<button class="button primary" id="download" type="submit">Validate and download JSONL</button>',
    "download control identity",
)
html = replace_once(
    html,
    'catch{cancelCapture(captureState);applyCaptureState();setStatus("Clipboard access is unavailable. Use the download button instead.","error")}',
    'catch{cancelCapture(captureState);applyCaptureState();setStatus("Clipboard access is unavailable. Use the download button instead.","error");q("#download").focus()}',
    "clipboard failure focus recovery",
)
HTML_PATH.write_text(html, encoding="utf-8")

test_text = TEST_PATH.read_text(encoding="utf-8")
addition = r'''

test("clipboard failure restores the download fallback", () => {
  assert.match(html, /id="download" type="submit">Validate and download JSONL<\/button>/);
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
'''
if addition.strip() in test_text:
    raise SystemExit("clipboard recovery test already present")
TEST_PATH.write_text(test_text.rstrip() + addition, encoding="utf-8")
