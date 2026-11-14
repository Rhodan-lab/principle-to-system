"""Safety and usability regressions for the unified static presentation."""
from __future__ import annotations

import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "software/one_website/build.py"
spec = importlib.util.spec_from_file_location("principia_atlas_web_preview", BUILDER)
assert spec and spec.loader
web = importlib.util.module_from_spec(spec)
spec.loader.exec_module(web)


class UnifiedWebsiteTests(unittest.TestCase):
    def test_route_contract_and_expected_files(self) -> None:
        self.assertEqual(web.ROUTES, ("refrigerator", "distributed-information"))
        self.assertEqual(len(web.ATLAS_PIN), 40)
        self.assertEqual(len(web.expected_paths()), 15)
        self.assertIn("research/data/workspace-shell-data.json", web.expected_paths())
        self.assertNotIn("learn/refrigerator/facilitator.html", web.expected_paths())
        self.assertNotIn("learn/refrigerator/pilot-lab.html", web.expected_paths())

    def test_navigation_preserves_learner_script_and_uses_same_origin(self) -> None:
        source = (ROOT / "software/product_alpha/index.html").read_bytes()
        self.assertEqual(len(re.findall(rb"<script>", source)), 1)
        for route in web.ROUTES:
            published = web.add_navigation(source, route)
            self.assertEqual(len(re.findall(rb"<script>", published)), 1)
            self.assertIn(b'aria-label="Unified Principia and Atlas navigation"', published)
            self.assertIn(b'href="/research/"', published)
            marker = 'aria-current="page">' + (
                "Refrigerator" if route == "refrigerator" else "Information"
            ) + "</a>"
            self.assertIn(marker.encode(), published)
            self.assertNotIn(b"//cdn.", published)

    def test_navigation_rejects_unexpected_structure_and_route(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown navigation"):
            web.add_navigation(b"<body></body>", "unknown")
        with self.assertRaisesRegex(ValueError, "Expected one head"):
            web.add_navigation(b"<head><body></body>", "atlas")

    def test_source_is_bounded_and_public_home_mentions_authority(self) -> None:
        homepage = (ROOT / "software/one_website/index.html").read_text()
        self.assertIn("Two distinct authorities", homepage)
        self.assertIn("read-only research preview", homepage)
        self.assertIn("/learn/refrigerator/", homepage)
        self.assertIn("/learn/distributed-information/", homepage)
        self.assertIn("/research/", homepage)
        self.assertNotIn("localStorage", homepage)
        self.assertNotIn("sessionStorage", homepage)

    def test_manifest_rejects_missing_or_modified_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            base = {
                "contract": web.CONTRACT,
                "product": "Principia & Atlas",
                "mode": "static-read-only-preview",
                "routes": list(web.ROUTES),
                "authority": {
                    "atlas_advisory_only": True, "authorities_separate": True,
                    "canonical_mutation": False, "external_runtime_network": False,
                    "human_verification_claimed": False, "live_sync": False,
                    "repository_mutation": False, "status_inheritance": False,
                },
                "files": [],
            }
            signed = {**base, "build_id": web.sha256(web.canonical(base))}
            (output / web.MANIFEST).write_bytes(web.canonical(signed))
            with self.assertRaisesRegex(ValueError, "asset set|byte budget"):
                web.verify(output)
            signed["build_id"] = "0" * 64
            (output / web.MANIFEST).write_bytes(web.canonical(signed))
            with self.assertRaisesRegex(ValueError, "seal"):
                web.verify(output)

    def test_safe_path_rejects_directory_traversal(self) -> None:
        for path in ("../secrets", "/etc/passwd", "learn\\bad", "a/./b", ""):
            with self.subTest(path=path), self.assertRaises(ValueError):
                web.safe_relative(path)

    def test_hosting_config_is_static_and_fail_closed(self) -> None:
        config = json.loads((ROOT / "vercel.json").read_text())
        self.assertEqual(config["outputDirectory"], "dist")
        self.assertEqual(config["buildCommand"], "bash software/one_website/vercel-build.sh")
        headers = {h["key"]: h["value"] for h in config["headers"][0]["headers"]}
        self.assertIn("connect-src 'self'", headers["Content-Security-Policy"])
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])


if __name__ == "__main__":
    unittest.main()
