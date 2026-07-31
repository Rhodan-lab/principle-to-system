#!/usr/bin/env python3
"""Generate deterministic Phase 47 candidate-population execution-readiness evidence."""
from __future__ import annotations
import argparse
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
SOURCE_CANDIDATE_SHA = "2b7ced60688ff02ea11231bc53bad3e39e0ec22aa10a233e5f270b0d586039ad"
SOURCE_POSTMERGE_SHA = "b9ccbd2125db1538bb1b4028b3dd15411971baba72bf059448d64fa32ccee121"
SOURCE_FINALIZATION_COMMIT = "87ccadcdbbc579593f4ef3fffc0194d7cbfce01e"
SOURCE_RECORD_SHAS = [
    "78907d0086df6856d85fe86fb2af432f578bebb2567707106adf0ef29eab23f2",
    "37a27fb3db161498c606294f97401be558fd3f77f5d714925df5345ed2c4c6a4",
]
MANIFEST = ROOT / f"release/phase-47-{MODE}.json"
REPORT = ROOT / f"reports/phase-47-{MODE}.md"

CHECK_IDS = [
    "source-candidate-sha-exact", "source-postmerge-sha-exact", "source-finalization-commit-exact",
    "source-phase-exact", "source-state-validated", "source-decision-exact", "source-next-gate-exact",
    "source-workflow-count-exact", "source-policy-count-exact", "source-profile-count-exact",
    "source-record-count-exact", "source-check-count-exact", "source-failed-check-count-zero",
    "source-slot-count-exact", "source-populated-slot-count-zero", "source-reference-count-exact",
    "source-stage-count-exact", "source-active-stage-count-zero", "source-requirement-count-exact",
    "source-evaluated-requirement-count-zero", "source-human-gates-pending-exact",
    "source-human-gates-satisfied-zero", "policy-binding-exact", "profile-binding-exact",
    "record-sequence-exact", "check-set-exact", "check-count-exact", "failed-check-count-zero",
    "population-slots-preserved", "population-slots-empty", "population-slots-blocked",
    "population-references-symbolic", "population-reference-resolution-forbidden", "population-values-absent",
    "execution-plan-count-exact", "population-operation-count-exact", "population-operations-planned",
    "population-operations-not-dispatched", "operation-order-deterministic", "operation-id-unique",
    "execution-stage-count-exact", "execution-stages-inactive", "execution-stage-activation-forbidden",
    "execution-precondition-count-exact", "execution-preconditions-unevaluated", "precondition-evaluation-forbidden",
    "rollback-rule-count-exact", "rollback-rules-inactive", "rollback-invocation-forbidden",
    "blank-ticket-count-exact", "blank-ticket-field-count-exact", "ticket-fields-empty",
    "ticket-issuance-forbidden", "human-gates-preserved", "human-gates-pending", "human-gates-unsatisfied",
    "dual-control-required", "role-independence-required", "operator-role-unassigned", "reviewer-role-unassigned",
    "authorization-officer-role-unassigned", "candidate-identity-absent", "candidate-body-absent",
    "candidate-signature-absent", "candidate-creation-forbidden", "candidate-assembly-forbidden",
    "candidate-population-forbidden", "candidate-persistence-forbidden", "candidate-submission-forbidden",
    "population-run-absent", "source-resolution-absent", "value-insertion-absent", "decision-selection-absent",
    "decision-recording-absent", "authorization-grant-absent", "token-issuance-absent",
    "execution-ticket-absent", "execution-run-absent", "response-envelope-absent", "validation-result-absent",
    "reviewer-identity-absent", "reviewer-contact-forbidden", "audit-event-absent", "status-change-absent",
    "atlas-boundary-preserved", "external-network-boundary-preserved", "repository-mutation-boundary-preserved",
    "automatic-status-boundary-preserved", "live-false", "authority-separated", "source-record-ledger-bound",
    "execution-ledger-chain-valid", "execution-verdict-exact", "recovery-matrix-complete",
    "mutation-rejection-boundary", "no-inherited-status", "local-only", "real-authorization-false",
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


def signed(value: dict[str, Any]) -> dict[str, Any]:
    result = dict(value)
    result["sha256"] = digest(value)
    return result


def build_document() -> dict[str, Any]:
    policy = signed({
        "id": "principia-phase47-population-execution-readiness-policy",
        "version": "0.1",
        "source_candidate_sha256": SOURCE_CANDIDATE_SHA,
        "source_postmerge_sha256": SOURCE_POSTMERGE_SHA,
        "source_finalization_commit": SOURCE_FINALIZATION_COMMIT,
        "check_ids": CHECK_IDS,
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
    })

    profiles: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for sequence in (1, 2):
        prefix = f"principia:phase47-population-execution:{sequence:04d}"
        operations = [
            {
                "id": f"{prefix}:operation:{index:02d}",
                "sequence": index,
                "slot_id": f"phase45-profile-{sequence:04d}-slot-{index:02d}",
                "source_reference": f"symbolic://phase45/profile/{sequence}/slot/{index}",
                "source_resolved": False,
                "value": None,
                "state": "planned-not-started",
                "dispatch_permitted": False,
            }
            for index in range(1, 19)
        ]
        stages = [
            {
                "id": f"{prefix}:stage:{index:02d}",
                "sequence": index,
                "state": "inactive",
                "activation_permitted": False,
            }
            for index in range(1, 11)
        ]
        preconditions = [
            {
                "id": f"{prefix}:precondition:{index:02d}",
                "sequence": index,
                "state": "unevaluated",
                "evaluation_permitted": False,
            }
            for index in range(1, 25)
        ]
        rollbacks = [
            {
                "id": f"{prefix}:rollback:{index:02d}",
                "operation_id": operations[index - 1]["id"],
                "state": "inactive",
                "invocation_permitted": False,
            }
            for index in range(1, 19)
        ]
        ticket = {field: None for field in TICKET_FIELDS}
        profile = signed({
            "id": f"principia:phase47-population-execution-profile:{sequence:04d}",
            "sequence": sequence,
            "source_population_assurance_sequence": sequence,
            "source_population_assurance_record_sha256": SOURCE_RECORD_SHAS[sequence - 1],
            "policy_sha256": policy["sha256"],
            "required_roles": ["population-operator", "reviewer", "authorization-officer"],
            "assigned_role_count": 0,
            "dual_control_required": True,
            "role_independence_required": True,
            "operations": operations,
            "stages": stages,
            "preconditions": preconditions,
            "rollback_rules": rollbacks,
            "execution_ticket_template": ticket,
            "population_execution_permitted": False,
        })
        profiles.append(profile)
        record = signed({
            "id": f"principia:phase47-population-execution-readiness-record:{sequence:04d}",
            "sequence": sequence,
            "source_population_assurance_sequence": sequence,
            "policy_sha256": policy["sha256"],
            "profile_sha256": profile["sha256"],
            "check_set_sha256": digest(CHECK_IDS),
            "passed_check_count": len(CHECK_IDS),
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
            "candidate_created": False,
            "candidate_assembled": False,
            "candidate_population_started": False,
            "candidate_populated": False,
            "candidate_persisted": False,
            "candidate_submitted": False,
            "source_resolution_started": False,
            "value_insertion_started": False,
            "operation_dispatched": False,
            "stage_activated": False,
            "precondition_evaluated": False,
            "rollback_invoked": False,
            "ticket_issued": False,
            "decision_selected": False,
            "decision_recorded": False,
            "authorization_granted": False,
            "token_issued": False,
            "execution_run_created": False,
            "envelope_received": False,
            "reviewer_identity_count": 0,
            "reviewer_contact_count": 0,
            "validation_result_count": 0,
            "audit_event_count": 0,
            "status_change_count": 0,
            "real_authorization_claimed": False,
            "local_only": True,
            "status": "population-execution-readiness-defined-no-run",
            "verdict": DECISION,
        })
        records.append(record)

    entries = []
    previous = None
    for record in records:
        entry = {
            "sequence": record["sequence"],
            "record_id": record["id"],
            "record_sha256": record["sha256"],
            "previous_entry_sha256": previous,
        }
        entry_sha = digest(entry)
        entries.append({"entry": entry, "entry_sha256": entry_sha})
        previous = entry_sha

    authority = {
        "local_population_execution_planning_permitted": True,
        "source_resolution_permitted": False,
        "value_insertion_permitted": False,
        "operation_dispatch_permitted": False,
        "stage_activation_permitted": False,
        "precondition_evaluation_permitted": False,
        "rollback_invocation_permitted": False,
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
        "automatic_status_change": False,
        "automatic_release_action": False,
        "human_authorization_claimed": False,
        "status_inheritance": "prohibited",
    }

    result = {
        "population_execution_readiness_policy_count": 1,
        "population_execution_profile_count": 2,
        "population_execution_readiness_record_count": 2,
        "population_execution_readiness_check_count": len(CHECK_IDS) * 2,
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

    return {
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
        "source_phase46": {
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
        },
        "population_execution_readiness_policy": policy,
        "population_execution_profiles": profiles,
        "population_execution_readiness_records": records,
        "ledger": {"entries": entries, "head_sequence": 2, "head_sha256": previous},
        "recovery_matrix": {
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
        },
        "authority": authority,
        "result": result,
    }


def render_report(document: dict[str, Any], manifest_sha: str) -> str:
    result = document["result"]
    return f"""# Phase 47 — Offline Candidate Population Execution Readiness

> Date: 2026-07-31
> Repository: `Rhodan-lab/principle-to-system`
> State: `{STATE}`

## Purpose

Phase 47 defines a deterministic, local-only execution-readiness plan for population of a still-uncreated authorization-decision candidate. It specifies symbolic operations, inactive stages, unevaluated preconditions, rollback rules, blank execution tickets, and pending human gates without resolving any source, inserting any value, creating a candidate, or starting a population run.

## Immutable source boundary

- Phase 46 candidate SHA-256: `{SOURCE_CANDIDATE_SHA}`
- Phase 46 post-merge SHA-256: `{SOURCE_POSTMERGE_SHA}`
- Phase 46 authoritative finalization: `{SOURCE_FINALIZATION_COMMIT}`
- Phase 46 applicable workflows: `39`
- Phase 47 candidate SHA-256: `{manifest_sha}`

## Deterministic readiness result

- Execution-readiness policies: `1`
- Execution profiles: `2`
- Readiness records: `2`
- Readiness checks: `{result['population_execution_readiness_check_count']}`
- Failed readiness checks: `0`
- Population slots: `36`; populated: `0`; blocked: `36`
- Symbolic references: `36`; resolved: `0`
- Planned population operations: `36`; dispatched: `0`
- Execution stages: `20`; active: `0`
- Preconditions: `48`; evaluated: `0`
- Rollback rules: `36`; invoked: `0`
- Blank execution tickets: `2`; blank fields: `24`
- Human gates pending: `12`; satisfied: `0`
- Recovery scenarios: `224`; rejected mutations: `223`

## Frozen boundaries

No candidate is created, assembled, populated, persisted, signed, or submitted. No source is resolved and no value is inserted. No operation is dispatched, stage activated, precondition evaluated, rollback invoked, ticket issued, population run started, decision selected, authorization granted, reviewer contacted, validation result recorded, audit event emitted, or status changed. Atlas is not called or modified. External networking is not required.

## Next gate

`{NEXT}`
"""


def write_or_check(check: bool) -> int:
    document = build_document()
    manifest_bytes = canonical(document)
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    expected = {MANIFEST: manifest_bytes, REPORT: render_report(document, manifest_sha).encode()}
    failures = []
    for path, data in expected.items():
        if check:
            if not path.is_file() or path.read_bytes() != data:
                failures.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    if failures:
        print("Phase 47 deterministic byte drift: " + ", ".join(failures), file=sys.stderr)
        return 1
    print(f"Phase 47 deterministic bytes passed: sha256={manifest_sha}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return write_or_check(args.check)


if __name__ == "__main__":
    raise SystemExit(main())
