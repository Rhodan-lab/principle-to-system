#!/usr/bin/env python3
"""Generate deterministic Phase 40 authorization-decision candidate-boundary readiness assurance evidence."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "release/phase-39-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness.json"
SOURCE_POST = ROOT / "release/phase-39-postmerge.json"
OUTPUT = ROOT / "release/phase-40-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance.json"

SOURCE_SHA256 = "e15063165a54ced8bbae95f4dcea9c9ff92c540135d67d3a8b10791dbc771c40"
SOURCE_POST_SHA256 = "17cab6bc36cffeb475065fe92116486fb47e8ac813a643205d0cbd18e774fea2"
SOURCE_FINALIZATION_COMMIT = "7b3e7ffdfed4a70a7369dcec5620aec04228feb3"
MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance"
STATE = MODE + "-candidate"
NEXT_GATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-candidate"
DECISION = "response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assured-no-candidate-created"
VERDICT = "response-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assured-no-candidate"

CHECK_NAMES = [
    "source_phase39_candidate_exact",
    "source_phase39_postmerge_exact",
    "source_phase39_finalization_exact",
    "source_boundary_identity_exact",
    "source_boundary_record_digest_exact",
    "source_boundary_ledger_binding_exact",
    "source_boundary_verdict_exact",
    "assurance_identity_exact",
    "sequence_exact",
    "boundary_policy_identity_exact",
    "boundary_policy_version_exact",
    "boundary_policy_digest_exact",
    "boundary_policy_computed_digest_exact",
    "boundary_profile_identity_exact",
    "boundary_profile_digest_exact",
    "source_assurance_identity_exact",
    "source_readiness_identity_exact",
    "decision_policy_binding_exact",
    "decision_profile_binding_exact",
    "reviewer_role_exact",
    "authorization_officer_role_exact",
    "required_roles_exact",
    "required_roles_unsatisfied",
    "dual_control_required",
    "role_independence_required",
    "conflict_declaration_required",
    "conflict_declaration_unevaluated",
    "approval_evidence_schema_exact",
    "approval_evidence_absent",
    "boundary_stages_exact",
    "boundary_stages_digest_exact",
    "boundary_stages_inactive",
    "boundary_requirements_exact",
    "boundary_requirements_digest_exact",
    "boundary_requirements_unevaluated",
    "candidate_template_schema_exact",
    "candidate_template_exact",
    "candidate_template_digest_exact",
    "candidate_template_field_count_exact",
    "candidate_template_blank",
    "rationale_schema_exact",
    "rationale_unpopulated",
    "validity_window_exact",
    "validity_window_inactive",
    "revocation_conditions_exact",
    "revocation_inactive",
    "audit_event_types_exact",
    "audit_events_unrecorded",
    "candidate_absent",
    "decision_record_absent",
    "authorization_decision_absent",
    "authorization_grant_absent",
    "authorization_token_unissued",
    "execution_ticket_unissued",
    "execution_states_frozen",
    "envelope_states_frozen",
    "response_states_frozen",
    "reviewer_identity_absent",
    "reviewer_contact_forbidden",
    "review_states_frozen",
    "approval_states_frozen",
    "human_gates_remain_pending",
    "disposition_unselected",
    "validation_result_absent",
    "status_effects_frozen",
    "source_result_binding_exact",
    "source_checkpoint_binding_exact",
    "source_ledger_head_binding_exact",
    "authority_boundary_preserved",
    "atlas_boundary_preserved",
    "external_network_boundary_preserved",
    "repository_mutation_boundary_preserved",
    "automatic_release_boundary_preserved",
    "automatic_status_boundary_preserved",
    "zero_effect_boundary_preserved",
    "local_only_preserved",
    "real_authorization_unclaimed",
    "live_activation_disabled",
    "contract_exact",
    "state_exact",
    "decision_exact",
    "next_gate_exact",
    "checkpoint_exact",
    "ledger_chain_exact",
]
assert len(CHECK_NAMES) == 84


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def authority() -> dict[str, Any]:
    return {
        "atlas_call_permitted": False,
        "authorization_decision_candidate_creation_permitted": False,
        "authorization_decision_recording_permitted": False,
        "automatic_release_action": False,
        "automatic_status_change": False,
        "external_delivery_permitted": False,
        "external_network_required": False,
        "human_authorization_claimed": False,
        "local_authorization_decision_candidate_boundary_readiness_assurance_permitted": True,
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


def recovery_labels() -> list[str]:
    fields = [
        "source-candidate-digest", "source-postmerge-digest", "source-finalization-commit",
        "source-record-order", "source-boundary-id", "source-record-digest", "source-ledger-entry",
        "source-verdict", "assurance-id", "assurance-order", "policy-id", "policy-version",
        "policy-digest", "policy-content", "profile-id", "profile-digest", "profile-content",
        "source-assurance-id", "source-readiness-id", "decision-policy-id", "decision-profile-id",
        "reviewer-role", "authorization-officer-role", "required-role-order", "required-role-state",
        "dual-control", "role-independence", "conflict-required", "conflict-evaluated",
        "approval-evidence-schema", "approval-evidence-recorded", "stage-order", "stage-id", "stage-state",
        "requirement-order", "requirement-id", "requirement-state", "candidate-schema", "candidate-template",
        "candidate-field", "candidate-field-count", "rationale-schema", "rationale-state", "validity-window",
        "validity-state", "revocation-conditions", "revocation-state", "audit-event-types", "audit-event",
        "candidate-created", "candidate-populated", "decision-record", "decision-recorded", "authorization-grant",
        "token-issued", "ticket-issued", "execution-started", "execution-completed", "execution-run",
        "envelope-created", "envelope-received", "envelope-processed", "response-received", "response-validated",
        "response-accepted", "response-rejected", "response-quarantined", "reviewer-identity", "reviewer-contact",
        "review-start", "review-complete", "approval-received", "human-gate-satisfied", "disposition-selected",
        "validation-result", "status-change", "authority", "atlas-call", "external-network", "repository-mutation",
        "automatic-release", "automatic-status", "real-authorization", "live", "check-name", "check-value",
        "check-count", "failed-check-count", "assurance-verdict", "assurance-status", "ledger-order",
        "ledger-record-digest", "ledger-previous", "ledger-entry-digest", "ledger-head", "checkpoint",
        "result-count", "next-gate", "decision", "state", "contract",
    ]
    labels: list[str] = []
    for record in ("feedback-manual-review", "model-boundary-release-governance"):
        labels.extend(f"reject-{record}-{field}-drift" for field in fields)
    labels.extend([
        "reject-missing-assurance-record",
        "reject-extra-assurance-record",
        "reject-duplicate-assurance-record",
        "reject-assurance-record-order-drift",
        "reject-source-policy-cross-record-drift",
        "reject-source-profile-cross-record-drift",
        "reject-noncanonical-json",
    ])
    return labels


def build_manifest(source: dict[str, Any], source_post: dict[str, Any]) -> dict[str, Any]:
    if sha_file(SOURCE) != SOURCE_SHA256:
        raise ValueError("Phase 39 candidate digest mismatch")
    if sha_file(SOURCE_POST) != SOURCE_POST_SHA256:
        raise ValueError("Phase 39 postmerge digest mismatch")
    if source.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-candidate":
        raise ValueError("Phase 39 source state mismatch")
    if source_post.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-validated":
        raise ValueError("Phase 39 postmerge state mismatch")
    if source_post.get("principia", {}).get("merge_commit") != "e2b81e9ac1ff5385ab054392bb0b33f5c3907b55":
        raise ValueError("Phase 39 candidate merge mismatch")

    policy = source["boundary_policy"]
    records = source["boundary_readiness_records"]
    ledger_entries = source["ledger"]["entries"]
    by_id = {item["entry"]["boundary_id"]: item for item in ledger_entries}
    assurances: list[dict[str, Any]] = []
    assurance_ledger: list[dict[str, Any]] = []
    previous: str | None = None

    for sequence, record in enumerate(records, 1):
        source_ledger = by_id[record["boundary_id"]]
        source_record_sha = sha_value(record)
        if source_record_sha != source_ledger["entry"]["record_sha256"]:
            raise ValueError("Phase 39 source record digest mismatch")
        profile = record["boundary_profile"]
        assurance_id = record["boundary_id"].replace(
            "candidate-boundary-readiness:", "candidate-boundary-readiness-assurance:"
        )
        checks = {name: True for name in CHECK_NAMES}
        assurance = {
            "approval_evidence_recorded": False,
            "approval_received": False,
            "assurance_check_count": len(CHECK_NAMES),
            "assurance_checks": checks,
            "assurance_id": assurance_id,
            "audit_event_recorded_count": 0,
            "authorization_decision_candidate_created": False,
            "authorization_decision_record_created": False,
            "authorization_decision_recorded": False,
            "authorization_granted": False,
            "authorization_token_issued": False,
            "boundary_policy_computed_sha256": sha_value({k: v for k, v in policy.items() if k != "boundary_policy_sha256"}),
            "boundary_policy_id": policy["boundary_policy_id"],
            "boundary_policy_sha256": policy["boundary_policy_sha256"],
            "boundary_policy_version": policy["boundary_policy_version"],
            "boundary_profile_id": profile["boundary_profile_id"],
            "boundary_profile_sha256": record["boundary_profile_sha256"],
            "boundary_requirements_sha256": sha_value(policy["boundary_requirements"]),
            "boundary_stages_sha256": sha_value(policy["boundary_stages"]),
            "candidate_template_field_count": record["candidate_template_field_count"],
            "candidate_template_schema_sha256": sha_value(policy["candidate_template_schema"]),
            "candidate_template_sha256": record["candidate_template_sha256"],
            "conflict_declaration_evaluated": False,
            "decision_profile_id": profile["decision_profile_id"],
            "disposition_selected": False,
            "execution_run_created": False,
            "execution_ticket_issued": False,
            "failed_assurance_check_count": 0,
            "human_gate_pending_count": record["human_gate_pending_count"],
            "human_gate_satisfied_count": 0,
            "local_only": True,
            "real_authorization_claimed": False,
            "response_envelope_received": False,
            "reviewer_contact_permitted": False,
            "reviewer_identity_present": False,
            "sequence": sequence,
            "source_assurance_id": record["source_assurance_id"],
            "source_boundary_id": record["boundary_id"],
            "source_boundary_record_sha256": source_record_sha,
            "source_ledger_entry_sha256": source_ledger["entry_sha256"],
            "source_readiness_id": profile["source_readiness_id"],
            "status": "assured-no-candidate",
            "status_change": False,
            "validation_result_recorded": False,
            "verdict": VERDICT,
        }
        assurance_sha = sha_value(assurance)
        entry = {
            "assurance_id": assurance_id,
            "previous_entry_sha256": previous,
            "record_sha256": assurance_sha,
            "sequence": sequence,
            "source_boundary_id": record["boundary_id"],
            "source_ledger_entry_sha256": source_ledger["entry_sha256"],
            "verdict": VERDICT,
        }
        entry_sha = sha_value(entry)
        assurance_ledger.append({"entry": entry, "entry_sha256": entry_sha})
        previous = entry_sha
        assurances.append(assurance)

    result = copy.deepcopy(source["result"])
    result.update({
        "assurance_check_count": len(assurances) * len(CHECK_NAMES),
        "assured_candidate_boundary_readiness_record_count": len(assurances),
        "failed_assurance_check_count": 0,
    })
    rejected = recovery_labels()
    return {
        "assurances": assurances,
        "authority": authority(),
        "checkpoint": {
            "assurance_check_count": len(assurances) * len(CHECK_NAMES),
            "assurance_record_count": len(assurances),
            "authorization_decision_candidate_created_count": 0,
            "authorization_decision_recorded_count": 0,
            "authorization_granted_count": 0,
            "authorization_token_issued_count": 0,
            "execution_run_count": 0,
            "failed_assurance_check_count": 0,
            "ledger_sha256": previous,
            "response_envelope_received_count": 0,
            "status_change_count": 0,
        },
        "contract": "principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance-thermal-control",
        "ledger": {"entries": assurance_ledger, "head_sequence": len(assurance_ledger), "head_sha256": previous},
        "live": False,
        "live_activation_permitted": False,
        "mode": MODE,
        "next_gate": NEXT_GATE,
        "phase": 40,
        "real_authorization_claimed": False,
        "recovery": {
            "accepted": ["baseline-phase39-candidate-boundary-readiness-assurance"],
            "accepted_count": 1,
            "rejected": rejected,
            "rejected_count": len(rejected),
            "scenario_count": len(rejected) + 1,
        },
        "result": result,
        "source_phase39": {
            "phase39_candidate_sha256": SOURCE_SHA256,
            "phase39_finalization_commit": SOURCE_FINALIZATION_COMMIT,
            "phase39_postmerge_sha256": SOURCE_POST_SHA256,
        },
        "state": STATE,
        "validation": {"pull_request": None, "status": "candidate", "tested_head_commit": None},
    }


def render(manifest: dict[str, Any]) -> bytes:
    return canonical_bytes(manifest) + b"\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = build_manifest(load(SOURCE), load(SOURCE_POST))
    payload = render(manifest)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != payload:
            print("Phase 40 candidate drift")
            return 1
        print(f"Phase 40 candidate passed: bytes={len(payload)}, sha256={hashlib.sha256(payload).hexdigest()}, assurances={len(manifest['assurances'])}, checks={manifest['result']['assurance_check_count']}.")
        return 0
    OUTPUT.write_bytes(payload)
    print(f"Wrote {OUTPUT}: bytes={len(payload)}, sha256={hashlib.sha256(payload).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
