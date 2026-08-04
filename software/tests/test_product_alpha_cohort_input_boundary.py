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

import summarize  # noqa: E402
import verify_cohort  # noqa: E402

BUILD_ID = "a" * 64


def encoded_session() -> bytes:
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
    return (
        json.dumps(session, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


class ProductAlphaCohortInputBoundaryTests(unittest.TestCase):
    def test_rejects_symlink_before_reading_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "private-sessions.jsonl"
            link = root / "cohort.jsonl"
            target.write_bytes(encoded_session())
            link.symlink_to(target)

            with mock.patch.object(
                summarize,
                "read_session_input",
                wraps=summarize.read_session_input,
            ) as bounded_read:
                with self.assertRaisesRegex(ValueError, "must be a regular file"):
                    verify_cohort.verify_cohort(link, BUILD_ID)

        bounded_read.assert_not_called()

    def test_rejects_directory_before_reading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "cohort-directory"
            input_path.mkdir()

            with mock.patch.object(
                summarize,
                "read_session_input",
                wraps=summarize.read_session_input,
            ) as bounded_read:
                with self.assertRaisesRegex(ValueError, "must be a regular file"):
                    verify_cohort.verify_cohort(input_path, BUILD_ID)

        bounded_read.assert_not_called()

    def test_regular_file_uses_bounded_reader(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "cohort.jsonl"
            input_path.write_bytes(encoded_session())

            with mock.patch.object(
                summarize,
                "read_session_input",
                wraps=summarize.read_session_input,
            ) as bounded_read:
                summary = verify_cohort.verify_cohort(input_path, BUILD_ID)

        self.assertEqual(summary["pilot_build_id"], BUILD_ID)
        bounded_read.assert_called_once_with(input_path)


if __name__ == "__main__":
    unittest.main()
