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


class ProductAlphaLoadingRuntimeTests(unittest.TestCase):
    def test_early_navigation_waits_for_route_and_uses_latest_hash(self) -> None:
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

        self.assertIn(
            'id="evidence" type="button" disabled aria-busy="true"', html
        )
        self.assertIn("function step(name){if(!route)return;", learner_script)
        loading_marker = 'applyLearnerAvailability("loading")'
        ready_marker = 'applyLearnerAvailability("ready")'
        fetch_marker = 'await fetch("data/refrigerator.json"'
        step_marker = "step(order.includes(location.hash.slice(1))"
        self.assertIn(loading_marker, learner_script)
        self.assertIn(ready_marker, learner_script)
        self.assertLess(
            learner_script.index(loading_marker), learner_script.index(fetch_marker)
        )
        ready_index = learner_script.index(ready_marker)
        self.assertLess(ready_index, learner_script.index(step_marker, ready_index))

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
      disabled: false,
      min: "",
      max: "",
      type: "",
      dataset: {{}},
      onclick: null,
      attributes: new Map(),
      classList: {{ toggle() {{}} }},
      content: {{ cloneNode() {{ return {{}}; }} }},
      replaceChildren() {{ this.innerHTML = ""; }},
      append() {{}},
      addEventListener() {{}},
      showModal() {{}},
      setAttribute(name, value) {{ this.attributes.set(name, String(value)); }},
      removeAttribute(name) {{ this.attributes.delete(name); }},
      getAttribute(name) {{ return this.attributes.get(name) ?? null; }},
    }});
  }}
  return elements.get(selector);
}}
const evidenceButton = element("#evidence");
evidenceButton.disabled = true;
evidenceButton.setAttribute("aria-busy", "true");
element("#title").textContent = "Loading route…";
const events = {{}};
global.document = {{
  querySelector(selector) {{ return element(selector); }},
  querySelectorAll(selector) {{
    if (selector === "[data-step]") return [];
    return [];
  }},
}};
global.location = {{ hash: "#observe", search: "" }};
global.addEventListener = (type, handler) => {{ events[type] = handler; }};
let releaseFetch;
global.fetch = async () => new Promise(resolve => {{
  releaseFetch = () => resolve({{
    ok: true,
    status: 200,
    json: async () => routeData,
  }});
}});
{learner_script}
assert.equal(typeof events.hashchange, "function");
assert.equal(evidenceButton.disabled, true);
assert.equal(evidenceButton.getAttribute("aria-busy"), "true");

location.hash = "#map";
assert.doesNotThrow(() => events.hashchange());
location.hash = "#redesign";
assert.doesNotThrow(() => events.hashchange());
assert.equal(element("#heading").textContent, "");
assert.equal(element("#title").textContent, "Loading route…");

releaseFetch();
setTimeout(() => {{
  assert.equal(
    element("#heading").textContent,
    routeData.learner_steps.redesign.heading
  );
  assert.equal(
    element("#prompt").textContent,
    routeData.learner_steps.redesign.prompt
  );
  assert.equal(evidenceButton.disabled, false);
  assert.equal(evidenceButton.getAttribute("aria-busy"), null);
  assert.notEqual(element("#title").textContent, "Product Alpha could not load");
  process.stdout.write(element("#heading").textContent);
}}, 0);
"""
        completed = subprocess.run(
            ["node", "-e", harness],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.stdout, route["learner_steps"]["redesign"]["heading"])


if __name__ == "__main__":
    unittest.main()
