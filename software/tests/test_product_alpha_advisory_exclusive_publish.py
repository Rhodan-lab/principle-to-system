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

import prepare_review  # noqa: E402
import record_decision  # noqa: E402

BUILD_ID = "a" * 64
HASH = "b" * 64

READINESS: dict[str, object] = {
    "workspace": "/private/workspace",
    "pilot_build_id": BUILD_ID,
    "route_id": "refrigerator-v1",
    "review_json_sha256": HASH,
    "review_markdown_sha256": HASH,
    "combined_sha256": HASH,
    "intake_manifest_sha256": HASH,
    "source_records_sha256": HASH,
    "source_record_count": 1,
}
RECORD: dict[str, object] = {
    "human_decision": {"primary_action": "hold-current-route"},
}


def paths(prefix: Path) -> tuple[Path, Path, Path]:
    return record_decision._decision_paths(prefix)


def temporary_paths(prefix: Path) -> tuple[Path, Path, Path]:
    return tuple(
        path.with_name(f".{path.name}.tmp-{os.getpid()}") for path in paths(prefix)
    )


def write(prefix: Path) -> tuple[Path, Path, Path, str, str]:
    with mock.patch.object(
        record_decision,
        "render_markdown",
        return_value="advisory record\n",
    ):
        return record_decision.write_decision_outputs(prefix, READINESS, RECORD)


class ProductAlphaAdvisoryExclusivePublishTests(unittest.TestCase):
    def test_successful_publication_leaves_no_temporary_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "review" / "refrigerator-review"

            result = write(prefix)

            for path in result[:3]:
                self.assertTrue(Path(path).is_file())
            for temporary in temporary_paths(prefix):
                self.assertFalse(temporary.exists())

    def test_second_publish_failure_rolls_back_owned_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "review" / "refrigerator-review"
            real_publish = prepare_review.publish_exclusive
            calls = 0

            def fail_second(staged: Path, destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated second advisory publish failure")
                real_publish(staged, destination)

            with mock.patch.object(
                prepare_review,
                "publish_exclusive",
                side_effect=fail_second,
            ):
                with self.assertRaisesRegex(OSError, "second advisory publish"):
                    write(prefix)

            for path in paths(prefix):
                self.assertFalse(path.exists())
            for temporary in temporary_paths(prefix):
                self.assertFalse(temporary.exists())

    def test_competing_markdown_destination_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "review" / "refrigerator-review"
            json_path, markdown_path, receipt_path = paths(prefix)
            real_publish = prepare_review.publish_exclusive
            calls = 0

            def publish_after_competitor(staged: Path, destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    destination.write_text("competing markdown\n", encoding="utf-8")
                real_publish(staged, destination)

            with mock.patch.object(
                prepare_review,
                "publish_exclusive",
                side_effect=publish_after_competitor,
            ):
                with self.assertRaises(FileExistsError):
                    write(prefix)

            self.assertFalse(json_path.exists())
            self.assertEqual(
                markdown_path.read_text(encoding="utf-8"),
                "competing markdown\n",
            )
            self.assertFalse(receipt_path.exists())
            for temporary in temporary_paths(prefix):
                self.assertFalse(temporary.exists())

    def test_competing_receipt_destination_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "review" / "refrigerator-review"
            json_path, markdown_path, receipt_path = paths(prefix)
            real_publish = prepare_review.publish_exclusive
            calls = 0

            def publish_after_competitor(staged: Path, destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 3:
                    destination.write_text("competing receipt\n", encoding="utf-8")
                real_publish(staged, destination)

            with mock.patch.object(
                prepare_review,
                "publish_exclusive",
                side_effect=publish_after_competitor,
            ):
                with self.assertRaises(FileExistsError):
                    write(prefix)

            self.assertFalse(json_path.exists())
            self.assertFalse(markdown_path.exists())
            self.assertEqual(
                receipt_path.read_text(encoding="utf-8"),
                "competing receipt\n",
            )
            for temporary in temporary_paths(prefix):
                self.assertFalse(temporary.exists())

    def test_preexisting_temporary_file_is_not_removed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "review" / "refrigerator-review"
            temp_json, temp_markdown, temp_receipt = temporary_paths(prefix)
            temp_markdown.parent.mkdir(parents=True)
            temp_markdown.write_text("competing temporary\n", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                write(prefix)

            self.assertFalse(temp_json.exists())
            self.assertEqual(
                temp_markdown.read_text(encoding="utf-8"),
                "competing temporary\n",
            )
            self.assertFalse(temp_receipt.exists())
            for path in paths(prefix):
                self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
