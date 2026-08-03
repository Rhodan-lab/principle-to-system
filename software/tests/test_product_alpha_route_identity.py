from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "software" / "product_alpha" / "route_identity.py"
SPEC = importlib.util.spec_from_file_location("product_alpha_route_identity", MODULE_PATH)
assert SPEC and SPEC.loader
route_identity = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = route_identity
SPEC.loader.exec_module(route_identity)


class ProductAlphaRouteIdentityTests(unittest.TestCase):
    def test_mapping_is_bijective_and_preserves_refrigerator_default(self) -> None:
        self.assertEqual(route_identity.DEFAULT_SOFTWARE_ROUTE, "refrigerator")
        self.assertEqual(route_identity.DEFAULT_EVIDENCE_ROUTE, "refrigerator-v1")
        self.assertEqual(
            route_identity.SOFTWARE_TO_EVIDENCE_ROUTE,
            {
                "refrigerator": "refrigerator-v1",
                "distributed-information": "distributed-information-v1",
            },
        )
        self.assertEqual(
            len(route_identity.SOFTWARE_TO_EVIDENCE_ROUTE),
            len(route_identity.EVIDENCE_TO_SOFTWARE_ROUTE),
        )

    def test_both_directions_are_explicit(self) -> None:
        self.assertEqual(
            route_identity.evidence_route_id("distributed-information"),
            "distributed-information-v1",
        )
        self.assertEqual(
            route_identity.software_route_id("distributed-information-v1"),
            "distributed-information",
        )

    def test_unknown_routes_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported Product Alpha software route"):
            route_identity.evidence_route_id("unknown")
        with self.assertRaisesRegex(ValueError, "unsupported Product Alpha evidence route"):
            route_identity.software_route_id("unknown-v1")
        with self.assertRaisesRegex(ValueError, "route_id must be text"):
            route_identity.validate_evidence_route_id(None)


if __name__ == "__main__":
    unittest.main()
