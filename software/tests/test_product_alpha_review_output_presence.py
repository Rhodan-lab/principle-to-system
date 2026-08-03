from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
sys.path.insert(0, str(EVALUATION_DIR))

import prepare_review  # noqa: E402

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


def packet(root: Path) -> dict[str, object]:
    input_path = root / "sessions.jsonl"
    input_path.write_text(
        json.dumps(session(), sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return prepare_review.build_review_packet(input_path, BUILD_ID)


def broken_symlink(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.symlink_to(path.parent / "missing-target")
    except OSError as exc:
        raise unittest.SkipTest(f"symlinks unavailable: {exc}") from exc


class ProductAlphaReviewOutputPresenceTests(unittest.TestCase):
    def test_output_paths_refuse_broken_destination_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "review" / "refrigerator-review"
            json_path = prefix.with_suffix(".json")
            broken_symlink(json_path)

            with self.assertRaisesRegex(
                FileExistsError,
                "refusing to overwrite existing review output",
            ):
                prepare_review.review_output_paths(prefix)

            self.assertTrue(json_path.is_symlink())

    def test_output_prefix_leaf_symlink_does_not_redirect_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            private = root / "private"
            private.mkdir()
            external = root / "external-prefix"
            prefix = private / "refrigerator-review"
            try:
                prefix.symlink_to(external)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")

            json_path, markdown_path = prepare_review.review_output_paths(prefix)

            self.assertEqual(json_path, private / "refrigerator-review.json")
            self.assertEqual(markdown_path, private / "refrigerator-review.md")
            self.assertNotEqual(json_path, external.with_suffix(".json"))

    def test_writer_refuses_broken_temporary_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prefix = root / "review" / "refrigerator-review"
            json_path = prefix.with_suffix(".json")
            temporary_json = json_path.with_name(
                f".{json_path.name}.tmp-{os.getpid()}"
            )
            broken_symlink(temporary_json)

            with self.assertRaisesRegex(
                FileExistsError,
                "temporary review output already exists",
            ):
                prepare_review.write_review_outputs(prefix, packet(root))

            self.assertTrue(temporary_json.is_symlink())
            self.assertFalse(json_path.exists())
            self.assertFalse(prefix.with_suffix(".md").exists())


if __name__ == "__main__":
    unittest.main()
