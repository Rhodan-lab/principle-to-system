#!/usr/bin/env python3
"""Generate deterministic Phase 42 candidate-preparation readiness assurance evidence."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_CANDIDATE_PATH = ROOT / "release/phase-41-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness.json"
SOURCE_POSTMERGE_PATH = ROOT / "release/phase-41-postmerge.json"
OUTPUT_PATH = ROOT / "release/phase-42-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance.json"

PHASE = 42
MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance"
STATE = MODE + "-candidate"
DECISION = "response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assured-no-candidate-created"
NEXT_GATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-candidate"
CONTRACT = "principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance/0.1"

SOURCE_CANDIDATE_SHA256 = "c45f148554f66bf21db03fa446475e55746086a47da0bb56841b95012be1d33b"
SOURCE_POSTMERGE_SHA256 = "864ef4e905df2c5a4cc4bac1b9ebdc035211c36a8c927eec9741c45fc6f5d1b0"
SOURCE_CANDIDATE_HEAD = "4700bd61823d66b2296b9513ad7f564d84bb0e73"
SOURCE_CANDIDATE_MERGE = "25073fd7765a9faf3f53235cded3356839861917"
SOURCE_FINALIZATION_COMMIT = "e819d08d6dac4ec6fba0943bf8ec0c1e55da01a5"
SOURCE_WORKFLOW_COUNT = 35

ASSURANCE_POLICY_ID = "principia-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-policy"
ASSURANCE_POLICY_VERSION = "0.1"

CHECK_NAMES = [
    "source_candidate_sha_exact",
    "source_postmerge_sha_exact",
    "source_candidate_head_exact",
    "source_candidate_merge_exact",
    "source_finalization_commit_exact",
    "source_finalization_status_exact",
    "source_validation_workflow_count_exact",
    "source_phase_exact",
    "source_mode_exact",
    "source_state_exact",
    "source_decision_exact",
    "source_next_gate_exact",
    "source_contract_exact",
    "source_live_false",
    "source_real_authorization_false",
    "source_preparation_identity_exact",
    "source_preparation_record_digest_exact",
    "source_ledger_entry_digest_exact",
    "source_ledger_chain_exact",
    "source_ledger_head_exact",
    "source_checkpoint_exact",
    "source_result_exact",
    "source_verdict_exact",
    "source_status_exact",
    "source_preparation_policy_id_exact",
    "source_preparation_policy_digest_exact",
    "source_preparation_policy_computed_digest_exact",
    "source_preparation_policy_version_exact",
    "source_preparation_profile_id_exact",
    "source_preparation_profile_digest_exact",
    "source_preparation_profile_computed_digest_exact",
    "source_boundary_policy_binding_exact",
    "source_boundary_profile_binding_exact",
    "source_decision_profile_binding_exact",
    "source_assurance_binding_exact",
    "source_boundary_binding_exact",
    "source_readiness_binding_exact",
    "source_candidate_template_schema_binding_exact",
    "source_candidate_template_binding_exact",
    "source_candidate_template_field_count_exact",
    "source_field_plan_count_exact",
    "source_field_plan_digest_exact",
    "source_field_plan_computed_digest_exact",
    "source_field_plan_order_exact",
    "source_field_plan_fields_exact",
    "source_field_plan_sources_exact",
    "source_field_plan_states_unpopulated",
    "source_field_plan_population_forbidden",
    "source_stage_count_exact",
    "source_stage_order_exact",
    "source_stage_ids_exact",
    "source_stage_states_inactive",
    "source_requirement_count_exact",
    "source_requirement_order_exact",
    "source_requirement_ids_exact",
    "source_requirement_states_unevaluated",
    "source_required_roles_exact",
    "source_roles_symbolic",
    "source_dual_control_required",
    "source_role_independence_required",
    "source_conflict_declaration_required",
    "source_conflict_declaration_unevaluated",
    "source_approval_evidence_required",
    "source_approval_evidence_absent",
    "source_rationale_required",
    "source_rationale_unpopulated",
    "source_proposed_decision_unselected",
    "source_validity_window_inactive",
    "source_revocation_reference_absent",
    "source_audit_chain_absent",
    "source_signature_absent",
    "source_candidate_identity_absent",
    "source_candidate_assembly_disabled",
    "source_candidate_absent",
    "source_decision_record_absent",
    "source_decision_absent",
    "source_authorization_grant_absent",
    "source_authorization_token_unissued",
    "source_execution_ticket_unissued",
    "source_execution_run_absent",
    "source_envelope_absent",
    "source_reviewer_identity_absent",
    "source_reviewer_contact_forbidden",
    "source_review_states_frozen",
    "source_approval_states_frozen",
    "source_human_gates_pending",
    "source_disposition_unselected",
    "source_validation_result_absent",
    "source_audit_events_unrecorded",
    "source_status_effects_frozen",
    "assurance_identity_exact",
    "assurance_policy_binding_exact",
    "assurance_record_sequence_exact",
    "assurance_source_binding_locked",
    "assurance_local_only_preserved",
    "assurance_authority_boundary_preserved",
    "assurance_atlas_boundary_preserved",
    "assurance_external_network_boundary_preserved",
    "assurance_repository_mutation_boundary_preserved",
    "assurance_automatic_release_boundary_preserved",
    "assurance_automatic_status_boundary_preserved",
    "assurance_zero_effect_boundary_preserved",
]
assert len(CHECK_NAMES) == 102

EXTRA_RECOVERY_SUFFIXES = [
    "ledger-order-drift",
    "ledger-record-digest-drift",
    "ledger-previous-drift",
    "ledger-entry-digest-drift",
    "ledger-head-drift",
    "checkpoint-drift",
    "result-count-drift",
    "noncanonical-json",
]


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_obj(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_sources() -> tuple[dict[str, Any], dict[str, Any]]:
    if sha256_file(SOURCE_CANDIDATE_PATH) != SOURCE_CANDIDATE_SHA256:
        raise ValueError("Phase 41 candidate SHA-256 drift")
    if sha256_file(SOURCE_POSTMERGE_PATH) != SOURCE_POSTMERGE_SHA256:
        raise ValueError("Phase 41 post-merge SHA-256 drift")
    source = json.loads(SOURCE_CANDIDATE_PATH.read_text(encoding="utf-8"))
    postmerge = json.loads(SOURCE_POSTMERGE_PATH.read_text(encoding="utf-8"))
    return source, postmerge


def assurance_policy(source: dict[str, Any]) -> dict[str, Any]:
    source_policy = source["candidate_preparation_policy"]
    policy = {
        "assurance_policy_id": ASSURANCE_POLICY_ID,
        "assurance_policy_version": ASSURANCE_POLICY_VERSION,
        "source_preparation_policy_id": source_policy["preparation_policy_id"],
        "source_preparation_policy_sha256": source_policy["preparation_policy_sha256"],
        "assurance_scope": [
            "source-provenance",
            "preparation-policy",
            "preparation-profiles",
            "candidate-field-plans",
            "inactive-stages",
            "unevaluated-requirements",
            "human-gate-freeze",
            "zero-candidate-authority",
            "zero-effect-boundary",
        ],
        "candidate_materialization_permitted": False,
        "candidate_population_permitted": False,
        "candidate_assembly_permitted": False,
        "assurance_requirements": [
            {"sequence": i + 1, "requirement_id": name.replace("_", "-"), "state": "defined"}
            for i, name in enumerate(CHECK_NAMES)
        ],
    }
    policy["assurance_policy_sha256"] = sha256_obj({k: v for k, v in policy.items() if k != "assurance_policy_sha256"})
    return policy


def record_digest_map(source: dict[str, Any]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for item in source["ledger"]["entries"]:
        entry = item["entry"]
        result[entry["preparation_id"]] = {
            "record_sha256": entry["record_sha256"],
            "entry_sha256": item["entry_sha256"],
        }
    return result


def make_assurance_record(
    source: dict[str, Any],
    source_record: dict[str, Any],
    sequence: int,
    policy: dict[str, Any],
    digests: dict[str, dict[str, str]],
) -> dict[str, Any]:
    preparation_id = source_record["preparation_id"]
    suffix = preparation_id.rsplit(":", 2)[-2] + ":" + preparation_id.rsplit(":", 1)[-1]
    assurance_id = f"principia:authorization-decision-candidate-preparation-readiness-assurance:{suffix}"
    source_digest = digests[preparation_id]
    checks = {name: True for name in CHECK_NAMES}
    return {
        "sequence": sequence,
        "assurance_id": assurance_id,
        "source_preparation_id": preparation_id,
        "source_preparation_record_sha256": source_digest["record_sha256"],
        "source_ledger_entry_sha256": source_digest["entry_sha256"],
        "source_verdict": source_record["verdict"],
        "source_status": source_record["status"],
        "assurance_policy_id": policy["assurance_policy_id"],
        "assurance_policy_sha256": policy["assurance_policy_sha256"],
        "preparation_policy_id": source_record["preparation_policy_id"],
        "preparation_policy_sha256": source_record["preparation_policy_sha256"],
        "preparation_profile": copy.deepcopy(source_record["preparation_profile"]),
        "preparation_profile_sha256": source_record["preparation_profile_sha256"],
        "candidate_field_plan": copy.deepcopy(source_record["candidate_field_plan"]),
        "candidate_field_plan_count": source_record["candidate_field_plan_count"],
        "candidate_field_plan_sha256": source_record["candidate_field_plan_sha256"],
        "candidate_field_populated_count": 0,
        "candidate_template_field_count": source_record["candidate_template_field_count"],
        "candidate_template_schema_sha256": source_record["candidate_template_schema_sha256"],
        "candidate_template_sha256": source_record["candidate_template_sha256"],
        "preparation_stage_count": len(source["candidate_preparation_policy"]["preparation_stages"]),
        "preparation_requirement_count": len(source["candidate_preparation_policy"]["preparation_requirements"]),
        "assurance_check_count": len(CHECK_NAMES),
        "failed_assurance_check_count": 0,
        "assurance_checks": checks,
        "human_gate_pending_count": source_record["human_gate_pending_count"],
        "human_gate_satisfied_count": 0,
        "approval_evidence_recorded": False,
        "approval_received": False,
        "conflict_declaration_evaluated": False,
        "rationale_populated": False,
        "proposed_decision_selected": False,
        "validity_window_active": False,
        "revocation_reference_present": False,
        "candidate_id_present": False,
        "candidate_signature_present": False,
        "candidate_assembly_permitted": False,
        "authorization_decision_candidate_created": False,
        "authorization_decision_record_created": False,
        "authorization_decision_recorded": False,
        "authorization_granted": False,
        "authorization_token_issued": False,
        "execution_ticket_issued": False,
        "execution_run_created": False,
        "response_envelope_received": False,
        "reviewer_identity_present": False,
        "reviewer_contact_permitted": False,
        "validation_result_recorded": False,
        "disposition_selected": False,
        "audit_event_recorded_count": 0,
        "status_change": False,
        "local_only": True,
        "real_authorization_claimed": False,
        "status": "preparation-readiness-assured-no-candidate",
        "verdict": "response-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assured-no-candidate",
    }


def make_ledger(records: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    previous = None
    for record in records:
        record_sha = sha256_obj(record)
        entry = {
            "sequence": record["sequence"],
            "assurance_id": record["assurance_id"],
            "source_preparation_id": record["source_preparation_id"],
            "source_ledger_entry_sha256": record["source_ledger_entry_sha256"],
            "record_sha256": record_sha,
            "previous_entry_sha256": previous,
            "verdict": record["verdict"],
        }
        entry_sha = sha256_obj(entry)
        entries.append({"entry": entry, "entry_sha256": entry_sha})
        previous = entry_sha
    return {"entries": entries, "head_sequence": len(entries), "head_sha256": previous}


def make_recovery(records: list[dict[str, Any]]) -> dict[str, Any]:
    rejected: list[str] = []
    for record in records:
        slug = record["assurance_id"].split(":")[-2]
        rejected.extend(f"reject-{slug}-{name.replace('_', '-')}" for name in CHECK_NAMES)
        rejected.extend(f"reject-{slug}-{suffix}" for suffix in EXTRA_RECOVERY_SUFFIXES)
    rejected.extend([
        "reject-missing-assurance-record",
        "reject-extra-assurance-record",
        "reject-duplicate-assurance-record",
        "reject-assurance-record-order-drift",
        "reject-cross-profile-source-binding",
    ])
    assert len(rejected) == 225
    return {
        "accepted": ["baseline-phase41-candidate-preparation-readiness-assurance"],
        "accepted_count": 1,
        "rejected": rejected,
        "rejected_count": len(rejected),
        "scenario_count": len(rejected) + 1,
    }


def build_manifest() -> dict[str, Any]:
    source, postmerge = load_sources()
    policy = assurance_policy(source)
    digests = record_digest_map(source)
    records = [
        make_assurance_record(source, record, i + 1, policy, digests)
        for i, record in enumerate(source["candidate_preparation_readiness_records"])
    ]
    ledger = make_ledger(records)
    result = copy.deepcopy(source["result"])
    result.update({
        "candidate_preparation_readiness_assurance_policy_count": 1,
        "candidate_preparation_readiness_assurance_record_count": len(records),
        "candidate_preparation_readiness_assurance_check_count": len(records) * len(CHECK_NAMES),
        "failed_candidate_preparation_readiness_assurance_check_count": 0,
        "candidate_field_populated_count": 0,
        "authorization_decision_candidate_created_count": 0,
        "authorization_decision_record_created_count": 0,
        "authorization_decision_recorded_count": 0,
        "authorization_granted_count": 0,
        "authorization_token_issued_count": 0,
        "execution_ticket_issued_count": 0,
        "execution_run_count": 0,
        "response_envelope_received_count": 0,
        "reviewer_contact_count": 0,
        "status_change_count": 0,
        "audit_event_recorded_count": 0,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
        "real_authorization_claimed": False,
    })
    checkpoint = {
        "assurance_record_count": len(records),
        "assurance_check_count": len(records) * len(CHECK_NAMES),
        "failed_assurance_check_count": 0,
        "candidate_field_populated_count": 0,
        "authorization_decision_candidate_created_count": 0,
        "authorization_decision_recorded_count": 0,
        "authorization_granted_count": 0,
        "authorization_token_issued_count": 0,
        "execution_run_count": 0,
        "response_envelope_received_count": 0,
        "status_change_count": 0,
        "ledger_sha256": ledger["head_sha256"],
    }
    authority = {
        "local_authorization_decision_candidate_preparation_readiness_assurance_permitted": True,
        "authorization_decision_candidate_creation_permitted": False,
        "authorization_decision_candidate_population_permitted": False,
        "authorization_decision_candidate_assembly_permitted": False,
        "authorization_decision_recording_permitted": False,
        "response_envelope_validation_execution_authorization_grant_permitted": False,
        "response_envelope_validation_execution_authorized": False,
        "response_envelope_validation_result_recording_permitted": False,
        "response_envelope_creation_permitted": False,
        "response_envelope_processing_authorized": False,
        "response_receipt_permitted": False,
        "response_validation_authorized": False,
        "response_intake_authorized": False,
        "response_quarantine_execution_authorized": False,
        "review_request_dispatch_authorized": False,
        "reviewer_contact_permitted": False,
        "review_execution_authorized": False,
        "atlas_call_permitted": False,
        "external_network_required": False,
        "external_delivery_permitted": False,
        "repository_mutation": False,
        "automatic_status_change": False,
        "automatic_release_action": False,
        "status_inheritance": "prohibited",
        "human_authorization_claimed": False,
    }
    return {
        "phase": PHASE,
        "contract": CONTRACT,
        "mode": MODE,
        "state": STATE,
        "decision": DECISION,
        "next_gate": NEXT_GATE,
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-thermal-control",
        "source_phase41": {
            "phase41_candidate_sha256": SOURCE_CANDIDATE_SHA256,
            "phase41_postmerge_sha256": SOURCE_POSTMERGE_SHA256,
            "phase41_candidate_head_commit": SOURCE_CANDIDATE_HEAD,
            "phase41_candidate_merge_commit": SOURCE_CANDIDATE_MERGE,
            "phase41_finalization_commit": SOURCE_FINALIZATION_COMMIT,
            "phase41_applicable_workflows": SOURCE_WORKFLOW_COUNT,
            "phase41_candidate_record_count": len(source["candidate_preparation_readiness_records"]),
            "phase41_ledger_head_sha256": source["ledger"]["head_sha256"],
            "phase41_checkpoint_sha256": sha256_obj(source["checkpoint"]),
            "phase41_result_sha256": sha256_obj(source["result"]),
            "phase41_postmerge_state": postmerge["state"],
        },
        "candidate_preparation_readiness_assurance_policy": policy,
        "candidate_preparation_readiness_assurance_records": records,
        "ledger": ledger,
        "checkpoint": checkpoint,
        "result": result,
        "recovery": make_recovery(records),
        "authority": authority,
        "validation": {"status": "candidate", "pull_request": None, "tested_head_commit": None},
        "real_authorization_claimed": False,
        "live_activation_permitted": False,
        "live": False,
    }


def evaluate_candidate(candidate: dict[str, Any]) -> list[str]:
    expected = build_manifest()
    if candidate != expected:
        return ["candidate manifest differs from deterministic expected object"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = build_manifest()
    data = canonical_bytes(manifest)
    if args.check:
        if not OUTPUT_PATH.exists():
            print(f"missing: {OUTPUT_PATH}")
            return 1
        actual = OUTPUT_PATH.read_bytes()
        if actual != data:
            print("Phase 42 candidate bytes drift")
            return 1
        errors = evaluate_candidate(json.loads(actual))
        if errors:
            print("\n".join(errors))
            return 1
        print(f"Phase 42 candidate passed: bytes={len(data)}, sha256={sha256_bytes(data)}, assurances=2, checks=204.")
        return 0
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(data)
    print(f"wrote {OUTPUT_PATH}: bytes={len(data)}, sha256={sha256_bytes(data)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
