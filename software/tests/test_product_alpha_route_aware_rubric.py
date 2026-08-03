from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_PATH = REPO_ROOT / "software" / "product_alpha" / "build.py"
SPEC = importlib.util.spec_from_file_location("product_alpha_build_route_rubric", BUILD_PATH)
assert SPEC and SPEC.loader
build_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_module)


class ProductAlphaRouteAwareRubricTests(unittest.TestCase):
    def test_route_configs_bind_matching_rubrics(self) -> None:
        expectations = {
            "refrigerator": (
                "refrigerator-v1",
                "software/product_alpha/evaluation/rubric.json",
            ),
            "distributed-information": (
                "distributed-information-v1",
                "software/product_alpha/evaluation/rubrics/distributed-information-v1.json",
            ),
        }
        for software_route, (evidence_route, rubric_path) in expectations.items():
            with self.subTest(route=software_route):
                config = json.loads(
                    (
                        REPO_ROOT
                        / "software"
                        / "product_alpha"
                        / "routes"
                        / f"{software_route}.json"
                    ).read_text(encoding="utf-8")
                )
                self.assertEqual(config["evaluation"]["rubric"], rubric_path)
                rubric = json.loads((REPO_ROOT / rubric_path).read_text(encoding="utf-8"))
                self.assertEqual(rubric["route_id"], evidence_route)
                self.assertEqual(
                    sorted(rubric["measures"]),
                    [
                        "evidence_boundary",
                        "failure_diagnosis",
                        "mechanism_explanation",
                        "model_reasoning",
                        "redesign_tradeoff",
                    ],
                )

    def test_both_packages_bind_rubric_and_session_template_to_route(self) -> None:
        expected = {
            "refrigerator": "refrigerator-v1",
            "distributed-information": "distributed-information-v1",
        }
        for software_route, evidence_route in expected.items():
            with self.subTest(route=software_route), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                build_module.build(REPO_ROOT, output, software_route)
                rubric = json.loads(
                    (output / "evaluation" / "rubric.json").read_text(encoding="utf-8")
                )
                template = json.loads(
                    (output / "evaluation" / "session-template.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(rubric["route_id"], evidence_route)
                self.assertEqual(template["route_id"], evidence_route)
                prompts = " ".join(
                    str(item).lower()
                    for measure in rubric["measures"].values()
                    for item in measure.values()
                )
                if software_route == "refrigerator":
                    self.assertIn("refrigerator", prompts)
                    self.assertIn("compressor", prompts)
                else:
                    self.assertIn("retry", prompts)
                    self.assertIn("queue", prompts)
                    self.assertNotIn("refrigerator", prompts)
                    self.assertNotIn("compressor", prompts)
                    self.assertNotIn("cabinet temperature", prompts)

    def test_packaging_rejects_a_rubric_for_the_wrong_route(self) -> None:
        refrigerator_rubric = (
            REPO_ROOT / "software" / "product_alpha" / "evaluation" / "rubric.json"
        ).read_bytes()
        with self.assertRaisesRegex(ValueError, "rubric route_id"):
            build_module.prepare_static_asset(
                "evaluation/rubric.json",
                refrigerator_rubric,
                "distributed-information",
            )


if __name__ == "__main__":
    unittest.main()
