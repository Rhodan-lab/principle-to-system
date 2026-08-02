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
SCRIPT = EVALUATION_DIR / "assemble_workspace.py"
sys.path.insert(0, str(EVALUATION_DIR))

import assemble_workspace  # noqa: E402

BUILD_ID = "a" * 64
OTHER_BUILD_ID = "b" * 64


def session(session_id: str, *, build_id: str = BUILD_ID) -> dict[str, object]:
    return {
        "pilot_build_id": build_id,
        "session_id": session_id,
        "route_id": "refrigerator-v1",
        "started": True,
        "completed_steps": ["observe", "map", "model"],
        "duration_minutes": 24,
        "scores": {
            "mechanism_explanation": 2,
            "model_reasoning": 1,
            "failure_diagnosis": 1,
            "evidence_boundary": 2,
            "redesign_tradeoff": 1,
        },
        "confusion_tags": [],
        "voluntary_continue": True,
        "facilitator_notes": "",
    }


def workspace_manifest() -> dict[str, object]:
    return {
        "contract": "principia-product-alpha-pilot-workspace/0.1",
        "pilot_build_id": BUILD_ID,
        "route_id": "refrigerator-v1",
        "privacy_boundaries": {
            "participant_names_allowed": False,
            "raw_sessions_committed_to_repository": False,
            "repository_output_allowed": False,
        },
        "paths": {
            "incoming_sessions": "incoming-sessions",
            "combined_jsonl": "verified/anonymous-sessions.jsonl",
            "intake_manifest": "verified/intake-manifest.json",
            "review_output_prefix": "review/refrigerator-review",
        },
    }


def create_workspace(root: Path) -> Path:
    workspace = root / "cohort"
    (workspace / "incoming-sessions").mkdir(parents=True)
    (workspace / "verified").mkdir()
    (workspace / "review").mkdir()
    (workspace / "workspace.json").write_text(
        json.dumps(workspace_manifest(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return workspace


class ProductAlphaWorkspaceIntakeTests(unittest.TestCase):
    def test_assembles_deterministic_build_bound_cohort(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            second_path = workspace / "incoming-sessions" / "second.jsonl"
            first_path = workspace / "incoming-sessions" / "first.json"
            second_path.write_text(
                json.dumps(session("anonymous-002")) + "\n",
                encoding="utf-8",
            )
            first_path.write_text(
                json.dumps(session("anonymous-001"), indent=2) + "\n",
                encoding="utf-8",
            )

            report = assemble_workspace.assemble_workspace(workspace)
            combined = workspace / "verified" / "anonymous-sessions.jsonl"
            intake = workspace / "verified" / "intake-manifest.json"
            lines = combined.read_text(encoding="utf-8").splitlines()
            saved = json.loads(intake.read_text(encoding="utf-8"))

            self.assertEqual(
                report["contract"],
                "principia-product-alpha-workspace-intake/0.1",
            )
            self.assertEqual(report["decision"], "workspace-intake-assembled")
            self.assertEqual(report["pilot_build_id"], BUILD_ID)
            self.assertEqual(report["sessions"], 2)
            self.assertEqual(report["evidence_status"], "incomplete")
            self.assertTrue(report["human_review_required"])
            self.assertFalse(report["raw_source_files_modified"])
            self.assertEqual(saved, report)
            self.assertEqual(
                report["combined_sha256"],
                hashlib.sha256(combined.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                [json.loads(line)["session_id"] for line in lines],
                ["anonymous-001", "anonymous-002"],
            )
            self.assertEqual(
                [entry["session_id"] for entry in report["source_records"]],
                ["anonymous-001", "anonymous-002"],
            )
            self.assertEqual(
                json.loads(first_path.read_text(encoding="utf-8"))["session_id"],
                "anonymous-001",
            )
            self.assertEqual(
                json.loads(second_path.read_text(encoding="utf-8"))["session_id"],
                "anonymous-002",
            )

    def test_rejects_mixed_build_before_writing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            (workspace / "incoming-sessions" / "one.jsonl").write_text(
                json.dumps(session("anonymous-001")) + "\n",
                encoding="utf-8",
            )
            (workspace / "incoming-sessions" / "two.jsonl").write_text(
                json.dumps(
                    session("anonymous-002", build_id=OTHER_BUILD_ID)
                )
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "pilot_build_id does not match workspace build",
            ):
                assemble_workspace.assemble_workspace(workspace)
            self.assertFalse(
                (workspace / "verified" / "anonymous-sessions.jsonl").exists()
            )
            self.assertFalse(
                (workspace / "verified" / "intake-manifest.json").exists()
            )

    def test_rejects_duplicate_session_ids_before_writing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            for name in ("one.jsonl", "two.json"):
                (workspace / "incoming-sessions" / name).write_text(
                    json.dumps(session("anonymous-001")) + "\n",
                    encoding="utf-8",
                )

            with self.assertRaisesRegex(ValueError, "duplicate session_id"):
                assemble_workspace.assemble_workspace(workspace)
            self.assertEqual(list((workspace / "verified").iterdir()), [])

    def test_rejects_personal_data_before_writing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            value = session("anonymous-001")
            value["email"] = "not-allowed@example.test"
            (workspace / "incoming-sessions" / "one.jsonl").write_text(
                json.dumps(value) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "personal-data fields"):
                assemble_workspace.assemble_workspace(workspace)
            self.assertEqual(list((workspace / "verified").iterdir()), [])

    def test_refuses_to_overwrite_existing_combined_cohort(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            (workspace / "incoming-sessions" / "one.jsonl").write_text(
                json.dumps(session("anonymous-001")) + "\n",
                encoding="utf-8",
            )
            combined = workspace / "verified" / "anonymous-sessions.jsonl"
            combined.write_text("keep\n", encoding="utf-8")

            with self.assertRaisesRegex(FileExistsError, "already exists"):
                assemble_workspace.assemble_workspace(workspace)
            self.assertEqual(combined.read_text(encoding="utf-8"), "keep\n")

    def test_cli_reports_private_intake(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            (workspace / "incoming-sessions" / "one.jsonl").write_text(
                json.dumps(session("anonymous-001")) + "\n",
                encoding="utf-8",
            )
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
            self.assertEqual(report["decision"], "workspace-intake-assembled")
            self.assertEqual(report["sessions"], 1)
            self.assertEqual(
                report["combined_jsonl"],
                str((workspace / "verified" / "anonymous-sessions.jsonl").resolve()),
            )


if __name__ == "__main__":
    unittest.main()
