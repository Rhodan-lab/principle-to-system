from __future__ import annotations
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "scripts/validate_phase47_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_execution_readiness.py"
SPEC = importlib.util.spec_from_file_location("phase47_validator", VALIDATOR_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)
MANIFEST = ROOT / "release/phase-47-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness.json"


class Phase47PopulationExecutionReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def errors(self, mutate):
        document = copy.deepcopy(self.baseline)
        mutate(document)
        return VALIDATOR.validate_document(document)

    def assert_rejected(self, mutate) -> None:
        self.assertTrue(self.errors(mutate))

    def test_baseline_passes(self):
        self.assertEqual(VALIDATOR.validate_document(copy.deepcopy(self.baseline)), [])

    def test_source_digest_rejected(self):
        self.assert_rejected(lambda d: d["source_phase46"].__setitem__("candidate_sha256", "0" * 64))

    def test_source_finalization_rejected(self):
        self.assert_rejected(lambda d: d["source_phase46"].__setitem__("authoritative_finalization_commit", "0" * 40))

    def test_next_gate_rejected(self):
        self.assert_rejected(lambda d: d.__setitem__("next_gate", "live"))

    def test_live_rejected(self):
        self.assert_rejected(lambda d: d.__setitem__("live", True))

    def test_candidate_creation_rejected(self):
        self.assert_rejected(lambda d: d["population_execution_readiness_records"][0].__setitem__("candidate_created", True))

    def test_source_resolution_rejected(self):
        self.assert_rejected(lambda d: d["population_execution_profiles"][0]["operations"][0].__setitem__("source_resolved", True))

    def test_value_insertion_rejected(self):
        self.assert_rejected(lambda d: d["population_execution_profiles"][0]["operations"][0].__setitem__("value", "inserted"))

    def test_operation_dispatch_rejected(self):
        self.assert_rejected(lambda d: d["population_execution_profiles"][0]["operations"][0].__setitem__("dispatch_permitted", True))

    def test_operation_order_rejected(self):
        self.assert_rejected(lambda d: d["population_execution_profiles"][0]["operations"][0].__setitem__("sequence", 2))

    def test_active_stage_rejected(self):
        self.assert_rejected(lambda d: d["population_execution_profiles"][0]["stages"][0].__setitem__("state", "active"))

    def test_evaluated_precondition_rejected(self):
        self.assert_rejected(lambda d: d["population_execution_profiles"][0]["preconditions"][0].__setitem__("state", "passed"))

    def test_rollback_invocation_rejected(self):
        self.assert_rejected(lambda d: d["population_execution_profiles"][0]["rollback_rules"][0].__setitem__("invocation_permitted", True))

    def test_ticket_contamination_rejected(self):
        self.assert_rejected(lambda d: d["population_execution_profiles"][0]["execution_ticket_template"].__setitem__("ticket_id", "ticket-1"))

    def test_human_gate_satisfaction_rejected(self):
        self.assert_rejected(lambda d: d["population_execution_readiness_records"][0].__setitem__("human_gate_satisfied_count", 1))

    def test_authorization_grant_rejected(self):
        self.assert_rejected(lambda d: d["population_execution_readiness_records"][0].__setitem__("authorization_granted", True))

    def test_decision_rejected(self):
        self.assert_rejected(lambda d: d["population_execution_readiness_records"][0].__setitem__("decision_selected", True))

    def test_reviewer_contact_rejected(self):
        self.assert_rejected(lambda d: d["population_execution_readiness_records"][0].__setitem__("reviewer_contact_count", 1))

    def test_atlas_permission_rejected(self):
        self.assert_rejected(lambda d: d["authority"].__setitem__("atlas_call_permitted", True))

    def test_network_requirement_rejected(self):
        self.assert_rejected(lambda d: d["authority"].__setitem__("external_network_required", True))

    def test_profile_role_assignment_rejected(self):
        self.assert_rejected(lambda d: d["population_execution_profiles"][0].__setitem__("assigned_role_count", 1))

    def test_ledger_chain_rejected(self):
        self.assert_rejected(lambda d: d["ledger"]["entries"][1]["entry"].__setitem__("previous_entry_sha256", None))

    def test_recovery_matrix_rejected(self):
        self.assert_rejected(lambda d: d["recovery_matrix"].__setitem__("rejected_mutation_count", 222))

    def test_result_counter_rejected(self):
        self.assert_rejected(lambda d: d["result"].__setitem__("dispatched_operation_count", 1))


if __name__ == "__main__":
    unittest.main()
