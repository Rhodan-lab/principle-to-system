from __future__ import annotations

import json
import os
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
    def test_rejects_symlink_without_reading_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "private-sessions.jsonl"
            link = root / "cohort.jsonl"
            target_bytes = encoded_session()
            target.write_bytes(target_bytes)
            link.symlink_to(target)

            with self.assertRaisesRegex(ValueError, "must be a regular file"):
                verify_cohort.read_cohort_input(link)

            self.assertEqual(target.read_bytes(), target_bytes)

    def test_rejects_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "cohort-directory"
            input_path.mkdir()

            with self.assertRaisesRegex(ValueError, "must be a regular file"):
                verify_cohort.read_cohort_input(input_path)

    @unittest.skipUnless(
        getattr(os, "O_NOFOLLOW", 0),
        "platform does not provide O_NOFOLLOW",
    )
    def test_rejects_path_replaced_by_symlink_during_open(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "cohort.jsonl"
            target = root / "private-target.jsonl"
            target_bytes = b"private target must not be read\n"
            input_path.write_bytes(encoded_session())
            target.write_bytes(target_bytes)
            real_open = os.open
            replaced = False

            def replace_then_open(path: Path, flags: int) -> int:
                nonlocal replaced
                if not replaced:
                    replaced = True
                    input_path.unlink()
                    input_path.symlink_to(target)
                return real_open(path, flags)

            with mock.patch.object(
                verify_cohort.os,
                "open",
                side_effect=replace_then_open,
            ):
                with self.assertRaisesRegex(ValueError, "must be a regular file"):
                    verify_cohort.read_cohort_input(input_path)

            self.assertTrue(replaced)
            self.assertEqual(target.read_bytes(), target_bytes)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "platform does not provide FIFOs")
    def test_rejects_fifo_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "cohort.fifo"
            os.mkfifo(input_path)

            with self.assertRaisesRegex(ValueError, "must be a regular file"):
                verify_cohort.read_cohort_input(input_path)

    def test_rejects_oversized_regular_file(self) -> None:
        raw = encoded_session()
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "cohort.jsonl"
            input_path.write_bytes(raw)

            with mock.patch.object(summarize, "MAX_INPUT_BYTES", len(raw) - 1):
                with self.assertRaisesRegex(
                    ValueError,
                    "Product Alpha session limit",
                ):
                    verify_cohort.read_cohort_input(input_path)

    def test_regular_file_uses_descriptor_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "cohort.jsonl"
            input_path.write_bytes(encoded_session())
            real_open = os.open

            with mock.patch.object(
                verify_cohort.os,
                "open",
                wraps=real_open,
            ) as descriptor_open:
                summary = verify_cohort.verify_cohort(input_path, BUILD_ID)

        self.assertEqual(summary["pilot_build_id"], BUILD_ID)
        descriptor_open.assert_called_once()
        flags = descriptor_open.call_args.args[1]
        if getattr(os, "O_NOFOLLOW", 0):
            self.assertTrue(flags & os.O_NOFOLLOW)
        if getattr(os, "O_NONBLOCK", 0):
            self.assertTrue(flags & os.O_NONBLOCK)


if __name__ == "__main__":
    unittest.main()
