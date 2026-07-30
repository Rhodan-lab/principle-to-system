#!/usr/bin/env python3
"""Validate the immutable Phase 37 post-merge record and project-state transition."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent.parent
CANDIDATE=ROOT/"release/phase-37-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness.json"
POST=ROOT/"release/phase-37-postmerge.json"
REPORT=ROOT/"reports/phase-37-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness.md"
STATE=ROOT/"PROJECT_STATE.md"
WORKFLOW=ROOT/".github/workflows/validate-phase-37-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness.yml"
CANDIDATE_SHA="724a12243300d6c91cf60fef046f5ae40089c98867bba62bdd524e3684aec2ae"
POST_SHA="519c98afb8cd34f618c2e3c5421e0c1be2a0baa0c5ef836621910ce487c86795"
HEAD="b3b5cb7ce580b83b96e03dc91830c210aeb50ddd"
MERGE="16516cd5b67b480a572b949996e8ebceaa8d1acb"
NEXT="offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-candidate"


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
            errors.append(f"Phase 37 {label} missing")
    if errors:
        return errors
    if sha_file(CANDIDATE)!=CANDIDATE_SHA:
        errors.append("Phase 37 candidate digest drift")
    if sha_file(POST)!=POST_SHA:
        errors.append("Phase 37 postmerge digest drift")
    candidate,post=load(CANDIDATE),load(POST)
    if candidate.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-candidate" or candidate.get("next_gate")!=NEXT:
        errors.append("Phase 37 candidate gate drift")
    if post.get("contract")!="principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-finalization/0.1":
        errors.append("Phase 37 finalization contract drift")
    if post.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-validated" or post.get("next_gate")!=NEXT:
        errors.append("Phase 37 final state drift")
    if post.get("candidate_record")!={"path":"release/phase-37-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness.json","sha256":CANDIDATE_SHA}:
        errors.append("Phase 37 candidate binding drift")
    if post.get("principia")!={"candidate_head_commit":HEAD,"merge_commit":MERGE,"pull_request":65,"repository":"Rhodan-lab/principle-to-system"}:
        errors.append("Phase 37 merge provenance drift")
    if post.get("validation")!={"applicable_workflows":31,"candidate_head_commit":HEAD,"status":"success"}:
        errors.append("Phase 37 workflow provenance drift")
    if post.get("result")!=candidate.get("result"):
        errors.append("Phase 37 result binding drift")
    if post.get("authority")!=candidate.get("authority") or post.get("live") is not False or post.get("real_authorization_claimed") is not False:
        errors.append("Phase 37 authority drift")
    state=STATE.read_text()
    required=(
        "**Phase 37 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Readiness merged and validated through PR #65.**",
        "Phase 37 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-validated**",
        "| 37 | Offline consequence-plan review-response intake envelope validation execution authorization decision readiness | Merged and validated through PR #65 |",
        f"Phase 37 exact candidate validation passed at `{HEAD}`",
        f"PR #65 was merged into `main` at commit `{MERGE}`",
        "Historical Phase 36 finalization marker: **Phase 36 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Readiness Assurance merged and validated through PR #63.**",
        "Historical Phase 37 candidate marker: `exact-head validation pending`",
        "Historical Phase 37 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-candidate`",
        "Historical Phase 38 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-candidate`",
        "Atlas remains unchanged by Principia Phase 37",
        "## Phase 37 result — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Readiness",
        CANDIDATE_SHA,HEAD,MERGE,"all 31 applicable workflows","138 deterministic scenarios","137 mutations",
    )
    for marker in required:
        if marker not in state:
            errors.append(f"Phase 37 project-state marker missing: {marker}")
    if "Principia and Atlas remain separate repositories with separate lifecycle authority." not in state:
        errors.append("Repository authority separation lost")
    report=REPORT.read_text()
    for marker in (
        "# Phase 37 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Readiness",
        "State: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-validated`",
        f"Candidate SHA-256: `{CANDIDATE_SHA}`",f"Exact tested head: `{HEAD}`","Candidate PR: `#65`",
        f"Candidate merge: `{MERGE}`","Applicable candidate workflows: `31`",f"Post-merge SHA-256: `{POST_SHA}`",
        f"Next gate: `{NEXT}`","138 deterministic scenarios","137 mutations","No authorization-decision candidate was created",
    ):
        if marker not in report:
            errors.append(f"Phase 37 report marker missing: {marker}")
    workflow=WORKFLOW.read_text()
    if "contents: read" not in workflow:
        errors.append("Phase 37 workflow is not read-only")
    if "validate_phase37_postmerge_record.py" not in workflow:
        errors.append("Phase 37 workflow does not validate postmerge record")
    for token in ("contents: write","pull_request_target","git push","git commit","repository: Rhodan-lab/Atlas"):
        if token in workflow:
            errors.append(f"Phase 37 workflow forbidden token: {token}")
    return errors


def main()->int:
    errors=validate()
    if errors:
        print("Phase 37 post-merge record errors:",file=sys.stderr)
        for error in errors:
            print(f"- {error}",file=sys.stderr)
        return 1
    print(f"Phase 37 post-merge record passed: candidate={CANDIDATE_SHA}, postmerge={POST_SHA}, head={HEAD}, merge={MERGE}, workflows=31.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
