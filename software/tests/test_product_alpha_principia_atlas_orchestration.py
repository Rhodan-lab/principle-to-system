from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from software.principia_atlas import orchestrate


class PrincipiaAtlasOrchestrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.principia = self.root / "principia-source"
        self.atlas = self.root / "atlas-source"
        self.output = self.root / "published-product"
        (self.principia / "software/product_alpha").mkdir(parents=True)
        (self.principia / "software/principia_atlas").mkdir(parents=True)
        (self.principia / "software/product_alpha/build.py").write_text(
            "# product build\n", encoding="utf-8"
        )
        (self.principia / "software/principia_atlas/suite.py").write_text(
            "# suite\n", encoding="utf-8"
        )
        (self.atlas / "tools/phase4_workspace").mkdir(parents=True)
        (self.atlas / "apps/workspace-shell").mkdir(parents=True)
        (self.atlas / "tools/phase4_workspace/package_product_input.py").write_text(
            "# packager\n", encoding="utf-8"
        )
        (self.atlas / "apps/workspace-shell/index.html").write_text(
            "<!doctype html>\n", encoding="utf-8"
        )
        self.principia_state = {
            "repository": orchestrate.PRINCIPIA_REPOSITORY,
            "commit": "1" * 40,
            "clean": True,
        }
        self.atlas_state = {
            "repository": orchestrate.ATLAS_REPOSITORY,
            "commit": "2" * 40,
            "clean": True,
        }
        self.manifest = {
            "bundle_id": "b" * 64,
            "principia": {
                "route_id": "distributed-information",
                "build_id": "p" * 64,
            },
            "atlas": {
                "shell_build_digest": "a" * 64,
                "report_digest": "r" * 64,
                "workspace": {"id": "workspace:test", "revision": 7},
            },
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _fake_source_packages(
        self,
        principia_root: Path,
        atlas_root: Path,
        route: str,
        work_root: Path,
    ) -> tuple[Path, Path, Path]:
        principia_package = work_root / "principia-package"
        atlas_package = work_root / "atlas-package"
        principia_package.mkdir()
        atlas_package.mkdir()
        report = atlas_package / orchestrate.ATLAS_REPORT_NAME
        report.write_text("{}\n", encoding="utf-8")
        return principia_package, atlas_package, report

    def _fake_bundle(
        self,
        principia_package: Path,
        atlas_package: Path,
        report: Path,
        output: Path,
    ) -> dict[str, object]:
        output.mkdir()
        (output / "index.html").write_text("new product\n", encoding="utf-8")
        return self.manifest

    def _build_patches(self):
        return (
            mock.patch.object(
                orchestrate,
                "_source_states",
                side_effect=[
                    (self.principia_state, self.atlas_state),
                    (self.principia_state, self.atlas_state),
                ],
            ),
            mock.patch.object(orchestrate, "check_source_determinism"),
            mock.patch.object(
                orchestrate,
                "build_source_packages",
                side_effect=self._fake_source_packages,
            ),
            mock.patch.object(
                orchestrate.suite,
                "build_bundle",
                side_effect=self._fake_bundle,
            ),
            mock.patch.object(
                orchestrate.suite,
                "verify_bundle",
                return_value=(self.manifest, {"index.html": b"new product\n"}),
            ),
            mock.patch.object(
                orchestrate.suite,
                "smoke",
                return_value={"loopback_only": True},
            ),
        )

    def test_build_atomically_replaces_previous_product_and_writes_receipt(self) -> None:
        self.output.mkdir()
        (self.output / "index.html").write_text("old product\n", encoding="utf-8")
        patches = self._build_patches()
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
            manifest, receipt = orchestrate.build_product(
                principia_root=self.principia,
                atlas_repo=self.atlas,
                route="distributed-information",
                output=self.output,
            )
        self.assertEqual(manifest, self.manifest)
        self.assertEqual(receipt["bundle_id"], self.manifest["bundle_id"])
        self.assertEqual(
            (self.output / "index.html").read_text(encoding="utf-8"),
            "new product\n",
        )
        receipt_file = orchestrate.receipt_path(self.output)
        self.assertTrue(receipt_file.is_file())
        stored = json.loads(receipt_file.read_text(encoding="utf-8"))
        self.assertEqual(stored["receipt_id"], receipt["receipt_id"])
        self.assertFalse((self.root / ".published-product.build.lock").exists())

    def test_failed_smoke_preserves_previous_product(self) -> None:
        self.output.mkdir()
        old = self.output / "index.html"
        old.write_text("old product\n", encoding="utf-8")
        patches = self._build_patches()
        patches = list(patches)
        patches[-1] = mock.patch.object(
            orchestrate.suite,
            "smoke",
            side_effect=ValueError("smoke failed"),
        )
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
            with self.assertRaisesRegex(ValueError, "smoke failed"):
                orchestrate.build_product(
                    principia_root=self.principia,
                    atlas_repo=self.atlas,
                    route="distributed-information",
                    output=self.output,
                )
        self.assertEqual(old.read_text(encoding="utf-8"), "old product\n")
        self.assertFalse(orchestrate.receipt_path(self.output).exists())
        self.assertFalse((self.root / ".published-product.build.lock").exists())

    def test_receipt_tamper_is_rejected(self) -> None:
        receipt = orchestrate.make_receipt(
            self.manifest,
            self.principia_state,
            self.atlas_state,
        )
        receipt["route_id"] = "refrigerator"
        path = orchestrate.receipt_path(self.output)
        path.write_bytes(orchestrate.canonical_json(receipt))
        with mock.patch.object(
            orchestrate.suite,
            "verify_bundle",
            return_value=(self.manifest, {}),
        ):
            with self.assertRaisesRegex(ValueError, "receipt seal"):
                orchestrate.verify_receipt(self.output)

    def test_build_lock_rejects_concurrent_owner(self) -> None:
        lock = self.root / ".published-product.build.lock"
        lock.write_text("pid=123\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "another product build"):
            with orchestrate.build_lock(self.output):
                self.fail("lock should not have been acquired")
        self.assertEqual(lock.read_text(encoding="utf-8"), "pid=123\n")

    def test_atlas_official_packager_owns_build_and_verification(self) -> None:
        calls: list[tuple[str, ...]] = []

        def fake_atlas(root: Path, *arguments: str) -> None:
            calls.append(tuple(arguments))
            if arguments[0] == "build":
                output = Path(arguments[2])
                output.mkdir()
                (output / orchestrate.ATLAS_REPORT_NAME).write_text(
                    "{}\n", encoding="utf-8"
                )

        def fake_principia_build(root: Path, output: Path, route: str) -> None:
            output.mkdir()

        with mock.patch.object(orchestrate, "_atlas", side_effect=fake_atlas), mock.patch.object(
            orchestrate.principia_build,
            "build",
            side_effect=fake_principia_build,
        ):
            with tempfile.TemporaryDirectory() as temporary:
                orchestrate.build_source_packages(
                    self.principia,
                    self.atlas,
                    "distributed-information",
                    Path(temporary),
                )
        self.assertEqual(calls[0][0:2], ("build", "--output"))
        self.assertEqual(calls[1][0:2], ("verify", "--package"))

    def test_git_state_rejects_dirty_checkout(self) -> None:
        with mock.patch.object(
            orchestrate,
            "_run",
            side_effect=[str(self.principia), "3" * 40, " M tracked.py"],
        ):
            with self.assertRaisesRegex(ValueError, "tracked changes"):
                orchestrate.git_state(
                    self.principia,
                    orchestrate.PRINCIPIA_REPOSITORY,
                    allow_dirty=False,
                )

    def test_git_state_enforces_expected_commit(self) -> None:
        with mock.patch.object(
            orchestrate,
            "_run",
            side_effect=[str(self.atlas), "4" * 40],
        ):
            with self.assertRaisesRegex(ValueError, "expected"):
                orchestrate.git_state(
                    self.atlas,
                    orchestrate.ATLAS_REPOSITORY,
                    allow_dirty=False,
                    expected_commit="5" * 40,
                )

    def test_output_must_not_replace_a_source_checkout(self) -> None:
        with self.assertRaisesRegex(ValueError, "source checkout"):
            orchestrate._validate_output(self.root, (self.principia, self.atlas))


if __name__ == "__main__":
    unittest.main()
