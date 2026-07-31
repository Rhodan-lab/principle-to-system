#!/usr/bin/env python3
from __future__ import annotations
import copy, importlib.util, json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / 'scripts/validate_phase46_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_readiness_assurance.py'
spec = importlib.util.spec_from_file_location('phase46_validator', VALIDATOR)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
MANIFEST = ROOT / 'release/phase-46-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance.json'

class Phase46PopulationReadinessAssuranceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads(MANIFEST.read_text(encoding='utf-8'))
    def assertRejected(self, mutate):
        value = copy.deepcopy(self.baseline)
        mutate(value)
        self.assertTrue(module.validate_document(value))
    def test_baseline_passes(self): self.assertEqual(module.validate_document(copy.deepcopy(self.baseline)), [])
    def test_source_digest_rejected(self): self.assertRejected(lambda d: d['source_phase45'].__setitem__('candidate_sha256','0'*64))
    def test_source_finalization_rejected(self): self.assertRejected(lambda d: d['source_phase45'].__setitem__('authoritative_finalization_commit','0'*40))
    def test_next_gate_rejected(self): self.assertRejected(lambda d: d.__setitem__('next_gate','invalid'))
    def test_decision_rejected(self): self.assertRejected(lambda d: d.__setitem__('decision','invalid'))
    def test_live_rejected(self): self.assertRejected(lambda d: d.__setitem__('live',True))
    def test_policy_population_permission_rejected(self): self.assertRejected(lambda d: d['population_assurance_policy'].__setitem__('candidate_population_permitted',True))
    def test_profile_independence_rejected(self): self.assertRejected(lambda d: d['population_assurance_profiles'][0].__setitem__('role_independence_required',False))
    def test_record_check_count_rejected(self): self.assertRejected(lambda d: d['population_assurance_records'][0].__setitem__('passed_check_count',79))
    def test_populated_slot_rejected(self): self.assertRejected(lambda d: d['population_assurance_records'][0].__setitem__('populated_slot_count',1))
    def test_active_stage_rejected(self): self.assertRejected(lambda d: d['population_assurance_records'][0].__setitem__('active_stage_count',1))
    def test_evaluated_requirement_rejected(self): self.assertRejected(lambda d: d['population_assurance_records'][0].__setitem__('evaluated_requirement_count',1))
    def test_human_gate_satisfaction_rejected(self): self.assertRejected(lambda d: d['population_assurance_records'][0].__setitem__('human_gate_satisfied_count',1))
    def test_candidate_creation_rejected(self): self.assertRejected(lambda d: d['population_assurance_records'][0].__setitem__('candidate_created',True))
    def test_population_start_rejected(self): self.assertRejected(lambda d: d['population_assurance_records'][0].__setitem__('candidate_population_started',True))
    def test_atlas_permission_rejected(self): self.assertRejected(lambda d: d['authority'].__setitem__('atlas_call_permitted',True))
    def test_network_requirement_rejected(self): self.assertRejected(lambda d: d['authority'].__setitem__('external_network_required',True))
    def test_reviewer_contact_rejected(self): self.assertRejected(lambda d: d['authority'].__setitem__('reviewer_contact_permitted',True))
    def test_ledger_chain_rejected(self): self.assertRejected(lambda d: d['ledger']['entries'][1]['entry'].__setitem__('previous_entry_sha256','0'*64))
    def test_recovery_matrix_rejected(self): self.assertRejected(lambda d: d['recovery_matrix'].__setitem__('rejected_mutation_count',196))
    def test_result_counter_rejected(self): self.assertRejected(lambda d: d['result'].__setitem__('candidate_count',1))

if __name__ == '__main__': unittest.main()
