#!/usr/bin/env python3
"""Validate the finalized Phase 28 response-intake readiness assurance record."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
CANDIDATE_PATH = ROOT / "release/phase-28-offline-consequence-plan-review-response-intake-readiness-assurance.json"
FINALIZATION_PATH = ROOT / "release/phase-28-postmerge.json"
REPORT_PATH = ROOT / "reports/phase-28-offline-consequence-plan-review-response-intake-readiness-assurance.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-28-offline-consequence-plan-review-response-intake-readiness-assurance.yml"
EXPECTED_HEAD = "14a278af023f6cc623ed42cc50f661242b1c78a3"
EXPECTED_MERGE = "90430186a9f2842fe41dfb5df4cb3bad6f8e5611"
EXPECTED_SHA = "ce21c69cd246db67d5b03d2ac84962789ae5ff78ace4fd1d5b90b79cf6301fda"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path)
    return value


def fail(errors: list[str]) -> int:
    print("Phase 28 post-merge record errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


def main() -> int:
    errors: list[str] = []
    for path in (STATE_PATH, CANDIDATE_PATH, FINALIZATION_PATH, REPORT_PATH, WORKFLOW_PATH):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)
    if sha(CANDIDATE_PATH) != EXPECTED_SHA:
        errors.append("candidate digest changed after merge")
    finalization = load(FINALIZATION_PATH)
    expected = {
        "contract": "principia-offline-consequence-plan-review-response-intake-readiness-assurance-finalization/0.1",
        "phase": 28,
        "state": "offline-consequence-plan-review-response-intake-readiness-assurance-validated",
        "mode": "offline-consequence-plan-review-response-intake-readiness-assurance",
        "fixture_kind": "bounded-synthetic",
        "decision": "response-intake-readiness-assured-no-response-received",
        "live": False,
        "next_gate": "offline-consequence-plan-review-response-intake-envelope-readiness-candidate",
        "live_activation_permitted": False,
        "real_authorization_claimed": False,
    }
    for key, value in expected.items():
        if finalization.get(key) != value:
            errors.append(f"{key} drift")
    if finalization.get("candidate_record") != {
        "path": "release/phase-28-offline-consequence-plan-review-response-intake-readiness-assurance.json",
        "sha256": EXPECTED_SHA,
    }:
        errors.append("candidate pin")
    if finalization.get("principia") != {
        "repository": "Rhodan-lab/principle-to-system",
        "pull_request": 47,
        "candidate_head_commit": EXPECTED_HEAD,
        "merge_commit": EXPECTED_MERGE,
    }:
        errors.append("provenance")
    if finalization.get("validation") != {
        "applicable_workflows": 22,
        "candidate_head_commit": EXPECTED_HEAD,
        "status": "success",
    }:
        errors.append("validation provenance")
    result = finalization.get("result", {})
    expected_result = {
        "assurance_check_count": 40,
        "assured_readiness_record_count": 2,
        "blank_question_slot_count": 6,
        "failed_assurance_count": 0,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
        "intake_readiness_record_count": 2,
        "required_field_count": 30,
        "response_accepted_count": 0,
        "response_intake_authorized_count": 0,
        "response_quarantined_count": 0,
        "response_received_count": 0,
        "response_rejected_count": 0,
        "response_schema_count": 2,
        "response_schema_section_count": 12,
        "response_validated_count": 0,
        "review_completed_count": 0,
        "review_started_count": 0,
        "reviewer_contact_count": 0,
        "reviewer_identity_count": 0,
        "status_change_count": 0,
        "real_authorization_claimed": False,
    }
    for key, value in expected_result.items():
        if result.get(key) != value:
            errors.append(f"result {key}")
    authority = finalization.get("authority")
    if not isinstance(authority, Mapping):
        errors.append("authority missing")
    else:
        for key in (
            "atlas_call_permitted",
            "automatic_release_action",
            "automatic_status_change",
            "external_delivery_permitted",
            "external_network_required",
            "human_authorization_claimed",
            "repository_mutation",
            "response_intake_authorized",
            "response_receipt_permitted",
            "response_validation_authorized",
            "review_execution_authorized",
            "review_request_dispatch_authorized",
            "reviewer_contact_permitted",
        ):
            if authority.get(key) is not False:
                errors.append(f"authority {key}")
        if authority.get("local_response_intake_assurance_permitted") is not True:
            errors.append("local assurance disabled")
        if authority.get("status_inheritance") != "prohibited":
            errors.append("status inheritance")
    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "**Phase 28 — Offline Consequence-Plan Review-Response Intake Readiness Assurance merged and validated through PR #47.**",
        "Phase 28 state: **offline-consequence-plan-review-response-intake-readiness-assurance-validated**",
        "| 28 | Offline consequence-plan review-response intake readiness assurance | Merged and validated through PR #47 |",
        f"Phase 28 exact candidate validation passed at `{EXPECTED_HEAD}`",
        f"PR #47 was merged into `main` at commit `{EXPECTED_MERGE}`",
        "release/phase-28-postmerge.json",
        "Historical Phase 28 candidate marker: `exact-head validation pending`",
        "offline-consequence-plan-review-response-intake-envelope-readiness-candidate",
        "response-intake-readiness-assured-no-response-received",
        "response-intake-readiness-assured-no-response",
        "assured_readiness_record_count: 2",
        "assurance_check_count: 40",
        "response_received_count: 0",
        "human_gate_pending_count: 8",
        "real_authorization_claimed: false",
        "Atlas remains unchanged by Principia Phase 28.",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"state marker {marker}")
    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        "# Phase 28 — Offline Consequence-Plan Review-Response Intake Readiness Assurance",
        f"> Exact tested head: `{EXPECTED_HEAD}`",
        f"> Merge commit: `{EXPECTED_MERGE}`",
        "> Final state: `offline-consequence-plan-review-response-intake-readiness-assurance-validated`",
        "release/phase-28-postmerge.json",
        "2 assured readiness records",
        "40 passing invariant checks",
        "8 pending human gates",
        "response-intake-readiness-assured-no-response-received",
        "> Live: `false`",
    ):
        if marker not in report:
            errors.append(f"report marker {marker}")
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/finalize-phase-28-record",
        "scripts/validate_phase28_postmerge_record.py",
        "release/phase-28-postmerge.json",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"workflow marker {marker}")
    for forbidden in (
        "contents: write",
        "git push",
        "git commit",
        "pull_request_target",
        "repository: Rhodan-lab/Atlas",
        "curl ",
        "wget ",
    ):
        if forbidden in workflow:
            errors.append(f"forbidden {forbidden}")
    if errors:
        return fail(sorted(set(errors)))
    print(
        "Phase 28 post-merge record passed: exact candidate and PR pinned, "
        "two readiness records assured, 40 checks passing, zero responses received."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
