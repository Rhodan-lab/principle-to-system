from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
sys.path.insert(0, str(EVALUATION_DIR))

import prepare_handoff  # noqa: E402
import prepare_review  # noqa: E402


class ProductAlphaExclusiveStagingTests(unittest.TestCase):
    def _assert_review_preserves_competing_stage(self, stage_index: int) -> None:
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "private" / "review"
            json_path = prefix.with_suffix(".json")
            markdown_path = prefix.with_suffix(".md")
            temporary_paths = (
                json_path.with_name(f".{json_path.name}.tmp-{os.getpid()}"),
                markdown_path.with_name(f".{markdown_path.name}.tmp-{os.getpid()}"),
            )
            competitor = temporary_paths[stage_index]
            competitor_bytes = b"competing review stage\n"
            real_open = Path.open

            def controlled_open(
                path: Path,
                *args: object,
                **kwargs: object,
            ) -> object:
                mode = args[0] if args else kwargs.get("mode", "r")
                if path == competitor and mode == "xb":
                    with real_open(path, "wb") as stream:
                        stream.write(competitor_bytes)
                return real_open(path, *args, **kwargs)

            with (
                mock.patch.object(prepare_review, "canonical_json", return_value=b"{}\n"),
                mock.patch.object(prepare_review, "render_markdown", return_value="review\n"),
                mock.patch.object(Path, "open", new=controlled_open),
            ):
                with self.assertRaises(FileExistsError):
                    prepare_review.write_review_outputs(prefix, {})

            self.assertEqual(competitor.read_bytes(), competitor_bytes)
            for index, path in enumerate(temporary_paths):
                if index != stage_index:
                    self.assertFalse(prepare_review.path_present(path))
            self.assertFalse(prepare_review.path_present(json_path))
            self.assertFalse(prepare_review.path_present(markdown_path))

    def _assert_handoff_preserves_competing_stage(self, stage_index: int) -> None:
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "private" / "handoff"
            json_path = prefix.with_suffix(".json")
            markdown_path = prefix.with_suffix(".md")
            temporary_paths = (
                json_path.with_name(f".{json_path.name}.tmp-{os.getpid()}"),
                markdown_path.with_name(f".{markdown_path.name}.tmp-{os.getpid()}"),
            )
            competitor = temporary_paths[stage_index]
            competitor_bytes = b"competing handoff stage\n"
            real_open = Path.open

            def controlled_open(
                path: Path,
                *args: object,
                **kwargs: object,
            ) -> object:
                mode = args[0] if args else kwargs.get("mode", "r")
                if path == competitor and mode == "xb":
                    with real_open(path, "wb") as stream:
                        stream.write(competitor_bytes)
                return real_open(path, *args, **kwargs)

            with (
                mock.patch.object(prepare_handoff, "build_handoff_candidate", return_value={}),
                mock.patch.object(
                    prepare_handoff.prepare_review,
                    "canonical_json",
                    return_value=b"{}\n",
                ),
                mock.patch.object(prepare_handoff, "render_markdown", return_value="handoff\n"),
                mock.patch.object(Path, "open", new=controlled_open),
            ):
                with self.assertRaises(FileExistsError):
                    prepare_handoff.write_handoff(Path("unused"), prefix)

            self.assertEqual(competitor.read_bytes(), competitor_bytes)
            for index, path in enumerate(temporary_paths):
                if index != stage_index:
                    self.assertFalse(prepare_review.path_present(path))
            self.assertFalse(prepare_review.path_present(json_path))
            self.assertFalse(prepare_review.path_present(markdown_path))

    def test_review_preserves_competing_first_stage(self) -> None:
        self._assert_review_preserves_competing_stage(0)

    def test_review_preserves_competing_second_stage(self) -> None:
        self._assert_review_preserves_competing_stage(1)

    def test_handoff_preserves_competing_first_stage(self) -> None:
        self._assert_handoff_preserves_competing_stage(0)

    def test_handoff_preserves_competing_second_stage(self) -> None:
        self._assert_handoff_preserves_competing_stage(1)


if __name__ == "__main__":
    unittest.main()
