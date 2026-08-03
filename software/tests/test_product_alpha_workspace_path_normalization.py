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


class ProductAlphaWorkspacePathNormalizationTests(unittest.TestCase):
    def test_member_rejects_ambiguous_components(self) -> None:
        cases = (
            ".",
            "..",
            "verified/..",
            "verified/./cohort.jsonl",
            "verified//cohort.jsonl",
            "verified/",
            "verified\\..\\outside.json",
        )
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            for relative in cases:
                with self.subTest(relative=relative):
                    with self.assertRaisesRegex(
                        ValueError,
                        "must use normalized relative components",
                    ):
                        assemble_workspace._member(
                            workspace,
                            relative,
                            "test_path",
                        )

    def test_member_preserves_safe_nested_leaf(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()

            candidate = assemble_workspace._member(
                workspace,
                "verified/anonymous-sessions.jsonl",
                "combined_jsonl",
            )

            self.assertEqual(
                candidate,
                workspace / "verified" / "anonymous-sessions.jsonl",
            )

    def test_workspace_load_rejects_final_parent_component(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "cohort"
            workspace.mkdir()
            value = manifest()
            paths = value["paths"]
            assert isinstance(paths, dict)
            paths["combined_jsonl"] = "verified/.."
            (workspace / "workspace.json").write_text(
                json.dumps(value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "combined_jsonl path must use normalized relative components",
            ):
                assemble_workspace._load_workspace(workspace.resolve())

    def test_workspace_load_keeps_generated_paths_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "cohort"
            workspace.mkdir()
            (workspace / "workspace.json").write_text(
                json.dumps(manifest(), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            loaded, incoming, combined, intake = assemble_workspace._load_workspace(
                workspace.resolve()
            )

            self.assertEqual(loaded["route_id"], "refrigerator-v1")
            self.assertEqual(incoming, workspace.resolve() / "incoming-sessions")
            self.assertEqual(
                combined,
                workspace.resolve() / "verified" / "anonymous-sessions.jsonl",
            )
            self.assertEqual(
                intake,
                workspace.resolve() / "verified" / "intake-manifest.json",
            )


if __name__ == "__main__":
    unittest.main()
