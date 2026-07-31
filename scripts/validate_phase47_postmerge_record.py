#!/usr/bin/env python3
# Validate immutable Phase 47 finalization provenance and state markers.
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "release/phase-47-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness.json"
POST = ROOT / "release/phase-47-postmerge.json"
REPORT = ROOT / "reports/phase-47-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness.md"
STATE = ROOT / "PROJECT_STATE.md"
WORKFLOW = ROOT / ".github/workflows/validate-phase-47-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness.yml"
CANDIDATE_SHA = "31b57486ca590cd066642981e640c21cc306869f99241d0fa81013d681df5065"
POST_SHA = "7048a8235b379991f3e618a3390cbd978a016e989e4dcb558c518dc9a84a365c"
HEAD = "bc9c8b5e2431db5105da9253715ced6c08c5914a"
MERGE = "384b5a868ed63e33dc118d3311ecf7241dc6cb93"
MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness"
FINAL_STATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-validated"
NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance-candidate"
WORKFLOWS = 40

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def validate():
    errors = []
    for path, name in ((CANDIDATE, "candidate"), (POST, "postmerge"), (REPORT, "report"), (STATE, "state"), (WORKFLOW, "workflow")):
        if not path.is_file():
            errors.append("Phase 47 %s missing" % name)
    if errors:
        return errors
    if sha(CANDIDATE) != CANDIDATE_SHA:
        errors.append("Phase 47 candidate digest drift")
    if sha(POST) != POST_SHA:
        errors.append("Phase 47 postmerge digest drift")
    candidate, post = load(CANDIDATE), load(POST)
    if post.get("candidate_record") != {"path": CANDIDATE.relative_to(ROOT).as_posix(), "sha256": CANDIDATE_SHA}:
        errors.append("candidate binding drift")
    if post.get("principia") != {"candidate_head_commit": HEAD, "merge_commit": MERGE, "pull_request": 86, "repository": "Rhodan-lab/principle-to-system"}:
        errors.append("merge provenance drift")
    if post.get("validation") != {"applicable_workflows": WORKFLOWS, "candidate_head_commit": HEAD, "status": "success"}:
        errors.append("workflow provenance drift")
    if post.get("result") != candidate.get("result") or post.get("authority") != candidate.get("authority"):
        errors.append("candidate finalization binding drift")
    if post.get("state") != FINAL_STATE or post.get("next_gate") != NEXT:
        errors.append("final state drift")
    if post.get("decision") != candidate.get("decision") or post.get("live") is not False or post.get("real_authorization_claimed") is not False:
        errors.append("final decision or frozen-state drift")
    state_text = STATE.read_text(encoding="utf-8")
    for marker in (
        "**Phase 47 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Population Execution Readiness merged and validated through PR #86.**",
        "Phase 47 state: **%s**" % FINAL_STATE,
        "| 47 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate population execution readiness | Merged and validated through PR #86 |",
        "Phase 47 exact candidate validation passed at `%s`" % HEAD,
        "PR #86 was merged into `main` at commit `%s`" % MERGE,
        "Historical Phase 46 finalization marker:",
        "Atlas remains unchanged by Principia Phase 47",
        CANDIDATE_SHA, POST_SHA, "all 40 applicable workflows", "224 deterministic scenarios", "223 mutations",
    ):
        if marker not in state_text:
            errors.append("state marker missing: %s" % marker)
    if "## Next phase" not in state_text:
        errors.append("current next-phase section missing")
    else:
        section = state_text.rsplit("## Next phase", 1)[1]
        if "Next gate: **%s**." % NEXT not in section:
            errors.append("current Phase 48 population-execution-readiness-assurance gate missing")
        if "Next gate: **%s-candidate**." % MODE in section:
            errors.append("historical Phase 47 candidate gate remains current")
    report_text = REPORT.read_text(encoding="utf-8")
    for marker in (
        "State: `%s`" % FINAL_STATE,
        "Phase 47 candidate SHA-256: `%s`" % CANDIDATE_SHA,
        "Phase 47 post-merge SHA-256: `%s`" % POST_SHA,
        "Phase 47 applicable candidate workflows: `40`",
        "Next gate: `%s`" % NEXT,
    ):
        if marker not in report_text:
            errors.append("report marker missing: %s" % marker)
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    if "contents: read" not in workflow_text or "validate_phase47_postmerge_record.py" not in workflow_text:
        errors.append("workflow finalization integration drift")
    for token in ("contents: write", "pull_request_target", "git push", "git commit", "repository: Rhodan-lab/Atlas"):
        if token in workflow_text:
            errors.append("forbidden workflow token: %s" % token)
    return errors

def main():
    errors = validate()
    if errors:
        print("Phase 47 post-merge record errors:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1
    print("Phase 47 post-merge record passed: candidate=%s, postmerge=%s, head=%s, merge=%s, workflows=%s." % (CANDIDATE_SHA, POST_SHA, HEAD, MERGE, WORKFLOWS))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
