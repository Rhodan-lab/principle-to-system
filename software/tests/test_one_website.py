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
        self.assertEqual(len(web.expected_paths()), 32)
        self.assertIn("research/data/workspace-shell-data.json", web.expected_paths())
        self.assertIn("experience.css", web.expected_paths())
        self.assertIn("experience.js", web.expected_paths())
        self.assertIn("site.js", web.expected_paths())
        self.assertIn("atlas-workspace.css", web.expected_paths())
        self.assertIn("atlas-workspace.js", web.expected_paths())
        self.assertIn("universe.css", web.expected_paths())
        self.assertIn("universe.js", web.expected_paths())
        for asset in ("knowledge/index.html", "knowledge.css", "knowledge.js", "knowledge-content.js"):
            self.assertIn(asset, web.expected_paths())
        self.assertEqual(web.EXPLORATIONS, ("rainwater", "microgrid"))
        for topic in web.EXPLORATIONS:
            self.assertIn(f"explore/{topic}/index.html", web.expected_paths())
        self.assertIn("explore/index.html", web.expected_paths())
        self.assertIn("exploration.js", web.expected_paths())
        self.assertIn("exploration-models.js", web.expected_paths())
        self.assertIn("exploration.css", web.expected_paths())
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
            marker = 'aria-current="page">Laboratories</a>'
            self.assertIn(marker.encode(), published)
            self.assertNotIn(b"//cdn.", published)
            self.assertIn(b'href="/experience.css"', published)
            self.assertIn(b'src="/experience.js"', published)
            self.assertIn(b'class="pa-learner"', published)
            self.assertIn(b'<link rel="stylesheet" href="/universe.css">', published)
            self.assertIn(b'<script defer src="/universe.js"></script>', published)
            self.assertIn(b'class="pa-nav-command"', published)

    def test_atlas_presentation_preserves_source_shell_and_uses_first_party_assets(self) -> None:
        original = b'<!doctype html><html><head><title>Atlas</title></head><body><main id="main-content"></main><script type="module" src="./app.js"></script></body></html>'
        generated = web.add_navigation(original, "atlas")
        self.assertIn(b'<body class="pa-research">', generated)
        self.assertIn(b'<link rel="stylesheet" href="/atlas-workspace.css">', generated)
        self.assertIn(b'<script defer src="/atlas-workspace.js"></script>', generated)
        self.assertIn(b'<script type="module" src="./app.js"></script>', generated)
        self.assertNotIn(b'<script defer src="/experience.js"></script>', generated)
        self.assertIn(b'<nav id="pa-global-nav"', generated)
        self.assertIn(b'/universe.css', generated)
        self.assertIn(b'/universe.js', generated)

    def test_exploration_templates_are_source_bounded(self) -> None:
        template = (ROOT / "software/one_website/exploration.html").read_text()
        library = (ROOT / "software/one_website/explore-library.html").read_text()
        self.assertEqual(template.count("__EXPLORATION_ID__"), 2)
        self.assertEqual(template.count("__EXPLORATION_TITLE__"), 3)
        self.assertIn('id="lab-form"', template)
        self.assertIn('src="/exploration-models.js"', template)
        self.assertIn('src="/exploration.js"', template)
        self.assertIn("NOT PRODUCT ALPHA", template)
        for route in web.EXPLORATIONS:
            self.assertIn(f'href="/explore/{route}/"', library)

    def test_knowledge_atlas_is_complete_and_safe(self) -> None:
        page = (ROOT / "software/one_website/knowledge.html").read_text()
        self.assertIn('id="knowledge-article"', page)
        self.assertIn('id="knowledge-check-form"', page)
        self.assertIn('src="/knowledge-content.js"', page)
        self.assertIn('src="/knowledge.js"', page)
        self.assertIn('href="/knowledge.css"', page)
        self.assertIn("original teaching syntheses", page)
        config = json.loads((ROOT / "vercel.json").read_text())
        self.assertTrue(any(r["source"] == "/knowledge/" for r in config["rewrites"]))

    def test_navigation_rejects_unexpected_structure_and_route(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown navigation"):
            web.add_navigation(b"<body></body>", "unknown")
        with self.assertRaisesRegex(ValueError, "Expected one head"):
            web.add_navigation(b"<head><body></body>", "atlas")

    def test_source_is_bounded_and_public_home_mentions_authority(self) -> None:
        homepage = (ROOT / "software/one_website/index.html").read_text()
        self.assertIn("Two authorities.", homepage)
        self.assertIn("pinned, read-only fixture", homepage)
        self.assertIn("/learn/refrigerator/", homepage)
        self.assertIn("/learn/distributed-information/", homepage)
        self.assertIn("/research/", homepage)
        self.assertIn("/explore/", homepage)
        self.assertIn("/explore/rainwater/", homepage)
        self.assertIn("/explore/microgrid/", homepage)
        self.assertIn('href="/knowledge/"', homepage)
        self.assertIn('id="knowledge-chapters"', homepage)
        self.assertIn("Connected knowledge chapters", homepage)
        self.assertIn("04</b> Interactive laboratories", homepage)
        self.assertNotIn("localStorage", homepage)
        self.assertNotIn("sessionStorage", homepage)
        self.assertIn('id="studio-panel"', homepage)
        self.assertIn('src="/site.js"', homepage)
        self.assertIn('aria-label="Model preview"', homepage)
        self.assertIn('id="pa-global-nav"', homepage)
        self.assertIn('id="discover"', homepage)
        self.assertIn('id="explore"', homepage)
        self.assertIn('id="method"', homepage)
        self.assertIn('id="evidence-boundary"', homepage)
        self.assertIn('src="/universe.js"', homepage)
        self.assertIn('href="/universe.css"', homepage)

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
