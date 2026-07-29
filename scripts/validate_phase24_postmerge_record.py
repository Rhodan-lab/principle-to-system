#!/usr/bin/env python3
"""Validate the finalized post-merge Phase 24 review-readiness record."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
CANDIDATE_PATH = ROOT / "release/phase-24-offline-consequence-plan-review-readiness.json"
FINALIZATION_PATH = ROOT / "release/phase-24-postmerge.json"
REPORT_PATH = ROOT / "reports/phase-24-offline-consequence-plan-review-readiness.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-24-offline-consequence-plan-review-readiness.yml"

EXPECTED_CANDIDATE_HEAD = "e385e3f418fc48517be20bfebc30eda2b5f319aa"
EXPECTED_MERGE = "ab97b345045264653cacdbf26b5ea5d8778d3d3b"
EXPECTED_CANDIDATE_SHA256 = "45ca01dd5af4cfc550abcacb4d5b6cf090c7e138ff2b4663a077fde43d615a85"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def fail(errors: list[str]) -> int:
    print("Phase 24 post-merge record errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


def main() -> int:
    errors: list[str] = []
    for path in (STATE_PATH, CANDIDATE_PATH, FINALIZATION_PATH, REPORT_PATH, WORKFLOW_PATH):
        if not path.is_file():
            errors.append(f"missing Phase 24 finalization file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    if sha256_file(CANDIDATE_PATH) != EXPECTED_CANDIDATE_SHA256:
        errors.append("Phase 24 candidate record digest changed after merge")

    finalization = load_json(FINALIZATION_PATH)
    for key, value in {
        "contract": "principia-offline-consequence-plan-review-readiness-finalization/0.1",
        "phase": 24,
        "state": "offline-consequence-plan-review-readiness-validated",
        "mode": "offline-consequence-plan-review-readiness",
        "fixture_kind": "bounded-synthetic",
        "decision": "review-readiness-recorded-no-review-started",
        "live": False,
        "next_gate": "offline-consequence-plan-review-request-packet-candidate",
        "live_activation_permitted": False,
        "real_authorization_claimed": False,
    }.items():
        if finalization.get(key) != value:
            errors.append(f"Phase 24 finalization {key} must equal {value}")

    if finalization.get("candidate_record") != {
        "path": "release/phase-24-offline-consequence-plan-review-readiness.json",
        "sha256": EXPECTED_CANDIDATE_SHA256,
    }:
        errors.append("Phase 24 finalization candidate record pin is invalid")

    principia = finalization.get("principia")
    expected_principia = {
        "repository": "Rhodan-lab/principle-to-system",
        "pull_request": 39,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "merge_commit": EXPECTED_MERGE,
    }
    if not isinstance(principia, Mapping) or any(
        principia.get(key) != value for key, value in expected_principia.items()
    ):
        errors.append("Phase 24 Principia provenance is invalid")

    if finalization.get("validation") != {
        "applicable_workflows": 18,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "status": "success",
    }:
        errors.append("Phase 24 exact-head validation provenance is invalid")

    if finalization.get("result") != {
        "effective_hold_count": 0,
        "human_authorization_count": 0,
        "human_ready_count": 0,
        "machine_ready_count": 2,
        "operational_effect_count": 0,
        "outcome_selected_count": 0,
        "plan_count": 2,
        "readiness_record_count": 2,
        "real_authorization_claimed": False,
        "review_completed_count": 0,
        "review_request_dispatch_count": 0,
        "review_request_packet_preparation_count": 2,
        "review_started_count": 0,
        "status_change_count": 0,
        "unmet_human_gate_count": 8,
    }:
        errors.append("Phase 24 finalization result is invalid")

    authority = finalization.get("authority")
    if not isinstance(authority, Mapping):
        errors.append("Phase 24 authority record is missing")
    else:
        for key in (
            "atlas_call_permitted",
            "automatic_status_change",
            "automatic_release_action",
            "external_network_required",
            "human_authorization_claimed",
            "repository_mutation",
            "review_execution_authorized",
            "review_request_dispatch_authorized",
        ):
            if authority.get(key) is not False:
                errors.append(f"Phase 24 finalization must keep {key}=false")
        if authority.get("status_inheritance") != "prohibited":
            errors.append("Phase 24 finalization must prohibit status inheritance")

    state = STATE_PATH.read_text(encoding="utf-8")
    # Phase 24 may no longer be the current heading after a later phase is validated.
    # Its immutable row, provenance, candidate history, and next-gate record remain required.
    for marker in (
        "Phase 24 state: **offline-consequence-plan-review-readiness-validated**",
        "| 24 | Offline consequence-plan review readiness | Merged and validated through PR #39 |",
        f"Phase 24 exact candidate validation passed at `{EXPECTED_CANDIDATE_HEAD}`",
        f"PR #39 was merged into `main` at commit `{EXPECTED_MERGE}`",
        "release/phase-24-postmerge.json",
        "Historical Phase 24 candidate marker: `exact-head validation pending`",
        "offline-consequence-plan-review-request-packet-candidate",
        "review-readiness-recorded-no-review-started",
        "machine-ready-human-gates-pending",
        "human_authorization_count: 0",
        "review_started_count: 0",
        "real_authorization_claimed: false",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 24 finalization marker: {marker}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        "# Phase 24 — Offline Consequence-Plan Review Readiness",
        f"> Exact tested head: `{EXPECTED_CANDIDATE_HEAD}`",
        f"> Merge commit: `{EXPECTED_MERGE}`",
        "> Final state: `offline-consequence-plan-review-readiness-validated`",
        "release/phase-24-postmerge.json",
        "2 machine-ready plans",
        "8 pending human gates",
        "review-readiness-recorded-no-review-started",
        "> Live: `false`",
    ):
        if marker not in report:
            errors.append(f"Phase 24 report missing finalization marker: {marker}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/finalize-phase-24-record",
        "scripts/validate_phase24_postmerge_record.py",
        "release/phase-24-postmerge.json",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"Phase 24 workflow missing finalization marker: {marker}")
    for forbidden in (
        "contents" + ": write",
        "git " + "push",
        "git " + "commit",
        "pull_request" + "_target",
        "repository: Rhodan-lab/Atlas",
        "curl ",
        "wget ",
    ):
        if forbidden in workflow:
            errors.append(f"Phase 24 workflow contains forbidden token: {forbidden}")

    if errors:
        return fail(errors)
    print(
        "Phase 24 post-merge record passed: PR #39 and exact candidate head pinned, "
        "two plans machine-ready, eight human gates pending, and review execution disabled."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
