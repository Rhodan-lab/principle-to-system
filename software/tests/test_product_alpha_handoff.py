from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
SCRIPT = EVALUATION_DIR / "prepare_handoff.py"
sys.path.insert(0, str(EVALUATION_DIR))

import assemble_workspace  # noqa: E402
import prepare_handoff  # noqa: E402
import prepare_review  # noqa: E402
import prepare_workspace  # noqa: E402
import record_decision  # noqa: E402
import review_workspace  # noqa: E402

BUILD_ID = "a" * 64
PRIVATE_REVIEWER = "private-reviewer-label"
PRIVATE_RATIONALE = "Private rationale says the bounded route needs revision now."
PRIVATE_CHECKPOINT = "Private checkpoint after facilitator note reconciliation."
PRIVATE_NOTE = "private facilitator observation"
CUSTOM_TAG = "private-custom-confusion-text"


def session(session_id: str, *, custom: bool = False) -> dict[str, object]:
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
        "confusion_tags": [CUSTOM_TAG] if custom else [],
        "voluntary_continue": True,
        "facilitator_notes": PRIVATE_NOTE if custom else "",
    }


def decided_workspace(root: Path, *, count: int = 5) -> Path:
    workspace = root / "cohort"
    prepare_workspace.prepare_workspace(workspace, BUILD_ID)
    for index in range(1, count + 1):
        value = session(f"anonymous-{index:03d}", custom=index == 1)
        (workspace / "incoming-sessions" / f"session-{index:03d}.jsonl").write_text(
            json.dumps(value, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    assemble_workspace.assemble_workspace(
        workspace,
        allow_incomplete=count < 5,
    )
    review_workspace.prepare_workspace_review(workspace)
    record_decision.record_workspace_decision(
        workspace,
        "revise-current-route",
        PRIVATE_REVIEWER,
        "2026-08-02",
        PRIVATE_RATIONALE,
        PRIVATE_CHECKPOINT,
    )
    return workspace


class ProductAlphaHandoffTests(unittest.TestCase):
    def test_candidate_is_deterministic_and_excludes_private_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = decided_workspace(Path(directory))
            first = prepare_handoff.build_handoff_candidate(workspace)
            second = prepare_handoff.build_handoff_candidate(workspace)
            raw = prepare_review.canonical_json(first).decode("utf-8")

            self.assertEqual(first, second)
            self.assertEqual(first["primary_action"], "revise-current-route")
            self.assertEqual(first["sessions"], 5)
            self.assertEqual(first["evidence_status"], "ready-for-human-review")
            self.assertTrue(first["advisory_only"])
            self.assertFalse(first["roadmap_gate"])
            self.assertFalse(first["decision_authority"])
            self.assertFalse(first["planning_review_action_selected"])
            self.assertNotIn(PRIVATE_REVIEWER, raw)
            self.assertNotIn(PRIVATE_RATIONALE, raw)
            self.assertNotIn(PRIVATE_CHECKPOINT, raw)
            self.assertNotIn(PRIVATE_NOTE, raw)
            self.assertNotIn(CUSTOM_TAG, raw)
            self.assertNotIn("anonymous-001", raw)
            self.assertNotIn(str(workspace), raw)
            self.assertIn("other-custom-tag", raw)
            boundaries = first["boundaries"]
            self.assertIsInstance(boundaries, dict)
            self.assertFalse(boundaries["automatic_repository_mutation"])
            self.assertFalse(boundaries["repository_change_authorized"])
            self.assertFalse(boundaries["reviewer_identity_included"])
            self.assertFalse(boundaries["human_rationale_included"])
            self.assertTrue(boundaries["advisory_only"])
            self.assertFalse(boundaries["decision_authority"])

    def test_check_is_read_only_and_reports_candidate_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = decided_workspace(Path(directory))
            prefix = workspace / "handoff" / "repository-candidate"
            before = {
                path.relative_to(workspace): path.read_bytes()
                for path in workspace.rglob("*")
                if path.is_file()
            }

            report = prepare_handoff.check_handoff(workspace, prefix)
            after = {
                path.relative_to(workspace): path.read_bytes()
                for path in workspace.rglob("*")
                if path.is_file()
            }

            self.assertEqual(report["decision"], "repository-handoff-candidate-ready")
            self.assertFalse(report["outputs_exist"])
            self.assertFalse(report["writes_performed"])
            self.assertRegex(str(report["candidate_sha256"]), r"^[0-9a-f]{64}$")
            self.assertEqual(before, after)

    def test_prepare_and_verify_write_canonical_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = decided_workspace(Path(directory))
            prefix = workspace / "handoff" / "repository-candidate"

            created = prepare_handoff.write_handoff(workspace, prefix)
            json_path = Path(str(created["output_json"]))
            markdown_path = Path(str(created["output_markdown"]))
            candidate = json.loads(json_path.read_text(encoding="utf-8"))

            self.assertEqual(
                json_path.read_bytes(),
                prepare_review.canonical_json(candidate),
            )
            self.assertEqual(
                markdown_path.read_text(encoding="utf-8"),
                prepare_handoff.render_markdown(candidate),
            )
            verified = prepare_handoff.verify_handoff(workspace, prefix)
            self.assertEqual(
                verified["decision"],
                "repository-handoff-candidate-verified",
            )
            self.assertFalse(verified["writes_performed"])
            self.assertEqual(
                verified["candidate_sha256"],
                created["candidate_sha256"],
            )

    def test_publish_failure_rolls_back_both_final_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = decided_workspace(Path(directory))
            prefix = workspace / "handoff" / "repository-candidate"
            json_path, markdown_path = prepare_handoff._output_paths(prefix)
            real_publish = prepare_review.publish_exclusive
            calls = 0

            def fail_second_publish(source: Path, destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("forced second publication failure")
                real_publish(source, destination)

            with mock.patch.object(
                prepare_review,
                "publish_exclusive",
                side_effect=fail_second_publish,
            ):
                with self.assertRaisesRegex(OSError, "forced second publication"):
                    prepare_handoff.write_handoff(workspace, prefix)

            self.assertFalse(json_path.exists())
            self.assertFalse(markdown_path.exists())
            self.assertEqual(list(json_path.parent.glob(".*.tmp-*")), [])

    def test_cli_check_and_verify_write_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = decided_workspace(Path(directory))
            prefix = workspace / "handoff" / "repository-candidate"
            prepare_handoff.write_handoff(workspace, prefix)
            before = {
                path.relative_to(workspace): path.read_bytes()
                for path in workspace.rglob("*")
                if path.is_file()
            }

            for command in ("check", "verify"):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        command,
                        "--workspace",
                        str(workspace),
                        "--output-prefix",
                        str(prefix),
                    ],
                    cwd=REPO_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                report = json.loads(completed.stdout)
                self.assertFalse(report.get("writes_performed", False))

            after = {
                path.relative_to(workspace): path.read_bytes()
                for path in workspace.rglob("*")
                if path.is_file()
            }
            self.assertEqual(before, after)

    def test_refuses_repository_output_and_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = decided_workspace(Path(directory))
            with self.assertRaisesRegex(ValueError, "outside the repository"):
                prepare_handoff.check_handoff(
                    workspace,
                    REPO_ROOT / "reports" / "unsafe-handoff",
                )

            prefix = workspace / "handoff" / "repository-candidate"
            prepare_handoff.write_handoff(workspace, prefix)
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                prepare_handoff.write_handoff(workspace, prefix)

    def test_rejects_missing_decision_and_partial_handoff_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "cohort"
            prepare_workspace.prepare_workspace(workspace, BUILD_ID)
            for index in range(1, 6):
                value = session(f"anonymous-{index:03d}")
                (
                    workspace
                    / "incoming-sessions"
                    / f"session-{index:03d}.jsonl"
                ).write_text(json.dumps(value) + "\n", encoding="utf-8")
            assemble_workspace.assemble_workspace(workspace)
            review_workspace.prepare_workspace_review(workspace)
            prefix = workspace / "handoff" / "repository-candidate"

            with self.assertRaisesRegex(ValueError, "decision artifacts do not exist"):
                prepare_handoff.check_handoff(workspace, prefix)

            record_decision.record_workspace_decision(
                workspace,
                "hold-current-route",
                PRIVATE_REVIEWER,
                "2026-08-02",
                PRIVATE_RATIONALE,
                PRIVATE_CHECKPOINT,
            )
            json_path, _ = prepare_handoff._output_paths(prefix)
            json_path.parent.mkdir(parents=True)
            json_path.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "pair is incomplete"):
                prepare_handoff.verify_handoff(workspace, prefix)

    def test_rejects_changed_handoff_or_private_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = decided_workspace(Path(directory))
            prefix = workspace / "handoff" / "repository-candidate"
            created = prepare_handoff.write_handoff(workspace, prefix)
            json_path = Path(str(created["output_json"]))
            markdown_path = Path(str(created["output_markdown"]))

            candidate = json.loads(json_path.read_text(encoding="utf-8"))
            candidate["primary_action"] = "hold-current-route"
            json_path.write_bytes(prepare_review.canonical_json(candidate))
            markdown_path.write_text(
                prepare_handoff.render_markdown(candidate),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "does not match"):
                prepare_handoff.verify_handoff(workspace, prefix)

            json_path.unlink()
            markdown_path.unlink()
            prepare_handoff.write_handoff(workspace, prefix)
            source = workspace / "incoming-sessions" / "session-001.jsonl"
            value = json.loads(source.read_text(encoding="utf-8"))
            value["facilitator_notes"] = "changed private source"
            source.write_text(json.dumps(value) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "do not match intake manifest"):
                prepare_handoff.verify_handoff(workspace, prefix)


if __name__ == "__main__":
    unittest.main()
