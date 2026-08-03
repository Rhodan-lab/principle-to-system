from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ALPHA = REPO_ROOT / "software" / "product_alpha"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


route_identity = load_module(
    "route_identity", PRODUCT_ALPHA / "route_identity.py"
)
build_module = load_module("route_aware_build", PRODUCT_ALPHA / "build.py")
summarize = load_module(
    "route_aware_summarize", PRODUCT_ALPHA / "evaluation" / "summarize.py"
)
prepare_workspace = load_module(
    "route_aware_prepare_workspace",
    PRODUCT_ALPHA / "evaluation" / "prepare_workspace.py",
)

BUILD_ID = "a" * 64


def session(route_id: str, label: str = "anonymous-route") -> dict[str, object]:
    return {
        "pilot_build_id": BUILD_ID,
        "session_id": label,
        "route_id": route_id,
        "started": True,
        "completed_steps": ["observe", "map"],
        "duration_minutes": 12,
        "scores": {
            "mechanism_explanation": 1,
            "model_reasoning": 1,
            "failure_diagnosis": 1,
            "evidence_boundary": 1,
            "redesign_tradeoff": 1,
        },
        "confusion_tags": [],
        "voluntary_continue": None,
        "facilitator_notes": "",
    }


class ProductAlphaRouteAwareEvidenceTests(unittest.TestCase):
    def test_both_packages_bind_template_and_pilot_lab_to_the_route(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for software_route, evidence_route in (
                ("refrigerator", "refrigerator-v1"),
                ("distributed-information", "distributed-information-v1"),
            ):
                output = root / software_route
                build_module.build(REPO_ROOT, output, software_route)
                template = json.loads(
                    (output / "evaluation" / "session-template.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(template["route_id"], evidence_route)
                self.assertEqual(
                    template["supported_route_ids"],
                    ["refrigerator-v1", "distributed-information-v1"],
                )
                pilot_lab = (output / "pilot-lab.html").read_text(encoding="utf-8")
                self.assertIn(f'const ROUTE_ID="{evidence_route}"', pilot_lab)
                facilitator = (output / "facilitator.html").read_text(encoding="utf-8")
                self.assertIn("route_id:template.route_id", facilitator)

    def test_session_validation_accepts_both_routes(self) -> None:
        for route_id in route_identity.SUPPORTED_EVIDENCE_ROUTES:
            validated = summarize.validate_session(session(route_id), 1)
            self.assertEqual(validated["route_id"], route_id)

    def test_session_validation_rejects_unknown_and_expected_route_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported Product Alpha evidence route"):
            summarize.validate_session(session("unknown-v1"), 1)
        with self.assertRaisesRegex(ValueError, "does not match expected route"):
            summarize.validate_session(
                session("distributed-information-v1"),
                1,
                "refrigerator-v1",
            )

    def test_summarizer_preserves_route_and_rejects_mixed_route_cohorts(self) -> None:
        information = [
            session("distributed-information-v1", "anonymous-one"),
            session("distributed-information-v1", "anonymous-two"),
        ]
        summary = summarize.summarize(information)
        self.assertEqual(summary["route_id"], "distributed-information-v1")
        with self.assertRaisesRegex(ValueError, "route_id does not match across the cohort"):
            summarize.summarize(
                [
                    session("refrigerator-v1", "anonymous-one"),
                    session("distributed-information-v1", "anonymous-two"),
                ]
            )

    def test_workspace_manifest_binds_route_specific_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository = base / "repository"
            repository.mkdir()
            for route_id, slug in (
                ("refrigerator-v1", "refrigerator"),
                ("distributed-information-v1", "distributed-information"),
            ):
                workspace = base / f"workspace-{slug}"
                manifest = prepare_workspace.prepare_workspace(
                    workspace,
                    BUILD_ID,
                    repo_root=repository,
                    route_id=route_id,
                )
                self.assertEqual(manifest["route_id"], route_id)
                self.assertEqual(
                    manifest["paths"]["review_output_prefix"],
                    f"review/{slug}-review",
                )
                readme = (workspace / "README.md").read_text(encoding="utf-8")
                self.assertIn(f"- Route: `{route_id}`", readme)
                self.assertIn(f"{slug}-product-change", readme)


if __name__ == "__main__":
    unittest.main()
