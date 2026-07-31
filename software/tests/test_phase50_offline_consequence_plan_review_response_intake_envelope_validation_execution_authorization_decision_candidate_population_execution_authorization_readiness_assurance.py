#!/usr/bin/env python3
from __future__ import annotations
import copy, importlib.util, json, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / 'scripts/validate_phase50_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_execution_authorization_readiness_assurance.py'
spec = importlib.util.spec_from_file_location("phase50_validator", VALIDATOR)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
MANIFEST = ROOT / 'release/phase-50-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-assurance.json'

class Phase50AuthorizationReadinessAssuranceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def assertRejected(self, mutate):
        value = copy.deepcopy(self.baseline)
        mutate(value)
        self.assertTrue(module.validate_document(value))

    def test_baseline_passes(self):
        self.assertEqual(module.validate_document(copy.deepcopy(self.baseline)), [])

    def test_source_candidate_rejected(self): self.assertRejected(lambda d: d['source_phase49'].__setitem__('candidate_sha256','0'*64))
    def test_source_postmerge_rejected(self): self.assertRejected(lambda d: d['source_phase49'].__setitem__('postmerge_sha256','0'*64))
    def test_source_finalization_rejected(self): self.assertRejected(lambda d: d['source_phase49'].__setitem__('authoritative_finalization_commit','0'*40))
    def test_next_gate_rejected(self): self.assertRejected(lambda d: d.__setitem__('next_gate','invalid'))
    def test_decision_rejected(self): self.assertRejected(lambda d: d.__setitem__('decision','invalid'))
    def test_live_rejected(self): self.assertRejected(lambda d: d.__setitem__('live',True))
    def test_policy_source_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_policy'].__setitem__('source_authorization_policy_sha256','0'*64))
    def test_policy_checks_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_policy']['check_ids'].__setitem__(0,'invalid'))
    def test_policy_stage_count_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_policy'].__setitem__('authorization_stage_count',23))
    def test_policy_requirement_count_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_policy'].__setitem__('authorization_requirement_count',63))
    def test_policy_role_count_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_policy'].__setitem__('required_approval_role_count',5))
    def test_policy_token_count_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_policy'].__setitem__('blank_authorization_token_count',1))
    def test_policy_request_permission_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_policy'].__setitem__('authorization_request_creation_permitted',True))
    def test_profile_source_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_profiles'][0].__setitem__('source_authorization_profile_sha256','0'*64))
    def test_profile_independence_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_profiles'][0].__setitem__('role_independence_required',False))
    def test_profile_execution_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_profiles'][0].__setitem__('assurance_execution_permitted',True))
    def test_record_check_count_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_records'][0].__setitem__('passed_check_count',143))
    def test_record_active_auth_stage_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_records'][0].__setitem__('active_authorization_stage_count',1))
    def test_record_eval_requirement_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_records'][0].__setitem__('evaluated_authorization_requirement_count',1))
    def test_record_satisfied_role_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_records'][0].__setitem__('satisfied_approval_role_count',1))
    def test_record_token_field_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_records'][0].__setitem__('blank_authorization_token_field_count',17))
    def test_record_request_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_records'][0].__setitem__('authorization_request_created',True))
    def test_record_approval_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_records'][0].__setitem__('approval_evaluated',True))
    def test_record_decision_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_records'][0].__setitem__('authorization_decision_recorded',True))
    def test_record_grant_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_records'][0].__setitem__('authorization_granted',True))
    def test_record_token_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_records'][0].__setitem__('authorization_token_issued',True))
    def test_record_dispatch_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_records'][0].__setitem__('operation_dispatched',True))
    def test_record_candidate_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_records'][0].__setitem__('candidate_created',True))
    def test_record_reviewer_rejected(self): self.assertRejected(lambda d: d['authorization_assurance_records'][0].__setitem__('reviewer_contact_count',1))
    def test_authority_atlas_rejected(self): self.assertRejected(lambda d: d['authority'].__setitem__('atlas_call_permitted',True))
    def test_authority_network_rejected(self): self.assertRejected(lambda d: d['authority'].__setitem__('external_network_required',True))
    def test_authority_repository_rejected(self): self.assertRejected(lambda d: d['authority'].__setitem__('repository_mutation',True))
    def test_ledger_chain_rejected(self): self.assertRejected(lambda d: d['ledger']['entries'][1]['entry'].__setitem__('previous_entry_sha256','0'*64))
    def test_recovery_matrix_rejected(self): self.assertRejected(lambda d: d['recovery_matrix'].__setitem__('rejected_mutation_count',346))
    def test_result_counter_rejected(self): self.assertRejected(lambda d: d['result'].__setitem__('authorization_grant_count',1))

if __name__ == "__main__":
    unittest.main()
