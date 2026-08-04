from __future__ import annotations

import hashlib
import stat
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest import mock

from software.principia_atlas import orchestrate, release


class PrincipiaAtlasReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.product = self.root / "product"
        (self.product / "principia").mkdir(parents=True)
        (self.product / "atlas").mkdir(parents=True)
        (self.product / "index.html").write_text("release home\n", encoding="utf-8")
        (self.product / "principia/index.html").write_text("learn\n", encoding="utf-8")
        (self.product / "atlas/index.html").write_text("research\n", encoding="utf-8")
        orchestrate.receipt_path(self.product).write_text("{}\n", encoding="utf-8")
        self.product_manifest = {
            "bundle_id": "b" * 64,
            "principia": {
                "route_id": "distributed-information",
                "build_id": "p" * 64,
            },
        }
        self.receipt = {"receipt_id": "r" * 64}
        self.version = "0.1.0-alpha.1"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _verification(self):
        return mock.patch.object(
            release.orchestrate,
            "verify_product",
            return_value=(self.product_manifest, self.receipt),
        )

    @staticmethod
    def _rewrite_archive(
        source: Path,
        destination: Path,
        mutate,
        *,
        duplicate: str | None = None,
        symlink: str | None = None,
    ) -> None:
        with zipfile.ZipFile(source, "r") as current, zipfile.ZipFile(
            destination,
            "w",
            compression=zipfile.ZIP_STORED,
            allowZip64=False,
        ) as updated:
            for info in current.infolist():
                raw = mutate(info.filename, current.read(info))
                updated.writestr(info, raw)
            if duplicate is not None:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    updated.writestr(duplicate, b"duplicate\n")
            if symlink is not None:
                info = zipfile.ZipInfo(symlink, release.FIXED_ZIP_TIME)
                info.create_system = 3
                info.compress_type = zipfile.ZIP_STORED
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                updated.writestr(info, b"product/index.html")
        raw = destination.read_bytes()
        release.checksum_path(destination).write_text(
            f"{hashlib.sha256(raw).hexdigest()}  {destination.name}\n",
            encoding="ascii",
        )

    def test_pack_is_deterministic_and_standalone_verifier_runs(self) -> None:
        first = self.root / "first.zip"
        second = self.root / "second.zip"
        with self._verification():
            first_manifest = release.pack_product(
                product=self.product,
                version=self.version,
                output=first,
            )
            second_manifest = release.pack_product(
                product=self.product,
                version=self.version,
                output=second,
            )
            verified = release.verify_archive(first)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(first_manifest, second_manifest)
        self.assertEqual(verified["release_id"], first_manifest["release_id"])
        self.assertEqual(verified["bundle_id"], self.product_manifest["bundle_id"])
        with zipfile.ZipFile(first, "r") as archive:
            archive.extractall(self.root / "extracted")
        extracted = self.root / "extracted" / release.release_root(self.version)
        completed = subprocess.run(
            [sys.executable, str(extracted / "launcher.py"), "verify"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Verified Principia & Atlas release", completed.stdout)

    def test_checksum_tamper_is_rejected(self) -> None:
        archive = self.root / "release.zip"
        with self._verification():
            release.pack_product(
                product=self.product,
                version=self.version,
                output=archive,
            )
        raw = bytearray(archive.read_bytes())
        raw[-1] ^= 1
        archive.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, "checksum"):
            release.verify_archive(archive)

    def test_payload_tamper_is_rejected_even_with_new_checksum(self) -> None:
        original = self.root / "original.zip"
        tampered = self.root / "tampered.zip"
        with self._verification():
            release.pack_product(
                product=self.product,
                version=self.version,
                output=original,
            )
        self._rewrite_archive(
            original,
            tampered,
            lambda name, raw: (
                b"changed\n" if name.endswith("product/index.html") else raw
            ),
        )
        with self.assertRaisesRegex(ValueError, "payload"):
            release.verify_archive(tampered)

    def test_duplicate_archive_path_is_rejected(self) -> None:
        original = self.root / "original.zip"
        duplicate = self.root / "duplicate.zip"
        with self._verification():
            release.pack_product(
                product=self.product,
                version=self.version,
                output=original,
            )
        root = release.release_root(self.version)
        self._rewrite_archive(
            original,
            duplicate,
            lambda name, raw: raw,
            duplicate=f"{root}/product/index.html",
        )
        with self.assertRaisesRegex(ValueError, "duplicate"):
            release.verify_archive(duplicate)

    def test_symlink_archive_entry_is_rejected(self) -> None:
        original = self.root / "original.zip"
        linked = self.root / "linked.zip"
        with self._verification():
            release.pack_product(
                product=self.product,
                version=self.version,
                output=original,
            )
        root = release.release_root(self.version)
        self._rewrite_archive(
            original,
            linked,
            lambda name, raw: raw,
            symlink=f"{root}/linked-index.html",
        )
        with self.assertRaisesRegex(ValueError, "symlink"):
            release.verify_archive(linked)

    def test_publication_failure_restores_previous_pair(self) -> None:
        archive = self.root / "release.zip"
        checksum = release.checksum_path(archive)
        archive.write_bytes(b"old archive")
        checksum.write_bytes(b"old checksum")
        with mock.patch.object(
            release,
            "verify_archive",
            side_effect=ValueError("verification failed"),
        ):
            with self.assertRaisesRegex(ValueError, "verification failed"):
                release._publish_release(archive, b"new archive")
        self.assertEqual(archive.read_bytes(), b"old archive")
        self.assertEqual(checksum.read_bytes(), b"old checksum")

    def test_incomplete_existing_release_pair_is_rejected(self) -> None:
        archive = self.root / "release.zip"
        archive.write_bytes(b"orphan archive")
        with self.assertRaisesRegex(ValueError, "complete pair"):
            release._publish_release(archive, b"new archive")
        self.assertEqual(archive.read_bytes(), b"orphan archive")
        self.assertFalse(release.checksum_path(archive).exists())

    def test_build_release_delegates_exact_source_constraints(self) -> None:
        archive = self.root / "release.zip"
        product = self.root / "built-product"
        principia = self.root / "principia"
        atlas = self.root / "atlas"
        principia.mkdir()
        atlas.mkdir()

        def fake_build_product(**kwargs):
            kwargs["output"].mkdir()
            (kwargs["output"] / "index.html").write_text(
                "built\n",
                encoding="utf-8",
            )
            orchestrate.receipt_path(kwargs["output"]).write_text(
                "{}\n",
                encoding="utf-8",
            )
            return self.product_manifest, self.receipt

        with mock.patch.object(
            release.orchestrate,
            "_source_roots",
            return_value=(principia, atlas),
        ), mock.patch.object(
            release.orchestrate,
            "build_product",
            side_effect=fake_build_product,
        ) as builder, mock.patch.object(
            release,
            "pack_product",
            return_value={"release_id": "a" * 64},
        ) as packer:
            manifest = release.build_release(
                principia_root=principia,
                atlas_repo=atlas,
                route="distributed-information",
                version=self.version,
                output=archive,
                product_output=product,
                expected_principia_commit="1" * 40,
                expected_atlas_commit="2" * 40,
            )
        self.assertEqual(manifest["release_id"], "a" * 64)
        builder.assert_called_once()
        kwargs = builder.call_args.kwargs
        self.assertEqual(kwargs["expected_principia_commit"], "1" * 40)
        self.assertEqual(kwargs["expected_atlas_commit"], "2" * 40)
        self.assertEqual(kwargs["output"], product)
        packer.assert_called_once_with(
            product=product,
            version=self.version,
            output=archive,
        )

    def test_invalid_version_and_launcher_syntax_are_bounded(self) -> None:
        with self.assertRaisesRegex(ValueError, "SemVer"):
            release.validate_version("August 5")
        compile(release.RUNTIME_PATH.read_bytes(), "launcher.py", "exec")
        payload = release._generated_payload(self.version)
        self.assertIn("launch.cmd", payload)
        self.assertIn("launch.command", payload)


if __name__ == "__main__":
    unittest.main()
