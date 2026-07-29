from __future__ import annotations

import copy
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "scripts/generate_phase29_offline_consequence_plan_review_response_intake_envelope_readiness.py"
spec = importlib.util.spec_from_file_location("phase29_generator", GENERATOR)
assert spec and spec.loader
phase29 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(phase29)


class Phase29EnvelopeReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = phase29.build_document()

    def test_baseline_passes(self) -> None:
        self.assertEqual(phase29.validate_document(self.document), [])

    def test_build_is_deterministic(self) -> None:
        self.assertEqual(phase29.render(phase29.build_document()), phase29.render(phase29.build_document()))

    def test_envelope_version_drift_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["envelope_readiness_records"][0]["envelope_spec"]["envelope_version"] = "9.9"
        self.assertTrue(phase29.validate_document(changed))

    def test_filled_template_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["envelope_readiness_records"][0]["blank_envelope_template"]["response_id"] = "fabricated"
        self.assertTrue(phase29.validate_document(changed))

    def test_quarantine_authority_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["envelope_readiness_records"][0]["quarantine_policy"]["execution_authorized"] = True
        self.assertTrue(phase29.validate_document(changed))

    def test_response_receipt_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["envelope_readiness_records"][0]["response_received"] = True
        self.assertTrue(phase29.validate_document(changed))

    def test_atlas_access_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["authority"]["atlas_call_permitted"] = True
        self.assertTrue(phase29.validate_document(changed))

    def test_ledger_tamper_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["ledger"]["entries"][0]["entry_sha256"] = "0" * 64
        self.assertTrue(phase29.validate_document(changed))

    def test_live_activation_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["live"] = True
        self.assertTrue(phase29.validate_document(changed))


if __name__ == "__main__":
    unittest.main()
