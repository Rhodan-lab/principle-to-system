#!/usr/bin/env python3
"""Validate immutable Phase 49 finalization provenance and state markers."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "release/phase-49-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness.json"
POST = ROOT / "release/phase-49-postmerge.json"
REPORT = ROOT / "reports/phase-49-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness.md"
STATE = ROOT / "PROJECT_STATE.md"
WORKFLOW = ROOT / ".github/workflows/validate-phase-49-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness.yml"
CANDIDATE_SHA = "3c073e7a2b320987e86795aa053967e4a83eb2ec42ce36828322e6e6f31b4b4d"
POST_SHA = "e7f592280777c12c9ed51d70241729797db9dad053ddc234dbeaf492322c8413"
HEAD = "baa70c6f756fd747e40b4eb52d905a26583b988c"
MERGE = "65afc6dbcd4bf73518c2703dc2f15a0a3614ed95"
MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness"
FINAL_STATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-validated"
NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-assurance-candidate"
WORKFLOWS = 42

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def validate():
    errors = []
    for path, name in ((CANDIDATE,"candidate"),(POST,"postmerge"),(REPORT,"report"),(STATE,"state"),(WORKFLOW,"workflow")):
        if not path.is_file(): errors.append("Phase 49 %s missing" % name)
    if errors: return errors
    if sha(CANDIDATE) != CANDIDATE_SHA: errors.append("Phase 49 candidate digest drift")
    if sha(POST) != POST_SHA: errors.append("Phase 49 postmerge digest drift")
    candidate, post = load(CANDIDATE), load(POST)
    if post.get("candidate_record") != {"path": CANDIDATE.relative_to(ROOT).as_posix(), "sha256": CANDIDATE_SHA}: errors.append("candidate binding drift")
    if post.get("principia") != {"candidate_head_commit": HEAD, "merge_commit": MERGE, "pull_request": 90, "repository": "Rhodan-lab/principle-to-system"}: errors.append("merge provenance drift")
    if post.get("validation") != {"applicable_workflows": WORKFLOWS, "candidate_head_commit": HEAD, "status": "success"}: errors.append("workflow provenance drift")
    if post.get("result") != candidate.get("result") or post.get("authority") != candidate.get("authority"): errors.append("candidate finalization binding drift")
    if post.get("state") != FINAL_STATE or post.get("next_gate") != NEXT: errors.append("final state drift")
    if post.get("decision") != candidate.get("decision") or post.get("live") is not False or post.get("real_authorization_claimed") is not False: errors.append("final decision or frozen-state drift")
    state_text = STATE.read_text(encoding="utf-8")
    for marker in (
        "**Phase 49 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Population Execution Authorization Readiness merged and validated through PR #90.**",
        "Phase 49 state: **%s**" % FINAL_STATE,
        "| 49 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate population execution authorization readiness | Merged and validated through PR #90 |",
        "Phase 49 exact candidate validation passed at `%s`" % HEAD,
        "PR #90 was merged into `main` at commit `%s`" % MERGE,
        "Historical Phase 48 finalization marker:",
        "Atlas remains unchanged by Principia Phase 49",
        CANDIDATE_SHA, POST_SHA, "all 42 applicable workflows", "318 deterministic scenarios", "317 mutations",
    ):
        if marker not in state_text: errors.append("state marker missing: %s" % marker)
    if "## Next phase" not in state_text: errors.append("current next-phase section missing")
    else:
        section = state_text.rsplit("## Next phase",1)[1]
        if "Next gate: **%s**." % NEXT not in section: errors.append("current Phase 50 assurance gate missing")
        if "Next gate: **%s-candidate**." % MODE in section: errors.append("historical Phase 49 candidate gate remains current")
    report_text = REPORT.read_text(encoding="utf-8")
    for marker in ("Phase 49 candidate SHA-256: `%s`" % CANDIDATE_SHA, "Next gate", NEXT):
        if marker not in report_text: errors.append("report marker missing: %s" % marker)
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    if "contents: read" not in workflow_text or "validate_phase49_postmerge_record.py" not in workflow_text: errors.append("workflow finalization integration drift")
    for token in ("contents: write","pull_request_target","git push","git commit","repository: Rhodan-lab/Atlas"):
        if token in workflow_text: errors.append("forbidden workflow token: %s" % token)
    return errors

def main():
    errors = validate()
    if errors:
        print("Phase 49 post-merge record errors:", file=sys.stderr)
        for error in errors: print("- %s" % error, file=sys.stderr)
        return 1
    print("Phase 49 post-merge record passed: candidate=%s, postmerge=%s, head=%s, merge=%s, workflows=%s." % (CANDIDATE_SHA, POST_SHA, HEAD, MERGE, WORKFLOWS))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
