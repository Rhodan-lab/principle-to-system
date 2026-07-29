#!/usr/bin/env python3
"""Generate deterministic Phase 29 response-intake envelope readiness evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
MODE = "offline-consequence-plan-review-response-intake-envelope-readiness"
DECISION = "response-intake-envelope-readiness-recorded-no-response-received"
STATE = MODE + "-candidate"
NEXT_GATE = MODE + "-assurance-candidate"
OUT = ROOT / "release/phase-29-offline-consequence-plan-review-response-intake-envelope-readiness.json"

PHASE28_CANDIDATE = ROOT / "release/phase-28-offline-consequence-plan-review-response-intake-readiness-assurance.json"
PHASE28_POSTMERGE = ROOT / "release/phase-28-postmerge.json"
EXPECTED_CANDIDATE_SHA256 = "ce21c69cd246db67d5b03d2ac84962789ae5ff78ace4fd1d5b90b79cf6301fda"
EXPECTED_POSTMERGE_SHA256 = "c6f6e6b5b03e82226fcdc40b7bb8b3545cd6ba26b952396a6c4b09908f9675af"
EXPECTED_PHASE28_FINALIZATION_COMMIT = "7ba58a027e159d69ac7054effbe36e936b107c84"

ENVELOPE_SECTIONS = (
    "source-binding",
    "transport-metadata",
    "payload-integrity",
    "schema-binding",
    "reviewer-gate-attestations",
    "quarantine-routing",
    "submission-state",
)
ENVELOPE_FIELDS = (
    "envelope_version",
    "envelope_id",
    "response_id",
    "intake_readiness_id",
    "intake_readiness_assurance_id",
    "packet_id",
    "packet_assurance_id",
    "schema_id",
    "payload_media_type",
    "payload_encoding",
    "payload_sha256",
    "source_digest",
    "submitted_at",
    "signature_ref",
)
INTEGRITY_RULES = (
    "canonical-json-required",
    "utf8-required",
    "media-type-exact",
    "schema-id-exact",
    "assurance-id-exact",
    "packet-id-exact",
    "payload-sha256-required",
    "source-digest-required",
    "duplicate-envelope-prohibited",
    "unknown-fields-prohibited",
)
QUARANTINE_REASONS = (
    "malformed-envelope",
    "unsupported-envelope-version",
    "schema-binding-mismatch",
    "assurance-binding-mismatch",
    "packet-binding-mismatch",
    "payload-digest-mismatch",
    "source-digest-missing",
    "reviewer-gates-incomplete",
    "duplicate-envelope",
    "signature-or-timestamp-missing",
)

EXPECTED = (
    {
        "key": "feedback-manual-review",
        "sequence": 1,
        "intake_readiness_assurance_id": "principia:consequence-plan-review-response-intake-readiness-assurance:feedback-manual-review:0001",
        "assurance_record_sha256": "485376d8f2e39ae8f9050dce3ff42ba8ffb8f06391ddb1e8db22ad6db568ebd2",
        "assurance_ledger_entry_sha256": "656544c79f245e3d72b408cd750732a151fe0a0aee74c1e5df3b0caa867a478a",
        "intake_readiness_id": "principia:consequence-plan-review-response-intake-readiness:feedback-manual-review:0001",
        "packet_assurance_id": "principia:consequence-plan-review-request-packet-assurance:feedback-manual-review:0001",
        "packet_id": "principia:consequence-plan-review-request-packet:feedback-manual-review:0001",
        "schema_id": "principia:review-response-intake-schema:feedback-manual-review:0001",
        "reviewer_role_required": "qualified-pedagogical-reviewer",
    },
    {
        "key": "model-boundary-release-governance",
        "sequence": 2,
        "intake_readiness_assurance_id": "principia:consequence-plan-review-response-intake-readiness-assurance:model-boundary-release-governance:0002",
        "assurance_record_sha256": "a469959e96c84f4d5738efcebcd8cc78adc279b90fdfaf65bff70d623da448b6",
        "assurance_ledger_entry_sha256": "1377b4d6073dd2840a57b2150e94b5824668a9f949a065b5abcdbf0a702d154a",
        "intake_readiness_id": "principia:consequence-plan-review-response-intake-readiness:model-boundary-release-governance:0002",
        "packet_assurance_id": "principia:consequence-plan-review-request-packet-assurance:model-boundary-release-governance:0002",
        "packet_id": "principia:consequence-plan-review-request-packet:model-boundary-release-governance:0002",
        "schema_id": "principia:review-response-intake-schema:model-boundary-release-governance:0002",
        "reviewer_role_required": "qualified-release-governance-reviewer",
    },
)

AUTHORITY = {
    "atlas_call_permitted": False,
    "automatic_release_action": False,
    "automatic_status_change": False,
    "external_delivery_permitted": False,
    "external_network_required": False,
    "human_authorization_claimed": False,
    "local_response_envelope_readiness_permitted": True,
    "repository_mutation": False,
    "response_envelope_creation_permitted": False,
    "response_envelope_processing_authorized": False,
    "response_intake_authorized": False,
    "response_quarantine_execution_authorized": False,
    "response_receipt_permitted": False,
    "response_validation_authorized": False,
    "review_execution_authorized": False,
    "review_request_dispatch_authorized": False,
    "reviewer_contact_permitted": False,
    "status_inheritance": "prohibited",
}

MUTATIONS = (
    "phase28-candidate-drift", "phase28-postmerge-drift", "missing-envelope-readiness",
    "orphan-envelope-readiness", "duplicate-envelope-readiness", "sequence-drift",
    "assurance-id-drift", "assurance-record-digest-drift", "assurance-ledger-entry-drift",
    "readiness-id-drift", "packet-assurance-id-drift", "packet-id-drift", "schema-id-drift",
    "envelope-id-drift", "envelope-version-drift", "envelope-media-type-drift",
    "envelope-encoding-drift", "envelope-section-count-drift", "envelope-section-order-drift",
    "envelope-section-state-drift", "envelope-field-count-drift", "envelope-field-order-drift",
    "max-payload-bytes-drift", "digest-algorithm-drift", "integrity-rule-count-drift",
    "integrity-rule-id-drift", "integrity-rule-state-drift", "quarantine-reason-count-drift",
    "quarantine-reason-id-drift", "quarantine-default-state-drift", "envelope-id-recorded",
    "response-id-recorded", "payload-sha-recorded", "source-digest-recorded",
    "submitted-at-recorded", "signature-recorded", "template-submitted", "quarantine-state-changed",
    "quarantine-reason-recorded", "human-gate-satisfied", "envelope-created", "envelope-received",
    "envelope-processed", "integrity-failure-recorded", "duplicate-envelope-recorded",
    "quarantine-record-created", "quarantine-execution-authorized", "response-intake-authorized",
    "response-receipt-permitted", "response-received", "response-validated", "response-accepted",
    "response-rejected", "response-quarantined", "packet-dispatched", "reviewer-contact-permitted",
    "reviewer-identity-recorded", "review-start-permitted", "review-started", "review-completed",
    "outcome-selected", "content-change-proposed", "status-recommendation-recorded", "effective-hold",
    "operational-effect", "status-change", "human-authorization-claimed", "real-authorization-claimed",
    "status-inheritance-enabled", "automatic-status-change", "automatic-release-action",
    "repository-mutation", "external-network-required", "external-delivery-permitted",
    "atlas-call-permitted", "live-activation", "envelope-verdict-drift", "envelope-status-drift",
    "envelope-locality-drift", "ledger-drift", "checkpoint-drift", "summary-drift", "authority-drift",
    "source-pin-drift", "record-count-drift", "recovery-count-drift",
)


def render(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def doc_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def verify_sources() -> list[str]:
    errors: list[str] = []
    if not PHASE28_CANDIDATE.is_file() or file_sha(PHASE28_CANDIDATE) != EXPECTED_CANDIDATE_SHA256:
        errors.append("Phase 28 candidate file drift")
    if not PHASE28_POSTMERGE.is_file() or file_sha(PHASE28_POSTMERGE) != EXPECTED_POSTMERGE_SHA256:
        errors.append("Phase 28 postmerge file drift")
    if errors:
        return errors
    candidate = load(PHASE28_CANDIDATE)
    postmerge = load(PHASE28_POSTMERGE)
    if candidate.get("state") != "offline-consequence-plan-review-response-intake-readiness-assurance-candidate":
        errors.append("Phase 28 candidate state drift")
    if candidate.get("next_gate") != STATE:
        errors.append("Phase 28 next gate drift")
    if postmerge.get("state") != "offline-consequence-plan-review-response-intake-readiness-assurance-validated":
        errors.append("Phase 28 final state drift")
    if postmerge.get("candidate_record", {}).get("sha256") != EXPECTED_CANDIDATE_SHA256:
        errors.append("Phase 28 finalization candidate digest drift")
    if postmerge.get("next_gate") != STATE:
        errors.append("Phase 28 finalization next gate drift")
    assurances = {r.get("intake_readiness_assurance_id"): r for r in candidate.get("assurances", [])}
    entries = {w.get("entry", {}).get("intake_readiness_assurance_id"): w for w in candidate.get("ledger", {}).get("entries", [])}
    for expected in EXPECTED:
        assurance = assurances.get(expected["intake_readiness_assurance_id"])
        wrapper = entries.get(expected["intake_readiness_assurance_id"])
        if not assurance or doc_sha(assurance) != expected["assurance_record_sha256"]:
            errors.append(f"Phase 28 assurance record drift: {expected['key']}")
            continue
        if not wrapper or wrapper.get("entry_sha256") != expected["assurance_ledger_entry_sha256"]:
            errors.append(f"Phase 28 assurance ledger drift: {expected['key']}")
        if assurance.get("verdict") != "response-intake-readiness-assured-no-response":
            errors.append(f"Phase 28 assurance verdict drift: {expected['key']}")
        if assurance.get("response_schema_id") != expected["schema_id"]:
            errors.append(f"Phase 28 schema binding drift: {expected['key']}")
        if assurance.get("human_gate_pending_count") != 4 or assurance.get("human_gate_satisfied_count") != 0:
            errors.append(f"Phase 28 human gate drift: {expected['key']}")
    return errors


def build_envelope_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for expected in EXPECTED:
        envelope_id = f"principia:review-response-intake-envelope:{expected['key']}:{expected['sequence']:04d}"
        template = {
            "envelope_version": "0.1",
            "envelope_id": None,
            "response_id": None,
            "intake_readiness_id": expected["intake_readiness_id"],
            "intake_readiness_assurance_id": expected["intake_readiness_assurance_id"],
            "packet_id": expected["packet_id"],
            "packet_assurance_id": expected["packet_assurance_id"],
            "schema_id": expected["schema_id"],
            "payload_media_type": "application/json",
            "payload_encoding": "utf-8",
            "payload_sha256": None,
            "source_digest": None,
            "submitted_at": None,
            "signature_ref": None,
            "submitted": False,
            "quarantine_state": "not-evaluated",
            "quarantine_reason": None,
        }
        records.append({
            "blank_envelope_template": template,
            "blank_required_field_count": 6,
            "envelope_readiness_id": (
                "principia:consequence-plan-review-response-intake-envelope-readiness:"
                f"{expected['key']}:{expected['sequence']:04d}"
            ),
            "envelope_spec": {
                "digest_algorithm": "sha256",
                "encoding": "utf-8",
                "envelope_id": envelope_id,
                "envelope_version": "0.1",
                "max_payload_bytes": 131072,
                "media_type": "application/json",
                "required_fields": list(ENVELOPE_FIELDS),
                "sections": [
                    {"section_id": section_id, "sequence": index, "state": "defined-not-active"}
                    for index, section_id in enumerate(ENVELOPE_SECTIONS, start=1)
                ],
            },
            "human_gate_pending_count": 4,
            "human_gate_satisfied_count": 0,
            "intake_readiness_assurance_id": expected["intake_readiness_assurance_id"],
            "intake_readiness_assurance_ledger_entry_sha256": expected["assurance_ledger_entry_sha256"],
            "intake_readiness_assurance_record_sha256": expected["assurance_record_sha256"],
            "intake_readiness_id": expected["intake_readiness_id"],
            "integrity_rules": [
                {"rule_id": rule_id, "sequence": index, "state": "defined-not-active"}
                for index, rule_id in enumerate(INTEGRITY_RULES, start=1)
            ],
            "local_only": True,
            "packet_assurance_id": expected["packet_assurance_id"],
            "packet_id": expected["packet_id"],
            "quarantine_policy": {
                "default_state": "not-evaluated",
                "execution_authorized": False,
                "reason_codes": [
                    {"reason_id": reason_id, "sequence": index, "state": "defined-not-active"}
                    for index, reason_id in enumerate(QUARANTINE_REASONS, start=1)
                ],
            },
            "real_authorization_claimed": False,
            "response_accepted": False,
            "response_envelope_created": False,
            "response_envelope_processed": False,
            "response_envelope_received": False,
            "response_intake_authorized": False,
            "response_quarantined": False,
            "response_received": False,
            "response_rejected": False,
            "response_schema_id": expected["schema_id"],
            "response_validated": False,
            "review_completed": False,
            "review_start_permitted": False,
            "review_started": False,
            "reviewer_contact_permitted": False,
            "reviewer_identity_present": False,
            "reviewer_role_required": expected["reviewer_role_required"],
            "sequence": expected["sequence"],
            "status_change": False,
            "verdict": "response-envelope-schema-ready-no-response",
        })
    return records


def validate_envelope_record(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("verdict") != "response-envelope-schema-ready-no-response":
        errors.append("verdict")
    if record.get("local_only") is not True:
        errors.append("locality")
    spec = record.get("envelope_spec")
    if not isinstance(spec, Mapping):
        errors.append("envelope-spec")
    else:
        if spec.get("envelope_version") != "0.1" or spec.get("media_type") != "application/json" or spec.get("encoding") != "utf-8":
            errors.append("envelope-format")
        if spec.get("digest_algorithm") != "sha256" or spec.get("max_payload_bytes") != 131072:
            errors.append("integrity-limits")
        if spec.get("required_fields") != list(ENVELOPE_FIELDS):
            errors.append("required-fields")
        sections = spec.get("sections", [])
        if [section.get("section_id") for section in sections] != list(ENVELOPE_SECTIONS):
            errors.append("sections")
        if any(section.get("state") != "defined-not-active" for section in sections):
            errors.append("section-state")
    template = record.get("blank_envelope_template")
    if not isinstance(template, Mapping):
        errors.append("template")
    else:
        for key in ("envelope_id", "response_id", "payload_sha256", "source_digest", "submitted_at", "signature_ref"):
            if template.get(key) is not None:
                errors.append(f"template-{key}")
        if template.get("submitted") is not False or template.get("quarantine_state") != "not-evaluated" or template.get("quarantine_reason") is not None:
            errors.append("template-state")
    rules = record.get("integrity_rules", [])
    if [item.get("rule_id") for item in rules] != list(INTEGRITY_RULES) or any(item.get("state") != "defined-not-active" for item in rules):
        errors.append("integrity-rules")
    quarantine = record.get("quarantine_policy")
    if not isinstance(quarantine, Mapping):
        errors.append("quarantine-policy")
    else:
        reasons = quarantine.get("reason_codes", [])
        if [item.get("reason_id") for item in reasons] != list(QUARANTINE_REASONS):
            errors.append("quarantine-reasons")
        if any(item.get("state") != "defined-not-active" for item in reasons):
            errors.append("quarantine-reason-state")
        if quarantine.get("default_state") != "not-evaluated" or quarantine.get("execution_authorized") is not False:
            errors.append("quarantine-state")
    for key in (
        "response_accepted", "response_envelope_created", "response_envelope_processed",
        "response_envelope_received", "response_intake_authorized", "response_quarantined",
        "response_received", "response_rejected", "response_validated", "review_completed",
        "review_start_permitted", "review_started", "reviewer_contact_permitted",
        "reviewer_identity_present", "status_change", "real_authorization_claimed",
    ):
        if record.get(key) is not False:
            errors.append(key)
    if record.get("human_gate_pending_count") != 4 or record.get("human_gate_satisfied_count") != 0:
        errors.append("human-gates")
    return errors


def build_ledger(records: list[dict[str, Any]]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    previous: str | None = None
    for record in records:
        entry = {
            "envelope_readiness_id": record["envelope_readiness_id"],
            "intake_readiness_assurance_id": record["intake_readiness_assurance_id"],
            "previous_entry_sha256": previous,
            "record_sha256": doc_sha(record),
            "sequence": record["sequence"],
            "verdict": record["verdict"],
        }
        entry_sha = doc_sha(entry)
        entries.append({"entry": entry, "entry_sha256": entry_sha})
        previous = entry_sha
    return {"entries": entries, "head_sequence": len(entries), "head_sha256": previous}


def build_document() -> dict[str, Any]:
    records = build_envelope_records()
    ledger = build_ledger(records)
    result = {
        "blank_required_envelope_field_count": sum(r["blank_required_field_count"] for r in records),
        "duplicate_envelope_count": 0,
        "envelope_readiness_record_count": len(records),
        "envelope_section_count": len(records) * len(ENVELOPE_SECTIONS),
        "envelope_spec_count": len(records),
        "envelope_template_count": len(records),
        "human_gate_pending_count": sum(r["human_gate_pending_count"] for r in records),
        "human_gate_satisfied_count": 0,
        "integrity_failure_count": 0,
        "integrity_rule_count": len(records) * len(INTEGRITY_RULES),
        "quarantine_reason_code_count": len(records) * len(QUARANTINE_REASONS),
        "quarantine_record_count": 0,
        "real_authorization_claimed": False,
        "required_envelope_field_count": len(records) * len(ENVELOPE_FIELDS),
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
    }
    recovery = {
        "accepted_count": 1,
        "rejected_count": len(MUTATIONS),
        "scenario_count": len(MUTATIONS) + 1,
        "scenarios": [{"expected": "accepted", "id": "baseline"}] + [
            {"expected": "rejected", "id": mutation} for mutation in MUTATIONS
        ],
    }
    checkpoint = {
        "envelope_readiness_record_count": len(records),
        "envelope_received_count": 0,
        "integrity_failure_count": 0,
        "ledger_sha256": doc_sha(ledger),
        "quarantine_record_count": 0,
        "response_received_count": 0,
        "review_started_count": 0,
        "status_change_count": 0,
    }
    return {
        "authority": dict(AUTHORITY),
        "checkpoint": checkpoint,
        "contract": "principia-offline-consequence-plan-review-response-intake-envelope-readiness/0.1",
        "decision": DECISION,
        "envelope_readiness_records": records,
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-offline-consequence-plan-review-response-intake-envelope-readiness-thermal-control",
        "ledger": ledger,
        "live": False,
        "live_activation_permitted": False,
        "mode": MODE,
        "next_gate": NEXT_GATE,
        "phase": 29,
        "real_authorization_claimed": False,
        "recovery": recovery,
        "result": result,
        "source_phase28": {
            "phase28_candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "phase28_finalization_commit": EXPECTED_PHASE28_FINALIZATION_COMMIT,
            "phase28_postmerge_sha256": EXPECTED_POSTMERGE_SHA256,
        },
        "state": STATE,
        "validation": {"pull_request": None, "status": "pending", "tested_head_commit": None},
    }


def validate_document(document: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, expected in {
        "contract": "principia-offline-consequence-plan-review-response-intake-envelope-readiness/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "live_activation_permitted": False,
        "mode": MODE,
        "next_gate": NEXT_GATE,
        "phase": 29,
        "real_authorization_claimed": False,
        "state": STATE,
    }.items():
        if document.get(key) != expected:
            errors.append(f"{key} drift")
    if document.get("authority") != AUTHORITY:
        errors.append("authority drift")
    records = document.get("envelope_readiness_records")
    if not isinstance(records, list) or len(records) != 2:
        errors.append("record count")
        records = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, Mapping):
            errors.append(f"record {index} type")
        else:
            errors.extend(f"record {index}: {error}" for error in validate_envelope_record(record))
    if records and document.get("ledger") != build_ledger(list(records)):
        errors.append("ledger drift")
    result = document.get("result")
    expected_result = build_document()["result"] if document is not _BUILD_SENTINEL else {}
    if isinstance(result, Mapping) and expected_result and dict(result) != expected_result:
        errors.append("result drift")
    recovery = document.get("recovery")
    if not isinstance(recovery, Mapping) or recovery.get("scenario_count") != len(MUTATIONS) + 1 or recovery.get("rejected_count") != len(MUTATIONS):
        errors.append("recovery drift")
    source = document.get("source_phase28")
    if source != {
        "phase28_candidate_sha256": EXPECTED_CANDIDATE_SHA256,
        "phase28_finalization_commit": EXPECTED_PHASE28_FINALIZATION_COMMIT,
        "phase28_postmerge_sha256": EXPECTED_POSTMERGE_SHA256,
    }:
        errors.append("source pin drift")
    return sorted(set(errors))


_BUILD_SENTINEL: Mapping[str, Any] = {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source_errors = verify_sources()
    if source_errors:
        print("Phase 29 source errors:", file=sys.stderr)
        for error in source_errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    document = build_document()
    errors = validate_document(document)
    if errors:
        print("Phase 29 generation errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    rendered = render(document)
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != rendered:
            print("Phase 29 candidate differs from deterministic generation", file=sys.stderr)
            return 1
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(rendered, encoding="utf-8")
    raw = rendered.encode()
    print(
        f"Phase 29 candidate passed: {len(raw)} bytes, sha256={hashlib.sha256(raw).hexdigest()}, "
        "2 local envelope readiness records, 0 envelopes received."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
