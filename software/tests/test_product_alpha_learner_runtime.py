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


class ProductAlphaLearnerRuntimeTests(unittest.TestCase):
    def test_packaged_model_step_renders_finite_prediction(self) -> None:
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
            route = json.loads(
                (output / "data" / "refrigerator.json").read_text(encoding="utf-8")
            )

        self.assertNotIn("points.at(-1).temperature", learner_script)
        self.assertNotIn("points[0].temperature", learner_script)
        self.assertIn("points.at(-1).t", learner_script)
        self.assertIn("points[0].t", learner_script)

        harness = f"""
const assert = require("node:assert/strict");
const routeData = {json.dumps(route, ensure_ascii=False, separators=(',', ':'))};
const elements = new Map();
function element(selector) {{
  if (!elements.has(selector)) {{
    elements.set(selector, {{
      value: "",
      textContent: "",
      innerHTML: "",
      checked: false,
      min: "",
      max: "",
      type: "",
      dataset: {{}},
      onclick: null,
      classList: {{ toggle() {{}} }},
      content: {{ cloneNode() {{ return {{}}; }} }},
      replaceChildren() {{}},
      append() {{}},
      addEventListener() {{}},
      showModal() {{}},
    }});
  }}
  return elements.get(selector);
}}
const inputs = [
  Object.assign(element("input-room"), {{
    dataset: {{ model: "room_temperature_c" }},
    type: "range",
  }}),
  Object.assign(element("input-ua"), {{
    dataset: {{ model: "ua_w_per_k" }},
    type: "range",
  }}),
  Object.assign(element("input-load"), {{
    dataset: {{ model: "load_w" }},
    type: "range",
  }}),
  Object.assign(element("input-cooling"), {{
    dataset: {{ model: "cooling_w" }},
    type: "range",
  }}),
  Object.assign(element("input-on"), {{
    dataset: {{ model: "cooling_on" }},
    type: "checkbox",
  }}),
];
global.document = {{
  querySelector(selector) {{ return element(selector); }},
  querySelectorAll(selector) {{
    if (selector === "[data-model]") return inputs;
    if (selector === "[data-step]") return [];
    return [];
  }},
}};
global.location = {{ hash: "#model", search: "" }};
global.addEventListener = () => {{}};
global.fetch = async () => ({{
  ok: true,
  status: 200,
  json: async () => routeData,
}});
{learner_script}
setTimeout(() => {{
  const result = element("#result").textContent;
  assert.match(
    result,
    /^Prediction: cabinet temperature (falls|rises|stays nearly level) to -?\\d+\\.\\d °C after 180 minutes\\.$/
  );
  assert.notEqual(element("#title").textContent, "Product Alpha could not load");
  process.stdout.write(result);
}}, 0);
"""
        completed = subprocess.run(
            ["node", "-e", harness],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Prediction: cabinet temperature", completed.stdout)


if __name__ == "__main__":
    unittest.main()
