from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
sys.path.insert(0, str(EVALUATION_DIR))

import assemble_workspace  # noqa: E402
import prepare_review  # noqa: E402
import review_workspace  # noqa: E402

BUILD_ID = "a" * 64


def session() -> dict[str, object]:
    return {
        "pilot_build_id": BUILD_ID,
        "session_id": "anonymous-001",
        "route_id": "refrigerator-v1",
        "started": True,
        "completed_steps": ["observe", "map", "model", "diagnose", "redesign"],
        "duration_minutes": 20,
        "scores": {
            "mechanism_explanation": 2,
            "model_reasoning": 2,
            "failure_diagnosis": 2,
            "evidence_boundary": 2,
            "redesign_tradeoff": 2,
        },
        "confusion_tags": [],
        "voluntary_continue": True,
        "facilitator_notes": "",
    }


def create_workspace(root: Path) -> tuple[Path, Path, Path, Path]:
    workspace = root / "cohort"
    incoming = workspace / "incoming-sessions"
    verified = workspace / "verified"
    review = workspace / "review"
    incoming.mkdir(parents=True)
    verified.mkdir()
    review.mkdir()
    manifest = {
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
    (workspace / "workspace.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    source = incoming / "session-001.jsonl"
    source.write_text(
        json.dumps(session(), sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    assemble_workspace.assemble_workspace(workspace)
    return (
        workspace,
        source,
        verified / "anonymous-sessions.jsonl",
        verified / "intake-manifest.json",
    )


def rewrite_intake_for_source(intake_path: Path, source_path: Path) -> None:
    intake = json.loads(intake_path.read_text(encoding="utf-8"))
    source_records = intake["source_records"]
    source_records[0]["sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
    intake["source_records_sha256"] = hashlib.sha256(
        prepare_review.canonical_json(source_records)
    ).hexdigest()
    intake_path.write_text(
        json.dumps(intake, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


class ProductAlphaWorkspaceReviewInputBoundaryTests(unittest.TestCase):
    def test_rejects_duplicate_intake_manifest_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace, _, _, intake = create_workspace(Path(directory))
            text = intake.read_text(encoding="utf-8")
            duplicate = (
                '{\n  "contract": "principia-product-alpha-workspace-intake/0.1",\n'
                + text[2:]
            )
            intake.write_text(duplicate, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "duplicate JSON key 'contract'"):
                review_workspace.verify_workspace_intake(workspace)

    def test_rejects_duplicate_raw_source_keys_after_hash_update(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace, source, _, intake = create_workspace(Path(directory))
            raw = source.read_text(encoding="utf-8")
            source.write_text(
                raw.replace("{", '{"started":true,', 1),
                encoding="utf-8",
            )
            rewrite_intake_for_source(intake, source)

            with self.assertRaisesRegex(ValueError, "duplicate JSON key 'started'"):
                review_workspace.verify_workspace_intake(workspace)

    def test_rejects_oversized_intake_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace, _, _, intake = create_workspace(Path(directory))
            with mock.patch.object(
                review_workspace,
                "MAX_JSON_OBJECT_BYTES",
                len(intake.read_bytes()) - 1,
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "verified intake manifest exceeds",
                ):
                    review_workspace.verify_workspace_intake(workspace)

    def test_rejects_oversized_source_export(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace, source, _, _ = create_workspace(Path(directory))
            with mock.patch.object(
                review_workspace,
                "MAX_SOURCE_FILE_BYTES",
                len(source.read_bytes()) - 1,
            ):
                with self.assertRaisesRegex(ValueError, "session-001.jsonl exceeds"):
                    review_workspace.verify_workspace_intake(workspace)

    def test_rejects_source_set_over_total_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace, source, _, _ = create_workspace(Path(directory))
            with mock.patch.object(
                review_workspace,
                "MAX_TOTAL_SOURCE_BYTES",
                len(source.read_bytes()) - 1,
            ):
                with self.assertRaisesRegex(ValueError, "total limit"):
                    review_workspace.verify_workspace_intake(workspace)

    def test_rejects_oversized_combined_cohort(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace, _, combined, _ = create_workspace(Path(directory))
            with mock.patch.object(
                review_workspace,
                "MAX_COMBINED_BYTES",
                len(combined.read_bytes()) - 1,
            ):
                with self.assertRaisesRegex(ValueError, "combined cohort exceeds"):
                    review_workspace.verify_workspace_intake(workspace)

    def test_summary_uses_the_combined_snapshot_already_hashed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace, _, combined, _ = create_workspace(Path(directory))
            original = combined.read_bytes()
            replacement = b"tampered after bounded read\n"
            real_read = review_workspace._read_bounded_bytes
            combined_reads = 0

            def mutate_after_combined_read(
                path: Path,
                label: str,
                limit: int,
            ) -> bytes:
                nonlocal combined_reads
                raw = real_read(path, label, limit)
                if path == combined:
                    combined_reads += 1
                    path.write_bytes(replacement)
                return raw

            with mock.patch.object(
                review_workspace,
                "_read_bounded_bytes",
                side_effect=mutate_after_combined_read,
            ):
                report = review_workspace.verify_workspace_intake(workspace)

            current = combined.read_bytes()

        self.assertEqual(combined_reads, 1)
        self.assertEqual(current, replacement)
        self.assertEqual(
            report["combined_sha256"],
            hashlib.sha256(original).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
