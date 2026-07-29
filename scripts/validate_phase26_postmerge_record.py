#!/usr/bin/env python3
"""Validate the finalized post-merge Phase 26 packet-assurance record."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
CANDIDATE_PATH = ROOT / "release/phase-26-offline-consequence-plan-review-request-packet-assurance.json"
FINALIZATION_PATH = ROOT / "release/phase-26-postmerge.json"
REPORT_PATH = ROOT / "reports/phase-26-offline-consequence-plan-review-request-packet-assurance.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-26-offline-consequence-plan-review-request-packet-assurance.yml"

EXPECTED_CANDIDATE_HEAD = "58ffacbaff03301145ab0c68f4f692083641a7c1"
EXPECTED_MERGE = "72bca34c7623c19fed0c7f625e19cd9b7291c47d"
EXPECTED_CANDIDATE_SHA256 = "cdf82f5e4792d43e21b3242fa4114a4063bab9849abb68be25abb44c3a51b22c"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def fail(errors: list[str]) -> int:
    print("Phase 26 post-merge record errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


def main() -> int:
    errors: list[str] = []
    for path in (STATE_PATH, CANDIDATE_PATH, FINALIZATION_PATH, REPORT_PATH, WORKFLOW_PATH):
        if not path.is_file():
            errors.append(f"missing Phase 26 finalization file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    if sha256_file(CANDIDATE_PATH) != EXPECTED_CANDIDATE_SHA256:
        errors.append("Phase 26 candidate record digest changed after merge")

    finalization = load_json(FINALIZATION_PATH)
    for key, value in {
        "contract": "principia-offline-consequence-plan-review-request-packet-assurance-finalization/0.1",
        "phase": 26,
        "state": "offline-consequence-plan-review-request-packet-assurance-validated",
        "mode": "offline-consequence-plan-review-request-packet-assurance",
        "fixture_kind": "bounded-synthetic",
        "decision": "review-request-packets-assured-no-dispatch",
        "live": False,
        "next_gate": "offline-consequence-plan-review-response-intake-readiness-candidate",
        "live_activation_permitted": False,
        "real_authorization_claimed": False,
    }.items():
        if finalization.get(key) != value:
            errors.append(f"Phase 26 finalization {key} must equal {value}")

    if finalization.get("candidate_record") != {
        "path": "release/phase-26-offline-consequence-plan-review-request-packet-assurance.json",
        "sha256": EXPECTED_CANDIDATE_SHA256,
    }:
        errors.append("Phase 26 finalization candidate record pin is invalid")

    principia = finalization.get("principia")
    expected_principia = {
        "repository": "Rhodan-lab/principle-to-system",
        "pull_request": 43,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "merge_commit": EXPECTED_MERGE,
    }
    if not isinstance(principia, Mapping) or any(
        principia.get(key) != value for key, value in expected_principia.items()
    ):
        errors.append("Phase 26 Principia provenance is invalid")

    if finalization.get("validation") != {
        "applicable_workflows": 20,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "status": "success",
    }:
        errors.append("Phase 26 exact-head validation provenance is invalid")

    expected_result = {
        "assured_packet_count": 2,
        "blank_question_response_count": 6,
        "effective_hold_count": 0,
        "failed_assurance_count": 0,
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
        errors.append("Phase 26 finalization result is invalid")

    authority = finalization.get("authority")
    if not isinstance(authority, Mapping):
        errors.append("Phase 26 authority record is missing")
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
                errors.append(f"Phase 26 finalization must keep {key}=false")
        for key in ("local_assurance_permitted", "local_packet_preparation_permitted"):
            if authority.get(key) is not True:
                errors.append(f"Phase 26 finalization must keep {key}=true")
        if authority.get("status_inheritance") != "prohibited":
            errors.append("Phase 26 finalization must prohibit status inheritance")

    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "**Phase 26 — Offline Consequence-Plan Review-Request Packet Assurance merged and validated through PR #43.**",
        "Phase 26 state: **offline-consequence-plan-review-request-packet-assurance-validated**",
        "| 26 | Offline consequence-plan review-request packet assurance | Merged and validated through PR #43 |",
        f"Phase 26 exact candidate validation passed at `{EXPECTED_CANDIDATE_HEAD}`",
        f"PR #43 was merged into `main` at commit `{EXPECTED_MERGE}`",
        "release/phase-26-postmerge.json",
        "Historical Phase 26 candidate marker: `exact-head validation pending`",
        "offline-consequence-plan-review-response-intake-readiness-candidate",
        "review-request-packets-assured-no-dispatch",
        "packet-assured-local-no-dispatch",
        "assured_packet_count: 2",
        "packet_dispatch_count: 0",
        "human_gate_pending_count: 8",
        "review_started_count: 0",
        "real_authorization_claimed: false",
        "Atlas remains unchanged by Principia Phase 26.",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 26 finalization marker: {marker}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        "# Phase 26 — Offline Consequence-Plan Review-Request Packet Assurance",
        f"> Exact tested head: `{EXPECTED_CANDIDATE_HEAD}`",
        f"> Merge commit: `{EXPECTED_MERGE}`",
        "> Final state: `offline-consequence-plan-review-request-packet-assurance-validated`",
        "release/phase-26-postmerge.json",
        "2 assured packets",
        "8 human gates still pending",
        "review-request-packets-assured-no-dispatch",
        "> Live: `false`",
    ):
        if marker not in report:
            errors.append(f"Phase 26 report missing finalization marker: {marker}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/finalize-phase-26-record",
        "scripts/validate_phase26_postmerge_record.py",
        "release/phase-26-postmerge.json",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"Phase 26 workflow missing finalization marker: {marker}")
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
            errors.append(f"Phase 26 workflow contains forbidden token: {forbidden}")

    if errors:
        return fail(errors)
    print(
        "Phase 26 post-merge record passed: PR #43 and exact candidate head pinned, "
        "two packets assured, eight human gates pending, and dispatch and review disabled."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
