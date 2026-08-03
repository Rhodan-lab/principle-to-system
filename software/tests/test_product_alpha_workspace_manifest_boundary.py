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


def empty_workspace(root: Path) -> Path:
    workspace = root / "cohort"
    (workspace / "incoming-sessions").mkdir(parents=True)
    (workspace / "verified").mkdir()
    (workspace / "review").mkdir()
    return workspace


class ProductAlphaWorkspaceManifestBoundaryTests(unittest.TestCase):
    def test_preflight_rejects_symlinked_workspace_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = empty_workspace(root)
            external = root / "external-workspace.json"
            external.write_text(
                json.dumps(manifest(), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            try:
                (workspace / "workspace.json").symlink_to(external)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")

            with self.assertRaisesRegex(
                ValueError,
                "workspace.json: must be a regular file",
            ):
                assemble_workspace.preflight_workspace(workspace)

            self.assertEqual(list((workspace / "verified").iterdir()), [])

    def test_preflight_rejects_non_utf8_workspace_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = empty_workspace(Path(directory))
            (workspace / "workspace.json").write_bytes(b"\xff\xfe\x00")

            with self.assertRaisesRegex(
                ValueError,
                "workspace.json: must be UTF-8",
            ):
                assemble_workspace.preflight_workspace(workspace)

            self.assertEqual(list((workspace / "verified").iterdir()), [])

    def test_preflight_rejects_non_object_workspace_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = empty_workspace(Path(directory))
            (workspace / "workspace.json").write_text(
                "[]\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "workspace.json: must contain one JSON object",
            ):
                assemble_workspace.preflight_workspace(workspace)

            self.assertEqual(list((workspace / "verified").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
