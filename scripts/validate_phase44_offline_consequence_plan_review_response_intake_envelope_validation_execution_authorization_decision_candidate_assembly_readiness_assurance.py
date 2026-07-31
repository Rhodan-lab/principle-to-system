#!/usr/bin/env python3
"""Independently validate Phase 44 assembly-readiness assurance."""
from __future__ import annotations
import copy,hashlib,json,sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent.parent
M=ROOT/'release/phase-44-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance.json'
SRC=ROOT/'release/phase-43-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness.json';POST=ROOT/'release/phase-43-postmerge.json'
M_SHA='f6e807f7c56513c0a13265f833cefeca3f9b9503d52b8826a4055069220d08c6';SRC_SHA='5ffd6005a907742ac0c02c4077d68d8f1f646963a030405e53daed2219802ef3';POST_SHA='bbec0856c15c3286e9698d1a738cd9a7e77b13fc110b8aa0571cd4f9632d8488'
HEAD='faa7b7f698767722bc58cd8785e04f1ac278f927';MERGE='0c1938169137ef9b5eead27f39e2b7c07f614f5b';FINAL='2462efed6c42b8cb57bb78f5cf2603dc1ecf65c9'
MODE='offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance';STATE=MODE+'-candidate';DECISION='response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assured-no-candidate-assembled';NEXT='offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-candidate'
def canon(v:Any)->bytes:return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n').encode()
def h(v:Any)->str:return hashlib.sha256(canon(v)).hexdigest()
def fh(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def req(e:list[str],c:bool,m:str):
 if not c:e.append(m)
def hashed(e:list[str],v:Any,label:str):
 req(e,isinstance(v,dict),label+' missing')
 if isinstance(v,dict):
  x=copy.deepcopy(v);s=x.pop('sha256',None);req(e,s==h(x),label+' digest drift')
def validate_document(d:Any)->list[str]:
 e=[];req(e,isinstance(d,dict),'manifest must be object')
 if not isinstance(d,dict):return e
 for k,v in {'contract':'principia-phase44-assembly-readiness-assurance/0.1','phase':44,'mode':MODE,'state':STATE,'decision':DECISION,'next_gate':NEXT,'fixture_kind':'bounded-synthetic','live':False,'live_activation_permitted':False,'real_authorization_claimed':False}.items():req(e,d.get(k)==v,k+' drift')
 source=d.get('source_phase43');expected_source={'candidate_sha256':SRC_SHA,'postmerge_sha256':POST_SHA,'candidate_head_commit':HEAD,'candidate_merge_commit':MERGE,'authoritative_finalization_commit':FINAL,'applicable_workflows':37,'state':'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-validated','policy_count':1,'profile_count':2,'record_count':2,'check_count':128,'failed_check_count':0,'slot_count':36,'populated_slot_count':0,'stage_count':32,'active_stage_count':0,'requirement_count':64,'evaluated_requirement_count':0,'human_gate_pending_count':8,'human_gate_satisfied_count':0};req(e,source==expected_source,'source binding drift')
 policy=d.get('assurance_policy');hashed(e,policy,'policy');checks=[]
 if isinstance(policy,dict):
  checks=policy.get('checks',[]);req(e,isinstance(checks,list) and len(checks)==48 and len(set(checks))==48,'check families drift')
  req(e,policy.get('source_candidate_sha256')==SRC_SHA and policy.get('source_postmerge_sha256')==POST_SHA,'policy source drift')
  req(e,policy.get('assurance_permitted') is True,'assurance disabled')
  for k in ('candidate_creation_permitted','candidate_population_permitted','candidate_assembly_permitted'):req(e,policy.get(k) is False,k+' escalated')
 profiles=d.get('assurance_profiles');records=d.get('assurance_records');req(e,isinstance(profiles,list) and len(profiles)==2,'profiles drift');req(e,isinstance(records,list) and len(records)==2,'records drift');csha=h(checks)
 if isinstance(profiles,list):
  for n,p in enumerate(profiles,1):
   hashed(e,p,f'profile {n}')
   if isinstance(p,dict):
    req(e,p.get('sequence')==n and p.get('source_sequence')==n,f'profile {n} sequence drift');req(e,p.get('policy_sha256')==(policy or {}).get('sha256'),f'profile {n} policy drift');req(e,p.get('dual_control_preserved') is True and p.get('role_independence_preserved') is True,f'profile {n} governance drift')
 rsh=[]
 if isinstance(records,list):
  for n,r in enumerate(records,1):
   hashed(e,r,f'record {n}')
   if not isinstance(r,dict):continue
   rsh.append(r.get('sha256'));req(e,r.get('sequence')==n and r.get('source_sequence')==n,f'record {n} sequence drift');req(e,r.get('policy_sha256')==(policy or {}).get('sha256'),f'record {n} policy drift');req(e,r.get('profile_sha256')==(profiles[n-1] if isinstance(profiles,list) and len(profiles)>=n else {}).get('sha256'),f'record {n} profile drift');req(e,r.get('check_set_sha256')==csha and r.get('passed_check_count')==48 and r.get('failed_check_count')==0,f'record {n} checks drift')
   for k,v in {'source_slot_count':18,'populated_slot_count':0,'source_stage_count':16,'active_stage_count':0,'source_requirement_count':32,'evaluated_requirement_count':0,'human_gate_pending_count':4,'human_gate_satisfied_count':0,'reviewer_identity_count':0,'reviewer_contact_count':0,'validation_result_count':0,'audit_event_count':0,'status_change_count':0}.items():req(e,r.get(k)==v,f'record {n} {k} drift')
   for k in ('candidate_created','candidate_populated','candidate_assembled','decision_recorded','authorization_granted','token_issued','ticket_issued','execution_run_created','envelope_received','real_authorization_claimed'):req(e,r.get(k) is False,f'record {n} {k} escalated')
   req(e,r.get('local_only') is True and r.get('status')=='assembly-readiness-assured-no-candidate' and r.get('verdict')==DECISION,f'record {n} disposition drift')
 ledger=d.get('ledger');req(e,isinstance(ledger,dict),'ledger missing');prev=None
 if isinstance(ledger,dict):
  entries=ledger.get('entries');req(e,isinstance(entries,list) and len(entries)==2,'ledger count drift')
  if isinstance(entries,list):
   for n,w in enumerate(entries,1):
    x=w.get('entry',{}) if isinstance(w,dict) else {};req(e,x.get('sequence')==n and x.get('previous_entry_sha256')==prev,f'ledger {n} chain drift');req(e,len(rsh)>=n and x.get('record_sha256')==rsh[n-1],f'ledger {n} record drift');prev=h(x);req(e,isinstance(w,dict) and w.get('entry_sha256')==prev,f'ledger {n} digest drift')
  req(e,ledger.get('head_sequence')==2 and ledger.get('head_sha256')==prev,'ledger head drift')
 authority=d.get('authority',{});req(e,isinstance(authority,dict),'authority missing')
 if isinstance(authority,dict):
  req(e,authority.get('local_assembly_readiness_assurance_permitted') is True,'local assurance forbidden')
  for k,v in authority.items():
   if k not in ('local_assembly_readiness_assurance_permitted','status_inheritance'):req(e,v is False,k+' authority escalated')
  req(e,authority.get('status_inheritance')=='prohibited','status inheritance drift')
 expected_result={'assurance_policy_count':1,'assurance_profile_count':2,'assurance_record_count':2,'assurance_check_count':96,'failed_assurance_check_count':0,'source_policy_count':1,'source_profile_count':2,'source_record_count':2,'source_check_count':128,'source_slot_count':36,'populated_slot_count':0,'source_stage_count':32,'active_stage_count':0,'source_requirement_count':64,'evaluated_requirement_count':0,'human_gate_pending_count':8,'human_gate_satisfied_count':0,'candidate_count':0,'decision_count':0,'grant_count':0,'token_count':0,'ticket_count':0,'run_count':0,'envelope_count':0,'reviewer_identity_count':0,'reviewer_contact_count':0,'validation_result_count':0,'audit_event_count':0,'status_change_count':0,'real_authorization_claimed':False};req(e,d.get('result')==expected_result,'result drift')
 req(e,d.get('checkpoint')=={'record_count':2,'check_count':96,'failed_check_count':0,'candidate_count':0,'populated_slot_count':0,'human_gate_satisfied_count':0,'status_change_count':0,'ledger_sha256':prev},'checkpoint drift');req(e,d.get('recovery')=={'accepted':['baseline-phase44-assurance'],'accepted_count':1,'record_count':2,'check_families':48,'structural_mutations_per_record':12,'global_mutations':5,'scenario_count':126,'rejected_count':125},'recovery drift');req(e,d.get('validation')=={'status':'candidate','pull_request':None,'tested_head_commit':None},'validation marker drift');return e
def sources()->list[str]:
 e=[]
 if not SRC.is_file() or fh(SRC)!=SRC_SHA:e.append('Phase 43 candidate source drift')
 if not POST.is_file() or fh(POST)!=POST_SHA:return e+['Phase 43 postmerge source drift']
 p=json.loads(POST.read_text());req(e,p.get('state')=='offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-validated','Phase 43 state drift');req(e,p.get('next_gate')==STATE,'Phase 43 next gate drift');req(e,p.get('validation')=={'applicable_workflows':37,'candidate_head_commit':HEAD,'status':'success'},'Phase 43 validation drift');return e
def main()->int:
 e=sources()
 if not M.is_file():e.append('Phase 44 manifest missing')
 else:
  if fh(M)!=M_SHA:e.append('Phase 44 manifest digest drift')
  try:d=json.loads(M.read_text())
  except Exception as x:e.append('Phase 44 parse failure: '+str(x))
  else:e+=validate_document(d)
 if e:
  print('Phase 44 validation errors:',file=sys.stderr);[print('- '+x,file=sys.stderr) for x in e];return 1
 print(f'Phase 44 assurance passed: manifest={M_SHA}, checks=96, records=2, scenarios=126.');return 0
if __name__=='__main__':raise SystemExit(main())
