from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ALPHA_DIR = REPO_ROOT / "software" / "product_alpha"
sys.path.insert(0, str(PRODUCT_ALPHA_DIR))

import package_integrity  # noqa: E402


def write_package(root: Path, route: str = "refrigerator") -> bytes:
    payloads = {
        path: f"package asset: {path}\n".encode("utf-8")
        for path in package_integrity.REQUIRED_STATIC_FILES
    }
    payloads[f"data/{route}.json"] = b'{}\n'
    entries: list[dict[str, str]] = []
    for relative, payload in payloads.items():
        path = root.joinpath(*relative.split("/"))
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
        "contract": package_integrity.BUILD_CONTRACT,
        "route_id": route,
        "file_count": len(entries),
        "files": entries,
        "deterministic": True,
    }
    raw = (
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    (root / package_integrity.BUILD_MANIFEST).write_bytes(raw)
    return raw


class ProductAlphaBuildPackageIntegrityTests(unittest.TestCase):
    def test_valid_exact_package_returns_manifest_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            raw = write_package(output)

            build_id = package_integrity.pilot_build_identity(output)

        self.assertEqual(build_id, hashlib.sha256(raw).hexdigest())

    def test_loader_returns_the_verified_package_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            raw = write_package(output)
            expected_index = (output / "index.html").read_bytes()

            manifest, manifest_raw, package = package_integrity.load_verified_package(
                output
            )
            (output / "index.html").write_bytes(b"changed after snapshot\n")

        self.assertEqual(manifest["route_id"], "refrigerator")
        self.assertEqual(manifest_raw, raw)
        self.assertEqual(package[package_integrity.BUILD_MANIFEST], raw)
        self.assertEqual(package["index.html"], expected_index)

    def test_rejects_mutated_declared_asset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_package(output)
            (output / "index.html").write_bytes(b"mutated learner asset\n")

            with self.assertRaisesRegex(ValueError, "SHA-256 does not match"):
                package_integrity.pilot_build_identity(output)

    def test_rejects_undeclared_file_in_served_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_package(output)
            (output / "private-notes.txt").write_text(
                "must not be served\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "undeclared=private-notes.txt"):
                package_integrity.pilot_build_identity(output)

    def test_rejects_missing_declared_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_package(output)
            (output / "model-adapters.js").unlink()

            with self.assertRaisesRegex(ValueError, "missing=model-adapters.js"):
                package_integrity.pilot_build_identity(output)

    def test_rejects_manifest_missing_required_route_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            raw = write_package(output)
            manifest = json.loads(raw)
            route_path = "data/refrigerator.json"
            manifest["files"] = [
                entry for entry in manifest["files"] if entry["path"] != route_path
            ]
            manifest["file_count"] = len(manifest["files"])
            (output / route_path).unlink()
            (output / package_integrity.BUILD_MANIFEST).write_text(
                json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "missing required package files: data/refrigerator.json",
            ):
                package_integrity.pilot_build_identity(output)

    def test_rejects_symlinked_package_asset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_package(output)
            asset = output / "index.html"
            target = Path(directory).parent / f"{output.name}-external-index.html"
            target.write_bytes(asset.read_bytes())
            asset.unlink()
            asset.symlink_to(target)
            try:
                with self.assertRaisesRegex(ValueError, "must not be a symlink"):
                    package_integrity.pilot_build_identity(output)
            finally:
                target.unlink(missing_ok=True)

    def test_rejects_duplicate_manifest_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            raw = write_package(output)
            duplicated = raw.replace(
                b'"route_id":',
                b'"contract":"duplicate","route_id":',
                1,
            )
            (output / package_integrity.BUILD_MANIFEST).write_bytes(duplicated)

            with self.assertRaisesRegex(ValueError, "duplicate JSON key: 'contract'"):
                package_integrity.pilot_build_identity(output)

    def test_rejects_unsafe_manifest_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            raw = write_package(output)
            manifest = json.loads(raw)
            manifest["files"][0]["path"] = "../escape.json"
            (output / package_integrity.BUILD_MANIFEST).write_text(
                json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "file path is unsafe"):
                package_integrity.pilot_build_identity(output)

    def test_rejects_asset_over_byte_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_package(output)
            asset_size = (output / "index.html").stat().st_size

            with mock.patch.object(
                package_integrity,
                "MAX_ASSET_BYTES",
                asset_size - 1,
            ):
                with self.assertRaisesRegex(ValueError, "build package limit"):
                    package_integrity.pilot_build_identity(output)

    def test_rejects_manifest_over_file_count_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            raw = write_package(output)
            declared_count = len(json.loads(raw)["files"])

            with mock.patch.object(
                package_integrity,
                "MAX_PACKAGE_FILES",
                declared_count - 1,
            ):
                with self.assertRaisesRegex(ValueError, "file package limit"):
                    package_integrity.load_verified_package(output)

    def test_rejects_snapshot_over_total_byte_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            raw = write_package(output)

            with mock.patch.object(
                package_integrity,
                "MAX_PACKAGE_BYTES",
                len(raw),
            ):
                with self.assertRaisesRegex(ValueError, "byte package limit"):
                    package_integrity.load_verified_package(output)


if __name__ == "__main__":
    unittest.main()
