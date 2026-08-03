from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
sys.path.insert(0, str(EVALUATION_DIR))

import assemble_workspace  # noqa: E402
import prepare_handoff  # noqa: E402
import prepare_workspace  # noqa: E402
import record_decision  # noqa: E402
import review_workspace  # noqa: E402

BUILD_ID = "d" * 64
ROUTE_ID = "distributed-information-v1"
PRIVATE_NOTE = "Synthetic fixture note that must remain private."


def synthetic_session(index: int) -> dict[str, object]:
    return {
        "pilot_build_id": BUILD_ID,
        "session_id": f"anonymous-synthetic-{index:03d}",
        "route_id": ROUTE_ID,
        "started": True,
        "completed_steps": ["observe", "map", "model", "diagnose", "redesign"],
        "duration_minutes": 24 + index,
        "scores": {
            "mechanism_explanation": 2,
            "model_reasoning": 2,
            "failure_diagnosis": 2,
            "evidence_boundary": 2,
            "redesign_tradeoff": 1,
        },
        "confusion_tags": ["retry-versus-recovery"] if index == 1 else [],
        "voluntary_continue": True,
        "facilitator_notes": PRIVATE_NOTE if index == 1 else "",
    }


class ProductAlphaDistributedEvidenceChainTests(unittest.TestCase):
    def test_synthetic_distributed_chain_preserves_route_and_privacy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "distributed-information-fixture"
            manifest = prepare_workspace.prepare_workspace(
                workspace,
                BUILD_ID,
                route_id=ROUTE_ID,
            )
            self.assertEqual(manifest["route_id"], ROUTE_ID)
            self.assertEqual(
                manifest["paths"]["review_output_prefix"],
                "review/distributed-information-review",
            )
            workspace_readme = (workspace / "README.md").read_text(encoding="utf-8")
            for marker in (
                "review/distributed-information-review.json",
                "review/distributed-information-review.md",
                "review/distributed-information-review-decision.json",
                "review/distributed-information-review-decision.md",
                "review/distributed-information-review-decision-receipt.json",
                "handoff/distributed-information-product-change",
            ):
                self.assertIn(marker, workspace_readme)
            self.assertNotIn("review/refrigerator-review", workspace_readme)

            for index in range(1, 6):
                path = (
                    workspace
                    / "incoming-sessions"
                    / f"synthetic-session-{index:03d}.jsonl"
                )
                path.write_text(
                    json.dumps(synthetic_session(index), sort_keys=True) + "\n",
                    encoding="utf-8",
                )

            preflight = assemble_workspace.preflight_workspace(workspace)
            self.assertEqual(preflight["route_id"], ROUTE_ID)
            self.assertTrue(preflight["cohort_complete"])
            assembled = assemble_workspace.assemble_workspace(workspace)
            self.assertEqual(assembled["route_id"], ROUTE_ID)

            intake_path = workspace / "verified" / "intake-manifest.json"
            intake = json.loads(intake_path.read_text(encoding="utf-8"))
            self.assertEqual(intake["route_id"], ROUTE_ID)

            review_report = review_workspace.prepare_workspace_review(workspace)
            review_json = Path(str(review_report["review_json"]))
            self.assertEqual(
                review_json.name,
                "distributed-information-review.json",
            )
            review_packet = json.loads(review_json.read_text(encoding="utf-8"))
            self.assertEqual(review_packet["route_id"], ROUTE_ID)
            self.assertEqual(
                review_packet["aggregate_summary"]["confusion_counts"],
                {"retry-versus-recovery": 1},
            )

            decision_report = record_decision.record_workspace_decision(
                workspace,
                "revise-current-route",
                "synthetic-test-reviewer",
                "2026-08-03",
                "The deterministic fixture verifies route propagation through the private evidence chain.",
                "Keep the fixture as integration coverage and do not represent it as real learner evidence.",
            )
            self.assertEqual(decision_report["route_id"], ROUTE_ID)
            decision_json = Path(str(decision_report["decision_json"]))
            decision_receipt = Path(str(decision_report["decision_receipt"]))
            self.assertEqual(
                decision_json.name,
                "distributed-information-review-decision.json",
            )
            self.assertEqual(
                json.loads(decision_json.read_text(encoding="utf-8"))["route_id"],
                ROUTE_ID,
            )
            self.assertEqual(
                json.loads(decision_receipt.read_text(encoding="utf-8"))["route_id"],
                ROUTE_ID,
            )
            verified_decision = record_decision.verify_workspace_decision(workspace)
            self.assertEqual(verified_decision["route_id"], ROUTE_ID)

            handoff_prefix = (
                workspace
                / "handoff"
                / "distributed-information-product-change"
            )
            handoff_report = prepare_handoff.write_handoff(
                workspace,
                handoff_prefix,
            )
            self.assertEqual(handoff_report["route_id"], ROUTE_ID)
            handoff_json = Path(str(handoff_report["output_json"]))
            candidate = json.loads(handoff_json.read_text(encoding="utf-8"))
            self.assertEqual(candidate["route_id"], ROUTE_ID)
            self.assertEqual(
                candidate["aggregate_summary"]["confusion_counts"],
                {"retry-versus-recovery": 1},
            )
            raw_candidate = handoff_json.read_text(encoding="utf-8")
            self.assertNotIn(PRIVATE_NOTE, raw_candidate)
            self.assertNotIn("anonymous-synthetic-001", raw_candidate)
            self.assertNotIn(str(workspace), raw_candidate)

            verified_handoff = prepare_handoff.verify_handoff(
                workspace,
                handoff_prefix,
            )
            self.assertEqual(verified_handoff["route_id"], ROUTE_ID)
            self.assertEqual(
                verified_handoff["decision"],
                "repository-handoff-candidate-verified",
            )

    def test_workspace_intake_rejects_route_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "distributed-information-fixture"
            prepare_workspace.prepare_workspace(
                workspace,
                BUILD_ID,
                route_id=ROUTE_ID,
            )
            drifted = synthetic_session(1)
            drifted["route_id"] = "refrigerator-v1"
            (
                workspace
                / "incoming-sessions"
                / "synthetic-session-001.jsonl"
            ).write_text(
                json.dumps(drifted, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "does not match expected route"):
                assemble_workspace.preflight_workspace(workspace)
            self.assertEqual(list((workspace / "verified").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
