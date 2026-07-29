from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = ROOT / "scripts/generate_phase35_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_readiness.py"
VALIDATOR_PATH = ROOT / "scripts/validate_phase35_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_readiness.py"
MANIFEST_PATH = ROOT / "release/phase-35-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = load_module("phase35_generator_test", GENERATOR_PATH)
validator = load_module("phase35_validator_test", VALIDATOR_PATH)


class Phase35AuthorizationReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = generator.build_document()

    def assert_rejected(self, document):
        self.assertTrue(validator.validate_document(document))

    def test_manifest_matches_deterministic_generation(self):
        self.assertEqual(json.loads(MANIFEST_PATH.read_text()), self.baseline)

    def test_baseline_is_accepted(self):
        self.assertEqual(validator.validate_document(self.baseline), [])

    def test_source_assurance_digest_drift_is_rejected(self):
        value = copy.deepcopy(self.baseline)
        value["authorization_readiness_records"][0]["source_assurance_record_sha256"] = "0" * 64
        self.assert_rejected(value)

    def test_approval_role_drift_is_rejected(self):
        value = copy.deepcopy(self.baseline)
        value["authorization_profiles"][0]["required_approval_roles"][1]["role"] = "unknown"
        self.assert_rejected(value)

    def test_requirement_state_drift_is_rejected(self):
        value = copy.deepcopy(self.baseline)
        value["authorization_policy"]["authorization_requirements"][0]["state"] = "satisfied"
        self.assert_rejected(value)

    def test_filled_authorization_token_is_rejected(self):
        value = copy.deepcopy(self.baseline)
        value["authorization_readiness_records"][0]["blank_authorization_token"]["authorization_id"] = "auth-1"
        self.assert_rejected(value)

    def test_authorization_grant_is_rejected(self):
        value = copy.deepcopy(self.baseline)
        value["authorization_readiness_records"][0]["authorization_granted"] = True
        self.assert_rejected(value)

    def test_human_gate_satisfaction_is_rejected(self):
        value = copy.deepcopy(self.baseline)
        value["authorization_readiness_records"][0]["human_gate_satisfied_count"] = 1
        self.assert_rejected(value)

    def test_authority_grant_permission_is_rejected(self):
        value = copy.deepcopy(self.baseline)
        value["authority"]["response_envelope_validation_execution_authorization_grant_permitted"] = True
        self.assert_rejected(value)

    def test_ledger_drift_is_rejected(self):
        value = copy.deepcopy(self.baseline)
        value["ledger"]["head_sha256"] = "f" * 64
        self.assert_rejected(value)

    def test_next_gate_drift_is_rejected(self):
        value = copy.deepcopy(self.baseline)
        value["next_gate"] = "live-validation"
        self.assert_rejected(value)


if __name__ == "__main__":
    unittest.main()
