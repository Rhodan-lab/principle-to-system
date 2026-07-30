#!/usr/bin/env python3
"""Validate deterministic Phase 39 authorization-decision candidate-boundary readiness evidence."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from typing import Any
import generate_phase39_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_boundary_readiness as gen

ROOT=Path(__file__).resolve().parent.parent
CANDIDATE=ROOT/'release/phase-39-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness.json'
EXPECTED_SHA='e15063165a54ced8bbae95f4dcea9c9ff92c540135d67d3a8b10791dbc771c40'

def load(path:Path)->dict[str,Any]:
    v=json.loads(path.read_text())
    if not isinstance(v,dict): raise ValueError(path)
    return v

def validate_manifest(value:dict[str,Any])->list[str]:
    errors=[]
    expected=gen.build_manifest(gen.load(gen.SOURCE),gen.load(gen.SOURCE_POST))
    if value!=expected: errors.append('Phase 39 deterministic structure drift')
    if value.get('contract')!='principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness/0.1': errors.append('contract drift')
    if value.get('state')!=gen.STATE or value.get('next_gate')!=gen.NEXT_GATE or value.get('decision')!=gen.DECISION: errors.append('state or gate drift')
    if value.get('live') is not False or value.get('real_authorization_claimed') is not False: errors.append('live or authorization claim drift')
    authority=value.get('authority',{})
    for key in ('atlas_call_permitted','authorization_decision_candidate_creation_permitted','authorization_decision_recording_permitted','reviewer_contact_permitted','repository_mutation'):
        if authority.get(key) is not False: errors.append(f'authority drift: {key}')
    records=value.get('boundary_readiness_records',[])
    if len(records)!=2: errors.append('boundary record count drift')
    for i,r in enumerate(records,1):
        if r.get('sequence')!=i or r.get('boundary_check_count')!=len(gen.CHECK_NAMES) or r.get('failed_boundary_check_count')!=0: errors.append(f'boundary check drift: {i}')
        if set(r.get('boundary_checks',{}))!=set(gen.CHECK_NAMES) or not all(r.get('boundary_checks',{}).values()): errors.append(f'boundary invariant drift: {i}')
        if any(v is not None for v in r.get('candidate_template',{}).values()): errors.append(f'candidate template populated: {i}')
        for key in ('authorization_decision_candidate_created','authorization_decision_record_created','authorization_decision_recorded','authorization_granted','authorization_token_issued','execution_ticket_issued','execution_run_created','response_envelope_received','reviewer_identity_present','approval_received','approval_evidence_recorded','status_change','validation_result_recorded'):
            if r.get(key) is not False: errors.append(f'zero-effect drift: {i}:{key}')
        if r.get('human_gate_satisfied_count')!=0 or r.get('human_gate_pending_count')!=4: errors.append(f'human gate drift: {i}')
    pol=value.get('boundary_policy',{})
    if len(pol.get('boundary_stages',[]))!=12 or any(s.get('state')!='inactive' for s in pol.get('boundary_stages',[])): errors.append('boundary stage drift')
    if len(pol.get('boundary_requirements',[]))!=30 or any(r.get('state')!='unevaluated' for r in pol.get('boundary_requirements',[])): errors.append('boundary requirement drift')
    if pol.get('boundary_policy_sha256')!=gen.sha_value({k:v for k,v in pol.items() if k!='boundary_policy_sha256'}): errors.append('boundary policy digest drift')
    result=value.get('result',{})
    expected_counts={'boundary_policy_count':1,'boundary_profile_count':2,'candidate_boundary_readiness_record_count':2,'boundary_stage_count':24,'boundary_requirement_count':60,'boundary_requirement_evaluated_count':0,'candidate_template_count':2,'candidate_template_field_count':36,'boundary_check_count':154,'failed_boundary_check_count':0,'audit_event_recorded_count':0,'authorization_decision_candidate_created_count':0,'authorization_decision_recorded_count':0,'authorization_granted_count':0,'authorization_token_issued_count':0,'execution_run_count':0,'response_envelope_received_count':0,'reviewer_contact_count':0,'status_change_count':0}
    for k,v in expected_counts.items():
        if result.get(k)!=v: errors.append(f'result drift: {k}')
    ledger=value.get('ledger',{})
    entries=ledger.get('entries',[]); previous=None
    if len(entries)!=2: errors.append('ledger count drift')
    for i,item in enumerate(entries,1):
        entry=item.get('entry',{})
        if entry.get('sequence')!=i or entry.get('previous_entry_sha256')!=previous: errors.append(f'ledger chain drift: {i}')
        if item.get('entry_sha256')!=gen.sha_value(entry): errors.append(f'ledger digest drift: {i}')
        previous=item.get('entry_sha256')
    if ledger.get('head_sequence')!=2 or ledger.get('head_sha256')!=previous: errors.append('ledger head drift')
    rec=value.get('recovery',{})
    if rec.get('accepted_count')!=1 or rec.get('rejected_count')!=180 or rec.get('scenario_count')!=181: errors.append('recovery count drift')
    return errors

def validate()->list[str]:
    if not CANDIDATE.is_file(): return ['Phase 39 candidate missing']
    errors=[]
    payload=CANDIDATE.read_bytes()
    if hashlib.sha256(payload).hexdigest()!=EXPECTED_SHA: errors.append('Phase 39 candidate digest drift')
    value=load(CANDIDATE)
    if payload!=gen.render(value): errors.append('Phase 39 candidate is not canonical JSON')
    errors.extend(validate_manifest(value))
    return errors

def main()->int:
    errors=validate()
    if errors:
        print('Phase 39 validation errors:',file=sys.stderr)
        for e in errors: print(f'- {e}',file=sys.stderr)
        return 1
    print(f'Phase 39 candidate passed: sha256={EXPECTED_SHA}, records=2, checks=154, scenarios=181.')
    return 0
if __name__=='__main__':raise SystemExit(main())
