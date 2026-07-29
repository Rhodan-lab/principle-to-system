#!/usr/bin/env python3
"""Validate the finalized post-merge Phase 25 review-request packet record."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
CANDIDATE_PATH = ROOT / "release/phase-25-offline-consequence-plan-review-request-packet.json"
FINALIZATION_PATH = ROOT / "release/phase-25-postmerge.json"
REPORT_PATH = ROOT / "reports/phase-25-offline-consequence-plan-review-request-packet.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-25-offline-consequence-plan-review-request-packet.yml"

EXPECTED_CANDIDATE_HEAD = "86c543c542b038038732b50ff6fdf9a79b55c934"
EXPECTED_MERGE = "3612d9f185f1db99565ecfd7fd1a9288dd0cb3e9"
EXPECTED_CANDIDATE_SHA256 = "38862c26ae18dc11c6570c33182c0da158ed8e59a19402073e1c733de6d154f3"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def fail(errors: list[str]) -> int:
    print("Phase 25 post-merge record errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


def main() -> int:
    errors: list[str] = []
    for path in (STATE_PATH, CANDIDATE_PATH, FINALIZATION_PATH, REPORT_PATH, WORKFLOW_PATH):
        if not path.is_file():
            errors.append(f"missing Phase 25 finalization file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    if sha256_file(CANDIDATE_PATH) != EXPECTED_CANDIDATE_SHA256:
        errors.append("Phase 25 candidate record digest changed after merge")

    finalization = load_json(FINALIZATION_PATH)
    for key, value in {
        "contract": "principia-offline-consequence-plan-review-request-packet-finalization/0.1",
        "phase": 25,
        "state": "offline-consequence-plan-review-request-packet-validated",
        "mode": "offline-consequence-plan-review-request-packet",
        "fixture_kind": "bounded-synthetic",
        "decision": "review-request-packets-prepared-no-dispatch",
        "live": False,
        "next_gate": "offline-consequence-plan-review-request-packet-assurance-candidate",
        "live_activation_permitted": False,
        "real_authorization_claimed": False,
    }.items():
        if finalization.get(key) != value:
            errors.append(f"Phase 25 finalization {key} must equal {value}")

    if finalization.get("candidate_record") != {
        "path": "release/phase-25-offline-consequence-plan-review-request-packet.json",
        "sha256": EXPECTED_CANDIDATE_SHA256,
    }:
        errors.append("Phase 25 finalization candidate record pin is invalid")

    principia = finalization.get("principia")
    expected_principia = {
        "repository": "Rhodan-lab/principle-to-system",
        "pull_request": 41,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "merge_commit": EXPECTED_MERGE,
    }
    if not isinstance(principia, Mapping) or any(
        principia.get(key) != value for key, value in expected_principia.items()
    ):
        errors.append("Phase 25 Principia provenance is invalid")

    if finalization.get("validation") != {
        "applicable_workflows": 19,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "status": "success",
    }:
        errors.append("Phase 25 exact-head validation provenance is invalid")

    expected_result = {
        "effective_hold_count": 0,
        "human_authorization_count": 0,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
        "operational_effect_count": 0,
        "outcome_selected_count": 0,
        "packet_count": 2,
        "packet_dispatch_count": 0,
        "packet_local_only_count": 2,
        "packet_prepared_count": 2,
        "question_count": 6,
        "real_authorization_claimed": False,
        "response_submission_count": 0,
        "review_completed_count": 0,
        "review_started_count": 0,
        "reviewer_contact_count": 0,
        "reviewer_identity_count": 0,
        "section_count": 12,
        "status_change_count": 0,
    }
    if finalization.get("result") != expected_result:
        errors.append("Phase 25 finalization result is invalid")

    authority = finalization.get("authority")
    if not isinstance(authority, Mapping):
        errors.append("Phase 25 authority record is missing")
    else:
        for key in (
            "atlas_call_permitted",
            "automatic_status_change",
            "automatic_release_action",
            "external_delivery_permitted",
            "external_network_required",
            "human_authorization_claimed",
            "repository_mutation",
            "review_execution_authorized",
            "review_request_dispatch_authorized",
            "reviewer_contact_permitted",
        ):
            if authority.get(key) is not False:
                errors.append(f"Phase 25 finalization must keep {key}=false")
        if authority.get("local_packet_preparation_permitted") is not True:
            errors.append("Phase 25 finalization must preserve local packet preparation")
        if authority.get("status_inheritance") != "prohibited":
            errors.append("Phase 25 finalization must prohibit status inheritance")

    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "**Phase 25 — Offline Consequence-Plan Review-Request Packet merged and validated through PR #41.**",
        "Phase 25 state: **offline-consequence-plan-review-request-packet-validated**",
        "| 25 | Offline consequence-plan review-request packet | Merged and validated through PR #41 |",
        f"Phase 25 exact candidate validation passed at `{EXPECTED_CANDIDATE_HEAD}`",
        f"PR #41 was merged into `main` at commit `{EXPECTED_MERGE}`",
        "release/phase-25-postmerge.json",
        "Historical Phase 25 candidate marker: `exact-head validation pending`",
        "offline-consequence-plan-review-request-packet-assurance-candidate",
        "review-request-packets-prepared-no-dispatch",
        "prepared-local-not-dispatched",
        "packet_count: 2",
        "packet_dispatch_count: 0",
        "human_gate_pending_count: 8",
        "review_started_count: 0",
        "real_authorization_claimed: false",
        "Atlas remains unchanged by Principia Phase 25.",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 25 finalization marker: {marker}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        "# Phase 25 — Offline Consequence-Plan Review-Request Packet",
        f"> Exact tested head: `{EXPECTED_CANDIDATE_HEAD}`",
        f"> Merge commit: `{EXPECTED_MERGE}`",
        "> Final state: `offline-consequence-plan-review-request-packet-validated`",
        "release/phase-25-postmerge.json",
        "2 local-only packets",
        "8 pending human gates",
        "review-request-packets-prepared-no-dispatch",
        "> Live: `false`",
    ):
        if marker not in report:
            errors.append(f"Phase 25 report missing finalization marker: {marker}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/finalize-phase-25-record",
        "scripts/validate_phase25_postmerge_record.py",
        "release/phase-25-postmerge.json",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"Phase 25 workflow missing finalization marker: {marker}")
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
            errors.append(f"Phase 25 workflow contains forbidden token: {forbidden}")

    if errors:
        return fail(errors)
    print(
        "Phase 25 post-merge record passed: PR #41 and exact candidate head pinned, "
        "two packets local-only, eight human gates pending, and dispatch and review disabled."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
