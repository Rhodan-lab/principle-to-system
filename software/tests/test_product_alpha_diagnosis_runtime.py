from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = REPO_ROOT / "software" / "product_alpha" / "build.py"
SCRIPT_PATTERN = re.compile(r"<script>(.*?)</script>", re.DOTALL)


class ProductAlphaDiagnosisRuntimeTests(unittest.TestCase):
    def test_answer_changes_clear_stale_diagnosis_feedback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dist"
            subprocess.run(
                [
                    sys.executable,
                    str(BUILD_SCRIPT),
                    "build",
                    "--root",
                    str(REPO_ROOT),
                    "--output",
                    str(output),
                ],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            html = (output / "index.html").read_text(encoding="utf-8")
            scripts = SCRIPT_PATTERN.findall(html)
            self.assertEqual(len(scripts), 1)
            learner_script = scripts[0]
            adapter_script = (output / "model-adapters.js").read_text(encoding="utf-8")
            route = json.loads(
                (output / "data" / "refrigerator.json").read_text(encoding="utf-8")
            )

        self.assertIn('options.addEventListener("change"', learner_script)

        harness = rf"""
const assert = require("node:assert/strict");
{adapter_script}
const routeData = {json.dumps(route, ensure_ascii=False, separators=(',', ':'))};
const elements = new Map();
let selectedDiagnosis = null;

function element(selector) {{
  if (!elements.has(selector)) {{
    elements.set(selector, {{
      value: "",
      textContent: "",
      innerHTML: "",
      disabled: false,
      dataset: {{}},
      onclick: null,
      listeners: {{}},
      attributes: new Map(),
      classList: {{ toggle() {{}} }},
      content: {{ cloneNode() {{ return {{}}; }} }},
      replaceChildren() {{ this.innerHTML = ""; }},
      append() {{}},
      addEventListener(type, handler) {{ this.listeners[type] = handler; }},
      showModal() {{}},
      setAttribute(name, value) {{ this.attributes.set(name, String(value)); }},
      removeAttribute(name) {{ this.attributes.delete(name); }},
    }});
  }}
  return elements.get(selector);
}}

const routeMarker = {{ content: "refrigerator" }};
global.document = {{
  querySelector(selector) {{
    if (selector === 'meta[name="principia-route"]') return routeMarker;
    if (selector === 'input[name="d"]:checked') return selectedDiagnosis;
    return element(selector);
  }},
  querySelectorAll(selector) {{
    if (selector === "[data-step]") return [];
    if (selector === "[data-model]") return [];
    if (selector === '[name="model-prediction"]') return [];
    return [];
  }},
}};
global.location = {{ hash: "#diagnose", search: "" }};
global.addEventListener = () => {{}};
global.fetch = async () => ({{
  ok: true,
  status: 200,
  json: async () => routeData,
}});

{learner_script}

setTimeout(() => {{
  const challenge = routeData.learner_steps.diagnose.challenge;
  const options = element("#options");
  const feedback = element("#feedback");
  const check = element("#check");
  const wrongIndex = (challenge.correct_index + 1) % challenge.options.length;

  assert.equal(feedback.textContent, "");

  check.onclick();
  assert.equal(feedback.textContent, "Choose a diagnosis first.");

  selectedDiagnosis = {{ value: String(wrongIndex) }};
  options.listeners.change();
  assert.equal(feedback.textContent, "");
  check.onclick();
  assert.match(feedback.textContent, /^Not yet\./);

  selectedDiagnosis = {{ value: String(challenge.correct_index) }};
  options.listeners.change();
  assert.equal(feedback.textContent, "");
  check.onclick();
  assert.match(feedback.textContent, /^Correct\./);

  selectedDiagnosis = {{ value: String(wrongIndex) }};
  options.listeners.change();
  assert.equal(feedback.textContent, "");
  check.onclick();
  assert.match(feedback.textContent, /^Not yet\./);

  assert.notEqual(element("#title").textContent, "Product Alpha could not load");
  process.stdout.write("diagnosis-feedback-invalidated");
}}, 0);
"""
        completed = subprocess.run(
            ["node", "-e", harness],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("diagnosis-feedback-invalidated", completed.stdout)


if __name__ == "__main__":
    unittest.main()
