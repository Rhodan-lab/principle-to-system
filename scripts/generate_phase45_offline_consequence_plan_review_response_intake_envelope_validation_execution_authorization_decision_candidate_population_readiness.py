#!/usr/bin/env python3
"""Generate deterministic Phase 45 candidate-population readiness evidence."""
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "release/phase-44-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance.json"
POSTMERGE = ROOT / "release/phase-44-postmerge.json"
OUTPUT = ROOT / "release/phase-45-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness.json"
MODE = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness'
STATE = MODE + "-candidate"
DECISION = 'response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-defined-no-candidate-populated'
NEXT = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance-candidate'
SOURCE_SHA = 'f6e807f7c56513c0a13265f833cefeca3f9b9503d52b8826a4055069220d08c6'
POST_SHA = '131e1886494caf9d686d8b4303ffe755b70146fb6b1b3f3577cf3564d2d75322'
HEAD = 'b58811f3b01dbb68992c4ee638978a06bbb095e7'
MERGE = 'd5756679785e283f044b191e01945009a506e8ec'
FINAL = '84e82c1c3ff6b87499f4f5130dd288da99f9cc31'
CHECK_IDS = ['source-candidate-sha-exact', 'source-postmerge-sha-exact', 'source-phase-exact', 'source-mode-exact', 'source-state-exact', 'source-decision-exact', 'source-next-gate-exact', 'source-validation-exact', 'source-finalization-exact', 'source-live-false', 'source-real-authorization-false', 'source-assurance-policy-count-exact', 'source-assurance-profile-count-exact', 'source-assurance-record-count-exact', 'source-assurance-check-count-exact', 'source-failed-assurance-check-count-zero', 'source-slot-count-exact', 'source-populated-slot-count-zero', 'source-stage-count-exact', 'source-active-stage-count-zero', 'source-requirement-count-exact', 'source-evaluated-requirement-count-zero', 'source-human-gates-pending-exact', 'source-human-gates-satisfied-zero', 'population-policy-binding-exact', 'population-profile-binding-exact', 'population-record-sequence-exact', 'population-slot-count-exact', 'population-slot-order-exact', 'population-slot-names-exact', 'population-slot-source-kinds-exact', 'population-slot-source-references-symbolic', 'population-slot-values-absent', 'population-slot-readiness-blocked', 'population-slot-permission-false', 'population-stage-count-exact', 'population-stage-order-exact', 'population-stage-states-inactive', 'population-requirement-count-exact', 'population-requirement-order-exact', 'population-requirement-states-unevaluated', 'population-requirement-permission-false', 'dual-control-required', 'role-independence-required', 'candidate-identity-absent', 'candidate-body-absent', 'candidate-signature-absent', 'candidate-creation-forbidden', 'candidate-assembly-forbidden', 'candidate-population-forbidden', 'candidate-persistence-forbidden', 'candidate-submission-forbidden', 'population-run-absent', 'decision-selection-absent', 'decision-recording-absent', 'authorization-grant-absent', 'token-issuance-absent', 'execution-ticket-absent', 'execution-run-absent', 'response-envelope-absent', 'validation-result-absent', 'reviewer-identity-absent', 'reviewer-contact-forbidden', 'human-gate-satisfaction-absent', 'audit-event-absent', 'status-change-absent', 'atlas-boundary-preserved', 'external-network-boundary-preserved', 'repository-mutation-boundary-preserved', 'automatic-status-boundary-preserved', 'live-false', 'authority-separated']
SLOTS = [('candidate_version', 'human-governance'), ('candidate_id', 'human-governance'), ('source_assurance_id', 'phase44-assurance'), ('source_assembly_id', 'phase43-assembly'), ('policy_id', 'phase40-boundary-policy'), ('profile_id', 'phase40-boundary-profile'), ('reviewer_role', 'human-role-assignment'), ('authorization_officer_role', 'human-role-assignment'), ('conflict_declaration_ref', 'human-governance'), ('approval_evidence_ref', 'human-governance'), ('rationale', 'human-governance'), ('proposed_decision', 'human-governance'), ('validity_start', 'human-governance'), ('validity_end', 'human-governance'), ('revocation_ref', 'human-governance'), ('audit_chain_ref', 'human-governance'), ('candidate_signature', 'human-signature'), ('submission_target', 'human-governance')]
STAGES = ['source-lock', 'candidate-schema-lock', 'assembly-readiness-lock', 'population-source-map-lock', 'data-classification-plan', 'human-source-availability-plan', 'role-binding-plan', 'conflict-declaration-source-plan', 'approval-evidence-source-plan', 'rationale-source-plan', 'decision-source-plan', 'validity-source-plan', 'revocation-source-plan', 'audit-source-plan', 'signature-source-plan', 'completeness-plan', 'consistency-plan', 'population-authorization-plan']
REQUIREMENTS = ['source-candidate-digest-exact', 'source-postmerge-digest-exact', 'source-finalization-commit-exact', 'source-phase-exact', 'source-state-validated', 'source-next-gate-exact', 'source-validation-success', 'assurance-policy-count-exact', 'assurance-profile-count-exact', 'assurance-record-count-exact', 'assurance-check-count-exact', 'failed-assurance-check-count-zero', 'source-slot-count-exact', 'source-populated-slot-count-zero', 'source-stage-count-exact', 'source-active-stage-count-zero', 'source-requirement-count-exact', 'source-evaluated-requirement-count-zero', 'population-slot-schema-defined', 'population-slot-order-defined', 'population-source-kinds-defined', 'population-source-references-symbolic', 'population-values-absent', 'population-readiness-blocked', 'population-permission-forbidden', 'population-stage-order-defined', 'population-stage-activation-forbidden', 'population-requirement-order-defined', 'population-requirement-evaluation-forbidden', 'dual-control-required', 'role-independence-required', 'candidate-creation-forbidden', 'candidate-population-forbidden', 'candidate-persistence-forbidden', 'atlas-call-forbidden', 'external-network-forbidden']

def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()

def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()

def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def signed(value: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(value)
    result["sha256"] = digest(result)
    return result

def source_errors() -> list[str]:
    errors: list[str] = []
    if not SOURCE.is_file() or file_digest(SOURCE) != SOURCE_SHA:
        errors.append("Phase 44 candidate source drift")
    if not POSTMERGE.is_file() or file_digest(POSTMERGE) != POST_SHA:
        return errors + ["Phase 44 post-merge source drift"]
    post = json.loads(POSTMERGE.read_text(encoding="utf-8"))
    expected = {
        "phase": 44,
        "state": "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance-validated",
        "decision": "response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assured-no-candidate-assembled",
        "next_gate": STATE,
        "live": False,
        "real_authorization_claimed": False,
    }
    for key, value in expected.items():
        if post.get(key) != value:
            errors.append(f"Phase 44 {key} drift")
    if post.get("candidate_record") != {
        "path": SOURCE.relative_to(ROOT).as_posix(),
        "sha256": SOURCE_SHA,
    }:
        errors.append("Phase 44 candidate binding drift")
    if post.get("principia") != {
        "candidate_head_commit": HEAD,
        "merge_commit": MERGE,
        "pull_request": 80,
        "repository": "Rhodan-lab/principle-to-system",
    }:
        errors.append("Phase 44 merge provenance drift")
    if post.get("validation") != {
        "applicable_workflows": 37,
        "candidate_head_commit": HEAD,
        "status": "success",
    }:
        errors.append("Phase 44 validation provenance drift")
    return errors

def build_manifest() -> dict[str, Any]:
    population_plan = [
        {
            "sequence": index + 1,
            "name": name,
            "source_kind": source_kind,
            "source_reference_state": "symbolic-unresolved",
            "value_state": "absent",
            "readiness_state": "blocked",
            "required": True,
            "population_permitted": False,
        }
        for index, (name, source_kind) in enumerate(SLOTS)
    ]
    stage_plan = [
        {"sequence": index + 1, "id": stage, "state": "inactive", "activation_permitted": False}
        for index, stage in enumerate(STAGES)
    ]
    requirement_plan = [
        {"sequence": index + 1, "id": requirement, "state": "unevaluated", "evaluation_permitted": False}
        for index, requirement in enumerate(REQUIREMENTS)
    ]
    policy = signed({
        "id": "principia-phase45-population-readiness-policy",
        "version": "0.1",
        "source_candidate_sha256": SOURCE_SHA,
        "source_postmerge_sha256": POST_SHA,
        "check_ids": CHECK_IDS,
        "population_plan": population_plan,
        "stages": stage_plan,
        "requirements": requirement_plan,
        "population_readiness_definition_permitted": True,
        "candidate_creation_permitted": False,
        "candidate_assembly_permitted": False,
        "candidate_population_permitted": False,
        "candidate_persistence_permitted": False,
        "candidate_submission_permitted": False,
    })
    check_sha = digest(CHECK_IDS)
    plan_sha = digest(population_plan)
    stage_sha = digest(stage_plan)
    requirement_sha = digest(requirement_plan)
    profiles: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for sequence in (1, 2):
        profile = signed({
            "id": f"principia:phase45-population-readiness-profile:{sequence:04d}",
            "sequence": sequence,
            "source_assurance_sequence": sequence,
            "source_candidate_sha256": SOURCE_SHA,
            "source_postmerge_sha256": POST_SHA,
            "policy_sha256": policy["sha256"],
            "required_roles": ["reviewer", "authorization-officer"],
            "dual_control_required": True,
            "role_independence_required": True,
            "population_permitted": False,
        })
        profiles.append(profile)
        records.append(signed({
            "id": f"principia:phase45-population-readiness-record:{sequence:04d}",
            "sequence": sequence,
            "source_assurance_sequence": sequence,
            "policy_sha256": policy["sha256"],
            "profile_sha256": profile["sha256"],
            "check_set_sha256": check_sha,
            "passed_check_count": 72,
            "failed_check_count": 0,
            "population_plan_sha256": plan_sha,
            "source_assembly_slot_count": 18,
            "population_slot_count": 18,
            "populated_slot_count": 0,
            "stage_plan_sha256": stage_sha,
            "stage_count": 18,
            "active_stage_count": 0,
            "requirement_plan_sha256": requirement_sha,
            "requirement_count": 36,
            "evaluated_requirement_count": 0,
            "human_gate_pending_count": 5,
            "human_gate_satisfied_count": 0,
            "candidate_created": False,
            "candidate_assembled": False,
            "candidate_population_started": False,
            "candidate_populated": False,
            "candidate_persisted": False,
            "candidate_submitted": False,
            "decision_selected": False,
            "decision_recorded": False,
            "authorization_granted": False,
            "token_issued": False,
            "ticket_issued": False,
            "execution_run_created": False,
            "envelope_received": False,
            "reviewer_identity_count": 0,
            "reviewer_contact_count": 0,
            "validation_result_count": 0,
            "audit_event_count": 0,
            "status_change_count": 0,
            "real_authorization_claimed": False,
            "local_only": True,
            "status": "population-readiness-defined-no-candidate",
            "verdict": DECISION,
        }))
    entries: list[dict[str, Any]] = []
    previous: str | None = None
    for record in records:
        entry = {
            "sequence": record["sequence"],
            "previous_entry_sha256": previous,
            "record_id": record["id"],
            "record_sha256": record["sha256"],
        }
        previous = digest(entry)
        entries.append({"entry": entry, "entry_sha256": previous})
    source = {
        "candidate_sha256": SOURCE_SHA,
        "postmerge_sha256": POST_SHA,
        "candidate_head_commit": HEAD,
        "candidate_merge_commit": MERGE,
        "authoritative_finalization_commit": FINAL,
        "applicable_workflows": 37,
        "state": "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance-validated",
        "assurance_policy_count": 1,
        "assurance_profile_count": 2,
        "assurance_record_count": 2,
        "assurance_check_count": 96,
        "failed_assurance_check_count": 0,
        "source_check_count": 128,
        "slot_count": 36,
        "populated_slot_count": 0,
        "stage_count": 32,
        "active_stage_count": 0,
        "requirement_count": 64,
        "evaluated_requirement_count": 0,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
    }
    authority = {
        "local_population_readiness_definition_permitted": True,
        "candidate_creation_permitted": False,
        "candidate_assembly_permitted": False,
        "candidate_population_permitted": False,
        "candidate_persistence_permitted": False,
        "candidate_submission_permitted": False,
        "decision_selection_permitted": False,
        "decision_recording_permitted": False,
        "authorization_grant_permitted": False,
        "token_issuance_permitted": False,
        "execution_ticket_issuance_permitted": False,
        "validation_execution_permitted": False,
        "reviewer_contact_permitted": False,
        "atlas_call_permitted": False,
        "external_network_required": False,
        "repository_mutation": False,
        "automatic_release_action": False,
        "automatic_status_change": False,
        "human_authorization_claimed": False,
        "status_inheritance": "prohibited",
    }
    result = {
        "source_assurance_policy_count": 1,
        "source_assurance_profile_count": 2,
        "source_assurance_record_count": 2,
        "source_assurance_check_count": 96,
        "source_failed_assurance_check_count": 0,
        "source_assembly_check_count": 128,
        "source_assembly_slot_count": 36,
        "source_populated_slot_count": 0,
        "source_stage_count": 32,
        "source_active_stage_count": 0,
        "source_requirement_count": 64,
        "source_evaluated_requirement_count": 0,
        "population_readiness_policy_count": 1,
        "population_readiness_profile_count": 2,
        "population_readiness_record_count": 2,
        "population_check_count": 144,
        "failed_population_check_count": 0,
        "population_slot_count": 36,
        "populated_slot_count": 0,
        "population_stage_count": 36,
        "active_stage_count": 0,
        "population_requirement_count": 72,
        "evaluated_requirement_count": 0,
        "human_gate_pending_count": 10,
        "human_gate_satisfied_count": 0,
        "candidate_count": 0,
        "candidate_population_run_count": 0,
        "decision_count": 0,
        "grant_count": 0,
        "token_count": 0,
        "ticket_count": 0,
        "execution_run_count": 0,
        "envelope_count": 0,
        "reviewer_identity_count": 0,
        "reviewer_contact_count": 0,
        "validation_result_count": 0,
        "audit_event_count": 0,
        "status_change_count": 0,
        "real_authorization_claimed": False,
    }
    return {
        "contract": "principia-phase45-population-readiness/0.1",
        "phase": 45,
        "mode": MODE,
        "state": STATE,
        "decision": DECISION,
        "next_gate": NEXT,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "live_activation_permitted": False,
        "real_authorization_claimed": False,
        "source_phase44": source,
        "population_readiness_policy": policy,
        "population_readiness_profiles": profiles,
        "population_readiness_records": records,
        "ledger": {"entries": entries, "head_sequence": 2, "head_sha256": previous},
        "checkpoint": {
            "record_count": 2,
            "check_count": 144,
            "failed_check_count": 0,
            "candidate_count": 0,
            "populated_slot_count": 0,
            "human_gate_satisfied_count": 0,
            "status_change_count": 0,
            "ledger_sha256": previous,
        },
        "recovery": {
            "accepted": ["baseline-phase45-population-readiness"],
            "accepted_count": 1,
            "record_count": 2,
            "check_families": 72,
            "structural_mutations_per_record": 42,
            "global_mutations": 85,
            "scenario_count": 170,
            "rejected_count": 169,
        },
        "authority": authority,
        "result": result,
        "validation": {"status": "candidate", "pull_request": None, "tested_head_commit": None},
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = source_errors()
    if errors:
        print("\n".join(errors))
        return 1
    data = canonical(build_manifest())
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(data)
        print(f"wrote {OUTPUT.relative_to(ROOT)} sha256={hashlib.sha256(data).hexdigest()}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_bytes() != data:
        print("Phase 45 deterministic bytes drift")
        return 1
    print(f"Phase 45 deterministic bytes passed: sha256={hashlib.sha256(data).hexdigest()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
