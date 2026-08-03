from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
SCRIPT = EVALUATION_DIR / "workspace_status.py"
sys.path.insert(0, str(EVALUATION_DIR))

import assemble_workspace  # noqa: E402
import prepare_handoff  # noqa: E402
import prepare_workspace  # noqa: E402
import record_decision  # noqa: E402
import review_workspace  # noqa: E402
import workspace_status  # noqa: E402

BUILD_ID = "a" * 64
DEFAULT_ROUTE_ID = "refrigerator-v1"
DISTRIBUTED_ROUTE_ID = "distributed-information-v1"


def session(
    session_id: str,
    route_id: str = DEFAULT_ROUTE_ID,
) -> dict[str, object]:
    return {
        "pilot_build_id": BUILD_ID,
        "session_id": session_id,
        "route_id": route_id,
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


def create_workspace(
    root: Path,
    route_id: str = DEFAULT_ROUTE_ID,
) -> Path:
    workspace = root / "cohort"
    prepare_workspace.prepare_workspace(
        workspace,
        BUILD_ID,
        route_id=route_id,
    )
    return workspace


def write_sessions(
    workspace: Path,
    count: int,
    route_id: str = DEFAULT_ROUTE_ID,
) -> None:
    for index in range(1, count + 1):
        path = workspace / "incoming-sessions" / f"session-{index:03d}.jsonl"
        path.write_text(
            json.dumps(
                session(f"anonymous-{index:03d}", route_id),
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )


def assemble(
    workspace: Path,
    count: int = 5,
    route_id: str = DEFAULT_ROUTE_ID,
) -> None:
    write_sessions(workspace, count, route_id)
    assemble_workspace.assemble_workspace(workspace)


def review(
    workspace: Path,
    count: int = 5,
    route_id: str = DEFAULT_ROUTE_ID,
) -> None:
    assemble(workspace, count, route_id)
    review_workspace.prepare_workspace_review(workspace)


def decide(
    workspace: Path,
    count: int = 5,
    route_id: str = DEFAULT_ROUTE_ID,
) -> None:
    review(workspace, count, route_id)
    record_decision.record_workspace_decision(
        workspace,
        "revise-current-route",
        "facilitator-reviewer",
        "2026-08-02",
        "Repeated model-control confusion requires a bounded route revision.",
        "Review the revised route before scheduling another optional observation set.",
    )


def handoff(workspace: Path, route_slug: str = "refrigerator") -> Path:
    prefix = workspace / "handoff" / f"{route_slug}-product-change"
    prepare_handoff.write_handoff(workspace, prefix)
    return prefix


def snapshot(workspace: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(workspace)): path.read_bytes()
        for path in sorted(workspace.rglob("*"))
        if path.is_file()
    }


class ProductAlphaWorkspaceStatusTests(unittest.TestCase):
    def test_reports_prepared_empty_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            report = workspace_status.inspect_workspace(workspace)

            self.assertEqual(report["stage"], "prepared")
            self.assertEqual(report["sessions"], 0)
            self.assertEqual(report["evidence_status"], "not-collected")
            self.assertEqual(report["next_action"], "collect-session-records")
            self.assertFalse(report["writes_performed"])
            self.assertIn("launch_workspace.py", str(report["next_command"]))
            self.assertEqual(list((workspace / "verified").iterdir()), [])

    def test_reports_any_valid_observation_set_ready_to_assemble(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 2)
            report = workspace_status.inspect_workspace(workspace)

            self.assertEqual(report["stage"], "ready-to-assemble")
            self.assertEqual(report["sessions"], 2)
            self.assertTrue(report["cohort_complete"])
            self.assertEqual(report["minimum_cohort_size"], 0)
            self.assertEqual(report["next_action"], "assemble-immutable-intake")
            self.assertRegex(str(report["predicted_combined_sha256"]), r"^[0-9a-f]{64}$")
            self.assertEqual(list((workspace / "verified").iterdir()), [])

    def test_reports_complete_collection_ready_to_assemble(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 5)
            report = workspace_status.inspect_workspace(workspace)

            self.assertEqual(report["stage"], "ready-to-assemble")
            self.assertEqual(report["sessions"], 5)
            self.assertTrue(report["cohort_complete"])
            self.assertEqual(report["next_action"], "assemble-immutable-intake")
            self.assertIn("assemble_workspace.py", str(report["next_command"]))
            self.assertEqual(list((workspace / "verified").iterdir()), [])

    def test_reports_verified_intake_before_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            assemble(workspace)
            report = workspace_status.inspect_workspace(workspace)

            self.assertEqual(report["stage"], "intake-verified")
            self.assertEqual(report["sessions"], 5)
            self.assertEqual(report["next_action"], "create-review-packet")
            self.assertIn("review_workspace.py", str(report["next_command"]))
            self.assertEqual(list((workspace / "review").iterdir()), [])

    def test_reports_review_ready_for_human_decision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            review(workspace)
            report = workspace_status.inspect_workspace(workspace)

            self.assertEqual(report["stage"], "review-ready-for-advisory")
            self.assertFalse(report["planning_review_eligible"])
            self.assertEqual(report["next_action"], "record-optional-advisory")
            self.assertIsNone(report["next_command"])
            self.assertIn("<allowed-primary-action>", str(report["next_command_template"]))

    def test_reports_verified_decision_ready_for_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            decide(workspace)
            report = workspace_status.inspect_workspace(workspace)

            self.assertEqual(report["stage"], "advisory-verified")
            self.assertEqual(report["primary_action"], "revise-current-route")
            self.assertEqual(
                report["next_action"],
                "prepare-deidentified-advisory-handoff",
            )
            self.assertEqual(
                report["post_handoff_action"],
                "return-to-internal-multi-perspective-review",
            )
            self.assertRegex(str(report["decision_receipt_sha256"]), r"^[0-9a-f]{64}$")
            self.assertIn("prepare_handoff.py prepare", str(report["next_command"]))
            self.assertIn("prepare_handoff.py check", str(report["validation_command"]))

    def test_distributed_route_uses_route_specific_handoff_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(
                Path(directory),
                route_id=DISTRIBUTED_ROUTE_ID,
            )
            decide(
                workspace,
                count=2,
                route_id=DISTRIBUTED_ROUTE_ID,
            )

            report = workspace_status.inspect_workspace(workspace)
            expected_prefix = (
                workspace / "handoff" / "distributed-information-product-change"
            )

            self.assertEqual(report["route_id"], DISTRIBUTED_ROUTE_ID)
            self.assertEqual(report["handoff_output_prefix"], str(expected_prefix))
            self.assertIn(
                "distributed-information-product-change",
                str(report["next_command"]),
            )
            self.assertNotIn(
                "refrigerator-product-change",
                str(report["next_command"]),
            )

            handoff(workspace, route_slug="distributed-information")
            completed = workspace_status.inspect_workspace(workspace)

            self.assertEqual(completed["stage"], "advisory-handoff-verified")
            self.assertTrue(completed["artifacts"]["handoff_json"])
            self.assertTrue(completed["artifacts"]["handoff_markdown"])
            self.assertIn(
                "distributed-information-product-change",
                str(completed["validation_command"]),
            )

    def test_reports_verified_handoff_and_human_follow_up(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            decide(workspace)
            handoff(workspace)
            report = workspace_status.inspect_workspace(workspace)

            self.assertEqual(report["stage"], "advisory-handoff-verified")
            self.assertEqual(report["primary_action"], "revise-current-route")
            self.assertEqual(report["next_action"], "return-to-internal-multi-perspective-review")
            self.assertRegex(str(report["handoff_candidate_sha256"]), r"^[0-9a-f]{64}$")
            self.assertIn("prepare_handoff.py verify", str(report["validation_command"]))
            self.assertTrue(report["artifacts"]["handoff_json"])
            self.assertTrue(report["artifacts"]["handoff_markdown"])

    def test_rejects_partial_or_out_of_order_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            (workspace / "verified" / "anonymous-sessions.jsonl").write_text(
                "partial\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "verified intake pair is incomplete"):
                workspace_status.inspect_workspace(workspace)

        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            review_path = workspace / "review" / "refrigerator-review.json"
            review_path.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "review packet pair is incomplete"):
                workspace_status.inspect_workspace(workspace)

        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            review(workspace)
            decision_path = workspace / "review" / "refrigerator-review-decision.json"
            decision_path.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "decision artifact trio is incomplete"):
                workspace_status.inspect_workspace(workspace)

        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            decide(workspace)
            handoff_path = workspace / "handoff" / "refrigerator-product-change.json"
            handoff_path.parent.mkdir()
            handoff_path.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "repository handoff pair is incomplete"):
                workspace_status.inspect_workspace(workspace)

        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            prefix = workspace / "handoff" / "refrigerator-product-change"
            prefix.parent.mkdir()
            prefix.with_suffix(".json").write_text("{}\n", encoding="utf-8")
            prefix.with_suffix(".md").write_text("unsafe\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "before immutable intake"):
                workspace_status.inspect_workspace(workspace)

    def test_cli_is_read_only_for_completed_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            decide(workspace)
            handoff(workspace)
            before = snapshot(workspace)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--workspace",
                    str(workspace),
                ],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(completed.stdout)

            self.assertEqual(report["stage"], "advisory-handoff-verified")
            self.assertFalse(report["writes_performed"])
            self.assertEqual(snapshot(workspace), before)


if __name__ == "__main__":
    unittest.main()
