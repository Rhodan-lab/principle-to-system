#!/usr/bin/env python3
"""Independently validate Phase 45 candidate-population readiness."""
from __future__ import annotations
import copy, hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "release/phase-45-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness.json"
SOURCE = ROOT / "release/phase-44-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance.json"
POSTMERGE = ROOT / "release/phase-44-postmerge.json"
MANIFEST_SHA = '3fa7ce42cce65231c394f27f248e68ce40799ba9a5ccf183923c59fa9da851d6'
SOURCE_SHA = 'f6e807f7c56513c0a13265f833cefeca3f9b9503d52b8826a4055069220d08c6'
POST_SHA = '131e1886494caf9d686d8b4303ffe755b70146fb6b1b3f3577cf3564d2d75322'
HEAD = 'b58811f3b01dbb68992c4ee638978a06bbb095e7'
MERGE = 'd5756679785e283f044b191e01945009a506e8ec'
FINAL = '84e82c1c3ff6b87499f4f5130dd288da99f9cc31'
MODE = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness'
STATE = MODE + "-candidate"
DECISION = 'response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-defined-no-candidate-populated'
NEXT = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance-candidate'
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

def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)

def validate_signed(errors: list[str], value: Any, label: str) -> None:
    require(errors, isinstance(value, dict), label + " missing")
    if isinstance(value, dict):
        unsigned = copy.deepcopy(value)
        actual = unsigned.pop("sha256", None)
        require(errors, actual == digest(unsigned), label + " digest drift")

def expected_population_plan() -> list[dict[str, Any]]:
    return [
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

def expected_stage_plan() -> list[dict[str, Any]]:
    return [
        {"sequence": index + 1, "id": stage, "state": "inactive", "activation_permitted": False}
        for index, stage in enumerate(STAGES)
    ]

def expected_requirement_plan() -> list[dict[str, Any]]:
    return [
        {"sequence": index + 1, "id": requirement, "state": "unevaluated", "evaluation_permitted": False}
        for index, requirement in enumerate(REQUIREMENTS)
    ]

def validate_document(document: Any) -> list[str]:
    errors: list[str] = []
    require(errors, isinstance(document, dict), "manifest must be object")
    if not isinstance(document, dict):
        return errors
    expected_root = {
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
    }
    for key, value in expected_root.items():
        require(errors, document.get(key) == value, key + " drift")
    expected_source = {
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
    require(errors, document.get("source_phase44") == expected_source, "source binding drift")
    policy = document.get("population_readiness_policy")
    validate_signed(errors, policy, "policy")
    population_plan = expected_population_plan()
    stage_plan = expected_stage_plan()
    requirement_plan = expected_requirement_plan()
    if isinstance(policy, dict):
        require(errors, policy.get("id") == "principia-phase45-population-readiness-policy", "policy id drift")
        require(errors, policy.get("version") == "0.1", "policy version drift")
        require(errors, policy.get("source_candidate_sha256") == SOURCE_SHA, "policy source candidate drift")
        require(errors, policy.get("source_postmerge_sha256") == POST_SHA, "policy source postmerge drift")
        require(errors, policy.get("check_ids") == CHECK_IDS, "check ids drift")
        require(errors, policy.get("population_plan") == population_plan, "population plan drift")
        require(errors, policy.get("stages") == stage_plan, "stage plan drift")
        require(errors, policy.get("requirements") == requirement_plan, "requirement plan drift")
        require(errors, policy.get("population_readiness_definition_permitted") is True, "population-readiness definition disabled")
        for key in (
            "candidate_creation_permitted","candidate_assembly_permitted",
            "candidate_population_permitted","candidate_persistence_permitted","candidate_submission_permitted",
        ):
            require(errors, policy.get(key) is False, key + " escalated")
    profiles = document.get("population_readiness_profiles")
    records = document.get("population_readiness_records")
    require(errors, isinstance(profiles, list) and len(profiles) == 2, "profiles drift")
    require(errors, isinstance(records, list) and len(records) == 2, "records drift")
    policy_sha = policy.get("sha256") if isinstance(policy, dict) else None
    check_sha = digest(CHECK_IDS)
    plan_sha = digest(population_plan)
    stage_sha = digest(stage_plan)
    requirement_sha = digest(requirement_plan)
    if isinstance(profiles, list):
        for sequence, profile in enumerate(profiles, 1):
            validate_signed(errors, profile, f"profile {sequence}")
            if isinstance(profile, dict):
                require(errors, profile.get("sequence") == sequence, f"profile {sequence} sequence drift")
                require(errors, profile.get("source_assurance_sequence") == sequence, f"profile {sequence} source sequence drift")
                require(errors, profile.get("source_candidate_sha256") == SOURCE_SHA, f"profile {sequence} source candidate drift")
                require(errors, profile.get("source_postmerge_sha256") == POST_SHA, f"profile {sequence} source postmerge drift")
                require(errors, profile.get("policy_sha256") == policy_sha, f"profile {sequence} policy drift")
                require(errors, profile.get("required_roles") == ["reviewer", "authorization-officer"], f"profile {sequence} roles drift")
                require(errors, profile.get("dual_control_required") is True, f"profile {sequence} dual control drift")
                require(errors, profile.get("role_independence_required") is True, f"profile {sequence} role independence drift")
                require(errors, profile.get("population_permitted") is False, f"profile {sequence} population escalated")
    record_shas: list[str | None] = []
    if isinstance(records, list):
        for sequence, record in enumerate(records, 1):
            validate_signed(errors, record, f"record {sequence}")
            if not isinstance(record, dict):
                continue
            record_shas.append(record.get("sha256"))
            profile_sha = profiles[sequence - 1].get("sha256") if isinstance(profiles, list) and len(profiles) >= sequence and isinstance(profiles[sequence - 1], dict) else None
            require(errors, record.get("sequence") == sequence, f"record {sequence} sequence drift")
            require(errors, record.get("source_assurance_sequence") == sequence, f"record {sequence} source sequence drift")
            require(errors, record.get("policy_sha256") == policy_sha, f"record {sequence} policy drift")
            require(errors, record.get("profile_sha256") == profile_sha, f"record {sequence} profile drift")
            expected_record = {
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
                "reviewer_identity_count": 0,
                "reviewer_contact_count": 0,
                "validation_result_count": 0,
                "audit_event_count": 0,
                "status_change_count": 0,
            }
            for key, value in expected_record.items():
                require(errors, record.get(key) == value, f"record {sequence} {key} drift")
            for key in (
                "candidate_created","candidate_assembled","candidate_population_started","candidate_populated",
                "candidate_persisted","candidate_submitted","decision_selected","decision_recorded",
                "authorization_granted","token_issued","ticket_issued","execution_run_created",
                "envelope_received","real_authorization_claimed",
            ):
                require(errors, record.get(key) is False, f"record {sequence} {key} escalated")
            require(errors, record.get("local_only") is True, f"record {sequence} local boundary drift")
            require(errors, record.get("status") == "population-readiness-defined-no-candidate", f"record {sequence} status drift")
            require(errors, record.get("verdict") == DECISION, f"record {sequence} verdict drift")
    ledger = document.get("ledger")
    require(errors, isinstance(ledger, dict), "ledger missing")
    previous: str | None = None
    if isinstance(ledger, dict):
        entries = ledger.get("entries")
        require(errors, isinstance(entries, list) and len(entries) == 2, "ledger count drift")
        if isinstance(entries, list):
            for sequence, wrapper in enumerate(entries, 1):
                entry = wrapper.get("entry", {}) if isinstance(wrapper, dict) else {}
                require(errors, entry.get("sequence") == sequence, f"ledger {sequence} sequence drift")
                require(errors, entry.get("previous_entry_sha256") == previous, f"ledger {sequence} chain drift")
                expected_record_sha = record_shas[sequence - 1] if len(record_shas) >= sequence else None
                require(errors, entry.get("record_sha256") == expected_record_sha, f"ledger {sequence} record drift")
                previous = digest(entry)
                require(errors, isinstance(wrapper, dict) and wrapper.get("entry_sha256") == previous, f"ledger {sequence} digest drift")
        require(errors, ledger.get("head_sequence") == 2, "ledger head sequence drift")
        require(errors, ledger.get("head_sha256") == previous, "ledger head digest drift")
    authority = document.get("authority")
    require(errors, isinstance(authority, dict), "authority missing")
    if isinstance(authority, dict):
        require(errors, authority.get("local_population_readiness_definition_permitted") is True, "local definition disabled")
        for key, value in authority.items():
            if key not in ("local_population_readiness_definition_permitted", "status_inheritance"):
                require(errors, value is False, key + " authority escalated")
        require(errors, authority.get("status_inheritance") == "prohibited", "status inheritance drift")
    expected_result = {'source_assurance_policy_count': 1, 'source_assurance_profile_count': 2, 'source_assurance_record_count': 2, 'source_assurance_check_count': 96, 'source_failed_assurance_check_count': 0, 'source_assembly_check_count': 128, 'source_assembly_slot_count': 36, 'source_populated_slot_count': 0, 'source_stage_count': 32, 'source_active_stage_count': 0, 'source_requirement_count': 64, 'source_evaluated_requirement_count': 0, 'population_readiness_policy_count': 1, 'population_readiness_profile_count': 2, 'population_readiness_record_count': 2, 'population_check_count': 144, 'failed_population_check_count': 0, 'population_slot_count': 36, 'populated_slot_count': 0, 'population_stage_count': 36, 'active_stage_count': 0, 'population_requirement_count': 72, 'evaluated_requirement_count': 0, 'human_gate_pending_count': 10, 'human_gate_satisfied_count': 0, 'candidate_count': 0, 'candidate_population_run_count': 0, 'decision_count': 0, 'grant_count': 0, 'token_count': 0, 'ticket_count': 0, 'execution_run_count': 0, 'envelope_count': 0, 'reviewer_identity_count': 0, 'reviewer_contact_count': 0, 'validation_result_count': 0, 'audit_event_count': 0, 'status_change_count': 0, 'real_authorization_claimed': False}
    require(errors, document.get("result") == expected_result, "result drift")
    expected_checkpoint = {
        "record_count": 2,
        "check_count": 144,
        "failed_check_count": 0,
        "candidate_count": 0,
        "populated_slot_count": 0,
        "human_gate_satisfied_count": 0,
        "status_change_count": 0,
        "ledger_sha256": previous,
    }
    require(errors, document.get("checkpoint") == expected_checkpoint, "checkpoint drift")
    expected_recovery = {
        "accepted": ["baseline-phase45-population-readiness"],
        "accepted_count": 1,
        "record_count": 2,
        "check_families": 72,
        "structural_mutations_per_record": 42,
        "global_mutations": 85,
        "scenario_count": 170,
        "rejected_count": 169,
    }
    require(errors, document.get("recovery") == expected_recovery, "recovery drift")
    require(errors, document.get("validation") == {"status": "candidate", "pull_request": None, "tested_head_commit": None}, "validation marker drift")
    return errors

def source_errors() -> list[str]:
    errors: list[str] = []
    if not SOURCE.is_file() or file_digest(SOURCE) != SOURCE_SHA:
        errors.append("Phase 44 candidate source drift")
    if not POSTMERGE.is_file() or file_digest(POSTMERGE) != POST_SHA:
        return errors + ["Phase 44 post-merge source drift"]
    post = json.loads(POSTMERGE.read_text(encoding="utf-8"))
    require(errors, post.get("state") == "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance-validated", "Phase 44 state drift")
    require(errors, post.get("next_gate") == STATE, "Phase 44 next gate drift")
    require(errors, post.get("candidate_record") == {"path": SOURCE.relative_to(ROOT).as_posix(), "sha256": SOURCE_SHA}, "Phase 44 candidate binding drift")
    require(errors, post.get("principia") == {"candidate_head_commit": HEAD, "merge_commit": MERGE, "pull_request": 80, "repository": "Rhodan-lab/principle-to-system"}, "Phase 44 merge provenance drift")
    require(errors, post.get("validation") == {"applicable_workflows": 37, "candidate_head_commit": HEAD, "status": "success"}, "Phase 44 validation drift")
    return errors

def main() -> int:
    errors = source_errors()
    if not MANIFEST.is_file():
        errors.append("Phase 45 manifest missing")
    else:
        if file_digest(MANIFEST) != MANIFEST_SHA:
            errors.append("Phase 45 manifest digest drift")
        try:
            document = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append("Phase 45 parse failure: " + str(exc))
        else:
            errors.extend(validate_document(document))
    if errors:
        print("Phase 45 validation errors:", file=sys.stderr)
        for error in errors:
            print("- " + error, file=sys.stderr)
        return 1
    print(f"Phase 45 population readiness passed: manifest={MANIFEST_SHA}, checks=144, records=2, scenarios=170.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
