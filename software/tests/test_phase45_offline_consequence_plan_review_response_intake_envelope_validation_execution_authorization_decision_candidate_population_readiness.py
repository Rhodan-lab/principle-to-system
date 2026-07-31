from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "release/phase-45-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness.json"
VALIDATOR_PATH = ROOT / "scripts/validate_phase45_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_readiness.py"

spec = importlib.util.spec_from_file_location("phase45_validator", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)

class Phase45PopulationReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def assert_rejected(self, mutator) -> None:
        candidate = copy.deepcopy(self.baseline)
        mutator(candidate)
        self.assertTrue(validator.validate_document(candidate))

    def test_baseline_passes(self) -> None:
        self.assertEqual([], validator.validate_document(copy.deepcopy(self.baseline)))

    def test_source_digest_mutation_rejected(self) -> None:
        self.assert_rejected(lambda d: d["source_phase44"].__setitem__("candidate_sha256", "0" * 64))

    def test_source_finalization_mutation_rejected(self) -> None:
        self.assert_rejected(lambda d: d["source_phase44"].__setitem__("authoritative_finalization_commit", "1" * 40))

    def test_policy_population_escalation_rejected(self) -> None:
        self.assert_rejected(lambda d: d["population_readiness_policy"].__setitem__("candidate_population_permitted", True))

    def test_population_value_injection_rejected(self) -> None:
        self.assert_rejected(lambda d: d["population_readiness_policy"]["population_plan"][0].__setitem__("value_state", "present"))

    def test_population_source_resolution_rejected(self) -> None:
        self.assert_rejected(lambda d: d["population_readiness_policy"]["population_plan"][1].__setitem__("source_reference_state", "resolved"))

    def test_population_slot_permission_rejected(self) -> None:
        self.assert_rejected(lambda d: d["population_readiness_policy"]["population_plan"][2].__setitem__("population_permitted", True))

    def test_stage_activation_rejected(self) -> None:
        self.assert_rejected(lambda d: d["population_readiness_policy"]["stages"][0].__setitem__("state", "active"))

    def test_requirement_evaluation_rejected(self) -> None:
        self.assert_rejected(lambda d: d["population_readiness_policy"]["requirements"][0].__setitem__("state", "passed"))

    def test_profile_role_independence_mutation_rejected(self) -> None:
        self.assert_rejected(lambda d: d["population_readiness_profiles"][0].__setitem__("role_independence_required", False))

    def test_record_check_count_mutation_rejected(self) -> None:
        self.assert_rejected(lambda d: d["population_readiness_records"][0].__setitem__("passed_check_count", 71))

    def test_record_population_rejected(self) -> None:
        self.assert_rejected(lambda d: d["population_readiness_records"][0].__setitem__("populated_slot_count", 1))

    def test_candidate_creation_rejected(self) -> None:
        self.assert_rejected(lambda d: d["population_readiness_records"][0].__setitem__("candidate_created", True))

    def test_population_start_rejected(self) -> None:
        self.assert_rejected(lambda d: d["population_readiness_records"][1].__setitem__("candidate_population_started", True))

    def test_human_gate_satisfaction_rejected(self) -> None:
        self.assert_rejected(lambda d: d["population_readiness_records"][0].__setitem__("human_gate_satisfied_count", 1))

    def test_atlas_permission_rejected(self) -> None:
        self.assert_rejected(lambda d: d["authority"].__setitem__("atlas_call_permitted", True))

    def test_ledger_chain_mutation_rejected(self) -> None:
        self.assert_rejected(lambda d: d["ledger"]["entries"][1]["entry"].__setitem__("previous_entry_sha256", None))

    def test_result_counter_mutation_rejected(self) -> None:
        self.assert_rejected(lambda d: d["result"].__setitem__("failed_population_check_count", 1))

    def test_recovery_matrix_mutation_rejected(self) -> None:
        self.assert_rejected(lambda d: d["recovery"].__setitem__("scenario_count", 171))

    def test_next_gate_mutation_rejected(self) -> None:
        self.assert_rejected(lambda d: d.__setitem__("next_gate", "live-candidate-population"))

if __name__ == "__main__":
    unittest.main()
