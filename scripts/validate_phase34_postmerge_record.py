#!/usr/bin/env python3
"""Validate the immutable Phase 34 post-merge record and project-state transition."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent.parent
CANDIDATE=ROOT/"release/phase-34-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance.json"
POST=ROOT/"release/phase-34-postmerge.json"
REPORT=ROOT/"reports/phase-34-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance.md"
STATE=ROOT/"PROJECT_STATE.md"
WORKFLOW=ROOT/".github/workflows/validate-phase-34-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance.yml"
CANDIDATE_SHA="2ca9b454124b1fb42f91f09479d9aed1d0c54f9ef443f121caa3a7ee67823828"
POST_SHA="c23152786eb92b8abfdba51dba95ff332dc71a8500d15c4148036099c0d85e65"
HEAD="99be153a563c0c7dd3c395b90969f3fb2546e91b"
MERGE="3878ad9d8ccdb49b05f02c6fdcb89a01cd9f7646"
NEXT="offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-candidate"
def sha_file(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path:Path)->dict[str,Any]:
    value=json.loads(path.read_text())
    if not isinstance(value,dict): raise ValueError(path)
    return value
def validate()->list[str]:
    errors=[]
    for path,label in ((CANDIDATE,"candidate"),(POST,"postmerge"),(REPORT,"report"),(STATE,"project state"),(WORKFLOW,"workflow")):
        if not path.is_file(): errors.append(f"Phase 34 {label} missing")
    if errors: return errors
    if sha_file(CANDIDATE)!=CANDIDATE_SHA: errors.append("Phase 34 candidate digest drift")
    if sha_file(POST)!=POST_SHA: errors.append("Phase 34 postmerge digest drift")
    candidate,post=load(CANDIDATE),load(POST)
    if candidate.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance-candidate" or candidate.get("next_gate")!=NEXT: errors.append("Phase 34 candidate gate drift")
    if post.get("contract")!="principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance-finalization/0.1": errors.append("Phase 34 finalization contract drift")
    if post.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance-validated" or post.get("next_gate")!=NEXT: errors.append("Phase 34 final state drift")
    if post.get("candidate_record")!={"path":"release/phase-34-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance.json","sha256":CANDIDATE_SHA}: errors.append("Phase 34 candidate binding drift")
    if post.get("principia")!={"candidate_head_commit":HEAD,"merge_commit":MERGE,"pull_request":59,"repository":"Rhodan-lab/principle-to-system"}: errors.append("Phase 34 merge provenance drift")
    if post.get("validation")!={"applicable_workflows":28,"candidate_head_commit":HEAD,"status":"success"}: errors.append("Phase 34 workflow provenance drift")
    if post.get("result")!=candidate.get("result"): errors.append("Phase 34 result binding drift")
    if post.get("authority")!=candidate.get("authority") or post.get("live") is not False or post.get("real_authorization_claimed") is not False: errors.append("Phase 34 authority drift")
    state=STATE.read_text()
    required=(
      "**Phase 34 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Readiness Assurance merged and validated through PR #59.**",
      "Phase 34 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance-validated**",
      "| 34 | Offline consequence-plan review-response intake envelope validation execution readiness assurance | Merged and validated through PR #59 |",
      f"Phase 34 exact candidate validation passed at `{HEAD}`",
      f"PR #59 was merged into `main` at commit `{MERGE}`",
      "Historical Phase 33 finalization marker: **Phase 33 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Readiness merged and validated through PR #57.**",
      "Historical Phase 34 candidate marker: `exact-head validation pending`",
      "Historical Phase 34 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance-candidate`",
      "Atlas remains unchanged by Principia Phase 34",
      "## Phase 34 result — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Readiness Assurance",
      CANDIDATE_SHA,HEAD,MERGE,"all 28 applicable workflows","121 deterministic scenarios","120 mutations")
    for marker in required:
        if marker not in state: errors.append(f"Phase 34 project-state marker missing: {marker}")
    if f"Next gate: **{NEXT}**" not in state and f"Historical Phase 35 target marker: `{NEXT}`" not in state:
        errors.append("Phase 34 next-gate history marker missing")
    if "Principia and Atlas remain separate repositories with separate lifecycle authority." not in state: errors.append("Repository authority separation lost")
    report=REPORT.read_text()
    for marker in ("# Phase 34 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Readiness Assurance","State: `offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance-validated`",f"Candidate SHA-256: `{CANDIDATE_SHA}`",f"Exact tested head: `{HEAD}`","Candidate PR: `#59`",f"Candidate merge: `{MERGE}`","Applicable candidate workflows: `28`",f"Post-merge SHA-256: `{POST_SHA}`",f"Next gate: `{NEXT}`","121 deterministic scenarios","120 rejected mutations","No envelope was created or received"):
        if marker not in report: errors.append(f"Phase 34 report marker missing: {marker}")
    workflow=WORKFLOW.read_text()
    if "contents: read" not in workflow: errors.append("Phase 34 workflow is not read-only")
    if "validate_phase34_postmerge_record.py" not in workflow: errors.append("Phase 34 workflow does not validate postmerge record")
    for token in ("contents: write","pull_request_target","git push","git commit","repository: Rhodan-lab/Atlas"):
        if token in workflow: errors.append(f"Phase 34 workflow forbidden token: {token}")
    return errors
def main()->int:
    errors=validate()
    if errors:
        print("Phase 34 post-merge record errors:",file=sys.stderr)
        for error in errors: print(f"- {error}",file=sys.stderr)
        return 1
    print(f"Phase 34 post-merge record passed: candidate={CANDIDATE_SHA}, postmerge={POST_SHA}, head={HEAD}, merge={MERGE}, workflows=28.")
    return 0
if __name__=="__main__": raise SystemExit(main())
