from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
sys.path.insert(0, str(EVALUATION_DIR))

import summarize  # noqa: E402

BUILD_ID = "a" * 64


def valid_session() -> dict[str, object]:
    return {
        "pilot_build_id": BUILD_ID,
        "session_id": "anonymous-001",
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


def load_raw(raw: str) -> list[dict[str, object]]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "sessions.jsonl"
        path.write_text(raw + "\n", encoding="utf-8")
        return summarize.load_sessions(path)


class ProductAlphaStrictSessionJsonTests(unittest.TestCase):
    def test_valid_recorder_compatible_session_still_loads(self) -> None:
        session = valid_session()
        loaded = load_raw(json.dumps(session, sort_keys=True))
        self.assertEqual(loaded, [session])

    def test_unknown_session_field_is_rejected(self) -> None:
        session = valid_session()
        session["participant_email"] = "private@example.test"
        with self.assertRaisesRegex(ValueError, "unsupported session fields"):
            summarize.validate_session(session, 1)

    def test_missing_session_field_is_rejected(self) -> None:
        session = valid_session()
        del session["facilitator_notes"]
        with self.assertRaisesRegex(ValueError, "missing session fields"):
            summarize.validate_session(session, 1)

    def test_duplicate_top_level_key_is_rejected(self) -> None:
        raw = json.dumps(valid_session(), separators=(",", ":"))
        raw = raw[:-1] + ',"session_id":"anonymous-002"}'
        with self.assertRaisesRegex(ValueError, "duplicate JSON key 'session_id'"):
            load_raw(raw)

    def test_duplicate_nested_score_key_is_rejected(self) -> None:
        raw = json.dumps(valid_session(), separators=(",", ":"))
        marker = '"scores":{'
        replacement = marker + '"mechanism_explanation":0,'
        raw = raw.replace(marker, replacement, 1)
        with self.assertRaisesRegex(
            ValueError,
            "duplicate JSON key 'mechanism_explanation'",
        ):
            load_raw(raw)

    def test_nan_duration_is_rejected_during_decode(self) -> None:
        raw = json.dumps(valid_session(), separators=(",", ":"))
        raw = raw.replace('"duration_minutes":24', '"duration_minutes":NaN')
        with self.assertRaisesRegex(ValueError, "unsupported non-finite number"):
            load_raw(raw)

    def test_overflow_duration_is_rejected_as_non_finite(self) -> None:
        raw = json.dumps(valid_session(), separators=(",", ":"))
        raw = raw.replace('"duration_minutes":24', '"duration_minutes":1e309')
        with self.assertRaisesRegex(ValueError, "duration_minutes must be finite"):
            load_raw(raw)


if __name__ == "__main__":
    unittest.main()
