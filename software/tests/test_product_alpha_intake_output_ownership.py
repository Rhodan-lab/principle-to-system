from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
sys.path.insert(0, str(EVALUATION_DIR))

import assemble_workspace  # noqa: E402

BUILD_ID = "a" * 64


def create_workspace(root: Path) -> Path:
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
        "completed_steps": ["observe", "map", "model"],
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


class ProductAlphaIntakeOutputOwnershipTests(unittest.TestCase):
    def test_competing_combined_output_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cohort = create_workspace(Path(directory))
            plan = assemble_workspace._build_plan(cohort)
            real_open = Path.open
            competitor = b"competing combined output\n"
            raced = False

            def race_combined(path: Path, *args: object, **kwargs: object) -> object:
                nonlocal raced
                mode = args[0] if args else kwargs.get("mode", "r")
                if path == plan.combined and mode == "xb" and not raced:
                    raced = True
                    with real_open(path, "wb") as stream:
                        stream.write(competitor)
                return real_open(path, *args, **kwargs)

            with mock.patch.object(Path, "open", new=race_combined):
                with self.assertRaises(FileExistsError):
                    assemble_workspace.assemble_workspace(cohort)

            self.assertEqual(plan.combined.read_bytes(), competitor)
            self.assertFalse(assemble_workspace._path_present(plan.intake))

    def test_competing_intake_output_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cohort = create_workspace(Path(directory))
            plan = assemble_workspace._build_plan(cohort)
            real_open = Path.open
            competitor = "competing intake manifest\n"
            raced = False

            def race_intake(path: Path, *args: object, **kwargs: object) -> object:
                nonlocal raced
                mode = args[0] if args else kwargs.get("mode", "r")
                if path == plan.intake and mode == "x" and not raced:
                    raced = True
                    with real_open(path, "w", encoding="utf-8") as stream:
                        stream.write(competitor)
                return real_open(path, *args, **kwargs)

            with mock.patch.object(Path, "open", new=race_intake):
                with self.assertRaises(FileExistsError):
                    assemble_workspace.assemble_workspace(cohort)

            self.assertFalse(assemble_workspace._path_present(plan.combined))
            self.assertEqual(plan.intake.read_text(encoding="utf-8"), competitor)

    def test_normal_publication_still_creates_verified_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cohort = create_workspace(Path(directory))
            plan = assemble_workspace._build_plan(cohort)

            report = assemble_workspace.assemble_workspace(cohort)

            self.assertEqual(report["sessions"], 1)
            self.assertEqual(plan.combined.read_bytes(), plan.combined_bytes)
            self.assertEqual(
                json.loads(plan.intake.read_text(encoding="utf-8")),
                report,
            )


if __name__ == "__main__":
    unittest.main()
