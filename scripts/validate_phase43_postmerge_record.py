#!/usr/bin/env python3
"""Validate immutable Phase 43 finalization provenance and state markers."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "release/phase-43-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness.json"
POST = ROOT / "release/phase-43-postmerge.json"
REPORT = ROOT / "reports/phase-43-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness.md"
STATE = ROOT / "PROJECT_STATE.md"
WORKFLOW = ROOT / ".github/workflows/validate-phase-43-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness.yml"
CANDIDATE_SHA = "5ffd6005a907742ac0c02c4077d68d8f1f646963a030405e53daed2219802ef3"
POST_SHA = "bbec0856c15c3286e9698d1a738cd9a7e77b13fc110b8aa0571cd4f9632d8488"
HEAD = "faa7b7f698767722bc58cd8785e04f1ac278f927"
MERGE = "0c1938169137ef9b5eead27f39e2b7c07f614f5b"
PREVIOUS_NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-candidate"
NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance-candidate"
CURRENT_NEXT = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-candidate'
FINAL_STATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-validated"
# Phase 43 keeps its immutable next-gate binding while the authoritative project gate advances through Phase 44 finalization.


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate():
    errors = []
    for path, name in ((CANDIDATE, "candidate"), (POST, "postmerge"), (REPORT, "report"), (STATE, "state"), (WORKFLOW, "workflow")):
        if not path.is_file():
            errors.append(f"Phase 43 {name} missing")
    if errors:
        return errors
    if sha(CANDIDATE) != CANDIDATE_SHA:
        errors.append("Phase 43 candidate digest drift")
    if sha(POST) != POST_SHA:
        errors.append("Phase 43 postmerge digest drift")
    candidate, post = load(CANDIDATE), load(POST)
    if post.get("candidate_record") != {"path": CANDIDATE.relative_to(ROOT).as_posix(), "sha256": CANDIDATE_SHA}:
        errors.append("candidate binding drift")
    if post.get("principia") != {"candidate_head_commit": HEAD, "merge_commit": MERGE, "pull_request": 78, "repository": "Rhodan-lab/principle-to-system"}:
        errors.append("merge provenance drift")
    if post.get("validation") != {"applicable_workflows": 37, "candidate_head_commit": HEAD, "status": "success"}:
        errors.append("workflow provenance drift")
    if post.get("result") != candidate.get("result") or post.get("authority") != candidate.get("authority"):
        errors.append("candidate finalization binding drift")
    if post.get("state") != FINAL_STATE or post.get("next_gate") != NEXT:
        errors.append("final state drift")
    if post.get("decision") != candidate.get("decision") or post.get("live") is not False or post.get("real_authorization_claimed") is not False:
        errors.append("final decision or frozen-state drift")

    state_text = STATE.read_text(encoding="utf-8")
    for marker in (
        "**Phase 43 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Assembly Readiness merged and validated through PR #78.**",
        f"Phase 43 state: **{FINAL_STATE}**",
        "| 43 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate assembly readiness | Merged and validated through PR #78 |",
        f"Phase 43 exact candidate validation passed at `{HEAD}`",
        f"PR #78 was merged into `main` at commit `{MERGE}`",
        "Historical Phase 42 finalization marker:",
        "Historical Phase 43 target marker:",
        f"Historical Phase 42 next-gate marker: Next gate: **{PREVIOUS_NEXT}**.",
        f"Historical Phase 43 next-gate marker: Next gate: **{NEXT}**.",
        "Atlas remains unchanged by Principia Phase 43",
        CANDIDATE_SHA,
        "all 37 applicable workflows",
        "150 deterministic scenarios",
        "149 mutations",
    ):
        if marker not in state_text:
            errors.append(f"state marker missing: {marker}")
    if "## Next phase" not in state_text:
        errors.append("current next-phase section missing")
    else:
        current_gate_section = state_text.rsplit("## Next phase", 1)[1]
        if f"Next gate: **{CURRENT_NEXT}**." not in current_gate_section:
            errors.append("current Phase 49 population-execution-authorization-readiness gate missing")
        if f"Next gate: **{NEXT}**." in current_gate_section:
            errors.append("historical Phase 44 assurance gate remains current")
        if f"Next gate: **{PREVIOUS_NEXT}**." in current_gate_section:
            errors.append("historical Phase 43 candidate gate remains current")

    report_text = REPORT.read_text(encoding="utf-8")
    for marker in (
        f"State: `{FINAL_STATE}`",
        f"Candidate SHA-256: `{CANDIDATE_SHA}`",
        f"Post-merge SHA-256: `{POST_SHA}`",
        "Applicable candidate workflows: `37`",
        f"Next gate: `{NEXT}`",
    ):
        if marker not in report_text:
            errors.append(f"report marker missing: {marker}")

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    if "contents: read" not in workflow_text or "validate_phase43_postmerge_record.py" not in workflow_text:
        errors.append("workflow finalization integration drift")
    for token in ("contents: write", "pull_request_target", "git push", "git commit", "repository: Rhodan-lab/Atlas"):
        if token in workflow_text:
            errors.append(f"forbidden workflow token: {token}")
    return errors


def main():
    errors = validate()
    if errors:
        print("Phase 43 post-merge record errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Phase 43 post-merge record passed: candidate={CANDIDATE_SHA}, postmerge={POST_SHA}, head={HEAD}, merge={MERGE}, workflows=37.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
