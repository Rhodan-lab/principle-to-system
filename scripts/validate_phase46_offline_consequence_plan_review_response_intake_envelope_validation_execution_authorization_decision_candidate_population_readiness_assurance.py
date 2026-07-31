#!/usr/bin/env python3
"""Independently validate Phase 46 population-readiness assurance."""
from __future__ import annotations
import copy, hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'release/phase-46-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance.json'
SOURCE_CANDIDATE = ROOT / 'release/phase-45-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness.json'
SOURCE_POSTMERGE = ROOT / 'release/phase-45-postmerge.json'
MANIFEST_SHA = '2b7ced60688ff02ea11231bc53bad3e39e0ec22aa10a233e5f270b0d586039ad'
SOURCE_CANDIDATE_SHA = '3fa7ce42cce65231c394f27f248e68ce40799ba9a5ccf183923c59fa9da851d6'
SOURCE_POSTMERGE_SHA = '74a75833b867fa1db0bad3651e2131d0cbc0f9cacff9fa27f5f9498f11810ac1'
SOURCE_FINALIZATION_COMMIT = '76ad08f04fc1452c0359da40702cd4e86764467a'
MODE = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance'
STATE = MODE + '-candidate'
DECISION = 'response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assured-no-candidate-populated'
NEXT = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-candidate'
CHECK_SET_SHA = '3b58dcc26f7213833c94d67b36d3d26d2526c79d959167d1e872f121b2c9214a'


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
    require(errors, isinstance(value, dict), label + ' missing')
    if isinstance(value, dict):
        unsigned = copy.deepcopy(value)
        actual = unsigned.pop('sha256', None)
        require(errors, actual == digest(unsigned), label + ' digest drift')


def validate_document(document: Any) -> list[str]:
    errors: list[str] = []
    require(errors, isinstance(document, dict), 'manifest must be object')
    if not isinstance(document, dict):
        return errors
    expected_root = {
        'contract': 'principia-phase46-population-readiness-assurance/0.1',
        'phase': 46, 'mode': MODE, 'state': STATE, 'decision': DECISION, 'next_gate': NEXT,
        'fixture_kind': 'bounded-synthetic', 'live': False,
        'live_activation_permitted': False, 'real_authorization_claimed': False,
    }
    for key, value in expected_root.items():
        require(errors, document.get(key) == value, key + ' drift')
    source = document.get('source_phase45')
    expected_source = {
        'candidate_sha256': SOURCE_CANDIDATE_SHA,
        'postmerge_sha256': SOURCE_POSTMERGE_SHA,
        'authoritative_finalization_commit': SOURCE_FINALIZATION_COMMIT,
        'state': 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-validated',
        'decision': 'response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-defined-no-candidate-populated',
        'next_gate': MODE + '-candidate', 'applicable_workflows': 38,
        'population_readiness_policy_count': 1, 'population_readiness_profile_count': 2,
        'population_readiness_record_count': 2, 'population_check_count': 144,
        'failed_population_check_count': 0, 'population_slot_count': 36,
        'populated_slot_count': 0, 'population_stage_count': 36, 'active_stage_count': 0,
        'population_requirement_count': 72, 'evaluated_requirement_count': 0,
        'human_gate_pending_count': 10, 'human_gate_satisfied_count': 0,
    }
    require(errors, source == expected_source, 'source binding drift')
    policy = document.get('population_assurance_policy')
    validate_signed(errors, policy, 'policy')
    if isinstance(policy, dict):
        require(errors, policy.get('id') == 'principia-phase46-population-readiness-assurance-policy', 'policy id drift')
        require(errors, policy.get('version') == '0.1', 'policy version drift')
        require(errors, policy.get('source_candidate_sha256') == SOURCE_CANDIDATE_SHA, 'policy source candidate drift')
        require(errors, policy.get('source_postmerge_sha256') == SOURCE_POSTMERGE_SHA, 'policy source postmerge drift')
        require(errors, policy.get('source_finalization_commit') == SOURCE_FINALIZATION_COMMIT, 'policy finalization drift')
        check_ids = policy.get('check_ids')
        require(errors, isinstance(check_ids, list) and len(check_ids) == 80, 'policy check count drift')
        require(errors, isinstance(check_ids, list) and digest(check_ids) == CHECK_SET_SHA, 'policy check set drift')
        for key, value in {
            'population_slot_count':36,'populated_slot_count':0,'blocked_slot_count':36,
            'symbolic_reference_count':36,'population_stage_count':36,'active_stage_count':0,
            'population_requirement_count':72,'evaluated_requirement_count':0,
            'human_gate_pending_count':10,'human_gate_satisfied_count':0,
            'dual_control_required':True,'role_independence_required':True,
            'local_population_readiness_assurance_permitted':True,
            'candidate_creation_permitted':False,'candidate_assembly_permitted':False,
            'candidate_population_permitted':False,'candidate_persistence_permitted':False,
            'candidate_submission_permitted':False,
        }.items():
            require(errors, policy.get(key) == value, 'policy ' + key + ' drift')
    profiles = document.get('population_assurance_profiles')
    records = document.get('population_assurance_records')
    require(errors, isinstance(profiles, list) and len(profiles) == 2, 'profiles drift')
    require(errors, isinstance(records, list) and len(records) == 2, 'records drift')
    policy_sha = policy.get('sha256') if isinstance(policy, dict) else None
    record_shas: list[str | None] = []
    if isinstance(profiles, list) and isinstance(records, list) and len(profiles) == len(records) == 2:
        for sequence, (profile, record) in enumerate(zip(profiles, records), 1):
            validate_signed(errors, profile, f'profile {sequence}')
            validate_signed(errors, record, f'record {sequence}')
            if not isinstance(profile, dict) or not isinstance(record, dict):
                continue
            require(errors, profile.get('sequence') == sequence, f'profile {sequence} sequence drift')
            require(errors, profile.get('source_population_readiness_sequence') == sequence, f'profile {sequence} source drift')
            require(errors, profile.get('policy_sha256') == policy_sha, f'profile {sequence} policy drift')
            require(errors, profile.get('required_roles') == ['reviewer','authorization-officer'], f'profile {sequence} roles drift')
            require(errors, profile.get('dual_control_required') is True, f'profile {sequence} dual control drift')
            require(errors, profile.get('role_independence_required') is True, f'profile {sequence} independence drift')
            require(errors, profile.get('assurance_execution_permitted') is False, f'profile {sequence} execution escalated')
            record_shas.append(record.get('sha256'))
            expected = {
                'sequence':sequence,'source_population_readiness_sequence':sequence,
                'policy_sha256':policy_sha,'profile_sha256':profile.get('sha256'),
                'check_set_sha256':CHECK_SET_SHA,'passed_check_count':80,'failed_check_count':0,
                'population_slot_count':18,'populated_slot_count':0,'blocked_slot_count':18,
                'symbolic_reference_count':18,'population_stage_count':18,'active_stage_count':0,
                'population_requirement_count':36,'evaluated_requirement_count':0,
                'human_gate_pending_count':5,'human_gate_satisfied_count':0,
                'reviewer_identity_count':0,'reviewer_contact_count':0,'validation_result_count':0,
                'audit_event_count':0,'status_change_count':0,'real_authorization_claimed':False,
                'local_only':True,'status':'population-readiness-assured-no-candidate','verdict':DECISION,
            }
            for key, value in expected.items():
                require(errors, record.get(key) == value, f'record {sequence} {key} drift')
            for key in ('candidate_created','candidate_assembled','candidate_population_started','candidate_populated',
                        'candidate_persisted','candidate_submitted','decision_selected','decision_recorded',
                        'authorization_granted','token_issued','ticket_issued','execution_run_created','envelope_received'):
                require(errors, record.get(key) is False, f'record {sequence} {key} escalated')
    ledger = document.get('ledger')
    previous = None
    require(errors, isinstance(ledger, dict), 'ledger missing')
    if isinstance(ledger, dict):
        entries = ledger.get('entries')
        require(errors, isinstance(entries, list) and len(entries) == 2, 'ledger entries drift')
        if isinstance(entries, list) and len(record_shas) == 2:
            for sequence, wrapped in enumerate(entries, 1):
                entry = wrapped.get('entry') if isinstance(wrapped, dict) else None
                require(errors, isinstance(entry, dict), f'ledger entry {sequence} missing')
                if isinstance(entry, dict):
                    require(errors, entry.get('sequence') == sequence, f'ledger entry {sequence} sequence drift')
                    require(errors, entry.get('record_sha256') == record_shas[sequence-1], f'ledger entry {sequence} record drift')
                    require(errors, entry.get('previous_entry_sha256') == previous, f'ledger entry {sequence} chain drift')
                    previous = digest(entry)
                    require(errors, wrapped.get('entry_sha256') == previous, f'ledger entry {sequence} digest drift')
        require(errors, ledger.get('head_sequence') == 2, 'ledger head sequence drift')
        require(errors, ledger.get('head_sha256') == previous, 'ledger head digest drift')
    require(errors, document.get('recovery_matrix') == {
        'scenario_count':198,'baseline_count':1,'mutation_count':197,'rejected_mutation_count':197,
        'categories':['source-provenance','population-slot-integrity','population-stage-integrity',
                      'population-requirement-integrity','human-governance','authority-boundary',
                      'ledger-integrity','recovery-determinism']}, 'recovery matrix drift')
    authority = document.get('authority')
    require(errors, isinstance(authority, dict), 'authority missing')
    if isinstance(authority, dict):
        require(errors, authority.get('local_population_readiness_assurance_permitted') is True, 'local assurance disabled')
        require(errors, authority.get('status_inheritance') == 'prohibited', 'status inheritance drift')
        for key in ('candidate_creation_permitted','candidate_assembly_permitted','candidate_population_permitted',
                    'candidate_persistence_permitted','candidate_submission_permitted','decision_selection_permitted',
                    'decision_recording_permitted','authorization_grant_permitted','token_issuance_permitted',
                    'execution_ticket_issuance_permitted','validation_execution_permitted','reviewer_contact_permitted',
                    'atlas_call_permitted','external_network_required','repository_mutation','automatic_status_change',
                    'automatic_release_action','human_authorization_claimed'):
            require(errors, authority.get(key) is False, 'authority ' + key + ' escalated')
    require(errors, document.get('result') == {
        'population_assurance_policy_count':1,'population_assurance_profile_count':2,
        'population_assurance_record_count':2,'population_assurance_check_count':160,
        'failed_population_assurance_check_count':0,'source_population_check_count':144,
        'source_failed_population_check_count':0,'population_slot_count':36,'populated_slot_count':0,
        'blocked_slot_count':36,'symbolic_reference_count':36,'population_stage_count':36,
        'active_stage_count':0,'population_requirement_count':72,'evaluated_requirement_count':0,
        'human_gate_pending_count':10,'human_gate_satisfied_count':0,'candidate_count':0,
        'candidate_population_run_count':0,'decision_count':0,'grant_count':0,'token_count':0,
        'ticket_count':0,'execution_run_count':0,'envelope_count':0,'reviewer_identity_count':0,
        'reviewer_contact_count':0,'validation_result_count':0,'audit_event_count':0,
        'status_change_count':0,'real_authorization_claimed':False}, 'result drift')
    return errors


def validate_files() -> list[str]:
    errors: list[str] = []
    for path, label in ((MANIFEST,'manifest'),(SOURCE_CANDIDATE,'source candidate'),(SOURCE_POSTMERGE,'source postmerge')):
        if not path.is_file():
            errors.append(label + ' missing')
    if errors:
        return errors
    if file_digest(MANIFEST) != MANIFEST_SHA: errors.append('manifest digest drift')
    if file_digest(SOURCE_CANDIDATE) != SOURCE_CANDIDATE_SHA: errors.append('source candidate digest drift')
    if file_digest(SOURCE_POSTMERGE) != SOURCE_POSTMERGE_SHA: errors.append('source postmerge digest drift')
    post = json.loads(SOURCE_POSTMERGE.read_text(encoding='utf-8'))
    if post.get('state') != 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-validated': errors.append('source state drift')
    if post.get('next_gate') != MODE + '-candidate': errors.append('source next gate drift')
    if post.get('validation') != {'applicable_workflows':38,'candidate_head_commit':'74b8522b71d2963dbbfa6923b5fe41cb10b1bfcc','status':'success'}: errors.append('source validation drift')
    errors.extend(validate_document(json.loads(MANIFEST.read_text(encoding='utf-8'))))
    return errors


def main() -> int:
    errors = validate_files()
    if errors:
        print('Phase 46 assurance errors:', file=sys.stderr)
        for error in errors:
            print('- ' + error, file=sys.stderr)
        return 1
    document = json.loads(MANIFEST.read_text(encoding='utf-8'))
    print(f"Phase 46 population-readiness assurance passed: manifest={MANIFEST_SHA}, checks={document['result']['population_assurance_check_count']}, scenarios={document['recovery_matrix']['scenario_count']}.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
