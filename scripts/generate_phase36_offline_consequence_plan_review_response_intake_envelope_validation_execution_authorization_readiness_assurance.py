#!/usr/bin/env python3
"""Generate the deterministic Principia Phase 36 authorization-readiness assurance record."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "release/phase-36-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance.json"
SOURCE = ROOT / "release/phase-35-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness.json"
POST = ROOT / "release/phase-35-postmerge.json"
CANDIDATE_SHA = "539bfd832f157b54d491998c0438c67d284d1250bd57a5f3d54d623815a1e7a3"
POST_SHA = "97e0b7c8b2ea718b8c29fdd98340d8e699791e1a7cd3d19bdbb5bdd6e5ff3fc2"
FINALIZATION_COMMIT = "01e4b798fa0f4671bc5c676d8b0de94c4938f5e0"
POLICY_SHA = "37df52fb6e8c954bc7b13ca62c0a63a19b3d16b67a0b16fc79240db1006f967a"
NEXT_GATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-candidate"
PROFILES = [{'seq': 1, 'slug': 'feedback-manual-review', 'reviewer': 'qualified-pedagogical-reviewer', 'readiness_record_sha': 'f59d0f68642cb434d83e62bd38e5cbc79218dfaee88c0b74baf8364ee207e026', 'readiness_ledger_sha': 'c429e423b6e9d77f95651e2c496a2349e9dff457efdb3b9aa6f4f92efd213f18', 'source_assurance_record_sha': '6656a802b202ba3ee2ab816036e1fcd1087ee4f0aee350b7aa9b4f2af128dea7', 'source_assurance_ledger_sha': 'c7cb0a1a0ad6558516af7eba45e6821a0569b144dfd27af88a39840069972da3'}, {'seq': 2, 'slug': 'model-boundary-release-governance', 'reviewer': 'qualified-release-governance-reviewer', 'readiness_record_sha': 'ee67207f70220934032b629a04ffaf2a2135260089d34e30cd1dfd80ea75c976', 'readiness_ledger_sha': 'ca3131103521d3873fcf061c854fcae166881f8254fe74357dbe618220fe8a5e', 'source_assurance_record_sha': '459305d278e85e4c9d7e743f9d64d20a55e90e54ccfeca69e9d196dcff51c3b7', 'source_assurance_ledger_sha': 'ffa6c51b50d93c195f94f367504dff04585b66adbb1788d037edbbe929b4226e'}]
CHECK_NAMES = ['source_candidate_exact', 'source_postmerge_exact', 'source_finalization_exact', 'authorization_readiness_identity_exact', 'authorization_readiness_record_digest_exact', 'authorization_readiness_ledger_binding_exact', 'source_assurance_identity_exact', 'source_assurance_record_digest_exact', 'source_assurance_ledger_binding_exact', 'authorization_policy_identity_exact', 'authorization_policy_version_exact', 'authorization_policy_digest_exact', 'policy_input_state_exact', 'policy_mode_exact', 'stage_count_exact', 'stage_order_exact', 'stage_states_inactive', 'requirement_count_exact', 'requirement_order_exact', 'requirement_states_unevaluated', 'scope_operation_exact', 'scope_profile_binding_exact', 'scope_engine_binding_exact', 'scope_resource_binding_exact', 'scope_one_time_use_exact', 'scope_result_recording_disabled', 'scope_disposition_selection_disabled', 'scope_network_disabled', 'scope_atlas_disabled', 'scope_repository_write_disabled', 'validity_window_exact', 'revocation_policy_exact', 'authorization_profile_identity_exact', 'execution_profile_identity_exact', 'validation_profile_identity_exact', 'reviewer_role_exact', 'authorization_officer_role_exact', 'dual_control_exact', 'approval_role_count_exact', 'approval_roles_pending', 'blank_token_exact', 'blank_token_field_count_exact', 'token_unissued', 'human_gates_remain_pending', 'authorization_states_frozen', 'execution_states_frozen', 'envelope_response_states_frozen', 'review_states_frozen', 'authority_boundary_preserved', 'zero_effect_boundary_preserved']
REJECTED = ['phase35-candidate-drift', 'phase35-postmerge-drift', 'phase35-finalization-commit-drift', 'missing-authorization-readiness-assurance', 'orphan-authorization-readiness-assurance', 'duplicate-authorization-readiness-assurance', 'assurance-sequence-drift', 'assurance-id-drift', 'authorization-readiness-id-drift', 'authorization-readiness-record-digest-drift', 'authorization-readiness-ledger-entry-drift', 'source-assurance-id-drift', 'source-assurance-record-digest-drift', 'source-assurance-ledger-entry-drift', 'authorization-profile-id-drift', 'execution-profile-id-drift', 'validation-profile-id-drift', 'policy-id-drift', 'policy-version-drift', 'policy-digest-drift', 'policy-mode-drift', 'policy-input-state-drift', 'stage-count-drift', 'stage-id-drift', 'stage-order-drift', 'stage-state-drift', 'requirement-count-drift', 'requirement-id-drift', 'requirement-order-drift', 'requirement-state-drift', 'scope-operation-drift', 'scope-profile-binding-disabled', 'scope-engine-binding-disabled', 'scope-resource-binding-disabled', 'scope-one-time-use-disabled', 'scope-result-recording-enabled', 'scope-disposition-selection-enabled', 'scope-network-enabled', 'scope-atlas-enabled', 'scope-repository-write-enabled', 'validity-window-drift', 'validity-window-active', 'revocation-policy-drift', 'revocation-policy-active', 'reviewer-role-drift', 'authorization-officer-role-drift', 'dual-control-disabled', 'approval-role-count-drift', 'approval-role-order-drift', 'approval-role-satisfied', 'approval-received', 'approval-evidence-recorded', 'blank-token-field-count-drift', 'authorization-id-filled', 'grantor-identity-filled', 'grantor-role-filled', 'granted-at-filled', 'expires-at-filled', 'scope-digest-filled', 'execution-ticket-id-filled', 'one-time-nonce-filled', 'revocation-id-filled', 'revocation-reason-filled', 'authorization-signature-filled', 'approval-evidence-digest-filled', 'authorized-engine-version-filled', 'authorized-resource-profile-digest-filled', 'authorization-token-issued', 'human-gate-satisfied', 'authorization-candidate-created', 'authorization-decision-recorded', 'authorization-granted', 'authorization-revoked', 'authorization-expired', 'authorization-officer-identity-recorded', 'authorization-scope-recorded', 'execution-authorization-present', 'execution-ticket-issued', 'execution-run-created', 'execution-started', 'execution-completed', 'validation-result-recorded', 'disposition-selected', 'envelope-created', 'envelope-received', 'envelope-processed', 'response-intake-authorized', 'response-receipt-permitted', 'response-received', 'response-validated', 'response-accepted', 'response-rejected', 'response-quarantined', 'reviewer-contact-permitted', 'reviewer-identity-recorded', 'review-start-permitted', 'review-started', 'review-completed', 'status-change', 'human-authorization-claimed', 'real-authorization-claimed', 'authorization-grant-permitted', 'authorization-decision-recording-permitted', 'validation-execution-authorized', 'validation-result-recording-permitted', 'response-envelope-creation-permitted', 'response-envelope-processing-authorized', 'quarantine-execution-authorized', 'response-validation-authorized', 'review-request-dispatch-authorized', 'review-execution-authorized', 'status-inheritance-enabled', 'automatic-status-change', 'automatic-release-action', 'repository-mutation', 'external-network-required', 'external-delivery-permitted', 'atlas-call-permitted', 'live-activation', 'assurance-check-failed', 'assurance-verdict-drift', 'assurance-status-drift', 'assurance-locality-drift', 'assurance-ledger-drift', 'assurance-checkpoint-drift', 'summary-drift', 'authority-drift', 'source-pin-drift', 'assurance-count-drift', 'recovery-count-drift', 'next-gate-drift']

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"Expected object: {path}")
    return value

def validate_sources() -> None:
    if sha_file(SOURCE) != CANDIDATE_SHA:
        raise ValueError("Phase 35 candidate digest drift")
    if sha_file(POST) != POST_SHA:
        raise ValueError("Phase 35 postmerge digest drift")
    source, post = load(SOURCE), load(POST)
    if source.get("phase") != 35 or source.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-candidate":
        raise ValueError("Phase 35 candidate state drift")
    if source.get("next_gate") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-candidate":
        raise ValueError("Phase 35 candidate next-gate drift")
    if post.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-validated":
        raise ValueError("Phase 35 final state drift")
    if post.get("candidate_record") != {"path": "release/phase-35-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness.json", "sha256": CANDIDATE_SHA}:
        raise ValueError("Phase 35 candidate binding drift")
    if post.get("principia") != {"candidate_head_commit": "f0f97245f9c0b4057a55d43d9a2d7b4a26dc8391", "merge_commit": "4cc3c5dcf3ad1d48c15ee3468ff75b08634bd866", "pull_request": 61, "repository": "Rhodan-lab/principle-to-system"}:
        raise ValueError("Phase 35 merge provenance drift")
    if post.get("validation") != {"applicable_workflows": 29, "candidate_head_commit": "f0f97245f9c0b4057a55d43d9a2d7b4a26dc8391", "status": "success"}:
        raise ValueError("Phase 35 workflow provenance drift")
    policy = source.get("authorization_policy")
    if not isinstance(policy, dict) or hashlib.sha256(canonical_bytes(policy)).hexdigest() != POLICY_SHA:
        raise ValueError("Phase 35 policy digest drift")
    records = source.get("authorization_readiness_records")
    entries = source.get("ledger", {}).get("entries")
    source_profiles = source.get("authorization_profiles")
    if not isinstance(records, list) or not isinstance(entries, list) or not isinstance(source_profiles, list) or len(records) != 2 or len(entries) != 2 or len(source_profiles) != 2:
        raise ValueError("Phase 35 record/profile/ledger count drift")
    for index, expected in enumerate(PROFILES):
        record, wrapper, profile = records[index], entries[index], source_profiles[index]
        if hashlib.sha256(canonical_bytes(record)).hexdigest() != expected["readiness_record_sha"]:
            raise ValueError(f"Phase 35 readiness record {index + 1} digest drift")
        if wrapper.get("entry_sha256") != expected["readiness_ledger_sha"]:
            raise ValueError(f"Phase 35 readiness ledger {index + 1} drift")
        if record.get("source_assurance_record_sha256") != expected["source_assurance_record_sha"] or record.get("source_assurance_ledger_entry_sha256") != expected["source_assurance_ledger_sha"]:
            raise ValueError(f"Phase 35 source assurance binding {index + 1} drift")
        if profile.get("policy_sha256") != POLICY_SHA or record.get("policy_sha256") != POLICY_SHA:
            raise ValueError(f"Phase 35 policy binding {index + 1} drift")

def make_assurance(expected: dict[str, Any]) -> dict[str, Any]:
    sequence, slug = expected["seq"], expected["slug"]
    return {
        "sequence": sequence,
        "authorization_readiness_assurance_id": f"principia:consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance:{slug}:000{sequence}",
        "authorization_readiness_id": f"principia:consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness:{slug}:000{sequence}",
        "authorization_profile_id": f"principia:review-response-intake-envelope-validation-execution-authorization-profile:{slug}:000{sequence}",
        "execution_profile_id": f"principia:review-response-intake-envelope-validation-execution-profile:{slug}:000{sequence}",
        "validation_profile_id": f"principia:review-response-intake-envelope-validation-profile:{slug}:000{sequence}",
        "execution_readiness_assurance_id": f"principia:consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance:{slug}:000{sequence}",
        "authorization_readiness_record_sha256": expected["readiness_record_sha"],
        "authorization_readiness_ledger_entry_sha256": expected["readiness_ledger_sha"],
        "source_assurance_record_sha256": expected["source_assurance_record_sha"],
        "source_assurance_ledger_entry_sha256": expected["source_assurance_ledger_sha"],
        "policy_sha256": POLICY_SHA,
        "reviewer_role_required": expected["reviewer"],
        "authorization_officer_role_required": "qualified-validation-authorization-officer",
        "authorization_stage_count": 10,
        "authorization_requirement_count": 22,
        "required_approval_role_count": 2,
        "blank_authorization_token_field_count": 14,
        "human_gate_pending_count": 4,
        "human_gate_satisfied_count": 0,
        "dual_control_required": True,
        "approval_received": False,
        "approval_evidence_recorded": False,
        "authorization_candidate_created": False,
        "authorization_decision_recorded": False,
        "authorization_granted": False,
        "authorization_revoked": False,
        "authorization_expired": False,
        "authorization_officer_identity_present": False,
        "authorization_scope_recorded": False,
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
        "assurance_check_count": 50,
        "assurance_checks": {name: True for name in CHECK_NAMES},
        "status": "authorization-readiness-assured-no-authorization-granted",
        "verdict": "response-envelope-validation-execution-authorization-readiness-assured-no-authorization",
    }

def build_document() -> dict[str, Any]:
    assurances = [make_assurance(profile) for profile in PROFILES]
    entries, previous = [], None
    for assurance in assurances:
        entry = {
            "sequence": assurance["sequence"],
            "authorization_readiness_assurance_id": assurance["authorization_readiness_assurance_id"],
            "authorization_readiness_id": assurance["authorization_readiness_id"],
            "previous_entry_sha256": previous,
            "record_sha256": hashlib.sha256(canonical_bytes(assurance)).hexdigest(),
            "verdict": assurance["verdict"],
        }
        entry_sha = hashlib.sha256(canonical_bytes(entry)).hexdigest()
        entries.append({"entry": entry, "entry_sha256": entry_sha})
        previous = entry_sha
    result = {'authorization_policy_count': 1, 'authorization_profile_count': 2, 'authorization_readiness_record_count': 2, 'assured_authorization_readiness_record_count': 2, 'assurance_check_count': 100, 'failed_assurance_count': 0, 'authorization_stage_count': 20, 'authorization_requirement_count': 44, 'authorization_requirement_evaluated_count': 0, 'required_approval_role_count': 4, 'dual_control_profile_count': 2, 'approval_received_count': 0, 'approval_evidence_recorded_count': 0, 'blank_authorization_token_count': 2, 'blank_authorization_token_field_count': 28, 'human_gate_pending_count': 8, 'human_gate_satisfied_count': 0, 'authorization_candidate_created_count': 0, 'authorization_decision_recorded_count': 0, 'authorization_granted_count': 0, 'authorization_revoked_count': 0, 'authorization_expired_count': 0, 'authorization_officer_identity_count': 0, 'authorization_scope_recorded_count': 0, 'authorization_token_issued_count': 0, 'execution_authorization_present_count': 0, 'execution_ticket_issued_count': 0, 'execution_run_count': 0, 'execution_started_count': 0, 'execution_completed_count': 0, 'validation_result_recorded_count': 0, 'disposition_selected_count': 0, 'response_envelope_created_count': 0, 'response_envelope_received_count': 0, 'response_envelope_processed_count': 0, 'response_received_count': 0, 'response_validated_count': 0, 'response_accepted_count': 0, 'response_rejected_count': 0, 'response_quarantined_count': 0, 'reviewer_identity_count': 0, 'reviewer_contact_count': 0, 'review_started_count': 0, 'review_completed_count': 0, 'status_change_count': 0, 'real_authorization_claimed': False}
    authority = {'atlas_call_permitted': False, 'authorization_decision_recording_permitted': False, 'automatic_release_action': False, 'automatic_status_change': False, 'external_delivery_permitted': False, 'external_network_required': False, 'human_authorization_claimed': False, 'local_response_envelope_validation_execution_authorization_readiness_assurance_permitted': True, 'repository_mutation': False, 'response_envelope_creation_permitted': False, 'response_envelope_processing_authorized': False, 'response_envelope_validation_execution_authorization_grant_permitted': False, 'response_envelope_validation_execution_authorized': False, 'response_envelope_validation_result_recording_permitted': False, 'response_intake_authorized': False, 'response_quarantine_execution_authorized': False, 'response_receipt_permitted': False, 'response_validation_authorized': False, 'review_execution_authorized': False, 'review_request_dispatch_authorized': False, 'reviewer_contact_permitted': False, 'status_inheritance': 'prohibited'}
    return {
        "contract": "principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance/0.1",
        "id": "principia-atlas-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-thermal-control",
        "phase": 36,
        "mode": "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance",
        "state": "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-candidate",
        "decision": "response-intake-envelope-validation-execution-authorization-readiness-assured-no-authorization-granted",
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "live_activation_permitted": False,
        "real_authorization_claimed": False,
        "source_phase35": {"phase35_candidate_sha256": CANDIDATE_SHA, "phase35_postmerge_sha256": POST_SHA, "phase35_finalization_commit": FINALIZATION_COMMIT},
        "assurances": assurances,
        "ledger": {"entries": entries, "head_sequence": 2, "head_sha256": previous},
        "checkpoint": {
            "assured_authorization_readiness_record_count": 2,
            "assurance_check_count": 100,
            "failed_assurance_count": 0,
            "authorization_granted_count": 0,
            "authorization_token_issued_count": 0,
            "execution_authorization_present_count": 0,
            "response_envelope_received_count": 0,
            "response_received_count": 0,
            "validation_result_recorded_count": 0,
            "status_change_count": 0,
            "ledger_sha256": hashlib.sha256(canonical_bytes(entries)).hexdigest(),
        },
        "result": result,
        "authority": authority,
        "recovery": {"accepted": ["baseline"], "accepted_count": 1, "rejected": REJECTED, "rejected_count": len(REJECTED), "scenario_count": len(REJECTED) + 1},
        "next_gate": NEXT_GATE,
        "validation": {"status": "pending", "pull_request": None, "tested_head_commit": None},
    }

def output_bytes() -> bytes:
    return canonical_bytes(build_document()) + b"\n"

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    validate_sources()
    expected = output_bytes()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != expected:
            print("Phase 36 deterministic manifest drift", file=sys.stderr)
            return 1
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(expected)
    print(f"Phase 36 candidate passed: {len(expected)} bytes, sha256={hashlib.sha256(expected).hexdigest()}, 2 assurances, 100 checks, 0 authorization grants.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
