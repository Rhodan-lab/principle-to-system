from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from software.principia_atlas import promotion, promotion_policy, release


def digest(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


class PromotionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def fixture(
        self,
        version: str,
        *,
        route: str = "distributed-information",
        python_floor: str = ">=3.10",
        entrypoints: dict[str, str] | None = None,
        boundaries: dict[str, object] | None = None,
        clean: bool = True,
    ) -> tuple[Path, dict[str, object], dict[str, bytes], str]:
        archive = self.root / f"principia-atlas-{version}.zip"
        archive.write_bytes(b"archive")
        release_id = digest("release:" + version)
        bundle_id = digest("bundle:" + version)
        receipt_id = digest("receipt:" + version)
        manifest = {
            "contract": release.CONTRACT,
            "product": release.PRODUCT,
            "version": version,
            "release_id": release_id,
            "bundle_id": bundle_id,
            "receipt_id": receipt_id,
            "route_id": route,
            "entrypoints": entrypoints
            or {
                "verify": "launcher.py verify",
                "run": "launcher.py run",
                "linux_macos": "launch.sh",
                "macos_double_click": "launch.command",
                "windows": "launch.cmd",
            },
            "runtime": {
                "host": "127.0.0.1",
                "external_network_required": False,
                "python": python_floor,
            },
            "boundaries": boundaries
            or {
                "authorities_separate": True,
                "status_inheritance": "prohibited",
                "live_cross_repository_dependency": False,
                "canonical_mutation": False,
            },
        }
        status = promotion.EMPTY_STATUS_SHA256 if clean else digest("dirty")
        receipt = {
            "contract": "principia-atlas-orchestration-receipt/0.2",
            "receipt_id": receipt_id,
            "sources": {
                "principia": {
                    "repository": "Rhodan-lab/principle-to-system",
                    "commit": "1" * 40,
                    "clean": clean,
                    "status_sha256": status,
                },
                "atlas": {
                    "repository": "Rhodan-lab/Atlas",
                    "commit": "2" * 40,
                    "clean": clean,
                    "status_sha256": status,
                },
            },
        }
        entries = {
            "product.build-receipt.json": json.dumps(receipt).encode("utf-8")
        }
        return archive, manifest, entries, digest("archive:" + version)

    def build_promotion(self, version: str, history=(), **kwargs):
        archive, manifest, entries, archive_digest = self.fixture(version, **kwargs)
        tag = promotion.TAG_PREFIX + version
        with mock.patch.object(release, "verify_archive", return_value=manifest), mock.patch.object(
            release, "_read_archive", return_value=(f"principia-atlas-{version}", entries, manifest)
        ), mock.patch.object(release, "_checksum", return_value=archive_digest):
            value = promotion.make_promotion(archive=archive, tag=tag, history=history)
        return value, archive, manifest, entries, archive_digest

    def verify_with_fixture(self, descriptor, index, archive, manifest, entries, archive_digest):
        with mock.patch.object(release, "verify_archive", return_value=manifest), mock.patch.object(
            release, "_read_archive", return_value=("root", entries, manifest)
        ), mock.patch.object(release, "_checksum", return_value=archive_digest):
            promotion.verify_candidate(archive, descriptor, index)

    def test_channel_and_tag_policy(self) -> None:
        self.assertEqual(promotion.channel_for("0.1.0-alpha.1"), "alpha")
        self.assertEqual(promotion.channel_for("0.1.0-beta.2"), "beta")
        self.assertEqual(promotion.channel_for("0.1.0"), "stable")
        with self.assertRaisesRegex(ValueError, "alpha.N or beta.N"):
            promotion.channel_for("0.1.0-rc.1")
        with self.assertRaisesRegex(ValueError, "build metadata"):
            promotion.channel_for("0.1.0+build.1")
        with self.assertRaisesRegex(ValueError, "exactly"):
            promotion.validate_tag("v0.1.0", "0.1.0")

    def test_first_alpha_promotion_and_index(self) -> None:
        descriptor, archive, manifest, entries, archive_digest = self.build_promotion(
            "0.1.0-alpha.1"
        )
        self.assertEqual(descriptor["channel"], "alpha")
        self.assertEqual(descriptor["upgrade"]["kind"], "first-release")
        index = promotion.make_index([], descriptor)
        self.assertEqual(index["release_count"], 1)
        self.assertEqual(index["channels"]["alpha"]["version"], "0.1.0-alpha.1")
        self.assertIsNone(index["channels"]["beta"])
        self.verify_with_fixture(
            descriptor, index, archive, manifest, entries, archive_digest
        )

    def test_global_history_advances_alpha_beta_stable(self) -> None:
        alpha, *_ = self.build_promotion("0.1.0-alpha.1")
        beta, *_ = self.build_promotion("0.1.0-beta.1", [alpha])
        stable, *_ = self.build_promotion("0.1.0", [alpha, beta])
        self.assertEqual(beta["predecessor"]["version"], "0.1.0-alpha.1")
        self.assertEqual(stable["predecessor"]["version"], "0.1.0-beta.1")
        index = promotion.make_index([alpha, beta], stable)
        self.assertEqual(index["channels"]["alpha"]["version"], "0.1.0-alpha.1")
        self.assertEqual(index["channels"]["beta"]["version"], "0.1.0-beta.1")
        self.assertEqual(index["channels"]["stable"]["version"], "0.1.0")

    def test_version_must_advance_global_history(self) -> None:
        stable, *_ = self.build_promotion("0.2.0")
        with self.assertRaisesRegex(ValueError, "advance the global"):
            self.build_promotion("0.1.1-alpha.1", [stable])

    def test_dirty_source_is_not_promotable(self) -> None:
        with self.assertRaisesRegex(ValueError, "clean source"):
            self.build_promotion("0.1.0-alpha.1", clean=False)

    def test_non_major_route_change_is_rejected(self) -> None:
        first, *_ = self.build_promotion("0.1.0-alpha.1")
        with self.assertRaisesRegex(ValueError, "route identity"):
            self.build_promotion(
                "0.1.0-alpha.2", [first], route="refrigerator"
            )

    def test_non_major_python_floor_increase_is_rejected(self) -> None:
        first, *_ = self.build_promotion("0.1.0-alpha.1")
        with self.assertRaisesRegex(ValueError, "Python runtime floor"):
            self.build_promotion(
                "0.1.0-alpha.2", [first], python_floor=">=3.11"
            )

    def test_major_upgrade_can_change_route_but_not_authority_boundary(self) -> None:
        first, *_ = self.build_promotion("0.9.0")
        major, *_ = self.build_promotion("1.0.0-alpha.1", [first], route="refrigerator")
        self.assertEqual(major["upgrade"]["kind"], "major")
        changed = {
            "authorities_separate": False,
            "status_inheritance": "prohibited",
            "live_cross_repository_dependency": False,
            "canonical_mutation": False,
        }
        with self.assertRaisesRegex(ValueError, "authority boundary"):
            self.build_promotion("2.0.0-alpha.1", [major], boundaries=changed)

    def test_promotion_and_index_tamper_are_rejected(self) -> None:
        descriptor, *_ = self.build_promotion("0.1.0-alpha.1")
        tampered = copy.deepcopy(descriptor)
        tampered["channel"] = "stable"
        with self.assertRaisesRegex(ValueError, "channel"):
            promotion.verify_promotion(tampered)
        index = promotion.make_index([], descriptor)
        broken = copy.deepcopy(index)
        broken["release_count"] = 9
        with self.assertRaisesRegex(ValueError, "seal"):
            promotion.verify_index(broken)

    def test_index_pointer_must_be_latest(self) -> None:
        alpha1, *_ = self.build_promotion("0.1.0-alpha.1")
        alpha2, *_ = self.build_promotion("0.1.0-alpha.2", [alpha1])
        index = promotion.make_index([alpha1], alpha2)
        unsigned = dict(index)
        unsigned.pop("index_id")
        unsigned["channels"] = copy.deepcopy(unsigned["channels"])
        unsigned["channels"]["alpha"] = {
            "version": alpha1["version"],
            "tag": alpha1["tag"],
            "promotion_id": alpha1["promotion_id"],
        }
        broken = promotion_policy.seal(unsigned, "index_id")
        with self.assertRaisesRegex(ValueError, "latest"):
            promotion.verify_index(broken)

    def test_release_notes_are_deterministic(self) -> None:
        descriptor, *_ = self.build_promotion("0.1.0-alpha.1")
        first = promotion.release_notes(descriptor)
        second = promotion.release_notes(descriptor)
        self.assertEqual(first, second)
        self.assertIn("Channel: `alpha`", first)
        self.assertIn("Principia", first)
        self.assertIn("Atlas", first)

    def test_resealed_semantic_tamper_is_rejected(self) -> None:
        descriptor, *_ = self.build_promotion("0.1.0-alpha.1")
        unsigned = copy.deepcopy(descriptor)
        unsigned.pop("promotion_id")
        unsigned["compatibility"]["runtime"]["host"] = "0.0.0.0"
        broken = promotion_policy.seal(unsigned, "promotion_id")
        with self.assertRaisesRegex(ValueError, "runtime boundary|compatibility snapshot"):
            promotion.verify_promotion(broken)

    def test_expected_tag_set_must_match_history_assets(self) -> None:
        descriptor, *_ = self.build_promotion("0.1.0-alpha.1")
        history = self.root / "history" / descriptor["tag"]
        history.mkdir(parents=True)
        (history / promotion.PROMOTION_NAME).write_bytes(
            promotion.canonical_json(descriptor)
        )
        expected = self.root / "tags.txt"
        expected.write_text("principia-atlas-v0.1.0-alpha.2\n", encoding="utf-8")
        archive, manifest, entries, archive_digest = self.fixture("0.1.0-alpha.2")
        with mock.patch.object(release, "verify_archive", return_value=manifest), mock.patch.object(
            release, "_read_archive", return_value=("root", entries, manifest)
        ), mock.patch.object(release, "_checksum", return_value=archive_digest):
            with self.assertRaisesRegex(ValueError, "immutable release tags"):
                promotion.prepare(
                    archive,
                    "principia-atlas-v0.1.0-alpha.2",
                    history.parent,
                    self.root / "output",
                    expected,
                )


if __name__ == "__main__":
    unittest.main()
