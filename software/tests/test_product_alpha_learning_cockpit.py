from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "software" / "product_alpha" / "index.html"
SCRIPT_PATTERN = re.compile(r"<script>(.*?)</script>", re.DOTALL)


class ProductAlphaLearningCockpitTests(unittest.TestCase):
    def test_source_exposes_guided_progress_and_accessibility_boundaries(self) -> None:
        html = SOURCE.read_text(encoding="utf-8")

        self.assertIn('class="skip-link" href="#heading"', html)
        self.assertIn('id="journeyProgress" max="5"', html)
        self.assertIn('id="progressText"', html)
        self.assertIn('id="prevStep"', html)
        self.assertIn('id="nextStep"', html)
        self.assertIn("Private to this tab", html)
        self.assertIn("No account or upload", html)
        self.assertIn("min-height:2.75rem", html)
        self.assertIn("@media(prefers-reduced-motion:reduce)", html)
        self.assertIn("@media(forced-colors:active)", html)
        self.assertIn("scroll-padding-top:7.5rem", html)
        self.assertNotIn("localStorage", html)
        self.assertNotIn("sessionStorage", html)

    def test_runtime_updates_progress_and_adjacent_step_links(self) -> None:
        html = SOURCE.read_text(encoding="utf-8")
        scripts = SCRIPT_PATTERN.findall(html)
        self.assertEqual(len(scripts), 1)
        learner_script = scripts[0]
        route = {
            "route_id": "refrigerator",
            "title": "Test route",
            "subtitle": "Test subtitle",
            "canonical_sources": [
                {
                    "title": "Source",
                    "path": "source.md",
                    "status": "active",
                    "release_status": "alpha",
                }
            ],
            "atlas": {"references": []},
            "learner_steps": {
                name: {
                    "heading": name.title(),
                    "body": "Body",
                    "prompt": "Prompt",
                }
                for name in ("observe", "map", "model", "diagnose", "redesign")
            },
            "model": {
                "activity_title": "Model",
                "defaults": {},
                "parameters": [],
                "prediction": {
                    "legend": "",
                    "choices": [],
                    "initial_message": "",
                    "ready_message": "",
                    "error": "",
                },
                "equation": "",
                "limitations": [],
                "adapter": "unused",
            },
        }

        harness = rf"""
const assert = require("node:assert/strict");
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
      href: "",
      dataset: {{}},
      onclick: null,
      listeners: {{}},
      attributes: new Map(),
      style: {{}},
      classList: {{
        values: new Set(),
        toggle(name, on) {{
          if (on === undefined) {{
            if (this.values.has(name)) this.values.delete(name);
            else this.values.add(name);
          }} else if (on) this.values.add(name);
          else this.values.delete(name);
        }},
        contains(name) {{ return this.values.has(name); }},
      }},
      content: {{ cloneNode() {{ return {{}}; }} }},
      replaceChildren() {{ this.innerHTML = ""; }},
      append() {{}},
      addEventListener(type, handler) {{ this.listeners[type] = handler; }},
      showModal() {{}},
      focus() {{}},
      setAttribute(name, value) {{
        this.attributes.set(name, String(value));
        if (name === "href") this.href = String(value);
      }},
      removeAttribute(name) {{
        this.attributes.delete(name);
        if (name === "href") this.href = "";
      }},
      getAttribute(name) {{ return this.attributes.get(name) ?? null; }},
      querySelector() {{ return null; }},
    }});
  }}
  return elements.get(selector);
}}
const anchors = ["observe", "map", "model", "diagnose", "redesign"].map(name =>
  Object.assign(element(`a-${{name}}`), {{ dataset: {{ step: name }} }})
);
const routeMarker = {{ content: "refrigerator" }};
global.document = {{
  title: "",
  querySelector(selector) {{
    if (selector === 'meta[name="principia-route"]') return routeMarker;
    return element(selector);
  }},
  querySelectorAll(selector) {{
    if (selector === "[data-step]") return anchors;
    if (selector === 'a[href^="#"]') return anchors;
    return [];
  }},
}};
global.location = {{ hash: "#map", search: "" }};
global.addEventListener = () => {{}};
global.fetch = async () => ({{
  ok: true,
  status: 200,
  json: async () => ({json.dumps(route, ensure_ascii=False, separators=(",", ":"))}),
}});
global.PrincipiaModelAdapters = {{
  thermalResultSummary() {{}},
  getAdapter() {{ throw new Error("not used"); }},
}};
{learner_script}
setTimeout(() => {{
  assert.equal(element("#journeyProgress").value, 2);
  assert.equal(element("#progressText").textContent, "2 of 5");
  assert.equal(element("#prevStep").getAttribute("href"), "#observe");
  assert.equal(element("#nextStep").getAttribute("href"), "#model");
  assert.equal(anchors[1].getAttribute("aria-current"), "step");
  assert.equal(anchors[1].classList.contains("visited"), true);
  process.stdout.write("learning-cockpit-ok");
}}, 0);
"""
        with tempfile.TemporaryDirectory() as directory:
            harness_path = Path(directory) / "learning-cockpit.js"
            harness_path.write_text(harness, encoding="utf-8")
            completed = subprocess.run(
                ["node", str(harness_path)],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.stdout, "learning-cockpit-ok")


if __name__ == "__main__":
    unittest.main()
