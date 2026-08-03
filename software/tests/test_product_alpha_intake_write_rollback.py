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


class FailingWriteContext:
    def __init__(self, stream: object, message: str) -> None:
        self.stream = stream
        self.message = message

    def __enter__(self) -> FailingWriteContext:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.stream.close()

    def write(self, value: object) -> int:
        prefix = value[: max(1, len(value) // 3)]
        self.stream.write(prefix)
        self.stream.flush()
        raise OSError(self.message)


class ProductAlphaIntakeWriteRollbackTests(unittest.TestCase):
    def _assert_failure_rolls_back(self, failing_output: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cohort = workspace(Path(directory))
            plan = assemble_workspace._build_plan(cohort)
            target = plan.combined if failing_output == "combined" else plan.intake
            real_open = Path.open

            def controlled_open(path: Path, *args: object, **kwargs: object) -> object:
                stream = real_open(path, *args, **kwargs)
                if path == target:
                    return FailingWriteContext(
                        stream,
                        f"simulated {failing_output} write failure",
                    )
                return stream

            with mock.patch.object(Path, "open", new=controlled_open):
                with self.assertRaisesRegex(
                    OSError,
                    f"simulated {failing_output} write failure",
                ):
                    assemble_workspace.assemble_workspace(cohort)

            self.assertFalse(assemble_workspace._path_present(plan.combined))
            self.assertFalse(assemble_workspace._path_present(plan.intake))
            self.assertEqual(list((cohort / "verified").iterdir()), [])

            report = assemble_workspace.assemble_workspace(cohort)
            self.assertEqual(report["sessions"], 1)
            self.assertTrue(plan.combined.is_file())
            self.assertTrue(plan.intake.is_file())

    def test_combined_write_failure_removes_partial_pair(self) -> None:
        self._assert_failure_rolls_back("combined")

    def test_intake_write_failure_removes_partial_pair(self) -> None:
        self._assert_failure_rolls_back("intake")


if __name__ == "__main__":
    unittest.main()
