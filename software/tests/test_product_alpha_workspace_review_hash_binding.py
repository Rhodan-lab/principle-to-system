from __future__ import annotations

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


def session(session_id: str, duration: int) -> dict[str, object]:
    return {
        "pilot_build_id": BUILD_ID,
        "session_id": session_id,
        "route_id": "refrigerator-v1",
        "started": True,
        "completed_steps": ["observe", "map", "model", "diagnose", "redesign"],
        "duration_minutes": duration,
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


def encoded_session(session_id: str, duration: int) -> bytes:
    return (
        json.dumps(
            session(session_id, duration),
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def create_workspace(root: Path) -> tuple[Path, Path, Path]:
    workspace = root / "cohort"
    incoming = workspace / "incoming-sessions"
    (workspace / "verified").mkdir(parents=True)
    (workspace / "review").mkdir()
    incoming.mkdir()
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
    (incoming / "session-001.jsonl").write_bytes(
        encoded_session("anonymous-001", 20)
    )
    assemble_workspace.assemble_workspace(workspace)
    return (
        workspace,
        workspace / "verified" / "anonymous-sessions.jsonl",
        workspace / "review" / "refrigerator-review",
    )


class ProductAlphaWorkspaceReviewHashBindingTests(unittest.TestCase):
    def test_bound_packet_uses_verified_combined_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace, _, _ = create_workspace(Path(directory))
            verification = review_workspace.verify_workspace_intake(workspace)

            packet = review_workspace.build_bound_review_packet(verification)

        evidence = packet["evidence_binding"]
        self.assertEqual(
            evidence["input_sha256"],
            verification["combined_sha256"],
        )
        self.assertEqual(
            evidence["source_records_sha256"],
            verification["source_records_sha256"],
        )
        self.assertTrue(evidence["raw_sources_verified"])

    def test_rejects_combined_mutation_before_packet_publication(self) -> None:
        replacement = encoded_session("anonymous-002", 30)
        with tempfile.TemporaryDirectory() as directory:
            workspace, combined, prefix = create_workspace(Path(directory))
            real_build = prepare_review.build_review_packet
            build_calls = 0

            def mutate_then_build(path: Path, expected_build_id: str) -> dict[str, object]:
                nonlocal build_calls
                build_calls += 1
                path.write_bytes(replacement)
                return real_build(path, expected_build_id)

            with mock.patch.object(
                review_workspace.prepare_review,
                "build_review_packet",
                side_effect=mutate_then_build,
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "input SHA-256 does not match verified combined cohort",
                ):
                    review_workspace.prepare_workspace_review(workspace)

            current = combined.read_bytes()

        self.assertEqual(build_calls, 1)
        self.assertEqual(current, replacement)
        self.assertFalse(prefix.with_suffix(".json").exists())
        self.assertFalse(prefix.with_suffix(".md").exists())

    def test_rejects_packet_with_unverified_input_hash(self) -> None:
        verification = {
            "combined_jsonl": "/private/combined.jsonl",
            "pilot_build_id": BUILD_ID,
            "combined_sha256": "a" * 64,
            "workspace_contract": "workspace-contract",
            "intake_manifest_sha256": "b" * 64,
            "source_records_sha256": "c" * 64,
            "source_record_count": 1,
        }
        packet = {"evidence_binding": {"input_sha256": "d" * 64}}
        with mock.patch.object(
            review_workspace.prepare_review,
            "build_review_packet",
            return_value=packet,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "input SHA-256 does not match verified combined cohort",
            ):
                review_workspace.build_bound_review_packet(verification)


if __name__ == "__main__":
    unittest.main()
