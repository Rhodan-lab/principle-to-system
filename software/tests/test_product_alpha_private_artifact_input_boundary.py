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
import private_artifact  # noqa: E402
import record_decision  # noqa: E402


class ProductAlphaPrivateArtifactInputBoundaryTests(unittest.TestCase):
    def test_reads_exactly_bounded_regular_file(self) -> None:
        raw = b"bounded private artifact\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact.json"
            path.write_bytes(raw)

            result = private_artifact.read_regular_bytes(
                path,
                "private artifact",
                maximum_bytes=len(raw),
            )

        self.assertEqual(result, raw)

    def test_rejects_oversized_regular_file(self) -> None:
        raw = b"oversized private artifact\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact.json"
            path.write_bytes(raw)

            with self.assertRaisesRegex(
                ValueError,
                "Product Alpha private artifact limit",
            ):
                private_artifact.read_regular_bytes(
                    path,
                    "private artifact",
                    maximum_bytes=len(raw) - 1,
                )

    def test_rejects_symlink_without_reading_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "private-target.json"
            link = root / "artifact.json"
            target_bytes = b"target must not be followed\n"
            target.write_bytes(target_bytes)
            link.symlink_to(target)

            with self.assertRaisesRegex(ValueError, "must be a regular file"):
                private_artifact.read_regular_bytes(link, "private artifact")

            self.assertEqual(target.read_bytes(), target_bytes)

    @unittest.skipUnless(
        getattr(os, "O_NOFOLLOW", 0),
        "platform does not provide O_NOFOLLOW",
    )
    def test_rejects_path_replaced_by_symlink_during_open(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "artifact.json"
            target = root / "target.json"
            path.write_bytes(b"original\n")
            target_bytes = b"replacement target must not be read\n"
            target.write_bytes(target_bytes)
            real_open = os.open
            replaced = False

            def replace_then_open(candidate: Path, flags: int) -> int:
                nonlocal replaced
                if not replaced:
                    replaced = True
                    path.unlink()
                    path.symlink_to(target)
                return real_open(candidate, flags)

            with mock.patch.object(
                private_artifact.os,
                "open",
                side_effect=replace_then_open,
            ):
                with self.assertRaisesRegex(ValueError, "must be a regular file"):
                    private_artifact.read_regular_bytes(path, "private artifact")

            self.assertTrue(replaced)
            self.assertEqual(target.read_bytes(), target_bytes)

    def test_rejects_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact-directory"
            path.mkdir()

            with self.assertRaisesRegex(ValueError, "must be a regular file"):
                private_artifact.read_regular_bytes(path, "private artifact")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "platform does not provide FIFOs")
    def test_rejects_fifo_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact.fifo"
            os.mkfifo(path)

            with self.assertRaisesRegex(ValueError, "must be a regular file"):
                private_artifact.read_regular_bytes(path, "private artifact")

    def test_regular_file_uses_descriptor_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact.json"
            path.write_bytes(b"artifact\n")
            real_open = os.open

            with mock.patch.object(
                private_artifact.os,
                "open",
                wraps=real_open,
            ) as descriptor_open:
                private_artifact.read_regular_bytes(path, "private artifact")

        descriptor_open.assert_called_once()
        flags = descriptor_open.call_args.args[1]
        if getattr(os, "O_NOFOLLOW", 0):
            self.assertTrue(flags & os.O_NOFOLLOW)
        if getattr(os, "O_NONBLOCK", 0):
            self.assertTrue(flags & os.O_NONBLOCK)

    def test_decision_reader_delegates_to_shared_boundary(self) -> None:
        path = Path("/private/review.json")
        with mock.patch.object(
            record_decision.private_artifact,
            "read_regular_bytes",
            return_value=b"decision\n",
        ) as shared_read:
            result = record_decision._regular_bytes(path, "decision record JSON")

        self.assertEqual(result, b"decision\n")
        shared_read.assert_called_once_with(path, "decision record JSON")

    def test_handoff_reader_delegates_to_shared_boundary(self) -> None:
        path = Path("/private/handoff.json")
        with mock.patch.object(
            prepare_handoff.private_artifact,
            "read_regular_bytes",
            return_value=b"handoff\n",
        ) as shared_read:
            result = prepare_handoff._regular_bytes(path, "handoff JSON")

        self.assertEqual(result, b"handoff\n")
        shared_read.assert_called_once_with(path, "handoff JSON")


if __name__ == "__main__":
    unittest.main()
