#!/usr/bin/env python3
"""Independently validate Phase 49 population-execution authorization readiness."""
from __future__ import annotations
import copy, hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
MODE = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness'
STATE = MODE + "-candidate"
DECISION = 'response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-recorded-no-authorization-granted'
NEXT = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-assurance-candidate'
MANIFEST = ROOT / f"release/phase-49-{MODE}.json"
SOURCE_CANDIDATE = ROOT / "release/phase-48-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance.json"
SOURCE_POSTMERGE = ROOT / "release/phase-48-postmerge.json"
MANIFEST_SHA = "3c073e7a2b320987e86795aa053967e4a83eb2ec42ce36828322e6e6f31b4b4d"
SOURCE_CANDIDATE_SHA = '9bfebeca19a7ce8f15c2e377db773fea78a479e773735318ac1cfc4d97f3e628'
SOURCE_POSTMERGE_SHA = '2acb658af81739e76369065743e13e83031a60c43ddcb75eb03fad5c1c7e2a82'
SOURCE_FINALIZATION_COMMIT = '745a433b0f5175d0debbed6da56bf216ddf1f752'
SOURCE_POLICY_SHA = '8674f2b36586b517a422865733de952f26c1e20f71a773f3ae922cfb36771afc'
SOURCE_PROFILE_SHAS = ['e8575b682de9f8d999744b696ddc9012380241fce32f4a684481c085d134c827', 'c9edc7f08eff62a0606e227494614aedc3ba1ef76ce7aa7be83894dd18a97ff3']
SOURCE_RECORD_SHAS = ['dc6d5b8121f7ab53f0963c59f21e33bac231cac236ded4d43a754f28a743f8de', 'bdec63ea6a3a087c8be937bc7b295a93dadabb28cf388f87aced7356f8d1b35d']
CHECK_SET_SHA = '1c6e73f5757e9d59bc7b85196f6ebffb904c53d09bb314b296a94f2afab1a773'
CHECK_COUNT = 136
AUTHORIZATION_STAGES = ['source-provenance-lock', 'assurance-profile-resolution', 'operation-set-binding', 'authorization-scope-definition', 'human-gate-requirement-lock', 'approval-role-separation', 'execution-ticket-template-binding', 'authorization-token-template-binding', 'validity-window-control', 'revocation-control', 'audit-record-preparation', 'authorization-grant-freeze']
AUTHORIZATION_REQUIREMENTS = ['source-assurance-candidate-pinned', 'source-assurance-postmerge-pinned', 'source-finalization-commit-pinned', 'source-assurance-policy-pinned', 'source-assurance-profile-pinned', 'source-assurance-record-pinned', 'source-assurance-ledger-pinned', 'population-slots-remain-empty', 'population-references-remain-symbolic', 'population-values-remain-absent', 'operation-set-order-pinned', 'operation-set-digest-pinned', 'operation-dispatch-remains-forbidden', 'execution-stages-remain-inactive', 'preconditions-remain-unevaluated', 'rollback-rules-remain-inactive', 'execution-ticket-remains-blank', 'candidate-identity-remains-absent', 'candidate-body-remains-absent', 'candidate-signature-remains-absent', 'human-gates-remain-pending', 'population-operator-role-required', 'reviewer-role-required', 'authorization-officer-role-required', 'three-role-independence-required', 'authorization-scope-defined', 'source-snapshot-binding-defined', 'engine-binding-defined', 'resource-binding-defined', 'one-time-use-defined', 'revocation-path-defined', 'authorization-grant-remains-absent']
TOKEN_FIELDS = ['authorization_id', 'authorization_request_id', 'profile_id', 'candidate_id', 'population_operator_identity', 'reviewer_identity', 'authorization_officer_identity', 'source_snapshot_sha256', 'operation_set_sha256', 'execution_ticket_id', 'granted_at', 'expires_at', 'one_time_nonce', 'revocation_id', 'revocation_reason', 'approval_evidence_sha256', 'authorization_signature_ref', 'authorization_reference']
REQUIRED_ROLES = ["population-operator", "reviewer", "authorization-officer"]

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

def operation_ids(sequence: int) -> list[str]:
    prefix = f"principia:phase47-population-execution:{sequence:04d}"
    return [f"{prefix}:operation:{index:02d}" for index in range(1, 19)]

def validate_document(document: Any) -> list[str]:
    errors: list[str] = []
    require(errors, isinstance(document, dict), "manifest must be object")
    if not isinstance(document, dict):
        return errors
    expected_root = {
        "contract": "principia-phase49-population-execution-authorization-readiness/0.1",
        "phase": 49, "mode": MODE, "state": STATE, "decision": DECISION, "next_gate": NEXT,
        "fixture_kind": "bounded-synthetic", "live": False, "live_activation_permitted": False,
        "real_authorization_claimed": False,
    }
    for key, value in expected_root.items():
        require(errors, document.get(key) == value, key + " drift")
    expected_source = {
        "candidate_sha256": SOURCE_CANDIDATE_SHA,
        "postmerge_sha256": SOURCE_POSTMERGE_SHA,
        "authoritative_finalization_commit": SOURCE_FINALIZATION_COMMIT,
        "state": "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance-validated",
        "decision": "response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assured-no-population-run",
        "next_gate": STATE, "applicable_workflows": 41,
        "population_execution_assurance_policy_count": 1,
        "population_execution_assurance_profile_count": 2,
        "population_execution_assurance_record_count": 2,
        "population_execution_assurance_check_count": 240,
        "failed_population_execution_assurance_check_count": 0,
        "population_slot_count": 36, "populated_slot_count": 0,
        "symbolic_reference_count": 36, "resolved_reference_count": 0,
        "population_operation_count": 36, "dispatched_operation_count": 0,
        "execution_stage_count": 20, "active_stage_count": 0,
        "execution_precondition_count": 48, "evaluated_precondition_count": 0,
        "rollback_rule_count": 36, "invoked_rollback_count": 0,
        "blank_execution_ticket_count": 2, "blank_execution_ticket_field_count": 24,
        "human_gate_pending_count": 12, "human_gate_satisfied_count": 0,
    }
    require(errors, document.get("source_phase48") == expected_source, "source binding drift")
    policy = document.get("authorization_readiness_policy")
    validate_signed(errors, policy, "policy")
    policy_sha = policy.get("sha256") if isinstance(policy, dict) else None
    if isinstance(policy, dict):
        require(errors, policy.get("id") == "principia-phase49-population-execution-authorization-readiness-policy", "policy id drift")
        require(errors, policy.get("version") == "0.1", "policy version drift")
        require(errors, policy.get("source_candidate_sha256") == SOURCE_CANDIDATE_SHA, "policy source candidate drift")
        require(errors, policy.get("source_postmerge_sha256") == SOURCE_POSTMERGE_SHA, "policy source postmerge drift")
        require(errors, policy.get("source_finalization_commit") == SOURCE_FINALIZATION_COMMIT, "policy finalization drift")
        require(errors, policy.get("source_assurance_policy_sha256") == SOURCE_POLICY_SHA, "policy source assurance drift")
        check_ids = policy.get("check_ids")
        require(errors, isinstance(check_ids, list) and len(check_ids) == CHECK_COUNT, "policy check count drift")
        require(errors, isinstance(check_ids, list) and digest(check_ids) == CHECK_SET_SHA, "policy check set drift")
        expected_policy_counts = {
            "authorization_profile_count":2,"authorization_stage_count":24,"authorization_requirement_count":64,
            "required_approval_role_count":6,"blank_authorization_token_count":2,
            "blank_authorization_token_field_count":36,"population_slot_count":36,"populated_slot_count":0,
            "symbolic_reference_count":36,"resolved_reference_count":0,"population_operation_count":36,
            "dispatched_operation_count":0,"execution_stage_count":20,"active_stage_count":0,
            "execution_precondition_count":48,"evaluated_precondition_count":0,"rollback_rule_count":36,
            "invoked_rollback_count":0,"blank_execution_ticket_count":2,"blank_execution_ticket_field_count":24,
            "human_gate_pending_count":12,"human_gate_satisfied_count":0,"dual_control_required":True,
            "role_independence_required":True,"local_population_execution_authorization_readiness_planning_permitted":True,
            "authorization_request_creation_permitted":False,"approval_evaluation_permitted":False,
            "authorization_decision_recording_permitted":False,"authorization_grant_permitted":False,
            "authorization_token_issuance_permitted":False,
        }
        for key, value in expected_policy_counts.items():
            require(errors, policy.get(key) == value, "policy " + key + " drift")
    profiles = document.get("authorization_readiness_profiles")
    records = document.get("authorization_readiness_records")
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
            require(errors, profile.get("source_population_execution_assurance_sequence") == sequence, f"profile {sequence} source sequence drift")
            require(errors, profile.get("source_population_execution_assurance_profile_sha256") == SOURCE_PROFILE_SHAS[sequence-1], f"profile {sequence} source profile drift")
            require(errors, profile.get("source_population_execution_assurance_record_sha256") == SOURCE_RECORD_SHAS[sequence-1], f"profile {sequence} source record drift")
            require(errors, profile.get("policy_sha256") == policy_sha, f"profile {sequence} policy drift")
            require(errors, profile.get("required_roles") == REQUIRED_ROLES, f"profile {sequence} roles drift")
            require(errors, profile.get("assigned_role_count") == 0, f"profile {sequence} assigned roles drift")
            require(errors, profile.get("dual_control_required") is True, f"profile {sequence} dual control drift")
            require(errors, profile.get("role_independence_required") is True, f"profile {sequence} independence drift")
            astages = profile.get("authorization_stages")
            require(errors, isinstance(astages, list) and len(astages) == 12, f"profile {sequence} stage count drift")
            if isinstance(astages, list):
                for index, stage in enumerate(astages, 1):
                    require(errors, stage == {
                        "id": f"principia:phase49-population-execution-authorization:{sequence:04d}:stage:{index:02d}",
                        "sequence": index, "stage_kind": AUTHORIZATION_STAGES[index-1],
                        "state": "defined-not-active", "activation_permitted": False,
                    }, f"profile {sequence} stage {index} drift")
            reqs = profile.get("authorization_requirements")
            require(errors, isinstance(reqs, list) and len(reqs) == 32, f"profile {sequence} requirement count drift")
            if isinstance(reqs, list):
                for index, requirement in enumerate(reqs, 1):
                    require(errors, requirement == {
                        "id": f"principia:phase49-population-execution-authorization:{sequence:04d}:requirement:{index:02d}",
                        "sequence": index, "requirement_kind": AUTHORIZATION_REQUIREMENTS[index-1],
                        "state": "required-not-evaluated", "evaluation_permitted": False,
                    }, f"profile {sequence} requirement {index} drift")
            approvals = profile.get("approval_roles")
            require(errors, isinstance(approvals, list) and len(approvals) == 3, f"profile {sequence} approvals drift")
            if isinstance(approvals, list):
                for index, role in enumerate(REQUIRED_ROLES, 1):
                    require(errors, approvals[index-1] == {"sequence":index,"role":role,"state":"required-not-satisfied","identity":None,"approval_evidence_sha256":None}, f"profile {sequence} approval {index} drift")
            scope = profile.get("authorization_scope")
            expected_scope = {
                "profile_bound":True,"source_snapshot_bound":True,"operation_set_bound":True,
                "engine_bound":True,"resource_bound":True,"one_time_use":True,"maximum_operation_count":18,
                "source_snapshot_sha256":SOURCE_CANDIDATE_SHA,"operation_set_sha256":digest(operation_ids(sequence)),
                "external_network":False,"atlas_access":False,"repository_write":False,
                "result_recording_enabled":False,"status_change_enabled":False,
            }
            require(errors, scope == expected_scope, f"profile {sequence} scope drift")
            require(errors, profile.get("validity_window_policy") == {"maximum_seconds":900,"state":"defined-not-active"}, f"profile {sequence} validity drift")
            require(errors, profile.get("revocation_policy") == {"immediate_revocation_supported":True,"state":"defined-not-active"}, f"profile {sequence} revocation drift")
            token = profile.get("authorization_token_template")
            require(errors, isinstance(token, dict), f"profile {sequence} token missing")
            if isinstance(token, dict):
                require(errors, token.get("issued") is False and token.get("state") == "blank-not-issued", f"profile {sequence} token state drift")
                for field in TOKEN_FIELDS:
                    require(errors, token.get(field) is None, f"profile {sequence} token field populated: {field}")
                require(errors, set(token) == set(TOKEN_FIELDS) | {"issued","state"}, f"profile {sequence} token shape drift")
            require(errors, profile.get("authorization_grant_permitted") is False, f"profile {sequence} grant escalated")
            record_shas.append(record.get("sha256"))
            expected_record = {
                "sequence":sequence,"source_population_execution_assurance_sequence":sequence,
                "policy_sha256":policy_sha,"profile_sha256":profile.get("sha256"),
                "check_set_sha256":CHECK_SET_SHA,"passed_check_count":CHECK_COUNT,"failed_check_count":0,
                "authorization_stage_count":12,"active_authorization_stage_count":0,
                "authorization_requirement_count":32,"evaluated_authorization_requirement_count":0,
                "required_approval_role_count":3,"satisfied_approval_role_count":0,
                "blank_authorization_token_count":1,"blank_authorization_token_field_count":18,
                "population_slot_count":18,"populated_slot_count":0,"symbolic_reference_count":18,
                "resolved_reference_count":0,"population_operation_count":18,"dispatched_operation_count":0,
                "execution_stage_count":10,"active_execution_stage_count":0,"execution_precondition_count":24,
                "evaluated_precondition_count":0,"rollback_rule_count":18,"invoked_rollback_count":0,
                "blank_execution_ticket_count":1,"blank_execution_ticket_field_count":12,
                "human_gate_pending_count":6,"human_gate_satisfied_count":0,
                "reviewer_identity_count":0,"reviewer_contact_count":0,"validation_result_count":0,
                "audit_event_count":0,"status_change_count":0,"real_authorization_claimed":False,
                "local_only":True,"status":"population-execution-authorization-readiness-defined-no-grant",
                "verdict":DECISION,
            }
            for key, value in expected_record.items():
                require(errors, record.get(key) == value, f"record {sequence} {key} drift")
            for key in ("authorization_request_created","approval_evaluated","authorization_decision_recorded",
                        "authorization_granted","authorization_token_issued","candidate_created","candidate_assembled",
                        "candidate_population_started","candidate_populated","candidate_persisted","candidate_submitted",
                        "source_resolution_started","value_insertion_started","operation_dispatched","stage_activated",
                        "precondition_evaluated","rollback_invoked","execution_ticket_issued","execution_run_created",
                        "envelope_received"):
                require(errors, record.get(key) is False, f"record {sequence} {key} escalated")
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
                    require(errors, entry.get("record_sha256") == record_shas[sequence-1], f"ledger entry {sequence} record drift")
                    require(errors, entry.get("previous_entry_sha256") == previous, f"ledger entry {sequence} chain drift")
                    previous = digest(entry)
                    require(errors, wrapped.get("entry_sha256") == previous, f"ledger entry {sequence} digest drift")
        require(errors, ledger.get("head_sequence") == 2, "ledger head sequence drift")
        require(errors, ledger.get("head_sha256") == previous, "ledger head digest drift")
    require(errors, document.get("recovery_matrix") == {
        "scenario_count":318,"baseline_count":1,"mutation_count":317,"rejected_mutation_count":317,
        "categories":["source-provenance","authorization-profile-integrity","authorization-stage-integrity",
                      "authorization-requirement-integrity","approval-role-integrity","authorization-scope-integrity",
                      "token-integrity","execution-boundary","human-governance","authority-boundary",
                      "ledger-integrity","recovery-determinism"]}, "recovery matrix drift")
    authority = document.get("authority")
    require(errors, isinstance(authority, dict), "authority missing")
    if isinstance(authority, dict):
        require(errors, authority.get("local_population_execution_authorization_readiness_planning_permitted") is True, "local readiness disabled")
        require(errors, authority.get("status_inheritance") == "prohibited", "status inheritance drift")
        for key in ("authorization_request_creation_permitted","approval_evaluation_permitted",
                    "authorization_decision_recording_permitted","authorization_grant_permitted",
                    "authorization_token_issuance_permitted","source_resolution_permitted","value_insertion_permitted",
                    "operation_dispatch_permitted","stage_activation_permitted","precondition_evaluation_permitted",
                    "rollback_invocation_permitted","execution_ticket_issuance_permitted","candidate_creation_permitted",
                    "candidate_assembly_permitted","candidate_population_permitted","candidate_persistence_permitted",
                    "candidate_submission_permitted","reviewer_contact_permitted","validation_execution_permitted",
                    "token_issuance_permitted","atlas_call_permitted","external_network_required","repository_mutation",
                    "automatic_status_change","automatic_release_action","human_authorization_claimed"):
            require(errors, authority.get(key) is False, "authority " + key + " escalated")
    result = document.get("result")
    expected_result = {
        "authorization_readiness_policy_count":1,"authorization_readiness_profile_count":2,
        "authorization_readiness_record_count":2,"authorization_readiness_check_count":CHECK_COUNT*2,
        "failed_authorization_readiness_check_count":0,"source_population_execution_assurance_check_count":240,
        "source_failed_population_execution_assurance_check_count":0,"authorization_stage_count":24,
        "active_authorization_stage_count":0,"authorization_requirement_count":64,
        "evaluated_authorization_requirement_count":0,"required_approval_role_count":6,
        "satisfied_approval_role_count":0,"blank_authorization_token_count":2,
        "blank_authorization_token_field_count":36,"population_slot_count":36,"populated_slot_count":0,
        "symbolic_reference_count":36,"resolved_reference_count":0,"population_operation_count":36,
        "dispatched_operation_count":0,"execution_stage_count":20,"active_execution_stage_count":0,
        "execution_precondition_count":48,"evaluated_precondition_count":0,"rollback_rule_count":36,
        "invoked_rollback_count":0,"blank_execution_ticket_count":2,"blank_execution_ticket_field_count":24,
        "human_gate_pending_count":12,"human_gate_satisfied_count":0,"authorization_request_count":0,
        "approval_evaluation_count":0,"authorization_decision_count":0,"authorization_grant_count":0,
        "authorization_token_count":0,"candidate_count":0,"population_run_count":0,"execution_run_count":0,
        "envelope_count":0,"reviewer_identity_count":0,"reviewer_contact_count":0,
        "validation_result_count":0,"audit_event_count":0,"status_change_count":0,
        "real_authorization_claimed":False,
    }
    require(errors, result == expected_result, "result drift")
    return errors

def validate_files() -> list[str]:
    errors: list[str] = []
    for path, label in ((MANIFEST,"manifest"),(SOURCE_CANDIDATE,"source candidate"),(SOURCE_POSTMERGE,"source postmerge")):
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
    if post.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance-validated":
        errors.append("source state drift")
    if post.get("next_gate") != STATE:
        errors.append("source next gate drift")
    if post.get("validation") != {"applicable_workflows":41,"candidate_head_commit":"24b133e90195bbd8bec36f6952e3f782d481ae27","status":"success"}:
        errors.append("source validation drift")
    errors.extend(validate_document(json.loads(MANIFEST.read_text(encoding="utf-8"))))
    return errors

def main() -> int:
    errors = validate_files()
    if errors:
        print("Phase 49 authorization-readiness errors:", file=sys.stderr)
        for error in errors:
            print("- " + error, file=sys.stderr)
        return 1
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print(f"Phase 49 population-execution authorization readiness passed: manifest={MANIFEST_SHA}, checks={document['result']['authorization_readiness_check_count']}, scenarios={document['recovery_matrix']['scenario_count']}.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
