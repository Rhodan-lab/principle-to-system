from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from software.principia_atlas import (
    hosted_catalog,
    hosted_store,
    orchestrate,
    promotion_policy as policy,
    release,
)


class PrincipiaAtlasHostedStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.product = self.root / "product"
        (self.product / "principia").mkdir(parents=True)
        (self.product / "atlas").mkdir(parents=True)
        (self.product / "index.html").write_text("release home\n", encoding="utf-8")
        (self.product / "principia/index.html").write_text("learn\n", encoding="utf-8")
        (self.product / "principia/app.js").write_text("console.log('learn')\n", encoding="utf-8")
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
        self.archives = self.root / "archives"
        self.archives.mkdir()
        self.archive = self.archives / f"principia-atlas-{self.version}.zip"
        with self._product_verification():
            self.release_manifest = release.pack_product(
                product=self.product,
                version=self.version,
                output=self.archive,
            )
        self.catalog = self._catalog()
        self.catalog_path = self.root / "catalog.json"
        self.catalog_path.write_bytes(policy.canonical_json(self.catalog))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _product_verification(self):
        return mock.patch.object(
            release.orchestrate,
            "verify_product",
            return_value=(self.product_manifest, self.receipt),
        )

    def _catalog(self, *, archive_sha: str | None = None) -> dict[str, object]:
        archive_sha = archive_sha or hashlib.sha256(self.archive.read_bytes()).hexdigest()
        entry = {
            "tag": f"principia-atlas-v{self.version}",
            "channel": "alpha",
            "promotion_id": "a" * 64,
            "release": {
                "release_id": self.release_manifest["release_id"],
                "bundle_id": self.release_manifest["bundle_id"],
                "receipt_id": self.release_manifest["receipt_id"],
                "route_id": self.release_manifest["route_id"],
                "archive": {
                    "name": self.archive.name,
                    "sha256": archive_sha,
                    "checksum_name": self.archive.name + ".sha256",
                },
            },
            "sources": {
                "principia": {
                    "repository": "Rhodan-lab/principle-to-system",
                    "commit": "1" * 40,
                },
                "atlas": {
                    "repository": "Rhodan-lab/Atlas",
                    "commit": "2" * 40,
                },
            },
            "compatibility": {
                "release_contract": release.CONTRACT,
                "route_id": self.release_manifest["route_id"],
                "entrypoints": self.release_manifest["entrypoints"],
                "runtime": self.release_manifest["runtime"],
                "boundaries": self.release_manifest["boundaries"],
            },
        }
        unsigned = {
            "contract": hosted_catalog.CONTRACT,
            "product": hosted_catalog.PRODUCT,
            "release_count": 1,
            "releases": {self.version: entry},
            "channels": {
                "alpha": {
                    "version": self.version,
                    "tag": entry["tag"],
                    "promotion_id": entry["promotion_id"],
                },
                "beta": None,
                "stable": None,
            },
        }
        return hosted_catalog.verify_catalog(policy.seal(unsigned, "catalog_id"))

    @staticmethod
    def _snapshot(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    def _build(self, output: Path) -> dict[str, object]:
        with self._product_verification():
            return hosted_store.build_store(
                catalog_path=self.catalog_path,
                archives=self.archives,
                output=output,
            )

    def test_build_is_deterministic_and_verifiable(self) -> None:
        first = self.root / "first-store"
        second = self.root / "second-store"
        first_manifest = self._build(first)
        second_manifest = self._build(second)
        self.assertEqual(first_manifest, second_manifest)
        self.assertEqual(self._snapshot(first), self._snapshot(second))
        verified = hosted_store.verify_store(first, self.catalog)
        self.assertEqual(verified["store_id"], first_manifest["store_id"])
        entry = verified["releases"][self.version]
        self.assertEqual(entry["entrypoint"], "index.html")
        self.assertEqual(entry["archive_sha256"], hashlib.sha256(self.archive.read_bytes()).hexdigest())
        self.assertIn("principia/app.js", entry["files"])

    def test_store_file_tamper_and_extra_file_are_rejected(self) -> None:
        store = self.root / "store"
        manifest = self._build(store)
        entry = manifest["releases"][self.version]
        asset = store / entry["object_root"] / "index.html"
        asset.write_text("tampered\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "does not match"):
            hosted_store.verify_store(store, self.catalog)
        self._build(store)
        (store / "unexpected.txt").write_text("extra\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "file set"):
            hosted_store.verify_store(store, self.catalog)

    def test_store_symlink_is_rejected(self) -> None:
        store = self.root / "store"
        manifest = self._build(store)
        entry = manifest["releases"][self.version]
        asset = store / entry["object_root"] / "index.html"
        asset.unlink()
        try:
            asset.symlink_to(self.root / "outside.html")
        except OSError as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        with self.assertRaisesRegex(ValueError, "regular file|symlink"):
            hosted_store.verify_store(store, self.catalog)

    def test_archive_identity_mismatch_is_rejected(self) -> None:
        changed = self._catalog(archive_sha="f" * 64)
        changed_path = self.root / "changed-catalog.json"
        changed_path.write_bytes(policy.canonical_json(changed))
        with self._product_verification():
            with self.assertRaisesRegex(ValueError, "archive identity"):
                hosted_store.build_store(
                    catalog_path=changed_path,
                    archives=self.archives,
                    output=self.root / "store",
                )

    def test_catalog_identity_drift_is_rejected(self) -> None:
        store = self.root / "store"
        self._build(store)
        changed = json.loads(json.dumps(self.catalog))
        changed["catalog_id"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "catalog|seal"):
            hosted_store.verify_store(store, changed)

    def test_publication_failure_restores_previous_store(self) -> None:
        output = self.root / "store"
        old_manifest = self._build(output)
        old_snapshot = self._snapshot(output)
        stage = self.root / "stage"
        with self._product_verification():
            hosted_store._build_stage(
                catalog=self.catalog,
                archives=self.archives,
                stage=stage,
            )
        with mock.patch.object(
            hosted_store,
            "verify_store",
            side_effect=[old_manifest, ValueError("post-swap verification failed")],
        ):
            with self.assertRaisesRegex(ValueError, "post-swap"):
                hosted_store._publish(output, stage, self.catalog)
        self.assertEqual(self._snapshot(output), old_snapshot)
        self.assertFalse(stage.exists())

    def test_check_command_rebuilds_identical_store(self) -> None:
        with self._product_verification():
            store_id = hosted_store.check_store(
                catalog_path=self.catalog_path,
                archives=self.archives,
            )
        self.assertRegex(store_id, r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
