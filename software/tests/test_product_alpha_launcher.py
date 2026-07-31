from __future__ import annotations

import importlib.util
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
            },
        )

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

    def test_launcher_source_has_no_external_or_persistent_data_path(self) -> None:
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn('"0.0.0.0"', source)
        self.assertNotIn("localStorage", source)
        self.assertNotIn("sessionStorage", source)
        self.assertNotIn("urllib.request", source)
        self.assertNotIn("requests.", source)
        self.assertIn("no session data is stored", source)


if __name__ == "__main__":
    unittest.main()
