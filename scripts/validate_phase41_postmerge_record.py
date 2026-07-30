#!/usr/bin/env python3
"""Validate immutable Phase 41 finalization provenance and state markers."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "release/phase-41-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness.json"
POST = ROOT / "release/phase-41-postmerge.json"
REPORT = ROOT / "reports/phase-41-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness.md"
STATE = ROOT / "PROJECT_STATE.md"
WORKFLOW = ROOT / ".github/workflows/validate-phase-41-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness.yml"
CANDIDATE_SHA = "c45f148554f66bf21db03fa446475e55746086a47da0bb56841b95012be1d33b"
POST_SHA = "864ef4e905df2c5a4cc4bac1b9ebdc035211c36a8c927eec9741c45fc6f5d1b0"
HEAD = "4700bd61823d66b2296b9513ad7f564d84bb0e73"
MERGE = "25073fd7765a9faf3f53235cded3356839861917"
NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-candidate"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate():
    errors = []
    for path, name in ((CANDIDATE, "candidate"), (POST, "postmerge"), (REPORT, "report"), (STATE, "state"), (WORKFLOW, "workflow")):
        if not path.is_file():
            errors.append(f"Phase 41 {name} missing")
    if errors:
        return errors
    if sha(CANDIDATE) != CANDIDATE_SHA:
        errors.append("Phase 41 candidate digest drift")
    if sha(POST) != POST_SHA:
        errors.append("Phase 41 postmerge digest drift")
    candidate, post = load(CANDIDATE), load(POST)
    if post.get("candidate_record") != {"path": CANDIDATE.relative_to(ROOT).as_posix(), "sha256": CANDIDATE_SHA}:
        errors.append("candidate binding drift")
    if post.get("principia") != {"candidate_head_commit": HEAD, "merge_commit": MERGE, "pull_request": 73, "repository": "Rhodan-lab/principle-to-system"}:
        errors.append("merge provenance drift")
    if post.get("validation") != {"applicable_workflows": 35, "candidate_head_commit": HEAD, "status": "success"}:
        errors.append("workflow provenance drift")
    if post.get("result") != candidate.get("result") or post.get("authority") != candidate.get("authority"):
        errors.append("candidate finalization binding drift")
    if post.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-validated" or post.get("next_gate") != NEXT:
        errors.append("final state drift")
    state_text = STATE.read_text(encoding="utf-8")
    for marker in (
        "**Phase 41 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Preparation Readiness merged and validated through PR #73.**",
        "Phase 41 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-validated**",
        "| 41 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate preparation readiness | Merged and validated through PR #73 |",
        f"Phase 41 exact candidate validation passed at `{HEAD}`",
        f"PR #73 was merged into `main` at commit `{MERGE}`",
        "Historical Phase 40 finalization marker:",
        "Historical Phase 41 target marker:",
        "Atlas remains unchanged by Principia Phase 41",
        CANDIDATE_SHA,
        "all 35 applicable workflows",
        "198 deterministic scenarios",
        "197 mutations",
        f"Next gate: **{NEXT}**",
    ):
        if marker not in state_text:
            errors.append(f"state marker missing: {marker}")
    report_text = REPORT.read_text(encoding="utf-8")
    for marker in (
        "State: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-validated`",
        f"Candidate SHA-256: `{CANDIDATE_SHA}`",
        f"Post-merge SHA-256: `{POST_SHA}`",
        "Applicable candidate workflows: `35`",
        f"Next gate: `{NEXT}`",
    ):
        if marker not in report_text:
            errors.append(f"report marker missing: {marker}")
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    if "contents: read" not in workflow_text or "validate_phase41_postmerge_record.py" not in workflow_text:
        errors.append("workflow finalization integration drift")
    for token in ("contents: write", "pull_request_target", "git push", "git commit", "repository: Rhodan-lab/Atlas"):
        if token in workflow_text:
            errors.append(f"forbidden workflow token: {token}")
    return errors


def main():
    errors = validate()
    if errors:
        print("Phase 41 post-merge record errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Phase 41 post-merge record passed: candidate={CANDIDATE_SHA}, postmerge={POST_SHA}, head={HEAD}, merge={MERGE}, workflows=35.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
