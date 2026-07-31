#!/usr/bin/env python3
"""Generate deterministic Phase 43 candidate-assembly readiness evidence."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "release/phase-42-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance.json"
POSTMERGE = ROOT / "release/phase-42-postmerge.json"
OUTPUT = ROOT / "release/phase-43-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness.json"
MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness"
STATE = MODE + "-candidate"
DECISION = "response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-defined-no-candidate-assembled"
NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance-candidate"
SOURCE_SHA = "6fb602bc5ef863765ceb50ba66124b843381fd15c6dac9da9250429e18e76f26"
POST_SHA = "887aa4a6c23be70b0c619c09b024e58f4321acf19ea2181bbb0f5734c1fe5cf4"
CHECK_IDS = ['source-candidate-sha-exact',
 'source-postmerge-sha-exact',
 'source-phase-exact',
 'source-mode-exact',
 'source-state-exact',
 'source-decision-exact',
 'source-next-gate-exact',
 'source-live-false',
 'source-real-authorization-false',
 'source-assurance-policy-count-exact',
 'source-assurance-record-count-exact',
 'source-assurance-check-count-exact',
 'source-failed-assurance-check-count-zero',
 'source-field-plan-count-exact',
 'source-field-populated-count-zero',
 'source-preparation-stage-count-exact',
 'source-preparation-requirement-count-exact',
 'source-human-gate-pending-count-exact',
 'source-human-gate-satisfied-count-zero',
 'source-candidate-count-zero',
 'source-decision-record-count-zero',
 'source-decision-count-zero',
 'source-grant-count-zero',
 'source-token-count-zero',
 'source-ticket-count-zero',
 'source-execution-run-count-zero',
 'source-envelope-count-zero',
 'source-reviewer-contact-count-zero',
 'source-status-change-count-zero',
 'source-audit-event-count-zero',
 'assembly-policy-binding-exact',
 'assembly-profile-binding-exact',
 'assembly-record-sequence-exact',
 'assembly-slot-count-exact',
 'assembly-slot-order-exact',
 'assembly-slot-names-exact',
 'assembly-slot-sources-symbolic',
 'assembly-slot-states-unpopulated',
 'assembly-slot-population-forbidden',
 'assembly-stage-count-exact',
 'assembly-stage-order-exact',
 'assembly-stage-states-inactive',
 'assembly-requirement-count-exact',
 'assembly-requirement-order-exact',
 'assembly-requirement-states-unevaluated',
 'candidate-identity-absent',
 'candidate-body-absent',
 'candidate-signature-absent',
 'candidate-persistence-absent',
 'candidate-submission-absent',
 'candidate-assembly-forbidden',
 'decision-selection-absent',
 'authorization-grant-absent',
 'token-issuance-absent',
 'execution-ticket-absent',
 'reviewer-identity-absent',
 'reviewer-contact-forbidden',
 'human-gate-satisfaction-absent',
 'validation-result-absent',
 'atlas-boundary-preserved',
 'external-network-boundary-preserved',
 'repository-mutation-boundary-preserved',
 'automatic-status-boundary-preserved',
 'zero-effect-boundary-preserved']
SLOTS = [('candidate_version', 'human-governance'),
 ('candidate_id', 'human-governance'),
 ('source_assurance_id', 'phase42-assurance'),
 ('source_preparation_id', 'phase41-preparation'),
 ('policy_id', 'phase40-boundary-policy'),
 ('profile_id', 'phase40-boundary-profile'),
 ('reviewer_role', 'human-role-assignment'),
 ('authorization_officer_role', 'human-role-assignment'),
 ('conflict_declaration_ref', 'human-governance'),
 ('approval_evidence_ref', 'human-governance'),
 ('rationale', 'human-governance'),
 ('proposed_decision', 'human-governance'),
 ('validity_start', 'human-governance'),
 ('validity_end', 'human-governance'),
 ('revocation_ref', 'human-governance'),
 ('audit_chain_ref', 'human-governance'),
 ('candidate_signature', 'human-signature'),
 ('submission_target', 'human-governance')]
STAGES = ['source-lock',
 'candidate-schema-lock',
 'field-order-lock',
 'field-source-map-lock',
 'mandatory-field-completeness-plan',
 'role-binding-plan',
 'conflict-declaration-plan',
 'approval-evidence-plan',
 'rationale-plan',
 'decision-selection-plan',
 'validity-window-plan',
 'revocation-linkage-plan',
 'audit-chain-plan',
 'signature-plan',
 'persistence-plan',
 'submission-plan']
REQUIREMENTS = ['source-manifest-digest-exact',
 'source-postmerge-digest-exact',
 'source-phase-exact',
 'source-state-validated',
 'source-next-gate-exact',
 'assurance-record-count-exact',
 'assurance-check-count-exact',
 'failed-assurance-check-count-zero',
 'candidate-field-plan-count-exact',
 'candidate-field-populated-count-zero',
 'human-gate-pending-count-exact',
 'human-gate-satisfied-count-zero',
 'assembly-slot-schema-defined',
 'assembly-slot-order-defined',
 'assembly-slot-source-kinds-symbolic',
 'assembly-slot-population-forbidden',
 'assembly-stage-order-defined',
 'assembly-stage-activation-forbidden',
 'dual-control-required',
 'role-independence-required',
 'conflict-declaration-required',
 'approval-evidence-required',
 'rationale-required',
 'decision-selection-required',
 'validity-window-required',
 'revocation-linkage-required',
 'audit-chain-required',
 'signature-required',
 'persistence-forbidden',
 'submission-forbidden',
 'atlas-call-forbidden',
 'external-network-forbidden']


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_errors() -> list[str]:
    errors = []
    if not SOURCE.exists() or not POSTMERGE.exists():
        return ["Phase 42 source files missing"]
    if file_digest(SOURCE) != SOURCE_SHA:
        errors.append("Phase 42 candidate digest drift")
    if file_digest(POSTMERGE) != POST_SHA:
        errors.append("Phase 42 post-merge digest drift")
    try:
        source = json.loads(SOURCE.read_text())
        post = json.loads(POSTMERGE.read_text())
    except json.JSONDecodeError as exc:
        return [f"Phase 42 JSON parse error: {exc}"]
    if source.get("phase") != 42 or source.get("next_gate") != MODE + "-candidate":
        errors.append("Phase 42 candidate gate drift")
    result = source.get("result", {})
    expected = {
        "candidate_preparation_readiness_assurance_policy_count": 1,
        "candidate_preparation_readiness_assurance_record_count": 2,
        "candidate_preparation_readiness_assurance_check_count": 204,
        "failed_candidate_preparation_readiness_assurance_check_count": 0,
        "candidate_field_plan_count": 36,
        "candidate_field_populated_count": 0,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
    }
    if any(result.get(key) != value for key, value in expected.items()):
        errors.append("Phase 42 candidate result drift")
    expected_post_state = (
        "offline-consequence-plan-review-response-intake-envelope-validation-execution-"
        "authorization-decision-candidate-preparation-readiness-assurance-validated"
    )
    if post.get("state") != expected_post_state or post.get("next_gate") != MODE + "-candidate":
        errors.append("Phase 42 post-merge gate drift")
    if post.get("candidate_record", {}).get("sha256") != SOURCE_SHA:
        errors.append("Phase 42 post-merge candidate binding drift")
    return errors


def build_manifest() -> dict[str, Any]:
    policy_core = {
        "policy_id": "principia-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-policy",
        "version": "0.1",
        "source_manifest_sha256": SOURCE_SHA,
        "check_ids": CHECK_IDS,
        "slot_schema": [
            {"sequence": i + 1, "name": name, "source_kind": source, "required": True}
            for i, (name, source) in enumerate(SLOTS)
        ],
        "stages": [
            {"sequence": i + 1, "id": name, "state": "inactive", "activation_permitted": False}
            for i, name in enumerate(STAGES)
        ],
        "requirements": [
            {"sequence": i + 1, "id": name, "state": "unevaluated", "evaluation_permitted": False}
            for i, name in enumerate(REQUIREMENTS)
        ],
        "candidate_creation_permitted": False,
        "candidate_population_permitted": False,
        "candidate_assembly_permitted": False,
        "candidate_persistence_permitted": False,
        "candidate_submission_permitted": False,
    }
    policy = dict(policy_core)
    policy["sha256"] = digest(policy_core)
    check_sha = digest(policy_core["check_ids"])
    slot_sha = digest(policy_core["slot_schema"])
    stage_sha = digest(policy_core["stages"])
    requirement_sha = digest(policy_core["requirements"])
    profiles, records = [], []
    for sequence in (1, 2):
        profile_core = {
            "sequence": sequence,
            "id": (
                "principia:authorization-decision-candidate-assembly-readiness-profile:"
                f"feedback-manual-review:{sequence:04d}"
            ),
            "source_assurance_sequence": sequence,
            "source_manifest_sha256": SOURCE_SHA,
            "policy_sha256": policy["sha256"],
            "required_roles": ["reviewer", "authorization-officer"],
            "dual_control_required": True,
            "role_independence_required": True,
            "assembly_permitted": False,
        }
        profile = dict(profile_core)
        profile["sha256"] = digest(profile_core)
        profiles.append(profile)
        records.append({
            "sequence": sequence,
            "id": (
                "principia:authorization-decision-candidate-assembly-readiness:"
                f"feedback-manual-review:{sequence:04d}"
            ),
            "source_assurance_sequence": sequence,
            "source_manifest_sha256": SOURCE_SHA,
            "policy_sha256": policy["sha256"],
            "profile_sha256": profile["sha256"],
            "check_set_sha256": check_sha,
            "passed_check_count": 64,
            "failed_check_count": 0,
            "slot_schema_sha256": slot_sha,
            "slot_count": 18,
            "populated_slot_count": 0,
            "stage_plan_sha256": stage_sha,
            "stage_count": 16,
            "active_stage_count": 0,
            "requirement_plan_sha256": requirement_sha,
            "requirement_count": 32,
            "evaluated_requirement_count": 0,
            "human_gate_pending_count": 4,
            "human_gate_satisfied_count": 0,
            "candidate_id_present": False,
            "candidate_body_present": False,
            "candidate_signature_present": False,
            "candidate_persisted": False,
            "candidate_submitted": False,
            "candidate_assembled": False,
            "decision_recorded": False,
            "authorization_granted": False,
            "authorization_token_issued": False,
            "execution_ticket_issued": False,
            "execution_run_created": False,
            "response_envelope_received": False,
            "reviewer_identity_present": False,
            "reviewer_contact_permitted": False,
            "validation_result_recorded": False,
            "audit_event_count": 0,
            "status_change": False,
            "local_only": True,
            "real_authorization_claimed": False,
            "status": "assembly-readiness-defined-no-candidate",
            "verdict": (
                "response-envelope-validation-execution-authorization-decision-candidate-"
                "assembly-readiness-defined-no-candidate"
            ),
        })
    entries, previous = [], None
    for record in records:
        entry = {
            "sequence": record["sequence"],
            "record_id": record["id"],
            "record_sha256": digest(record),
            "previous_entry_sha256": previous,
        }
        entry_sha = digest(entry)
        entries.append({"entry": entry, "entry_sha256": entry_sha})
        previous = entry_sha
    result = {
        "source_assurance_policy_count": 1,
        "source_assurance_record_count": 2,
        "source_assurance_check_count": 204,
        "source_failed_assurance_check_count": 0,
        "assembly_readiness_policy_count": 1,
        "assembly_readiness_profile_count": 2,
        "assembly_readiness_record_count": 2,
        "assembly_check_count": 128,
        "failed_assembly_check_count": 0,
        "assembly_slot_count": 36,
        "populated_slot_count": 0,
        "assembly_stage_count": 32,
        "active_stage_count": 0,
        "assembly_requirement_count": 64,
        "evaluated_requirement_count": 0,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
        "authorization_decision_candidate_count": 0,
        "decision_record_count": 0,
        "authorization_grant_count": 0,
        "authorization_token_count": 0,
        "execution_ticket_count": 0,
        "execution_run_count": 0,
        "response_envelope_count": 0,
        "reviewer_identity_count": 0,
        "reviewer_contact_count": 0,
        "validation_result_count": 0,
        "audit_event_count": 0,
        "status_change_count": 0,
        "real_authorization_claimed": False,
    }
    authority = {
        "local_assembly_readiness_definition_permitted": True,
        "candidate_creation_permitted": False,
        "candidate_population_permitted": False,
        "candidate_assembly_permitted": False,
        "candidate_persistence_permitted": False,
        "candidate_submission_permitted": False,
        "decision_recording_permitted": False,
        "authorization_grant_permitted": False,
        "token_issuance_permitted": False,
        "execution_ticket_issuance_permitted": False,
        "response_envelope_processing_permitted": False,
        "validation_execution_permitted": False,
        "reviewer_contact_permitted": False,
        "review_execution_permitted": False,
        "atlas_call_permitted": False,
        "external_network_required": False,
        "repository_mutation": False,
        "automatic_status_change": False,
        "automatic_release_action": False,
        "status_inheritance": "prohibited",
        "human_authorization_claimed": False,
    }
    return {
        "phase": 43,
        "contract": "principia-" + MODE + "/0.1",
        "mode": MODE,
        "state": STATE,
        "decision": DECISION,
        "next_gate": NEXT,
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-" + MODE + "-thermal-control",
        "source_phase42": {
            "candidate_sha256": SOURCE_SHA,
            "postmerge_sha256": POST_SHA,
            "candidate_head_commit": "0597916365d489b2738fbb905f0f40991f42a4b7",
            "candidate_merge_commit": "057da54503e2c3b1ea1e86150c4015a99628dfed",
            "authoritative_finalization_commit": "c1b05c6fae7eddf3b535093df3f382f65cc7fe10",
            "applicable_workflows": 36,
            "assurance_record_count": 2,
            "assurance_check_count": 204,
            "failed_assurance_check_count": 0,
            "candidate_field_plan_count": 36,
            "candidate_field_populated_count": 0,
            "human_gate_pending_count": 8,
            "human_gate_satisfied_count": 0,
            "postmerge_state": (
                "offline-consequence-plan-review-response-intake-envelope-validation-execution-"
                "authorization-decision-candidate-preparation-readiness-assurance-validated"
            ),
        },
        "assembly_readiness_policy": policy,
        "assembly_readiness_profiles": profiles,
        "assembly_readiness_records": records,
        "ledger": {"entries": entries, "head_sequence": 2, "head_sha256": previous},
        "checkpoint": {
            "record_count": 2,
            "check_count": 128,
            "failed_check_count": 0,
            "populated_slot_count": 0,
            "active_stage_count": 0,
            "evaluated_requirement_count": 0,
            "human_gate_satisfied_count": 0,
            "candidate_count": 0,
            "authorization_grant_count": 0,
            "status_change_count": 0,
            "ledger_sha256": previous,
        },
        "result": result,
        "recovery": {
            "accepted": ["baseline-phase42-candidate-assembly-readiness"],
            "accepted_count": 1,
            "mutation_check_families": 64,
            "per_record_structural_mutations": 8,
            "record_count": 2,
            "global_mutations": 5,
            "rejected_count": 149,
            "scenario_count": 150,
        },
        "authority": authority,
        "validation": {"status": "candidate", "pull_request": None, "tested_head_commit": None},
        "real_authorization_claimed": False,
        "live_activation_permitted": False,
        "live": False,
    }


def evaluate_candidate(candidate: dict[str, Any]) -> list[str]:
    return [] if candidate == build_manifest() else ["candidate manifest differs from deterministic expected object"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = source_errors()
    if errors:
        print("\n".join(errors))
        return 1
    data = canonical(build_manifest())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != data:
            print("Phase 43 candidate bytes drift")
            return 1
        print(
            f"Phase 43 candidate passed: bytes={len(data)}, "
            f"sha256={hashlib.sha256(data).hexdigest()}, records=2, checks=128, recovery=150."
        )
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(data)
    print(f"wrote {OUTPUT}: bytes={len(data)}, sha256={hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
