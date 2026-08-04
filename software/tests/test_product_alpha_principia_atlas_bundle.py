from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from software.principia_atlas import suite


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def json_digest(value: dict[str, object], field: str) -> str:
    unsigned = dict(value)
    unsigned.pop(field, None)
    return hashlib.sha256(
        json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


class PrincipiaAtlasBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.principia = self.root / "principia"
        self.atlas = self.root / "atlas"
        self.report = self.root / "atlas-report.json"
        self.output = self.root / "bundle"
        self.principia.mkdir()
        self.atlas.mkdir()
        self._write_principia_package()
        self._write_atlas_package()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _write_principia_package(self) -> None:
        files = {
            "index.html": b"<!doctype html><html><head><title>Principia</title></head><body>Learn</body></html>",
            "model-adapters.js": b'"use strict";\n',
            "facilitator.html": b"<!doctype html><html><head><title>Recorder</title></head><body>Recorder</body></html>",
            "pilot-lab.html": b"<!doctype html><html><head><title>Pilot Lab</title></head><body>Pilot Lab</body></html>",
            "evaluation/rubric.json": b"{}\n",
            "evaluation/session-template.json": b"{}\n",
            "data/refrigerator.json": b"{}\n",
        }
        records = []
        for relative, raw in files.items():
            path = self.principia / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            records.append(
                {"path": relative, "sha256": hashlib.sha256(raw).hexdigest()}
            )
        manifest = {
            "contract": "principia-product-alpha-build/0.1",
            "route_id": "refrigerator",
            "file_count": len(records),
            "files": sorted(records, key=lambda item: item["path"]),
            "deterministic": True,
        }
        (self.principia / "build-manifest.json").write_bytes(
            canonical_json(manifest)
        )

    def _write_atlas_package(
        self,
        *,
        live: bool = False,
        automatic_status_inheritance: bool = False,
    ) -> None:
        workspace = {"id": "workspace:test", "revision": 1}
        export = {
            "contract": "atlas-research-workspace-export/0.1",
            "workspace": workspace,
            "principia_references": [
                {
                    "id": "principia-reference:test",
                    "revision": 1,
                    "principia_status_separate": True,
                    "live": live,
                    "automatic_status_inheritance": automatic_status_inheritance,
                }
            ],
            "report_digest": "e" * 64,
        }
        manifest = {
            "contract": "atlas-research-workspace-manifest/0.1",
            "report_digest": "m" * 64,
        }
        export_raw = canonical_json(export)
        manifest_raw = canonical_json(manifest)
        shell = {
            "contract": "atlas-workspace-shell-data/0.1",
            "workspace": workspace,
            "accepted_export": {
                "artifact": {
                    "bytes": len(export_raw),
                    "sha256": hashlib.sha256(export_raw).hexdigest(),
                }
            },
            "accepted_manifest": {
                "artifact": {
                    "bytes": len(manifest_raw),
                    "sha256": hashlib.sha256(manifest_raw).hexdigest(),
                }
            },
            "authority": {
                "accepted_export_only": True,
                "exact_revision_required": True,
                "principia_status_separate": True,
                "zero_external_requests_required": True,
                "canonical_mutation": False,
                "repository_mutation": False,
                "live_principia_dependency": live,
            },
        }
        shell["build_digest"] = json_digest(shell, "build_digest")
        files = {
            "index.html": b"<!doctype html><html><head><title>Atlas</title></head><body>Research</body></html>",
            "styles.css": b"body{}\n",
            "app.js": b'"use strict";\n',
            "data/workspace-shell-data.json": canonical_json(shell),
            "data/workspace-export.json": export_raw,
            "data/workspace-manifest.json": manifest_raw,
        }
        for relative, raw in files.items():
            path = self.atlas / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        report = {
            "contract": "atlas-workspace-shell-build-report/0.1",
            "external_network_required": False,
            "canonical_mutation": False,
            "repository_mutation": False,
            "live_principia_dependency": live,
            "static_assets": ["index.html", "styles.css", "app.js"],
            "generated_files": [
                "data/workspace-shell-data.json",
                "data/workspace-export.json",
                "data/workspace-manifest.json",
            ],
            "shell_build_digest": shell["build_digest"],
            "export_digest": export["report_digest"],
            "manifest_digest": manifest["report_digest"],
            "workspace_id": workspace["id"],
            "workspace_revision": workspace["revision"],
            "source_digest": "s" * 64,
        }
        report["report_digest"] = json_digest(report, "report_digest")
        self.report.write_bytes(canonical_json(report))

    def test_builds_one_verified_product_bundle(self) -> None:
        manifest = suite.build_bundle(
            self.principia,
            self.atlas,
            self.report,
            self.output,
        )
        verified, snapshot = suite.verify_bundle(self.output)
        self.assertEqual(verified, manifest)
        self.assertEqual(manifest["product"], "Principia & Atlas")
        self.assertTrue(manifest["integration"]["authorities_separate"])
        self.assertFalse(
            manifest["integration"]["live_cross_repository_dependency"]
        )
        self.assertIn("principia/index.html", snapshot)
        self.assertIn("atlas/index.html", snapshot)
        launcher = snapshot["index.html"].decode("utf-8")
        self.assertIn("Understand systems. Inspect what supports them.", launcher)
        self.assertIn(manifest["principia"]["build_id"], launcher)
        self.assertIn("atlas/index.html", launcher)

    def test_bundle_build_is_deterministic(self) -> None:
        suite.check_determinism(self.principia, self.atlas, self.report)

    def test_suite_server_adds_navigation_without_mutating_snapshots(self) -> None:
        manifest = suite.build_bundle(
            self.principia,
            self.atlas,
            self.report,
            self.output,
        )
        _, snapshot = suite.verify_bundle(self.output)
        self.assertNotIn(b'class="pa-suite"', snapshot["principia/index.html"])
        injected = suite.inject_nav(
            "principia/index.html",
            snapshot["principia/index.html"],
            manifest["principia"]["build_id"],
        )
        self.assertIn(b'class="pa-suite"', injected)
        self.assertIn(b"/atlas/index.html", injected)
        report = suite.smoke(self.output)
        self.assertTrue(report["loopback_only"])

    def test_verify_rejects_resealed_authority_drift(self) -> None:
        suite.build_bundle(self.principia, self.atlas, self.report, self.output)
        manifest_path = self.output / suite.MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["integration"]["status_inheritance"] = "allowed"
        unsigned = dict(manifest)
        unsigned.pop("bundle_id", None)
        manifest["bundle_id"] = hashlib.sha256(canonical_json(unsigned)).hexdigest()
        manifest_path.write_bytes(canonical_json(manifest))
        with self.assertRaisesRegex(ValueError, "authority boundary"):
            suite.verify_bundle(self.output)

    def test_rejects_live_atlas_principia_dependency(self) -> None:
        self._write_atlas_package(live=True)
        with self.assertRaisesRegex(ValueError, "offline boundaries"):
            suite.build_bundle(
                self.principia,
                self.atlas,
                self.report,
                self.output,
            )

    def test_rejects_atlas_status_inheritance(self) -> None:
        self._write_atlas_package(automatic_status_inheritance=True)
        with self.assertRaisesRegex(ValueError, "bridge boundary"):
            suite.build_bundle(
                self.principia,
                self.atlas,
                self.report,
                self.output,
            )

    def test_rejects_tampered_source_snapshots(self) -> None:
        (self.principia / "index.html").write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "SHA-256|hash"):
            suite.build_bundle(
                self.principia,
                self.atlas,
                self.report,
                self.output,
            )
        self._write_principia_package()
        export_path = self.atlas / "data" / "workspace-export.json"
        export_path.write_bytes(export_path.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "accepted export identity"):
            suite.build_bundle(
                self.principia,
                self.atlas,
                self.report,
                self.output,
            )

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_rejects_symlinked_atlas_asset(self) -> None:
        target = self.root / "outside.js"
        target.write_text("outside", encoding="utf-8")
        asset = self.atlas / "app.js"
        asset.unlink()
        try:
            asset.symlink_to(target)
        except OSError as exc:
            self.skipTest(f"symlink creation unavailable: {exc}")
        with self.assertRaisesRegex(ValueError, "must not be a symlink"):
            suite.build_bundle(
                self.principia,
                self.atlas,
                self.report,
                self.output,
            )


if __name__ == "__main__":
    unittest.main()
