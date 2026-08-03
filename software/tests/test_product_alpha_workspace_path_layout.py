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


def write_manifest(root: Path, value: dict[str, object]) -> Path:
    workspace = root / "cohort"
    workspace.mkdir()
    (workspace / "workspace.json").write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return workspace.resolve()


class ProductAlphaWorkspacePathLayoutTests(unittest.TestCase):
    def test_rejects_combined_inside_incoming_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = manifest()
            paths = value["paths"]
            assert isinstance(paths, dict)
            paths["combined_jsonl"] = "incoming-sessions/combined.jsonl"
            workspace = write_manifest(Path(directory), value)

            with self.assertRaisesRegex(
                ValueError,
                "artifact paths must be outside incoming_sessions",
            ):
                assemble_workspace._load_workspace(workspace)

    def test_rejects_intake_inside_incoming_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = manifest()
            paths = value["paths"]
            assert isinstance(paths, dict)
            paths["intake_manifest"] = "incoming-sessions/intake.json"
            workspace = write_manifest(Path(directory), value)

            with self.assertRaisesRegex(
                ValueError,
                "artifact paths must be outside incoming_sessions",
            ):
                assemble_workspace._load_workspace(workspace)

    def test_rejects_review_outputs_inside_incoming_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = manifest()
            paths = value["paths"]
            assert isinstance(paths, dict)
            paths["review_output_prefix"] = "incoming-sessions/refrigerator-review"
            workspace = write_manifest(Path(directory), value)

            with self.assertRaisesRegex(
                ValueError,
                "artifact paths must be outside incoming_sessions",
            ):
                assemble_workspace._load_workspace(workspace)

    def test_rejects_duplicate_combined_and_intake_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = manifest()
            paths = value["paths"]
            assert isinstance(paths, dict)
            paths["intake_manifest"] = paths["combined_jsonl"]
            workspace = write_manifest(Path(directory), value)

            with self.assertRaisesRegex(
                ValueError,
                "artifact paths must be distinct",
            ):
                assemble_workspace._load_workspace(workspace)

    def test_rejects_review_json_collision_with_combined_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = manifest()
            paths = value["paths"]
            assert isinstance(paths, dict)
            paths["combined_jsonl"] = "review/refrigerator-review.json"
            workspace = write_manifest(Path(directory), value)

            with self.assertRaisesRegex(
                ValueError,
                "artifact paths must be distinct",
            ):
                assemble_workspace._load_workspace(workspace)

    def test_generated_layout_remains_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_manifest(Path(directory), manifest())

            loaded, incoming, combined, intake = assemble_workspace._load_workspace(
                workspace
            )

            self.assertEqual(loaded["route_id"], "refrigerator-v1")
            self.assertEqual(incoming, workspace / "incoming-sessions")
            self.assertEqual(
                combined,
                workspace / "verified" / "anonymous-sessions.jsonl",
            )
            self.assertEqual(
                intake,
                workspace / "verified" / "intake-manifest.json",
            )


if __name__ == "__main__":
    unittest.main()
