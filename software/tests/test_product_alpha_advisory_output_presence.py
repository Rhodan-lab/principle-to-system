from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
sys.path.insert(0, str(EVALUATION_DIR))

import record_decision  # noqa: E402


def broken_symlink(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.symlink_to(path.parent / "missing-target")
    except OSError as exc:
        raise unittest.SkipTest(f"symlinks unavailable: {exc}") from exc


class ProductAlphaAdvisoryOutputPresenceTests(unittest.TestCase):
    def test_decision_state_rejects_broken_partial_trio(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = (
                root / "review-decision.json",
                root / "review-decision.md",
                root / "review-decision-receipt.json",
            )
            broken_symlink(paths[0])

            with self.assertRaisesRegex(
                ValueError,
                "decision artifact trio is incomplete",
            ):
                record_decision._decision_output_state(paths)

    def test_decision_state_distinguishes_empty_and_complete_trios(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = (
                root / "review-decision.json",
                root / "review-decision.md",
                root / "review-decision-receipt.json",
            )
            self.assertFalse(record_decision._decision_output_state(paths))

            for path in paths:
                path.write_text("artifact\n", encoding="utf-8")

            self.assertTrue(record_decision._decision_output_state(paths))

    def test_decision_prefix_leaf_symlink_does_not_redirect_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            review_dir = root / "review"
            review_dir.mkdir()
            prefix = review_dir / "refrigerator-review"
            external = root / "external-prefix"
            try:
                prefix.symlink_to(external)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")

            paths = record_decision._decision_paths(prefix)

            self.assertEqual(
                paths[0],
                review_dir / "refrigerator-review-decision.json",
            )
            self.assertEqual(
                paths[2],
                review_dir / "refrigerator-review-decision-receipt.json",
            )
            self.assertNotEqual(paths[0], Path(f"{external}-decision.json"))

    def test_writer_refuses_broken_decision_destination_before_serializing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "review" / "refrigerator-review"
            json_path, markdown_path, receipt_path = record_decision._decision_paths(
                prefix
            )
            broken_symlink(json_path)

            with self.assertRaisesRegex(
                FileExistsError,
                "refusing to overwrite existing decision output",
            ):
                record_decision.write_decision_outputs(prefix, {}, {})

            self.assertTrue(json_path.is_symlink())
            self.assertFalse(markdown_path.exists())
            self.assertFalse(receipt_path.exists())


if __name__ == "__main__":
    unittest.main()
