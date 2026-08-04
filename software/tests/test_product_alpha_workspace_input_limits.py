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

BUILD_ID = "a" * 64


def manifest() -> dict[str, object]:
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


def session(number: int) -> dict[str, object]:
    return {
        "pilot_build_id": BUILD_ID,
        "session_id": f"anonymous-{number:03d}",
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


def source_bytes(number: int) -> bytes:
    return (json.dumps(session(number), sort_keys=True) + "\n").encode("utf-8")


def combined_bytes(numbers: list[int]) -> bytes:
    return "".join(
        json.dumps(session(number), sort_keys=True, separators=(",", ":")) + "\n"
        for number in numbers
    ).encode("utf-8")


def create_workspace(root: Path, numbers: list[int]) -> tuple[Path, bytes]:
    workspace = root / "cohort"
    incoming = workspace / "incoming-sessions"
    incoming.mkdir(parents=True)
    (workspace / "verified").mkdir()
    (workspace / "review").mkdir()
    manifest_raw = (json.dumps(manifest(), sort_keys=True) + "\n").encode("utf-8")
    (workspace / "workspace.json").write_bytes(manifest_raw)
    for number in numbers:
        (incoming / f"session-{number:03d}.jsonl").write_bytes(source_bytes(number))
    return workspace, manifest_raw


def verified_entries(workspace: Path) -> list[Path]:
    return list((workspace / "verified").iterdir())


class ProductAlphaWorkspaceInputLimitTests(unittest.TestCase):
    def test_exact_resource_limits_still_allow_valid_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace, manifest_raw = create_workspace(Path(directory), [1])
            raw = source_bytes(1)
            canonical = combined_bytes([1])
            with (
                mock.patch.object(assemble_workspace, "MAX_INCOMING_ENTRIES", 1),
                mock.patch.object(assemble_workspace, "MAX_SOURCE_FILE_BYTES", len(raw)),
                mock.patch.object(assemble_workspace, "MAX_TOTAL_SOURCE_BYTES", len(raw)),
                mock.patch.object(
                    assemble_workspace,
                    "MAX_JSON_OBJECT_BYTES",
                    len(manifest_raw),
                ),
                mock.patch.object(assemble_workspace, "MAX_COMBINED_BYTES", len(canonical)),
            ):
                report = assemble_workspace.preflight_workspace(workspace)

            self.assertEqual(report["sessions"], 1)
            self.assertEqual(verified_entries(workspace), [])

    def test_incoming_entry_count_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace, _ = create_workspace(Path(directory), [1, 2, 3])
            with mock.patch.object(assemble_workspace, "MAX_INCOMING_ENTRIES", 2):
                with self.assertRaisesRegex(ValueError, "more than 2 entries"):
                    assemble_workspace.preflight_workspace(workspace)
            self.assertEqual(verified_entries(workspace), [])

    def test_single_source_file_read_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace, _ = create_workspace(Path(directory), [1])
            raw = source_bytes(1)
            with mock.patch.object(
                assemble_workspace,
                "MAX_SOURCE_FILE_BYTES",
                len(raw) - 1,
            ):
                with self.assertRaisesRegex(ValueError, "exceeds the .*byte limit"):
                    assemble_workspace.preflight_workspace(workspace)
            self.assertEqual(verified_entries(workspace), [])

    def test_total_source_bytes_are_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace, _ = create_workspace(Path(directory), [1, 2])
            total = len(source_bytes(1)) + len(source_bytes(2))
            with (
                mock.patch.object(assemble_workspace, "MAX_SOURCE_FILE_BYTES", total),
                mock.patch.object(
                    assemble_workspace,
                    "MAX_TOTAL_SOURCE_BYTES",
                    total - 1,
                ),
            ):
                with self.assertRaisesRegex(ValueError, "total limit"):
                    assemble_workspace.preflight_workspace(workspace)
            self.assertEqual(verified_entries(workspace), [])

    def test_workspace_manifest_read_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace, manifest_raw = create_workspace(Path(directory), [1])
            with mock.patch.object(
                assemble_workspace,
                "MAX_JSON_OBJECT_BYTES",
                len(manifest_raw) - 1,
            ):
                with self.assertRaisesRegex(ValueError, "workspace.json: exceeds"):
                    assemble_workspace.preflight_workspace(workspace)
            self.assertEqual(verified_entries(workspace), [])

    def test_canonical_combined_output_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace, _ = create_workspace(Path(directory), [1])
            canonical = combined_bytes([1])
            with mock.patch.object(
                assemble_workspace,
                "MAX_COMBINED_BYTES",
                len(canonical) - 1,
            ):
                with self.assertRaisesRegex(ValueError, "canonical combined cohort exceeds"):
                    assemble_workspace.preflight_workspace(workspace)
            self.assertEqual(verified_entries(workspace), [])


if __name__ == "__main__":
    unittest.main()
