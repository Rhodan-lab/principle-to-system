#!/usr/bin/env python3
"""Validate the immutable Phase 33 post-merge record and project-state transition."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent.parent
CANDIDATE=ROOT/"release/phase-33-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness.json"
POST=ROOT/"release/phase-33-postmerge.json"
REPORT=ROOT/"reports/phase-33-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness.md"
STATE=ROOT/"PROJECT_STATE.md"
WORKFLOW=ROOT/".github/workflows/validate-phase-33-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness.yml"
CANDIDATE_SHA="6e0eee781b4a8b76baf1d29e8504fac0686cf306d052d69bd2e3966071562284"
POST_SHA="666f6171fb1ef7c0a2e9e1b9fd4c8d521b3fcc6c12e945819b1d98f04ca50886"
HEAD="8cd3580a2e12d6bd8d852b1a76f56850cc0c8a89"
MERGE="d05db33982e0001c9ebc636043dc0cc64592c42d"
NEXT="offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance-candidate"
def sha_file(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path:Path)->dict[str,Any]:
    value=json.loads(path.read_text())
    if not isinstance(value,dict): raise ValueError(path)
    return value
def validate()->list[str]:
    errors=[]
    for path,label in ((CANDIDATE,"candidate"),(POST,"postmerge"),(REPORT,"report"),(STATE,"project state"),(WORKFLOW,"workflow")):
        if not path.is_file(): errors.append(f"Phase 33 {label} missing")
    if errors: return errors
    if sha_file(CANDIDATE)!=CANDIDATE_SHA: errors.append("Phase 33 candidate digest drift")
    if sha_file(POST)!=POST_SHA: errors.append("Phase 33 postmerge digest drift")
    candidate,post=load(CANDIDATE),load(POST)
    if candidate.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-candidate" or candidate.get("next_gate")!=NEXT: errors.append("Phase 33 candidate gate drift")
    if post.get("contract")!="principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-finalization/0.1": errors.append("Phase 33 finalization contract drift")
    if post.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-validated" or post.get("next_gate")!=NEXT: errors.append("Phase 33 final state drift")
    if post.get("candidate_record")!={"path":"release/phase-33-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness.json","sha256":CANDIDATE_SHA}: errors.append("Phase 33 candidate binding drift")
    if post.get("principia")!={"candidate_head_commit":HEAD,"merge_commit":MERGE,"pull_request":57,"repository":"Rhodan-lab/principle-to-system"}: errors.append("Phase 33 merge provenance drift")
    if post.get("validation")!={"applicable_workflows":27,"candidate_head_commit":HEAD,"status":"success"}: errors.append("Phase 33 workflow provenance drift")
    if post.get("result")!=candidate.get("result"): errors.append("Phase 33 result binding drift")
    if post.get("authority")!=candidate.get("authority") or post.get("live") is not False or post.get("real_authorization_claimed") is not False: errors.append("Phase 33 authority drift")
    state=STATE.read_text()
    required=("Phase 33 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-validated**","| 33 | Offline consequence-plan review-response intake envelope validation execution readiness | Merged and validated through PR #57 |",f"Phase 33 exact candidate validation passed at `{HEAD}`",f"PR #57 was merged into `main` at commit `{MERGE}`","Historical Phase 32 finalization marker: **Phase 32 — Offline Consequence-Plan Review-Response Intake Envelope Validation Readiness Assurance merged and validated through PR #55.**","Historical Phase 33 candidate marker: `exact-head validation pending`","Historical Phase 33 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-candidate`","Atlas remains unchanged by Principia Phase 33","## Phase 33 result — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Readiness",CANDIDATE_SHA,HEAD,MERGE,"all 27 applicable workflows","119 deterministic scenarios","118 mutations")
    for marker in required:
        if marker not in state: errors.append(f"Phase 33 project-state marker missing: {marker}")
    current=f"Next gate: **{NEXT}**"
    historical=f"Historical Phase 34 target marker: `{NEXT}`"
    if current not in state and historical not in state: errors.append(f"Phase 33 project-state gate marker missing: {NEXT}")
    if "**Phase 32 — Offline Consequence-Plan Review-Response Intake Envelope Validation Readiness Assurance merged and validated through PR #55.**" not in state: errors.append("Phase 32 historical heading lost")
    if "Principia and Atlas remain separate repositories with separate lifecycle authority." not in state: errors.append("Repository authority separation lost")
    report=REPORT.read_text()
    for marker in ("# Phase 33 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Readiness","State: `offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-validated`",f"Candidate SHA-256: `{CANDIDATE_SHA}`",f"Exact tested head: `{HEAD}`","Candidate PR: `#57`",f"Candidate merge: `{MERGE}`","Applicable candidate workflows: `27`",f"Next gate: `{NEXT}`","119 deterministic scenarios","118 rejected mutations"):
        if marker not in report: errors.append(f"Phase 33 report marker missing: {marker}")
    workflow=WORKFLOW.read_text()
    if "contents: read" not in workflow: errors.append("Phase 33 workflow is not read-only")
    if "validate_phase33_postmerge_record.py" not in workflow: errors.append("Phase 33 workflow does not validate postmerge record")
    for token in ("contents: write","pull_request_target","git push","git commit","repository: Rhodan-lab/Atlas"):
        if token in workflow: errors.append(f"Phase 33 workflow forbidden token: {token}")
    return errors
def main()->int:
    errors=validate()
    if errors:
        print("Phase 33 post-merge record errors:",file=sys.stderr)
        for error in errors: print(f"- {error}",file=sys.stderr)
        return 1
    print(f"Phase 33 post-merge record passed: candidate={CANDIDATE_SHA}, postmerge={POST_SHA}, head={HEAD}, merge={MERGE}, workflows=27.")
    return 0
if __name__=="__main__": raise SystemExit(main())
