from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "product_alpha" / "run_pilot.py"
SPEC = importlib.util.spec_from_file_location("product_alpha_pilot_smoke", MODULE_PATH)
assert SPEC and SPEC.loader
launcher = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = launcher
SPEC.loader.exec_module(launcher)


class ProductAlphaPilotSmokeTests(unittest.TestCase):
    def test_real_packaged_build_passes_loopback_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            launcher.run_builder("build", output)
            build_id = launcher.pilot_build_identity(output)
            report = launcher.smoke_served_output(output, build_id)

        self.assertEqual(report["contract"], "principia-product-alpha-pilot-smoke/0.1")
        self.assertEqual(report["decision"], "pilot-smoke-passed")
        self.assertEqual(report["host"], launcher.LOOPBACK_HOST)
        self.assertEqual(report["build_id"], build_id)
        self.assertEqual(report["target_count"], 5)
        self.assertEqual(
            report["targets"],
            ["learner", "facilitator", "pilot_lab", "route", "manifest"],
        )
        self.assertEqual(
            report["headers_verified"],
            sorted(launcher.SMOKE_REQUIRED_HEADERS),
        )
        self.assertFalse(report["session_data_stored"])

    def test_smoke_rejects_missing_packaged_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            launcher.run_builder("build", output)
            build_id = launcher.pilot_build_identity(output)
            pilot_lab = output / "pilot-lab.html"
            data = pilot_lab.read_bytes()
            marker = b"EXPECTED_BUILD_ID=new URLSearchParams"
            self.assertIn(marker, data)
            pilot_lab.write_bytes(data.replace(marker, b"BROKEN_BUILD_BINDING", 1))
            with self.assertRaisesRegex(ValueError, "missing its packaged marker"):
                launcher.smoke_served_output(output, build_id)

    def test_smoke_rejects_invalid_expected_build_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            launcher.run_builder("build", output)
            with self.assertRaisesRegex(ValueError, "64-character lowercase SHA-256"):
                launcher.smoke_served_output(output, "not-a-build-id")

    def test_pilot_day_smoke_command_is_end_to_end(self) -> None:
        first = subprocess.run(
            [sys.executable, str(MODULE_PATH), "smoke"],
            check=True,
            capture_output=True,
            text=True,
        )
        second = subprocess.run(
            [sys.executable, str(MODULE_PATH), "smoke"],
            check=True,
            capture_output=True,
            text=True,
        )
        first_line = next(
            line for line in first.stdout.splitlines() if line.startswith("Product Alpha pilot smoke passed:")
        )
        second_line = next(
            line for line in second.stdout.splitlines() if line.startswith("Product Alpha pilot smoke passed:")
        )
        self.assertEqual(first_line, second_line)
        self.assertIn("host=127.0.0.1", first_line)
        self.assertIn("targets=5", first_line)
        self.assertIn("session_data_stored=false", first_line)
        self.assertRegex(first_line, r"build_id=[0-9a-f]{64}")


if __name__ == "__main__":
    unittest.main()
