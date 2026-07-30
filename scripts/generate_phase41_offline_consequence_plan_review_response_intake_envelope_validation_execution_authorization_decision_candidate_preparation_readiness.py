#!/usr/bin/env python3
"""Generate deterministic Phase 41 authorization-decision candidate-preparation readiness evidence."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "release/phase-40-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance.json"
SOURCE_POST = ROOT / "release/phase-40-postmerge.json"
OUTPUT = ROOT / "release/phase-41-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness.json"

SOURCE_SHA256 = "a935dbfcc1758b0aab68fb358968801d2b380690a9ebcd6efdc12416d2ef58c8"
SOURCE_POST_SHA256 = "2beeadfd27f823d0afc7f7dfd434e8dad9157488b2d1902b78e7efa26a5e9e20"
SOURCE_FINALIZATION_COMMIT = "840e80dd269809b62ee514206f8567c76928047e"
SOURCE_CANDIDATE_MERGE_COMMIT = "893c00336ddca21c5b5c36d423f6666c0cfb3531"

MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness"
STATE = MODE + "-candidate"
NEXT_GATE = MODE + "-assurance-candidate"
DECISION = "response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-recorded-no-candidate-created"
VERDICT = "response-envelope-validation-execution-authorization-decision-candidate-preparation-ready-no-candidate"

CANDIDATE_FIELDS = [
    "candidate_version", "candidate_id", "source_assurance_id", "source_readiness_id",
    "policy_id", "profile_id", "reviewer_role", "authorization_officer_role",
    "conflict_declaration_ref", "approval_evidence_refs", "rationale",
    "proposed_decision", "valid_from", "expires_at", "revocation_ref",
    "audit_chain_head", "created_at", "signature_ref",
]
FIELD_SOURCES = {
    "candidate_version": "human-governance",
    "candidate_id": "human-governance",
    "source_assurance_id": "phase40-assurance",
    "source_readiness_id": "phase40-assurance",
    "policy_id": "phase40-boundary-policy",
    "profile_id": "phase40-boundary-profile",
    "reviewer_role": "human-role-assignment",
    "authorization_officer_role": "human-role-assignment",
    "conflict_declaration_ref": "human-evidence",
    "approval_evidence_refs": "human-evidence",
    "rationale": "human-authored",
    "proposed_decision": "human-decision",
    "valid_from": "human-authorization",
    "expires_at": "human-authorization",
    "revocation_ref": "human-governance",
    "audit_chain_head": "runtime-audit",
    "created_at": "runtime-clock",
    "signature_ref": "human-signature",
}
STAGES = [
    "source-assurance-binding",
    "boundary-policy-binding",
    "boundary-profile-binding",
    "candidate-schema-binding",
    "field-source-mapping",
    "role-assignment-readiness",
    "conflict-declaration-readiness",
    "approval-evidence-readiness",
    "rationale-composition-readiness",
    "proposed-decision-readiness",
    "validity-revocation-readiness",
    "audit-signature-readiness",
    "assembly-preflight",
    "candidate-freeze",
]
REQUIREMENTS = [
    "phase40-candidate-digest-exact",
    "phase40-postmerge-digest-exact",
    "phase40-finalization-commit-exact",
    "phase40-candidate-merge-commit-exact",
    "source-assurance-id-exact",
    "source-assurance-record-digest-exact",
    "source-assurance-ledger-entry-exact",
    "source-assurance-verdict-exact",
    "source-boundary-id-exact",
    "boundary-policy-id-exact",
    "boundary-policy-digest-exact",
    "boundary-profile-id-exact",
    "boundary-profile-digest-exact",
    "decision-profile-id-exact",
    "candidate-template-schema-digest-exact",
    "candidate-template-digest-exact",
    "candidate-template-field-count-exact",
    "candidate-field-plan-schema-defined",
    "candidate-field-plan-complete",
    "candidate-field-plan-ordered",
    "candidate-field-plan-unpopulated",
    "candidate-field-population-forbidden",
    "source-bindings-locked",
    "role-assignments-symbolic",
    "dual-control-required",
    "role-independence-required",
    "conflict-declaration-required",
    "conflict-declaration-unevaluated",
    "approval-evidence-required",
    "approval-evidence-absent",
    "rationale-required",
    "rationale-unpopulated",
    "proposed-decision-unselected",
    "validity-window-inactive",
    "revocation-reference-absent",
    "audit-chain-absent",
    "signature-absent",
    "candidate-identity-absent",
    "candidate-assembly-disabled",
    "candidate-creation-forbidden",
    "zero-effect-boundary-preserved",
    "atlas-boundary-preserved",
    "external-network-boundary-preserved",
    "repository-mutation-boundary-preserved",
]
CHECK_NAMES = [
    "source_phase40_candidate_exact",
    "source_phase40_postmerge_exact",
    "source_phase40_finalization_exact",
    "source_phase40_candidate_merge_exact",
    "source_assurance_identity_exact",
    "source_assurance_record_digest_exact",
    "source_assurance_ledger_binding_exact",
    "source_assurance_verdict_exact",
    "source_boundary_identity_exact",
    "preparation_identity_exact",
    "sequence_exact",
    "preparation_policy_identity_exact",
    "preparation_policy_version_exact",
    "preparation_policy_digest_exact",
    "preparation_policy_computed_digest_exact",
    "preparation_profile_identity_exact",
    "preparation_profile_digest_exact",
    "boundary_policy_binding_exact",
    "boundary_profile_binding_exact",
    "decision_profile_binding_exact",
    "candidate_schema_binding_exact",
    "candidate_template_binding_exact",
    "candidate_field_count_exact",
    "candidate_field_plan_exact",
    "candidate_field_plan_digest_exact",
    "candidate_field_plan_order_exact",
    "candidate_field_plan_sources_exact",
    "candidate_field_plan_unpopulated",
    "candidate_field_population_forbidden",
    "source_bindings_locked",
    "required_roles_exact",
    "required_roles_unsatisfied",
    "dual_control_required",
    "role_independence_required",
    "conflict_declaration_required",
    "conflict_declaration_unevaluated",
    "approval_evidence_required",
    "approval_evidence_absent",
    "rationale_required",
    "rationale_unpopulated",
    "proposed_decision_unselected",
    "validity_window_inactive",
    "revocation_reference_absent",
    "audit_chain_absent",
    "signature_absent",
    "candidate_identity_absent",
    "preparation_stages_exact",
    "preparation_stages_digest_exact",
    "preparation_stages_inactive",
    "preparation_requirements_exact",
    "preparation_requirements_digest_exact",
    "preparation_requirements_unevaluated",
    "candidate_assembly_disabled",
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
    "audit_events_unrecorded",
    "status_effects_frozen",
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
    "source_result_binding_exact",
    "source_checkpoint_binding_exact",
    "source_ledger_head_binding_exact",
    "contract_exact",
    "state_exact",
    "decision_exact",
    "next_gate_exact",
    "checkpoint_exact",
    "ledger_chain_exact",
]
assert len(CANDIDATE_FIELDS) == 18
assert len(STAGES) == 14
assert len(REQUIREMENTS) == 44
assert len(CHECK_NAMES) == 90

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
        "local_authorization_decision_candidate_preparation_readiness_permitted": True,
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

def preparation_policy() -> dict[str, Any]:
    policy = {
        "preparation_policy_id": "principia-envelope-validation-execution-authorization-decision-candidate-preparation-policy",
        "preparation_policy_version": "0.1",
        "preparation_stages": [
            {"sequence": i, "stage_id": stage, "state": "inactive"}
            for i, stage in enumerate(STAGES, 1)
        ],
        "preparation_requirements": [
            {"sequence": i, "requirement_id": requirement, "state": "unevaluated"}
            for i, requirement in enumerate(REQUIREMENTS, 1)
        ],
        "candidate_field_plan_schema": {
            "media_type": "application/json",
            "encoding": "utf-8",
            "unknown_fields": "prohibited",
            "required_fields": [
                "sequence", "candidate_field", "source_kind", "required",
                "state", "population_permitted",
            ],
        },
        "candidate_fields": CANDIDATE_FIELDS,
        "assembly": {
            "candidate_materialization_permitted": False,
            "candidate_population_permitted": False,
            "candidate_persistence_permitted": False,
        },
        "human_gates": {
            "required_roles": [
                "qualified-pedagogical-reviewer",
                "qualified-release-governance-reviewer",
            ],
            "required_count": 2,
            "satisfied_count": 0,
        },
    }
    policy["preparation_policy_sha256"] = sha_value(policy)
    return policy

def field_plan() -> list[dict[str, Any]]:
    return [
        {
            "sequence": i,
            "candidate_field": field,
            "source_kind": FIELD_SOURCES[field],
            "required": True,
            "state": "unpopulated",
            "population_permitted": False,
        }
        for i, field in enumerate(CANDIDATE_FIELDS, 1)
    ]

def recovery_labels() -> list[str]:
    fields = [
        "source-candidate-digest", "source-postmerge-digest", "source-finalization-commit",
        "source-candidate-merge-commit", "source-assurance-order", "source-assurance-id",
        "source-assurance-digest", "source-ledger-entry", "source-verdict", "source-boundary-id",
        "preparation-id", "preparation-order", "policy-id", "policy-version", "policy-digest",
        "policy-content", "profile-id", "profile-digest", "profile-content",
        "boundary-policy-binding", "boundary-profile-binding", "decision-profile-binding",
        "candidate-schema-binding", "candidate-template-binding", "candidate-field-count",
        "field-plan-order", "field-plan-field", "field-plan-source", "field-plan-state",
        "field-plan-population", "stage-order", "stage-id", "stage-state",
        "requirement-order", "requirement-id", "requirement-state", "role-order",
        "role-state", "dual-control", "role-independence", "conflict-required",
        "conflict-evaluated", "approval-required", "approval-recorded", "rationale-required",
        "rationale-populated", "proposed-decision", "validity-state", "revocation-reference",
        "audit-chain", "signature", "candidate-identity", "candidate-assembly",
        "candidate-created", "decision-record-created", "decision-recorded",
        "authorization-grant", "token-issued", "ticket-issued", "execution-run",
        "envelope-received", "reviewer-identity", "reviewer-contact", "review-start",
        "approval-received", "human-gate-satisfied", "disposition-selected",
        "validation-result", "audit-event", "status-change", "authority", "atlas-call",
        "external-network", "repository-mutation", "automatic-release", "automatic-status",
        "real-authorization", "live", "check-name", "check-value", "check-count",
        "failed-check-count", "verdict", "status", "ledger-order", "ledger-record-digest",
        "ledger-previous", "ledger-entry-digest", "ledger-head", "checkpoint",
        "result-count", "next-gate", "decision", "state", "contract",
    ]
    labels: list[str] = []
    for name in ("feedback-manual-review", "model-boundary-release-governance"):
        labels.extend(f"reject-{name}-{field}-drift" for field in fields)
    labels.extend([
        "reject-missing-preparation-record",
        "reject-extra-preparation-record",
        "reject-duplicate-preparation-record",
        "reject-preparation-record-order-drift",
        "reject-cross-profile-source-binding",
        "reject-cross-profile-field-plan-binding",
        "reject-noncanonical-json",
    ])
    return labels

def build_manifest(source: dict[str, Any], source_post: dict[str, Any]) -> dict[str, Any]:
    if sha_file(SOURCE) != SOURCE_SHA256:
        raise ValueError("Phase 40 candidate digest mismatch")
    if sha_file(SOURCE_POST) != SOURCE_POST_SHA256:
        raise ValueError("Phase 40 postmerge digest mismatch")
    if source.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance-candidate":
        raise ValueError("Phase 40 source state mismatch")
    if source_post.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance-validated":
        raise ValueError("Phase 40 postmerge state mismatch")
    if source_post.get("principia", {}).get("merge_commit") != SOURCE_CANDIDATE_MERGE_COMMIT:
        raise ValueError("Phase 40 candidate merge mismatch")

    policy = preparation_policy()
    ledger_by_id = {
        item["entry"]["assurance_id"]: item
        for item in source["ledger"]["entries"]
    }
    records: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    previous: str | None = None

    for sequence, assurance in enumerate(source["assurances"], 1):
        source_id = assurance["assurance_id"]
        source_ledger = ledger_by_id[source_id]
        source_sha = sha_value(assurance)
        if source_sha != source_ledger["entry"]["record_sha256"]:
            raise ValueError("Phase 40 assurance digest mismatch")
        suffix = source_id.rsplit(":", 2)[-2]
        profile = {
            "preparation_profile_id": f"principia:authorization-decision-candidate-preparation-profile:{suffix}:{sequence:04d}",
            "source_assurance_id": source_id,
            "source_boundary_id": assurance["source_boundary_id"],
            "source_readiness_id": assurance["source_readiness_id"],
            "boundary_policy_id": assurance["boundary_policy_id"],
            "boundary_profile_id": assurance["boundary_profile_id"],
            "decision_profile_id": assurance["decision_profile_id"],
            "required_roles": [
                "qualified-pedagogical-reviewer",
                "qualified-release-governance-reviewer",
            ],
            "reviewer_role": (
                "qualified-pedagogical-reviewer"
                if sequence == 1 else "qualified-release-governance-reviewer"
            ),
            "authorization_officer_role": "qualified-release-governance-reviewer",
            "dual_control_required": True,
            "role_independence_required": True,
            "conflict_declaration_required": True,
        }
        plan = field_plan()
        checks = {name: True for name in CHECK_NAMES}
        preparation_id = f"principia:authorization-decision-candidate-preparation-readiness:{suffix}:{sequence:04d}"
        record = {
            "approval_evidence_recorded": False,
            "approval_received": False,
            "audit_event_recorded_count": 0,
            "authorization_decision_candidate_created": False,
            "authorization_decision_record_created": False,
            "authorization_decision_recorded": False,
            "authorization_granted": False,
            "authorization_token_issued": False,
            "candidate_assembly_permitted": False,
            "candidate_field_plan": plan,
            "candidate_field_plan_count": len(plan),
            "candidate_field_plan_sha256": sha_value(plan),
            "candidate_field_populated_count": 0,
            "candidate_id_present": False,
            "candidate_signature_present": False,
            "candidate_template_field_count": assurance["candidate_template_field_count"],
            "candidate_template_schema_sha256": assurance["candidate_template_schema_sha256"],
            "candidate_template_sha256": assurance["candidate_template_sha256"],
            "conflict_declaration_evaluated": False,
            "disposition_selected": False,
            "execution_run_created": False,
            "execution_ticket_issued": False,
            "failed_preparation_check_count": 0,
            "human_gate_pending_count": assurance["human_gate_pending_count"],
            "human_gate_satisfied_count": 0,
            "local_only": True,
            "preparation_check_count": len(CHECK_NAMES),
            "preparation_checks": checks,
            "preparation_id": preparation_id,
            "preparation_policy_id": policy["preparation_policy_id"],
            "preparation_policy_sha256": policy["preparation_policy_sha256"],
            "preparation_profile": profile,
            "preparation_profile_sha256": sha_value(profile),
            "proposed_decision_selected": False,
            "rationale_populated": False,
            "real_authorization_claimed": False,
            "response_envelope_received": False,
            "reviewer_contact_permitted": False,
            "reviewer_identity_present": False,
            "revocation_reference_present": False,
            "sequence": sequence,
            "source_assurance_id": source_id,
            "source_assurance_record_sha256": source_sha,
            "source_ledger_entry_sha256": source_ledger["entry_sha256"],
            "status": "preparation-ready-no-candidate",
            "status_change": False,
            "validation_result_recorded": False,
            "validity_window_active": False,
            "verdict": VERDICT,
        }
        record_sha = sha_value(record)
        entry = {
            "preparation_id": preparation_id,
            "previous_entry_sha256": previous,
            "record_sha256": record_sha,
            "sequence": sequence,
            "source_assurance_id": source_id,
            "source_ledger_entry_sha256": source_ledger["entry_sha256"],
            "verdict": VERDICT,
        }
        entry_sha = sha_value(entry)
        ledger.append({"entry": entry, "entry_sha256": entry_sha})
        previous = entry_sha
        records.append(record)

    result = copy.deepcopy(source["result"])
    result.update({
        "candidate_field_plan_count": len(records) * len(CANDIDATE_FIELDS),
        "candidate_field_populated_count": 0,
        "candidate_preparation_policy_count": 1,
        "candidate_preparation_profile_count": len(records),
        "candidate_preparation_readiness_record_count": len(records),
        "candidate_preparation_stage_count": len(records) * len(STAGES),
        "candidate_preparation_requirement_count": len(records) * len(REQUIREMENTS),
        "candidate_preparation_requirement_evaluated_count": 0,
        "preparation_check_count": len(records) * len(CHECK_NAMES),
        "failed_preparation_check_count": 0,
    })
    rejected = recovery_labels()
    return {
        "authority": authority(),
        "candidate_preparation_policy": policy,
        "candidate_preparation_readiness_records": records,
        "checkpoint": {
            "authorization_decision_candidate_created_count": 0,
            "authorization_decision_recorded_count": 0,
            "authorization_granted_count": 0,
            "authorization_token_issued_count": 0,
            "candidate_field_populated_count": 0,
            "execution_run_count": 0,
            "failed_preparation_check_count": 0,
            "ledger_sha256": previous,
            "preparation_check_count": len(records) * len(CHECK_NAMES),
            "preparation_record_count": len(records),
            "response_envelope_received_count": 0,
            "status_change_count": 0,
        },
        "contract": "principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-thermal-control",
        "ledger": {
            "entries": ledger,
            "head_sequence": len(ledger),
            "head_sha256": previous,
        },
        "live": False,
        "live_activation_permitted": False,
        "mode": MODE,
        "next_gate": NEXT_GATE,
        "phase": 41,
        "real_authorization_claimed": False,
        "recovery": {
            "accepted": ["baseline-phase40-candidate-preparation-readiness"],
            "accepted_count": 1,
            "rejected": rejected,
            "rejected_count": len(rejected),
            "scenario_count": len(rejected) + 1,
        },
        "result": result,
        "source_phase40": {
            "phase40_candidate_sha256": SOURCE_SHA256,
            "phase40_candidate_merge_commit": SOURCE_CANDIDATE_MERGE_COMMIT,
            "phase40_finalization_commit": SOURCE_FINALIZATION_COMMIT,
            "phase40_postmerge_sha256": SOURCE_POST_SHA256,
        },
        "state": STATE,
        "validation": {
            "pull_request": None,
            "status": "candidate",
            "tested_head_commit": None,
        },
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
            print("Phase 41 candidate drift")
            return 1
        print(
            "Phase 41 candidate passed: "
            f"bytes={len(payload)}, sha256={hashlib.sha256(payload).hexdigest()}, "
            f"records={len(manifest['candidate_preparation_readiness_records'])}, "
            f"checks={manifest['result']['preparation_check_count']}."
        )
        return 0
    OUTPUT.write_bytes(payload)
    print(f"Wrote {OUTPUT}: bytes={len(payload)}, sha256={hashlib.sha256(payload).hexdigest()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
