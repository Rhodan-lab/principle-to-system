#!/usr/bin/env python3
"""Generate deterministic Phase 44 assembly-readiness assurance evidence."""
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT/'release/phase-43-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness.json'
POST=ROOT/'release/phase-43-postmerge.json'
OUT=ROOT/'release/phase-44-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance.json'
SRC_SHA='5ffd6005a907742ac0c02c4077d68d8f1f646963a030405e53daed2219802ef3'
POST_SHA='bbec0856c15c3286e9698d1a738cd9a7e77b13fc110b8aa0571cd4f9632d8488'
HEAD='faa7b7f698767722bc58cd8785e04f1ac278f927'; MERGE='0c1938169137ef9b5eead27f39e2b7c07f614f5b'; FINAL='2462efed6c42b8cb57bb78f5cf2603dc1ecf65c9'
MODE='offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance'
STATE=MODE+'-candidate'; DECISION='response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assured-no-candidate-assembled'
NEXT='offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-candidate'
CHECKS=(
'source-candidate','source-postmerge','source-phase','source-state','source-decision','source-next-gate','source-workflows','source-zero-effects',
'source-policy-count','source-profile-count','source-record-count','source-check-count','source-slot-count','source-stage-count','source-requirement-count','source-human-gates',
'policy-binding','profile-binding','record-binding','record-sequence','check-set','check-count','failed-checks-zero','verdict',
'slots-unpopulated','stages-inactive','requirements-unevaluated','candidate-absent','assembly-absent','population-absent','decision-absent','grant-absent',
'token-absent','ticket-absent','run-absent','envelope-absent','validation-absent','reviewer-absent','human-gates-unsatisfied','audit-absent',
'status-unchanged','atlas-forbidden','network-offline','repository-readonly','live-false','ledger-chain','checkpoint','authority-separated')
assert len(CHECKS)==48

def canon(v:Any)->bytes:return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n').encode()
def h(v:Any)->str:return hashlib.sha256(canon(v)).hexdigest()
def fh(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def signed(v:dict)->dict:
 d=copy.deepcopy(v);d['sha256']=h(d);return d

def build()->dict:
 policy=signed({'id':'principia-phase44-assembly-readiness-assurance-policy','version':'0.1','checks':list(CHECKS),'source_candidate_sha256':SRC_SHA,'source_postmerge_sha256':POST_SHA,'assurance_permitted':True,'candidate_creation_permitted':False,'candidate_population_permitted':False,'candidate_assembly_permitted':False})
 profiles=[];records=[];check_sha=h(list(CHECKS))
 for n in (1,2):
  p=signed({'id':f'principia:phase44-assurance-profile:{n:04d}','sequence':n,'source_sequence':n,'policy_sha256':policy['sha256'],'source_candidate_sha256':SRC_SHA,'source_postmerge_sha256':POST_SHA,'dual_control_preserved':True,'role_independence_preserved':True})
  profiles.append(p)
  r={'id':f'principia:phase44-assurance-record:{n:04d}','sequence':n,'source_sequence':n,'policy_sha256':policy['sha256'],'profile_sha256':p['sha256'],'check_set_sha256':check_sha,'passed_check_count':48,'failed_check_count':0,'source_slot_count':18,'populated_slot_count':0,'source_stage_count':16,'active_stage_count':0,'source_requirement_count':32,'evaluated_requirement_count':0,'human_gate_pending_count':4,'human_gate_satisfied_count':0,'candidate_created':False,'candidate_populated':False,'candidate_assembled':False,'decision_recorded':False,'authorization_granted':False,'token_issued':False,'ticket_issued':False,'execution_run_created':False,'envelope_received':False,'reviewer_identity_count':0,'reviewer_contact_count':0,'validation_result_count':0,'audit_event_count':0,'status_change_count':0,'real_authorization_claimed':False,'local_only':True,'status':'assembly-readiness-assured-no-candidate','verdict':DECISION}
  records.append(signed(r))
 entries=[];prev=None
 for r in records:
  e={'sequence':r['sequence'],'previous_entry_sha256':prev,'record_id':r['id'],'record_sha256':r['sha256']};prev=h(e);entries.append({'entry':e,'entry_sha256':prev})
 authority={'local_assembly_readiness_assurance_permitted':True,'candidate_creation_permitted':False,'candidate_population_permitted':False,'candidate_assembly_permitted':False,'candidate_persistence_permitted':False,'candidate_submission_permitted':False,'decision_recording_permitted':False,'authorization_grant_permitted':False,'token_issuance_permitted':False,'execution_ticket_issuance_permitted':False,'validation_execution_permitted':False,'reviewer_contact_permitted':False,'atlas_call_permitted':False,'external_network_required':False,'repository_mutation':False,'automatic_release_action':False,'automatic_status_change':False,'human_authorization_claimed':False,'status_inheritance':'prohibited'}
 result={'assurance_policy_count':1,'assurance_profile_count':2,'assurance_record_count':2,'assurance_check_count':96,'failed_assurance_check_count':0,'source_policy_count':1,'source_profile_count':2,'source_record_count':2,'source_check_count':128,'source_slot_count':36,'populated_slot_count':0,'source_stage_count':32,'active_stage_count':0,'source_requirement_count':64,'evaluated_requirement_count':0,'human_gate_pending_count':8,'human_gate_satisfied_count':0,'candidate_count':0,'decision_count':0,'grant_count':0,'token_count':0,'ticket_count':0,'run_count':0,'envelope_count':0,'reviewer_identity_count':0,'reviewer_contact_count':0,'validation_result_count':0,'audit_event_count':0,'status_change_count':0,'real_authorization_claimed':False}
 source={'candidate_sha256':SRC_SHA,'postmerge_sha256':POST_SHA,'candidate_head_commit':HEAD,'candidate_merge_commit':MERGE,'authoritative_finalization_commit':FINAL,'applicable_workflows':37,'state':'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-validated','policy_count':1,'profile_count':2,'record_count':2,'check_count':128,'failed_check_count':0,'slot_count':36,'populated_slot_count':0,'stage_count':32,'active_stage_count':0,'requirement_count':64,'evaluated_requirement_count':0,'human_gate_pending_count':8,'human_gate_satisfied_count':0}
 return {'contract':'principia-phase44-assembly-readiness-assurance/0.1','phase':44,'mode':MODE,'state':STATE,'decision':DECISION,'next_gate':NEXT,'fixture_kind':'bounded-synthetic','live':False,'live_activation_permitted':False,'real_authorization_claimed':False,'source_phase43':source,'assurance_policy':policy,'assurance_profiles':profiles,'assurance_records':records,'ledger':{'entries':entries,'head_sequence':2,'head_sha256':prev},'checkpoint':{'record_count':2,'check_count':96,'failed_check_count':0,'candidate_count':0,'populated_slot_count':0,'human_gate_satisfied_count':0,'status_change_count':0,'ledger_sha256':prev},'recovery':{'accepted':['baseline-phase44-assurance'],'accepted_count':1,'record_count':2,'check_families':48,'structural_mutations_per_record':12,'global_mutations':5,'scenario_count':126,'rejected_count':125},'authority':authority,'result':result,'validation':{'status':'candidate','pull_request':None,'tested_head_commit':None}}

def sources()->list[str]:
 e=[]
 if not SRC.is_file() or fh(SRC)!=SRC_SHA:e.append('Phase 43 candidate source drift')
 if not POST.is_file() or fh(POST)!=POST_SHA:return e+['Phase 43 postmerge source drift']
 p=json.loads(POST.read_text())
 expected={'phase':43,'state':'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-validated','decision':'response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-defined-no-candidate-assembled','next_gate':STATE,'live':False,'real_authorization_claimed':False}
 for k,v in expected.items():
  if p.get(k)!=v:e.append(f'Phase 43 {k} drift')
 if p.get('validation')!={'applicable_workflows':37,'candidate_head_commit':HEAD,'status':'success'}:e.append('Phase 43 validation drift')
 return e

def main()->int:
 a=argparse.ArgumentParser();g=a.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');x=a.parse_args();e=sources()
 if e:print('\n'.join(e));return 1
 data=canon(build())
 if x.write:OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_bytes(data);print(f'wrote {OUT.relative_to(ROOT)} sha256={hashlib.sha256(data).hexdigest()}');return 0
 if not OUT.is_file() or OUT.read_bytes()!=data:print('Phase 44 deterministic bytes drift');return 1
 print(f'Phase 44 deterministic bytes passed: sha256={hashlib.sha256(data).hexdigest()}');return 0
if __name__=='__main__':raise SystemExit(main())
