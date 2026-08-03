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
    session = {
        "pilot_build_id": BUILD_ID,
        "session_id": "anonymous-001",
        "route_id": "refrigerator-v1",
        "started": True,
        "completed_steps": ["observe", "map", "model", "diagnose", "redesign"],
        "duration_minutes": 20,
        "scores": {
            "mechanism_explanation": 2,
            "model_reasoning": 2,
            "failure_diagnosis": 2,
            "evidence_boundary": 2,
            "redesign_tradeoff": 2,
        },
        "confusion_tags": [],
        "voluntary_continue": True,
        "facilitator_notes": "",
    }
    (incoming / "session-001.jsonl").write_text(
        json.dumps(session, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return cohort


def broken_symlink(path: Path) -> None:
    try:
        path.symlink_to(path.parent / "missing-target")
    except OSError as exc:
        raise unittest.SkipTest(f"symlinks unavailable: {exc}") from exc


class ProductAlphaIntakeSymlinkPresenceTests(unittest.TestCase):
    def test_preflight_treats_one_broken_symlink_as_partial_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cohort = workspace(Path(directory))
            combined = cohort / "verified" / "anonymous-sessions.jsonl"
            broken_symlink(combined)

            with self.assertRaisesRegex(
                ValueError,
                "verified intake output pair is incomplete",
            ):
                assemble_workspace.preflight_workspace(cohort)

    def test_preflight_rejects_two_broken_symlinks_as_non_regular_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cohort = workspace(Path(directory))
            combined = cohort / "verified" / "anonymous-sessions.jsonl"
            intake = cohort / "verified" / "intake-manifest.json"
            broken_symlink(combined)
            broken_symlink(intake)

            with self.assertRaisesRegex(
                ValueError,
                "existing combined cohort must be a regular file",
            ):
                assemble_workspace.preflight_workspace(cohort)

    def test_assembly_refuses_broken_symlink_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cohort = workspace(Path(directory))
            combined = cohort / "verified" / "anonymous-sessions.jsonl"
            broken_symlink(combined)

            with self.assertRaisesRegex(
                FileExistsError,
                "combined cohort already exists",
            ):
                assemble_workspace.assemble_workspace(cohort)

            self.assertTrue(combined.is_symlink())
            self.assertFalse(
                (cohort / "verified" / "intake-manifest.json").exists()
            )


if __name__ == "__main__":
    unittest.main()
