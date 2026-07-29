#!/usr/bin/env python3
"""Validate the finalized Phase 27 response-intake readiness record."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from typing import Any, Mapping
ROOT=Path(__file__).resolve().parent.parent
STATE_PATH=ROOT/'PROJECT_STATE.md'
CANDIDATE_PATH=ROOT/'release/phase-27-offline-consequence-plan-review-response-intake-readiness.json'
FINALIZATION_PATH=ROOT/'release/phase-27-postmerge.json'
REPORT_PATH=ROOT/'reports/phase-27-offline-consequence-plan-review-response-intake-readiness.md'
WORKFLOW_PATH=ROOT/'.github/workflows/validate-phase-27-offline-consequence-plan-review-response-intake-readiness.yml'
EXPECTED_HEAD='2a1cd76562e6392121b265e5f668c2608cf19a56'
EXPECTED_MERGE='b8b5ec9a4c56342f22162c759f3d63585ed7cf43'
EXPECTED_SHA='9175291eaca5cae5d43e0ba71f85232712e40d9ae16d2767fc360363b7828589'
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path:Path)->dict[str,Any]:
 value=json.loads(path.read_text(encoding='utf-8'))
 if not isinstance(value,dict):raise ValueError(path)
 return value
def fail(errors:list[str])->int:
 print('Phase 27 post-merge record errors:',file=sys.stderr);[print(f'- {e}',file=sys.stderr) for e in errors];return 1
def main()->int:
 errors=[]
 for path in (STATE_PATH,CANDIDATE_PATH,FINALIZATION_PATH,REPORT_PATH,WORKFLOW_PATH):
  if not path.is_file():errors.append(f'missing {path.relative_to(ROOT)}')
 if errors:return fail(errors)
 if sha(CANDIDATE_PATH)!=EXPECTED_SHA:errors.append('candidate digest changed after merge')
 f=load(FINALIZATION_PATH)
 expected={'contract':'principia-offline-consequence-plan-review-response-intake-readiness-finalization/0.1','phase':27,'state':'offline-consequence-plan-review-response-intake-readiness-validated','mode':'offline-consequence-plan-review-response-intake-readiness','fixture_kind':'bounded-synthetic','decision':'response-intake-readiness-recorded-no-response-received','live':False,'next_gate':'offline-consequence-plan-review-response-intake-readiness-assurance-candidate','live_activation_permitted':False,'real_authorization_claimed':False}
 for k,v in expected.items():
  if f.get(k)!=v:errors.append(f'{k} drift')
 if f.get('candidate_record')!={'path':'release/phase-27-offline-consequence-plan-review-response-intake-readiness.json','sha256':EXPECTED_SHA}:errors.append('candidate pin')
 if f.get('principia')!={'repository':'Rhodan-lab/principle-to-system','pull_request':45,'candidate_head_commit':EXPECTED_HEAD,'merge_commit':EXPECTED_MERGE}:errors.append('provenance')
 if f.get('validation')!={'applicable_workflows':21,'candidate_head_commit':EXPECTED_HEAD,'status':'success'}:errors.append('validation provenance')
 result=f.get('result',{})
 for k,v in {'intake_readiness_record_count':2,'response_schema_count':2,'response_schema_section_count':12,'required_field_count':30,'blank_question_slot_count':6,'human_gate_pending_count':8,'human_gate_satisfied_count':0,'response_intake_authorized_count':0,'response_received_count':0,'response_validated_count':0,'response_accepted_count':0,'response_rejected_count':0,'response_quarantined_count':0,'reviewer_identity_count':0,'reviewer_contact_count':0,'review_started_count':0,'review_completed_count':0,'status_change_count':0,'real_authorization_claimed':False}.items():
  if result.get(k)!=v:errors.append(f'result {k}')
 authority=f.get('authority')
 if not isinstance(authority,Mapping):errors.append('authority missing')
 else:
  for k in ('atlas_call_permitted','automatic_release_action','automatic_status_change','external_delivery_permitted','external_network_required','human_authorization_claimed','repository_mutation','response_intake_authorized','response_receipt_permitted','response_validation_authorized','review_execution_authorized','review_request_dispatch_authorized','reviewer_contact_permitted'):
   if authority.get(k) is not False:errors.append(f'authority {k}')
  if authority.get('local_response_intake_readiness_permitted') is not True:errors.append('local readiness disabled')
  if authority.get('status_inheritance')!='prohibited':errors.append('status inheritance')
 state=STATE_PATH.read_text(encoding='utf-8')
 for marker in ('**Phase 27 — Offline Consequence-Plan Review-Response Intake Readiness merged and validated through PR #45.**','Phase 27 state: **offline-consequence-plan-review-response-intake-readiness-validated**','| 27 | Offline consequence-plan review-response intake readiness | Merged and validated through PR #45 |',f'Phase 27 exact candidate validation passed at `{EXPECTED_HEAD}`',f'PR #45 was merged into `main` at commit `{EXPECTED_MERGE}`','release/phase-27-postmerge.json','Historical Phase 27 candidate marker: `exact-head validation pending`','offline-consequence-plan-review-response-intake-readiness-assurance-candidate','response-intake-readiness-recorded-no-response-received','response-intake-schema-ready-no-response','intake_readiness_record_count: 2','response_received_count: 0','human_gate_pending_count: 8','real_authorization_claimed: false','Atlas remains unchanged by Principia Phase 27.','live: false'):
  if marker not in state:errors.append(f'state marker {marker}')
 report=REPORT_PATH.read_text(encoding='utf-8')
 for marker in ('# Phase 27 — Offline Consequence-Plan Review-Response Intake Readiness',f'> Exact tested head: `{EXPECTED_HEAD}`',f'> Merge commit: `{EXPECTED_MERGE}`','> Final state: `offline-consequence-plan-review-response-intake-readiness-validated`','release/phase-27-postmerge.json','2 readiness records','6 blank question slots','8 pending human gates','response-intake-readiness-recorded-no-response-received','> Live: `false`'):
  if marker not in report:errors.append(f'report marker {marker}')
 workflow=WORKFLOW_PATH.read_text(encoding='utf-8')
 for marker in ('agent/finalize-phase-27-record','scripts/validate_phase27_postmerge_record.py','release/phase-27-postmerge.json','contents: read'):
  if marker not in workflow:errors.append(f'workflow marker {marker}')
 for forbidden in ('contents: write','git push','git commit','pull_request_target','repository: Rhodan-lab/Atlas','curl ','wget '):
  if forbidden in workflow:errors.append(f'forbidden {forbidden}')
 if errors:return fail(sorted(set(errors)))
 print('Phase 27 post-merge record passed: exact candidate and PR pinned, two schemas ready, zero responses received.');return 0
if __name__=='__main__':raise SystemExit(main())
