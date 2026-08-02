from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PRODUCT_ALPHA = Path(__file__).resolve().parents[1] / "product_alpha"
sys.path.insert(0, str(PRODUCT_ALPHA))

import launch_workspace  # noqa: E402

BUILD_ID = "a" * 64
OTHER_BUILD_ID = "b" * 64


def workspace_manifest(build_id: str = BUILD_ID) -> dict[str, object]:
    return {
        "contract": "principia-product-alpha-pilot-workspace/0.1",
        "pilot_build_id": build_id,
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


def create_workspace(root: Path, build_id: str = BUILD_ID) -> Path:
    workspace = root / "cohort"
    workspace.mkdir(parents=True)
    (workspace / "workspace.json").write_text(
        json.dumps(workspace_manifest(build_id), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return workspace


class ProductAlphaWorkspaceLaunchTests(unittest.TestCase):
    def test_loads_repository_external_workspace_binding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repository"
            repository.mkdir()
            workspace = create_workspace(root)

            binding = launch_workspace.load_workspace_binding(
                workspace,
                repo_root=repository,
            )

            self.assertEqual(binding["workspace"], str(workspace.resolve()))
            self.assertEqual(binding["pilot_build_id"], BUILD_ID)
            self.assertEqual(binding["route_id"], "refrigerator-v1")

    def test_rejects_workspace_inside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            repository.mkdir()
            workspace = create_workspace(repository)

            with self.assertRaisesRegex(ValueError, "outside the repository"):
                launch_workspace.load_workspace_binding(
                    workspace,
                    repo_root=repository,
                )

    def test_rejects_relaxed_privacy_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repository"
            repository.mkdir()
            workspace = create_workspace(root)
            manifest_path = workspace / "workspace.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["privacy_boundaries"]["participant_names_allowed"] = True
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "privacy boundary"):
                launch_workspace.load_workspace_binding(
                    workspace,
                    repo_root=repository,
                )

    def test_prepares_exact_workspace_bound_build(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            output = Path(directory) / "dist"
            with (
                mock.patch.object(launch_workspace.run_pilot, "run_builder") as build,
                mock.patch.object(launch_workspace.run_pilot, "verify_output") as verify,
                mock.patch.object(
                    launch_workspace.run_pilot,
                    "pilot_build_identity",
                    return_value=BUILD_ID,
                ) as identity,
            ):
                report = launch_workspace.prepare_workspace_launch(workspace, output)

            build.assert_called_once_with("build", output.resolve())
            verify.assert_called_once_with(output.resolve())
            identity.assert_called_once_with(output.resolve())
            self.assertEqual(
                report["contract"],
                "principia-product-alpha-workspace-launch/0.1",
            )
            self.assertEqual(report["decision"], "workspace-build-bound")
            self.assertEqual(report["pilot_build_id"], BUILD_ID)
            self.assertEqual(report["workspace"], str(workspace.resolve()))
            self.assertFalse(report["session_data_stored"])
            self.assertFalse(report["workspace_manifest_modified"])

    def test_rejects_build_mismatch_before_server_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            output = Path(directory) / "dist"
            with (
                mock.patch.object(launch_workspace.run_pilot, "run_builder"),
                mock.patch.object(launch_workspace.run_pilot, "verify_output"),
                mock.patch.object(
                    launch_workspace.run_pilot,
                    "pilot_build_identity",
                    return_value=OTHER_BUILD_ID,
                ),
                mock.patch.object(
                    launch_workspace.run_pilot,
                    "create_server",
                ) as create_server,
            ):
                with self.assertRaisesRegex(ValueError, "does not match workspace"):
                    launch_workspace.launch(
                        workspace,
                        output,
                        0,
                        False,
                        True,
                    )

            create_server.assert_not_called()

    def test_check_command_reports_binding_without_serving(self) -> None:
        report = {
            "contract": "principia-product-alpha-workspace-launch/0.1",
            "decision": "workspace-build-bound",
            "pilot_build_id": BUILD_ID,
        }
        with (
            mock.patch.object(
                launch_workspace,
                "prepare_workspace_launch",
                return_value=report,
            ),
            mock.patch.object(launch_workspace, "launch") as launch,
            contextlib.redirect_stdout(io.StringIO()) as stdout,
        ):
            result = launch_workspace.main(
                [
                    "check",
                    "--workspace",
                    "/private/cohort",
                    "--output",
                    "/tmp/product-alpha",
                ]
            )

        self.assertEqual(result, 0)
        self.assertEqual(json.loads(stdout.getvalue()), report)
        launch.assert_not_called()

    def test_source_has_no_external_or_persistent_session_path(self) -> None:
        source = (PRODUCT_ALPHA / "launch_workspace.py").read_text(encoding="utf-8")
        self.assertNotIn('"0.0.0.0"', source)
        self.assertNotIn("localStorage", source)
        self.assertNotIn("sessionStorage", source)
        self.assertNotIn("requests.", source)
        self.assertIn("workspace must be outside the repository", source)
        self.assertIn("no session data is stored", source)


if __name__ == "__main__":
    unittest.main()
