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


class ProductAlphaIncomingDirectoryBoundaryTests(unittest.TestCase):
    def test_preflight_rejects_symlinked_incoming_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "cohort"
            workspace.mkdir()
            (workspace / "verified").mkdir()
            (workspace / "review").mkdir()
            external = root / "external-incoming"
            external.mkdir()
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
            try:
                (workspace / "incoming-sessions").symlink_to(
                    external,
                    target_is_directory=True,
                )
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")

            with self.assertRaisesRegex(
                ValueError,
                "incoming session directory must be a regular directory",
            ):
                assemble_workspace.preflight_workspace(workspace)

            self.assertEqual(list((workspace / "verified").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
