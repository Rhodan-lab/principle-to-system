#!/usr/bin/env python3
from __future__ import annotations
import copy, json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import generate_phase36_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_readiness_assurance as generator
import validate_phase36_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_readiness_assurance as validator

MANIFEST = ROOT / "release/phase-36-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance.json"

class Phase36AuthorizationReadinessAssuranceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = json.loads(MANIFEST.read_text())

    def assert_rejected(self, mutate) -> None:
        candidate = copy.deepcopy(self.document)
        mutate(candidate)
        self.assertTrue(validator.validate_document(candidate))

    def test_baseline_is_accepted(self):
        self.assertEqual([], validator.validate_document(self.document))

    def test_manifest_matches_deterministic_generation(self):
        self.assertEqual(generator.output_bytes(), MANIFEST.read_bytes())

    def test_source_pin_drift_is_rejected(self):
        self.assert_rejected(lambda d: d["source_phase35"].__setitem__("phase35_candidate_sha256", "0"*64))

    def test_assurance_record_digest_drift_is_rejected(self):
        self.assert_rejected(lambda d: d["assurances"][0].__setitem__("authorization_readiness_record_sha256", "0"*64))

    def test_policy_digest_drift_is_rejected(self):
        self.assert_rejected(lambda d: d["assurances"][0].__setitem__("policy_sha256", "0"*64))

    def test_dual_control_drift_is_rejected(self):
        self.assert_rejected(lambda d: d["assurances"][1].__setitem__("dual_control_required", False))

    def test_approval_activity_is_rejected(self):
        self.assert_rejected(lambda d: d["assurances"][0].__setitem__("approval_received", True))

    def test_authorization_grant_is_rejected(self):
        self.assert_rejected(lambda d: d["result"].__setitem__("authorization_granted_count", 1))

    def test_authority_grant_permission_is_rejected(self):
        self.assert_rejected(lambda d: d["authority"].__setitem__("response_envelope_validation_execution_authorization_grant_permitted", True))

    def test_human_gate_satisfaction_is_rejected(self):
        self.assert_rejected(lambda d: d["assurances"][0].__setitem__("human_gate_satisfied_count", 1))

    def test_next_gate_drift_is_rejected(self):
        self.assert_rejected(lambda d: d.__setitem__("next_gate", "live-authorization"))

if __name__ == "__main__":
    unittest.main()
