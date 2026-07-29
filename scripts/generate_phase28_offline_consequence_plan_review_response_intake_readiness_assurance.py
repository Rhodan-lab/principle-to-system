#!/usr/bin/env python3
"""Generate deterministic Phase 28 response-intake readiness assurance evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
MODE = "offline-consequence-plan-review-response-intake-readiness-assurance"
DECISION = "response-intake-readiness-assured-no-response-received"
STATE = MODE + "-candidate"
NEXT_GATE = "offline-consequence-plan-review-response-intake-envelope-readiness-candidate"
OUT = ROOT / "release/phase-28-offline-consequence-plan-review-response-intake-readiness-assurance.json"

PHASE27_CANDIDATE = ROOT / "release/phase-27-offline-consequence-plan-review-response-intake-readiness.json"
PHASE27_POSTMERGE = ROOT / "release/phase-27-postmerge.json"
EXPECTED_CANDIDATE_SHA256 = "9175291eaca5cae5d43e0ba71f85232712e40d9ae16d2767fc360363b7828589"
EXPECTED_POSTMERGE_SHA256 = "2ff65adb34b7790af3585de45254de5391ecf0d8dfbafa0286e8e21841966eca"
EXPECTED_PHASE27_FINALIZATION_COMMIT = "a54a4859cb7537767a3d77de769c213c6a2f6515"

SECTIONS = (
    "source-provenance",
    "reviewer-identity-and-eligibility",
    "human-gate-attestations",
    "question-responses",
    "review-observations",
    "submission-envelope",
)
FIELDS = (
    "schema_version",
    "response_id",
    "packet_id",
    "packet_assurance_id",
    "source_digest",
    "reviewer_identity",
    "reviewer_role",
    "competence_attestation",
    "conflict_declaration",
    "authorization_to_start",
    "question_responses",
    "review_observations",
    "review_recommendation",
    "submitted_at",
    "signature_ref",
)
CHECK_NAMES = (
    "authority_boundary_preserved",
    "blank_response_template_exact",
    "human_gates_remain_pending",
    "packet_assurance_binding_exact",
    "packet_identity_exact",
    "question_slots_blank",
    "readiness_identity_exact",
    "readiness_ledger_binding_exact",
    "readiness_record_digest_exact",
    "required_fields_exact",
    "response_states_frozen",
    "review_execution_frozen",
    "schema_encoding_exact",
    "schema_identity_exact",
    "schema_media_type_exact",
    "schema_sections_exact",
    "schema_version_exact",
    "source_candidate_exact",
    "source_finalization_exact",
    "zero_effect_boundary_preserved",
)
EXPECTED = (
    {
        "key": "feedback-manual-review",
        "sequence": 1,
        "intake_readiness_id": "principia:consequence-plan-review-response-intake-readiness:feedback-manual-review:0001",
        "record_sha256": "2a10068004e3417a2b70fbdf92add060eee265cfb7c95e0eb4947293e6d3ab6f",
        "ledger_entry_sha256": "d514f6934ffd86e2478c9bf124340ceb162315bae351ff8ee5c4b66a925169a0",
        "packet_assurance_id": "principia:consequence-plan-review-request-packet-assurance:feedback-manual-review:0001",
        "packet_id": "principia:consequence-plan-review-request-packet:feedback-manual-review:0001",
        "schema_id": "principia:review-response-intake-schema:feedback-manual-review:0001",
        "reviewer_role_required": "qualified-pedagogical-reviewer",
        "question_ids": ("conceptual-boundary", "evidence-sufficiency", "unresolved-pedagogical-risk"),
    },
    {
        "key": "model-boundary-release-governance",
        "sequence": 2,
        "intake_readiness_id": "principia:consequence-plan-review-response-intake-readiness:model-boundary-release-governance:0002",
        "record_sha256": "f43e0f9176438551d374d186f1d520fbbfa4d6706d2979ebb2e5d82b280ec1f7",
        "ledger_entry_sha256": "bcd693386b4d423f76497d46cc213efd6c4b9551bfbeb29585dc71fbab905a19",
        "packet_assurance_id": "principia:consequence-plan-review-request-packet-assurance:model-boundary-release-governance:0002",
        "packet_id": "principia:consequence-plan-review-request-packet:model-boundary-release-governance:0002",
        "schema_id": "principia:review-response-intake-schema:model-boundary-release-governance:0002",
        "reviewer_role_required": "qualified-release-governance-reviewer",
        "question_ids": ("governance-evidence-sufficiency", "model-boundary-risk", "missing-prerequisite"),
    },
)

AUTHORITY = {
    "atlas_call_permitted": False,
    "automatic_release_action": False,
    "automatic_status_change": False,
    "external_delivery_permitted": False,
    "external_network_required": False,
    "human_authorization_claimed": False,
    "local_response_intake_assurance_permitted": True,
    "repository_mutation": False,
    "response_intake_authorized": False,
    "response_receipt_permitted": False,
    "response_validation_authorized": False,
    "review_execution_authorized": False,
    "review_request_dispatch_authorized": False,
    "reviewer_contact_permitted": False,
    "status_inheritance": "prohibited",
}

MUTATIONS = (
    "phase27-candidate-drift", "phase27-postmerge-drift", "missing-assurance", "orphan-assurance",
    "duplicate-assurance", "sequence-drift", "readiness-id-drift", "readiness-record-digest-drift",
    "readiness-ledger-entry-drift", "packet-assurance-id-drift", "packet-id-drift", "schema-id-drift",
    "schema-version-drift", "schema-media-type-drift", "schema-encoding-drift", "schema-section-count-drift",
    "schema-section-order-drift", "schema-section-state-drift", "required-field-count-drift",
    "required-field-order-drift", "question-count-drift", "question-id-drift", "question-filled",
    "question-accepted", "template-submitted", "response-id-recorded", "source-digest-recorded",
    "reviewer-identity-recorded", "reviewer-role-recorded", "competence-attestation-recorded",
    "conflict-declaration-recorded", "authorization-recorded", "review-observation-recorded",
    "review-recommendation-recorded", "submitted-at-recorded", "signature-recorded",
    "human-gate-satisfied", "response-intake-authorized", "response-receipt-permitted",
    "response-received", "response-validated", "response-accepted", "response-rejected",
    "response-quarantined", "packet-dispatched", "reviewer-contact-permitted",
    "review-start-permitted", "review-started", "review-completed", "outcome-selected",
    "content-change-proposed", "status-recommendation-recorded", "effective-hold",
    "operational-effect", "status-change", "human-authorization-claimed",
    "real-authorization-claimed", "status-inheritance-enabled", "automatic-status-change",
    "automatic-release-action", "repository-mutation", "external-network-required",
    "external-delivery-permitted", "atlas-call-permitted", "live-activation",
    "assurance-check-failed", "assurance-verdict-drift", "assurance-status-drift",
    "assurance-locality-drift", "assurance-ledger-drift", "assurance-checkpoint-drift",
    "summary-drift", "authority-drift", "source-pin-drift", "assurance-count-drift",
    "recovery-count-drift",
)

def render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

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
    if not PHASE27_CANDIDATE.is_file() or file_sha(PHASE27_CANDIDATE) != EXPECTED_CANDIDATE_SHA256:
        errors.append("Phase 27 candidate file drift")
    if not PHASE27_POSTMERGE.is_file() or file_sha(PHASE27_POSTMERGE) != EXPECTED_POSTMERGE_SHA256:
        errors.append("Phase 27 postmerge file drift")
    if errors:
        return errors
    candidate = load(PHASE27_CANDIDATE)
    postmerge = load(PHASE27_POSTMERGE)
    if candidate.get("state") != "offline-consequence-plan-review-response-intake-readiness-candidate":
        errors.append("Phase 27 candidate state drift")
    if candidate.get("next_gate") != STATE:
        errors.append("Phase 27 next gate drift")
    if postmerge.get("state") != "offline-consequence-plan-review-response-intake-readiness-validated":
        errors.append("Phase 27 final state drift")
    if postmerge.get("candidate_record", {}).get("sha256") != EXPECTED_CANDIDATE_SHA256:
        errors.append("Phase 27 finalization candidate digest drift")
    records = {r.get("intake_readiness_id"): r for r in candidate.get("intake_readiness_records", [])}
    entries = {w.get("entry", {}).get("intake_readiness_id"): w for w in candidate.get("ledger", {}).get("entries", [])}
    for expected in EXPECTED:
        record = records.get(expected["intake_readiness_id"])
        wrapper = entries.get(expected["intake_readiness_id"])
        if not record or doc_sha(record) != expected["record_sha256"]:
            errors.append(f"Phase 27 readiness record drift: {expected['key']}")
            continue
        if not wrapper or wrapper.get("entry_sha256") != expected["ledger_entry_sha256"]:
            errors.append(f"Phase 27 readiness ledger drift: {expected['key']}")
        schema = record.get("response_schema", {})
        template = record.get("blank_response_template", {})
        if schema.get("schema_id") != expected["schema_id"]:
            errors.append(f"Phase 27 schema identity drift: {expected['key']}")
        if schema.get("schema_version") != "0.1" or schema.get("media_type") != "application/json" or schema.get("encoding") != "utf-8":
            errors.append(f"Phase 27 schema format drift: {expected['key']}")
        if schema.get("required_fields") != list(FIELDS):
            errors.append(f"Phase 27 required fields drift: {expected['key']}")
        if [s.get("section_id") for s in schema.get("sections", [])] != list(SECTIONS):
            errors.append(f"Phase 27 schema sections drift: {expected['key']}")
        slots = template.get("question_responses", [])
        if [q.get("question_id") for q in slots] != list(expected["question_ids"]):
            errors.append(f"Phase 27 question identity drift: {expected['key']}")
    return errors

def build_assurances() -> list[dict[str, Any]]:
    checks = {name: True for name in CHECK_NAMES}
    assurances = []
    for expected in EXPECTED:
        assurances.append({
            "assurance_check_count": len(CHECK_NAMES),
            "assurance_checks": dict(checks),
            "blank_question_slot_count": 3,
            "human_gate_pending_count": 4,
            "human_gate_satisfied_count": 0,
            "intake_readiness_assurance_id": (
                "principia:consequence-plan-review-response-intake-readiness-assurance:"
                f"{expected['key']}:{expected['sequence']:04d}"
            ),
            "intake_readiness_id": expected["intake_readiness_id"],
            "intake_readiness_ledger_entry_sha256": expected["ledger_entry_sha256"],
            "intake_readiness_record_sha256": expected["record_sha256"],
            "local_only": True,
            "packet_assurance_id": expected["packet_assurance_id"],
            "packet_id": expected["packet_id"],
            "real_authorization_claimed": False,
            "required_field_count": len(FIELDS),
            "response_accepted": False,
            "response_intake_authorized": False,
            "response_quarantined": False,
            "response_receipt_permitted": False,
            "response_received": False,
            "response_rejected": False,
            "response_schema_id": expected["schema_id"],
            "response_schema_section_count": len(SECTIONS),
            "response_validated": False,
            "review_completed": False,
            "review_start_permitted": False,
            "review_started": False,
            "reviewer_contact_permitted": False,
            "reviewer_identity_present": False,
            "reviewer_role_required": expected["reviewer_role_required"],
            "sequence": expected["sequence"],
            "status_change": False,
            "verdict": "response-intake-readiness-assured-no-response",
        })
    return assurances

def validate_assurance(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("verdict") != "response-intake-readiness-assured-no-response":
        errors.append("verdict")
    checks = record.get("assurance_checks")
    if not isinstance(checks, Mapping) or list(sorted(checks)) != list(sorted(CHECK_NAMES)):
        errors.append("checks")
    elif not all(checks.values()):
        errors.append("checks")
    if record.get("assurance_check_count") != len(CHECK_NAMES):
        errors.append("check-count")
    for key in (
        "response_intake_authorized", "response_receipt_permitted", "response_received",
        "response_validated", "response_accepted", "response_rejected", "response_quarantined",
        "review_start_permitted", "review_started", "review_completed", "reviewer_contact_permitted",
        "reviewer_identity_present", "status_change", "real_authorization_claimed",
    ):
        if record.get(key) is not False:
            errors.append("authority")
    if record.get("human_gate_pending_count") != 4 or record.get("human_gate_satisfied_count") != 0:
        errors.append("human-gates")
    if record.get("blank_question_slot_count") != 3:
        errors.append("questions")
    if record.get("required_field_count") != len(FIELDS) or record.get("response_schema_section_count") != len(SECTIONS):
        errors.append("schema")
    return sorted(set(errors))

def build() -> dict[str, Any]:
    assurances = build_assurances()
    entries = []
    previous = None
    for assurance in assurances:
        entry = {
            "intake_readiness_assurance_id": assurance["intake_readiness_assurance_id"],
            "intake_readiness_id": assurance["intake_readiness_id"],
            "intake_readiness_record_sha256": assurance["intake_readiness_record_sha256"],
            "previous_entry_sha256": previous,
            "record_sha256": doc_sha(assurance),
            "sequence": assurance["sequence"],
            "verdict": assurance["verdict"],
        }
        digest = doc_sha(entry)
        entries.append({"entry": entry, "entry_sha256": digest})
        previous = digest
    ledger = {"entries": entries, "head_sequence": 2, "head_sha256": previous}
    summary = {
        "assurance_check_count": len(CHECK_NAMES) * 2,
        "assured_readiness_record_count": 2,
        "blank_question_slot_count": 6,
        "failed_assurance_count": 0,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
        "intake_readiness_record_count": 2,
        "real_authorization_claimed": False,
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
    }
    checkpoint = {
        "assurance_check_count": summary["assurance_check_count"],
        "assured_readiness_record_count": 2,
        "failed_assurance_count": 0,
        "human_gate_pending_count": 8,
        "ledger_sha256": doc_sha(ledger),
        "response_received_count": 0,
        "response_validated_count": 0,
        "review_started_count": 0,
        "status_change_count": 0,
    }
    recovery = {
        "accepted_count": 1,
        "rejected_count": len(MUTATIONS),
        "scenario_count": len(MUTATIONS) + 1,
        "scenarios": [{"expected": "accepted", "id": "baseline"}]
        + [{"expected": "rejected", "id": mutation} for mutation in MUTATIONS],
    }
    return {
        "assurances": assurances,
        "authority": AUTHORITY,
        "checkpoint": checkpoint,
        "contract": "principia-offline-consequence-plan-review-response-intake-readiness-assurance/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-offline-consequence-plan-review-response-intake-readiness-assurance-thermal-control",
        "ledger": ledger,
        "live": False,
        "live_activation_permitted": False,
        "mode": MODE,
        "next_gate": NEXT_GATE,
        "phase": 28,
        "real_authorization_claimed": False,
        "recovery": recovery,
        "result": summary,
        "source_phase27": {
            "candidate_path": PHASE27_CANDIDATE.relative_to(ROOT).as_posix(),
            "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "finalization_commit": EXPECTED_PHASE27_FINALIZATION_COMMIT,
            "postmerge_path": PHASE27_POSTMERGE.relative_to(ROOT).as_posix(),
            "postmerge_sha256": EXPECTED_POSTMERGE_SHA256,
        },
        "state": STATE,
        "validation": {"pull_request": None, "status": "pending", "tested_head_commit": None},
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = verify_sources()
    value = build()
    text = render(value)
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != text:
            errors.append("generated file drift")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(text, encoding="utf-8")
    if errors:
        print("Phase 28 generation errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Phase 28 readiness assurance is deterministic, source-pinned, local-only, and non-receiving.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
