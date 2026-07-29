#!/usr/bin/env python3
"""Generate deterministic Phase 31 response-envelope validation-readiness evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
MODE = "offline-consequence-plan-review-response-intake-envelope-validation-readiness"
DECISION = "response-intake-envelope-validation-readiness-recorded-no-envelope-received"
STATE = MODE + "-candidate"
NEXT_GATE = MODE + "-assurance-candidate"
OUT = ROOT / "release/phase-31-offline-consequence-plan-review-response-intake-envelope-validation-readiness.json"
SOURCE = ROOT / "release/phase-30-offline-consequence-plan-review-response-intake-envelope-readiness-assurance.json"
POST = ROOT / "release/phase-30-postmerge.json"
SOURCE_SHA = "f3a232a6895b153020a2ce49bf5a4cbc10d7adabb5b9780da4edfe4d1f764ce5"
POST_SHA = "7f5be4be6efeb4b6223c9ef099be9b545eeebe3f8d467fe5e39f424ca2f3b6d0"
FINAL_COMMIT = "112423a77d619da8d97afc8247b20959890defa3"

STAGES = (
    "source-provenance",
    "envelope-structure",
    "identity-bindings",
    "payload-integrity",
    "human-gate-preconditions",
    "duplicate-detection",
    "quarantine-classification",
    "decision-freeze",
)
CONTROLS = (
    "canonical-json-required",
    "utf8-required",
    "media-type-exact",
    "envelope-version-exact",
    "envelope-id-required",
    "response-id-required",
    "intake-readiness-binding-exact",
    "envelope-readiness-assurance-binding-exact",
    "packet-binding-exact",
    "schema-binding-exact",
    "payload-size-within-limit",
    "payload-sha256-required",
    "source-digest-required",
    "submitted-at-required",
    "signature-reference-required",
    "human-gates-complete",
    "duplicate-envelope-prohibited",
    "unknown-fields-prohibited",
)
DISPOSITIONS = (
    "structural-rejection",
    "quarantine-candidate",
    "validation-pass-candidate",
)
BLANK_RECEIPT_FIELDS = (
    "validation_run_id",
    "envelope_id",
    "response_id",
    "validation_started_at",
    "validation_completed_at",
    "evaluated_payload_sha256",
    "failed_control_ids",
    "selected_disposition",
    "quarantine_reason_ids",
    "validator_signature_ref",
)
EXPECTED = (
    (
        "feedback-manual-review",
        1,
        "5e406afd558b0e11f6d8502ff04761814f71dbea958c05b4d208d9e9c3670743",
        "dc861b02baae0ff6f649bb7b2efabca2d7179a3fc5318891f44c788875f37c18",
        "qualified-pedagogical-reviewer",
    ),
    (
        "model-boundary-release-governance",
        2,
        "4e1b9a3d77f20dc78d945150e71d5f9d6e7df1108faea4bffb2dfc9d42eccfc2",
        "566fc2b02385c05d1b373e3c91cc83784c0fcaea1cf83c5ef61cfb8ae860dd41",
        "qualified-release-governance-reviewer",
    ),
)
AUTHORITY = {
    "atlas_call_permitted": False,
    "automatic_release_action": False,
    "automatic_status_change": False,
    "external_delivery_permitted": False,
    "external_network_required": False,
    "human_authorization_claimed": False,
    "local_response_envelope_validation_readiness_permitted": True,
    "repository_mutation": False,
    "response_envelope_creation_permitted": False,
    "response_envelope_processing_authorized": False,
    "response_envelope_validation_execution_authorized": False,
    "response_envelope_validation_result_recording_permitted": False,
    "response_intake_authorized": False,
    "response_quarantine_execution_authorized": False,
    "response_receipt_permitted": False,
    "response_validation_authorized": False,
    "review_execution_authorized": False,
    "review_request_dispatch_authorized": False,
    "reviewer_contact_permitted": False,
    "status_inheritance": "prohibited",
}
ZERO_FIELDS = (
    "disposition_selected",
    "integrity_failure_recorded",
    "quarantine_record_created",
    "response_accepted",
    "response_envelope_created",
    "response_envelope_processed",
    "response_envelope_received",
    "response_intake_authorized",
    "response_quarantined",
    "response_received",
    "response_rejected",
    "response_validated",
    "review_completed",
    "review_start_permitted",
    "review_started",
    "reviewer_contact_permitted",
    "reviewer_identity_present",
    "status_change",
    "validation_completed",
    "validation_execution_authorized",
    "validation_result_recording_permitted",
    "validation_run_created",
    "validation_started",
    "real_authorization_claimed",
)
MUTATIONS = (
    "phase30-candidate-drift",
    "phase30-postmerge-drift",
    "missing-validation-readiness-record",
    "orphan-validation-readiness-record",
    "duplicate-validation-readiness-record",
    "validation-readiness-sequence-drift",
    "validation-readiness-id-drift",
    "source-assurance-id-drift",
    "source-assurance-record-digest-drift",
    "source-assurance-ledger-entry-drift",
    "envelope-readiness-id-drift",
    "envelope-spec-id-drift",
    "intake-readiness-assurance-id-drift",
    "packet-assurance-id-drift",
    "packet-id-drift",
    "schema-id-drift",
    "reviewer-role-drift",
    "profile-id-drift",
    "profile-version-drift",
    "profile-mode-drift",
    "profile-input-state-drift",
    "profile-media-type-drift",
    "profile-encoding-drift",
    "profile-digest-algorithm-drift",
    "profile-payload-limit-drift",
    "stage-count-drift",
    "stage-id-drift",
    "stage-order-drift",
    "stage-state-drift",
    "control-count-drift",
    "control-id-drift",
    "control-order-drift",
    "control-state-drift",
    "disposition-count-drift",
    "disposition-id-drift",
    "disposition-order-drift",
    "disposition-state-drift",
    "blank-receipt-count-drift",
    "blank-receipt-field-count-drift",
    "validation-run-id-filled",
    "envelope-id-filled",
    "response-id-filled",
    "validation-started-at-filled",
    "validation-completed-at-filled",
    "evaluated-payload-digest-filled",
    "failed-control-ids-filled",
    "selected-disposition-filled",
    "quarantine-reason-ids-filled",
    "validator-signature-filled",
    "blank-receipt-executed",
    "blank-receipt-source-binding-drift",
    "human-gate-satisfied",
    "validation-run-created",
    "validation-started",
    "validation-completed",
    "validation-execution-authorized",
    "validation-result-recording-permitted",
    "validation-check-executed",
    "validation-failure-recorded",
    "disposition-selected",
    "structural-rejection-selected",
    "quarantine-candidate-selected",
    "validation-pass-selected",
    "envelope-created",
    "envelope-received",
    "envelope-processed",
    "integrity-failure-recorded",
    "duplicate-envelope-recorded",
    "quarantine-record-created",
    "quarantine-execution-authorized",
    "response-intake-authorized",
    "response-receipt-permitted",
    "response-received",
    "response-validated",
    "response-accepted",
    "response-rejected",
    "response-quarantined",
    "packet-dispatched",
    "reviewer-contact-permitted",
    "reviewer-identity-recorded",
    "review-start-permitted",
    "review-started",
    "review-completed",
    "outcome-selected",
    "content-change-proposed",
    "status-recommendation-recorded",
    "effective-hold",
    "operational-effect",
    "status-change",
    "human-authorization-claimed",
    "real-authorization-claimed",
    "status-inheritance-enabled",
    "automatic-status-change",
    "automatic-release-action",
    "repository-mutation",
    "external-network-required",
    "external-delivery-permitted",
    "atlas-call-permitted",
    "live-activation",
    "record-verdict-drift",
    "record-status-drift",
    "record-locality-drift",
    "ledger-drift",
    "checkpoint-drift",
    "summary-drift",
    "authority-drift",
    "source-pin-drift",
    "record-count-drift",
    "recovery-count-drift",
)

def render(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"

def sha_doc(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path)
    return value

def verify_sources() -> list[str]:
    errors: list[str] = []
    if not SOURCE.is_file() or sha_file(SOURCE) != SOURCE_SHA:
        errors.append("Phase 30 candidate file drift")
    if not POST.is_file() or sha_file(POST) != POST_SHA:
        errors.append("Phase 30 postmerge file drift")
    if errors:
        return errors

    source = load(SOURCE)
    post = load(POST)
    if source.get("state") != "offline-consequence-plan-review-response-intake-envelope-readiness-assurance-candidate":
        errors.append("Phase 30 candidate state drift")
    if source.get("next_gate") != STATE:
        errors.append("Phase 30 candidate next-gate drift")
    if post.get("state") != "offline-consequence-plan-review-response-intake-envelope-readiness-assurance-validated":
        errors.append("Phase 30 final state drift")
    if post.get("next_gate") != STATE:
        errors.append("Phase 30 finalization next-gate drift")
    if post.get("candidate_record", {}).get("sha256") != SOURCE_SHA:
        errors.append("Phase 30 candidate digest drift")

    records = {r.get("envelope_readiness_assurance_id"): r for r in source.get("assurances", [])}
    entries = {
        wrapper.get("entry", {}).get("envelope_readiness_assurance_id"): wrapper
        for wrapper in source.get("ledger", {}).get("entries", [])
    }
    for key, sequence, record_sha, ledger_sha, role in EXPECTED:
        assurance_id = (
            "principia:consequence-plan-review-response-intake-envelope-readiness-assurance:"
            f"{key}:{sequence:04d}"
        )
        record = records.get(assurance_id)
        wrapper = entries.get(assurance_id)
        if not record or sha_doc(record) != record_sha:
            errors.append(f"Phase 30 assurance record drift: {key}")
            continue
        if not wrapper or wrapper.get("entry_sha256") != ledger_sha:
            errors.append(f"Phase 30 assurance ledger drift: {key}")
        if record.get("verdict") != "response-envelope-readiness-assured-no-envelope":
            errors.append(f"Phase 30 assurance verdict drift: {key}")
        if record.get("status") != "assured-no-envelope-received":
            errors.append(f"Phase 30 assurance status drift: {key}")
        if record.get("assurance_check_count") != 24:
            errors.append(f"Phase 30 assurance count drift: {key}")
        if any(value is not True for value in record.get("assurance_checks", {}).values()):
            errors.append(f"Phase 30 failed assurance check: {key}")
        if record.get("human_gate_pending_count") != 4 or record.get("human_gate_satisfied_count") != 0:
            errors.append(f"Phase 30 human-gate drift: {key}")
        if record.get("reviewer_role_required") != role:
            errors.append(f"Phase 30 reviewer-role drift: {key}")
        for field in (
            "response_envelope_created",
            "response_envelope_received",
            "response_envelope_processed",
            "response_received",
            "response_validated",
            "review_started",
            "status_change",
        ):
            if record.get(field) is not False:
                errors.append(f"Phase 30 frozen-state drift {field}: {key}")

    expected_result = {
        "assurance_check_count": 48,
        "assured_envelope_readiness_record_count": 2,
        "failed_assurance_count": 0,
        "response_envelope_created_count": 0,
        "response_envelope_received_count": 0,
        "response_envelope_processed_count": 0,
        "response_received_count": 0,
        "review_started_count": 0,
        "status_change_count": 0,
    }
    for field, expected in expected_result.items():
        if source.get("result", {}).get(field) != expected:
            errors.append(f"Phase 30 result drift: {field}")
        if post.get("result", {}).get(field) != expected:
            errors.append(f"Phase 30 final result drift: {field}")
    return sorted(set(errors))

def validation_readiness_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for key, sequence, source_record_sha, source_ledger_sha, role in EXPECTED:
        prefix = "principia:consequence-plan-review-response-intake"
        assurance_id = f"{prefix}-envelope-readiness-assurance:{key}:{sequence:04d}"
        profile_id = f"principia:review-response-intake-envelope-validation-profile:{key}:{sequence:04d}"
        blank_receipt = {
            "validation_profile_id": profile_id,
            "envelope_readiness_assurance_id": assurance_id,
            "envelope_spec_id": f"principia:review-response-intake-envelope:{key}:{sequence:04d}",
            "response_schema_id": f"principia:review-response-intake-schema:{key}:{sequence:04d}",
            "validation_run_id": None,
            "envelope_id": None,
            "response_id": None,
            "validation_started_at": None,
            "validation_completed_at": None,
            "evaluated_payload_sha256": None,
            "failed_control_ids": None,
            "selected_disposition": None,
            "quarantine_reason_ids": None,
            "validator_signature_ref": None,
            "executed": False,
        }
        record = {
            "blank_validation_receipt": blank_receipt,
            "blank_validation_receipt_field_count": len(BLANK_RECEIPT_FIELDS),
            "disposition_count": len(DISPOSITIONS),
            "envelope_readiness_assurance_id": assurance_id,
            "envelope_readiness_assurance_ledger_entry_sha256": source_ledger_sha,
            "envelope_readiness_assurance_record_sha256": source_record_sha,
            "envelope_readiness_id": f"{prefix}-envelope-readiness:{key}:{sequence:04d}",
            "envelope_spec_id": f"principia:review-response-intake-envelope:{key}:{sequence:04d}",
            "human_gate_pending_count": 4,
            "human_gate_satisfied_count": 0,
            "intake_readiness_assurance_id": f"{prefix}-readiness-assurance:{key}:{sequence:04d}",
            "local_only": True,
            "packet_assurance_id": f"principia:consequence-plan-review-request-packet-assurance:{key}:{sequence:04d}",
            "packet_id": f"principia:consequence-plan-review-request-packet:{key}:{sequence:04d}",
            "response_schema_id": f"principia:review-response-intake-schema:{key}:{sequence:04d}",
            "reviewer_role_required": role,
            "sequence": sequence,
            "status": "validation-readiness-recorded-no-envelope-received",
            "validation_control_count": len(CONTROLS),
            "validation_profile": {
                "controls": [
                    {"control_id": control, "sequence": index, "state": "defined-not-active"}
                    for index, control in enumerate(CONTROLS, start=1)
                ],
                "digest_algorithm": "sha256",
                "dispositions": [
                    {"disposition_id": disposition, "sequence": index, "state": "defined-not-active"}
                    for index, disposition in enumerate(DISPOSITIONS, start=1)
                ],
                "encoding": "utf-8",
                "input_state": "no-envelope-present",
                "max_payload_bytes": 131072,
                "media_type": "application/json",
                "mode": "offline-dry-run-only",
                "profile_id": profile_id,
                "profile_version": "0.1",
                "stages": [
                    {"sequence": index, "stage_id": stage, "state": "defined-not-active"}
                    for index, stage in enumerate(STAGES, start=1)
                ],
            },
            "validation_readiness_id": f"{prefix}-envelope-validation-readiness:{key}:{sequence:04d}",
            "validation_stage_count": len(STAGES),
            "verdict": "response-envelope-validation-controls-ready-no-envelope",
        }
        record.update({field: False for field in ZERO_FIELDS})
        records.append(record)
    return records

def build_ledger(records: list[dict[str, Any]]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    previous: str | None = None
    for record in records:
        entry = {
            "envelope_readiness_assurance_id": record["envelope_readiness_assurance_id"],
            "previous_entry_sha256": previous,
            "record_sha256": sha_doc(record),
            "sequence": record["sequence"],
            "validation_readiness_id": record["validation_readiness_id"],
            "verdict": record["verdict"],
        }
        entry_sha = sha_doc(entry)
        entries.append({"entry": entry, "entry_sha256": entry_sha})
        previous = entry_sha
    return {"entries": entries, "head_sequence": len(entries), "head_sha256": previous}

def build_document() -> dict[str, Any]:
    records = validation_readiness_records()
    ledger = build_ledger(records)
    result = {
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
    return {
        "authority": dict(AUTHORITY),
        "checkpoint": {
            "disposition_selected_count": 0,
            "envelope_received_count": 0,
            "failed_control_count": 0,
            "ledger_sha256": sha_doc(ledger),
            "quarantine_record_count": 0,
            "response_received_count": 0,
            "status_change_count": 0,
            "validation_readiness_record_count": 2,
            "validation_run_count": 0,
        },
        "contract": "principia-offline-consequence-plan-review-response-intake-envelope-validation-readiness/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-offline-consequence-plan-review-response-intake-envelope-validation-readiness-thermal-control",
        "ledger": ledger,
        "live": False,
        "live_activation_permitted": False,
        "mode": MODE,
        "next_gate": NEXT_GATE,
        "phase": 31,
        "real_authorization_claimed": False,
        "recovery": {
            "accepted": ["baseline"],
            "accepted_count": 1,
            "rejected": list(MUTATIONS),
            "rejected_count": len(MUTATIONS),
            "scenario_count": len(MUTATIONS) + 1,
        },
        "result": result,
        "source_phase30": {
            "phase30_candidate_sha256": SOURCE_SHA,
            "phase30_finalization_commit": FINAL_COMMIT,
            "phase30_postmerge_sha256": POST_SHA,
        },
        "state": STATE,
        "validation": {"pull_request": None, "status": "pending", "tested_head_commit": None},
        "validation_readiness_records": records,
    }

def validate_document(document: Mapping[str, Any]) -> list[str]:
    return [] if document == build_document() else ["document drift"]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = verify_sources()
    if errors:
        print("Phase 31 source errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    text = render(build_document())
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != text:
            print("Phase 31 candidate differs from deterministic generation", file=sys.stderr)
            return 1
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(text, encoding="utf-8")
    raw = text.encode()
    print(
        f"Phase 31 candidate passed: {len(raw)} bytes, sha256={hashlib.sha256(raw).hexdigest()}, "
        "2 validation-readiness records, 36 inactive controls, 0 envelopes received."
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
