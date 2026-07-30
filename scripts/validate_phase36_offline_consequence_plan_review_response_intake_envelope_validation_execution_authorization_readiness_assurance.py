#!/usr/bin/env python3
"""Validate the deterministic Principia Phase 36 authorization-readiness assurance record."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from typing import Any
import generate_phase36_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_readiness_assurance as generator

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "release/phase-36-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance.json"
EXPECTED_SHA = "c90abcedeffcc66ff1d1e1d615e03cc5e002a76177d3ab8a0754543c4ad1677e"

def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(path)
    return value

def validate_document(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = generator.build_document()
    scalar_keys = ("contract","id","phase","mode","state","decision","fixture_kind","live","live_activation_permitted","real_authorization_claimed","source_phase35","next_gate","validation")
    for key in scalar_keys:
        if document.get(key) != expected.get(key):
            errors.append(f"{key} drift")
    assurances = document.get("assurances")
    if not isinstance(assurances, list) or len(assurances) != 2:
        errors.append("assurance count drift")
    else:
        for index, (actual, wanted) in enumerate(zip(assurances, expected["assurances"]), start=1):
            if actual != wanted:
                errors.append(f"assurance {index} drift")
            checks = actual.get("assurance_checks") if isinstance(actual, dict) else None
            if not isinstance(checks, dict) or len(checks) != 50 or not all(value is True for value in checks.values()):
                errors.append(f"assurance {index} checks failed")
    if document.get("ledger") != expected["ledger"]:
        errors.append("ledger drift")
    if document.get("checkpoint") != expected["checkpoint"]:
        errors.append("checkpoint drift")
    if document.get("result") != expected["result"]:
        errors.append("result drift")
    if document.get("authority") != expected["authority"]:
        errors.append("authority drift")
    if document.get("recovery") != expected["recovery"]:
        errors.append("recovery drift")
    result = document.get("result", {})
    zero_fields = (
        "failed_assurance_count","authorization_requirement_evaluated_count","approval_received_count",
        "approval_evidence_recorded_count","human_gate_satisfied_count","authorization_candidate_created_count",
        "authorization_decision_recorded_count","authorization_granted_count","authorization_revoked_count",
        "authorization_expired_count","authorization_officer_identity_count","authorization_scope_recorded_count",
        "authorization_token_issued_count","execution_authorization_present_count","execution_ticket_issued_count",
        "execution_run_count","execution_started_count","execution_completed_count","validation_result_recorded_count",
        "disposition_selected_count","response_envelope_created_count","response_envelope_received_count",
        "response_envelope_processed_count","response_received_count","response_validated_count",
        "response_accepted_count","response_rejected_count","response_quarantined_count","reviewer_identity_count",
        "reviewer_contact_count","review_started_count","review_completed_count","status_change_count"
    )
    for field in zero_fields:
        if result.get(field) != 0:
            errors.append(f"nonzero result: {field}")
    authority = document.get("authority", {})
    allowed_true = {"local_response_envelope_validation_execution_authorization_readiness_assurance_permitted"}
    for key, value in authority.items():
        if key == "status_inheritance":
            if value != "prohibited":
                errors.append("status inheritance enabled")
        elif key in allowed_true:
            if value is not True:
                errors.append(f"assurance authority lost: {key}")
        elif value is not False:
            errors.append(f"forbidden authority enabled: {key}")
    if document.get("live") is not False or document.get("real_authorization_claimed") is not False:
        errors.append("live or authorization claim enabled")
    return errors

def validate() -> list[str]:
    errors: list[str] = []
    if not MANIFEST.is_file():
        return ["Phase 36 manifest missing"]
    if hashlib.sha256(MANIFEST.read_bytes()).hexdigest() != EXPECTED_SHA:
        errors.append("Phase 36 manifest digest drift")
    try:
        generator.validate_sources()
    except Exception as exc:
        errors.append(str(exc))
    errors.extend(validate_document(load(MANIFEST)))
    return errors

def main() -> int:
    errors = validate()
    if errors:
        print("Phase 36 validation errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Phase 36 validation passed: 2 authorization-readiness assurances, 100 checks, 0 grants.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
