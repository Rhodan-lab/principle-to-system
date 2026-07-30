from __future__ import annotations
import copy, importlib.util, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SCRIPTS=ROOT/'scripts'
sys.path.insert(0,str(SCRIPTS))
import generate_phase39_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_boundary_readiness as gen
import validate_phase39_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_boundary_readiness as val

class Phase39Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=gen.build_manifest(gen.load(gen.SOURCE),gen.load(gen.SOURCE_POST))
    def reject(self,mut):
        value=copy.deepcopy(self.base);mut(value);self.assertTrue(val.validate_manifest(value))
    def test_baseline(self): self.assertEqual(val.validate_manifest(copy.deepcopy(self.base)),[])
    def test_candidate_creation_rejected(self): self.reject(lambda v:v['boundary_readiness_records'][0].__setitem__('authorization_decision_candidate_created',True))
    def test_template_population_rejected(self): self.reject(lambda v:v['boundary_readiness_records'][0]['candidate_template'].__setitem__('candidate_id','forbidden'))
    def test_stage_activation_rejected(self): self.reject(lambda v:v['boundary_policy']['boundary_stages'][0].__setitem__('state','active'))
    def test_requirement_evaluation_rejected(self): self.reject(lambda v:v['boundary_policy']['boundary_requirements'][0].__setitem__('state','satisfied'))
    def test_conflict_evaluation_rejected(self): self.reject(lambda v:v['boundary_readiness_records'][0].__setitem__('conflict_declaration_evaluated',True))
    def test_approval_evidence_rejected(self): self.reject(lambda v:v['boundary_readiness_records'][0].__setitem__('approval_evidence_recorded',True))
    def test_reviewer_contact_rejected(self): self.reject(lambda v:v['boundary_readiness_records'][0].__setitem__('reviewer_contact_permitted',True))
    def test_authorization_grant_rejected(self): self.reject(lambda v:v['boundary_readiness_records'][1].__setitem__('authorization_granted',True))
    def test_atlas_call_rejected(self): self.reject(lambda v:v['authority'].__setitem__('atlas_call_permitted',True))
    def test_ledger_drift_rejected(self): self.reject(lambda v:v['ledger']['entries'][1]['entry'].__setitem__('previous_entry_sha256','0'*64))
    def test_gate_drift_rejected(self): self.reject(lambda v:v.__setitem__('next_gate','forbidden'))
    def test_live_rejected(self): self.reject(lambda v:v.__setitem__('live',True))
    def test_missing_record_rejected(self): self.reject(lambda v:v['boundary_readiness_records'].pop())

if __name__=='__main__':unittest.main()
