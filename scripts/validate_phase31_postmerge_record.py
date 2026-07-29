#!/usr/bin/env python3
"""Validate the finalized Phase 31 response-envelope validation-readiness record."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
CANDIDATE_PATH = ROOT / "release/phase-31-offline-consequence-plan-review-response-intake-envelope-validation-readiness.json"
FINALIZATION_PATH = ROOT / "release/phase-31-postmerge.json"
REPORT_PATH = ROOT / "reports/phase-31-offline-consequence-plan-review-response-intake-envelope-validation-readiness.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-31-offline-consequence-plan-review-response-intake-envelope-validation-readiness.yml"
EXPECTED_HEAD = "7d281af68d74404bc3f00d2bee8f368165433cb0"
EXPECTED_MERGE = "eac5429eaa99f7902b338d87a8b6b9c981d5d1a3"
EXPECTED_SHA = "a764c145481d1ddba59df45dd29042636547ced8f308fbaf3f22b6ce79c0473c"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path)
    return value

def fail(errors: list[str]) -> int:
    print("Phase 31 post-merge record errors:", file=sys.stderr)
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
        "contract": "principia-offline-consequence-plan-review-response-intake-envelope-validation-readiness-finalization/0.1",
        "phase": 31,
        "state": "offline-consequence-plan-review-response-intake-envelope-validation-readiness-validated",
        "mode": "offline-consequence-plan-review-response-intake-envelope-validation-readiness",
        "fixture_kind": "bounded-synthetic",
        "decision": "response-intake-envelope-validation-readiness-recorded-no-envelope-received",
        "live": False,
        "next_gate": "offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance-candidate",
        "live_activation_permitted": False,
        "real_authorization_claimed": False,
    }
    for key, value in expected.items():
        if finalization.get(key) != value:
            errors.append(f"{key} drift")

    if finalization.get("candidate_record") != {
        "path": "release/phase-31-offline-consequence-plan-review-response-intake-envelope-validation-readiness.json",
        "sha256": EXPECTED_SHA,
    }:
        errors.append("candidate pin")

    if finalization.get("principia") != {
        "repository": "Rhodan-lab/principle-to-system",
        "pull_request": 53,
        "candidate_head_commit": EXPECTED_HEAD,
        "merge_commit": EXPECTED_MERGE,
    }:
        errors.append("provenance")

    if finalization.get("validation") != {
        "applicable_workflows": 25,
        "candidate_head_commit": EXPECTED_HEAD,
        "status": "success",
    }:
        errors.append("validation provenance")

    expected_result = {
        "blank_validation_receipt_count": 2,
        "blank_validation_receipt_field_count": 20,
        "disposition_selected_count": 0,
        "envelope_readiness_assurance_record_count": 2,
        "failed_control_count": 0,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
        "integrity_failure_count": 0,
        "integrity_rule_count": 20,
        "possible_disposition_count": 6,
        "quarantine_reason_code_count": 20,
        "quarantine_record_count": 0,
        "real_authorization_claimed": False,
        "response_accepted_count": 0,
        "response_envelope_created_count": 0,
        "response_envelope_processed_count": 0,
        "response_envelope_received_count": 0,
        "response_intake_authorized_count": 0,
        "response_quarantined_count": 0,
        "response_received_count": 0,
        "response_rejected_count": 0,
        "response_validated_count": 0,
        "review_completed_count": 0,
        "review_started_count": 0,
        "reviewer_contact_count": 0,
        "reviewer_identity_count": 0,
        "status_change_count": 0,
        "validation_completed_count": 0,
        "validation_control_count": 36,
        "validation_execution_authorized_count": 0,
        "validation_profile_count": 2,
        "validation_readiness_record_count": 2,
        "validation_result_recorded_count": 0,
        "validation_run_count": 0,
        "validation_stage_count": 16,
        "validation_started_count": 0,
    }
    if finalization.get("result") != expected_result:
        errors.append("result drift")

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
            "response_envelope_creation_permitted",
            "response_envelope_processing_authorized",
            "response_envelope_validation_execution_authorized",
            "response_envelope_validation_result_recording_permitted",
            "response_intake_authorized",
            "response_quarantine_execution_authorized",
            "response_receipt_permitted",
            "response_validation_authorized",
            "review_execution_authorized",
            "review_request_dispatch_authorized",
            "reviewer_contact_permitted",
        ):
            if authority.get(key) is not False:
                errors.append(f"authority {key}")
        if authority.get("local_response_envelope_validation_readiness_permitted") is not True:
            errors.append("local validation readiness disabled")
        if authority.get("status_inheritance") != "prohibited":
            errors.append("status inheritance")

    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "**Phase 31 — Offline Consequence-Plan Review-Response Intake Envelope Validation Readiness merged and validated through PR #53.**",
        "Phase 31 state: **offline-consequence-plan-review-response-intake-envelope-validation-readiness-validated**",
        "| 31 | Offline consequence-plan review-response intake envelope validation readiness | Merged and validated through PR #53 |",
        f"Phase 31 exact candidate validation passed at `{EXPECTED_HEAD}`",
        f"PR #53 was merged into `main` at commit `{EXPECTED_MERGE}`",
        "release/phase-31-postmerge.json",
        "Historical Phase 31 candidate marker: `exact-head validation pending`",
        "offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance-candidate",
        "response-intake-envelope-validation-readiness-recorded-no-envelope-received",
        "response-envelope-validation-controls-ready-no-envelope",
        "validation_readiness_record_count: 2",
        "validation_control_count: 36",
        "validation_run_count: 0",
        "human_gate_pending_count: 8",
        "real_authorization_claimed: false",
        "Atlas remains unchanged by Principia Phase 31.",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"state marker {marker}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        "# Phase 31 — Offline Consequence-Plan Review-Response Intake Envelope Validation Readiness",
        f"> Exact tested head: `{EXPECTED_HEAD}`",
        f"> Merge commit: `{EXPECTED_MERGE}`",
        "> Final state: `offline-consequence-plan-review-response-intake-envelope-validation-readiness-validated`",
        "release/phase-31-postmerge.json",
        "2 validation-readiness records",
        "36 inactive controls",
        "110 deterministic scenarios",
        "response-intake-envelope-validation-readiness-recorded-no-envelope-received",
        "> Live: `false`",
    ):
        if marker not in report:
            errors.append(f"report marker {marker}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/finalize-phase-31-record",
        "scripts/validate_phase31_postmerge_record.py",
        "release/phase-31-postmerge.json",
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
        "Phase 31 post-merge record passed: exact candidate and PR pinned, "
        "two validation profiles ready, 36 controls inactive, zero envelopes received."
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
