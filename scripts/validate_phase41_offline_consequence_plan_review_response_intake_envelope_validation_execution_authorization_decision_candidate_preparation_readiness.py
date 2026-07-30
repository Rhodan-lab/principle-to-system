#!/usr/bin/env python3
"""Validate deterministic Phase 41 candidate-preparation readiness evidence."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
GENERATOR_PATH = ROOT / "scripts/generate_phase41_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_preparation_readiness.py"
spec = importlib.util.spec_from_file_location("phase41_generator", GENERATOR_PATH)
generator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(generator)

CANDIDATE = ROOT / "release/phase-41-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness.json"
SOURCE = ROOT / "release/phase-40-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance.json"
SOURCE_POST = ROOT / "release/phase-40-postmerge.json"
EXPECTED_SHA = "c45f148554f66bf21db03fa446475e55746086a47da0bb56841b95012be1d33b"
EXPECTED_STATE = generator.STATE
EXPECTED_NEXT = generator.NEXT_GATE
EXPECTED_DECISION = generator.DECISION
EXPECTED_VERDICT = generator.VERDICT

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path)
    return value

def validate_payload(candidate: dict[str, Any], source: dict[str, Any], source_post: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        expected = generator.build_manifest(source, source_post)
    except Exception as exc:
        return [f"Phase 41 expected-manifest reconstruction failed: {exc}"]

    if canonical_bytes(candidate) != canonical_bytes(expected):
        errors.append("Phase 41 deterministic manifest drift")
    if candidate.get("phase") != 41 or candidate.get("state") != EXPECTED_STATE:
        errors.append("Phase 41 identity/state drift")
    if candidate.get("next_gate") != EXPECTED_NEXT or candidate.get("decision") != EXPECTED_DECISION:
        errors.append("Phase 41 gate/decision drift")
    if candidate.get("live") is not False or candidate.get("real_authorization_claimed") is not False:
        errors.append("Phase 41 live/authorization drift")

    records = candidate.get("candidate_preparation_readiness_records")
    if not isinstance(records, list) or len(records) != 2:
        errors.append("Phase 41 preparation record count drift")
        return errors

    previous = None
    expected_entries = []
    for index, record in enumerate(records, 1):
        if record.get("sequence") != index:
            errors.append(f"preparation {index} sequence drift")
        if record.get("preparation_check_count") != 90:
            errors.append(f"preparation {index} check count drift")
        checks = record.get("preparation_checks")
        if not isinstance(checks, dict) or len(checks) != 90 or set(checks.values()) != {True}:
            errors.append(f"preparation {index} checks drift")
        if record.get("failed_preparation_check_count") != 0:
            errors.append(f"preparation {index} failed checks drift")
        if record.get("verdict") != EXPECTED_VERDICT or record.get("status") != "preparation-ready-no-candidate":
            errors.append(f"preparation {index} verdict drift")
        plan = record.get("candidate_field_plan")
        if not isinstance(plan, list) or len(plan) != 18:
            errors.append(f"preparation {index} field-plan count drift")
        elif any(
            item.get("state") != "unpopulated"
            or item.get("population_permitted") is not False
            for item in plan
        ):
            errors.append(f"preparation {index} field-plan population drift")
        forbidden_true = (
            "authorization_decision_candidate_created",
            "authorization_decision_record_created",
            "authorization_decision_recorded",
            "authorization_granted",
            "authorization_token_issued",
            "candidate_assembly_permitted",
            "candidate_id_present",
            "candidate_signature_present",
            "conflict_declaration_evaluated",
            "execution_run_created",
            "execution_ticket_issued",
            "proposed_decision_selected",
            "rationale_populated",
            "response_envelope_received",
            "reviewer_contact_permitted",
            "reviewer_identity_present",
            "revocation_reference_present",
            "status_change",
            "validation_result_recorded",
            "validity_window_active",
            "approval_evidence_recorded",
            "approval_received",
        )
        if any(record.get(key) is not False for key in forbidden_true):
            errors.append(f"preparation {index} zero-effect drift")
        if record.get("candidate_field_populated_count") != 0:
            errors.append(f"preparation {index} populated field drift")
        if record.get("human_gate_pending_count") != 4 or record.get("human_gate_satisfied_count") != 0:
            errors.append(f"preparation {index} human-gate drift")
        entry = {
            "preparation_id": record.get("preparation_id"),
            "previous_entry_sha256": previous,
            "record_sha256": generator.sha_value(record),
            "sequence": index,
            "source_assurance_id": record.get("source_assurance_id"),
            "source_ledger_entry_sha256": record.get("source_ledger_entry_sha256"),
            "verdict": EXPECTED_VERDICT,
        }
        entry_sha = generator.sha_value(entry)
        expected_entries.append({"entry": entry, "entry_sha256": entry_sha})
        previous = entry_sha

    if candidate.get("ledger") != {"entries": expected_entries, "head_sequence": 2, "head_sha256": previous}:
        errors.append("Phase 41 ledger drift")

    checkpoint = candidate.get("checkpoint", {})
    expected_checkpoint = {
        "authorization_decision_candidate_created_count": 0,
        "authorization_decision_recorded_count": 0,
        "authorization_granted_count": 0,
        "authorization_token_issued_count": 0,
        "candidate_field_populated_count": 0,
        "execution_run_count": 0,
        "failed_preparation_check_count": 0,
        "ledger_sha256": previous,
        "preparation_check_count": 180,
        "preparation_record_count": 2,
        "response_envelope_received_count": 0,
        "status_change_count": 0,
    }
    if checkpoint != expected_checkpoint:
        errors.append("Phase 41 checkpoint drift")

    result = candidate.get("result", {})
    expected_counts = {
        "candidate_field_plan_count": 36,
        "candidate_field_populated_count": 0,
        "candidate_preparation_policy_count": 1,
        "candidate_preparation_profile_count": 2,
        "candidate_preparation_readiness_record_count": 2,
        "candidate_preparation_stage_count": 28,
        "candidate_preparation_requirement_count": 88,
        "candidate_preparation_requirement_evaluated_count": 0,
        "preparation_check_count": 180,
        "failed_preparation_check_count": 0,
    }
    if any(result.get(key) != value for key, value in expected_counts.items()):
        errors.append("Phase 41 result count drift")
    zero_keys = [
        "authorization_decision_candidate_created_count",
        "authorization_decision_recorded_count",
        "authorization_granted_count",
        "authorization_token_issued_count",
        "execution_ticket_issued_count",
        "execution_run_count",
        "response_envelope_received_count",
        "reviewer_contact_count",
        "status_change_count",
        "audit_event_recorded_count",
        "human_gate_satisfied_count",
    ]
    if any(result.get(key) != 0 for key in zero_keys):
        errors.append("Phase 41 result zero-effect drift")

    authority = candidate.get("authority", {})
    permitted_key = "local_authorization_decision_candidate_preparation_readiness_permitted"
    if authority.get(permitted_key) is not True:
        errors.append("Phase 41 local readiness authority missing")
    for key, value in authority.items():
        if key in {permitted_key, "status_inheritance"}:
            continue
        if value is not False:
            errors.append(f"Phase 41 authority drift: {key}")
    if authority.get("status_inheritance") != "prohibited":
        errors.append("Phase 41 status inheritance drift")

    recovery = candidate.get("recovery", {})
    rejected = recovery.get("rejected", [])
    if (
        recovery.get("accepted_count") != 1
        or recovery.get("rejected_count") != len(rejected)
        or recovery.get("scenario_count") != len(rejected) + 1
        or len(set(rejected)) != len(rejected)
    ):
        errors.append("Phase 41 recovery drift")
    return errors

def validate() -> list[str]:
    if not CANDIDATE.is_file():
        return ["Phase 41 candidate missing"]
    if hashlib.sha256(CANDIDATE.read_bytes()).hexdigest() != EXPECTED_SHA:
        return ["Phase 41 candidate digest drift"]
    return validate_payload(load(CANDIDATE), load(SOURCE), load(SOURCE_POST))

def main() -> int:
    errors = validate()
    if errors:
        print("Phase 41 candidate errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    candidate = load(CANDIDATE)
    recovery = candidate["recovery"]["scenario_count"]
    print(
        f"Phase 41 candidate passed: sha256={EXPECTED_SHA}, "
        f"records=2, checks=180, recovery={recovery}."
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
