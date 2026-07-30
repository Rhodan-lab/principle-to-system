#!/usr/bin/env python3
"""Validate the immutable Phase 38 post-merge record and project-state transition."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "release/phase-38-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance.json"
POST = ROOT / "release/phase-38-postmerge.json"
REPORT = ROOT / "reports/phase-38-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance.md"
STATE = ROOT / "PROJECT_STATE.md"
WORKFLOW = ROOT / ".github/workflows/validate-phase-38-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance.yml"
CANDIDATE_SHA = "b3c5d8ea8da88cd2975531ccd149b0dde980dc480b9e7385425cafad3e024ec8"
POST_SHA = "5c6e146edfe4d8e8743b8cbf38bf19593383c5fde34e5111c6eb6a6d28c0b2af"
HEAD = "08b75c7d280f3482b746a5de9c5c6d48541e3cf6"
MERGE = "be3f305f7234875be541e6f5e2bb8fb1bf0c0f43"
NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-candidate"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path)
    return value


def validate() -> list[str]:
    errors: list[str] = []
    for path, label in ((CANDIDATE, "candidate"), (POST, "postmerge"), (REPORT, "report"), (STATE, "project state"), (WORKFLOW, "workflow")):
        if not path.is_file():
            errors.append(f"Phase 38 {label} missing")
    if errors:
        return errors
    if sha_file(CANDIDATE) != CANDIDATE_SHA:
        errors.append("Phase 38 candidate digest drift")
    if sha_file(POST) != POST_SHA:
        errors.append("Phase 38 postmerge digest drift")
    candidate, post = load(CANDIDATE), load(POST)
    if candidate.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-candidate" or candidate.get("next_gate") != NEXT:
        errors.append("Phase 38 candidate gate drift")
    if post.get("contract") != "principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-finalization/0.1":
        errors.append("Phase 38 finalization contract drift")
    if post.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-validated" or post.get("next_gate") != NEXT:
        errors.append("Phase 38 final state drift")
    expected_record = {
        "path": "release/phase-38-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance.json",
        "sha256": CANDIDATE_SHA,
    }
    if post.get("candidate_record") != expected_record:
        errors.append("Phase 38 candidate binding drift")
    expected_pr = {
        "candidate_head_commit": HEAD,
        "merge_commit": MERGE,
        "pull_request": 67,
        "repository": "Rhodan-lab/principle-to-system",
    }
    if post.get("principia") != expected_pr:
        errors.append("Phase 38 merge provenance drift")
    expected_validation = {"applicable_workflows": 32, "candidate_head_commit": HEAD, "status": "success"}
    if post.get("validation") != expected_validation:
        errors.append("Phase 38 workflow provenance drift")
    if post.get("result") != candidate.get("result"):
        errors.append("Phase 38 result binding drift")
    if post.get("authority") != candidate.get("authority") or post.get("live") is not False or post.get("real_authorization_claimed") is not False:
        errors.append("Phase 38 authority drift")

    state = STATE.read_text(encoding="utf-8")
    required = (
        "**Phase 38 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Readiness Assurance merged and validated through PR #67.**",
        "Phase 38 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-validated**",
        "| 38 | Offline consequence-plan review-response intake envelope validation execution authorization decision readiness assurance | Merged and validated through PR #67 |",
        f"Phase 38 exact candidate validation passed at `{HEAD}`",
        f"PR #67 was merged into `main` at commit `{MERGE}`",
        "Historical Phase 37 finalization marker: **Phase 37 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Readiness merged and validated through PR #65.**",
        "Historical Phase 38 candidate marker: `exact-head validation pending`",
        "Historical Phase 38 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-candidate`",
        "Atlas remains unchanged by Principia Phase 38",
        "## Phase 38 result — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Readiness Assurance",
        CANDIDATE_SHA,
        HEAD,
        MERGE,
        "all 32 applicable workflows",
        "206 deterministic scenarios",
        "205 mutations",
    )
    for marker in required:
        if marker not in state:
            errors.append(f"Phase 38 project-state marker missing: {marker}")
    gate_markers = (
        f"Next gate: **{NEXT}**",
        f"Historical Phase 39 target marker: `{NEXT}`",
    )
    if not any(marker in state for marker in gate_markers):
        errors.append("Phase 38 project-state gate marker missing")
    if "Principia and Atlas remain separate repositories with separate lifecycle authority." not in state:
        errors.append("Repository authority separation lost")

    report = REPORT.read_text(encoding="utf-8")
    for marker in (
        "# Phase 38 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Readiness Assurance",
        "State: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-validated`",
        f"Candidate SHA-256: `{CANDIDATE_SHA}`",
        f"Exact tested head: `{HEAD}`",
        "Candidate PR: `#67`",
        f"Candidate merge: `{MERGE}`",
        "Applicable candidate workflows: `32`",
        f"Post-merge SHA-256: `{POST_SHA}`",
        f"Next gate: `{NEXT}`",
        "206 deterministic scenarios",
        "205 rejected mutations",
        "No authorization-decision candidate was created",
    ):
        if marker not in report:
            errors.append(f"Phase 38 report marker missing: {marker}")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    if "contents: read" not in workflow:
        errors.append("Phase 38 workflow is not read-only")
    if "validate_phase38_postmerge_record.py" not in workflow:
        errors.append("Phase 38 workflow does not validate postmerge record")
    for token in ("contents: write", "pull_request_target", "git push", "git commit", "repository: Rhodan-lab/Atlas"):
        if token in workflow:
            errors.append(f"Phase 38 workflow forbidden token: {token}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Phase 38 post-merge record errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Phase 38 post-merge record passed: candidate={CANDIDATE_SHA}, postmerge={POST_SHA}, head={HEAD}, merge={MERGE}, workflows=32.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
