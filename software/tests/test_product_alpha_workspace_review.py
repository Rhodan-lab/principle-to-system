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
SCRIPT = EVALUATION_DIR / "review_workspace.py"
sys.path.insert(0, str(EVALUATION_DIR))

import assemble_workspace  # noqa: E402
import prepare_workspace  # noqa: E402
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


def assembled_workspace(root: Path, count: int = 5) -> Path:
    workspace = root / "cohort"
    prepare_workspace.prepare_workspace(workspace, BUILD_ID)
    for index in range(1, count + 1):
        value = session(f"anonymous-{index:03d}")
        (workspace / "incoming-sessions" / f"session-{index:03d}.jsonl").write_text(
            json.dumps(value, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    assemble_workspace.assemble_workspace(
        workspace,
        allow_incomplete=count < 5,
    )
    return workspace


class ProductAlphaWorkspaceReviewTests(unittest.TestCase):
    def test_verifies_complete_intake_and_creates_bound_review_packet(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = assembled_workspace(Path(directory))

            verification = review_workspace.verify_workspace_intake(workspace)
            self.assertEqual(
                verification["contract"],
                "principia-product-alpha-workspace-review/0.1",
            )
            self.assertEqual(verification["decision"], "workspace-intake-verified")
            self.assertEqual(verification["sessions"], 5)
            self.assertEqual(verification["evidence_status"], "ready-for-human-review")
            self.assertTrue(verification["raw_sources_verified"])
            self.assertEqual(verification["source_record_count"], 5)
            self.assertEqual(
                verification["observation_mode"],
                "optional-descriptive",
            )
            self.assertFalse(verification["roadmap_gate"])
            self.assertFalse(verification["decision_authority"])
            self.assertRegex(
                str(verification["intake_manifest_sha256"]),
                r"^[0-9a-f]{64}$",
            )

            report = review_workspace.prepare_workspace_review(workspace)
            review_json = Path(str(report["review_json"]))
            review_markdown = Path(str(report["review_markdown"]))
            packet = json.loads(review_json.read_text(encoding="utf-8"))
            evidence = packet["evidence_binding"]

            self.assertEqual(report["decision"], "workspace-review-packet-created")
            self.assertTrue(review_json.is_file())
            self.assertTrue(review_markdown.is_file())
            self.assertEqual(
                evidence["workspace_contract"],
                "principia-product-alpha-pilot-workspace/0.1",
            )
            self.assertEqual(
                evidence["workspace_intake_contract"],
                "principia-product-alpha-workspace-intake/0.1",
            )
            self.assertEqual(
                evidence["intake_manifest_sha256"],
                verification["intake_manifest_sha256"],
            )
            self.assertEqual(
                evidence["source_records_sha256"],
                verification["source_records_sha256"],
            )
            self.assertEqual(evidence["source_record_count"], 5)
            self.assertTrue(evidence["raw_sources_verified"])
            self.assertEqual(
                report["review_packet_sha256"],
                hashlib.sha256(review_json.read_bytes()).hexdigest(),
            )

    def test_rejects_combined_cohort_changed_after_intake(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = assembled_workspace(Path(directory), count=2)
            combined = workspace / "verified" / "anonymous-sessions.jsonl"
            combined.write_bytes(combined.read_bytes() + b"\n")

            with self.assertRaisesRegex(ValueError, "does not match intake manifest"):
                review_workspace.verify_workspace_intake(workspace)
            self.assertEqual(list((workspace / "review").iterdir()), [])

    def test_rejects_raw_export_changed_after_intake(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = assembled_workspace(Path(directory), count=2)
            source = workspace / "incoming-sessions" / "session-001.jsonl"
            value = json.loads(source.read_text(encoding="utf-8"))
            value["facilitator_notes"] = "changed after intake"
            source.write_text(json.dumps(value) + "\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "do not match intake manifest hashes"):
                review_workspace.verify_workspace_intake(workspace)
            self.assertEqual(list((workspace / "review").iterdir()), [])

    def test_rejects_relaxed_intake_review_boundary(self) -> None:
        cases = (
            ("human_review_required", False, "human_review_required=true"),
            (
                "observation_mode",
                "required-product-gate",
                "observation_mode must be 'optional-descriptive'",
            ),
            ("roadmap_gate", True, "roadmap_gate=false"),
            ("decision_authority", True, "decision_authority=false"),
        )
        for field, replacement, message in cases:
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory() as directory:
                    workspace = assembled_workspace(Path(directory), count=1)
                    intake_path = workspace / "verified" / "intake-manifest.json"
                    intake = json.loads(intake_path.read_text(encoding="utf-8"))
                    intake[field] = replacement
                    intake_path.write_text(
                        json.dumps(intake, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )

                    with self.assertRaisesRegex(ValueError, message):
                        review_workspace.verify_workspace_intake(workspace)
                    self.assertEqual(list((workspace / "review").iterdir()), [])

    def test_cli_check_reports_verified_chain_without_writing_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = assembled_workspace(Path(directory), count=1)
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
            self.assertEqual(report["decision"], "workspace-intake-verified")
            self.assertEqual(report["sessions"], 1)
            self.assertTrue(report["raw_sources_verified"])
            self.assertEqual(report["observation_mode"], "optional-descriptive")
            self.assertFalse(report["roadmap_gate"])
            self.assertFalse(report["decision_authority"])
            self.assertEqual(list((workspace / "review").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
