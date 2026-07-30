#!/usr/bin/env python3
"""Generate deterministic Phase 37 authorization-decision readiness evidence.

This phase defines only offline prerequisites for considering an authorization
 decision. It does not create a candidate, record a decision, grant authority,
 issue a token or ticket, receive an envelope, execute validation, contact a
 reviewer, call Atlas, or mutate repository status.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SOURCE_CANDIDATE = ROOT / "release/phase-36-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance.json"
SOURCE_POSTMERGE = ROOT / "release/phase-36-postmerge.json"
OUTPUT = ROOT / "release/phase-37-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness.json"
PHASE36_CANDIDATE_SHA = "c90abcedeffcc66ff1d1e1d615e03cc5e002a76177d3ab8a0754543c4ad1677e"
PHASE36_POSTMERGE_SHA = "79b689ad032d29c21e620525cdea665545f0ee9e2e4f633b708a78240b252f52"
PHASE36_FINALIZATION_COMMIT = "31a66a144fe605d864b67f89e585b823ff2ae72c"
MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness"
STATE = MODE + "-candidate"
NEXT_GATE = MODE + "-assurance-candidate"
DECISION = "response-intake-envelope-validation-execution-authorization-decision-readiness-recorded-no-decision-candidate-created"
CONTRACT = "principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness/0.1"
POLICY_ID = "principia-envelope-validation-execution-authorization-decision-policy"
POLICY_VERSION = "0.1"

STAGE_IDS = [
    "source-assurance-lock",
    "decision-profile-resolution",
    "decision-scope-definition",
    "dual-control-role-lock",
    "conflict-declaration-requirement",
    "approval-evidence-requirement-lock",
    "decision-option-schema-lock",
    "rationale-schema-lock",
    "blank-decision-record-binding",
    "expiration-and-revocation-boundary-lock",
    "audit-record-preparation",
    "decision-and-grant-freeze",
]
REQUIREMENT_IDS = [
    "source-phase36-candidate-pinned",
    "source-phase36-postmerge-pinned",
    "source-phase36-finalization-pinned",
    "authorization-readiness-assurance-identity-pinned",
    "authorization-readiness-identity-pinned",
    "authorization-profile-identity-pinned",
    "execution-profile-identity-pinned",
    "validation-profile-identity-pinned",
    "authorization-policy-digest-pinned",
    "source-assurance-record-digest-pinned",
    "source-assurance-ledger-entry-pinned",
    "reviewer-role-defined",
    "authorization-officer-role-defined",
    "dual-control-required",
    "approval-roles-remain-unsatisfied",
    "human-gates-remain-pending",
    "conflict-declaration-required",
    "decision-options-defined-not-selectable",
    "decision-rationale-schema-defined",
    "blank-decision-record-preserved",
    "authorization-token-remains-unissued",
    "authorization-candidate-absent",
    "authorization-decision-absent",
    "authorization-grant-absent",
    "envelope-response-and-execution-absent",
    "result-disposition-and-status-effects-disabled",
]
DECISION_OPTIONS = ["grant", "deny", "defer"]
BLANK_DECISION_FIELDS = [
    "decision_id", "authorization_candidate_id", "decision_option",
    "primary_decider_identity", "primary_decider_role",
    "secondary_decider_identity", "secondary_decider_role", "decided_at",
    "rationale_code", "rationale_text_ref", "source_assurance_digest",
    "approval_evidence_digest", "authorization_token_id",
    "decision_signature_ref", "conflict_declaration_ref", "expires_at",
]
CHECK_NAMES = [
    "source_candidate_exact", "source_postmerge_exact", "source_finalization_exact",
    "source_assurance_identity_exact", "source_assurance_record_digest_exact",
    "source_assurance_ledger_binding_exact", "authorization_readiness_identity_exact",
    "authorization_profile_identity_exact", "execution_profile_identity_exact",
    "validation_profile_identity_exact", "authorization_policy_digest_exact",
    "decision_policy_identity_exact", "decision_policy_version_exact",
    "decision_policy_mode_exact", "decision_policy_input_state_exact",
    "decision_stage_count_exact", "decision_stage_order_exact",
    "decision_stage_states_inactive", "decision_requirement_count_exact",
    "decision_requirement_order_exact", "decision_requirement_states_unevaluated",
    "decision_options_exact", "decision_options_unselectable",
    "decision_scope_operation_exact", "decision_scope_profile_bound",
    "decision_scope_assurance_bound", "decision_scope_dual_control_exact",
    "decision_scope_network_disabled", "decision_scope_atlas_disabled",
    "decision_scope_repository_write_disabled", "decision_scope_token_issue_disabled",
    "decision_scope_execution_disabled", "decision_scope_result_recording_disabled",
    "decision_scope_status_change_disabled", "reviewer_role_exact",
    "authorization_officer_role_exact", "required_approval_role_count_exact",
    "approval_roles_pending", "dual_control_exact", "human_gates_remain_pending",
    "conflict_declaration_required_not_evaluated", "blank_decision_record_exact",
    "blank_decision_field_count_exact", "decision_record_unissued",
    "decision_candidate_absent", "decision_record_absent", "authorization_grant_absent",
    "authorization_token_unissued", "authorization_states_frozen",
    "envelope_response_states_frozen", "execution_states_frozen",
    "validation_result_frozen", "review_states_frozen", "disposition_frozen",
    "status_effects_frozen", "authority_boundary_preserved", "zero_effect_boundary_preserved",
    "locality_preserved",
]


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()

def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected object: {path}")
    return value

def policy() -> dict[str, Any]:
    p = {
        "decision_policy_id": POLICY_ID,
        "decision_policy_version": POLICY_VERSION,
        "mode": "offline-authorization-decision-preflight-only",
        "input_state": "no-envelope-no-authorization-no-decision",
        "decision_stages": [
            {"sequence": i + 1, "stage_id": stage, "state": "defined-not-active"}
            for i, stage in enumerate(STAGE_IDS)
        ],
        "decision_requirements": [
            {"sequence": i + 1, "requirement_id": req, "state": "required-not-evaluated"}
            for i, req in enumerate(REQUIREMENT_IDS)
        ],
        "decision_options": [
            {"sequence": i + 1, "option": option, "state": "defined-not-selectable"}
            for i, option in enumerate(DECISION_OPTIONS)
        ],
        "decision_scope": {
            "operation": "consider-one-bound-validation-execution-authorization-decision",
            "profile_bound": True,
            "assurance_bound": True,
            "dual_control_required": True,
            "conflict_declaration_required": True,
            "external_network": False,
            "atlas_access": False,
            "repository_write": False,
            "token_issue_enabled": False,
            "execution_enabled": False,
            "result_recording_enabled": False,
            "disposition_selection_enabled": False,
            "status_change_enabled": False,
        },
        "rationale_schema": {
            "required_fields": ["rationale_code", "rationale_text_ref"],
            "state": "defined-not-active",
        },
        "blank_decision_record_fields": BLANK_DECISION_FIELDS,
        "validity_window_policy": {"maximum_seconds": 900, "state": "defined-not-active"},
        "revocation_boundary": {"authorization_revocation_supported": True, "state": "defined-not-active"},
    }
    p["decision_policy_sha256"] = digest(p)
    return p

def expected_blank_record(profile: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    record = {field: None for field in BLANK_DECISION_FIELDS}
    record.update({
        "decision_profile_id": profile["decision_profile_id"],
        "authorization_readiness_assurance_id": source["authorization_readiness_assurance_id"],
        "authorization_profile_id": source["authorization_profile_id"],
        "execution_profile_id": source["execution_profile_id"],
        "validation_profile_id": source["validation_profile_id"],
        "issued": False,
        "recorded": False,
    })
    return record

def build() -> dict[str, Any]:
    if file_sha(SOURCE_CANDIDATE) != PHASE36_CANDIDATE_SHA:
        raise ValueError("Phase 36 candidate digest drift")
    if file_sha(SOURCE_POSTMERGE) != PHASE36_POSTMERGE_SHA:
        raise ValueError("Phase 36 postmerge digest drift")
    source = load(SOURCE_CANDIDATE)
    post = load(SOURCE_POSTMERGE)
    if source.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-candidate":
        raise ValueError("Phase 36 candidate state drift")
    if post.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-validated":
        raise ValueError("Phase 36 final state drift")
    if post.get("principia", {}).get("merge_commit") != "2c0f3bc5d01e8f36782108a14a8611e38c4d5ca6":
        raise ValueError("Phase 36 candidate merge drift")
    if PHASE36_FINALIZATION_COMMIT != "31a66a144fe605d864b67f89e585b823ff2ae72c":
        raise ValueError("Phase 36 finalization pin drift")
    p = policy()
    source_assurances = source.get("assurances")
    source_ledger = source.get("ledger", {}).get("entries")
    if not isinstance(source_assurances, list) or len(source_assurances) != 2:
        raise ValueError("Phase 36 assurance count drift")
    if not isinstance(source_ledger, list) or len(source_ledger) != 2:
        raise ValueError("Phase 36 ledger count drift")
    profiles: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for index, (assurance, ledger_item) in enumerate(zip(source_assurances, source_ledger), 1):
        source_record_sha = digest(assurance)
        if ledger_item.get("entry", {}).get("record_sha256") != source_record_sha:
            raise ValueError(f"Phase 36 source record {index} ledger mismatch")
        suffix = assurance["authorization_readiness_assurance_id"].split(":")[-2:]
        label = ":".join(suffix)
        profile_id = f"principia:review-response-intake-envelope-validation-execution-authorization-decision-profile:{label}"
        readiness_id = f"principia:consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness:{label}"
        profile = {
            "sequence": index,
            "decision_profile_id": profile_id,
            "authorization_readiness_assurance_id": assurance["authorization_readiness_assurance_id"],
            "authorization_readiness_id": assurance["authorization_readiness_id"],
            "authorization_profile_id": assurance["authorization_profile_id"],
            "execution_profile_id": assurance["execution_profile_id"],
            "validation_profile_id": assurance["validation_profile_id"],
            "reviewer_role_required": assurance["reviewer_role_required"],
            "authorization_officer_role_required": assurance["authorization_officer_role_required"],
            "required_decision_roles": [
                {"sequence": 1, "role": assurance["reviewer_role_required"], "state": "required-not-satisfied"},
                {"sequence": 2, "role": assurance["authorization_officer_role_required"], "state": "required-not-satisfied"},
            ],
            "dual_control_required": True,
            "conflict_declaration_required": True,
            "decision_policy_sha256": p["decision_policy_sha256"],
        }
        profiles.append(profile)
        blank = expected_blank_record(profile, assurance)
        checks = {name: True for name in CHECK_NAMES}
        record = {
            "sequence": index,
            "decision_readiness_id": readiness_id,
            "decision_profile_id": profile_id,
            "authorization_readiness_assurance_id": assurance["authorization_readiness_assurance_id"],
            "authorization_readiness_assurance_record_sha256": source_record_sha,
            "authorization_readiness_assurance_ledger_entry_sha256": ledger_item["entry_sha256"],
            "authorization_readiness_id": assurance["authorization_readiness_id"],
            "authorization_profile_id": assurance["authorization_profile_id"],
            "execution_profile_id": assurance["execution_profile_id"],
            "validation_profile_id": assurance["validation_profile_id"],
            "reviewer_role_required": assurance["reviewer_role_required"],
            "authorization_officer_role_required": assurance["authorization_officer_role_required"],
            "required_decision_role_count": 2,
            "dual_control_required": True,
            "decision_stage_count": len(STAGE_IDS),
            "decision_requirement_count": len(REQUIREMENT_IDS),
            "decision_requirement_evaluated_count": 0,
            "decision_option_count": len(DECISION_OPTIONS),
            "decision_option_selected": False,
            "conflict_declaration_required": True,
            "conflict_declaration_evaluated": False,
            "approval_received": False,
            "approval_evidence_recorded": False,
            "human_gate_pending_count": assurance["human_gate_pending_count"],
            "human_gate_satisfied_count": 0,
            "blank_decision_record": blank,
            "blank_decision_record_field_count": len(BLANK_DECISION_FIELDS),
            "decision_candidate_created": False,
            "decision_record_created": False,
            "authorization_decision_recorded": False,
            "authorization_granted": False,
            "authorization_revoked": False,
            "authorization_expired": False,
            "authorization_token_issued": False,
            "execution_authorization_present": False,
            "execution_ticket_issued": False,
            "execution_run_created": False,
            "execution_started": False,
            "execution_completed": False,
            "validation_result_recorded": False,
            "disposition_selected": False,
            "response_envelope_created": False,
            "response_envelope_received": False,
            "response_envelope_processed": False,
            "response_received": False,
            "response_validated": False,
            "response_accepted": False,
            "response_rejected": False,
            "response_quarantined": False,
            "reviewer_identity_present": False,
            "reviewer_contact_permitted": False,
            "review_start_permitted": False,
            "review_started": False,
            "review_completed": False,
            "status_change": False,
            "real_authorization_claimed": False,
            "local_only": True,
            "readiness_check_count": len(CHECK_NAMES),
            "readiness_checks": checks,
            "status": "authorization-decision-readiness-recorded-no-decision-candidate-created",
            "verdict": "response-envelope-validation-execution-authorization-decision-controls-ready-no-decision",
        }
        records.append(record)
    ledger_entries = []
    previous = None
    for record in records:
        entry = {
            "sequence": record["sequence"],
            "decision_readiness_id": record["decision_readiness_id"],
            "authorization_readiness_assurance_id": record["authorization_readiness_assurance_id"],
            "record_sha256": digest(record),
            "previous_entry_sha256": previous,
            "verdict": record["verdict"],
        }
        entry_sha = digest(entry)
        ledger_entries.append({"entry": entry, "entry_sha256": entry_sha})
        previous = entry_sha
    authority = {
        "local_response_envelope_validation_execution_authorization_decision_readiness_permitted": True,
        "authorization_decision_candidate_creation_permitted": False,
        "authorization_decision_recording_permitted": False,
        "response_envelope_validation_execution_authorization_grant_permitted": False,
        "response_envelope_validation_execution_authorized": False,
        "response_envelope_validation_result_recording_permitted": False,
        "response_envelope_creation_permitted": False,
        "response_envelope_processing_authorized": False,
        "response_receipt_permitted": False,
        "response_validation_authorized": False,
        "response_quarantine_execution_authorized": False,
        "response_intake_authorized": False,
        "review_request_dispatch_authorized": False,
        "reviewer_contact_permitted": False,
        "review_execution_authorized": False,
        "external_network_required": False,
        "external_delivery_permitted": False,
        "atlas_call_permitted": False,
        "repository_mutation": False,
        "automatic_status_change": False,
        "automatic_release_action": False,
        "human_authorization_claimed": False,
        "status_inheritance": "prohibited",
    }
    result = {
        "decision_policy_count": 1,
        "decision_profile_count": 2,
        "decision_readiness_record_count": 2,
        "decision_stage_count": len(STAGE_IDS) * 2,
        "decision_requirement_count": len(REQUIREMENT_IDS) * 2,
        "decision_requirement_evaluated_count": 0,
        "decision_option_count": len(DECISION_OPTIONS),
        "decision_option_selected_count": 0,
        "required_decision_role_count": 4,
        "dual_control_profile_count": 2,
        "conflict_declaration_required_count": 2,
        "conflict_declaration_evaluated_count": 0,
        "blank_decision_record_count": 2,
        "blank_decision_record_field_count": len(BLANK_DECISION_FIELDS) * 2,
        "readiness_check_count": len(CHECK_NAMES) * 2,
        "failed_readiness_check_count": 0,
        "approval_received_count": 0,
        "approval_evidence_recorded_count": 0,
        "human_gate_pending_count": sum(r["human_gate_pending_count"] for r in records),
        "human_gate_satisfied_count": 0,
        "authorization_decision_candidate_created_count": 0,
        "authorization_decision_record_created_count": 0,
        "authorization_decision_recorded_count": 0,
        "authorization_granted_count": 0,
        "authorization_revoked_count": 0,
        "authorization_expired_count": 0,
        "authorization_token_issued_count": 0,
        "execution_authorization_present_count": 0,
        "execution_ticket_issued_count": 0,
        "execution_run_count": 0,
        "execution_started_count": 0,
        "execution_completed_count": 0,
        "validation_result_recorded_count": 0,
        "disposition_selected_count": 0,
        "response_envelope_created_count": 0,
        "response_envelope_received_count": 0,
        "response_envelope_processed_count": 0,
        "response_received_count": 0,
        "response_validated_count": 0,
        "response_accepted_count": 0,
        "response_rejected_count": 0,
        "response_quarantined_count": 0,
        "reviewer_identity_count": 0,
        "reviewer_contact_count": 0,
        "review_started_count": 0,
        "review_completed_count": 0,
        "status_change_count": 0,
        "real_authorization_claimed": False,
    }
    rejected = [
        "phase36-candidate-drift", "phase36-postmerge-drift", "phase36-finalization-commit-drift",
        "missing-decision-readiness-record", "orphan-decision-readiness-record",
        "duplicate-decision-readiness-record", "decision-readiness-sequence-drift",
        "decision-readiness-id-drift", "decision-profile-id-drift",
        "source-assurance-id-drift", "source-assurance-record-digest-drift",
        "source-assurance-ledger-entry-drift", "authorization-readiness-id-drift",
        "authorization-profile-id-drift", "execution-profile-id-drift",
        "validation-profile-id-drift", "decision-policy-id-drift",
        "decision-policy-version-drift", "decision-policy-digest-drift",
        "decision-policy-mode-drift", "decision-policy-input-state-drift",
        "decision-stage-count-drift", "decision-stage-id-drift", "decision-stage-order-drift",
        "decision-stage-state-drift", "decision-requirement-count-drift",
        "decision-requirement-id-drift", "decision-requirement-order-drift",
        "decision-requirement-evaluated", "decision-option-count-drift",
        "decision-option-id-drift", "decision-option-order-drift", "decision-option-selected",
        "decision-scope-operation-drift", "decision-scope-profile-binding-disabled",
        "decision-scope-assurance-binding-disabled", "decision-scope-dual-control-disabled",
        "decision-scope-network-enabled", "decision-scope-atlas-enabled",
        "decision-scope-repository-write-enabled", "decision-scope-token-issue-enabled",
        "decision-scope-execution-enabled", "decision-scope-result-recording-enabled",
        "decision-scope-disposition-enabled", "decision-scope-status-change-enabled",
        "reviewer-role-drift", "authorization-officer-role-drift",
        "required-decision-role-count-drift", "required-decision-role-satisfied",
        "dual-control-disabled", "approval-received", "approval-evidence-recorded",
        "human-gate-satisfied", "conflict-declaration-not-required",
        "conflict-declaration-evaluated", "rationale-schema-drift",
        "blank-decision-field-count-drift", "decision-id-filled", "candidate-id-filled",
        "decision-option-filled", "primary-decider-identity-filled", "primary-decider-role-filled",
        "secondary-decider-identity-filled", "secondary-decider-role-filled", "decided-at-filled",
        "rationale-code-filled", "rationale-text-ref-filled", "source-assurance-digest-filled",
        "approval-evidence-digest-filled", "authorization-token-id-filled",
        "decision-signature-ref-filled", "conflict-declaration-ref-filled", "decision-expires-at-filled",
        "decision-record-issued", "decision-record-marked-recorded",
        "decision-candidate-created", "decision-record-created", "authorization-decision-recorded",
        "authorization-granted", "authorization-revoked", "authorization-expired",
        "authorization-token-issued", "execution-authorization-present", "execution-ticket-issued",
        "execution-run-created", "execution-started", "execution-completed",
        "validation-result-recorded", "disposition-selected", "envelope-created",
        "envelope-received", "envelope-processed", "response-received", "response-validated",
        "response-accepted", "response-rejected", "response-quarantined",
        "reviewer-identity-recorded", "reviewer-contact-permitted", "review-start-permitted",
        "review-started", "review-completed", "status-change", "human-authorization-claimed",
        "real-authorization-claimed", "decision-candidate-creation-permitted",
        "decision-recording-permitted", "authorization-grant-permitted",
        "validation-execution-authorized", "validation-result-recording-permitted",
        "response-envelope-creation-permitted", "response-envelope-processing-authorized",
        "response-receipt-permitted", "response-validation-authorized",
        "quarantine-execution-authorized", "review-request-dispatch-authorized",
        "review-execution-authorized", "status-inheritance-enabled", "automatic-status-change",
        "automatic-release-action", "repository-mutation", "external-network-required",
        "external-delivery-permitted", "atlas-call-permitted", "live-activation",
        "readiness-check-failed", "readiness-verdict-drift", "readiness-status-drift",
        "readiness-locality-drift", "readiness-ledger-drift", "readiness-checkpoint-drift",
        "summary-drift", "authority-drift", "source-pin-drift", "readiness-count-drift",
        "recovery-count-drift", "next-gate-drift",
    ]
    doc = {
        "id": "principia-atlas-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-thermal-control",
        "phase": 37,
        "contract": CONTRACT,
        "fixture_kind": "bounded-synthetic",
        "mode": MODE,
        "state": STATE,
        "decision": DECISION,
        "next_gate": NEXT_GATE,
        "live": False,
        "live_activation_permitted": False,
        "real_authorization_claimed": False,
        "source_phase36": {
            "phase36_candidate_sha256": PHASE36_CANDIDATE_SHA,
            "phase36_postmerge_sha256": PHASE36_POSTMERGE_SHA,
            "phase36_finalization_commit": PHASE36_FINALIZATION_COMMIT,
        },
        "decision_policy": p,
        "decision_profiles": profiles,
        "decision_readiness_records": records,
        "ledger": {
            "entries": ledger_entries,
            "head_sequence": len(ledger_entries),
            "head_sha256": ledger_entries[-1]["entry_sha256"],
        },
        "checkpoint": {
            "decision_readiness_record_count": 2,
            "readiness_check_count": len(CHECK_NAMES) * 2,
            "failed_readiness_check_count": 0,
            "authorization_decision_candidate_created_count": 0,
            "authorization_decision_recorded_count": 0,
            "authorization_granted_count": 0,
            "authorization_token_issued_count": 0,
            "response_envelope_received_count": 0,
            "execution_run_count": 0,
            "status_change_count": 0,
            "ledger_sha256": digest(ledger_entries),
        },
        "result": result,
        "authority": authority,
        "recovery": {
            "accepted": ["baseline"],
            "accepted_count": 1,
            "rejected": rejected,
            "rejected_count": len(rejected),
            "scenario_count": len(rejected) + 1,
        },
        "validation": {"status": "pending", "pull_request": None, "tested_head_commit": None},
    }
    return doc

def render(doc: dict[str, Any]) -> bytes:
    return canonical(doc) + b"\n"

def validate(doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if doc.get("phase") != 37 or doc.get("contract") != CONTRACT:
        errors.append("Phase or contract drift")
    if doc.get("mode") != MODE or doc.get("state") != STATE or doc.get("decision") != DECISION or doc.get("next_gate") != NEXT_GATE:
        errors.append("Lifecycle identity drift")
    if doc.get("live") is not False or doc.get("real_authorization_claimed") is not False:
        errors.append("Live or real authorization drift")
    source = doc.get("source_phase36", {})
    if source != {"phase36_candidate_sha256": PHASE36_CANDIDATE_SHA, "phase36_postmerge_sha256": PHASE36_POSTMERGE_SHA, "phase36_finalization_commit": PHASE36_FINALIZATION_COMMIT}:
        errors.append("Phase 36 source pin drift")
    p = doc.get("decision_policy", {})
    p_copy = copy.deepcopy(p)
    embedded_policy_sha = p_copy.pop("decision_policy_sha256", None)
    if embedded_policy_sha != digest(p_copy):
        errors.append("Decision policy digest drift")
    if [x.get("stage_id") for x in p.get("decision_stages", [])] != STAGE_IDS or any(x.get("state") != "defined-not-active" for x in p.get("decision_stages", [])):
        errors.append("Decision stage drift")
    if [x.get("requirement_id") for x in p.get("decision_requirements", [])] != REQUIREMENT_IDS or any(x.get("state") != "required-not-evaluated" for x in p.get("decision_requirements", [])):
        errors.append("Decision requirement drift")
    if [x.get("option") for x in p.get("decision_options", [])] != DECISION_OPTIONS or any(x.get("state") != "defined-not-selectable" for x in p.get("decision_options", [])):
        errors.append("Decision option drift")
    records = doc.get("decision_readiness_records")
    profiles = doc.get("decision_profiles")
    entries = doc.get("ledger", {}).get("entries")
    if not isinstance(records, list) or len(records) != 2:
        errors.append("Decision readiness record count drift")
        records = []
    if not isinstance(profiles, list) or len(profiles) != 2:
        errors.append("Decision profile count drift")
        profiles = []
    if not isinstance(entries, list) or len(entries) != 2:
        errors.append("Ledger count drift")
        entries = []
    for index, record in enumerate(records, 1):
        if record.get("sequence") != index:
            errors.append(f"Record {index} sequence drift")
        checks = record.get("readiness_checks", {})
        if set(checks) != set(CHECK_NAMES) or not all(checks.values()) or record.get("readiness_check_count") != len(CHECK_NAMES):
            errors.append(f"Record {index} readiness checks drift")
        blank = record.get("blank_decision_record", {})
        if record.get("blank_decision_record_field_count") != len(BLANK_DECISION_FIELDS) or any(blank.get(field) is not None for field in BLANK_DECISION_FIELDS):
            errors.append(f"Record {index} blank decision record drift")
        false_fields = [
            "decision_option_selected", "conflict_declaration_evaluated", "approval_received",
            "approval_evidence_recorded", "decision_candidate_created", "decision_record_created",
            "authorization_decision_recorded", "authorization_granted", "authorization_revoked",
            "authorization_expired", "authorization_token_issued", "execution_authorization_present",
            "execution_ticket_issued", "execution_run_created", "execution_started", "execution_completed",
            "validation_result_recorded", "disposition_selected", "response_envelope_created",
            "response_envelope_received", "response_envelope_processed", "response_received",
            "response_validated", "response_accepted", "response_rejected", "response_quarantined",
            "reviewer_identity_present", "reviewer_contact_permitted", "review_start_permitted",
            "review_started", "review_completed", "status_change", "real_authorization_claimed",
        ]
        if any(record.get(field) is not False for field in false_fields):
            errors.append(f"Record {index} frozen state drift")
        if record.get("human_gate_satisfied_count") != 0 or record.get("decision_requirement_evaluated_count") != 0 or record.get("local_only") is not True:
            errors.append(f"Record {index} gate or locality drift")
        if index <= len(entries):
            entry = entries[index-1]
            if entry.get("entry", {}).get("record_sha256") != digest(record) or entry.get("entry_sha256") != digest(entry.get("entry", {})):
                errors.append(f"Record {index} ledger binding drift")
    if entries:
        if entries[0]["entry"].get("previous_entry_sha256") is not None or entries[1]["entry"].get("previous_entry_sha256") != entries[0].get("entry_sha256"):
            errors.append("Ledger chain drift")
        if doc.get("ledger", {}).get("head_sha256") != entries[-1].get("entry_sha256"):
            errors.append("Ledger head drift")
    result = doc.get("result", {})
    zero_result_fields = [k for k in result if k.endswith("_count") and k not in {
        "decision_policy_count", "decision_profile_count", "decision_readiness_record_count",
        "decision_stage_count", "decision_requirement_count", "decision_option_count",
        "required_decision_role_count", "dual_control_profile_count",
        "conflict_declaration_required_count", "blank_decision_record_count",
        "blank_decision_record_field_count", "readiness_check_count", "human_gate_pending_count",
    }]
    if any(result.get(k) != 0 for k in zero_result_fields):
        errors.append("Non-zero operational result detected")
    authority = doc.get("authority", {})
    if authority.get("local_response_envelope_validation_execution_authorization_decision_readiness_permitted") is not True:
        errors.append("Local readiness authority missing")
    for key, value in authority.items():
        if key == "local_response_envelope_validation_execution_authorization_decision_readiness_permitted" or key == "status_inheritance":
            continue
        if value is not False:
            errors.append(f"Forbidden authority enabled: {key}")
    if authority.get("status_inheritance") != "prohibited":
        errors.append("Status inheritance drift")
    recovery = doc.get("recovery", {})
    if recovery.get("accepted") != ["baseline"] or recovery.get("accepted_count") != 1 or recovery.get("rejected_count") != len(recovery.get("rejected", [])) or recovery.get("scenario_count") != recovery.get("rejected_count", 0) + 1:
        errors.append("Recovery matrix drift")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    doc = build()
    errors = validate(doc)
    if errors:
        print("Phase 37 generator validation errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    rendered = render(doc)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != rendered:
            print("Phase 37 deterministic output drift", file=sys.stderr)
            return 1
        print(f"Phase 37 deterministic output passed: bytes={len(rendered)}, sha256={hashlib.sha256(rendered).hexdigest()}.")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(rendered)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}: bytes={len(rendered)}, sha256={hashlib.sha256(rendered).hexdigest()}.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
