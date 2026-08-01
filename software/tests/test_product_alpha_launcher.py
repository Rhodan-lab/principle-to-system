from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "product_alpha" / "run_pilot.py"
SPEC = importlib.util.spec_from_file_location("product_alpha_run_pilot", MODULE_PATH)
assert SPEC and SPEC.loader
launcher = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = launcher
SPEC.loader.exec_module(launcher)


class ProductAlphaLauncherTests(unittest.TestCase):
    def test_urls_are_loopback_only(self) -> None:
        self.assertEqual(
            launcher.pilot_urls(8123),
            {
                "learner": "http://127.0.0.1:8123/",
                "facilitator": "http://127.0.0.1:8123/facilitator.html",
                "pilot_lab": "http://127.0.0.1:8123/pilot-lab.html",
            },
        )

    def test_urls_bind_local_cohort_tools_to_build_identity(self) -> None:
        build_id = "a" * 64
        self.assertEqual(
            launcher.pilot_urls(8123, build_id),
            {
                "learner": "http://127.0.0.1:8123/",
                "facilitator": (
                    "http://127.0.0.1:8123/facilitator.html?build_id=" + build_id
                ),
                "pilot_lab": (
                    "http://127.0.0.1:8123/pilot-lab.html?build_id=" + build_id
                ),
            },
        )
        with self.assertRaisesRegex(ValueError, "64-character lowercase SHA-256"):
            launcher.pilot_urls(8123, "not-a-build-id")

    def test_port_validation(self) -> None:
        self.assertEqual(launcher.validate_port(0), 0)
        self.assertEqual(launcher.validate_port(65535), 65535)
        with self.assertRaises(ValueError):
            launcher.validate_port(-1)
        with self.assertRaises(ValueError):
            launcher.validate_port(65536)

    def test_builder_uses_current_interpreter_and_repository_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with mock.patch.object(subprocess, "run") as run:
                launcher.run_builder("build", output)
            run.assert_called_once_with(
                [
                    sys.executable,
                    str(launcher.BUILD_SCRIPT),
                    "build",
                    "--root",
                    str(launcher.REPO_ROOT),
                    "--output",
                    str(output),
                ],
                check=True,
            )

    def test_server_binds_only_to_loopback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            server = launcher.create_server(Path(directory), 0, quiet=True)
            try:
                self.assertEqual(server.server_address[0], launcher.LOOPBACK_HOST)
                self.assertGreater(int(server.server_address[1]), 0)
            finally:
                server.server_close()

    def test_launcher_requires_pilot_lab_and_build_manifest_assets(self) -> None:
        self.assertIn("pilot-lab.html", launcher.REQUIRED_OUTPUTS)
        self.assertIn("facilitator.html", launcher.REQUIRED_OUTPUTS)
        self.assertIn("evaluation/rubric.json", launcher.REQUIRED_OUTPUTS)
        self.assertIn("build-manifest.json", launcher.REQUIRED_OUTPUTS)

    def test_pilot_build_identity_hashes_exact_valid_manifest_bytes(self) -> None:
        manifest = {
            "contract": "principia-product-alpha-build/0.1",
            "route_id": "refrigerator",
            "file_count": 1,
            "files": [{"path": "index.html", "sha256": "0" * 64}],
            "deterministic": True,
        }
        raw = (
            json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / launcher.BUILD_MANIFEST).write_bytes(raw)
            self.assertEqual(
                launcher.pilot_build_identity(output),
                hashlib.sha256(raw).hexdigest(),
            )

    def test_pilot_build_identity_rejects_missing_or_invalid_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with self.assertRaises(FileNotFoundError):
                launcher.pilot_build_identity(output)
            invalid = {
                "contract": "wrong-contract",
                "route_id": "refrigerator",
                "file_count": 0,
                "files": [],
                "deterministic": True,
            }
            (output / launcher.BUILD_MANIFEST).write_text(
                json.dumps(invalid),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "contract is invalid"):
                launcher.pilot_build_identity(output)

    def test_pilot_build_identity_rejects_inconsistent_file_count(self) -> None:
        manifest = {
            "contract": "principia-product-alpha-build/0.1",
            "route_id": "refrigerator",
            "file_count": 2,
            "files": [{"path": "index.html", "sha256": "0" * 64}],
            "deterministic": True,
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / launcher.BUILD_MANIFEST).write_text(
                json.dumps(manifest),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "file_count is inconsistent"):
                launcher.pilot_build_identity(output)

    def test_launcher_source_has_no_external_or_persistent_data_path(self) -> None:
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn('"0.0.0.0"', source)
        self.assertNotIn("localStorage", source)
        self.assertNotIn("sessionStorage", source)
        self.assertNotIn("urllib.request", source)
        self.assertNotIn("requests.", source)
        self.assertIn("no session data is stored", source)
        self.assertIn("every exported session carries this pilot build ID", source)


if __name__ == "__main__":
    unittest.main()
