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


def write_sessions(
    workspace: Path,
    count: int,
    *,
    start: int = 1,
    build_id: str = BUILD_ID,
) -> None:
    incoming = workspace / "incoming-sessions"
    for number in range(start, start + count):
        path = incoming / f"session-{number:03d}.jsonl"
        path.write_text(
            json.dumps(
                session(f"anonymous-{number:03d}", build_id=build_id),
                indent=2 if number % 2 else None,
            )
            + "\n",
            encoding="utf-8",
        )


class ProductAlphaWorkspaceIntakeTests(unittest.TestCase):
    def test_preflight_predicts_complete_intake_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 5)

            report = assemble_workspace.preflight_workspace(workspace)

            self.assertEqual(
                report["contract"],
                "principia-product-alpha-workspace-intake-preflight/0.1",
            )
            self.assertEqual(
                report["decision"],
                "workspace-intake-preflight-passed",
            )
            self.assertEqual(report["sessions"], 5)
            self.assertEqual(report["minimum_cohort_size"], 0)
            self.assertTrue(report["cohort_complete"])
            self.assertEqual(report["evidence_status"], "ready-for-human-review")
            self.assertTrue(report["ready_for_default_assembly"])
            self.assertFalse(report["incomplete_assembly_requires_override"])
            self.assertFalse(report["writes_performed"])
            self.assertEqual(
                report["verified_outputs_exist"],
                {"combined_jsonl": False, "intake_manifest": False},
            )
            self.assertEqual(list((workspace / "verified").iterdir()), [])

    def test_repeated_preflight_allows_more_sessions_before_assembly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 2)

            first = assemble_workspace.preflight_workspace(workspace)
            write_sessions(workspace, 3, start=3)
            second = assemble_workspace.preflight_workspace(workspace)

            self.assertEqual(first["sessions"], 2)
            self.assertTrue(first["cohort_complete"])
            self.assertFalse(first["incomplete_assembly_requires_override"])
            self.assertTrue(first["ready_for_default_assembly"])
            self.assertEqual(second["sessions"], 5)
            self.assertTrue(second["cohort_complete"])
            self.assertNotEqual(
                first["predicted_combined_sha256"],
                second["predicted_combined_sha256"],
            )
            self.assertEqual(list((workspace / "verified").iterdir()), [])

    def test_complete_assembly_matches_preflight_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 5)
            preflight = assemble_workspace.preflight_workspace(workspace)

            report = assemble_workspace.assemble_workspace(workspace)
            combined = workspace / "verified" / "anonymous-sessions.jsonl"
            intake = workspace / "verified" / "intake-manifest.json"
            saved = json.loads(intake.read_text(encoding="utf-8"))

            self.assertEqual(report["decision"], "workspace-intake-assembled")
            self.assertEqual(report["sessions"], 5)
            self.assertTrue(report["cohort_complete"])
            self.assertFalse(report["incomplete_assembly_authorized"])
            self.assertEqual(saved, report)
            self.assertEqual(
                report["combined_sha256"],
                preflight["predicted_combined_sha256"],
            )
            self.assertEqual(
                report["source_records_sha256"],
                preflight["source_records_sha256"],
            )
            self.assertEqual(
                report["combined_sha256"],
                hashlib.sha256(combined.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                [
                    json.loads(line)["session_id"]
                    for line in combined.read_text(encoding="utf-8").splitlines()
                ],
                [f"anonymous-{number:03d}" for number in range(1, 6)],
            )

    def test_default_assembly_accepts_any_nonempty_valid_observation_set(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 1)

            report = assemble_workspace.assemble_workspace(workspace)

            self.assertEqual(report["sessions"], 1)
            self.assertEqual(report["minimum_cohort_size"], 0)
            self.assertTrue(report["cohort_complete"])
            self.assertFalse(report["incomplete_assembly_authorized"])
            self.assertEqual(report["observation_mode"], "optional-descriptive")
            self.assertFalse(report["roadmap_gate"])
            self.assertTrue(
                (workspace / "verified" / "anonymous-sessions.jsonl").exists()
            )

    def test_allow_incomplete_flag_is_a_compatibility_noop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 2)

            report = assemble_workspace.assemble_workspace(
                workspace,
                allow_incomplete=True,
            )

            self.assertEqual(report["sessions"], 2)
            self.assertTrue(report["cohort_complete"])
            self.assertEqual(report["evidence_status"], "ready-for-human-review")
            self.assertFalse(report["incomplete_assembly_authorized"])

    def test_preflight_reports_existing_verified_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 5)
            assemble_workspace.assemble_workspace(workspace)

            report = assemble_workspace.preflight_workspace(workspace)

            self.assertEqual(
                report["verified_outputs_exist"],
                {"combined_jsonl": True, "intake_manifest": True},
            )
            self.assertFalse(report["ready_for_default_assembly"])
            with self.assertRaisesRegex(FileExistsError, "already exists"):
                assemble_workspace.assemble_workspace(workspace)

    def test_rejects_mixed_build_before_writing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 1)
            write_sessions(workspace, 1, start=2, build_id=OTHER_BUILD_ID)

            with self.assertRaisesRegex(
                ValueError,
                "pilot_build_id does not match workspace build",
            ):
                assemble_workspace.preflight_workspace(workspace)
            self.assertEqual(list((workspace / "verified").iterdir()), [])

    def test_rejects_duplicate_session_ids_before_writing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            incoming = workspace / "incoming-sessions"
            for name in ("one.jsonl", "two.json"):
                (incoming / name).write_text(
                    json.dumps(session("anonymous-001")) + "\n",
                    encoding="utf-8",
                )

            with self.assertRaisesRegex(ValueError, "duplicate session_id"):
                assemble_workspace.preflight_workspace(workspace)
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
                assemble_workspace.preflight_workspace(workspace)
            self.assertEqual(list((workspace / "verified").iterdir()), [])

    def test_rejects_workspace_inside_repository_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            workspace = create_workspace(repository)
            with self.assertRaisesRegex(ValueError, "outside the repository"):
                assemble_workspace.preflight_workspace(
                    workspace,
                    repo_root=repository,
                )
            self.assertEqual(list((workspace / "verified").iterdir()), [])

    def test_cli_check_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 2)
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

            self.assertEqual(
                report["decision"],
                "workspace-intake-preflight-passed",
            )
            self.assertEqual(report["sessions"], 2)
            self.assertFalse(report["writes_performed"])
            self.assertEqual(list((workspace / "verified").iterdir()), [])

    def test_cli_assembles_single_observation_without_override(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 1)

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
            self.assertEqual(report["sessions"], 1)
            self.assertTrue(report["cohort_complete"])
            self.assertFalse(report["incomplete_assembly_authorized"])


if __name__ == "__main__":
    unittest.main()
