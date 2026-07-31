#!/usr/bin/env python3
"""Validate immutable Phase 44 finalization provenance and state markers."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "release/phase-44-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance.json"
POST = ROOT / "release/phase-44-postmerge.json"
REPORT = ROOT / "reports/phase-44-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance.md"
STATE = ROOT / "PROJECT_STATE.md"
WORKFLOW = ROOT / ".github/workflows/validate-phase-44-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance.yml"
CANDIDATE_SHA = "f6e807f7c56513c0a13265f833cefeca3f9b9503d52b8826a4055069220d08c6"
POST_SHA = "131e1886494caf9d686d8b4303ffe755b70146fb6b1b3f3577cf3564d2d75322"
HEAD = "b58811f3b01dbb68992c4ee638978a06bbb095e7"
MERGE = "d5756679785e283f044b191e01945009a506e8ec"
PREVIOUS_NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance-candidate"
NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-candidate"
CURRENT_NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-candidate"
FINAL_STATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance-validated"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate():
    errors = []
    for path, name in ((CANDIDATE, "candidate"), (POST, "postmerge"), (REPORT, "report"), (STATE, "state"), (WORKFLOW, "workflow")):
        if not path.is_file():
            errors.append(f"Phase 44 {name} missing")
    if errors:
        return errors
    if sha(CANDIDATE) != CANDIDATE_SHA:
        errors.append("Phase 44 candidate digest drift")
    if sha(POST) != POST_SHA:
        errors.append("Phase 44 postmerge digest drift")
    candidate, post = load(CANDIDATE), load(POST)
    if post.get("candidate_record") != {"path": CANDIDATE.relative_to(ROOT).as_posix(), "sha256": CANDIDATE_SHA}:
        errors.append("candidate binding drift")
    if post.get("principia") != {"candidate_head_commit": HEAD, "merge_commit": MERGE, "pull_request": 80, "repository": "Rhodan-lab/principle-to-system"}:
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
        "**Phase 44 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Assembly Readiness Assurance merged and validated through PR #80.**",
        f"Phase 44 state: **{FINAL_STATE}**",
        "| 44 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate assembly readiness assurance | Merged and validated through PR #80 |",
        f"Phase 44 exact candidate validation passed at `{HEAD}`",
        f"PR #80 was merged into `main` at commit `{MERGE}`",
        "Historical Phase 43 finalization marker:",
        "Historical Phase 44 target marker:",
        f"Historical Phase 43 next-gate marker: Next gate: **{PREVIOUS_NEXT}**.",
        "Atlas remains unchanged by Principia Phase 44",
        CANDIDATE_SHA,
        "all 37 applicable workflows",
        "126 deterministic scenarios",
        "125 mutations",
    ):
        if marker not in state_text:
            errors.append(f"state marker missing: {marker}")
    if "## Next phase" not in state_text:
        errors.append("current next-phase section missing")
    else:
        current_gate_section = state_text.rsplit("## Next phase", 1)[1]
        if f"Next gate: **{CURRENT_NEXT}**." not in current_gate_section:
            errors.append("current Phase 47 population-execution-readiness gate missing")
        if f"Next gate: **{NEXT}**." in current_gate_section:
            errors.append("historical Phase 45 population-readiness gate remains current")
        if f"Next gate: **{PREVIOUS_NEXT}**." in current_gate_section:
            errors.append("historical Phase 44 assurance gate remains current")

    report_text = REPORT.read_text(encoding="utf-8")
    for marker in (
        f"State: `{FINAL_STATE}`",
        f"Phase 44 candidate SHA-256: `{CANDIDATE_SHA}`",
        f"Phase 44 post-merge SHA-256: `{POST_SHA}`",
        "Phase 44 applicable candidate workflows: `37`",
        f"Next gate: `{NEXT}`",
    ):
        if marker not in report_text:
            errors.append(f"report marker missing: {marker}")

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    if "contents: read" not in workflow_text or "validate_phase44_postmerge_record.py" not in workflow_text:
        errors.append("workflow finalization integration drift")
    for token in ("contents: write", "pull_request_target", "git push", "git commit", "repository: Rhodan-lab/Atlas"):
        if token in workflow_text:
            errors.append(f"forbidden workflow token: {token}")
    return errors


def main():
    errors = validate()
    if errors:
        print("Phase 44 post-merge record errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Phase 44 post-merge record passed: candidate={CANDIDATE_SHA}, postmerge={POST_SHA}, head={HEAD}, merge={MERGE}, workflows=37.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
