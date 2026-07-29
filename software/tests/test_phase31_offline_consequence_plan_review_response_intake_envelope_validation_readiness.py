from __future__ import annotations

import copy
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "scripts/generate_phase31_offline_consequence_plan_review_response_intake_envelope_validation_readiness.py"
spec = importlib.util.spec_from_file_location("phase31_generator", GENERATOR)
assert spec and spec.loader
phase31 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(phase31)

class Phase31EnvelopeValidationReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = phase31.build_document()

    def test_baseline_passes(self) -> None:
        self.assertEqual(phase31.validate_document(self.document), [])

    def test_build_is_deterministic(self) -> None:
        self.assertEqual(
            phase31.render(phase31.build_document()),
            phase31.render(phase31.build_document()),
        )

    def test_profile_stage_drift_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["validation_readiness_records"][0]["validation_profile"]["stages"][0]["stage_id"] = "drift"
        self.assertTrue(phase31.validate_document(changed))

    def test_control_drift_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["validation_readiness_records"][0]["validation_profile"]["controls"][0]["state"] = "active"
        self.assertTrue(phase31.validate_document(changed))

    def test_filled_validation_receipt_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["validation_readiness_records"][0]["blank_validation_receipt"]["validation_run_id"] = "fabricated"
        self.assertTrue(phase31.validate_document(changed))

    def test_validation_execution_authority_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["authority"]["response_envelope_validation_execution_authorized"] = True
        self.assertTrue(phase31.validate_document(changed))

    def test_envelope_receipt_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["validation_readiness_records"][0]["response_envelope_received"] = True
        self.assertTrue(phase31.validate_document(changed))

    def test_disposition_selection_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["validation_readiness_records"][0]["disposition_selected"] = True
        self.assertTrue(phase31.validate_document(changed))

    def test_atlas_access_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["authority"]["atlas_call_permitted"] = True
        self.assertTrue(phase31.validate_document(changed))

    def test_ledger_tamper_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["ledger"]["entries"][0]["entry_sha256"] = "0" * 64
        self.assertTrue(phase31.validate_document(changed))

    def test_live_activation_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["live"] = True
        self.assertTrue(phase31.validate_document(changed))

if __name__ == "__main__":
    unittest.main()
