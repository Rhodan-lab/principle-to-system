#!/usr/bin/env python3
"""Independently validate Phase 47 population-execution readiness."""
from __future__ import annotations
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness"
STATE = MODE + "-candidate"
DECISION = "response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-recorded-no-population-run"
NEXT = MODE + "-assurance-candidate"
MANIFEST = ROOT / f"release/phase-47-{MODE}.json"
SOURCE_CANDIDATE = ROOT / "release/phase-46-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance.json"
SOURCE_POSTMERGE = ROOT / "release/phase-46-postmerge.json"
MANIFEST_SHA = "31b57486ca590cd066642981e640c21cc306869f99241d0fa81013d681df5065"
SOURCE_CANDIDATE_SHA = "2b7ced60688ff02ea11231bc53bad3e39e0ec22aa10a233e5f270b0d586039ad"
SOURCE_POSTMERGE_SHA = "b9ccbd2125db1538bb1b4028b3dd15411971baba72bf059448d64fa32ccee121"
SOURCE_FINALIZATION_COMMIT = "87ccadcdbbc579593f4ef3fffc0194d7cbfce01e"
CHECK_SET_SHA = "3f5d00db5d24bdfeff76a8774a5d87792e2487363f563a0a74f3ed61871977bd"
SOURCE_RECORD_SHAS = [
    "78907d0086df6856d85fe86fb2af432f578bebb2567707106adf0ef29eab23f2",
    "37a27fb3db161498c606294f97401be558fd3f77f5d714925df5345ed2c4c6a4",
]
TICKET_FIELDS = [
    "ticket_id", "candidate_id", "profile_id", "operator_identity", "reviewer_identity",
    "authorization_officer_identity", "source_snapshot_sha256", "operation_set_sha256",
    "approved_at", "expires_at", "signature", "authorization_reference",
]


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


def validate_document(document: Any) -> list[str]:
    errors: list[str] = []
    require(errors, isinstance(document, dict), "manifest must be object")
    if not isinstance(document, dict):
        return errors

    expected_root = {
        "contract": "principia-phase47-population-execution-readiness/0.1",
        "phase": 47,
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

    source = document.get("source_phase46")
    expected_source = {
        "candidate_sha256": SOURCE_CANDIDATE_SHA,
        "postmerge_sha256": SOURCE_POSTMERGE_SHA,
        "authoritative_finalization_commit": SOURCE_FINALIZATION_COMMIT,
        "state": "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance-validated",
        "decision": "response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assured-no-candidate-populated",
        "next_gate": STATE,
        "applicable_workflows": 39,
        "population_assurance_policy_count": 1,
        "population_assurance_profile_count": 2,
        "population_assurance_record_count": 2,
        "population_assurance_check_count": 160,
        "failed_population_assurance_check_count": 0,
        "population_slot_count": 36,
        "populated_slot_count": 0,
        "symbolic_reference_count": 36,
        "population_stage_count": 36,
        "active_stage_count": 0,
        "population_requirement_count": 72,
        "evaluated_requirement_count": 0,
        "human_gate_pending_count": 10,
        "human_gate_satisfied_count": 0,
    }
    require(errors, source == expected_source, "source binding drift")

    policy = document.get("population_execution_readiness_policy")
    validate_signed(errors, policy, "policy")
    policy_sha = policy.get("sha256") if isinstance(policy, dict) else None
    if isinstance(policy, dict):
        require(errors, policy.get("id") == "principia-phase47-population-execution-readiness-policy", "policy id drift")
        require(errors, policy.get("version") == "0.1", "policy version drift")
        require(errors, policy.get("source_candidate_sha256") == SOURCE_CANDIDATE_SHA, "policy source candidate drift")
        require(errors, policy.get("source_postmerge_sha256") == SOURCE_POSTMERGE_SHA, "policy source postmerge drift")
        require(errors, policy.get("source_finalization_commit") == SOURCE_FINALIZATION_COMMIT, "policy source finalization drift")
        check_ids = policy.get("check_ids")
        require(errors, isinstance(check_ids, list) and len(check_ids) == 98, "policy check count drift")
        require(errors, isinstance(check_ids, list) and digest(check_ids) == CHECK_SET_SHA, "policy check set drift")
        expected_policy_counts = {
            "population_execution_plan_count": 2,
            "population_slot_count": 36,
            "populated_slot_count": 0,
            "blocked_slot_count": 36,
            "symbolic_reference_count": 36,
            "resolved_reference_count": 0,
            "population_operation_count": 36,
            "dispatched_operation_count": 0,
            "execution_stage_count": 20,
            "active_stage_count": 0,
            "execution_precondition_count": 48,
            "evaluated_precondition_count": 0,
            "rollback_rule_count": 36,
            "invoked_rollback_count": 0,
            "blank_execution_ticket_count": 2,
            "blank_execution_ticket_field_count": 24,
            "human_gate_pending_count": 12,
            "human_gate_satisfied_count": 0,
            "dual_control_required": True,
            "role_independence_required": True,
            "local_population_execution_planning_permitted": True,
            "source_resolution_permitted": False,
            "value_insertion_permitted": False,
            "operation_dispatch_permitted": False,
            "candidate_creation_permitted": False,
            "candidate_assembly_permitted": False,
            "candidate_population_permitted": False,
            "candidate_persistence_permitted": False,
            "candidate_submission_permitted": False,
        }
        for key, value in expected_policy_counts.items():
            require(errors, policy.get(key) == value, "policy " + key + " drift")

    profiles = document.get("population_execution_profiles")
    records = document.get("population_execution_readiness_records")
    require(errors, isinstance(profiles, list) and len(profiles) == 2, "profiles drift")
    require(errors, isinstance(records, list) and len(records) == 2, "records drift")
    record_shas: list[str | None] = []
    if isinstance(profiles, list) and isinstance(records, list) and len(profiles) == len(records) == 2:
        for sequence, (profile, record) in enumerate(zip(profiles, records), 1):
            validate_signed(errors, profile, f"profile {sequence}")
            validate_signed(errors, record, f"record {sequence}")
            if not isinstance(profile, dict) or not isinstance(record, dict):
                continue
            require(errors, profile.get("sequence") == sequence, f"profile {sequence} sequence drift")
            require(errors, profile.get("source_population_assurance_sequence") == sequence, f"profile {sequence} source sequence drift")
            require(errors, profile.get("source_population_assurance_record_sha256") == SOURCE_RECORD_SHAS[sequence - 1], f"profile {sequence} source record drift")
            require(errors, profile.get("policy_sha256") == policy_sha, f"profile {sequence} policy drift")
            require(errors, profile.get("required_roles") == ["population-operator", "reviewer", "authorization-officer"], f"profile {sequence} roles drift")
            require(errors, profile.get("assigned_role_count") == 0, f"profile {sequence} role assignment drift")
            require(errors, profile.get("dual_control_required") is True, f"profile {sequence} dual control drift")
            require(errors, profile.get("role_independence_required") is True, f"profile {sequence} independence drift")
            require(errors, profile.get("population_execution_permitted") is False, f"profile {sequence} execution escalated")

            operations = profile.get("operations")
            stages = profile.get("stages")
            preconditions = profile.get("preconditions")
            rollbacks = profile.get("rollback_rules")
            ticket = profile.get("execution_ticket_template")
            require(errors, isinstance(operations, list) and len(operations) == 18, f"profile {sequence} operation count drift")
            if isinstance(operations, list):
                require(errors, [item.get("sequence") for item in operations] == list(range(1, 19)), f"profile {sequence} operation order drift")
                require(errors, len({item.get("id") for item in operations}) == 18, f"profile {sequence} operation ids drift")
                for item in operations:
                    require(errors, item.get("source_resolved") is False, f"profile {sequence} source resolved")
                    require(errors, item.get("value") is None, f"profile {sequence} value inserted")
                    require(errors, item.get("state") == "planned-not-started", f"profile {sequence} operation state drift")
                    require(errors, item.get("dispatch_permitted") is False, f"profile {sequence} dispatch escalated")
            require(errors, isinstance(stages, list) and len(stages) == 10, f"profile {sequence} stage count drift")
            if isinstance(stages, list):
                for item in stages:
                    require(errors, item.get("state") == "inactive" and item.get("activation_permitted") is False, f"profile {sequence} stage escalated")
            require(errors, isinstance(preconditions, list) and len(preconditions) == 24, f"profile {sequence} precondition count drift")
            if isinstance(preconditions, list):
                for item in preconditions:
                    require(errors, item.get("state") == "unevaluated" and item.get("evaluation_permitted") is False, f"profile {sequence} precondition escalated")
            require(errors, isinstance(rollbacks, list) and len(rollbacks) == 18, f"profile {sequence} rollback count drift")
            if isinstance(rollbacks, list):
                operation_ids = {item.get("id") for item in operations} if isinstance(operations, list) else set()
                for item in rollbacks:
                    require(errors, item.get("operation_id") in operation_ids, f"profile {sequence} rollback binding drift")
                    require(errors, item.get("state") == "inactive" and item.get("invocation_permitted") is False, f"profile {sequence} rollback escalated")
            require(errors, isinstance(ticket, dict) and set(ticket.keys()) == set(TICKET_FIELDS), f"profile {sequence} ticket schema drift")
            if isinstance(ticket, dict):
                require(errors, all(value is None for value in ticket.values()), f"profile {sequence} ticket contamination")

            expected_record = {
                "sequence": sequence,
                "source_population_assurance_sequence": sequence,
                "policy_sha256": policy_sha,
                "profile_sha256": profile.get("sha256"),
                "check_set_sha256": CHECK_SET_SHA,
                "passed_check_count": 98,
                "failed_check_count": 0,
                "population_slot_count": 18,
                "populated_slot_count": 0,
                "blocked_slot_count": 18,
                "symbolic_reference_count": 18,
                "resolved_reference_count": 0,
                "population_operation_count": 18,
                "dispatched_operation_count": 0,
                "execution_stage_count": 10,
                "active_stage_count": 0,
                "execution_precondition_count": 24,
                "evaluated_precondition_count": 0,
                "rollback_rule_count": 18,
                "invoked_rollback_count": 0,
                "blank_execution_ticket_count": 1,
                "blank_execution_ticket_field_count": 12,
                "human_gate_pending_count": 6,
                "human_gate_satisfied_count": 0,
                "reviewer_identity_count": 0,
                "reviewer_contact_count": 0,
                "validation_result_count": 0,
                "audit_event_count": 0,
                "status_change_count": 0,
                "real_authorization_claimed": False,
                "local_only": True,
                "status": "population-execution-readiness-defined-no-run",
                "verdict": DECISION,
            }
            for key, value in expected_record.items():
                require(errors, record.get(key) == value, f"record {sequence} {key} drift")
            for key in (
                "candidate_created", "candidate_assembled", "candidate_population_started", "candidate_populated",
                "candidate_persisted", "candidate_submitted", "source_resolution_started", "value_insertion_started",
                "operation_dispatched", "stage_activated", "precondition_evaluated", "rollback_invoked",
                "ticket_issued", "decision_selected", "decision_recorded", "authorization_granted",
                "token_issued", "execution_run_created", "envelope_received",
            ):
                require(errors, record.get(key) is False, f"record {sequence} {key} escalated")
            record_shas.append(record.get("sha256"))

    ledger = document.get("ledger")
    previous = None
    require(errors, isinstance(ledger, dict), "ledger missing")
    if isinstance(ledger, dict):
        entries = ledger.get("entries")
        require(errors, isinstance(entries, list) and len(entries) == 2, "ledger entries drift")
        if isinstance(entries, list) and len(record_shas) == 2:
            for sequence, wrapped in enumerate(entries, 1):
                entry = wrapped.get("entry") if isinstance(wrapped, dict) else None
                require(errors, isinstance(entry, dict), f"ledger entry {sequence} missing")
                if isinstance(entry, dict):
                    require(errors, entry.get("sequence") == sequence, f"ledger entry {sequence} sequence drift")
                    require(errors, entry.get("record_sha256") == record_shas[sequence - 1], f"ledger entry {sequence} record drift")
                    require(errors, entry.get("previous_entry_sha256") == previous, f"ledger entry {sequence} chain drift")
                    previous = digest(entry)
                    require(errors, wrapped.get("entry_sha256") == previous, f"ledger entry {sequence} digest drift")
        require(errors, ledger.get("head_sequence") == 2, "ledger head sequence drift")
        require(errors, ledger.get("head_sha256") == previous, "ledger head digest drift")

    expected_recovery = {
        "scenario_count": 224,
        "baseline_count": 1,
        "mutation_count": 223,
        "rejected_mutation_count": 223,
        "categories": [
            "source-provenance", "execution-plan-integrity", "population-operation-integrity",
            "execution-stage-integrity", "precondition-integrity", "rollback-integrity",
            "ticket-integrity", "human-governance", "authority-boundary",
            "ledger-integrity", "recovery-determinism",
        ],
    }
    require(errors, document.get("recovery_matrix") == expected_recovery, "recovery matrix drift")

    authority = document.get("authority")
    require(errors, isinstance(authority, dict), "authority missing")
    if isinstance(authority, dict):
        require(errors, authority.get("local_population_execution_planning_permitted") is True, "local planning disabled")
        require(errors, authority.get("status_inheritance") == "prohibited", "status inheritance drift")
        for key in (
            "source_resolution_permitted", "value_insertion_permitted", "operation_dispatch_permitted",
            "stage_activation_permitted", "precondition_evaluation_permitted", "rollback_invocation_permitted",
            "candidate_creation_permitted", "candidate_assembly_permitted", "candidate_population_permitted",
            "candidate_persistence_permitted", "candidate_submission_permitted", "decision_selection_permitted",
            "decision_recording_permitted", "authorization_grant_permitted", "token_issuance_permitted",
            "execution_ticket_issuance_permitted", "validation_execution_permitted", "reviewer_contact_permitted",
            "atlas_call_permitted", "external_network_required", "repository_mutation", "automatic_status_change",
            "automatic_release_action", "human_authorization_claimed",
        ):
            require(errors, authority.get(key) is False, "authority " + key + " escalated")

    expected_result = {
        "population_execution_readiness_policy_count": 1,
        "population_execution_profile_count": 2,
        "population_execution_readiness_record_count": 2,
        "population_execution_readiness_check_count": 196,
        "failed_population_execution_readiness_check_count": 0,
        "source_population_assurance_check_count": 160,
        "source_failed_population_assurance_check_count": 0,
        "population_slot_count": 36,
        "populated_slot_count": 0,
        "blocked_slot_count": 36,
        "symbolic_reference_count": 36,
        "resolved_reference_count": 0,
        "population_operation_count": 36,
        "dispatched_operation_count": 0,
        "execution_stage_count": 20,
        "active_stage_count": 0,
        "execution_precondition_count": 48,
        "evaluated_precondition_count": 0,
        "rollback_rule_count": 36,
        "invoked_rollback_count": 0,
        "blank_execution_ticket_count": 2,
        "blank_execution_ticket_field_count": 24,
        "human_gate_pending_count": 12,
        "human_gate_satisfied_count": 0,
        "candidate_count": 0,
        "candidate_population_run_count": 0,
        "source_resolution_count": 0,
        "value_insertion_count": 0,
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
    require(errors, document.get("result") == expected_result, "result drift")
    return errors


def validate_files() -> list[str]:
    errors: list[str] = []
    for path, label in ((MANIFEST, "manifest"), (SOURCE_CANDIDATE, "source candidate"), (SOURCE_POSTMERGE, "source postmerge")):
        if not path.is_file():
            errors.append(label + " missing")
    if errors:
        return errors
    if file_digest(MANIFEST) != MANIFEST_SHA:
        errors.append("manifest digest drift")
    if file_digest(SOURCE_CANDIDATE) != SOURCE_CANDIDATE_SHA:
        errors.append("source candidate digest drift")
    if file_digest(SOURCE_POSTMERGE) != SOURCE_POSTMERGE_SHA:
        errors.append("source postmerge digest drift")
    post = json.loads(SOURCE_POSTMERGE.read_text(encoding="utf-8"))
    if post.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance-validated":
        errors.append("source state drift")
    if post.get("next_gate") != STATE:
        errors.append("source next gate drift")
    if post.get("validation") != {
        "applicable_workflows": 39,
        "candidate_head_commit": "e108372f76503ca819afd3e6573e7efaf8e5a295",
        "status": "success",
    }:
        errors.append("source validation drift")
    errors.extend(validate_document(json.loads(MANIFEST.read_text(encoding="utf-8"))))
    return errors


def main() -> int:
    errors = validate_files()
    if errors:
        print("Phase 47 population-execution readiness errors:", file=sys.stderr)
        for error in errors:
            print("- " + error, file=sys.stderr)
        return 1
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print(
        "Phase 47 population-execution readiness passed: "
        f"manifest={MANIFEST_SHA}, checks={document['result']['population_execution_readiness_check_count']}, "
        f"scenarios={document['recovery_matrix']['scenario_count']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
