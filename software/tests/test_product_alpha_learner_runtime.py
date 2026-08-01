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
    def test_packaged_model_requires_prediction_and_invalidates_old_result(self) -> None:
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

        self.assertIn('name="model-prediction"', html)
        self.assertIn('id="runModel"', html)
        self.assertIn('id="modelOutput" hidden', html)
        self.assertIn("points.at(-1).t", learner_script)
        self.assertIn("points[0].t", learner_script)
        self.assertNotIn("function update()", learner_script)

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
      hidden: false,
      min: "",
      max: "",
      type: "",
      dataset: {{}},
      onclick: null,
      listeners: {{}},
      classList: {{ toggle() {{}} }},
      content: {{ cloneNode() {{ return {{}}; }} }},
      replaceChildren() {{ this.innerHTML = ""; }},
      append() {{}},
      addEventListener(type, handler) {{ this.listeners[type] = handler; }},
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
const predictions = ["falls", "rises", "stays nearly level"].map((value, index) =>
  Object.assign(element(`prediction-${{index}}`), {{
    type: "radio",
    value,
    checked: false,
  }})
);
global.document = {{
  querySelector(selector) {{
    if (selector === 'input[name="model-prediction"]:checked') {{
      return predictions.find(item => item.checked) || null;
    }}
    return element(selector);
  }},
  querySelectorAll(selector) {{
    if (selector === "[data-model]") return inputs;
    if (selector === '[name="model-prediction"]') return predictions;
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
  const output = element("#modelOutput");
  const run = element("#runModel");
  assert.equal(output.hidden, true);
  assert.equal(element("#result").textContent, "");
  assert.match(element("#modelFeedback").textContent, /Choose a direction/);

  run.onclick();
  assert.equal(output.hidden, true);
  assert.match(element("#modelFeedback").textContent, /before running the model/);

  predictions[0].checked = true;
  run.onclick();
  const rendered = element("#result").textContent;
  assert.match(
    rendered,
    /^Model result: cabinet temperature (falls|rises|stays nearly level) to -?\\d+\\.\\d °C after 180 minutes\\.$/
  );
  assert.equal(output.hidden, false);
  assert.match(
    element("#modelFeedback").textContent,
    /prediction (matched|differed)/i
  );

  inputs[0].value = String(Number(inputs[0].value) + 1);
  inputs[0].listeners.input();
  assert.equal(output.hidden, true);
  assert.equal(element("#result").textContent, "");
  assert.equal(predictions.some(item => item.checked), false);
  assert.notEqual(element("#title").textContent, "Product Alpha could not load");
  process.stdout.write(rendered);
}}, 0);
"""
        completed = subprocess.run(
            ["node", "-e", harness],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Model result: cabinet temperature", completed.stdout)


if __name__ == "__main__":
    unittest.main()
