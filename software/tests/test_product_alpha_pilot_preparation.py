from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ALPHA = REPO_ROOT / "software" / "product_alpha"
SCRIPT = PRODUCT_ALPHA / "prepare_pilot.py"
sys.path.insert(0, str(PRODUCT_ALPHA))
import prepare_pilot as preparation  # noqa: E402


class ProductAlphaPilotPreparationTests(unittest.TestCase):
    def test_cli_smokes_and_creates_empty_build_bound_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "cohort with spaces"
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--workspace", str(workspace)],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            report_line = next(
                line
                for line in reversed(completed.stdout.splitlines())
                if line.strip()
            )
            report = json.loads(report_line)
            manifest = json.loads(
                (workspace / "workspace.json").read_text(encoding="utf-8")
            )
            readme = (workspace / "README.md").read_text(encoding="utf-8")

            self.assertEqual(
                report["contract"],
                "principia-product-alpha-pilot-preparation/0.1",
            )
            self.assertEqual(report["decision"], "pilot-preparation-passed")
            self.assertEqual(
                report["smoke_contract"],
                "principia-product-alpha-pilot-smoke/0.1",
            )
            self.assertEqual(report["smoke_decision"], "pilot-smoke-passed")
            self.assertEqual(
                report["workspace_contract"],
                "principia-product-alpha-pilot-workspace/0.1",
            )
            self.assertRegex(report["pilot_build_id"], r"^[0-9a-f]{64}$")
            self.assertEqual(report["pilot_build_id"], manifest["pilot_build_id"])
            self.assertEqual(report["workspace"], str(workspace.resolve()))
            self.assertFalse(report["session_data_stored"])
            self.assertFalse(report["placeholder_evidence_created"])
            self.assertIn(report["pilot_build_id"], readme)
            for name in ("incoming-sessions", "verified", "review"):
                self.assertEqual(list((workspace / name).iterdir()), [])
            self.assertFalse((workspace / "verified" / "anonymous-sessions.jsonl").exists())

    def test_smoke_failure_leaves_no_workspace(self) -> None:
        build_id = "a" * 64
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "must-not-exist"
            with (
                mock.patch.object(preparation.run_pilot, "run_builder"),
                mock.patch.object(preparation.run_pilot, "verify_output"),
                mock.patch.object(
                    preparation.run_pilot,
                    "pilot_build_identity",
                    return_value=build_id,
                ),
                mock.patch.object(
                    preparation.run_pilot,
                    "smoke_served_output",
                    side_effect=ValueError("smoke failed"),
                ),
                mock.patch.object(preparation, "prepare_workspace") as create_workspace,
            ):
                with self.assertRaisesRegex(ValueError, "smoke failed"):
                    preparation.prepare_pilot(workspace)
            create_workspace.assert_not_called()
            self.assertFalse(workspace.exists())


if __name__ == "__main__":
    unittest.main()
