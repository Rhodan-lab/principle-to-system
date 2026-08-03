from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "software" / "product_alpha" / "evaluation" / "summarize.py"
SPEC = importlib.util.spec_from_file_location("product_alpha_evaluation", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
BUILD_ID = "a" * 64


def session(session_id: str, steps: list[str], **overrides):
    value = {
        "pilot_build_id": BUILD_ID,
        "session_id": session_id,
        "route_id": "refrigerator-v1",
        "started": True,
        "completed_steps": steps,
        "duration_minutes": 28,
        "scores": {
            "mechanism_explanation": 2,
            "model_reasoning": 1,
            "failure_diagnosis": 2,
            "evidence_boundary": 1,
            "redesign_tradeoff": 2,
        },
        "confusion_tags": [],
        "voluntary_continue": True,
        "facilitator_notes": "",
    }
    value.update(overrides)
    return value


class ProductAlphaEvaluationTests(unittest.TestCase):
    def test_summary_is_deterministic_and_has_no_observation_threshold(self):
        sessions = [
            session("anonymous-001", MODULE.STEPS, confusion_tags=["model-controls"]),
            session(
                "anonymous-002",
                MODULE.STEPS[:3],
                duration_minutes=20,
                voluntary_continue=False,
                confusion_tags=["model-controls", "evidence-status"],
            ),
        ]
        summary = MODULE.summarize(sessions)
        first = MODULE.render_markdown(summary)
        second = MODULE.render_markdown(MODULE.summarize(sessions))
        self.assertEqual(first, second)
        self.assertEqual(summary["contract"], "principia-product-alpha-pilot-summary/0.4")
        self.assertEqual(summary["pilot_build_id"], BUILD_ID)
        self.assertEqual(summary["evidence_status"], "ready-for-human-review")
        self.assertTrue(summary["cohort_complete"])
        self.assertEqual(summary["minimum_cohort_size"], 0)
        self.assertEqual(summary["observation_mode"], "optional-descriptive")
        self.assertFalse(summary["roadmap_gate"])
        self.assertFalse(summary["decision_authority"])
        self.assertIn(f"Pilot build ID: `{BUILD_ID}`", first)
        self.assertIn("Valid observations: 2 (no minimum count)", first)
        self.assertIn("Completion rate: 50.0%", first)
        self.assertIn("`model-controls`: 2", first)
        self.assertNotIn("`cohort-incomplete`", first)
        self.assertIn("`recurring-confusion:model-controls`", first)

    def test_single_observation_is_ready_for_optional_review(self):
        summary = MODULE.summarize([session("anonymous-001", MODULE.STEPS)])
        self.assertTrue(summary["cohort_complete"])
        self.assertEqual(summary["minimum_cohort_size"], 0)
        self.assertEqual(summary["evidence_status"], "ready-for-human-review")
        self.assertFalse(
            any(signal["code"] == "cohort-incomplete" for signal in summary["revision_signals"])
        )

    def test_load_rejects_personal_data_fields(self):
        value = session("anonymous-001", MODULE.STEPS)
        value["email"] = "not-allowed@example.test"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.jsonl"
            path.write_text(json.dumps(value) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "personal-data fields"):
                MODULE.load_sessions(path)

    def test_load_rejects_duplicate_session_ids(self):
        value = session("anonymous-001", MODULE.STEPS)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.jsonl"
            path.write_text(
                json.dumps(value) + "\n" + json.dumps(value) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate session_id"):
                MODULE.load_sessions(path)

    def test_load_rejects_mixed_build_ids(self):
        first = session("anonymous-001", MODULE.STEPS)
        second = session("anonymous-002", MODULE.STEPS, pilot_build_id="b" * 64)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.jsonl"
            path.write_text(
                json.dumps(first) + "\n" + json.dumps(second) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "does not match the cohort build"):
                MODULE.load_sessions(path)
        with self.assertRaisesRegex(ValueError, "does not match across the cohort"):
            MODULE.summarize([first, second])

    def test_pilot_build_id_must_be_exact_lowercase_sha256(self):
        value = session("anonymous-001", MODULE.STEPS, pilot_build_id="not-a-build-id")
        with self.assertRaisesRegex(ValueError, "64-character lowercase SHA-256"):
            MODULE.validate_session(value, 1)

    def test_session_id_must_be_anonymous(self):
        value = session("learner-001", MODULE.STEPS)
        with self.assertRaisesRegex(ValueError, "anonymous label"):
            MODULE.validate_session(value, 1)

    def test_completed_steps_must_be_ordered_prefix(self):
        value = session("anonymous-001", ["observe", "model"])
        with self.assertRaisesRegex(ValueError, "ordered route prefix"):
            MODULE.validate_session(value, 1)


if __name__ == "__main__":
    unittest.main()
