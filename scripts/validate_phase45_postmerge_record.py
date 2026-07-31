#!/usr/bin/env python3
"""Validate immutable Phase 45 finalization provenance and state markers."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / 'release/phase-45-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness.json'
POST = ROOT / "release/phase-45-postmerge.json"
REPORT = ROOT / 'reports/phase-45-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness.md'
STATE = ROOT / "PROJECT_STATE.md"
WORKFLOW = ROOT / '.github/workflows/validate-phase-45-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness.yml'
CANDIDATE_SHA = '3fa7ce42cce65231c394f27f248e68ce40799ba9a5ccf183923c59fa9da851d6'
POST_SHA = '74a75833b867fa1db0bad3651e2131d0cbc0f9cacff9fa27f5f9498f11810ac1'
HEAD = '74b8522b71d2963dbbfa6923b5fe41cb10b1bfcc'
MERGE = '63948f6a148f3ab733b16508fea3406374f7e4ab'
MODE = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness'
FINAL_STATE = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-validated'
NEXT = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance-candidate'
CURRENT_NEXT = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-candidate'
WORKFLOWS = 38

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def validate():
    errors = []
    for path, name in ((CANDIDATE, "candidate"), (POST, "postmerge"), (REPORT, "report"), (STATE, "state"), (WORKFLOW, "workflow")):
        if not path.is_file():
            errors.append(f"Phase 45 {name} missing")
    if errors:
        return errors
    if sha(CANDIDATE) != CANDIDATE_SHA:
        errors.append("Phase 45 candidate digest drift")
    if sha(POST) != POST_SHA:
        errors.append("Phase 45 postmerge digest drift")
    candidate, post = load(CANDIDATE), load(POST)
    if post.get("candidate_record") != {"path": CANDIDATE.relative_to(ROOT).as_posix(), "sha256": CANDIDATE_SHA}:
        errors.append("candidate binding drift")
    if post.get("principia") != {"candidate_head_commit": HEAD, "merge_commit": MERGE, "pull_request": 82, "repository": "Rhodan-lab/principle-to-system"}:
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
        "**Phase 45 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Population Readiness merged and validated through PR #82.**",
        f"Phase 45 state: **{FINAL_STATE}**",
        "| 45 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate population readiness | Merged and validated through PR #82 |",
        f"Phase 45 exact candidate validation passed at `{HEAD}`",
        f"PR #82 was merged into `main` at commit `{MERGE}`",
        "Atlas remains unchanged by Principia Phase 45",
        CANDIDATE_SHA,
        POST_SHA,
        "all 38 applicable workflows",
        "170 deterministic scenarios",
        "169 mutations",
    ):
        if marker not in state_text:
            errors.append(f"state marker missing: {marker}")
    if "## Next phase" not in state_text:
        errors.append("current next-phase section missing")
    else:
        section = state_text.rsplit("## Next phase", 1)[1]
        if f"Next gate: **{CURRENT_NEXT}**." not in section:
            errors.append("current Phase 47 population-execution-readiness gate missing")
        if f"Next gate: **{NEXT}**." in section:
            errors.append("historical Phase 46 assurance gate remains current")
        if f"Next gate: **{MODE}-candidate**." in section:
            errors.append("historical Phase 45 candidate gate remains current")

    report_text = REPORT.read_text(encoding="utf-8")
    for marker in (
        f"State: `{FINAL_STATE}`",
        f"Phase 45 candidate SHA-256: `{CANDIDATE_SHA}`",
        f"Phase 45 post-merge SHA-256: `{POST_SHA}`",
        "Phase 45 applicable candidate workflows: `38`",
        f"Next gate: `{NEXT}`",
    ):
        if marker not in report_text:
            errors.append(f"report marker missing: {marker}")

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    if "contents: read" not in workflow_text or "validate_phase45_postmerge_record.py" not in workflow_text:
        errors.append("workflow finalization integration drift")
    for token in ("contents: write", "pull_request_target", "git push", "git commit", "repository: Rhodan-lab/Atlas"):
        if token in workflow_text:
            errors.append(f"forbidden workflow token: {token}")
    return errors

def main():
    errors = validate()
    if errors:
        print("Phase 45 post-merge record errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Phase 45 post-merge record passed: candidate={CANDIDATE_SHA}, postmerge={POST_SHA}, head={HEAD}, merge={MERGE}, workflows={WORKFLOWS}.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
