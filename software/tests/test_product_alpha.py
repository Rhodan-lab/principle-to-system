from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "product_alpha" / "build.py"
SPEC = importlib.util.spec_from_file_location("product_alpha_build", MODULE_PATH)
assert SPEC and SPEC.loader
build_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = build_module
SPEC.loader.exec_module(build_module)


class ProductAlphaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        source_root = MODULE_PATH.parent
        target_root = self.root / "software" / "product_alpha"
        (target_root / "routes").mkdir(parents=True)
        (target_root / "evaluation").mkdir(parents=True)
        for relative in (
            "routes/refrigerator.json",
            "index.html",
            "model-adapters.js",
            "facilitator.html",
            "pilot-lab.html",
            "evaluation/rubric.json",
            "evaluation/session-template.json",
        ):
            target = target_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((source_root / relative).read_bytes())

        documents = {
            "system-dossiers/refrigerator.md": {
                "title": "The Domestic Refrigerator",
                "sections": {
                    "1. Observable system": "A refrigerator moves thermal energy.",
                    "2. System boundary and environment": "The cabinet and refrigerant loop are inside the boundary.",
                    "3. Inputs, outputs, stores, and flows": "| Type | Example |\n| --- | --- |\n| Input | Work |",
                    "6. Interaction architecture": "```text\nsensor -> controller -> compressor\n```",
                    "7. Quantitative model": "A bounded thermal model.",
                    "9. Failure modes": "- Damaged seal\n- Sensor fault",
                },
            },
            "failure-atlas/feedback-instability.md": {
                "title": "Feedback Instability",
                "sections": {"4. Amplifying mechanism": "Compare observed cycling with the intended control band."},
            },
            "investigations/room-cooling.md": {
                "title": "Room Cooling",
                "sections": {"10. Model revision": "Compare heat transfer models."},
            },
            "design-challenges/passive-cooler.md": {
                "title": "Passive Cooler",
                "sections": {"3. Requirements and success measures": "Design under thermal constraints."},
            },
        }
        for relative, data in documents.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            sections = "\n\n".join(
                f"## {heading}\n\n{body}" for heading, body in data["sections"].items()
            )
            path.write_text(
                f"---\ntitle: \"{data['title']}\"\nstatus: reviewed\nartifact_revision: 1\nrelease_status: draft\n---\n\n# {data['title']}\n\n{sections}\n",
                encoding="utf-8",
            )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_build_is_deterministic(self) -> None:
        first = self.root / "first"
        second = self.root / "second"
        build_module.build(self.root, first)
        build_module.build(self.root, second)
        first_files = sorted(path.relative_to(first) for path in first.rglob("*") if path.is_file())
        second_files = sorted(path.relative_to(second) for path in second.rglob("*") if path.is_file())
        self.assertEqual(first_files, second_files)
        for relative in first_files:
            self.assertEqual((first / relative).read_bytes(), (second / relative).read_bytes())

    def test_build_includes_pilot_lab_and_model_adapters(self) -> None:
        output = self.root / "dist"
        manifest = build_module.build(self.root, output)
        expected = {
            "index.html",
            "model-adapters.js",
            "facilitator.html",
            "pilot-lab.html",
            "evaluation/rubric.json",
            "evaluation/session-template.json",
            "data/refrigerator.json",
        }
        self.assertEqual({item["path"] for item in manifest["files"]}, expected)
        self.assertEqual(manifest["file_count"], 7)
        for relative in expected:
            self.assertTrue((output / relative).is_file(), relative)

    def test_build_normalizes_duplicate_counter_to_additive_increment(self) -> None:
        output = self.root / "dist"
        source = self.root / "software" / "product_alpha" / "pilot-lab.html"
        build_module.build(self.root, output)
        source_bytes = source.read_bytes()
        built_bytes = (output / "pilot-lab.html").read_bytes()
        self.assertEqual(
            source_bytes.count(build_module.PILOT_LAB_DUPLICATE_COUNTER_BUG),
            1,
        )
        self.assertNotIn(
            build_module.PILOT_LAB_DUPLICATE_COUNTER_BUG,
            built_bytes,
        )
        self.assertEqual(
            built_bytes.count(build_module.PILOT_LAB_DUPLICATE_COUNTER_FIX),
            1,
        )

    def test_static_asset_guards_reject_ambiguous_state(self) -> None:
        with self.assertRaisesRegex(ValueError, "route identity must occur exactly once"):
            build_module.prepare_static_asset("pilot-lab.html", b"no counter")
        with self.assertRaisesRegex(ValueError, "route identity must occur exactly once"):
            build_module.prepare_static_asset(
                "pilot-lab.html",
                build_module.PILOT_LAB_DUPLICATE_COUNTER_BUG * 2,
            )
        source_index = (
            self.root / "software" / "product_alpha" / "index.html"
        ).read_bytes()
        packaged = build_module.prepare_static_asset(
            "index.html", source_index, "distributed-information"
        )
        self.assertIn(
            b'<meta name="principia-route" content="distributed-information">',
            packaged,
        )
        with self.assertRaisesRegex(ValueError, "route marker must occur exactly once"):
            build_module.prepare_static_asset("index.html", b"unchanged")
        self.assertEqual(
            build_module.prepare_static_asset("model-adapters.js", b"unchanged"),
            b"unchanged",
        )

    def test_route_contract_and_boundaries(self) -> None:
        output = self.root / "dist"
        build_module.build(self.root, output)
        payload = json.loads((output / "data" / "refrigerator.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["contract"], "principia-product-alpha-route/0.1")
        self.assertEqual(set(payload["learner_steps"]), {"observe", "map", "model", "diagnose", "redesign"})
        self.assertEqual(len(payload["canonical_sources"]), 4)
        self.assertEqual(payload["model"]["adapter"], "thermal-cabinet-v1")
        self.assertFalse(payload["atlas"]["live"])
        self.assertEqual(payload["atlas"]["references"][0]["revision"], 2)
        self.assertFalse(payload["product_boundaries"]["external_network_required"])

    def test_static_assets_have_no_remote_or_persistent_dependencies(self) -> None:
        source_root = self.root / "software" / "product_alpha"
        combined = "\n".join(
            (source_root / name).read_text(encoding="utf-8")
            for name in ("index.html", "model-adapters.js", "facilitator.html", "pilot-lab.html")
        )
        self.assertNotIn("https://", combined)
        self.assertNotIn("http://", combined)
        self.assertNotIn("localStorage", combined)
        self.assertNotIn("sessionStorage", combined)
        self.assertNotIn("XMLHttpRequest", combined)
        self.assertNotIn("navigator.sendBeacon", combined)

    def test_pilot_lab_validates_and_exports_without_upload(self) -> None:
        asset = (self.root / "software" / "product_alpha" / "pilot-lab.html").read_text(encoding="utf-8")
        self.assertIn("FileReader", asset) if "FileReader" in asset else self.assertIn("file.text()", asset)
        self.assertIn("duplicate session_id", asset)
        self.assertIn("cohort-incomplete", asset)
        self.assertIn("recurring-confusion:", asset)
        self.assertIn("application/x-ndjson", asset)
        self.assertIn("product-alpha-pilot-summary.md", asset)
        self.assertIn("Refreshing clears the workspace", asset)


if __name__ == "__main__":
    unittest.main()
