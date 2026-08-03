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

BUILD_ID = "a" * 64


def session(index: int) -> dict[str, object]:
    return {
        "pilot_build_id": BUILD_ID,
        "session_id": f"anonymous-{index:03d}",
        "route_id": "refrigerator-v1",
        "started": True,
        "completed_steps": ["observe", "map", "model", "diagnose", "redesign"],
        "duration_minutes": 24,
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


def record(value: dict[str, object]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


class ProductAlphaSessionInputLimitTests(unittest.TestCase):
    def test_small_valid_input_still_loads(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.jsonl"
            path.write_bytes(record(session(1)))
            self.assertEqual(summarize.load_sessions(path), [session(1)])

    def test_input_byte_limit_is_enforced_before_decode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.jsonl"
            path.write_bytes(b"x" * 65)
            with mock.patch.object(summarize, "MAX_INPUT_BYTES", 64):
                with self.assertRaisesRegex(ValueError, "64-byte"):
                    summarize.load_sessions(path)

    def test_non_utf8_input_has_a_stable_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.jsonl"
            path.write_bytes(b"\xff\xfe\n")
            with self.assertRaisesRegex(ValueError, "input must be UTF-8"):
                summarize.load_sessions(path)

    def test_nonempty_record_limit_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.jsonl"
            path.write_bytes(b"\n" + record(session(1)) + b"\n" + record(session(2)))
            with mock.patch.object(summarize, "MAX_SESSION_RECORDS", 1):
                with self.assertRaisesRegex(ValueError, "more than 1"):
                    summarize.load_sessions(path)

    def test_limit_allows_exactly_the_configured_record_count(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.jsonl"
            path.write_bytes(record(session(1)) + record(session(2)))
            with mock.patch.object(summarize, "MAX_SESSION_RECORDS", 2):
                loaded = summarize.load_sessions(path)
            self.assertEqual([value["session_id"] for value in loaded], [
                "anonymous-001",
                "anonymous-002",
            ])


if __name__ == "__main__":
    unittest.main()
