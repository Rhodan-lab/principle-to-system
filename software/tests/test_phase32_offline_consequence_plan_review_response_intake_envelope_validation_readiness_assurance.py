from __future__ import annotations
import copy, importlib.util, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GEN_PATH=ROOT/"scripts/generate_phase32_offline_consequence_plan_review_response_intake_envelope_validation_readiness_assurance.py"
spec=importlib.util.spec_from_file_location("phase32gen",GEN_PATH)
gen=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(gen)

class Phase32Tests(unittest.TestCase):
    def setUp(self): self.doc=gen.build_document()
    def test_document_self_validates(self): self.assertEqual([],gen.validate_document(self.doc))
    def test_two_assurances_and_66_checks(self):
        self.assertEqual(2,len(self.doc["assurances"])); self.assertEqual(66,self.doc["result"]["assurance_check_count"])
        self.assertTrue(all(a["assurance_check_count"]==33 for a in self.doc["assurances"]))
    def test_profiles_remain_inactive(self):
        for key in ("validation_run_count","validation_started_count","validation_completed_count","validation_result_recorded_count"):
            self.assertEqual(0,self.doc["result"][key])
    def test_dispositions_remain_unselected(self):
        self.assertEqual(6,self.doc["result"]["possible_disposition_count"]); self.assertEqual(0,self.doc["result"]["disposition_selected_count"])
        self.assertTrue(all(not a["disposition_selected"] for a in self.doc["assurances"]))
    def test_envelope_and_response_states_remain_zero(self):
        for key in ("response_envelope_created_count","response_envelope_received_count","response_envelope_processed_count","response_received_count","response_validated_count","response_accepted_count","response_rejected_count","response_quarantined_count"):
            self.assertEqual(0,self.doc["result"][key])
    def test_human_gates_remain_pending(self):
        self.assertEqual(8,self.doc["result"]["human_gate_pending_count"]); self.assertEqual(0,self.doc["result"]["human_gate_satisfied_count"])
    def test_authority_remains_frozen(self):
        authority=self.doc["authority"]; self.assertTrue(authority["local_response_envelope_validation_readiness_assurance_permitted"])
        for key,value in authority.items():
            if key not in ("local_response_envelope_validation_readiness_assurance_permitted","status_inheritance"): self.assertFalse(value,key)
        self.assertEqual("prohibited",authority["status_inheritance"])
    def test_ledger_chain_is_bound(self):
        ledger=self.doc["ledger"]; self.assertEqual(2,ledger["head_sequence"])
        self.assertEqual(ledger["entries"][0]["entry_sha256"],ledger["entries"][1]["entry"]["previous_entry_sha256"])
        self.assertEqual(ledger["entries"][-1]["entry_sha256"],ledger["head_sha256"])
    def test_recovery_matrix_rejects_mutations(self):
        recovery=self.doc["recovery"]; self.assertEqual(1,recovery["accepted_count"]); self.assertEqual(111,recovery["rejected_count"]); self.assertEqual(112,recovery["scenario_count"])
    def test_mutated_check_fails_document_equality(self):
        mutated=copy.deepcopy(self.doc); mutated["assurances"][0]["assurance_checks"]["stage_order_exact"]=False; self.assertTrue(gen.validate_document(mutated))
    def test_mutated_authority_fails_document_equality(self):
        mutated=copy.deepcopy(self.doc); mutated["authority"]["response_envelope_validation_execution_authorized"]=True; self.assertTrue(gen.validate_document(mutated))

if __name__=="__main__": unittest.main()
