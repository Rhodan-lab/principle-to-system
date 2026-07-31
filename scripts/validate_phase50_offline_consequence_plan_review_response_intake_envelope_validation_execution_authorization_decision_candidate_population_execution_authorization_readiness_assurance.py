#!/usr/bin/env python3
"""Independently validate Phase 50 population-execution authorization-readiness assurance."""
from __future__ import annotations
import copy, hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'release/phase-50-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-assurance.json'
SOURCE_CANDIDATE = ROOT / "release/phase-49-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness.json"
SOURCE_POSTMERGE = ROOT / "release/phase-49-postmerge.json"
MANIFEST_SHA = 'ad47b053302b8c9b2237d6d0b9c8c48b80b51e4b8d14734d407a3afb3023fe66'
SOURCE_CANDIDATE_SHA = '3c073e7a2b320987e86795aa053967e4a83eb2ec42ce36828322e6e6f31b4b4d'
SOURCE_POSTMERGE_SHA = 'e7f592280777c12c9ed51d70241729797db9dad053ddc234dbeaf492322c8413'
SOURCE_FINALIZATION_COMMIT = '9c978cbee503142b120470ea44058f2910ccce43'
SOURCE_POLICY_SHA = '6492e338561d1e96aa5740590d0e43a95dffb50065422ee8ad0861998c68233d'
SOURCE_PROFILE_SHAS = ['a14608e3d21d69b54884fe759261ee5cdaa202526c8f4b0a1ddea7ee07460c54', 'fe8fb5bf8730f0605546e25f81d31f5984ef004ca2901ee35f63a7b01a511f72']
SOURCE_RECORD_SHAS = ['cfe003748f6445382f493f853b068c4401e15d96ef19369c906e086d837d52e6', 'ffb75c1cc887918bb2bdb7a1a2a8416124b79ade0b792897aa494055cac7b410']
SOURCE_LEDGER_HEAD = '5f145721ff7a38e38dd7d306ef4ce70f13eb10756cb67c0b519ad31f4891be03'
MODE = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-assurance'
STATE = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-assurance-candidate'
DECISION = 'response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-assured-no-authorization-granted'
NEXT = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-decision-readiness-candidate'
CHECK_SET_SHA = 'f2e58333efbfcf522e7c964ea2846797acdf069da82bf5f8ad04c56fc753706d'
EXPECTED_SOURCE = json.loads('{"active_authorization_stage_count":0,"active_execution_stage_count":0,"applicable_workflows":42,"authoritative_finalization_commit":"9c978cbee503142b120470ea44058f2910ccce43","authorization_readiness_check_count":272,"authorization_readiness_policy_count":1,"authorization_readiness_profile_count":2,"authorization_readiness_record_count":2,"authorization_requirement_count":64,"authorization_stage_count":24,"blank_authorization_token_count":2,"blank_authorization_token_field_count":36,"blank_execution_ticket_count":2,"blank_execution_ticket_field_count":24,"candidate_sha256":"3c073e7a2b320987e86795aa053967e4a83eb2ec42ce36828322e6e6f31b4b4d","decision":"response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-recorded-no-authorization-granted","dispatched_operation_count":0,"evaluated_authorization_requirement_count":0,"evaluated_precondition_count":0,"execution_precondition_count":48,"execution_stage_count":20,"failed_authorization_readiness_check_count":0,"human_gate_pending_count":12,"human_gate_satisfied_count":0,"invoked_rollback_count":0,"next_gate":"offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-assurance-candidate","populated_slot_count":0,"population_operation_count":36,"population_slot_count":36,"postmerge_sha256":"e7f592280777c12c9ed51d70241729797db9dad053ddc234dbeaf492322c8413","required_approval_role_count":6,"resolved_reference_count":0,"rollback_rule_count":36,"satisfied_approval_role_count":0,"state":"offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-validated","symbolic_reference_count":36}')
EXPECTED_RESULT = json.loads('{"active_authorization_stage_count":0,"active_execution_stage_count":0,"approval_evaluation_count":0,"audit_event_count":0,"authorization_assurance_check_count":288,"authorization_assurance_policy_count":1,"authorization_assurance_profile_count":2,"authorization_assurance_record_count":2,"authorization_decision_count":0,"authorization_grant_count":0,"authorization_request_count":0,"authorization_requirement_count":64,"authorization_stage_count":24,"authorization_token_count":0,"blank_authorization_token_count":2,"blank_authorization_token_field_count":36,"blank_execution_ticket_count":2,"blank_execution_ticket_field_count":24,"candidate_count":0,"dispatched_operation_count":0,"envelope_count":0,"evaluated_authorization_requirement_count":0,"evaluated_precondition_count":0,"execution_precondition_count":48,"execution_run_count":0,"execution_stage_count":20,"failed_authorization_assurance_check_count":0,"human_gate_pending_count":12,"human_gate_satisfied_count":0,"invoked_rollback_count":0,"populated_slot_count":0,"population_operation_count":36,"population_run_count":0,"population_slot_count":36,"real_authorization_claimed":false,"required_approval_role_count":6,"resolved_reference_count":0,"reviewer_contact_count":0,"reviewer_identity_count":0,"rollback_rule_count":36,"satisfied_approval_role_count":0,"source_authorization_readiness_check_count":272,"source_failed_authorization_readiness_check_count":0,"status_change_count":0,"symbolic_reference_count":36,"validation_result_count":0}')
EXPECTED_AUTHORITY = json.loads('{"approval_evaluation_permitted":false,"atlas_call_permitted":false,"authorization_decision_recording_permitted":false,"authorization_grant_permitted":false,"authorization_request_creation_permitted":false,"authorization_token_issuance_permitted":false,"automatic_release_action":false,"automatic_status_change":false,"candidate_assembly_permitted":false,"candidate_creation_permitted":false,"candidate_persistence_permitted":false,"candidate_population_permitted":false,"candidate_submission_permitted":false,"execution_ticket_issuance_permitted":false,"external_network_required":false,"human_authorization_claimed":false,"local_population_execution_authorization_readiness_assurance_permitted":true,"operation_dispatch_permitted":false,"precondition_evaluation_permitted":false,"repository_mutation":false,"reviewer_contact_permitted":false,"rollback_invocation_permitted":false,"source_resolution_permitted":false,"stage_activation_permitted":false,"status_inheritance":"prohibited","token_issuance_permitted":false,"validation_execution_permitted":false,"value_insertion_permitted":false}')
FALSE_RECORD_FIELDS = ['authorization_request_created', 'approval_evaluated', 'authorization_decision_recorded', 'authorization_granted', 'authorization_token_issued', 'execution_ticket_issued', 'execution_run_created', 'candidate_created', 'candidate_assembled', 'candidate_population_started', 'candidate_populated', 'candidate_persisted', 'candidate_submitted', 'source_resolution_started', 'value_insertion_started', 'operation_dispatched', 'stage_activated', 'precondition_evaluated', 'rollback_invoked', 'envelope_received']

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
        "contract":"principia-phase50-population-execution-authorization-readiness-assurance/0.1",
        "phase":50,"mode":MODE,"state":STATE,"decision":DECISION,"next_gate":NEXT,
        "fixture_kind":"bounded-synthetic","live":False,
        "live_activation_permitted":False,"real_authorization_claimed":False,
    }
    for key, value in expected_root.items():
        require(errors, document.get(key) == value, key + " drift")
    require(errors, document.get("source_phase49") == EXPECTED_SOURCE, "source binding drift")

    policy = document.get("authorization_assurance_policy")
    validate_signed(errors, policy, "policy")
    if isinstance(policy, dict):
        require(errors, policy.get("id") == "principia-phase50-population-execution-authorization-readiness-assurance-policy", "policy id drift")
        require(errors, policy.get("version") == "0.1", "policy version drift")
        require(errors, policy.get("source_candidate_sha256") == SOURCE_CANDIDATE_SHA, "policy source candidate drift")
        require(errors, policy.get("source_postmerge_sha256") == SOURCE_POSTMERGE_SHA, "policy source postmerge drift")
        require(errors, policy.get("source_finalization_commit") == SOURCE_FINALIZATION_COMMIT, "policy finalization drift")
        require(errors, policy.get("source_authorization_policy_sha256") == SOURCE_POLICY_SHA, "policy source policy drift")
        ids = policy.get("check_ids")
        require(errors, isinstance(ids, list) and len(ids) == 144, "policy check count drift")
        require(errors, isinstance(ids, list) and digest(ids) == CHECK_SET_SHA, "policy check set drift")
        expected_policy = {
            "authorization_profile_count":2,"authorization_stage_count":24,"active_authorization_stage_count":0,
            "authorization_requirement_count":64,"evaluated_authorization_requirement_count":0,
            "required_approval_role_count":6,"satisfied_approval_role_count":0,
            "blank_authorization_token_count":2,"blank_authorization_token_field_count":36,
            "population_slot_count":36,"populated_slot_count":0,"symbolic_reference_count":36,"resolved_reference_count":0,
            "population_operation_count":36,"dispatched_operation_count":0,
            "execution_stage_count":20,"active_execution_stage_count":0,
            "execution_precondition_count":48,"evaluated_precondition_count":0,
            "rollback_rule_count":36,"invoked_rollback_count":0,
            "blank_execution_ticket_count":2,"blank_execution_ticket_field_count":24,
            "human_gate_pending_count":12,"human_gate_satisfied_count":0,
            "dual_control_required":True,"role_independence_required":True,
            "local_population_execution_authorization_readiness_assurance_permitted":True,
            "authorization_request_creation_permitted":False,"approval_evaluation_permitted":False,
            "authorization_decision_recording_permitted":False,"authorization_grant_permitted":False,
            "authorization_token_issuance_permitted":False,"operation_dispatch_permitted":False,
        }
        for key, value in expected_policy.items():
            require(errors, policy.get(key) == value, "policy " + key + " drift")

    profiles = document.get("authorization_assurance_profiles")
    records = document.get("authorization_assurance_records")
    require(errors, isinstance(profiles, list) and len(profiles) == 2, "profiles drift")
    require(errors, isinstance(records, list) and len(records) == 2, "records drift")
    policy_sha = policy.get("sha256") if isinstance(policy, dict) else None
    record_shas: list[str | None] = []
    if isinstance(profiles, list) and isinstance(records, list) and len(profiles) == len(records) == 2:
        for sequence, (profile, record) in enumerate(zip(profiles, records), 1):
            validate_signed(errors, profile, f"profile {sequence}")
            validate_signed(errors, record, f"record {sequence}")
            if not isinstance(profile, dict) or not isinstance(record, dict):
                continue
            expected_profile = {
                "sequence":sequence,"source_authorization_readiness_sequence":sequence,
                "policy_sha256":policy_sha,"source_authorization_policy_sha256":SOURCE_POLICY_SHA,
                "source_authorization_profile_sha256":SOURCE_PROFILE_SHAS[sequence-1],
                "source_authorization_record_sha256":SOURCE_RECORD_SHAS[sequence-1],
                "source_ledger_head_sha256":SOURCE_LEDGER_HEAD,
                "required_roles":["population-operator","reviewer","authorization-officer"],
                "dual_control_required":True,"role_independence_required":True,
                "assurance_execution_permitted":False,"assigned_role_count":0,
            }
            for key, value in expected_profile.items():
                require(errors, profile.get(key) == value, f"profile {sequence} {key} drift")
            record_shas.append(record.get("sha256"))
            expected_record = {
                "sequence":sequence,"source_authorization_readiness_sequence":sequence,
                "policy_sha256":policy_sha,"profile_sha256":profile.get("sha256"),
                "check_set_sha256":CHECK_SET_SHA,"passed_check_count":144,"failed_check_count":0,
                "authorization_stage_count":12,"active_authorization_stage_count":0,
                "authorization_requirement_count":32,"evaluated_authorization_requirement_count":0,
                "required_approval_role_count":3,"satisfied_approval_role_count":0,"assigned_role_count":0,
                "blank_authorization_token_count":1,"blank_authorization_token_field_count":18,
                "population_slot_count":18,"populated_slot_count":0,"symbolic_reference_count":18,"resolved_reference_count":0,
                "population_operation_count":18,"dispatched_operation_count":0,
                "execution_stage_count":10,"active_execution_stage_count":0,
                "execution_precondition_count":24,"evaluated_precondition_count":0,
                "rollback_rule_count":18,"invoked_rollback_count":0,
                "blank_execution_ticket_count":1,"blank_execution_ticket_field_count":12,
                "human_gate_pending_count":6,"human_gate_satisfied_count":0,
                "reviewer_identity_count":0,"reviewer_contact_count":0,"validation_result_count":0,
                "audit_event_count":0,"status_change_count":0,"real_authorization_claimed":False,
                "local_only":True,"status":"population-execution-authorization-readiness-assured-no-grant",
                "verdict":DECISION,
            }
            for key, value in expected_record.items():
                require(errors, record.get(key) == value, f"record {sequence} {key} drift")
            for key in FALSE_RECORD_FIELDS:
                require(errors, record.get(key) is False, f"record {sequence} {key} escalated")

    ledger = document.get("ledger")
    require(errors, isinstance(ledger, dict), "ledger missing")
    previous = None
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
        "scenario_count":348,"baseline_count":1,"mutation_count":347,"rejected_mutation_count":347,
        "categories":["source-provenance","authorization-policy-integrity","authorization-profile-integrity",
        "authorization-stage-integrity","authorization-requirement-integrity","approval-role-integrity",
        "authorization-scope-integrity","validity-revocation-integrity","token-integrity","execution-boundary",
        "human-governance","authority-boundary","ledger-integrity","recovery-determinism"]}, "recovery matrix drift")
    require(errors, document.get("authority") == EXPECTED_AUTHORITY, "authority drift")
    require(errors, document.get("result") == EXPECTED_RESULT, "result drift")
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
    if post.get("state") != 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-validated':
        errors.append("source state drift")
    if post.get("next_gate") != 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-assurance-candidate':
        errors.append("source next gate drift")
    if post.get("decision") != 'response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-recorded-no-authorization-granted':
        errors.append("source decision drift")
    if post.get("candidate_record") != {"path": SOURCE_CANDIDATE.relative_to(ROOT).as_posix(), "sha256": SOURCE_CANDIDATE_SHA}:
        errors.append("source candidate binding drift")
    if post.get("principia") != {"candidate_head_commit":"baa70c6f756fd747e40b4eb52d905a26583b988c","merge_commit":"65afc6dbcd4bf73518c2703dc2f15a0a3614ed95","pull_request":90,"repository":"Rhodan-lab/principle-to-system"}:
        errors.append("source merge provenance drift")
    if post.get("validation") != {"applicable_workflows":42,"candidate_head_commit":"baa70c6f756fd747e40b4eb52d905a26583b988c","status":"success"}:
        errors.append("source validation provenance drift")
    errors.extend(validate_document(json.loads(MANIFEST.read_text(encoding="utf-8"))))
    return errors

def main() -> int:
    errors = validate_files()
    if errors:
        print("Phase 50 assurance errors:", file=sys.stderr)
        for error in errors:
            print("- " + error, file=sys.stderr)
        return 1
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print(f"Phase 50 authorization-readiness assurance passed: manifest={MANIFEST_SHA}, checks={document['result']['authorization_assurance_check_count']}, scenarios={document['recovery_matrix']['scenario_count']}.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
