from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
sys.path.insert(0, str(EVALUATION_DIR))

import prepare_handoff  # noqa: E402


class ProductAlphaHandoffAuthorityCopyTests(unittest.TestCase):
    def test_no_signal_copy_keeps_internal_review_authoritative(self) -> None:
        candidate: dict[str, object] = {
            "contract": prepare_handoff.CONTRACT,
            "pilot_build_id": "a" * 64,
            "route_id": "refrigerator-v1",
            "evidence_status": "ready-for-human-review",
            "sessions": 1,
            "primary_action": "record-observation-context",
            "planning_review_action_selected": False,
            "aggregate_summary": {
                "started": 1,
                "finished": 1,
                "completion_rate": 1.0,
                "average_duration_minutes": 20.0,
                "score_averages": {
                    "mechanism_explanation": 2.0,
                    "model_reasoning": 2.0,
                    "failure_diagnosis": 2.0,
                    "evidence_boundary": 2.0,
                    "redesign_tradeoff": 2.0,
                },
                "confusion_counts": {},
                "voluntary_continue": {
                    "yes": 1,
                    "no": 0,
                    "unknown": 0,
                    "yes_rate_among_answered": 1.0,
                },
                "revision_signals": [],
            },
            "evidence_binding": {
                "decision_receipt_sha256": "b" * 64,
                "review_json_sha256": "c" * 64,
                "intake_manifest_sha256": "d" * 64,
                "source_records_sha256": "e" * 64,
            },
            "boundaries": {},
        }

        markdown = prepare_handoff.render_markdown(candidate)

        self.assertIn(
            "internal multi-perspective review remains the product decision authority",
            markdown,
        )
        self.assertNotIn("human action remains the decision authority", markdown)
        self.assertIn("de-identified advisory context", markdown)


if __name__ == "__main__":
    unittest.main()
