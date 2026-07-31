#!/usr/bin/env python3
"""Validate immutable Phase 46 finalization provenance and state markers."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "release/phase-46-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance.json"
POST = ROOT / "release/phase-46-postmerge.json"
REPORT = ROOT / "reports/phase-46-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance.md"
STATE = ROOT / "PROJECT_STATE.md"
WORKFLOW = ROOT / ".github/workflows/validate-phase-46-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance.yml"
CANDIDATE_SHA = "2b7ced60688ff02ea11231bc53bad3e39e0ec22aa10a233e5f270b0d586039ad"
POST_SHA = "b9ccbd2125db1538bb1b4028b3dd15411971baba72bf059448d64fa32ccee121"
HEAD = "e108372f76503ca819afd3e6573e7efaf8e5a295"
MERGE = "d24fee31b04e7e312106cb020116c9b1e753117c"
MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance"
FINAL_STATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance-validated"
NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-candidate"
CURRENT_NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance-candidate"
WORKFLOWS = 39

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def validate():
    errors = []
    for path, name in ((CANDIDATE, "candidate"), (POST, "postmerge"), (REPORT, "report"), (STATE, "state"), (WORKFLOW, "workflow")):
        if not path.is_file():
            errors.append("Phase 46 %s missing" % name)
    if errors:
        return errors
    if sha(CANDIDATE) != CANDIDATE_SHA:
        errors.append("Phase 46 candidate digest drift")
    if sha(POST) != POST_SHA:
        errors.append("Phase 46 postmerge digest drift")
    candidate, post = load(CANDIDATE), load(POST)
    if post.get("candidate_record") != {"path": CANDIDATE.relative_to(ROOT).as_posix(), "sha256": CANDIDATE_SHA}:
        errors.append("candidate binding drift")
    if post.get("principia") != {"candidate_head_commit": HEAD, "merge_commit": MERGE, "pull_request": 84, "repository": "Rhodan-lab/principle-to-system"}:
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
    markers = (
        "**Phase 46 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Population Readiness Assurance merged and validated through PR #84.**",
        "Phase 46 state: **%s**" % FINAL_STATE,
        "| 46 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate population readiness assurance | Merged and validated through PR #84 |",
        "Phase 46 exact candidate validation passed at `%s`" % HEAD,
        "PR #84 was merged into `main` at commit `%s`" % MERGE,
        "Historical Phase 45 finalization marker:",
        "Atlas remains unchanged by Principia Phase 46",
        CANDIDATE_SHA,
        POST_SHA,
        "all 39 applicable workflows",
        "198 deterministic scenarios",
        "197 mutations",
    )
    for marker in markers:
        if marker not in state_text:
            errors.append("state marker missing: %s" % marker)
    if "## Next phase" not in state_text:
        errors.append("current next-phase section missing")
    else:
        section = state_text.rsplit("## Next phase", 1)[1]
        if "Next gate: **%s**." % CURRENT_NEXT not in section:
            errors.append("current Phase 48 population-execution-readiness-assurance gate missing")
        if "Next gate: **%s**." % NEXT in section:
            errors.append("historical Phase 47 population-execution-readiness gate remains current")
        if "Next gate: **%s-candidate**." % MODE in section:
            errors.append("historical Phase 46 assurance gate remains current")

    report_text = REPORT.read_text(encoding="utf-8")
    for marker in (
        "State: `%s`" % FINAL_STATE,
        "Phase 46 candidate SHA-256: `%s`" % CANDIDATE_SHA,
        "Phase 46 post-merge SHA-256: `%s`" % POST_SHA,
        "Phase 46 applicable candidate workflows: `39`",
        "Next gate: `%s`" % NEXT,
    ):
        if marker not in report_text:
            errors.append("report marker missing: %s" % marker)

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    if "contents: read" not in workflow_text or "validate_phase46_postmerge_record.py" not in workflow_text:
        errors.append("workflow finalization integration drift")
    for token in ("contents: write", "pull_request_target", "git push", "git commit", "repository: Rhodan-lab/Atlas"):
        if token in workflow_text:
            errors.append("forbidden workflow token: %s" % token)
    return errors

def main():
    errors = validate()
    if errors:
        print("Phase 46 post-merge record errors:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1
    print("Phase 46 post-merge record passed: candidate=%s, postmerge=%s, head=%s, merge=%s, workflows=%s." % (CANDIDATE_SHA, POST_SHA, HEAD, MERGE, WORKFLOWS))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
