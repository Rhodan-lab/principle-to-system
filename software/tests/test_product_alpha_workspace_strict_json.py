from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

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


def session() -> dict[str, object]:
    return {
        "pilot_build_id": BUILD_ID,
        "session_id": "anonymous-001",
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


def create_workspace(root: Path, *, manifest_text: str | None = None) -> Path:
    workspace = root / "cohort"
    (workspace / "incoming-sessions").mkdir(parents=True)
    (workspace / "verified").mkdir()
    (workspace / "review").mkdir()
    if manifest_text is None:
        manifest_text = json.dumps(manifest(), sort_keys=True) + "\n"
    (workspace / "workspace.json").write_text(manifest_text, encoding="utf-8")
    return workspace


def verified_entries(workspace: Path) -> list[Path]:
    return list((workspace / "verified").iterdir())


class ProductAlphaWorkspaceStrictJsonTests(unittest.TestCase):
    def test_valid_session_export_still_passes_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            (workspace / "incoming-sessions" / "one.jsonl").write_text(
                json.dumps(session()) + "\n",
                encoding="utf-8",
            )

            report = assemble_workspace.preflight_workspace(workspace)

            self.assertEqual(report["sessions"], 1)
            self.assertEqual(verified_entries(workspace), [])

    def test_duplicate_top_level_session_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            raw = json.dumps(session(), separators=(",", ":"))
            raw = raw[:-1] + ',"duration_minutes":25}'
            (workspace / "incoming-sessions" / "one.jsonl").write_text(
                raw + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicate JSON key 'duration_minutes'"):
                assemble_workspace.preflight_workspace(workspace)
            self.assertEqual(verified_entries(workspace), [])

    def test_duplicate_nested_score_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            raw = json.dumps(session(), separators=(",", ":"))
            raw = raw.replace(
                '"mechanism_explanation":2',
                '"mechanism_explanation":2,"mechanism_explanation":0',
            )
            (workspace / "incoming-sessions" / "one.jsonl").write_text(
                raw + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "duplicate JSON key 'mechanism_explanation'",
            ):
                assemble_workspace.preflight_workspace(workspace)
            self.assertEqual(verified_entries(workspace), [])

    def test_nonfinite_session_number_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            raw = json.dumps(session(), separators=(",", ":")).replace(
                '"duration_minutes":24',
                '"duration_minutes":NaN',
            )
            (workspace / "incoming-sessions" / "one.jsonl").write_text(
                raw + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "unsupported non-finite number 'NaN'"):
                assemble_workspace.preflight_workspace(workspace)
            self.assertEqual(verified_entries(workspace), [])

    def test_duplicate_workspace_manifest_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            raw = json.dumps(manifest(), separators=(",", ":"))
            raw = raw[:-1] + ',"route_id":"distributed-information-v1"}'
            workspace = create_workspace(Path(directory), manifest_text=raw + "\n")

            with self.assertRaisesRegex(ValueError, "duplicate JSON key 'route_id'"):
                assemble_workspace.preflight_workspace(workspace)
            self.assertEqual(verified_entries(workspace), [])

    def test_nonfinite_workspace_manifest_value_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            raw = json.dumps(manifest(), separators=(",", ":"))
            raw = raw[:-1] + ',"unexpected":Infinity}'
            workspace = create_workspace(Path(directory), manifest_text=raw + "\n")

            with self.assertRaisesRegex(
                ValueError,
                "unsupported non-finite number 'Infinity'",
            ):
                assemble_workspace.preflight_workspace(workspace)
            self.assertEqual(verified_entries(workspace), [])


if __name__ == "__main__":
    unittest.main()
