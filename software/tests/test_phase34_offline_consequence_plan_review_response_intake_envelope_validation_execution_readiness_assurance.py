from __future__ import annotations
import copy, hashlib, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import generate_phase34_offline_consequence_plan_review_response_intake_envelope_validation_execution_readiness_assurance as gen

class Phase34Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path=ROOT/"release/phase-34-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance.json"
        cls.doc=json.loads(cls.path.read_text())
    def test_sources_exact(self): self.assertEqual(gen.verify_sources(),[])
    def test_generated_bytes_exact(self): self.assertEqual(self.path.read_text(),gen.render(gen.build_document()))
    def test_digest_exact(self): self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(),"2ca9b454124b1fb42f91f09479d9aed1d0c54f9ef443f121caa3a7ee67823828")
    def test_assurance_checks_all_pass(self):
        self.assertEqual(len(self.doc["assurances"]),2)
        self.assertTrue(all(r["assurance_check_count"]==44 and all(r["assurance_checks"].values()) for r in self.doc["assurances"]))
    def test_blueprint_binding_exact(self): self.assertTrue(all(r["blueprint_sha256"]==gen.BLUEPRINT_SHA for r in self.doc["assurances"]))
    def test_runtime_states_are_zero(self): self.assertTrue(all(not r[x] for r in self.doc["assurances"] for x in gen.ZERO_FIELDS))
    def test_authority_is_bounded(self):
        self.assertTrue(self.doc["authority"]["local_response_envelope_validation_execution_readiness_assurance_permitted"])
        self.assertFalse(self.doc["authority"]["response_envelope_validation_execution_authorized"])
        self.assertFalse(self.doc["authority"]["atlas_call_permitted"])
        self.assertFalse(self.doc["authority"]["repository_mutation"])
    def test_ledger_binds_records(self):
        prev=None
        for r,w in zip(self.doc["assurances"],self.doc["ledger"]["entries"]):
            self.assertEqual(w["entry"]["previous_entry_sha256"],prev)
            self.assertEqual(w["entry"]["record_sha256"],gen.sha_doc(r))
            self.assertEqual(w["entry_sha256"],gen.sha_doc(w["entry"]))
            prev=w["entry_sha256"]
    def test_assurance_mutation_rejected(self):
        d=copy.deepcopy(self.doc); d["assurances"][0]["assurance_checks"]["blueprint_digest_exact"]=False
        self.assertNotEqual(d,gen.build_document())
    def test_execution_mutation_rejected(self):
        d=copy.deepcopy(self.doc); d["assurances"][0]["execution_started"]=True
        self.assertNotEqual(d,gen.build_document())
    def test_validator_accepts_baseline(self): self.assertEqual(gen.validate_document(self.doc),[])
if __name__=="__main__": unittest.main()
