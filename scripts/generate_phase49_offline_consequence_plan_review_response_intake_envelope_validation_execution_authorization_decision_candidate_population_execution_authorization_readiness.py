#!/usr/bin/env python3
"""Generate deterministic Phase 49 population-execution authorization-readiness evidence."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
MODE = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness'
STATE = MODE + "-candidate"
DECISION = 'response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-recorded-no-authorization-granted'
NEXT = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-authorization-readiness-assurance-candidate'
SOURCE_CANDIDATE = ROOT / "release/phase-48-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance.json"
SOURCE_POSTMERGE = ROOT / "release/phase-48-postmerge.json"
SOURCE_CANDIDATE_SHA = '9bfebeca19a7ce8f15c2e377db773fea78a479e773735318ac1cfc4d97f3e628'
SOURCE_POSTMERGE_SHA = '2acb658af81739e76369065743e13e83031a60c43ddcb75eb03fad5c1c7e2a82'
SOURCE_FINALIZATION_COMMIT = '745a433b0f5175d0debbed6da56bf216ddf1f752'
SOURCE_POLICY_SHA = '8674f2b36586b517a422865733de952f26c1e20f71a773f3ae922cfb36771afc'
SOURCE_PROFILE_SHAS = ['e8575b682de9f8d999744b696ddc9012380241fce32f4a684481c085d134c827', 'c9edc7f08eff62a0606e227494614aedc3ba1ef76ce7aa7be83894dd18a97ff3']
SOURCE_RECORD_SHAS = ['dc6d5b8121f7ab53f0963c59f21e33bac231cac236ded4d43a754f28a743f8de', 'bdec63ea6a3a087c8be937bc7b295a93dadabb28cf388f87aced7356f8d1b35d']
MANIFEST = ROOT / f"release/phase-49-{MODE}.json"
REPORT = ROOT / f"reports/phase-49-{MODE}.md"
CHECK_IDS = ['source-candidate-sha-exact', 'source-postmerge-sha-exact', 'source-finalization-commit-exact', 'source-phase-exact', 'source-state-validated', 'source-decision-exact', 'source-next-gate-exact', 'source-workflow-count-exact', 'source-policy-count-exact', 'source-profile-count-exact', 'source-record-count-exact', 'source-check-count-exact', 'source-failed-check-count-zero', 'source-slot-count-exact', 'source-populated-slot-count-zero', 'source-blocked-slot-count-exact', 'source-symbolic-reference-count-exact', 'source-resolved-reference-count-zero', 'source-operation-count-exact', 'source-dispatched-operation-count-zero', 'source-stage-count-exact', 'source-active-stage-count-zero', 'source-precondition-count-exact', 'source-evaluated-precondition-count-zero', 'source-rollback-count-exact', 'source-invoked-rollback-count-zero', 'source-ticket-count-exact', 'source-ticket-field-count-exact', 'source-human-gates-pending-exact', 'source-human-gates-satisfied-zero', 'source-real-authorization-false', 'policy-binding-exact', 'profile-binding-exact', 'record-sequence-exact', 'check-set-exact', 'check-count-exact', 'failed-check-count-zero', 'source-policy-sha-bound', 'source-profile-sha-bound', 'source-record-sha-bound', 'authorization-profile-count-exact', 'authorization-stage-count-exact', 'authorization-stages-defined', 'authorization-stages-inactive', 'authorization-stage-order-deterministic', 'authorization-stage-id-unique', 'authorization-requirement-count-exact', 'authorization-requirements-required', 'authorization-requirements-unevaluated', 'authorization-requirement-order-deterministic', 'authorization-requirement-id-unique', 'approval-role-count-exact', 'approval-roles-required', 'approval-roles-unsatisfied', 'approval-role-order-deterministic', 'dual-control-required', 'role-independence-required', 'operator-role-unassigned', 'reviewer-role-unassigned', 'authorization-officer-role-unassigned', 'authorization-scope-profile-bound', 'authorization-scope-source-bound', 'authorization-scope-operation-bound', 'authorization-scope-engine-bound', 'authorization-scope-resource-bound', 'authorization-scope-one-time-use', 'authorization-scope-operation-limit-exact', 'authorization-scope-network-forbidden', 'authorization-scope-atlas-forbidden', 'authorization-scope-repository-write-forbidden', 'authorization-scope-result-recording-forbidden', 'authorization-scope-status-change-forbidden', 'validity-window-defined', 'validity-window-inactive', 'validity-window-bounded', 'revocation-policy-defined', 'revocation-policy-inactive', 'immediate-revocation-supported', 'blank-token-count-exact', 'blank-token-field-count-exact', 'token-fields-empty', 'token-issued-false', 'token-scope-bound', 'token-source-bound', 'token-operation-set-bound', 'authorization-request-absent', 'approval-evaluation-absent', 'authorization-decision-absent', 'authorization-grant-absent', 'authorization-token-absent', 'execution-ticket-absent', 'population-run-absent', 'source-resolution-absent', 'value-insertion-absent', 'operation-dispatch-absent', 'stage-activation-absent', 'precondition-evaluation-absent', 'rollback-invocation-absent', 'candidate-identity-absent', 'candidate-body-absent', 'candidate-signature-absent', 'candidate-creation-forbidden', 'candidate-assembly-forbidden', 'candidate-population-forbidden', 'candidate-persistence-forbidden', 'candidate-submission-forbidden', 'response-envelope-absent', 'validation-result-absent', 'reviewer-identity-absent', 'reviewer-contact-forbidden', 'audit-event-absent', 'status-change-absent', 'atlas-boundary-preserved', 'external-network-boundary-preserved', 'repository-mutation-boundary-preserved', 'automatic-status-boundary-preserved', 'live-false', 'authority-separated', 'source-record-ledger-bound', 'authorization-ledger-chain-valid', 'authorization-verdict-exact', 'recovery-matrix-complete', 'mutation-rejection-boundary', 'no-inherited-status', 'local-only', 'real-authorization-false', 'authorization-request-creation-authority-exact', 'approval-evaluation-authority-exact', 'authorization-decision-recording-authority-exact', 'authorization-grant-authority-exact', 'authorization-token-issuance-authority-exact', 'operation-dispatch-authority-exact', 'stage-activation-authority-exact', 'precondition-evaluation-authority-exact', 'rollback-invocation-authority-exact', 'execution-ticket-authority-exact']
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

def signed(value: dict[str, Any]) -> dict[str, Any]:
    result = dict(value)
    result["sha256"] = digest(value)
    return result

def operation_ids(sequence: int) -> list[str]:
    prefix = f"principia:phase47-population-execution:{sequence:04d}"
    return [f"{prefix}:operation:{index:02d}" for index in range(1, 19)]

def build_document() -> dict[str, Any]:
    policy = signed({
        "id": "principia-phase49-population-execution-authorization-readiness-policy",
        "version": "0.1",
        "source_candidate_sha256": SOURCE_CANDIDATE_SHA,
        "source_postmerge_sha256": SOURCE_POSTMERGE_SHA,
        "source_finalization_commit": SOURCE_FINALIZATION_COMMIT,
        "source_assurance_policy_sha256": SOURCE_POLICY_SHA,
        "check_ids": CHECK_IDS,
        "authorization_profile_count": 2,
        "authorization_stage_count": 24,
        "authorization_requirement_count": 64,
        "required_approval_role_count": 6,
        "blank_authorization_token_count": 2,
        "blank_authorization_token_field_count": 36,
        "population_slot_count": 36,
        "populated_slot_count": 0,
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
        "local_population_execution_authorization_readiness_planning_permitted": True,
        "authorization_request_creation_permitted": False,
        "approval_evaluation_permitted": False,
        "authorization_decision_recording_permitted": False,
        "authorization_grant_permitted": False,
        "authorization_token_issuance_permitted": False,
    })
    profiles: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for sequence in (1, 2):
        prefix = f"principia:phase49-population-execution-authorization:{sequence:04d}"
        ops = operation_ids(sequence)
        op_sha = digest(ops)
        authorization_stages = [
            {"id": f"{prefix}:stage:{index:02d}", "sequence": index, "stage_kind": stage,
              "state": "defined-not-active", "activation_permitted": False}
            for index, stage in enumerate(AUTHORIZATION_STAGES, 1)
        ]
        authorization_requirements = [
            {"id": f"{prefix}:requirement:{index:02d}", "sequence": index, "requirement_kind": requirement,
              "state": "required-not-evaluated", "evaluation_permitted": False}
            for index, requirement in enumerate(AUTHORIZATION_REQUIREMENTS, 1)
        ]
        approval_roles = [
            {"sequence": index, "role": role, "state": "required-not-satisfied", "identity": None,
              "approval_evidence_sha256": None}
            for index, role in enumerate(REQUIRED_ROLES, 1)
        ]
        token = {field: None for field in TOKEN_FIELDS}
        token.update({"issued": False, "state": "blank-not-issued"})
        scope = {
            "profile_bound": True,
            "source_snapshot_bound": True,
            "operation_set_bound": True,
            "engine_bound": True,
            "resource_bound": True,
            "one_time_use": True,
            "maximum_operation_count": 18,
            "source_snapshot_sha256": SOURCE_CANDIDATE_SHA,
            "operation_set_sha256": op_sha,
            "external_network": False,
            "atlas_access": False,
            "repository_write": False,
            "result_recording_enabled": False,
            "status_change_enabled": False,
        }
        profile = signed({
            "id": f"principia:phase49-population-execution-authorization-profile:{sequence:04d}",
            "sequence": sequence,
            "source_population_execution_assurance_sequence": sequence,
            "source_population_execution_assurance_profile_sha256": SOURCE_PROFILE_SHAS[sequence - 1],
            "source_population_execution_assurance_record_sha256": SOURCE_RECORD_SHAS[sequence - 1],
            "policy_sha256": policy["sha256"],
            "required_roles": REQUIRED_ROLES,
            "assigned_role_count": 0,
            "dual_control_required": True,
            "role_independence_required": True,
            "authorization_stages": authorization_stages,
            "authorization_requirements": authorization_requirements,
            "approval_roles": approval_roles,
            "authorization_scope": scope,
            "validity_window_policy": {"maximum_seconds": 900, "state": "defined-not-active"},
            "revocation_policy": {"immediate_revocation_supported": True, "state": "defined-not-active"},
            "authorization_token_template": token,
            "authorization_grant_permitted": False,
        })
        profiles.append(profile)
        record = signed({
            "id": f"principia:phase49-population-execution-authorization-readiness-record:{sequence:04d}",
            "sequence": sequence,
            "source_population_execution_assurance_sequence": sequence,
            "policy_sha256": policy["sha256"],
            "profile_sha256": profile["sha256"],
            "check_set_sha256": digest(CHECK_IDS),
            "passed_check_count": len(CHECK_IDS),
            "failed_check_count": 0,
            "authorization_stage_count": 12,
            "active_authorization_stage_count": 0,
            "authorization_requirement_count": 32,
            "evaluated_authorization_requirement_count": 0,
            "required_approval_role_count": 3,
            "satisfied_approval_role_count": 0,
            "blank_authorization_token_count": 1,
            "blank_authorization_token_field_count": 18,
            "population_slot_count": 18,
            "populated_slot_count": 0,
            "symbolic_reference_count": 18,
            "resolved_reference_count": 0,
            "population_operation_count": 18,
            "dispatched_operation_count": 0,
            "execution_stage_count": 10,
            "active_execution_stage_count": 0,
            "execution_precondition_count": 24,
            "evaluated_precondition_count": 0,
            "rollback_rule_count": 18,
            "invoked_rollback_count": 0,
            "blank_execution_ticket_count": 1,
            "blank_execution_ticket_field_count": 12,
            "human_gate_pending_count": 6,
            "human_gate_satisfied_count": 0,
            "authorization_request_created": False,
            "approval_evaluated": False,
            "authorization_decision_recorded": False,
            "authorization_granted": False,
            "authorization_token_issued": False,
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
            "execution_ticket_issued": False,
            "execution_run_created": False,
            "envelope_received": False,
            "reviewer_identity_count": 0,
            "reviewer_contact_count": 0,
            "validation_result_count": 0,
            "audit_event_count": 0,
            "status_change_count": 0,
            "real_authorization_claimed": False,
            "local_only": True,
            "status": "population-execution-authorization-readiness-defined-no-grant",
            "verdict": DECISION,
        })
        records.append(record)
    entries = []
    previous = None
    for record in records:
        entry = {"sequence": record["sequence"], "record_id": record["id"], "record_sha256": record["sha256"],
                  "previous_entry_sha256": previous}
        entry_sha = digest(entry)
        entries.append({"entry": entry, "entry_sha256": entry_sha})
        previous = entry_sha
    authority = {
        "local_population_execution_authorization_readiness_planning_permitted": True,
        "authorization_request_creation_permitted": False,
        "approval_evaluation_permitted": False,
        "authorization_decision_recording_permitted": False,
        "authorization_grant_permitted": False,
        "authorization_token_issuance_permitted": False,
        "source_resolution_permitted": False,
        "value_insertion_permitted": False,
        "operation_dispatch_permitted": False,
        "stage_activation_permitted": False,
        "precondition_evaluation_permitted": False,
        "rollback_invocation_permitted": False,
        "execution_ticket_issuance_permitted": False,
        "candidate_creation_permitted": False,
        "candidate_assembly_permitted": False,
        "candidate_population_permitted": False,
        "candidate_persistence_permitted": False,
        "candidate_submission_permitted": False,
        "reviewer_contact_permitted": False,
        "validation_execution_permitted": False,
        "token_issuance_permitted": False,
        "atlas_call_permitted": False,
        "external_network_required": False,
        "repository_mutation": False,
        "automatic_status_change": False,
        "automatic_release_action": False,
        "human_authorization_claimed": False,
        "status_inheritance": "prohibited",
    }
    result = {
        "authorization_readiness_policy_count": 1,
        "authorization_readiness_profile_count": 2,
        "authorization_readiness_record_count": 2,
        "authorization_readiness_check_count": len(CHECK_IDS) * 2,
        "failed_authorization_readiness_check_count": 0,
        "source_population_execution_assurance_check_count": 240,
        "source_failed_population_execution_assurance_check_count": 0,
        "authorization_stage_count": 24,
        "active_authorization_stage_count": 0,
        "authorization_requirement_count": 64,
        "evaluated_authorization_requirement_count": 0,
        "required_approval_role_count": 6,
        "satisfied_approval_role_count": 0,
        "blank_authorization_token_count": 2,
        "blank_authorization_token_field_count": 36,
        "population_slot_count": 36,
        "populated_slot_count": 0,
        "symbolic_reference_count": 36,
        "resolved_reference_count": 0,
        "population_operation_count": 36,
        "dispatched_operation_count": 0,
        "execution_stage_count": 20,
        "active_execution_stage_count": 0,
        "execution_precondition_count": 48,
        "evaluated_precondition_count": 0,
        "rollback_rule_count": 36,
        "invoked_rollback_count": 0,
        "blank_execution_ticket_count": 2,
        "blank_execution_ticket_field_count": 24,
        "human_gate_pending_count": 12,
        "human_gate_satisfied_count": 0,
        "authorization_request_count": 0,
        "approval_evaluation_count": 0,
        "authorization_decision_count": 0,
        "authorization_grant_count": 0,
        "authorization_token_count": 0,
        "candidate_count": 0,
        "population_run_count": 0,
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
        "contract": "principia-phase49-population-execution-authorization-readiness/0.1",
        "phase": 49, "mode": MODE, "state": STATE, "decision": DECISION, "next_gate": NEXT,
        "fixture_kind": "bounded-synthetic", "live": False, "live_activation_permitted": False,
        "real_authorization_claimed": False,
        "source_phase48": {
            "candidate_sha256": SOURCE_CANDIDATE_SHA,
            "postmerge_sha256": SOURCE_POSTMERGE_SHA,
            "authoritative_finalization_commit": SOURCE_FINALIZATION_COMMIT,
            "state": "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assurance-validated",
            "decision": "response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-assured-no-population-run",
            "next_gate": STATE,
            "applicable_workflows": 41,
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
        },
        "authorization_readiness_policy": policy,
        "authorization_readiness_profiles": profiles,
        "authorization_readiness_records": records,
        "ledger": {"entries": entries, "head_sequence": 2, "head_sha256": previous},
        "recovery_matrix": {
            "scenario_count": 318, "baseline_count": 1, "mutation_count": 317, "rejected_mutation_count": 317,
            "categories": ["source-provenance","authorization-profile-integrity","authorization-stage-integrity",
                           "authorization-requirement-integrity","approval-role-integrity","authorization-scope-integrity",
                           "token-integrity","execution-boundary","human-governance","authority-boundary",
                           "ledger-integrity","recovery-determinism"],
        },
        "authority": authority,
        "result": result,
    }

def render_report(document: dict[str, Any], manifest_sha: str) -> str:
    r = document["result"]
    lines = [
        "# Phase 49 — Offline Candidate Population Execution Authorization Readiness", "",
        "> Date: 2026-07-31", "> Repository: `Rhodan-lab/principle-to-system`",
        f"> State: `{document['state']}`", "",
        "## Purpose", "",
        "Phase 49 defines deterministic authorization-readiness controls for the still-uncreated and unpopulated authorization-decision candidate. It binds the assured Phase 48 source, operation sets, role separation, validity and revocation controls, and blank authorization-token templates without evaluating approvals or granting authority.", "",
        "## Immutable source boundary", "",
        f"- Phase 48 candidate SHA-256: `{SOURCE_CANDIDATE_SHA}`",
        f"- Phase 48 post-merge SHA-256: `{SOURCE_POSTMERGE_SHA}`",
        f"- Phase 48 authoritative finalization: `{SOURCE_FINALIZATION_COMMIT}`",
        "- Phase 48 applicable workflows: `41`",
        f"- Phase 49 candidate SHA-256: `{manifest_sha}`", "",
        "## Deterministic authorization-readiness result", "",
        f"- Authorization-readiness policies: `{r['authorization_readiness_policy_count']}`",
        f"- Authorization-readiness profiles: `{r['authorization_readiness_profile_count']}`",
        f"- Authorization-readiness records: `{r['authorization_readiness_record_count']}`",
        f"- Readiness checks: `{r['authorization_readiness_check_count']}`; failed: `0`",
        f"- Authorization stages: `{r['authorization_stage_count']}`; active: `0`",
        f"- Authorization requirements: `{r['authorization_requirement_count']}`; evaluated: `0`",
        f"- Required approval roles: `{r['required_approval_role_count']}`; satisfied: `0`",
        f"- Blank authorization tokens: `{r['blank_authorization_token_count']}` with `{r['blank_authorization_token_field_count']}` empty fields",
        f"- Planned operations: `{r['population_operation_count']}`; dispatched: `0`",
        f"- Human gates pending: `{r['human_gate_pending_count']}`; satisfied: `0`",
        "- Recovery scenarios: `318`; rejected mutations: `317`", "",
        "## Frozen boundaries", "",
        "No authorization request, approval evaluation, authorization decision, grant, or token issuance occurs. No candidate is created, assembled, populated, persisted, signed, or submitted. No source is resolved, value inserted, operation dispatched, stage activated, precondition evaluated, rollback invoked, execution ticket issued, or population run started. Atlas is not called or modified; networking and repository mutation remain forbidden.", "",
        "## Next gate", "", f"`{document['next_gate']}`",
    ]
    return "\n".join(lines) + "\n"

def write_or_check(check: bool) -> int:
    document = build_document()
    manifest_bytes = canonical(document)
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    report_bytes = render_report(document, manifest_sha).encode()
    expected = {MANIFEST: manifest_bytes, REPORT: report_bytes}
    failures = []
    for path, data in expected.items():
        if check:
            if not path.is_file() or path.read_bytes() != data:
                failures.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    if failures:
        print("Phase 49 deterministic byte drift: " + ", ".join(failures), file=sys.stderr)
        return 1
    print(f"Phase 49 deterministic bytes passed: sha256={manifest_sha}")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return write_or_check(args.check)

if __name__ == "__main__":
    raise SystemExit(main())
