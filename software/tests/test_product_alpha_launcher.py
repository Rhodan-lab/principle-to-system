from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "product_alpha" / "run_pilot.py"
SPEC = importlib.util.spec_from_file_location("product_alpha_run_pilot", MODULE_PATH)
assert SPEC and SPEC.loader
launcher = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = launcher
SPEC.loader.exec_module(launcher)


def write_valid_package(output: Path, route: str = "refrigerator") -> bytes:
    payloads = {
        path: f"launcher package asset: {path}\n".encode("utf-8")
        for path in launcher.package_integrity.REQUIRED_STATIC_FILES
    }
    payloads[f"data/{route}.json"] = b'{}\n'
    entries: list[dict[str, str]] = []
    for relative, payload in payloads.items():
        path = output.joinpath(*relative.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        entries.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    entries.sort(key=lambda item: item["path"])
    manifest = {
        "contract": launcher.package_integrity.BUILD_CONTRACT,
        "route_id": route,
        "file_count": len(entries),
        "files": entries,
        "deterministic": True,
    }
    raw = (
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    (output / launcher.BUILD_MANIFEST).write_bytes(raw)
    return raw


def start_server(server: object) -> threading.Thread:
    thread = threading.Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.01},
        daemon=True,
    )
    thread.start()
    return thread


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
            output = Path(directory)
            raw = write_valid_package(output)
            build_id = hashlib.sha256(raw).hexdigest()
            server = launcher.create_server(output, 0, build_id, quiet=True)
            try:
                self.assertEqual(server.server_address[0], launcher.LOOPBACK_HOST)
                self.assertGreater(int(server.server_address[1]), 0)
            finally:
                server.server_close()

    def test_server_serves_verified_snapshot_after_filesystem_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            raw = write_valid_package(output)
            build_id = hashlib.sha256(raw).hexdigest()
            original = (output / "index.html").read_bytes()
            server = launcher.create_server(output, 0, build_id, quiet=True)
            (output / "index.html").write_bytes(b"mutated after snapshot\n")
            (output / "facilitator.html").unlink()
            thread = start_server(server)
            try:
                port = int(server.server_address[1])
                status, _, body = launcher._fetch_smoke_target(port, "/")
                facilitator_status, _, facilitator_body = launcher._fetch_smoke_target(
                    port,
                    "/facilitator.html?build_id=" + build_id,
                )
            finally:
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()

        self.assertEqual(status, 200)
        self.assertEqual(body, original)
        self.assertEqual(facilitator_status, 200)
        self.assertEqual(
            facilitator_body,
            b"launcher package asset: facilitator.html\n",
        )

    def test_server_rejects_undeclared_and_directory_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            raw = write_valid_package(output)
            build_id = hashlib.sha256(raw).hexdigest()
            server = launcher.create_server(output, 0, build_id, quiet=True)
            thread = start_server(server)
            try:
                port = int(server.server_address[1])
                undeclared_status, _, _ = launcher._fetch_smoke_target(
                    port,
                    "/private-notes.txt",
                )
                directory_status, _, _ = launcher._fetch_smoke_target(port, "/data/")
            finally:
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()

        self.assertEqual(undeclared_status, 404)
        self.assertEqual(directory_status, 404)

    def test_server_rejects_build_id_mismatch_before_socket_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_valid_package(output)
            with mock.patch.object(
                launcher.snapshot_server,
                "ThreadingHTTPServer",
            ) as server_class:
                with self.assertRaisesRegex(
                    ValueError,
                    "does not match the expected Pilot build ID",
                ):
                    launcher.create_server(output, 0, "a" * 64, quiet=True)

            server_class.assert_not_called()

    def test_launcher_requires_pilot_lab_and_build_manifest_assets(self) -> None:
        self.assertIn("pilot-lab.html", launcher.REQUIRED_OUTPUTS)
        self.assertIn("facilitator.html", launcher.REQUIRED_OUTPUTS)
        self.assertIn("evaluation/rubric.json", launcher.REQUIRED_OUTPUTS)
        self.assertIn("build-manifest.json", launcher.REQUIRED_OUTPUTS)

    def test_pilot_build_identity_hashes_exact_valid_manifest_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            raw = write_valid_package(output)
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

    def test_smoke_rejects_mutated_package_before_server_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            raw = write_valid_package(output)
            build_id = hashlib.sha256(raw).hexdigest()
            (output / "index.html").write_bytes(b"mutated after identity\n")

            with mock.patch.object(launcher, "create_server") as create_server:
                with self.assertRaisesRegex(ValueError, "SHA-256 does not match"):
                    launcher.smoke_served_output(output, build_id)

            create_server.assert_not_called()

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
