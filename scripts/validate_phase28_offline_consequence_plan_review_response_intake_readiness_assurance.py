#!/usr/bin/env python3
"""Validate Phase 28 response-intake readiness assurance evidence."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "release/phase-28-offline-consequence-plan-review-response-intake-readiness-assurance.json"
sys.path.insert(0, str(ROOT))
from scripts.generate_phase28_offline_consequence_plan_review_response_intake_readiness_assurance import (  # noqa: E402
    AUTHORITY, CHECK_NAMES, DECISION, EXPECTED, MODE, MUTATIONS, NEXT_GATE, STATE,
    build, doc_sha, validate_assurance, verify_sources,
)

def fail(errors: list[str]) -> int:
    print("Phase 28 validation errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1

def main() -> int:
    errors = verify_sources()
    if not OUT.is_file():
        return fail(errors + ["Phase 28 candidate missing"])
    try:
        actual: dict[str, Any] = json.loads(OUT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail(errors + [f"Phase 28 candidate unreadable: {exc}"])
    expected = build()
    if actual != expected:
        errors.append("Phase 28 candidate differs from deterministic build")
    if actual.get("phase") != 28 or actual.get("mode") != MODE or actual.get("state") != STATE:
        errors.append("Phase 28 identity drift")
    if actual.get("decision") != DECISION or actual.get("next_gate") != NEXT_GATE:
        errors.append("Phase 28 decision or next-gate drift")
    if actual.get("authority") != AUTHORITY:
        errors.append("Phase 28 authority drift")
    if actual.get("live") is not False or actual.get("live_activation_permitted") is not False:
        errors.append("Phase 28 must remain non-live")
    assurances = actual.get("assurances", [])
    if len(assurances) != len(EXPECTED):
        errors.append("Phase 28 assurance count drift")
    for assurance in assurances:
        for error in validate_assurance(assurance):
            errors.append(f"{assurance.get('intake_readiness_assurance_id')}: {error}")
    result = actual.get("result", {})
    for key in (
        "failed_assurance_count", "human_gate_satisfied_count", "response_accepted_count",
        "response_intake_authorized_count", "response_quarantined_count", "response_received_count",
        "response_rejected_count", "response_validated_count", "review_completed_count",
        "review_started_count", "reviewer_contact_count", "reviewer_identity_count",
        "status_change_count",
    ):
        if result.get(key) != 0:
            errors.append(f"Phase 28 result must keep {key}=0")
    if result.get("assured_readiness_record_count") != 2 or result.get("assurance_check_count") != 40:
        errors.append("Phase 28 assurance totals drift")
    if result.get("human_gate_pending_count") != 8 or result.get("blank_question_slot_count") != 6:
        errors.append("Phase 28 pending-gate or blank-question totals drift")
    ledger = actual.get("ledger", {})
    entries = ledger.get("entries", [])
    previous = None
    for sequence, wrapper in enumerate(entries, start=1):
        entry = wrapper.get("entry", {})
        if entry.get("sequence") != sequence or entry.get("previous_entry_sha256") != previous:
            errors.append("Phase 28 ledger chain drift")
        digest = doc_sha(entry)
        if wrapper.get("entry_sha256") != digest:
            errors.append("Phase 28 ledger entry digest drift")
        previous = digest
    if ledger.get("head_sequence") != 2 or ledger.get("head_sha256") != previous:
        errors.append("Phase 28 ledger head drift")
    checkpoint = actual.get("checkpoint", {})
    if checkpoint.get("ledger_sha256") != doc_sha(ledger):
        errors.append("Phase 28 checkpoint ledger binding drift")
    recovery = actual.get("recovery", {})
    if recovery.get("scenario_count") != len(MUTATIONS) + 1:
        errors.append("Phase 28 recovery scenario count drift")
    if recovery.get("accepted_count") != 1 or recovery.get("rejected_count") != len(MUTATIONS):
        errors.append("Phase 28 recovery summary drift")
    if errors:
        return fail(sorted(set(errors)))
    raw = OUT.read_bytes()
    print(
        "Phase 28 candidate passed: "
        f"{len(raw)} bytes, sha256={hashlib.sha256(raw).hexdigest()}, "
        "2 readiness records assured, 40 checks passing, 0 responses received."
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
