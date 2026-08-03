from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
WORKSPACE_SCRIPT = EVALUATION_DIR / "prepare_workspace.py"
sys.path.insert(0, str(EVALUATION_DIR))

import prepare_workspace  # noqa: E402

BUILD_ID = "a" * 64


class ProductAlphaWorkspaceTests(unittest.TestCase):
    def test_creates_empty_build_bound_private_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "cohort"
            manifest = prepare_workspace.prepare_workspace(workspace, BUILD_ID)

            self.assertEqual(
                manifest["contract"],
                "principia-product-alpha-pilot-workspace/0.1",
            )
            self.assertEqual(manifest["pilot_build_id"], BUILD_ID)
            self.assertEqual(manifest["route_id"], "refrigerator-v1")
            self.assertFalse(
                manifest["privacy_boundaries"]["participant_names_allowed"]
            )
            self.assertFalse(
                manifest["privacy_boundaries"]["raw_sessions_committed_to_repository"]
            )
            self.assertFalse(
                manifest["privacy_boundaries"]["repository_output_allowed"]
            )

            saved = json.loads(
                (workspace / "workspace.json").read_text(encoding="utf-8")
            )
            self.assertEqual(saved, manifest)
            self.assertEqual(list((workspace / "incoming-sessions").iterdir()), [])
            self.assertEqual(list((workspace / "verified").iterdir()), [])
            self.assertEqual(list((workspace / "review").iterdir()), [])

            readme = (workspace / "README.md").read_text(encoding="utf-8")
            self.assertIn(BUILD_ID, readme)
            self.assertIn("verify_cohort.py", readme)
            self.assertIn("prepare_review.py", readme)
            self.assertIn("verified/anonymous-sessions.jsonl", readme)
            self.assertIn("do not commit", readme.lower())
            self.assertIn("Do not treat an empty directory", readme)
            self.assertIn("review-ready-for-advisory", readme)
            self.assertIn("advisory-verified", readme)
            self.assertIn("advisory-handoff-verified", readme)
            self.assertIn("optional observation review packet", readme)
            self.assertIn(
                "historical filenames retain `decision` for compatibility",
                readme,
            )
            self.assertNotIn("review-ready-for-decision", readme)
            self.assertNotIn("decision-verified", readme)
            self.assertNotIn("handoff-verified stages", readme)
            self.assertFalse((workspace / "verified" / "anonymous-sessions.jsonl").exists())

    def test_rejects_invalid_build_id_without_creating_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "cohort"
            with self.assertRaisesRegex(ValueError, "64-character lowercase"):
                prepare_workspace.prepare_workspace(workspace, "A" * 64)
            self.assertFalse(workspace.exists())

    def test_rejects_repository_destination(self) -> None:
        workspace = REPO_ROOT / "software" / "product_alpha" / "private-cohort"
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            prepare_workspace.prepare_workspace(workspace, BUILD_ID)
        self.assertFalse(workspace.exists())

    def test_refuses_to_overwrite_existing_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "cohort"
            workspace.mkdir()
            marker = workspace / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "already exists"):
                prepare_workspace.prepare_workspace(workspace, BUILD_ID)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_cli_creates_workspace_and_reports_exact_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "cohort with spaces"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(WORKSPACE_SCRIPT),
                    "--workspace",
                    str(workspace),
                    "--expect-build-id",
                    BUILD_ID,
                ],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(completed.stdout)
            self.assertEqual(report["decision"], "private-workspace-created")
            self.assertEqual(report["pilot_build_id"], BUILD_ID)
            self.assertEqual(report["workspace"], str(workspace.resolve()))
            readme = (workspace / "README.md").read_text(encoding="utf-8")
            self.assertIn("'", readme)
            self.assertIn(str(workspace), readme)

    def test_cli_fails_closed_for_repository_output(self) -> None:
        workspace = REPO_ROOT / "private-cohort"
        completed = subprocess.run(
            [
                sys.executable,
                str(WORKSPACE_SCRIPT),
                "--workspace",
                str(workspace),
                "--expect-build-id",
                BUILD_ID,
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("outside the repository", completed.stderr)
        self.assertFalse(workspace.exists())


if __name__ == "__main__":
    unittest.main()
