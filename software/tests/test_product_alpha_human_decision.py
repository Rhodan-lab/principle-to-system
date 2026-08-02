from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
SCRIPT = EVALUATION_DIR / "record_decision.py"
sys.path.insert(0, str(EVALUATION_DIR))

import assemble_workspace  # noqa: E402
import prepare_review  # noqa: E402
import prepare_workspace  # noqa: E402
import record_decision  # noqa: E402
import review_workspace  # noqa: E402

BUILD_ID = "a" * 64


def session(session_id: str) -> dict[str, object]:
    return {
        "pilot_build_id": BUILD_ID,
        "session_id": session_id,
        "route_id": "refrigerator-v1",
        "started": True,
        "completed_steps": ["observe", "map", "model", "diagnose", "redesign"],
        "duration_minutes": 28,
        "scores": {
            "mechanism_explanation": 2,
            "model_reasoning": 1,
            "failure_diagnosis": 2,
            "evidence_boundary": 2,
            "redesign_tradeoff": 1,
        },
        "confusion_tags": [],
        "voluntary_continue": True,
        "facilitator_notes": "",
    }


def reviewed_workspace(root: Path, count: int = 5) -> Path:
    workspace = root / "cohort"
    prepare_workspace.prepare_workspace(workspace, BUILD_ID)
    for index in range(1, count + 1):
        value = session(f"anonymous-{index:03d}")
        (workspace / "incoming-sessions" / f"session-{index:03d}.jsonl").write_text(
            json.dumps(value, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    assemble_workspace.assemble_workspace(workspace)
    review_workspace.prepare_workspace_review(workspace)
    return workspace


class ProductAlphaHumanDecisionTests(unittest.TestCase):
    def test_records_immutable_decision_bound_to_untouched_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = reviewed_workspace(Path(directory))
            review_json = workspace / "review" / "refrigerator-review.json"
            review_markdown = workspace / "review" / "refrigerator-review.md"
            original_json_sha = hashlib.sha256(review_json.read_bytes()).hexdigest()
            original_markdown_sha = hashlib.sha256(review_markdown.read_bytes()).hexdigest()

            report = record_decision.record_workspace_decision(
                workspace,
                "revise-current-route",
                "facilitator-reviewer",
                "2026-08-02",
                "Repeated model-control confusion requires a bounded route revision.",
                "Review the revised refrigerator route before scheduling a repeat cohort.",
            )

            decision_json = Path(str(report["decision_json"]))
            decision_markdown = Path(str(report["decision_markdown"]))
            record = json.loads(decision_json.read_text(encoding="utf-8"))
            binding = record["review_packet_binding"]
            human = record["human_decision"]

            self.assertEqual(report["decision"], "human-decision-record-created")
            self.assertEqual(human["primary_action"], "revise-current-route")
            self.assertFalse(human["planning_review_action_selected"])
            self.assertEqual(binding["json_sha256"], original_json_sha)
            self.assertEqual(binding["markdown_sha256"], original_markdown_sha)
            self.assertTrue(binding["raw_sources_verified"])
            self.assertFalse(record["boundaries"]["automatic_repository_mutation"])
            self.assertFalse(record["boundaries"]["second_route_authorized"])
            self.assertIn(
                "This record captures a human product action only.",
                decision_markdown.read_text(encoding="utf-8"),
            )
            self.assertEqual(
                report["decision_record_sha256"],
                hashlib.sha256(decision_json.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                hashlib.sha256(review_json.read_bytes()).hexdigest(),
                original_json_sha,
            )

    def test_blocks_planning_advance_for_incomplete_cohort(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = reviewed_workspace(Path(directory), count=2)

            with self.assertRaisesRegex(ValueError, "requires ready-for-human-review"):
                record_decision.record_workspace_decision(
                    workspace,
                    "advance-to-next-product-planning-review",
                    "facilitator-reviewer",
                    "2026-08-02",
                    "The current evidence is intentionally incomplete and cannot advance.",
                    "Run the remaining learner sessions before another decision review.",
                )

            self.assertFalse(
                (workspace / "review" / "refrigerator-review-decision.json").exists()
            )

    def test_rejects_modified_review_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = reviewed_workspace(Path(directory))
            markdown = workspace / "review" / "refrigerator-review.md"
            markdown.write_text(
                markdown.read_text(encoding="utf-8") + "manual edit\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "does not match the untouched packet"):
                record_decision.validate_review_ready(workspace)

    def test_rejects_rebuilt_but_altered_review_packet(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = reviewed_workspace(Path(directory))
            review_json = workspace / "review" / "refrigerator-review.json"
            review_markdown = workspace / "review" / "refrigerator-review.md"
            packet = json.loads(review_json.read_text(encoding="utf-8"))
            packet["aggregate_summary"]["sessions"] = 99
            review_json.write_bytes(prepare_review.canonical_json(packet))
            review_markdown.write_text(
                prepare_review.render_markdown(packet),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "does not match verified workspace evidence",
            ):
                record_decision.validate_review_ready(workspace)

    def test_refuses_to_overwrite_existing_decision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = reviewed_workspace(Path(directory))
            arguments = (
                workspace,
                "hold-current-route",
                "facilitator-reviewer",
                "2026-08-02",
                "The route should remain unchanged until the private notes are resolved.",
                "Revisit the hold after the documented product questions are answered.",
            )
            record_decision.record_workspace_decision(*arguments)

            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                record_decision.record_workspace_decision(*arguments)

    def test_cli_check_verifies_decision_readiness_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = reviewed_workspace(Path(directory))
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "check",
                    "--workspace",
                    str(workspace),
                ],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(completed.stdout)

            self.assertEqual(report["decision"], "human-decision-ready")
            self.assertTrue(report["planning_review_eligible"])
            self.assertFalse(report["decision_outputs_exist"])
            self.assertFalse(
                (workspace / "review" / "refrigerator-review-decision.json").exists()
            )


if __name__ == "__main__":
    unittest.main()
