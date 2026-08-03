from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
sys.path.insert(0, str(EVALUATION_DIR))

import prepare_workspace  # noqa: E402

BUILD_ID = "a" * 64


def symlink(path: Path, target: Path, *, directory: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.symlink_to(target, target_is_directory=directory)
    except OSError as exc:
        raise unittest.SkipTest(f"symlinks unavailable: {exc}") from exc


class ProductAlphaWorkspaceDestinationBoundaryTests(unittest.TestCase):
    def test_creation_refuses_broken_destination_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            destination = root / "cohort"
            missing_target = root / "missing-target"
            symlink(destination, missing_target)

            with self.assertRaisesRegex(
                FileExistsError,
                "workspace already exists",
            ):
                prepare_workspace.prepare_workspace(destination, BUILD_ID)

            self.assertTrue(destination.is_symlink())
            self.assertFalse(missing_target.exists())

    def test_creation_does_not_follow_destination_leaf_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            destination = root / "cohort"
            external_target = root / "external-workspace"
            symlink(destination, external_target, directory=True)

            with self.assertRaisesRegex(
                FileExistsError,
                "workspace already exists",
            ):
                prepare_workspace.prepare_workspace(destination, BUILD_ID)

            self.assertTrue(destination.is_symlink())
            self.assertFalse(external_target.exists())

    def test_parent_symlink_into_repository_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repository"
            repository.mkdir()
            linked_parent = root / "linked-parent"
            symlink(linked_parent, repository, directory=True)
            destination = linked_parent / "private-workspace"

            with self.assertRaisesRegex(
                ValueError,
                "workspace must be outside the repository",
            ):
                prepare_workspace.prepare_workspace(
                    destination,
                    BUILD_ID,
                    repo_root=repository,
                )

            self.assertFalse((repository / "private-workspace").exists())

    def test_normal_creation_still_uses_requested_leaf(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "cohort"

            manifest = prepare_workspace.prepare_workspace(destination, BUILD_ID)

            self.assertEqual(manifest["pilot_build_id"], BUILD_ID)
            self.assertTrue((destination / "workspace.json").is_file())
            self.assertTrue((destination / "README.md").is_file())
            self.assertTrue((destination / "incoming-sessions").is_dir())


if __name__ == "__main__":
    unittest.main()
