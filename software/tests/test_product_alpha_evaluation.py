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


def session(session_id: str, steps: list[str], **overrides):
    value = {
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
    def test_summary_is_deterministic(self):
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
        first = MODULE.render_markdown(MODULE.summarize(sessions))
        second = MODULE.render_markdown(MODULE.summarize(sessions))
        self.assertEqual(first, second)
        self.assertIn("Completion rate: 50.0%", first)
        self.assertIn("`model-controls`: 2", first)

    def test_load_rejects_personal_data_fields(self):
        value = session("anonymous-001", MODULE.STEPS)
        value["email"] = "not-allowed@example.test"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.jsonl"
            path.write_text(json.dumps(value) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "personal-data fields"):
                MODULE.load_sessions(path)

    def test_completed_steps_must_be_ordered_prefix(self):
        value = session("anonymous-001", ["observe", "model"])
        with self.assertRaisesRegex(ValueError, "ordered route prefix"):
            MODULE.validate_session(value, 1)


if __name__ == "__main__":
    unittest.main()
