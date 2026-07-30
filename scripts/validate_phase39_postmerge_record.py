#!/usr/bin/env python3
"""Validate the immutable Phase 39 post-merge record and project-state transition."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent.parent
CANDIDATE=ROOT/'release/phase-39-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness.json'
POST=ROOT/'release/phase-39-postmerge.json'
REPORT=ROOT/'reports/phase-39-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness.md'
STATE=ROOT/'PROJECT_STATE.md'
WORKFLOW=ROOT/'.github/workflows/validate-phase-39-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness.yml'
CANDIDATE_SHA='e15063165a54ced8bbae95f4dcea9c9ff92c540135d67d3a8b10791dbc771c40'
POST_SHA='17cab6bc36cffeb475065fe92116486fb47e8ac813a643205d0cbd18e774fea2'
HEAD='c9bf3c5a0bdab6f6204d8fa8dd571f8d82b01896'
MERGE='e2b81e9ac1ff5385ab054392bb0b33f5c3907b55'
NEXT='offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance-candidate'

def sha_file(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:
    v=json.loads(p.read_text());
    if not isinstance(v,dict): raise ValueError(p)
    return v

def validate()->list[str]:
    errors=[]
    for p,label in ((CANDIDATE,'candidate'),(POST,'postmerge'),(REPORT,'report'),(STATE,'project state'),(WORKFLOW,'workflow')):
        if not p.is_file(): errors.append(f'Phase 39 {label} missing')
    if errors:return errors
    if sha_file(CANDIDATE)!=CANDIDATE_SHA: errors.append('Phase 39 candidate digest drift')
    if sha_file(POST)!=POST_SHA: errors.append('Phase 39 postmerge digest drift')
    c,p=load(CANDIDATE),load(POST)
    if c.get('state')!='offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-candidate': errors.append('Phase 39 candidate state drift')
    if c.get('next_gate')!=NEXT: errors.append('Phase 39 candidate gate drift')
    if p.get('contract')!='principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-finalization/0.1': errors.append('Phase 39 finalization contract drift')
    if p.get('state')!='offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-validated' or p.get('next_gate')!=NEXT: errors.append('Phase 39 final state drift')
    if p.get('candidate_record')!={'path':'release/phase-39-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness.json','sha256':CANDIDATE_SHA}: errors.append('Phase 39 candidate binding drift')
    if p.get('principia')!={'candidate_head_commit':HEAD,'merge_commit':MERGE,'pull_request':69,'repository':'Rhodan-lab/principle-to-system'}: errors.append('Phase 39 merge provenance drift')
    if p.get('validation')!={'applicable_workflows':33,'candidate_head_commit':HEAD,'status':'success'}: errors.append('Phase 39 workflow provenance drift')
    if p.get('result')!=c.get('result'): errors.append('Phase 39 result binding drift')
    if p.get('authority')!=c.get('authority') or p.get('live') is not False or p.get('real_authorization_claimed') is not False: errors.append('Phase 39 authority drift')
    state=STATE.read_text()
    required=(
      '**Phase 39 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Boundary Readiness merged and validated through PR #69.**',
      'Phase 39 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-validated**',
      '| 39 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate boundary readiness | Merged and validated through PR #69 |',
      f'Phase 39 exact candidate validation passed at `{HEAD}`',f'PR #69 was merged into `main` at commit `{MERGE}`',
      'Historical Phase 38 finalization marker: **Phase 38 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Readiness Assurance merged and validated through PR #67.**',
      'Historical Phase 39 candidate marker: `exact-head validation pending`',
      'Historical Phase 39 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-candidate`',
      'Atlas remains unchanged by Principia Phase 39','## Phase 39 result — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Boundary Readiness',
      CANDIDATE_SHA,HEAD,MERGE,'all 33 applicable workflows','181 deterministic scenarios','180 mutations',
      'Historical Phase 40 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance-candidate`')
    for m in required:
        if m not in state: errors.append(f'Phase 39 project-state marker missing: {m}')
    if 'Principia and Atlas remain separate repositories with separate lifecycle authority.' not in state: errors.append('Repository authority separation lost')
    report=REPORT.read_text()
    for m in ('# Phase 39 — Offline Authorization-Decision Candidate Boundary Readiness',
      'State: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-validated`',
      f'Candidate SHA-256: `{CANDIDATE_SHA}`',f'Exact tested head: `{HEAD}`','Candidate PR: `#69`',f'Candidate merge: `{MERGE}`',
      'Applicable candidate workflows: `33`',f'Post-merge SHA-256: `{POST_SHA}`',f'Next gate: `{NEXT}`','181 deterministic scenarios','180 rejected mutations','No authorization-decision candidate was created'):
        if m not in report: errors.append(f'Phase 39 report marker missing: {m}')
    workflow=WORKFLOW.read_text()
    if 'contents: read' not in workflow: errors.append('Phase 39 workflow is not read-only')
    if 'validate_phase39_postmerge_record.py' not in workflow: errors.append('Phase 39 workflow does not validate postmerge record')
    for token in ('contents: write','pull_request_target','git push','git commit','repository: Rhodan-lab/Atlas'):
        if token in workflow: errors.append(f'Phase 39 workflow forbidden token: {token}')
    return errors

def main()->int:
    e=validate()
    if e:
        print('Phase 39 post-merge record errors:',file=sys.stderr)
        for x in e: print(f'- {x}',file=sys.stderr)
        return 1
    print(f'Phase 39 post-merge record passed: candidate={CANDIDATE_SHA}, postmerge={POST_SHA}, head={HEAD}, merge={MERGE}, workflows=33.')
    return 0
if __name__=='__main__':raise SystemExit(main())
