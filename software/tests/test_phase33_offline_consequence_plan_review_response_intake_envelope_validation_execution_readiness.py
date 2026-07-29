from __future__ import annotations
import copy, hashlib, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; SCRIPTS=ROOT/"scripts"
if str(SCRIPTS) not in sys.path: sys.path.insert(0,str(SCRIPTS))
import generate_phase33_offline_consequence_plan_review_response_intake_envelope_validation_execution_readiness as p
import validate_phase33_offline_consequence_plan_review_response_intake_envelope_validation_execution_readiness as v

class Phase33Tests(unittest.TestCase):
    def setUp(self): self.d=p.build_document()
    def test_sources_exact(self): self.assertEqual(p.verify_sources(),[])
    def test_generated_bytes_exact(self):
        text=p.OUT.read_text(); self.assertEqual(text,p.render(self.d))
        self.assertEqual(hashlib.sha256(text.encode()).hexdigest(),"6e0eee781b4a8b76baf1d29e8504fac0686cf306d052d69bd2e3966071562284")
    def test_validator_accepts_baseline(self): self.assertEqual(v.validate(),[])
    def test_blueprint_is_inactive(self):
        bp=self.d["execution_blueprint"]
        self.assertEqual(len(bp["stages"]),9); self.assertEqual(len(bp["preconditions"]),20); self.assertEqual(len(bp["required_validation_controls"]),18)
        self.assertTrue(all(x["state"]=="defined-not-active" for x in bp["stages"]))
        self.assertTrue(all(x["state"]=="required-not-evaluated" for x in bp["preconditions"]))
        self.assertTrue(all(x["state"]=="defined-not-active" for x in bp["dispositions"]))
    def test_profiles_bind_blueprint(self):
        digest=p.sha_doc(self.d["execution_blueprint"])
        self.assertTrue(all(x["blueprint_sha256"]==digest for x in self.d["execution_profiles"]))
        self.assertTrue(all(x["blueprint_sha256"]==digest for x in self.d["execution_readiness_records"]))
    def test_tickets_are_blank(self):
        for r in self.d["execution_readiness_records"]:
            t=r["blank_execution_ticket"]; self.assertFalse(t["issued"]); self.assertTrue(all(t[x] is None for x in p.BLANK_TICKET_FIELDS))
    def test_runtime_states_are_zero(self):
        for r in self.d["execution_readiness_records"]: self.assertTrue(all(r[x] is False for x in p.ZERO_FIELDS))
        self.assertEqual(self.d["result"]["execution_run_count"],0); self.assertEqual(self.d["result"]["validation_result_recorded_count"],0)
    def test_authority_is_bounded(self):
        a=self.d["authority"]; self.assertTrue(a["local_response_envelope_validation_execution_readiness_permitted"])
        for k,val in a.items():
            if k=="local_response_envelope_validation_execution_readiness_permitted": continue
            self.assertEqual(val,"prohibited" if k=="status_inheritance" else False)
    def test_ledger_binds_records(self):
        prev=None
        for i,w in enumerate(self.d["ledger"]["entries"],1):
            e=w["entry"]; self.assertEqual(e["previous_entry_sha256"],prev); self.assertEqual(e["record_sha256"],p.sha_doc(self.d["execution_readiness_records"][i-1]))
            prev=p.sha_doc(e); self.assertEqual(w["entry_sha256"],prev)
        self.assertEqual(self.d["ledger"]["head_sha256"],prev)
    def test_ticket_mutation_rejected(self):
        m=copy.deepcopy(self.d); m["execution_readiness_records"][0]["blank_execution_ticket"]["execution_run_id"]="forbidden"; self.assertEqual(p.validate_document(m),["document drift"])
    def test_execution_or_blueprint_mutation_rejected(self):
        m=copy.deepcopy(self.d); m["authority"]["response_envelope_validation_execution_authorized"]=True; self.assertEqual(p.validate_document(m),["document drift"])
        m=copy.deepcopy(self.d); m["execution_blueprint"]["preconditions"][0]["state"]="satisfied"; self.assertEqual(p.validate_document(m),["document drift"])
if __name__=="__main__": unittest.main()
