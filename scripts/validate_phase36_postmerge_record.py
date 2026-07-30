#!/usr/bin/env python3
"""Validate the immutable Phase 36 post-merge record and project-state transition."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent.parent
CANDIDATE=ROOT/"release/phase-36-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance.json"
POST=ROOT/"release/phase-36-postmerge.json"
REPORT=ROOT/"reports/phase-36-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance.md"
STATE=ROOT/"PROJECT_STATE.md"
WORKFLOW=ROOT/".github/workflows/validate-phase-36-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance.yml"
CANDIDATE_SHA="c90abcedeffcc66ff1d1e1d615e03cc5e002a76177d3ab8a0754543c4ad1677e"
POST_SHA="79b689ad032d29c21e620525cdea665545f0ee9e2e4f633b708a78240b252f52"
HEAD="b9443786203f1fce54bef7a4461d659413998fc7"
MERGE="2c0f3bc5d01e8f36782108a14a8611e38c4d5ca6"
NEXT="offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-candidate"

def sha_file(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path:Path)->dict[str,Any]:
    value=json.loads(path.read_text())
    if not isinstance(value,dict):
        raise ValueError(path)
    return value

def validate()->list[str]:
    errors=[]
    for path,label in ((CANDIDATE,"candidate"),(POST,"postmerge"),(REPORT,"report"),(STATE,"project state"),(WORKFLOW,"workflow")):
        if not path.is_file():
            errors.append(f"Phase 36 {label} missing")
    if errors:
        return errors
    if sha_file(CANDIDATE)!=CANDIDATE_SHA:
        errors.append("Phase 36 candidate digest drift")
    if sha_file(POST)!=POST_SHA:
        errors.append("Phase 36 postmerge digest drift")
    candidate,post=load(CANDIDATE),load(POST)
    if candidate.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-candidate":
        errors.append("Phase 36 candidate state drift")
    if candidate.get("next_gate")!=NEXT:
        errors.append("Phase 36 candidate gate drift")
    if post.get("contract")!="principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-finalization/0.1":
        errors.append("Phase 36 finalization contract drift")
    if post.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-validated" or post.get("next_gate")!=NEXT:
        errors.append("Phase 36 final state drift")
    expected_record={"path":"release/phase-36-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance.json","sha256":CANDIDATE_SHA}
    if post.get("candidate_record")!=expected_record:
        errors.append("Phase 36 candidate binding drift")
    expected_pr={"candidate_head_commit":HEAD,"merge_commit":MERGE,"pull_request":63,"repository":"Rhodan-lab/principle-to-system"}
    if post.get("principia")!=expected_pr:
        errors.append("Phase 36 merge provenance drift")
    expected_validation={"applicable_workflows":30,"candidate_head_commit":HEAD,"status":"success"}
    if post.get("validation")!=expected_validation:
        errors.append("Phase 36 workflow provenance drift")
    if post.get("result")!=candidate.get("result"):
        errors.append("Phase 36 result binding drift")
    if post.get("authority")!=candidate.get("authority") or post.get("live") is not False or post.get("real_authorization_claimed") is not False:
        errors.append("Phase 36 authority drift")
    state=STATE.read_text()
    required=(
        "**Phase 36 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Readiness Assurance merged and validated through PR #63.**",
        "Phase 36 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-validated**",
        "| 36 | Offline consequence-plan review-response intake envelope validation execution authorization readiness assurance | Merged and validated through PR #63 |",
        f"Phase 36 exact candidate validation passed at `{HEAD}`",
        f"PR #63 was merged into `main` at commit `{MERGE}`",
        "Historical Phase 35 finalization marker: **Phase 35 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Readiness merged and validated through PR #61.**",
        "Historical Phase 36 candidate marker: `exact-head validation pending`",
        "Historical Phase 36 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-candidate`",
        "Atlas remains unchanged by Principia Phase 36",
        "## Phase 36 result — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Readiness Assurance",
        CANDIDATE_SHA,HEAD,MERGE,"all 30 applicable workflows","132 deterministic scenarios","131 mutations",f"Next gate: **{NEXT}**",
    )
    for marker in required:
        if marker not in state:
            errors.append(f"Phase 36 project-state marker missing: {marker}")
    if "Principia and Atlas remain separate repositories with separate lifecycle authority." not in state:
        errors.append("Repository authority separation lost")
    report=REPORT.read_text()
    for marker in (
        "# Phase 36 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Readiness Assurance",
        "State: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-validated`",
        f"Candidate SHA-256: `{CANDIDATE_SHA}`",f"Exact tested head: `{HEAD}`","Candidate PR: `#63`",
        f"Candidate merge: `{MERGE}`","Applicable candidate workflows: `30`",f"Post-merge SHA-256: `{POST_SHA}`",
        f"Next gate: `{NEXT}`","132 deterministic scenarios","131 rejected mutations",
        "No authorization candidate was created",
    ):
        if marker not in report:
            errors.append(f"Phase 36 report marker missing: {marker}")
    workflow=WORKFLOW.read_text()
    if "contents: read" not in workflow:
        errors.append("Phase 36 workflow is not read-only")
    if "validate_phase36_postmerge_record.py" not in workflow:
        errors.append("Phase 36 workflow does not validate postmerge record")
    for token in ("contents: write","pull_request_target","git push","git commit","repository: Rhodan-lab/Atlas"):
        if token in workflow:
            errors.append(f"Phase 36 workflow forbidden token: {token}")
    return errors

def main()->int:
    errors=validate()
    if errors:
        print("Phase 36 post-merge record errors:",file=sys.stderr)
        for error in errors:
            print(f"- {error}",file=sys.stderr)
        return 1
    print(f"Phase 36 post-merge record passed: candidate={CANDIDATE_SHA}, postmerge={POST_SHA}, head={HEAD}, merge={MERGE}, workflows=30.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
