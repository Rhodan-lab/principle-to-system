from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "software" / "product_alpha" / "run_pilot.py"
SECURITY_PATH = ROOT / "software" / "product_alpha" / "SECURITY.md"
SPEC = importlib.util.spec_from_file_location(
    "product_alpha_loopback_security_doc",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
launcher = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = launcher
SPEC.loader.exec_module(launcher)


class ProductAlphaLoopbackSecurityDocTests(unittest.TestCase):
    def test_document_matches_runtime_boundary(self) -> None:
        document = SECURITY_PATH.read_text(encoding="utf-8")
        lower = document.lower()

        self.assertIn(launcher.LOOPBACK_HOST, document)
        self.assertIn("HTTP `421`", document)
        self.assertIn("`GET`", document)
        self.assertIn("`HEAD`", document)
        self.assertIn("head_verified=true", document)
        self.assertIn("foreign_host_methods_rejected=GET+HEAD", document)
        self.assertIn("session_data_stored=false", document)

        for header in launcher.PILOT_RESPONSE_HEADERS:
            self.assertIn(header, lower)

        for directive in (
            "frame-ancestors 'none'",
            "form-action 'none'",
            "object-src 'none'",
            "connect-src 'self'",
        ):
            self.assertIn(directive, launcher.CONTENT_SECURITY_POLICY)

        for capability in (
            "camera=()",
            "display-capture=()",
            "geolocation=()",
            "microphone=()",
            "payment=()",
            "serial=()",
            "usb=()",
        ):
            self.assertIn(capability, launcher.PERMISSIONS_POLICY)

        self.assertIn("Clipboard write is intentionally still available", document)
        self.assertIn("not authentication", document)
        self.assertIn("outside the repository", document)


if __name__ == "__main__":
    unittest.main()
