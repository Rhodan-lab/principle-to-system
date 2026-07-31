#!/usr/bin/env python3
from __future__ import annotations
import copy, importlib.util, json, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts/validate_phase49_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_execution_authorization_readiness.py"
MANIFEST = ROOT / "release/phase-49-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness.json"
spec = importlib.util.spec_from_file_location("phase49_validator", VALIDATOR)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

class Phase49AuthorizationReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def assertRejected(self, mutate):
        value = copy.deepcopy(self.baseline)
        mutate(value)
        self.assertTrue(module.validate_document(value))

    def test_baseline_passes(self): self.assertEqual(module.validate_document(copy.deepcopy(self.baseline)), [])
    def test_source_candidate_rejected(self): self.assertRejected(lambda d: d["source_phase48"].__setitem__("candidate_sha256", "0"*64))
    def test_source_postmerge_rejected(self): self.assertRejected(lambda d: d["source_phase48"].__setitem__("postmerge_sha256", "0"*64))
    def test_source_finalization_rejected(self): self.assertRejected(lambda d: d["source_phase48"].__setitem__("authoritative_finalization_commit", "0"*40))
    def test_next_gate_rejected(self): self.assertRejected(lambda d: d.__setitem__("next_gate", "invalid"))
    def test_live_rejected(self): self.assertRejected(lambda d: d.__setitem__("live", True))
    def test_policy_digest_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_policy"].__setitem__("source_assurance_policy_sha256", "0"*64))
    def test_policy_grant_permission_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_policy"].__setitem__("authorization_grant_permitted", True))
    def test_profile_source_record_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0].__setitem__("source_population_execution_assurance_record_sha256", "0"*64))
    def test_profile_role_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["required_roles"].__setitem__(0, "other"))
    def test_profile_assigned_role_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0].__setitem__("assigned_role_count", 1))
    def test_stage_active_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["authorization_stages"][0].__setitem__("state", "active"))
    def test_stage_permission_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["authorization_stages"][0].__setitem__("activation_permitted", True))
    def test_requirement_evaluated_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["authorization_requirements"][0].__setitem__("state", "satisfied"))
    def test_requirement_permission_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["authorization_requirements"][0].__setitem__("evaluation_permitted", True))
    def test_approval_satisfied_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["approval_roles"][0].__setitem__("state", "satisfied"))
    def test_approval_identity_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["approval_roles"][0].__setitem__("identity", "person"))
    def test_scope_network_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["authorization_scope"].__setitem__("external_network", True))
    def test_scope_atlas_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["authorization_scope"].__setitem__("atlas_access", True))
    def test_scope_write_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["authorization_scope"].__setitem__("repository_write", True))
    def test_scope_operation_digest_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["authorization_scope"].__setitem__("operation_set_sha256", "0"*64))
    def test_validity_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["validity_window_policy"].__setitem__("maximum_seconds", 901))
    def test_revocation_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["revocation_policy"].__setitem__("immediate_revocation_supported", False))
    def test_token_issued_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["authorization_token_template"].__setitem__("issued", True))
    def test_token_field_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_profiles"][0]["authorization_token_template"].__setitem__("authorization_id", "auth-1"))
    def test_record_grant_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_records"][0].__setitem__("authorization_granted", True))
    def test_record_request_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_records"][0].__setitem__("authorization_request_created", True))
    def test_operation_dispatch_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_records"][0].__setitem__("operation_dispatched", True))
    def test_human_gate_rejected(self): self.assertRejected(lambda d: d["authorization_readiness_records"][0].__setitem__("human_gate_satisfied_count", 1))
    def test_ledger_chain_rejected(self): self.assertRejected(lambda d: d["ledger"]["entries"][1]["entry"].__setitem__("previous_entry_sha256", "0"*64))
    def test_recovery_matrix_rejected(self): self.assertRejected(lambda d: d["recovery_matrix"].__setitem__("rejected_mutation_count", 316))
    def test_authority_grant_rejected(self): self.assertRejected(lambda d: d["authority"].__setitem__("authorization_grant_permitted", True))
    def test_result_counter_rejected(self): self.assertRejected(lambda d: d["result"].__setitem__("authorization_grant_count", 1))

if __name__ == "__main__":
    unittest.main()
