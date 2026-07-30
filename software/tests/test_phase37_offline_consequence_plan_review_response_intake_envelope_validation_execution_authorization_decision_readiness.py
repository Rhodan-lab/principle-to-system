from __future__ import annotations
import copy,json,unittest
from pathlib import Path
from scripts.validate_phase37_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_readiness import validate_document
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/"release/phase-37-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness.json"

def load():return json.loads(PATH.read_text())
class Phase37DecisionReadinessTests(unittest.TestCase):
 def assertRejected(self,mutator):
  doc=load();mutator(doc);self.assertTrue(validate_document(doc))
 def test_baseline(self):self.assertEqual(validate_document(load()),[])
 def test_source_pin_drift(self):self.assertRejected(lambda d:d["source_phase36"].__setitem__("phase36_candidate_sha256","0"*64))
 def test_missing_record(self):self.assertRejected(lambda d:d["decision_readiness_records"].pop())
 def test_requirement_evaluated(self):self.assertRejected(lambda d:d["decision_policy"]["decision_requirements"][0].__setitem__("state","satisfied"))
 def test_option_selected(self):self.assertRejected(lambda d:d["decision_policy"]["decision_options"][0].__setitem__("state","selected"))
 def test_blank_record_populated(self):self.assertRejected(lambda d:d["decision_readiness_records"][0]["blank_decision_record"].__setitem__("decision_id","decision-1"))
 def test_decision_candidate_created(self):self.assertRejected(lambda d:d["decision_readiness_records"][0].__setitem__("decision_candidate_created",True))
 def test_decision_recorded(self):self.assertRejected(lambda d:d["decision_readiness_records"][0].__setitem__("authorization_decision_recorded",True))
 def test_authorization_granted(self):self.assertRejected(lambda d:d["decision_readiness_records"][0].__setitem__("authorization_granted",True))
 def test_token_issued(self):self.assertRejected(lambda d:d["decision_readiness_records"][0].__setitem__("authorization_token_issued",True))
 def test_envelope_received(self):self.assertRejected(lambda d:d["decision_readiness_records"][0].__setitem__("response_envelope_received",True))
 def test_atlas_enabled(self):self.assertRejected(lambda d:d["authority"].__setitem__("atlas_call_permitted",True))
 def test_ledger_drift(self):self.assertRejected(lambda d:d["ledger"]["entries"][0].__setitem__("entry_sha256","0"*64))
if __name__=="__main__":unittest.main()
