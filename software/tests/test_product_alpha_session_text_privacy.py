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
        "facilitator_notes": "Queue latency increased after the retry burst.",
    }


class ProductAlphaSessionTextPrivacyTests(unittest.TestCase):
    def test_ordinary_technical_note_remains_valid(self) -> None:
        session = valid_session()
        self.assertIs(summarize.validate_session(session, 1), session)

    def test_email_in_notes_is_rejected(self) -> None:
        session = valid_session()
        session["facilitator_notes"] = "Follow up with learner@example.test"
        with self.assertRaisesRegex(ValueError, "facilitator_notes contains possible personal data"):
            summarize.validate_session(session, 1)

    def test_labeled_identity_in_notes_is_rejected(self) -> None:
        session = valid_session()
        session["facilitator_notes"] = "Name: private learner"
        with self.assertRaisesRegex(ValueError, "facilitator_notes contains possible personal data"):
            summarize.validate_session(session, 1)

    def test_phone_like_text_in_notes_is_rejected(self) -> None:
        session = valid_session()
        session["facilitator_notes"] = "Call +62 812-3456-7890 after the session"
        with self.assertRaisesRegex(ValueError, "facilitator_notes contains possible personal data"):
            summarize.validate_session(session, 1)

    def test_email_in_custom_confusion_tag_is_rejected(self) -> None:
        session = valid_session()
        session["confusion_tags"] = ["learner@example.test"]
        with self.assertRaisesRegex(ValueError, "confusion tag contains possible personal data"):
            summarize.validate_session(session, 1)

    def test_unlabeled_product_address_language_is_not_a_false_positive(self) -> None:
        session = valid_session()
        session["facilitator_notes"] = "The redesign did not address queue recovery latency."
        self.assertIs(summarize.validate_session(session, 1), session)


if __name__ == "__main__":
    unittest.main()
