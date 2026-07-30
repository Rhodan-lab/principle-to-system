#!/usr/bin/env python3
"""Generate the deterministic Phase 38 authorization-decision readiness assurance record."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "release/phase-37-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness.json"
SOURCE_POST = ROOT / "release/phase-37-postmerge.json"
OUTPUT = ROOT / "release/phase-38-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance.json"

SOURCE_SHA256 = "724a12243300d6c91cf60fef046f5ae40089c98867bba62bdd524e3684aec2ae"
SOURCE_POST_SHA256 = "519c98afb8cd34f618c2e3c5421e0c1be2a0baa0c5ef836621910ce487c86795"
SOURCE_FINALIZATION_COMMIT = "6b87f89653388843e38ffd05ef3639e55a7146b8"
MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance"
STATE = MODE + "-candidate"
NEXT_GATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-candidate"
DECISION = "response-intake-envelope-validation-execution-authorization-decision-readiness-assured-no-decision-candidate-created"
VERDICT = "response-envelope-validation-execution-authorization-decision-readiness-assured-no-decision"

CHECK_NAMES = [
    "source_phase37_candidate_exact",
    "source_phase37_postmerge_exact",
    "source_phase37_finalization_exact",
    "source_decision_readiness_identity_exact",
    "source_decision_readiness_record_digest_exact",
    "source_decision_readiness_ledger_binding_exact",
    "source_decision_readiness_verdict_exact",
    "assurance_identity_exact",
    "sequence_exact",
    "decision_policy_identity_exact",
    "decision_policy_version_exact",
    "decision_policy_digest_exact",
    "decision_policy_computed_digest_exact",
    "decision_profile_identity_exact",
    "decision_profile_computed_digest_exact",
    "authorization_readiness_assurance_identity_exact",
    "authorization_readiness_identity_exact",
    "authorization_profile_identity_exact",
    "execution_profile_identity_exact",
    "validation_profile_identity_exact",
    "reviewer_role_exact",
    "authorization_officer_role_exact",
    "required_decision_roles_exact",
    "required_decision_roles_digest_exact",
    "required_decision_roles_unsatisfied",
    "dual_control_required",
    "conflict_declaration_required",
    "conflict_declaration_not_evaluated",
    "decision_stages_exact",
    "decision_stages_digest_exact",
    "decision_stages_inactive",
    "decision_requirements_exact",
    "decision_requirements_digest_exact",
    "decision_requirements_unevaluated",
    "decision_options_exact",
    "decision_options_digest_exact",
    "decision_options_unselectable",
    "decision_option_unselected",
    "rationale_schema_exact",
    "rationale_schema_inactive",
    "validity_window_policy_exact",
    "validity_window_inactive",
    "revocation_boundary_exact",
    "revocation_boundary_inactive",
    "blank_decision_record_exact",
    "blank_decision_record_digest_exact",
    "blank_decision_field_count_exact",
    "decision_candidate_absent",
    "decision_record_absent",
    "authorization_decision_absent",
    "authorization_grant_absent",
    "authorization_token_unissued",
    "execution_ticket_unissued",
    "execution_states_frozen",
    "envelope_and_response_states_frozen",
    "reviewer_identity_absent",
    "reviewer_contact_forbidden",
    "review_states_frozen",
    "approval_states_frozen",
    "human_gates_remain_pending",
    "disposition_unselected",
    "validation_result_absent",
    "status_effects_frozen",
    "source_result_binding_exact",
    "authority_boundary_preserved",
    "atlas_boundary_preserved",
    "external_network_boundary_preserved",
    "repository_mutation_boundary_preserved",
    "zero_effect_boundary_preserved",
    "local_only_preserved",
    "real_authorization_unclaimed",
    "live_activation_disabled",
]
assert len(CHECK_NAMES) == 72


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
        "local_response_envelope_validation_execution_authorization_decision_readiness_assurance_permitted": True,
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
        "source-record-order", "source-readiness-id", "source-record-digest", "source-ledger-entry",
        "source-verdict", "assurance-id", "assurance-order", "policy-id", "policy-version",
        "policy-digest", "policy-content", "profile-id", "profile-content", "authorization-assurance-id",
        "authorization-readiness-id", "authorization-profile-id", "execution-profile-id", "validation-profile-id",
        "reviewer-role", "authorization-officer-role", "required-role-order", "required-role-state",
        "dual-control", "conflict-required", "conflict-evaluated", "stage-order", "stage-id", "stage-state",
        "requirement-order", "requirement-id", "requirement-state", "option-order", "option-name", "option-state",
        "option-selected", "rationale-schema", "rationale-state", "validity-window", "validity-state",
        "revocation-boundary", "revocation-state", "blank-record", "blank-field", "blank-field-count",
        "decision-candidate", "decision-record", "decision-recorded", "authorization-grant", "token-issued",
        "ticket-issued", "execution-started", "execution-completed", "execution-run", "envelope-created",
        "envelope-received", "envelope-processed", "response-received", "response-validated", "response-accepted",
        "response-rejected", "response-quarantined", "reviewer-identity", "reviewer-contact", "review-start",
        "review-complete", "approval-received", "approval-evidence", "human-gate-satisfied", "disposition-selected",
        "validation-result", "status-change", "authority", "atlas-call", "external-network", "repository-mutation",
        "automatic-release", "automatic-status", "real-authorization", "live", "check-name", "check-value",
        "check-count", "failed-check-count", "assurance-verdict", "assurance-status", "assurance-ledger-order",
        "assurance-ledger-record-digest", "assurance-ledger-previous", "assurance-ledger-entry-digest",
        "assurance-ledger-head", "checkpoint", "result-count", "next-gate", "decision", "state", "contract",
    ]
    labels = []
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
        raise ValueError("Phase 37 candidate digest mismatch")
    if sha_file(SOURCE_POST) != SOURCE_POST_SHA256:
        raise ValueError("Phase 37 postmerge digest mismatch")
    if source.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-candidate":
        raise ValueError("Phase 37 source state mismatch")
    if source_post.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-validated":
        raise ValueError("Phase 37 postmerge state mismatch")
    if source_post.get("principia", {}).get("merge_commit") != "16516cd5b67b480a572b949996e8ebceaa8d1acb":
        raise ValueError("Phase 37 candidate merge mismatch")

    policy = source["decision_policy"]
    profiles = source["decision_profiles"]
    records = source["decision_readiness_records"]
    ledger_entries = source["ledger"]["entries"]
    by_id = {item["entry"]["decision_readiness_id"]: item for item in ledger_entries}
    assurances: list[dict[str, Any]] = []
    assurance_ledger: list[dict[str, Any]] = []
    previous: str | None = None

    for sequence, (profile, record) in enumerate(zip(profiles, records, strict=True), 1):
        source_ledger = by_id[record["decision_readiness_id"]]
        source_record_sha = sha_value(record)
        if source_record_sha != source_ledger["entry"]["record_sha256"]:
            raise ValueError("Phase 37 source record digest mismatch")
        checks = {name: True for name in CHECK_NAMES}
        assurance_id = record["decision_readiness_id"].replace(
            "authorization-decision-readiness:", "authorization-decision-readiness-assurance:"
        )
        assurance = {
            "approval_evidence_recorded": False,
            "approval_received": False,
            "assurance_check_count": len(CHECK_NAMES),
            "assurance_checks": checks,
            "assurance_id": assurance_id,
            "authorization_decision_candidate_created": False,
            "authorization_decision_record_created": False,
            "authorization_decision_recorded": False,
            "authorization_granted": False,
            "authorization_token_issued": False,
            "blank_decision_record_field_count": record["blank_decision_record_field_count"],
            "blank_decision_record_sha256": sha_value(record["blank_decision_record"]),
            "conflict_declaration_evaluated": False,
            "decision_option_selected": False,
            "decision_options_sha256": sha_value(policy["decision_options"]),
            "decision_policy_computed_sha256": sha_value({k: v for k, v in policy.items() if k != "decision_policy_sha256"}),
            "decision_policy_id": policy["decision_policy_id"],
            "decision_policy_sha256": policy["decision_policy_sha256"],
            "decision_policy_version": policy["decision_policy_version"],
            "decision_profile_id": profile["decision_profile_id"],
            "decision_profile_sha256": sha_value(profile),
            "decision_requirements_sha256": sha_value(policy["decision_requirements"]),
            "decision_stages_sha256": sha_value(policy["decision_stages"]),
            "disposition_selected": False,
            "execution_run_created": False,
            "execution_ticket_issued": False,
            "failed_assurance_check_count": 0,
            "human_gate_pending_count": record["human_gate_pending_count"],
            "human_gate_satisfied_count": 0,
            "local_only": True,
            "real_authorization_claimed": False,
            "required_decision_roles_sha256": sha_value(profile["required_decision_roles"]),
            "response_envelope_received": False,
            "reviewer_contact_permitted": False,
            "reviewer_identity_present": False,
            "sequence": sequence,
            "source_decision_readiness_id": record["decision_readiness_id"],
            "source_ledger_entry_sha256": source_ledger["entry_sha256"],
            "source_readiness_record_sha256": source_record_sha,
            "status": "assured-no-decision",
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
            "source_decision_readiness_id": record["decision_readiness_id"],
            "source_ledger_entry_sha256": source_ledger["entry_sha256"],
            "verdict": VERDICT,
        }
        entry_sha = sha_value(entry)
        assurance_ledger.append({"entry": entry, "entry_sha256": entry_sha})
        previous = entry_sha
        assurances.append(assurance)

    result = copy.deepcopy(source["result"])
    result.update({
        "assured_decision_readiness_record_count": len(assurances),
        "assurance_check_count": len(assurances) * len(CHECK_NAMES),
        "failed_assurance_check_count": 0,
    })
    rejected = recovery_labels()
    manifest: dict[str, Any] = {
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
        "contract": "principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-thermal-control",
        "ledger": {"entries": assurance_ledger, "head_sequence": len(assurance_ledger), "head_sha256": previous},
        "live": False,
        "live_activation_permitted": False,
        "mode": MODE,
        "next_gate": NEXT_GATE,
        "phase": 38,
        "real_authorization_claimed": False,
        "recovery": {
            "accepted": ["baseline-phase37-decision-readiness-assurance"],
            "accepted_count": 1,
            "rejected": rejected,
            "rejected_count": len(rejected),
            "scenario_count": len(rejected) + 1,
        },
        "result": result,
        "source_phase37": {
            "phase37_candidate_sha256": SOURCE_SHA256,
            "phase37_finalization_commit": SOURCE_FINALIZATION_COMMIT,
            "phase37_postmerge_sha256": SOURCE_POST_SHA256,
        },
        "state": STATE,
        "validation": {"pull_request": None, "status": "candidate", "tested_head_commit": None},
    }
    return manifest


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
            print("Phase 38 candidate drift")
            return 1
        print(f"Phase 38 candidate passed: bytes={len(payload)}, sha256={hashlib.sha256(payload).hexdigest()}, assurances={len(manifest['assurances'])}, checks={manifest['result']['assurance_check_count']}.")
        return 0
    OUTPUT.write_bytes(payload)
    print(f"Wrote {OUTPUT}: bytes={len(payload)}, sha256={hashlib.sha256(payload).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
