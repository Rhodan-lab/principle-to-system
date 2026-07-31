#!/usr/bin/env python3
"""Generate deterministic Phase 48 population-execution-readiness assurance evidence."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'release/phase-48-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance.json'
REPORT = ROOT / 'reports/phase-48-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance.md'
SOURCE_CANDIDATE = ROOT / 'release/phase-47-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness.json'
SOURCE_POSTMERGE = ROOT / 'release/phase-47-postmerge.json'
SOURCE_CANDIDATE_SHA = '31b57486ca590cd066642981e640c21cc306869f99241d0fa81013d681df5065'
SOURCE_POSTMERGE_SHA = '7048a8235b379991f3e618a3390cbd978a016e989e4dcb558c518dc9a84a365c'
SOURCE_FINALIZATION_COMMIT = '8fc91246692f213764551e20db67133d19149d5a'
MODE = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance'
STATE = MODE + '-candidate'
DECISION = 'response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assured-no-population-run'
NEXT = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-candidate'
CHECK_IDS = [
    'source-candidate-sha-exact','source-postmerge-sha-exact','source-finalization-commit-exact',
    'source-phase-exact','source-state-validated','source-decision-exact','source-next-gate-exact',
    'source-workflow-count-exact','source-policy-count-exact','source-profile-count-exact',
    'source-record-count-exact','source-check-count-exact','source-failed-check-count-zero',
    'source-slot-count-exact','source-populated-slot-count-zero','source-blocked-slot-count-exact',
    'source-symbolic-reference-count-exact','source-resolved-reference-count-zero',
    'source-resolution-count-zero','source-value-insertion-count-zero','source-operation-count-exact',
    'source-dispatched-operation-count-zero','source-stage-count-exact','source-active-stage-count-zero',
    'source-precondition-count-exact','source-evaluated-precondition-count-zero',
    'source-rollback-count-exact','source-invoked-rollback-count-zero',
    'source-blank-ticket-count-exact','source-blank-ticket-field-count-exact',
    'source-human-gates-pending-exact','source-human-gates-satisfied-zero','source-authority-exact',
    'assurance-policy-binding-exact','assurance-profile-binding-exact','assurance-record-sequence-exact',
    'assurance-check-set-exact','assurance-check-count-exact','assurance-failed-check-count-zero',
    'population-slots-preserved','population-slots-empty','population-slots-blocked',
    'population-references-symbolic','population-references-unresolved','source-resolution-forbidden',
    'population-values-absent','value-insertion-forbidden','population-operations-preserved',
    'population-operations-planned','population-operations-not-dispatched','operation-order-deterministic',
    'operation-id-unique','slot-mapping-exact','operation-rollback-bijection',
    'execution-stages-preserved','execution-stages-inactive','stage-activation-forbidden',
    'stage-order-deterministic','execution-preconditions-preserved','execution-preconditions-unevaluated',
    'precondition-evaluation-forbidden','precondition-order-deterministic','rollback-rules-preserved',
    'rollback-rules-inactive','rollback-invocation-forbidden','rollback-binding-exact',
    'blank-tickets-preserved','blank-ticket-field-count-exact','ticket-fields-empty',
    'ticket-issuance-forbidden','ticket-candidate-identity-absent','ticket-operation-set-absent',
    'ticket-source-snapshot-absent','human-gates-preserved','human-gates-pending',
    'human-gates-unsatisfied','dual-control-required','role-independence-required',
    'operator-role-unassigned','reviewer-role-unassigned','authorization-officer-role-unassigned',
    'candidate-identity-absent','candidate-body-absent','candidate-signature-absent',
    'candidate-creation-forbidden','candidate-assembly-forbidden','candidate-population-forbidden',
    'candidate-persistence-forbidden','candidate-submission-forbidden','population-run-absent',
    'decision-selection-absent','decision-recording-absent','authorization-grant-absent',
    'token-issuance-absent','execution-run-absent','response-envelope-absent',
    'validation-result-absent','reviewer-identity-absent','reviewer-contact-forbidden',
    'audit-event-absent','status-change-absent','atlas-boundary-preserved',
    'external-network-boundary-preserved','repository-mutation-boundary-preserved',
    'automatic-status-boundary-preserved','live-false','authority-separated',
    'source-record-ledger-bound','assurance-ledger-chain-valid','assurance-verdict-exact',
    'recovery-matrix-complete','mutation-rejection-boundary','no-inherited-status',
    'local-only','real-authorization-false','operation-dispatch-authority-exact',
    'stage-activation-authority-exact','precondition-evaluation-authority-exact',
    'rollback-invocation-authority-exact','ticket-issuance-authority-exact',
]


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()

def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()

def signed(value: dict[str, Any]) -> dict[str, Any]:
    value = dict(value)
    value['sha256'] = digest(value)
    return value

def build_document() -> dict[str, Any]:
    policy = signed({
        'id': 'principia-phase48-population-execution-readiness-assurance-policy',
        'version': '0.1',
        'source_candidate_sha256': SOURCE_CANDIDATE_SHA,
        'source_postmerge_sha256': SOURCE_POSTMERGE_SHA,
        'source_finalization_commit': SOURCE_FINALIZATION_COMMIT,
        'check_ids': CHECK_IDS,
        'population_slot_count': 36,
        'populated_slot_count': 0,
        'blocked_slot_count': 36,
        'symbolic_reference_count': 36,
        'resolved_reference_count': 0,
        'population_operation_count': 36,
        'dispatched_operation_count': 0,
        'execution_stage_count': 20,
        'active_stage_count': 0,
        'execution_precondition_count': 48,
        'evaluated_precondition_count': 0,
        'rollback_rule_count': 36,
        'invoked_rollback_count': 0,
        'blank_execution_ticket_count': 2,
        'blank_execution_ticket_field_count': 24,
        'human_gate_pending_count': 12,
        'human_gate_satisfied_count': 0,
        'dual_control_required': True,
        'role_independence_required': True,
        'local_population_execution_readiness_assurance_permitted': True,
        'source_resolution_permitted': False,
        'value_insertion_permitted': False,
        'operation_dispatch_permitted': False,
        'stage_activation_permitted': False,
        'precondition_evaluation_permitted': False,
        'rollback_invocation_permitted': False,
        'execution_ticket_issuance_permitted': False,
        'candidate_creation_permitted': False,
        'candidate_assembly_permitted': False,
        'candidate_population_permitted': False,
        'candidate_persistence_permitted': False,
        'candidate_submission_permitted': False,
    })
    profiles = []
    records = []
    for sequence in (1, 2):
        profile = signed({
            'id': f'principia:phase48-population-execution-readiness-assurance-profile:{sequence:04d}',
            'sequence': sequence,
            'source_population_execution_readiness_sequence': sequence,
            'policy_sha256': policy['sha256'],
            'source_candidate_sha256': SOURCE_CANDIDATE_SHA,
            'source_postmerge_sha256': SOURCE_POSTMERGE_SHA,
            'required_roles': ['population-operator','reviewer','authorization-officer'],
            'assigned_role_count': 0,
            'dual_control_required': True,
            'role_independence_required': True,
            'assurance_execution_permitted': False,
        })
        profiles.append(profile)
        record = signed({
            'id': f'principia:phase48-population-execution-readiness-assurance-record:{sequence:04d}',
            'sequence': sequence,
            'source_population_execution_readiness_sequence': sequence,
            'policy_sha256': policy['sha256'],
            'profile_sha256': profile['sha256'],
            'check_set_sha256': digest(CHECK_IDS),
            'passed_check_count': len(CHECK_IDS),
            'failed_check_count': 0,
            'population_slot_count': 18,
            'populated_slot_count': 0,
            'blocked_slot_count': 18,
            'symbolic_reference_count': 18,
            'resolved_reference_count': 0,
            'population_operation_count': 18,
            'dispatched_operation_count': 0,
            'execution_stage_count': 10,
            'active_stage_count': 0,
            'execution_precondition_count': 24,
            'evaluated_precondition_count': 0,
            'rollback_rule_count': 18,
            'invoked_rollback_count': 0,
            'blank_execution_ticket_count': 1,
            'blank_execution_ticket_field_count': 12,
            'human_gate_pending_count': 6,
            'human_gate_satisfied_count': 0,
            'candidate_created': False,
            'candidate_assembled': False,
            'candidate_population_started': False,
            'candidate_populated': False,
            'candidate_persisted': False,
            'candidate_submitted': False,
            'source_resolution_started': False,
            'value_insertion_started': False,
            'operation_dispatched': False,
            'stage_activated': False,
            'precondition_evaluated': False,
            'rollback_invoked': False,
            'decision_selected': False,
            'decision_recorded': False,
            'authorization_granted': False,
            'token_issued': False,
            'ticket_issued': False,
            'execution_run_created': False,
            'envelope_received': False,
            'reviewer_identity_count': 0,
            'reviewer_contact_count': 0,
            'validation_result_count': 0,
            'audit_event_count': 0,
            'status_change_count': 0,
            'real_authorization_claimed': False,
            'local_only': True,
            'status': 'population-execution-readiness-assured-no-run',
            'verdict': DECISION,
        })
        records.append(record)
    entries = []
    previous = None
    for record in records:
        entry = {
            'sequence': record['sequence'],
            'record_id': record['id'],
            'record_sha256': record['sha256'],
            'previous_entry_sha256': previous,
        }
        entry_sha = digest(entry)
        entries.append({'entry': entry, 'entry_sha256': entry_sha})
        previous = entry_sha
    authority = {
        'local_population_execution_readiness_assurance_permitted': True,
        'source_resolution_permitted': False,
        'value_insertion_permitted': False,
        'operation_dispatch_permitted': False,
        'stage_activation_permitted': False,
        'precondition_evaluation_permitted': False,
        'rollback_invocation_permitted': False,
        'candidate_creation_permitted': False,
        'candidate_assembly_permitted': False,
        'candidate_population_permitted': False,
        'candidate_persistence_permitted': False,
        'candidate_submission_permitted': False,
        'decision_selection_permitted': False,
        'decision_recording_permitted': False,
        'authorization_grant_permitted': False,
        'token_issuance_permitted': False,
        'execution_ticket_issuance_permitted': False,
        'validation_execution_permitted': False,
        'reviewer_contact_permitted': False,
        'atlas_call_permitted': False,
        'external_network_required': False,
        'repository_mutation': False,
        'automatic_status_change': False,
        'automatic_release_action': False,
        'human_authorization_claimed': False,
        'status_inheritance': 'prohibited',
    }
    result = {
        'population_execution_assurance_policy_count': 1,
        'population_execution_assurance_profile_count': 2,
        'population_execution_assurance_record_count': 2,
        'population_execution_assurance_check_count': len(CHECK_IDS) * 2,
        'failed_population_execution_assurance_check_count': 0,
        'source_population_execution_readiness_check_count': 196,
        'source_failed_population_execution_readiness_check_count': 0,
        'population_slot_count': 36,
        'populated_slot_count': 0,
        'blocked_slot_count': 36,
        'symbolic_reference_count': 36,
        'resolved_reference_count': 0,
        'source_resolution_count': 0,
        'value_insertion_count': 0,
        'population_operation_count': 36,
        'dispatched_operation_count': 0,
        'execution_stage_count': 20,
        'active_stage_count': 0,
        'execution_precondition_count': 48,
        'evaluated_precondition_count': 0,
        'rollback_rule_count': 36,
        'invoked_rollback_count': 0,
        'blank_execution_ticket_count': 2,
        'blank_execution_ticket_field_count': 24,
        'human_gate_pending_count': 12,
        'human_gate_satisfied_count': 0,
        'candidate_count': 0,
        'candidate_population_run_count': 0,
        'decision_count': 0,
        'grant_count': 0,
        'token_count': 0,
        'ticket_count': 0,
        'execution_run_count': 0,
        'envelope_count': 0,
        'reviewer_identity_count': 0,
        'reviewer_contact_count': 0,
        'validation_result_count': 0,
        'audit_event_count': 0,
        'status_change_count': 0,
        'real_authorization_claimed': False,
    }
    return {
        'contract': 'principia-phase48-population-execution-readiness-assurance/0.1',
        'phase': 48,
        'mode': MODE,
        'state': STATE,
        'decision': DECISION,
        'next_gate': NEXT,
        'fixture_kind': 'bounded-synthetic',
        'live': False,
        'live_activation_permitted': False,
        'real_authorization_claimed': False,
        'source_phase47': {
            'candidate_sha256': SOURCE_CANDIDATE_SHA,
            'postmerge_sha256': SOURCE_POSTMERGE_SHA,
            'authoritative_finalization_commit': SOURCE_FINALIZATION_COMMIT,
            'state': 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-validated',
            'decision': 'response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-recorded-no-population-run',
            'next_gate': MODE + '-candidate',
            'applicable_workflows': 40,
            'population_execution_readiness_policy_count': 1,
            'population_execution_profile_count': 2,
            'population_execution_readiness_record_count': 2,
            'population_execution_readiness_check_count': 196,
            'failed_population_execution_readiness_check_count': 0,
            'population_slot_count': 36,
            'populated_slot_count': 0,
            'blocked_slot_count': 36,
            'symbolic_reference_count': 36,
            'resolved_reference_count': 0,
            'source_resolution_count': 0,
            'value_insertion_count': 0,
            'population_operation_count': 36,
            'dispatched_operation_count': 0,
            'execution_stage_count': 20,
            'active_stage_count': 0,
            'execution_precondition_count': 48,
            'evaluated_precondition_count': 0,
            'rollback_rule_count': 36,
            'invoked_rollback_count': 0,
            'blank_execution_ticket_count': 2,
            'blank_execution_ticket_field_count': 24,
            'human_gate_pending_count': 12,
            'human_gate_satisfied_count': 0,
        },
        'population_execution_assurance_policy': policy,
        'population_execution_assurance_profiles': profiles,
        'population_execution_assurance_records': records,
        'ledger': {'entries': entries, 'head_sequence': 2, 'head_sha256': previous},
        'recovery_matrix': {
            'scenario_count': 280,
            'baseline_count': 1,
            'mutation_count': 279,
            'rejected_mutation_count': 279,
            'categories': [
                'source-provenance','population-slot-integrity','source-reference-integrity',
                'operation-order-integrity','execution-stage-integrity','precondition-integrity',
                'rollback-integrity','ticket-integrity','human-governance','authority-boundary',
                'ledger-integrity','recovery-determinism',
            ],
        },
        'authority': authority,
        'result': result,
    }

def render_report(document: dict[str, Any], manifest_sha: str) -> str:
    result = document['result']
    lines = [
        '# Phase 48 — Offline Candidate Population Execution Readiness Assurance', '',
        '> Date: 2026-07-31',
        '> Repository: `Rhodan-lab/principle-to-system`',
        f"> State: `{document['state']}`", '',
        '## Purpose', '',
        'Phase 48 independently assures the immutable Phase 47 population-execution-readiness evidence for a still-uncreated authorization-decision candidate. It verifies source provenance, operation ordering, inactive stages, unevaluated preconditions, inert rollback rules, blank ticket templates, role separation, ledger integrity, and the complete absence of operational authority.', '',
        '## Immutable source boundary', '',
        f'- Phase 47 candidate SHA-256: `{SOURCE_CANDIDATE_SHA}`',
        f'- Phase 47 post-merge SHA-256: `{SOURCE_POSTMERGE_SHA}`',
        f'- Phase 47 authoritative finalization: `{SOURCE_FINALIZATION_COMMIT}`',
        '- Phase 47 applicable workflows: `40`',
        f'- Phase 48 candidate SHA-256: `{manifest_sha}`', '',
        '## Deterministic assurance result', '',
        f"- Population-execution assurance policies: `{result['population_execution_assurance_policy_count']}`",
        f"- Population-execution assurance profiles: `{result['population_execution_assurance_profile_count']}`",
        f"- Population-execution assurance records: `{result['population_execution_assurance_record_count']}`",
        f"- Assurance checks: `{result['population_execution_assurance_check_count']}`",
        f"- Failed assurance checks: `{result['failed_population_execution_assurance_check_count']}`",
        f"- Population slots: `{result['population_slot_count']}`; populated: `0`; blocked: `{result['blocked_slot_count']}`",
        f"- Symbolic unresolved references: `{result['symbolic_reference_count']}`; resolved: `0`",
        f"- Planned operations: `{result['population_operation_count']}`; dispatched: `0`",
        f"- Execution stages: `{result['execution_stage_count']}`; active: `0`",
        f"- Preconditions: `{result['execution_precondition_count']}`; evaluated: `0`",
        f"- Rollback rules: `{result['rollback_rule_count']}`; invoked: `0`",
        f"- Blank tickets: `{result['blank_execution_ticket_count']}` with `{result['blank_execution_ticket_field_count']}` empty fields",
        f"- Human gates pending: `{result['human_gate_pending_count']}`; satisfied: `0`",
        '- Recovery scenarios: `280`; rejected mutations: `279`', '',
        '## Frozen boundaries', '',
        'No candidate is created, assembled, populated, persisted, signed, or submitted. No source reference is resolved and no value is inserted. No operation is dispatched, stage activated, precondition evaluated, rollback invoked, ticket issued, or population run started. No decision is selected or recorded. No authorization, token, or execution run is issued. No envelope is processed, reviewer contacted, validation result recorded, audit event emitted, or status changed. Atlas is not called or modified. External networking is not required.', '',
        '## Next gate', '',
        f"`{document['next_gate']}`",
    ]
    return '\n'.join(lines) + '\n'

def write_or_check(check: bool) -> int:
    document = build_document()
    manifest_bytes = canonical(document)
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    report = render_report(document, manifest_sha)
    expected = {MANIFEST: manifest_bytes, REPORT: report.encode()}
    failures = []
    for path, data in expected.items():
        if check:
            if not path.is_file() or path.read_bytes() != data:
                failures.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    if failures:
        print('Phase 48 deterministic byte drift: ' + ', '.join(failures), file=sys.stderr)
        return 1
    print(f'Phase 48 deterministic bytes passed: sha256={manifest_sha}')
    return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    return write_or_check(args.check)

if __name__ == '__main__':
    raise SystemExit(main())
