from __future__ import annotations

import sys
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
        "session_id": "anonymous-deadbeef",
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
        "confusion_tags": ["navigation"],
        "voluntary_continue": True,
        "facilitator_notes": "First line\nSecond line\twith context.",
    }


class ProductAlphaSessionTextBoundaryTests(unittest.TestCase):
    def test_valid_recorder_text_fields_are_accepted(self) -> None:
        session = valid_session()
        self.assertIs(summarize.validate_session(session, 1), session)

    def test_session_id_must_match_recorder_safe_alphabet(self) -> None:
        invalid_ids = (
            "anonymous-",
            "anonymous-person@example.test",
            "anonymous-path/segment",
            "anonymous-space value",
            "anonymous-" + "a" * 111,
        )
        for session_id in invalid_ids:
            with self.subTest(session_id=session_id):
                session = valid_session()
                session["session_id"] = session_id
                with self.assertRaisesRegex(ValueError, "session_id must be an anonymous label"):
                    summarize.validate_session(session, 1)

    def test_duplicate_confusion_tag_is_rejected(self) -> None:
        session = valid_session()
        session["confusion_tags"] = ["navigation", "navigation"]
        with self.assertRaisesRegex(ValueError, "duplicate confusion tag"):
            summarize.validate_session(session, 1)

    def test_noncanonical_confusion_tags_are_rejected(self) -> None:
        invalid_lists = (
            [" navigation"],
            ["navigation "],
            ["navigation\n"],
            ["x" * 81],
            [f"tag-{index}" for index in range(33)],
        )
        for confusion_tags in invalid_lists:
            with self.subTest(confusion_tags=confusion_tags):
                session = valid_session()
                session["confusion_tags"] = confusion_tags
                with self.assertRaises(ValueError):
                    summarize.validate_session(session, 1)

    def test_facilitator_notes_follow_recorder_limit(self) -> None:
        session = valid_session()
        session["facilitator_notes"] = "x" * 1201
        with self.assertRaisesRegex(ValueError, "at most 1200 characters"):
            summarize.validate_session(session, 1)

    def test_facilitator_notes_reject_unsupported_controls(self) -> None:
        for notes in ("private\x00note", "private\rnote", "private\x7fnote"):
            with self.subTest(notes=notes):
                session = valid_session()
                session["facilitator_notes"] = notes
                with self.assertRaisesRegex(ValueError, "unsupported control characters"):
                    summarize.validate_session(session, 1)


if __name__ == "__main__":
    unittest.main()
