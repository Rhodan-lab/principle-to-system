#!/usr/bin/env python3
"""Validate the finalized Phase 29 response-intake envelope readiness record."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from typing import Any, Mapping
ROOT=Path(__file__).resolve().parent.parent
STATE_PATH=ROOT/'PROJECT_STATE.md'
CANDIDATE_PATH=ROOT/'release/phase-29-offline-consequence-plan-review-response-intake-envelope-readiness.json'
FINALIZATION_PATH=ROOT/'release/phase-29-postmerge.json'
REPORT_PATH=ROOT/'reports/phase-29-offline-consequence-plan-review-response-intake-envelope-readiness.md'
WORKFLOW_PATH=ROOT/'.github/workflows/validate-phase-29-offline-consequence-plan-review-response-intake-envelope-readiness.yml'
EXPECTED_HEAD='6dc0e71a54aa2b02a0249f889ad8b3153361d078'
EXPECTED_MERGE='a16a7a9490ca038a511b1fcc09d834a4b354b8d1'
EXPECTED_SHA='1c921b77459b6cf46a0add6b47a7796e69e91c6a61f817750e3277de0685e74e'
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path:Path)->dict[str,Any]:
 value=json.loads(path.read_text(encoding='utf-8'))
 if not isinstance(value,dict):raise ValueError(path)
 return value
def fail(errors:list[str])->int:
 print('Phase 29 post-merge record errors:',file=sys.stderr);[print(f'- {e}',file=sys.stderr) for e in errors];return 1
def main()->int:
 errors=[]
 for path in (STATE_PATH,CANDIDATE_PATH,FINALIZATION_PATH,REPORT_PATH,WORKFLOW_PATH):
  if not path.is_file():errors.append(f'missing {path.relative_to(ROOT)}')
 if errors:return fail(errors)
 if sha(CANDIDATE_PATH)!=EXPECTED_SHA:errors.append('candidate digest changed after merge')
 f=load(FINALIZATION_PATH)
 expected={'contract':'principia-offline-consequence-plan-review-response-intake-envelope-readiness-finalization/0.1','phase':29,'state':'offline-consequence-plan-review-response-intake-envelope-readiness-validated','mode':'offline-consequence-plan-review-response-intake-envelope-readiness','fixture_kind':'bounded-synthetic','decision':'response-intake-envelope-readiness-recorded-no-response-received','live':False,'next_gate':'offline-consequence-plan-review-response-intake-envelope-readiness-assurance-candidate','live_activation_permitted':False,'real_authorization_claimed':False}
 for k,v in expected.items():
  if f.get(k)!=v:errors.append(f'{k} drift')
 if f.get('candidate_record')!={'path':'release/phase-29-offline-consequence-plan-review-response-intake-envelope-readiness.json','sha256':EXPECTED_SHA}:errors.append('candidate pin')
 if f.get('principia')!={'repository':'Rhodan-lab/principle-to-system','pull_request':49,'candidate_head_commit':EXPECTED_HEAD,'merge_commit':EXPECTED_MERGE}:errors.append('provenance')
 if f.get('validation')!={'applicable_workflows':23,'candidate_head_commit':EXPECTED_HEAD,'status':'success'}:errors.append('validation provenance')
 result=f.get('result',{})
 expected_result={'blank_required_envelope_field_count':12,'duplicate_envelope_count':0,'envelope_readiness_record_count':2,'envelope_section_count':14,'envelope_spec_count':2,'envelope_template_count':2,'human_gate_pending_count':8,'human_gate_satisfied_count':0,'integrity_failure_count':0,'integrity_rule_count':20,'quarantine_reason_code_count':20,'quarantine_record_count':0,'required_envelope_field_count':28,'response_envelope_created_count':0,'response_envelope_processed_count':0,'response_envelope_received_count':0,'response_received_count':0,'response_validated_count':0,'review_started_count':0,'status_change_count':0,'real_authorization_claimed':False}
 for k,v in expected_result.items():
  if result.get(k)!=v:errors.append(f'result {k}')
 authority=f.get('authority')
 if not isinstance(authority,Mapping):errors.append('authority missing')
 else:
  for k in ('atlas_call_permitted','automatic_release_action','automatic_status_change','external_delivery_permitted','external_network_required','human_authorization_claimed','repository_mutation','response_envelope_creation_permitted','response_envelope_processing_authorized','response_intake_authorized','response_quarantine_execution_authorized','response_receipt_permitted','response_validation_authorized','review_execution_authorized','review_request_dispatch_authorized','reviewer_contact_permitted'):
   if authority.get(k) is not False:errors.append(f'authority {k}')
  if authority.get('local_response_envelope_readiness_permitted') is not True:errors.append('local envelope readiness disabled')
  if authority.get('status_inheritance')!='prohibited':errors.append('status inheritance')
 state=STATE_PATH.read_text(encoding='utf-8')
 for marker in ('**Phase 29 — Offline Consequence-Plan Review-Response Intake Envelope Readiness merged and validated through PR #49.**','Phase 29 state: **offline-consequence-plan-review-response-intake-envelope-readiness-validated**','| 29 | Offline consequence-plan review-response intake envelope readiness | Merged and validated through PR #49 |',f'Phase 29 exact candidate validation passed at `{EXPECTED_HEAD}`',f'PR #49 was merged into `main` at commit `{EXPECTED_MERGE}`','release/phase-29-postmerge.json','Historical Phase 29 candidate marker: `exact-head validation pending`','offline-consequence-plan-review-response-intake-envelope-readiness-assurance-candidate','response-intake-envelope-readiness-recorded-no-response-received','response-envelope-schema-ready-no-response','envelope_readiness_record_count: 2','integrity_rule_count: 20','quarantine_reason_code_count: 20','response_envelope_received_count: 0','human_gate_pending_count: 8','real_authorization_claimed: false','Atlas remains unchanged by Principia Phase 29.','live: false'):
  if marker not in state:errors.append(f'state marker {marker}')
 report=REPORT_PATH.read_text(encoding='utf-8')
 for marker in ('# Phase 29 — Offline Consequence-Plan Review-Response Intake Envelope Readiness',f'> Exact tested head: `{EXPECTED_HEAD}`',f'> Merge commit: `{EXPECTED_MERGE}`','> Final state: `offline-consequence-plan-review-response-intake-envelope-readiness-validated`','release/phase-29-postmerge.json','2','20','8','response-intake-envelope-readiness-recorded-no-response-received','> Live: `false`'):
  if marker not in report:errors.append(f'report marker {marker}')
 workflow=WORKFLOW_PATH.read_text(encoding='utf-8')
 for marker in ('agent/finalize-phase-29-record','scripts/validate_phase29_postmerge_record.py','release/phase-29-postmerge.json','contents: read'):
  if marker not in workflow:errors.append(f'workflow marker {marker}')
 for forbidden in ('contents: write','git push','git commit','pull_request_target','repository: Rhodan-lab/Atlas','curl ','wget '):
  if forbidden in workflow:errors.append(f'forbidden {forbidden}')
 if errors:return fail(sorted(set(errors)))
 print('Phase 29 post-merge record passed: exact candidate and PR pinned, two envelope schemas ready, zero envelopes received.');return 0
if __name__=='__main__':raise SystemExit(main())
