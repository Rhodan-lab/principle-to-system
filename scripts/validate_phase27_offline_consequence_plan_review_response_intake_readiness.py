#!/usr/bin/env python3
"""Validate Phase 27 response-intake readiness."""
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Mapping
import generate_phase27_offline_consequence_plan_review_response_intake_readiness as gen
ROOT=Path(__file__).resolve().parent.parent
REPORT=ROOT/'reports/phase-27-offline-consequence-plan-review-response-intake-readiness.md'
WORKFLOW=ROOT/'.github/workflows/validate-phase-27-offline-consequence-plan-review-response-intake-readiness.yml'
def fail(errors:list[str])->int:
 print('Phase 27 validation errors:',file=sys.stderr);[print(f'- {e}',file=sys.stderr) for e in errors];return 1
def main()->int:
 errors=gen.verify_sources()
 for p in (gen.OUT,REPORT,WORKFLOW):
  if not p.is_file():errors.append(f'missing {p.relative_to(ROOT)}')
 if errors:return fail(errors)
 data=json.loads(gen.OUT.read_text());expected=gen.build()
 if data!=expected:errors.append('release record drift')
 if gen.OUT.read_text()!=gen.render(expected):errors.append('release bytes drift')
 records=data.get('intake_readiness_records',[])
 if len(records)!=2:errors.append('record count')
 for r in records:errors.extend(gen.validate_record(r))
 if data.get('result')!={'blank_question_slot_count':6,'human_gate_pending_count':8,'human_gate_satisfied_count':0,'intake_readiness_record_count':2,'packet_count':2,'question_slot_count':6,'required_field_count':30,'response_accepted_count':0,'response_intake_authorized_count':0,'response_quarantined_count':0,'response_received_count':0,'response_rejected_count':0,'response_schema_count':2,'response_schema_section_count':12,'response_template_count':2,'response_validated_count':0,'review_completed_count':0,'review_started_count':0,'reviewer_contact_count':0,'reviewer_identity_count':0,'status_change_count':0,'submitted_template_count':0,'real_authorization_claimed':False}:errors.append('summary drift')
 ledger=data.get('ledger',{});entries=ledger.get('entries',[]);prev=None
 for i,w in enumerate(entries,1):
  e=w.get('entry',{});d=gen.sha_doc(e)
  if e.get('sequence')!=i or e.get('previous_entry_sha256')!=prev or w.get('entry_sha256')!=d:errors.append('ledger drift')
  prev=d
 if ledger.get('head_sequence')!=2 or ledger.get('head_sha256')!=prev:errors.append('ledger head')
 checkpoint=data.get('checkpoint',{})
 if checkpoint.get('ledger_sha256')!=gen.sha_doc(ledger) or checkpoint.get('response_received_count')!=0 or checkpoint.get('review_started_count')!=0:errors.append('checkpoint drift')
 recovery=data.get('recovery',{})
 if recovery.get('scenario_count')!=77 or recovery.get('accepted_count')!=1 or recovery.get('rejected_count')!=76 or len(recovery.get('scenarios',[]))!=77:errors.append('recovery drift')
 authority=data.get('authority')
 if authority!=gen.AUTHORITY or any(authority.get(k) is not False for k in ('atlas_call_permitted','repository_mutation','response_intake_authorized','response_receipt_permitted','response_validation_authorized','review_execution_authorized','review_request_dispatch_authorized','reviewer_contact_permitted','external_network_required')):errors.append('authority drift')
 text=REPORT.read_text()
 for m in ('# Phase 27 — Offline Consequence-Plan Review-Response Intake Readiness Candidate','2 readiness records','6 blank question slots','8 pending human gates','77 deterministic scenarios','response_received_count: 0',gen.NEXT_GATE):
  if m not in text:errors.append(f'report marker {m}')
 wf=WORKFLOW.read_text()
 for m in ('contents: read','generate_phase27_offline_consequence_plan_review_response_intake_readiness.py --check','validate_phase27_offline_consequence_plan_review_response_intake_readiness.py','test_phase27_offline_consequence_plan_review_response_intake_readiness','validate_phase26_postmerge_record.py'):
  if m not in wf:errors.append(f'workflow marker {m}')
 for forbidden in ('contents: write','git push','git commit','pull_request_target','repository: Rhodan-lab/Atlas','curl ','wget '):
  if forbidden in wf:errors.append(f'forbidden {forbidden}')
 if errors:return fail(sorted(set(errors)))
 print('Phase 27 validated: two schemas ready, six response slots blank, eight human gates pending, zero responses received.');return 0
if __name__=='__main__':raise SystemExit(main())
