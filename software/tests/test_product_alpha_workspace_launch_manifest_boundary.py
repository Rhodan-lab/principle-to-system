from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PRODUCT_ALPHA = Path(__file__).resolve().parents[1] / "product_alpha"
sys.path.insert(0, str(PRODUCT_ALPHA))

import launch_workspace  # noqa: E402

BUILD_ID = "a" * 64


def manifest_value() -> dict[str, object]:
    return {
        "contract": launch_workspace.WORKSPACE_CONTRACT,
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


def encoded_manifest() -> bytes:
    return (
        json.dumps(manifest_value(), sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def create_environment(root: Path) -> tuple[Path, Path, Path]:
    repository = root / "repository"
    repository.mkdir()
    workspace = root / "cohort"
    workspace.mkdir()
    manifest = workspace / "workspace.json"
    manifest.write_bytes(encoded_manifest())
    return repository, workspace, manifest


class ProductAlphaWorkspaceLaunchManifestBoundaryTests(unittest.TestCase):
    def test_regular_manifest_uses_descriptor_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, workspace, manifest = create_environment(Path(directory))
            real_open = os.open

            with mock.patch.object(
                launch_workspace.os,
                "open",
                wraps=real_open,
            ) as descriptor_open:
                binding = launch_workspace.load_workspace_binding(
                    workspace,
                    repo_root=repository,
                )

        self.assertEqual(binding["pilot_build_id"], BUILD_ID)
        descriptor_open.assert_called_once()
        self.assertEqual(Path(descriptor_open.call_args.args[0]), manifest)
        flags = descriptor_open.call_args.args[1]
        if getattr(os, "O_NOFOLLOW", 0):
            self.assertTrue(flags & os.O_NOFOLLOW)
        if getattr(os, "O_NONBLOCK", 0):
            self.assertTrue(flags & os.O_NONBLOCK)

    def test_rejects_symlinked_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, workspace, manifest = create_environment(root)
            target = root / "target-workspace.json"
            target_bytes = encoded_manifest()
            target.write_bytes(target_bytes)
            manifest.unlink()
            manifest.symlink_to(target)

            with self.assertRaisesRegex(ValueError, "must be a regular file"):
                launch_workspace.load_workspace_binding(
                    workspace,
                    repo_root=repository,
                )

            self.assertEqual(target.read_bytes(), target_bytes)

    @unittest.skipUnless(
        getattr(os, "O_NOFOLLOW", 0),
        "platform does not provide O_NOFOLLOW",
    )
    def test_rejects_manifest_replaced_by_symlink_during_open(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, workspace, manifest = create_environment(root)
            target = root / "replacement-workspace.json"
            target_bytes = encoded_manifest()
            target.write_bytes(target_bytes)
            real_open = os.open
            replaced = False

            def replace_then_open(path: Path, flags: int) -> int:
                nonlocal replaced
                if not replaced:
                    replaced = True
                    manifest.unlink()
                    manifest.symlink_to(target)
                return real_open(path, flags)

            with mock.patch.object(
                launch_workspace.os,
                "open",
                side_effect=replace_then_open,
            ):
                with self.assertRaisesRegex(ValueError, "must be a regular file"):
                    launch_workspace.load_workspace_binding(
                        workspace,
                        repo_root=repository,
                    )

            self.assertTrue(replaced)
            self.assertEqual(target.read_bytes(), target_bytes)

    def test_rejects_directory_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, workspace, manifest = create_environment(Path(directory))
            manifest.unlink()
            manifest.mkdir()

            with self.assertRaisesRegex(ValueError, "must be a regular file"):
                launch_workspace.load_workspace_binding(
                    workspace,
                    repo_root=repository,
                )

    @unittest.skipUnless(hasattr(os, "mkfifo"), "platform does not provide FIFOs")
    def test_rejects_fifo_manifest_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, workspace, manifest = create_environment(Path(directory))
            manifest.unlink()
            os.mkfifo(manifest)

            with self.assertRaisesRegex(ValueError, "must be a regular file"):
                launch_workspace.load_workspace_binding(
                    workspace,
                    repo_root=repository,
                )

    def test_rejects_oversized_manifest(self) -> None:
        raw = encoded_manifest()
        with tempfile.TemporaryDirectory() as directory:
            repository, workspace, _ = create_environment(Path(directory))

            with mock.patch.object(
                launch_workspace,
                "MAX_WORKSPACE_MANIFEST_BYTES",
                len(raw) - 1,
            ):
                with self.assertRaisesRegex(ValueError, "Product Alpha workspace limit"):
                    launch_workspace.load_workspace_binding(
                        workspace,
                        repo_root=repository,
                    )

    def test_rejects_non_utf8_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, workspace, manifest = create_environment(Path(directory))
            manifest.write_bytes(b"\xff\xfe\x00")

            with self.assertRaisesRegex(ValueError, "workspace.json must be UTF-8"):
                launch_workspace.load_workspace_binding(
                    workspace,
                    repo_root=repository,
                )

    def test_rejects_duplicate_top_level_key(self) -> None:
        raw = encoded_manifest().replace(
            b'{"contract":',
            b'{"contract":"duplicate","contract":',
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            repository, workspace, manifest = create_environment(Path(directory))
            manifest.write_bytes(raw)

            with self.assertRaisesRegex(ValueError, "duplicate JSON key: 'contract'"):
                launch_workspace.load_workspace_binding(
                    workspace,
                    repo_root=repository,
                )

    def test_rejects_duplicate_nested_privacy_key(self) -> None:
        raw = encoded_manifest().replace(
            b'"participant_names_allowed":false',
            (
                b'"participant_names_allowed":true,'
                b'"participant_names_allowed":false'
            ),
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            repository, workspace, manifest = create_environment(Path(directory))
            manifest.write_bytes(raw)

            with self.assertRaisesRegex(
                ValueError,
                "duplicate JSON key: 'participant_names_allowed'",
            ):
                launch_workspace.load_workspace_binding(
                    workspace,
                    repo_root=repository,
                )

    def test_rejects_nonfinite_json_value(self) -> None:
        raw = encoded_manifest().replace(b"}\n", b',"unexpected":NaN}\n', 1)
        with tempfile.TemporaryDirectory() as directory:
            repository, workspace, manifest = create_environment(Path(directory))
            manifest.write_bytes(raw)

            with self.assertRaisesRegex(ValueError, "non-finite JSON constant"):
                launch_workspace.load_workspace_binding(
                    workspace,
                    repo_root=repository,
                )


if __name__ == "__main__":
    unittest.main()
