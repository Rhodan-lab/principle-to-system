from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_PATH = REPO_ROOT / "software" / "product_alpha" / "build.py"
LAUNCHER_PATH = REPO_ROOT / "software" / "product_alpha" / "run_pilot.py"
INDEX_PATH = REPO_ROOT / "software" / "product_alpha" / "index.html"
ADAPTER_PATH = REPO_ROOT / "software" / "product_alpha" / "model-adapters.js"

spec = importlib.util.spec_from_file_location("product_alpha_build_multi_route", BUILD_PATH)
assert spec and spec.loader
build_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = build_module
spec.loader.exec_module(build_module)


class ProductAlphaMultiRouteTests(unittest.TestCase):
    def test_source_shell_is_route_driven(self) -> None:
        html = INDEX_PATH.read_text(encoding="utf-8")
        self.assertIn('<meta name="principia-route" content="refrigerator">', html)
        self.assertIn('<script src="model-adapters.js"></script>', html)
        self.assertIn("route.model.activity_title", html)
        self.assertIn("route.model.parameters", html)
        self.assertIn("config.prediction.choices", html)
        self.assertIn("modelAdapter().validate", html)
        self.assertIn("data/${routeId}.json", html)
        self.assertNotIn("data/refrigerator.json", html)

    def test_both_routes_build_with_bound_identity_and_adapter_asset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifests = {}
            for route in ("refrigerator", "distributed-information"):
                output = root / route
                manifest = build_module.build(REPO_ROOT, output, route)
                manifests[route] = manifest
                self.assertEqual(manifest["route_id"], route)
                self.assertTrue((output / "model-adapters.js").is_file())
                self.assertTrue((output / "data" / f"{route}.json").is_file())
                html = (output / "index.html").read_text(encoding="utf-8")
                self.assertIn(
                    f'<meta name="principia-route" content="{route}">',
                    html,
                )
                payload = json.loads(
                    (output / "data" / f"{route}.json").read_text(encoding="utf-8")
                )
                self.assertEqual(payload["route_id"], route)
                self.assertIn(
                    payload["model"]["adapter"],
                    {"thermal-cabinet-v1", "queue-delay-fluid-v1"},
                )
            self.assertNotEqual(manifests["refrigerator"], manifests["distributed-information"])

    def test_refrigerator_remains_default_build(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = build_module.build(REPO_ROOT, Path(directory))
        self.assertEqual(manifest["route_id"], "refrigerator")

    def test_launcher_accepts_both_routes(self) -> None:
        for route in ("refrigerator", "distributed-information"):
            completed = subprocess.run(
                [sys.executable, str(LAUNCHER_PATH), "check", "--route", route],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("pilot launcher check passed", completed.stdout)

    def test_adapter_asset_has_no_external_or_persistent_path(self) -> None:
        source = ADAPTER_PATH.read_text(encoding="utf-8").lower()
        for forbidden in (
            "fetch(",
            "xmlhttprequest",
            "websocket",
            "localstorage",
            "sessionstorage",
            "indexeddb",
            "document.cookie",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
