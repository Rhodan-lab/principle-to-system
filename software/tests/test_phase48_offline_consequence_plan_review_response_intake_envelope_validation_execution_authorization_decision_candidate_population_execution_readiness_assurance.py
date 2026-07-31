#!/usr/bin/env python3
from __future__ import annotations
import copy, importlib.util, json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / 'scripts/validate_phase48_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_execution_readiness_assurance.py'
spec = importlib.util.spec_from_file_location('phase48_validator', VALIDATOR)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
MANIFEST = ROOT / 'release/phase-48-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance.json'

class Phase48PopulationExecutionReadinessAssuranceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads(MANIFEST.read_text(encoding='utf-8'))
    def assertRejected(self, mutate):
        value = copy.deepcopy(self.baseline)
        mutate(value)
        self.assertTrue(module.validate_document(value))
    def test_baseline_passes(self): self.assertEqual(module.validate_document(copy.deepcopy(self.baseline)), [])
    def test_source_candidate_digest_rejected(self): self.assertRejected(lambda d: d['source_phase47'].__setitem__('candidate_sha256','0'*64))
    def test_source_postmerge_digest_rejected(self): self.assertRejected(lambda d: d['source_phase47'].__setitem__('postmerge_sha256','0'*64))
    def test_source_finalization_rejected(self): self.assertRejected(lambda d: d['source_phase47'].__setitem__('authoritative_finalization_commit','0'*40))
    def test_source_workflow_count_rejected(self): self.assertRejected(lambda d: d['source_phase47'].__setitem__('applicable_workflows',39))
    def test_next_gate_rejected(self): self.assertRejected(lambda d: d.__setitem__('next_gate','invalid'))
    def test_decision_rejected(self): self.assertRejected(lambda d: d.__setitem__('decision','invalid'))
    def test_live_rejected(self): self.assertRejected(lambda d: d.__setitem__('live',True))
    def test_policy_dispatch_permission_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_policy'].__setitem__('operation_dispatch_permitted',True))
    def test_policy_stage_permission_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_policy'].__setitem__('stage_activation_permitted',True))
    def test_policy_precondition_permission_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_policy'].__setitem__('precondition_evaluation_permitted',True))
    def test_policy_rollback_permission_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_policy'].__setitem__('rollback_invocation_permitted',True))
    def test_policy_ticket_permission_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_policy'].__setitem__('execution_ticket_issuance_permitted',True))
    def test_profile_role_assignment_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_profiles'][0].__setitem__('assigned_role_count',1))
    def test_profile_independence_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_profiles'][0].__setitem__('role_independence_required',False))
    def test_record_check_count_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_records'][0].__setitem__('passed_check_count',119))
    def test_populated_slot_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_records'][0].__setitem__('populated_slot_count',1))
    def test_resolved_reference_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_records'][0].__setitem__('resolved_reference_count',1))
    def test_dispatched_operation_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_records'][0].__setitem__('operation_dispatched',True))
    def test_active_stage_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_records'][0].__setitem__('active_stage_count',1))
    def test_evaluated_precondition_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_records'][0].__setitem__('precondition_evaluated',True))
    def test_invoked_rollback_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_records'][0].__setitem__('rollback_invoked',True))
    def test_ticket_issue_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_records'][0].__setitem__('ticket_issued',True))
    def test_population_start_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_records'][0].__setitem__('candidate_population_started',True))
    def test_human_gate_satisfaction_rejected(self): self.assertRejected(lambda d: d['population_execution_assurance_records'][0].__setitem__('human_gate_satisfied_count',1))
    def test_atlas_permission_rejected(self): self.assertRejected(lambda d: d['authority'].__setitem__('atlas_call_permitted',True))
    def test_network_requirement_rejected(self): self.assertRejected(lambda d: d['authority'].__setitem__('external_network_required',True))
    def test_reviewer_contact_rejected(self): self.assertRejected(lambda d: d['authority'].__setitem__('reviewer_contact_permitted',True))
    def test_ledger_chain_rejected(self): self.assertRejected(lambda d: d['ledger']['entries'][1]['entry'].__setitem__('previous_entry_sha256','0'*64))
    def test_recovery_matrix_rejected(self): self.assertRejected(lambda d: d['recovery_matrix'].__setitem__('rejected_mutation_count',278))
    def test_result_counter_rejected(self): self.assertRejected(lambda d: d['result'].__setitem__('candidate_count',1))

if __name__ == '__main__': unittest.main()
