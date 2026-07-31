#!/usr/bin/env python3
"""Validate immutable Phase 42 finalization provenance and state markers."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "release/phase-42-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance.json"
POST = ROOT / "release/phase-42-postmerge.json"
REPORT = ROOT / "reports/phase-42-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance.md"
STATE = ROOT / "PROJECT_STATE.md"
WORKFLOW = ROOT / ".github/workflows/validate-phase-42-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance.yml"
CANDIDATE_SHA = "6fb602bc5ef863765ceb50ba66124b843381fd15c6dac9da9250429e18e76f26"
POST_SHA = "887aa4a6c23be70b0c619c09b024e58f4321acf19ea2181bbb0f5734c1fe5cf4"
HEAD = "0597916365d489b2738fbb905f0f40991f42a4b7"
MERGE = "057da54503e2c3b1ea1e86150c4015a99628dfed"
PREVIOUS_NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-candidate"
NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-candidate"
CURRENT_NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-candidate"
# Phase 42 keeps its immutable next-gate binding while the authoritative project gate advances through Phase 44 finalization.


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate():
    errors = []
    for path, name in ((CANDIDATE, "candidate"), (POST, "postmerge"), (REPORT, "report"), (STATE, "state"), (WORKFLOW, "workflow")):
        if not path.is_file():
            errors.append(f"Phase 42 {name} missing")
    if errors:
        return errors
    if sha(CANDIDATE) != CANDIDATE_SHA:
        errors.append("Phase 42 candidate digest drift")
    if sha(POST) != POST_SHA:
        errors.append("Phase 42 postmerge digest drift")
    candidate, post = load(CANDIDATE), load(POST)
    if post.get("candidate_record") != {"path": CANDIDATE.relative_to(ROOT).as_posix(), "sha256": CANDIDATE_SHA}:
        errors.append("candidate binding drift")
    if post.get("principia") != {"candidate_head_commit": HEAD, "merge_commit": MERGE, "pull_request": 75, "repository": "Rhodan-lab/principle-to-system"}:
        errors.append("merge provenance drift")
    if post.get("validation") != {"applicable_workflows": 36, "candidate_head_commit": HEAD, "status": "success"}:
        errors.append("workflow provenance drift")
    if post.get("result") != candidate.get("result") or post.get("authority") != candidate.get("authority"):
        errors.append("candidate finalization binding drift")
    if post.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-validated" or post.get("next_gate") != NEXT:
        errors.append("final state drift")
    state_text = STATE.read_text(encoding="utf-8")
    for marker in (
        "**Phase 42 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Preparation Readiness Assurance merged and validated through PR #75.**",
        "Phase 42 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-validated**",
        "| 42 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate preparation readiness assurance | Merged and validated through PR #75 |",
        f"Phase 42 exact candidate validation passed at `{HEAD}`",
        f"PR #75 was merged into `main` at commit `{MERGE}`",
        "Historical Phase 41 finalization marker:",
        "Historical Phase 42 target marker:",
        f"Historical Phase 41 next-gate marker: Next gate: **{PREVIOUS_NEXT}**.",
        f"Historical Phase 42 next-gate marker: Next gate: **{NEXT}**.",
        "Atlas remains unchanged by Principia Phase 42",
        CANDIDATE_SHA,
        "all 36 applicable workflows",
        "226 deterministic scenarios",
        "225 mutations",
    ):
        if marker not in state_text:
            errors.append(f"state marker missing: {marker}")
    if "## Next phase" not in state_text:
        errors.append("current next-phase section missing")
    else:
        current_gate_section = state_text.rsplit("## Next phase", 1)[1]
        if f"Next gate: **{CURRENT_NEXT}**." not in current_gate_section:
            errors.append("current Phase 47 population-execution-readiness gate missing from next-phase section")
        if f"Next gate: **{NEXT}**." in current_gate_section:
            errors.append("historical Phase 43 candidate gate remains current")
        if f"Next gate: **{PREVIOUS_NEXT}**." in current_gate_section:
            errors.append("historical Phase 42 assurance gate remains current")
    report_text = REPORT.read_text(encoding="utf-8")
    for marker in (
        "State: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-validated`",
        f"Candidate SHA-256: `{CANDIDATE_SHA}`",
        f"Post-merge SHA-256: `{POST_SHA}`",
        "Applicable candidate workflows: `36`",
        f"Next gate: `{NEXT}`",
    ):
        if marker not in report_text:
            errors.append(f"report marker missing: {marker}")
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    if "contents: read" not in workflow_text or "validate_phase42_postmerge_record.py" not in workflow_text:
        errors.append("workflow finalization integration drift")
    for token in ("contents: write", "pull_request_target", "git push", "git commit", "repository: Rhodan-lab/Atlas"):
        if token in workflow_text:
            errors.append(f"forbidden workflow token: {token}")
    return errors


def main():
    errors = validate()
    if errors:
        print("Phase 42 post-merge record errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Phase 42 post-merge record passed: candidate={CANDIDATE_SHA}, postmerge={POST_SHA}, head={HEAD}, merge={MERGE}, workflows=36.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
