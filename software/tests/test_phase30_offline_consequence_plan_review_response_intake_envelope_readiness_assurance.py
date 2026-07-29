from __future__ import annotations

import copy
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "scripts/generate_phase30_offline_consequence_plan_review_response_intake_envelope_readiness_assurance.py"
spec = importlib.util.spec_from_file_location("phase30_generator", GENERATOR)
assert spec and spec.loader
phase30 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(phase30)


class Phase30EnvelopeReadinessAssuranceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = phase30.build_document()

    def test_baseline_passes(self) -> None:
        self.assertEqual(phase30.validate_document(self.document), [])

    def test_build_is_deterministic(self) -> None:
        self.assertEqual(phase30.render(phase30.build_document()), phase30.render(phase30.build_document()))

    def test_failed_check_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["assurances"][0]["assurance_checks"]["sections_exact"] = False
        self.assertTrue(phase30.validate_document(changed))

    def test_fabricated_envelope_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["assurances"][0]["response_envelope_received"] = True
        self.assertTrue(phase30.validate_document(changed))

    def test_response_receipt_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["assurances"][0]["response_received"] = True
        self.assertTrue(phase30.validate_document(changed))

    def test_human_gate_satisfaction_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["assurances"][0]["human_gate_satisfied_count"] = 1
        self.assertTrue(phase30.validate_document(changed))

    def test_atlas_access_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["authority"]["atlas_call_permitted"] = True
        self.assertTrue(phase30.validate_document(changed))

    def test_ledger_tamper_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["ledger"]["entries"][0]["entry_sha256"] = "0" * 64
        self.assertTrue(phase30.validate_document(changed))

    def test_live_activation_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["live"] = True
        self.assertTrue(phase30.validate_document(changed))

    def test_next_gate_drift_is_rejected(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["next_gate"] = "unauthorized"
        self.assertTrue(phase30.validate_document(changed))


if __name__ == "__main__":
    unittest.main()
