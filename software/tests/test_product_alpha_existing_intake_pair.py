from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
sys.path.insert(0, str(EVALUATION_DIR))

import assemble_workspace  # noqa: E402

BUILD_ID = "a" * 64


def session() -> dict[str, object]:
    return {
        "pilot_build_id": BUILD_ID,
        "session_id": "anonymous-001",
        "route_id": "refrigerator-v1",
        "started": True,
        "completed_steps": ["observe", "map", "model", "diagnose", "redesign"],
        "duration_minutes": 24,
        "scores": {
            "mechanism_explanation": 2,
            "model_reasoning": 1,
            "failure_diagnosis": 2,
            "evidence_boundary": 2,
            "redesign_tradeoff": 1,
        },
        "confusion_tags": [],
        "voluntary_continue": True,
        "facilitator_notes": "",
    }


def workspace(root: Path) -> Path:
    cohort = root / "cohort"
    incoming = cohort / "incoming-sessions"
    incoming.mkdir(parents=True)
    (cohort / "verified").mkdir()
    (cohort / "review").mkdir()
    manifest = {
        "contract": "principia-product-alpha-pilot-workspace/0.1",
        "pilot_build_id": BUILD_ID,
        "route_id": "refrigerator-v1",
        "privacy_boundaries": {
            "participant_names_allowed": False,
            "raw_sessions_committed_to_repository": False,
            "repository_output_allowed": False,
        },
        "paths": {
            "incoming_sessions": "incoming-sessions",
            "combined_jsonl": "verified/anonymous-sessions.jsonl",
            "intake_manifest": "verified/intake-manifest.json",
            "review_output_prefix": "review/refrigerator-review",
        },
    }
    (cohort / "workspace.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (incoming / "session-001.jsonl").write_text(
        json.dumps(session(), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return cohort


class ProductAlphaExistingIntakePairTests(unittest.TestCase):
    def test_preflight_verifies_an_existing_valid_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cohort = workspace(Path(directory))
            assemble_workspace.assemble_workspace(cohort)

            report = assemble_workspace.preflight_workspace(cohort)

            self.assertEqual(
                report["verified_outputs_exist"],
                {"combined_jsonl": True, "intake_manifest": True},
            )
            self.assertTrue(report["verified_outputs_match_prediction"])
            self.assertFalse(report["ready_for_default_assembly"])
            self.assertFalse(report["writes_performed"])

    def test_preflight_rejects_combined_only_partial_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cohort = workspace(Path(directory))
            plan = assemble_workspace._build_plan(cohort)
            plan.combined.write_bytes(plan.combined_bytes)

            with self.assertRaisesRegex(
                ValueError,
                "verified intake output pair is incomplete",
            ):
                assemble_workspace.preflight_workspace(cohort)

    def test_preflight_rejects_manifest_only_partial_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cohort = workspace(Path(directory))
            plan = assemble_workspace._build_plan(cohort)
            plan.intake.write_text(
                json.dumps(
                    assemble_workspace._intake_report(plan),
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "verified intake output pair is incomplete",
            ):
                assemble_workspace.preflight_workspace(cohort)

    def test_preflight_rejects_stale_combined_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cohort = workspace(Path(directory))
            assemble_workspace.assemble_workspace(cohort)
            combined = cohort / "verified" / "anonymous-sessions.jsonl"
            combined.write_bytes(combined.read_bytes() + b"\n")

            with self.assertRaisesRegex(
                ValueError,
                "existing combined cohort does not match current raw exports",
            ):
                assemble_workspace.preflight_workspace(cohort)

    def test_preflight_rejects_stale_intake_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cohort = workspace(Path(directory))
            assemble_workspace.assemble_workspace(cohort)
            intake_path = cohort / "verified" / "intake-manifest.json"
            intake = json.loads(intake_path.read_text(encoding="utf-8"))
            intake["roadmap_gate"] = True
            intake_path.write_text(
                json.dumps(intake, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "existing intake manifest does not match current intake prediction",
            ):
                assemble_workspace.preflight_workspace(cohort)


if __name__ == "__main__":
    unittest.main()
