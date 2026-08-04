from __future__ import annotations

import copy
import unittest

from software.principia_atlas import hosted_catalog
from software.principia_atlas import promotion_policy as policy


def digest(character: str) -> str:
    return character * 64


def snapshot(version: str, history=()) -> dict[str, object]:
    channel = policy.channel_for(version)
    route = "distributed-information"
    sources = {
        "principia": {
            "repository": "Rhodan-lab/principle-to-system",
            "commit": "1" * 40,
            "clean": True,
            "status_sha256": policy.EMPTY_STATUS_SHA256,
        },
        "atlas": {
            "repository": "Rhodan-lab/Atlas",
            "commit": "2" * 40,
            "clean": True,
            "status_sha256": policy.EMPTY_STATUS_SHA256,
        },
    }
    compatibility = {
        "release_contract": "principia-atlas-release/0.1",
        "route_id": route,
        "entrypoints": {
            "verify": "launcher.py verify",
            "run": "launcher.py run",
            "linux_macos": "launch.sh",
            "macos_double_click": "launch.command",
            "windows": "launch.cmd",
        },
        "runtime": {
            "host": "127.0.0.1",
            "external_network_required": False,
            "python": ">=3.10",
        },
        "boundaries": dict(policy.BOUNDARIES),
    }
    candidate = {
        "tag": policy.TAG_PREFIX + version,
        "version": version,
        "channel": channel,
        "release": {
            "release_id": digest("a"),
            "bundle_id": digest("b"),
            "receipt_id": digest("c"),
            "route_id": route,
            "archive": {
                "name": f"principia-atlas-{version}.zip",
                "sha256": digest("d"),
                "checksum_name": f"principia-atlas-{version}.zip.sha256",
            },
        },
        "sources": sources,
        "compatibility": compatibility,
    }
    return policy.make_promotion(candidate, history)


class HostedCatalogTests(unittest.TestCase):
    def test_build_and_verify_catalog(self) -> None:
        alpha = snapshot("0.1.0-alpha.1")
        catalog = hosted_catalog.make_catalog([alpha])
        verified = hosted_catalog.verify_catalog(catalog)
        self.assertEqual(verified["release_count"], 1)
        self.assertEqual(
            verified["channels"]["alpha"]["version"], "0.1.0-alpha.1"
        )
        entry = verified["releases"]["0.1.0-alpha.1"]
        self.assertEqual(entry["release"]["route_id"], "distributed-information")
        self.assertEqual(
            set(entry["sources"]["principia"]), {"repository", "commit"}
        )

    def test_duplicate_version_is_rejected(self) -> None:
        alpha = snapshot("0.1.0-alpha.1")
        with self.assertRaisesRegex(ValueError, "duplicate versions"):
            hosted_catalog.make_catalog([alpha, alpha])

    def test_catalog_seal_tamper_is_rejected(self) -> None:
        catalog = hosted_catalog.make_catalog([snapshot("0.1.0-alpha.1")])
        catalog["release_count"] = 3
        with self.assertRaisesRegex(ValueError, "seal"):
            hosted_catalog.verify_catalog(catalog)

    def test_stale_channel_pointer_is_rejected_even_when_resealed(self) -> None:
        alpha1 = snapshot("0.1.0-alpha.1")
        alpha2 = snapshot("0.1.0-alpha.2", [alpha1])
        catalog = hosted_catalog.make_catalog([alpha1, alpha2])
        unsigned = copy.deepcopy(catalog)
        unsigned.pop("catalog_id")
        first = unsigned["releases"]["0.1.0-alpha.1"]
        unsigned["channels"]["alpha"] = {
            "version": "0.1.0-alpha.1",
            "tag": first["tag"],
            "promotion_id": first["promotion_id"],
        }
        broken = policy.seal(unsigned, "catalog_id")
        with self.assertRaisesRegex(ValueError, "stale"):
            hosted_catalog.verify_catalog(broken)

    def test_route_identity_drift_is_rejected_when_resealed(self) -> None:
        catalog = hosted_catalog.make_catalog([snapshot("0.1.0-alpha.1")])
        unsigned = copy.deepcopy(catalog)
        unsigned.pop("catalog_id")
        unsigned["releases"]["0.1.0-alpha.1"]["release"]["route_id"] = (
            "refrigerator"
        )
        broken = policy.seal(unsigned, "catalog_id")
        with self.assertRaisesRegex(ValueError, "route identity"):
            hosted_catalog.verify_catalog(broken)


if __name__ == "__main__":
    unittest.main()
