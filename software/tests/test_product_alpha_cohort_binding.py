from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD_PATH = ROOT / "software" / "product_alpha" / "build.py"
SPEC = importlib.util.spec_from_file_location("product_alpha_cohort_build", BUILD_PATH)
assert SPEC and SPEC.loader
build_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = build_module
SPEC.loader.exec_module(build_module)


class ProductAlphaCohortBindingTests(unittest.TestCase):
    def test_source_and_packaged_tools_bind_build_identity(self) -> None:
        source_pilot_lab = (
            ROOT / "software" / "product_alpha" / "pilot-lab.html"
        ).read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build_module.build(ROOT, output)
            facilitator = (output / "facilitator.html").read_text(encoding="utf-8")
            pilot_lab = (output / "pilot-lab.html").read_text(encoding="utf-8")

        self.assertIn("pilot_build_id:pilotBuildId", facilitator)
        self.assertIn('new URLSearchParams(location.search).get("build_id")', facilitator)
        self.assertIn("Pilot build ID is missing or invalid", facilitator)

        self.assertIn("EXPECTED_BUILD_ID", pilot_lab)
        self.assertIn("pilot_build_id does not match the cohort build", pilot_lab)
        self.assertIn("principia-product-alpha-pilot-summary/0.3", pilot_lab)
        self.assertIn(",q=s=>document.querySelector(s);", source_pilot_lab)
        self.assertNotIn(",c=s=>document.querySelector(s);", source_pilot_lab)
        self.assertIn(",q=s=>document.querySelector(s);", pilot_lab)
        self.assertNotIn(",c=s=>document.querySelector(s);", pilot_lab)

    def test_packaging_transforms_are_idempotent(self) -> None:
        source_root = ROOT / "software" / "product_alpha"
        for relative in ("facilitator.html", "pilot-lab.html"):
            first = build_module.prepare_static_asset(
                relative,
                (source_root / relative).read_bytes(),
            )
            second = build_module.prepare_static_asset(relative, first)
            self.assertEqual(first, second)

    def test_session_template_declares_build_identity(self) -> None:
        template = json.loads(
            (
                ROOT
                / "software"
                / "product_alpha"
                / "evaluation"
                / "session-template.json"
            ).read_text(encoding="utf-8")
        )
        self.assertIn("pilot_build_id", template)
        self.assertIn("64-character-build-id", template["pilot_build_id"])


if __name__ == "__main__":
    unittest.main()
