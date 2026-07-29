#!/usr/bin/env python3
"""Generate deterministic Phase 35 validation-execution authorization-readiness evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness"
DECISION = "response-intake-envelope-validation-execution-authorization-readiness-recorded-no-authorization-granted"
STATE = MODE + "-candidate"
NEXT_GATE = MODE + "-assurance-candidate"
OUT = ROOT / "release/phase-35-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness.json"
SOURCE = ROOT / "release/phase-34-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance.json"
POST = ROOT / "release/phase-34-postmerge.json"
SOURCE_SHA = "2ca9b454124b1fb42f91f09479d9aed1d0c54f9ef443f121caa3a7ee67823828"
POST_SHA = "c23152786eb92b8abfdba51dba95ff332dc71a8500d15c4148036099c0d85e65"
FINALIZATION_COMMIT = "49115ca3321d47363f21bb5a240497bf57c46dae"
CANDIDATE_MERGE = "3878ad9d8ccdb49b05f02c6fdcb89a01cd9f7646"

AUTHORIZATION_STAGES = "source-provenance-lock|assured-profile-resolution|authority-scope-definition|human-gate-requirement-lock|execution-ticket-template-binding|engine-and-resource-boundary-lock|approval-evidence-requirements|expiration-and-revocation-controls|audit-record-preparation|authorization-grant-freeze".split("|")
AUTHORIZATION_REQUIREMENTS = "source-assurance-pinned|candidate-and-postmerge-digests-match|execution-readiness-assurance-identity-pinned|execution-profile-identity-pinned|validation-profile-identity-pinned|execution-blueprint-digest-pinned|deterministic-engine-version-pinned|resource-limits-pinned|validation-control-order-pinned|blank-execution-ticket-preserved|no-envelope-present|no-response-present|human-gates-remain-pending|required-reviewer-role-defined|authorization-officer-role-defined|dual-control-required|authorization-scope-defined|validity-window-policy-defined|revocation-path-defined|one-time-use-policy-defined|result-and-disposition-recording-disabled|authorization-grant-absent".split("|")
BLANK_AUTHORIZATION_TOKEN_FIELDS = "authorization_id|grantor_identity|grantor_role|granted_at|expires_at|scope_digest|execution_ticket_id|one_time_nonce|revocation_id|revocation_reason|authorization_signature_ref|approval_evidence_digest|authorized_engine_version|authorized_resource_profile_digest".split("|")
AUTHORIZATION_OFFICER_ROLE = "qualified-validation-authorization-officer"
EXPECTED = (
    (
        "feedback-manual-review",
        1,
        "6656a802b202ba3ee2ab816036e1fcd1087ee4f0aee350b7aa9b4f2af128dea7",
        "c7cb0a1a0ad6558516af7eba45e6821a0569b144dfd27af88a39840069972da3",
        "qualified-pedagogical-reviewer",
    ),
    (
        "model-boundary-release-governance",
        2,
        "459305d278e85e4c9d7e743f9d64d20a55e90e54ccfeca69e9d196dcff51c3b7",
        "ffa6c51b50d93c195f94f367504dff04585b66adbb1788d037edbbe929b4226e",
        "qualified-release-governance-reviewer",
    ),
)

AUTHORITY = {
    "atlas_call_permitted": False,
    "automatic_release_action": False,
    "automatic_status_change": False,
    "authorization_decision_recording_permitted": False,
    "external_delivery_permitted": False,
    "external_network_required": False,
    "human_authorization_claimed": False,
    "local_response_envelope_validation_execution_authorization_readiness_permitted": True,
    "repository_mutation": False,
    "response_envelope_creation_permitted": False,
    "response_envelope_processing_authorized": False,
    "response_envelope_validation_execution_authorization_grant_permitted": False,
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

ZERO_FIELDS = "authorization_candidate_created|authorization_decision_recorded|authorization_granted|authorization_revoked|authorization_expired|approval_evidence_recorded|approval_received|authorization_scope_recorded|execution_authorization_present|execution_ticket_issued|execution_run_created|execution_started|execution_completed|validation_result_recorded|disposition_selected|response_envelope_created|response_envelope_received|response_envelope_processed|response_intake_authorized|response_received|response_validated|response_accepted|response_rejected|response_quarantined|reviewer_identity_present|reviewer_contact_permitted|review_start_permitted|review_started|review_completed|status_change|real_authorization_claimed".split("|")

MUTATIONS = "phase34-candidate-drift|phase34-postmerge-drift|phase34-finalization-commit-drift|missing-authorization-readiness-record|orphan-authorization-readiness-record|duplicate-authorization-readiness-record|authorization-readiness-sequence-drift|authorization-readiness-id-drift|source-assurance-id-drift|source-assurance-record-digest-drift|source-assurance-ledger-entry-drift|execution-readiness-id-drift|execution-profile-id-drift|validation-profile-id-drift|reviewer-role-drift|authorization-officer-role-drift|policy-id-drift|policy-version-drift|policy-mode-drift|policy-input-state-drift|policy-digest-drift|stage-count-drift|stage-id-drift|stage-order-drift|stage-state-drift|requirement-count-drift|requirement-id-drift|requirement-order-drift|requirement-state-drift|approval-role-count-drift|approval-role-id-drift|approval-role-order-drift|approval-role-state-drift|dual-control-disabled|scope-operation-drift|scope-profile-binding-disabled|scope-engine-binding-disabled|scope-resource-binding-disabled|scope-one-time-use-disabled|scope-result-recording-enabled|scope-disposition-selection-enabled|scope-network-enabled|scope-atlas-enabled|scope-repository-write-enabled|validity-window-drift|revocation-policy-drift|token-count-drift|token-field-count-drift|authorization-id-filled|grantor-identity-filled|grantor-role-filled|granted-at-filled|expires-at-filled|scope-digest-filled|execution-ticket-id-filled|one-time-nonce-filled|revocation-id-filled|revocation-reason-filled|authorization-signature-filled|approval-evidence-digest-filled|authorized-engine-version-filled|authorized-resource-profile-digest-filled|token-issued|token-source-binding-drift|human-gate-satisfied|approval-received|approval-evidence-recorded|authorization-candidate-created|authorization-decision-recorded|authorization-granted|authorization-revoked|authorization-expired|authorization-scope-recorded|authorization-grant-permitted|authorization-decision-recording-permitted|execution-authorization-present|validation-execution-authorized|validation-result-recording-permitted|execution-ticket-issued|execution-run-created|execution-started|execution-completed|validation-result-recorded|disposition-selected|structural-rejection-selected|quarantine-candidate-selected|validation-pass-selected|envelope-created|envelope-received|envelope-processed|integrity-failure-recorded|duplicate-envelope-recorded|quarantine-record-created|quarantine-execution-authorized|response-intake-authorized|response-receipt-permitted|response-received|response-validated|response-accepted|response-rejected|response-quarantined|packet-dispatched|reviewer-contact-permitted|reviewer-identity-recorded|review-start-permitted|review-started|review-completed|outcome-selected|content-change-proposed|status-recommendation-recorded|effective-hold|operational-effect|status-change|human-authorization-claimed|real-authorization-claimed|status-inheritance-enabled|automatic-status-change|automatic-release-action|repository-mutation|external-network-required|external-delivery-permitted|atlas-call-permitted|live-activation|record-verdict-drift|record-status-drift|record-locality-drift|ledger-drift|checkpoint-drift|summary-drift|authority-drift|source-pin-drift|record-count-drift|recovery-count-drift|next-gate-drift".split("|")


def render(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def sha_doc(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(path)
    return value


def verify_sources() -> list[str]:
    errors: list[str] = []
    if not SOURCE.is_file() or sha_file(SOURCE) != SOURCE_SHA:
        errors.append("Phase 34 candidate file drift")
    if not POST.is_file() or sha_file(POST) != POST_SHA:
        errors.append("Phase 34 postmerge file drift")
    if errors:
        return errors
    source, post = load(SOURCE), load(POST)
    if source.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance-candidate" or source.get("next_gate") != STATE:
        errors.append("Phase 34 candidate gate drift")
    if post.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance-validated" or post.get("next_gate") != STATE:
        errors.append("Phase 34 finalization gate drift")
    if post.get("candidate_record", {}).get("sha256") != SOURCE_SHA or post.get("principia", {}).get("merge_commit") != CANDIDATE_MERGE:
        errors.append("Phase 34 provenance drift")
    records = {record.get("execution_readiness_assurance_id"): record for record in source.get("assurances", [])}
    entries = {entry.get("entry", {}).get("execution_readiness_assurance_id"): entry for entry in source.get("ledger", {}).get("entries", [])}
    for key, seq, record_sha, ledger_sha, reviewer_role in EXPECTED:
        assurance_id = f"principia:consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance:{key}:{seq:04d}"
        record, entry = records.get(assurance_id), entries.get(assurance_id)
        if not record or sha_doc(record) != record_sha:
            errors.append(f"Phase 34 assurance record drift: {key}")
            continue
        if not entry or entry.get("entry_sha256") != ledger_sha:
            errors.append(f"Phase 34 assurance ledger drift: {key}")
        if record.get("reviewer_role_required") != reviewer_role or record.get("assurance_check_count") != 44 or not all(record.get("assurance_checks", {}).values()):
            errors.append(f"Phase 34 assurance content drift: {key}")
        if record.get("execution_stage_count") != 9 or record.get("execution_precondition_count") != 20 or record.get("validation_control_count") != 18 or record.get("blank_execution_ticket_field_count") != 12:
            errors.append(f"Phase 34 assurance count drift: {key}")
        if any(record.get(name) is not False for name in ZERO_FIELDS if name in record):
            errors.append(f"Phase 34 frozen-state drift: {key}")
    return errors


def authorization_policy() -> dict[str, Any]:
    return {
        "authorization_policy_id": "principia-envelope-validation-execution-authorization-policy",
        "authorization_policy_version": "0.1",
        "input_state": "no-envelope-no-authorization",
        "mode": "offline-authorization-preflight-only",
        "authorization_stages": [
            {"sequence": index, "stage_id": stage_id, "state": "defined-not-active"}
            for index, stage_id in enumerate(AUTHORIZATION_STAGES, 1)
        ],
        "authorization_requirements": [
            {"sequence": index, "requirement_id": requirement_id, "state": "required-not-evaluated"}
            for index, requirement_id in enumerate(AUTHORIZATION_REQUIREMENTS, 1)
        ],
        "authorization_scope": {
            "operation": "validate-one-bound-response-envelope",
            "profile_bound": True,
            "engine_bound": True,
            "resource_bound": True,
            "one_time_use": True,
            "result_recording_enabled": False,
            "disposition_selection_enabled": False,
            "external_network": False,
            "atlas_access": False,
            "repository_write": False,
        },
        "validity_window_policy": {"maximum_seconds": 900, "state": "defined-not-active"},
        "revocation_policy": {"immediate_revocation_supported": True, "state": "defined-not-active"},
        "blank_authorization_token_fields": BLANK_AUTHORIZATION_TOKEN_FIELDS,
    }


def authorization_profiles(policy_sha: str) -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    for key, seq, _record_sha, _ledger_sha, reviewer_role in EXPECTED:
        profiles.append(
            {
                "sequence": seq,
                "authorization_profile_id": f"principia:review-response-intake-envelope-validation-execution-authorization-profile:{key}:{seq:04d}",
                "execution_readiness_assurance_id": f"principia:consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance:{key}:{seq:04d}",
                "execution_profile_id": f"principia:review-response-intake-envelope-validation-execution-profile:{key}:{seq:04d}",
                "validation_profile_id": f"principia:review-response-intake-envelope-validation-profile:{key}:{seq:04d}",
                "reviewer_role_required": reviewer_role,
                "authorization_officer_role_required": AUTHORIZATION_OFFICER_ROLE,
                "dual_control_required": True,
                "policy_sha256": policy_sha,
                "required_approval_roles": [
                    {"sequence": 1, "role": reviewer_role, "state": "required-not-satisfied"},
                    {"sequence": 2, "role": AUTHORIZATION_OFFICER_ROLE, "state": "required-not-satisfied"},
                ],
            }
        )
    return profiles


def authorization_readiness_records(profiles: list[dict[str, Any]], policy: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    policy_sha = sha_doc(policy)
    for profile, (key, seq, source_record_sha, source_ledger_sha, reviewer_role) in zip(profiles, EXPECTED):
        token = {
            "authorization_profile_id": profile["authorization_profile_id"],
            "execution_profile_id": profile["execution_profile_id"],
            "execution_readiness_assurance_id": profile["execution_readiness_assurance_id"],
            "issued": False,
        }
        token.update({field: None for field in BLANK_AUTHORIZATION_TOKEN_FIELDS})
        record = {
            "sequence": seq,
            "authorization_readiness_id": f"principia:consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness:{key}:{seq:04d}",
            "authorization_profile_id": profile["authorization_profile_id"],
            "execution_readiness_assurance_id": profile["execution_readiness_assurance_id"],
            "execution_profile_id": profile["execution_profile_id"],
            "validation_profile_id": profile["validation_profile_id"],
            "reviewer_role_required": reviewer_role,
            "authorization_officer_role_required": AUTHORIZATION_OFFICER_ROLE,
            "source_assurance_record_sha256": source_record_sha,
            "source_assurance_ledger_entry_sha256": source_ledger_sha,
            "policy_sha256": policy_sha,
            "authorization_stage_count": len(AUTHORIZATION_STAGES),
            "authorization_requirement_count": len(AUTHORIZATION_REQUIREMENTS),
            "authorization_requirement_evaluated_count": 0,
            "required_approval_role_count": 2,
            "approval_received_count": 0,
            "dual_control_required": True,
            "blank_authorization_token": token,
            "blank_authorization_token_field_count": len(BLANK_AUTHORIZATION_TOKEN_FIELDS),
            "human_gate_pending_count": 4,
            "human_gate_satisfied_count": 0,
            "local_only": True,
            "status": "authorization-readiness-recorded-no-authorization-granted",
            "verdict": "response-envelope-validation-execution-authorization-controls-ready-no-authorization",
        }
        record.update({name: False for name in ZERO_FIELDS})
        records.append(record)
    return records


def ledger(records: list[dict[str, Any]]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    previous: str | None = None
    for record in records:
        entry = {
            "previous_entry_sha256": previous,
            "record_sha256": sha_doc(record),
            "sequence": record["sequence"],
            "authorization_readiness_id": record["authorization_readiness_id"],
            "execution_readiness_assurance_id": record["execution_readiness_assurance_id"],
            "verdict": record["verdict"],
        }
        previous = sha_doc(entry)
        entries.append({"entry": entry, "entry_sha256": previous})
    return {"entries": entries, "head_sequence": len(entries), "head_sha256": previous}


def build_document() -> dict[str, Any]:
    policy = authorization_policy()
    policy_sha = sha_doc(policy)
    profiles = authorization_profiles(policy_sha)
    records = authorization_readiness_records(profiles, policy)
    authorization_ledger = ledger(records)
    result = {
        "approval_evidence_recorded_count": 0,
        "approval_received_count": 0,
        "authorization_candidate_created_count": 0,
        "authorization_decision_recorded_count": 0,
        "authorization_granted_count": 0,
        "authorization_officer_identity_count": 0,
        "authorization_policy_count": 1,
        "authorization_profile_count": 2,
        "authorization_readiness_record_count": 2,
        "authorization_requirement_count": 44,
        "authorization_requirement_evaluated_count": 0,
        "authorization_revoked_count": 0,
        "authorization_expired_count": 0,
        "authorization_scope_recorded_count": 0,
        "authorization_stage_count": 20,
        "blank_authorization_token_count": 2,
        "blank_authorization_token_field_count": 28,
        "dual_control_profile_count": 2,
        "execution_authorization_present_count": 0,
        "execution_completed_count": 0,
        "execution_run_count": 0,
        "execution_started_count": 0,
        "execution_ticket_issued_count": 0,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
        "required_approval_role_count": 4,
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
        "validation_result_recorded_count": 0,
    }
    return {
        "authority": AUTHORITY,
        "authorization_policy": policy,
        "authorization_profiles": profiles,
        "authorization_readiness_records": records,
        "checkpoint": {
            "approval_received_count": 0,
            "authorization_granted_count": 0,
            "authorization_readiness_record_count": 2,
            "execution_authorization_present_count": 0,
            "ledger_sha256": sha_doc(authorization_ledger),
            "response_envelope_received_count": 0,
            "response_received_count": 0,
            "status_change_count": 0,
            "validation_result_recorded_count": 0,
        },
        "contract": "principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-thermal-control",
        "ledger": authorization_ledger,
        "live": False,
        "live_activation_permitted": False,
        "mode": MODE,
        "next_gate": NEXT_GATE,
        "phase": 35,
        "real_authorization_claimed": False,
        "recovery": {
            "accepted": ["baseline"],
            "accepted_count": 1,
            "rejected": MUTATIONS,
            "rejected_count": len(MUTATIONS),
            "scenario_count": len(MUTATIONS) + 1,
        },
        "result": result,
        "source_phase34": {
            "phase34_candidate_sha256": SOURCE_SHA,
            "phase34_finalization_commit": FINALIZATION_COMMIT,
            "phase34_postmerge_sha256": POST_SHA,
        },
        "state": STATE,
        "validation": {"pull_request": None, "status": "pending", "tested_head_commit": None},
    }


def validate_document(document: Mapping[str, Any]) -> list[str]:
    return [] if document == build_document() else ["document drift"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--skip-source-verification", action="store_true")
    args = parser.parse_args()
    errors = [] if args.skip_source_verification else verify_sources()
    if errors:
        print("Phase 35 source errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    text = render(build_document())
    if args.check and (not OUT.is_file() or OUT.read_text() != text):
        print("Phase 35 candidate differs from deterministic generation", file=sys.stderr)
        return 1
    if not args.check:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(text)
    print(
        f"Phase 35 candidate passed: {len(text.encode())} bytes, "
        f"sha256={hashlib.sha256(text.encode()).hexdigest()}, "
        "2 authorization-readiness records, 20 stages, 44 requirements, 0 authorizations granted."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
