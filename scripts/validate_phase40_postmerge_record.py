#!/usr/bin/env python3
"""Validate immutable Phase 40 finalization provenance and state markers."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "release/phase-40-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance.json"
POST = ROOT / "release/phase-40-postmerge.json"
REPORT = ROOT / "reports/phase-40-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance.md"
STATE = ROOT / "PROJECT_STATE.md"
WORKFLOW = ROOT / ".github/workflows/validate-phase-40-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance.yml"
CANDIDATE_SHA = "a935dbfcc1758b0aab68fb358968801d2b380690a9ebcd6efdc12416d2ef58c8"
POST_SHA = "2beeadfd27f823d0afc7f7dfd434e8dad9157488b2d1902b78e7efa26a5e9e20"
HEAD = "89b5ad5efb559bcf5c5f1b6c61621d97ca32c8e2"
MERGE = "893c00336ddca21c5b5c36d423f6666c0cfb3531"
NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-candidate"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate():
    errors=[]
    for p,n in ((CANDIDATE,"candidate"),(POST,"postmerge"),(REPORT,"report"),(STATE,"state"),(WORKFLOW,"workflow")):
        if not p.is_file(): errors.append(f"Phase 40 {n} missing")
    if errors: return errors
    if sha(CANDIDATE)!=CANDIDATE_SHA: errors.append("Phase 40 candidate digest drift")
    if sha(POST)!=POST_SHA: errors.append("Phase 40 postmerge digest drift")
    c,p=load(CANDIDATE),load(POST)
    if p.get("candidate_record")!={"path":CANDIDATE.relative_to(ROOT).as_posix(),"sha256":CANDIDATE_SHA}: errors.append("candidate binding drift")
    if p.get("principia")!={"candidate_head_commit":HEAD,"merge_commit":MERGE,"pull_request":71,"repository":"Rhodan-lab/principle-to-system"}: errors.append("merge provenance drift")
    if p.get("validation")!={"applicable_workflows":34,"candidate_head_commit":HEAD,"status":"success"}: errors.append("workflow provenance drift")
    if p.get("result")!=c.get("result") or p.get("authority")!=c.get("authority"): errors.append("candidate finalization binding drift")
    if p.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance-validated" or p.get("next_gate")!=NEXT: errors.append("final state drift")
    state=STATE.read_text(encoding="utf-8")
    for marker in (
        "**Phase 40 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Boundary Readiness Assurance merged and validated through PR #71.**",
        "Phase 40 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance-validated**",
        "| 40 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate boundary readiness assurance | Merged and validated through PR #71 |",
        f"Phase 40 exact candidate validation passed at `{HEAD}`", f"PR #71 was merged into `main` at commit `{MERGE}`",
        "Historical Phase 39 finalization marker:", "Historical Phase 40 target marker:", "Atlas remains unchanged by Principia Phase 40",
        CANDIDATE_SHA, "all 34 applicable workflows", "210 deterministic scenarios", "209 mutations", f"Next gate: **{NEXT}**",
    ):
        if marker not in state: errors.append(f"state marker missing: {marker}")
    report=REPORT.read_text(encoding="utf-8")
    for marker in ("State: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance-validated`",f"Candidate SHA-256: `{CANDIDATE_SHA}`",f"Post-merge SHA-256: `{POST_SHA}`","Applicable candidate workflows: `34`",f"Next gate: `{NEXT}`"):
        if marker not in report: errors.append(f"report marker missing: {marker}")
    workflow=WORKFLOW.read_text(encoding="utf-8")
    if "contents: read" not in workflow or "validate_phase40_postmerge_record.py" not in workflow: errors.append("workflow finalization integration drift")
    for token in ("contents: write","pull_request_target","git push","git commit","repository: Rhodan-lab/Atlas"):
        if token in workflow: errors.append(f"forbidden workflow token: {token}")
    return errors


def main():
    errors=validate()
    if errors:
        print("Phase 40 post-merge record errors:",file=sys.stderr)
        for e in errors: print(f"- {e}",file=sys.stderr)
        return 1
    print(f"Phase 40 post-merge record passed: candidate={CANDIDATE_SHA}, postmerge={POST_SHA}, head={HEAD}, merge={MERGE}, workflows=34.")
    return 0

if __name__=="__main__": raise SystemExit(main())
