#!/usr/bin/env python3
"""Validate immutable Phase 48 finalization provenance and state markers."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "release/phase-48-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance.json"
POST = ROOT / "release/phase-48-postmerge.json"
REPORT = ROOT / "reports/phase-48-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance.md"
STATE = ROOT / "PROJECT_STATE.md"
WORKFLOW = ROOT / ".github/workflows/validate-phase-48-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance.yml"
CANDIDATE_SHA = "9bfebeca19a7ce8f15c2e377db773fea78a479e773735318ac1cfc4d97f3e628"
POST_SHA = "2acb658af81739e76369065743e13e83031a60c43ddcb75eb03fad5c1c7e2a82"
HEAD = "24b133e90195bbd8bec36f6952e3f782d481ae27"
MERGE = "cd89c6728f841c18c2a797d246c22c581454359e"
MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance"
FINAL_STATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance-validated"
NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-candidate"
CURRENT_NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-assurance-candidate"
WORKFLOWS = 41

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def validate():
    errors = []
    for path, name in ((CANDIDATE,"candidate"),(POST,"postmerge"),(REPORT,"report"),(STATE,"state"),(WORKFLOW,"workflow")):
        if not path.is_file(): errors.append("Phase 48 %s missing" % name)
    if errors: return errors
    if sha(CANDIDATE) != CANDIDATE_SHA: errors.append("Phase 48 candidate digest drift")
    if sha(POST) != POST_SHA: errors.append("Phase 48 postmerge digest drift")
    candidate, post = load(CANDIDATE), load(POST)
    if post.get("candidate_record") != {"path": CANDIDATE.relative_to(ROOT).as_posix(), "sha256": CANDIDATE_SHA}: errors.append("candidate binding drift")
    if post.get("principia") != {"candidate_head_commit": HEAD, "merge_commit": MERGE, "pull_request": 88, "repository": "Rhodan-lab/principle-to-system"}: errors.append("merge provenance drift")
    if post.get("validation") != {"applicable_workflows": WORKFLOWS, "candidate_head_commit": HEAD, "status": "success"}: errors.append("workflow provenance drift")
    if post.get("result") != candidate.get("result") or post.get("authority") != candidate.get("authority"): errors.append("candidate finalization binding drift")
    if post.get("state") != FINAL_STATE or post.get("next_gate") != NEXT: errors.append("final state drift")
    if post.get("decision") != candidate.get("decision") or post.get("live") is not False or post.get("real_authorization_claimed") is not False: errors.append("final decision or frozen-state drift")
    state_text = STATE.read_text(encoding="utf-8")
    for marker in (
        "**Phase 48 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Population Execution Readiness Assurance merged and validated through PR #88.**",
        "Phase 48 state: **%s**" % FINAL_STATE,
        "| 48 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate population execution readiness assurance | Merged and validated through PR #88 |",
        "Phase 48 exact candidate validation passed at `%s`" % HEAD,
        "PR #88 was merged into `main` at commit `%s`" % MERGE,
        "Historical Phase 47 finalization marker:",
        "Atlas remains unchanged by Principia Phase 48",
        CANDIDATE_SHA, POST_SHA, "all 41 applicable workflows", "280 deterministic scenarios", "279 mutations",
    ):
        if marker not in state_text: errors.append("state marker missing: %s" % marker)
    if "## Next phase" not in state_text: errors.append("current next-phase section missing")
    else:
        section = state_text.rsplit("## Next phase",1)[1]
        if "Next gate: **%s**." % CURRENT_NEXT not in section: errors.append("current Phase 50 population-execution-authorization-readiness-assurance gate missing")
        if "Next gate: **%s**." % (MODE + "-candidate") in section: errors.append("historical Phase 48 gate remains current")
    report_text = REPORT.read_text(encoding="utf-8")
    for marker in ("Phase 48 candidate SHA-256: `%s`" % CANDIDATE_SHA, "Next gate", NEXT):
        if marker not in report_text: errors.append("report marker missing: %s" % marker)
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    if "contents: read" not in workflow_text or "validate_phase48_postmerge_record.py" not in workflow_text: errors.append("workflow finalization integration drift")
    for token in ("contents: write","pull_request_target","git push","git commit","repository: Rhodan-lab/Atlas"):
        if token in workflow_text: errors.append("forbidden workflow token: %s" % token)
    return errors

def main():
    errors = validate()
    if errors:
        print("Phase 48 post-merge record errors:", file=sys.stderr)
        for error in errors: print("- %s" % error, file=sys.stderr)
        return 1
    print("Phase 48 post-merge record passed: candidate=%s, postmerge=%s, head=%s, merge=%s, workflows=%s." % (CANDIDATE_SHA, POST_SHA, HEAD, MERGE, WORKFLOWS))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
