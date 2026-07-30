#!/usr/bin/env python3
"""Independently validate the Phase 38 authorization-decision readiness assurance record."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "release/phase-37-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness.json"
SOURCE_POST = ROOT / "release/phase-37-postmerge.json"
CANDIDATE = ROOT / "release/phase-38-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance.json"
SOURCE_SHA = "724a12243300d6c91cf60fef046f5ae40089c98867bba62bdd524e3684aec2ae"
SOURCE_POST_SHA = "519c98afb8cd34f618c2e3c5421e0c1be2a0baa0c5ef836621910ce487c86795"
CANDIDATE_SHA = "b3c5d8ea8da88cd2975531ccd149b0dde980dc480b9e7385425cafad3e024ec8"
FINALIZATION_COMMIT = "6b87f89653388843e38ffd05ef3639e55a7146b8"
MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance"
STATE = MODE + "-candidate"
NEXT_GATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-candidate"
DECISION = "response-intake-envelope-validation-execution-authorization-decision-readiness-assured-no-decision-candidate-created"
VERDICT = "response-envelope-validation-execution-authorization-decision-readiness-assured-no-decision"


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_value(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path)
    return value


def validate_manifest(candidate: dict[str, Any], source: dict[str, Any], post: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if candidate.get("contract") != "principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance/0.1":
        errors.append("contract drift")
    for key, expected in (("phase", 38), ("mode", MODE), ("state", STATE), ("decision", DECISION), ("next_gate", NEXT_GATE), ("live", False), ("live_activation_permitted", False), ("real_authorization_claimed", False)):
        if candidate.get(key) != expected:
            errors.append(f"{key} drift")

    source_binding = candidate.get("source_phase37", {})
    expected_source = {
        "phase37_candidate_sha256": SOURCE_SHA,
        "phase37_finalization_commit": FINALIZATION_COMMIT,
        "phase37_postmerge_sha256": SOURCE_POST_SHA,
    }
    if source_binding != expected_source:
        errors.append("Phase 37 source binding drift")
    if post.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-validated":
        errors.append("Phase 37 postmerge state drift")
    if post.get("candidate_record", {}).get("sha256") != SOURCE_SHA:
        errors.append("Phase 37 postmerge candidate binding drift")
    if post.get("principia", {}).get("merge_commit") != "16516cd5b67b480a572b949996e8ebceaa8d1acb":
        errors.append("Phase 37 candidate merge drift")

    authority = candidate.get("authority", {})
    true_authority = [key for key, value in authority.items() if value is True]
    if true_authority != ["local_response_envelope_validation_execution_authorization_decision_readiness_assurance_permitted"]:
        errors.append("authority true-set drift")
    for forbidden in (
        "atlas_call_permitted", "authorization_decision_candidate_creation_permitted",
        "authorization_decision_recording_permitted", "response_envelope_validation_execution_authorization_grant_permitted",
        "response_envelope_validation_execution_authorized", "reviewer_contact_permitted", "repository_mutation",
        "automatic_release_action", "automatic_status_change", "external_network_required",
    ):
        if authority.get(forbidden) is not False:
            errors.append(f"authority boundary drift: {forbidden}")
    if authority.get("status_inheritance") != "prohibited":
        errors.append("status inheritance drift")

    policy = source.get("decision_policy", {})
    profiles = source.get("decision_profiles", [])
    records = source.get("decision_readiness_records", [])
    source_ledger = {item["entry"]["decision_readiness_id"]: item for item in source.get("ledger", {}).get("entries", [])}
    assurances = candidate.get("assurances", [])
    if len(assurances) != 2 or len(records) != 2 or len(profiles) != 2:
        errors.append("record cardinality drift")
        return errors

    output_ledger = candidate.get("ledger", {}).get("entries", [])
    if len(output_ledger) != 2:
        errors.append("assurance ledger cardinality drift")
        return errors
    previous = None
    total_checks = 0
    for index, (assurance, record, profile, ledger_item) in enumerate(zip(assurances, records, profiles, output_ledger, strict=True), 1):
        sid = record.get("decision_readiness_id")
        source_entry = source_ledger.get(sid)
        if source_entry is None:
            errors.append(f"source ledger missing at {index}")
            continue
        expected_assurance_id = sid.replace("authorization-decision-readiness:", "authorization-decision-readiness-assurance:")
        expected_values = {
            "sequence": index,
            "assurance_id": expected_assurance_id,
            "source_decision_readiness_id": sid,
            "source_readiness_record_sha256": sha_value(record),
            "source_ledger_entry_sha256": source_entry["entry_sha256"],
            "decision_policy_id": policy.get("decision_policy_id"),
            "decision_policy_version": policy.get("decision_policy_version"),
            "decision_policy_sha256": policy.get("decision_policy_sha256"),
            "decision_profile_id": profile.get("decision_profile_id"),
            "decision_profile_sha256": sha_value(profile),
            "decision_stages_sha256": sha_value(policy.get("decision_stages")),
            "decision_requirements_sha256": sha_value(policy.get("decision_requirements")),
            "decision_options_sha256": sha_value(policy.get("decision_options")),
            "required_decision_roles_sha256": sha_value(profile.get("required_decision_roles")),
            "blank_decision_record_sha256": sha_value(record.get("blank_decision_record")),
            "blank_decision_record_field_count": 16,
            "human_gate_pending_count": 4,
            "human_gate_satisfied_count": 0,
            "failed_assurance_check_count": 0,
            "status": "assured-no-decision",
            "verdict": VERDICT,
            "local_only": True,
            "real_authorization_claimed": False,
        }
        for key, expected in expected_values.items():
            if assurance.get(key) != expected:
                errors.append(f"assurance {index} {key} drift")
        if assurance.get("decision_policy_computed_sha256") != sha_value({k: v for k, v in policy.items() if k != "decision_policy_sha256"}):
            errors.append(f"assurance {index} policy computed digest drift")
        checks = assurance.get("assurance_checks", {})
        if not isinstance(checks, dict) or len(checks) != 72 or any(value is not True for value in checks.values()):
            errors.append(f"assurance {index} checks drift")
        if assurance.get("assurance_check_count") != len(checks):
            errors.append(f"assurance {index} check count drift")
        total_checks += len(checks)
        frozen_false = (
            "approval_evidence_recorded", "approval_received", "authorization_decision_candidate_created",
            "authorization_decision_record_created", "authorization_decision_recorded", "authorization_granted",
            "authorization_token_issued", "conflict_declaration_evaluated", "decision_option_selected",
            "disposition_selected", "execution_run_created", "execution_ticket_issued", "response_envelope_received",
            "reviewer_contact_permitted", "reviewer_identity_present", "status_change", "validation_result_recorded",
        )
        for key in frozen_false:
            if assurance.get(key) is not False:
                errors.append(f"assurance {index} frozen state drift: {key}")
        record_sha = sha_value(assurance)
        entry = ledger_item.get("entry", {})
        expected_entry = {
            "assurance_id": expected_assurance_id,
            "previous_entry_sha256": previous,
            "record_sha256": record_sha,
            "sequence": index,
            "source_decision_readiness_id": sid,
            "source_ledger_entry_sha256": source_entry["entry_sha256"],
            "verdict": VERDICT,
        }
        if entry != expected_entry:
            errors.append(f"assurance ledger entry {index} drift")
        entry_sha = sha_value(entry)
        if ledger_item.get("entry_sha256") != entry_sha:
            errors.append(f"assurance ledger digest {index} drift")
        previous = entry_sha

    ledger = candidate.get("ledger", {})
    if ledger.get("head_sequence") != 2 or ledger.get("head_sha256") != previous:
        errors.append("assurance ledger head drift")
    checkpoint = candidate.get("checkpoint", {})
    if checkpoint.get("ledger_sha256") != previous or checkpoint.get("assurance_record_count") != 2 or checkpoint.get("assurance_check_count") != total_checks:
        errors.append("checkpoint drift")

    result = candidate.get("result", {})
    expected_counts = {
        "assured_decision_readiness_record_count": 2,
        "assurance_check_count": 144,
        "failed_assurance_check_count": 0,
        "decision_policy_count": 1,
        "decision_profile_count": 2,
        "decision_readiness_record_count": 2,
        "decision_stage_count": 24,
        "decision_requirement_count": 52,
        "decision_requirement_evaluated_count": 0,
        "decision_option_count": 3,
        "decision_option_selected_count": 0,
        "blank_decision_record_count": 2,
        "blank_decision_record_field_count": 32,
        "required_decision_role_count": 4,
        "dual_control_profile_count": 2,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
        "authorization_decision_candidate_created_count": 0,
        "authorization_decision_recorded_count": 0,
        "authorization_granted_count": 0,
        "authorization_token_issued_count": 0,
        "execution_run_count": 0,
        "response_envelope_received_count": 0,
        "reviewer_contact_count": 0,
        "status_change_count": 0,
    }
    for key, expected in expected_counts.items():
        if result.get(key) != expected:
            errors.append(f"result count drift: {key}")
    for key, value in result.items():
        if key.endswith("_count") and key not in {
            "assured_decision_readiness_record_count", "assurance_check_count", "decision_policy_count",
            "decision_profile_count", "decision_readiness_record_count", "decision_stage_count",
            "decision_requirement_count", "decision_option_count", "blank_decision_record_count",
            "blank_decision_record_field_count", "conflict_declaration_required_count", "dual_control_profile_count",
            "human_gate_pending_count", "readiness_check_count", "required_decision_role_count",
        } and value != 0:
            errors.append(f"nonzero operational result: {key}")

    recovery = candidate.get("recovery", {})
    if recovery.get("accepted") != ["baseline-phase37-decision-readiness-assurance"] or recovery.get("accepted_count") != 1:
        errors.append("recovery baseline drift")
    rejected = recovery.get("rejected", [])
    if recovery.get("rejected_count") != len(rejected) or recovery.get("scenario_count") != len(rejected) + 1 or len(rejected) != 205:
        errors.append("recovery matrix drift")
    return errors


def validate() -> list[str]:
    errors: list[str] = []
    for path, label in ((SOURCE, "source"), (SOURCE_POST, "source postmerge"), (CANDIDATE, "candidate")):
        if not path.is_file():
            errors.append(f"Phase 38 {label} missing")
    if errors:
        return errors
    if sha_file(SOURCE) != SOURCE_SHA:
        errors.append("Phase 37 source digest drift")
    if sha_file(SOURCE_POST) != SOURCE_POST_SHA:
        errors.append("Phase 37 postmerge digest drift")
    if sha_file(CANDIDATE) != CANDIDATE_SHA:
        errors.append("Phase 38 candidate digest drift")
    if CANDIDATE.read_bytes() != canonical(load(CANDIDATE)) + b"\n":
        errors.append("Phase 38 candidate is not canonical JSON")
    errors.extend(validate_manifest(load(CANDIDATE), load(SOURCE), load(SOURCE_POST)))
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Phase 38 assurance errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Phase 38 assurance passed: candidate={CANDIDATE_SHA}, assurances=2, checks=144, recovery=206, live=false.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
