from __future__ import annotations
import copy, importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'scripts/generate_phase27_offline_consequence_plan_review_response_intake_readiness.py'
s=importlib.util.spec_from_file_location('phase27',p);g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
class Tests(unittest.TestCase):
 def test_deterministic(self):self.assertEqual(g.render(g.build()),g.render(g.build()))
 def test_records(self):
  rs=g.build_records();self.assertEqual(len(rs),2)
  for r in rs:self.assertEqual(g.validate_record(r),[])
 def test_zero_effects(self):
  x=g.build();self.assertEqual(x['result']['response_received_count'],0);self.assertEqual(x['result']['review_started_count'],0);self.assertFalse(x['live']);self.assertFalse(x['authority']['atlas_call_permitted'])
 def test_filled_slot_rejected(self):
  r=copy.deepcopy(g.build_records()[0]);r['blank_response_template']['question_responses'][0]['response']='fabricated';self.assertIn('question',g.validate_record(r))
 def test_identity_rejected(self):
  r=copy.deepcopy(g.build_records()[0]);r['blank_response_template']['reviewer_identity']='fabricated';self.assertIn('template',g.validate_record(r))
 def test_receipt_rejected(self):
  r=copy.deepcopy(g.build_records()[0]);r['response_received']=True;self.assertIn('authority',g.validate_record(r))
 def test_recovery(self):
  r=g.build()['recovery'];self.assertEqual((r['accepted_count'],r['rejected_count'],r['scenario_count']),(1,76,77))
if __name__=='__main__':unittest.main()
