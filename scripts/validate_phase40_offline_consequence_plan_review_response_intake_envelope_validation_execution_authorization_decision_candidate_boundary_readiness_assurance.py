#!/usr/bin/env python3
"""Validate deterministic Phase 40 candidate-boundary readiness assurance evidence."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "release/phase-40-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance.json"
SOURCE = ROOT / "release/phase-39-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness.json"
SOURCE_POST = ROOT / "release/phase-39-postmerge.json"
EXPECTED_SHA = "a935dbfcc1758b0aab68fb358968801d2b380690a9ebcd6efdc12416d2ef58c8"
EXPECTED_STATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance-candidate"
EXPECTED_NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-candidate"
EXPECTED_DECISION = "response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assured-no-candidate-created"
EXPECTED_VERDICT = "response-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assured-no-candidate"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path)
    return value


def validate_payload(candidate: dict[str, Any], source: dict[str, Any], source_post: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if candidate.get("phase") != 40 or candidate.get("state") != EXPECTED_STATE:
        errors.append("Phase 40 identity/state drift")
    if candidate.get("next_gate") != EXPECTED_NEXT or candidate.get("decision") != EXPECTED_DECISION:
        errors.append("Phase 40 gate/decision drift")
    if candidate.get("live") is not False or candidate.get("real_authorization_claimed") is not False:
        errors.append("Phase 40 live/authorization drift")
    if candidate.get("source_phase39") != {
        "phase39_candidate_sha256": "e15063165a54ced8bbae95f4dcea9c9ff92c540135d67d3a8b10791dbc771c40",
        "phase39_finalization_commit": "7b3e7ffdfed4a70a7369dcec5620aec04228feb3",
        "phase39_postmerge_sha256": "17cab6bc36cffeb475065fe92116486fb47e8ac813a643205d0cbd18e774fea2",
    }:
        errors.append("Phase 39 source provenance drift")
    if source.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-candidate":
        errors.append("Phase 39 source state drift")
    if source_post.get("state") != "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-validated":
        errors.append("Phase 39 postmerge state drift")

    assurances = candidate.get("assurances")
    if not isinstance(assurances, list) or len(assurances) != 2:
        errors.append("Phase 40 assurance record count drift")
        return errors
    source_records = source.get("boundary_readiness_records", [])
    source_ledger = {x["entry"]["boundary_id"]: x for x in source.get("ledger", {}).get("entries", [])}
    previous = None
    expected_entries = []
    for index, (assurance, record) in enumerate(zip(assurances, source_records, strict=False), 1):
        if assurance.get("sequence") != index:
            errors.append(f"assurance {index} sequence drift")
        if assurance.get("source_boundary_id") != record.get("boundary_id"):
            errors.append(f"assurance {index} source identity drift")
        record_sha = sha_value(record)
        if assurance.get("source_boundary_record_sha256") != record_sha:
            errors.append(f"assurance {index} source digest drift")
        ledger_item = source_ledger.get(record.get("boundary_id"))
        if not ledger_item or assurance.get("source_ledger_entry_sha256") != ledger_item.get("entry_sha256"):
            errors.append(f"assurance {index} source ledger drift")
        checks = assurance.get("assurance_checks")
        if not isinstance(checks, dict) or len(checks) != 84 or set(checks.values()) != {True}:
            errors.append(f"assurance {index} checks drift")
        if assurance.get("assurance_check_count") != 84 or assurance.get("failed_assurance_check_count") != 0:
            errors.append(f"assurance {index} check counts drift")
        if assurance.get("verdict") != EXPECTED_VERDICT or assurance.get("status") != "assured-no-candidate":
            errors.append(f"assurance {index} verdict drift")
        forbidden_true = (
            "authorization_decision_candidate_created", "authorization_decision_record_created",
            "authorization_decision_recorded", "authorization_granted", "authorization_token_issued",
            "execution_run_created", "execution_ticket_issued", "response_envelope_received",
            "reviewer_identity_present", "status_change", "validation_result_recorded",
            "approval_evidence_recorded", "approval_received", "conflict_declaration_evaluated",
        )
        if any(assurance.get(k) is not False for k in forbidden_true):
            errors.append(f"assurance {index} zero-effect drift")
        if assurance.get("human_gate_satisfied_count") != 0 or assurance.get("human_gate_pending_count") != 4:
            errors.append(f"assurance {index} human-gate drift")
        entry = {
            "assurance_id": assurance.get("assurance_id"),
            "previous_entry_sha256": previous,
            "record_sha256": sha_value(assurance),
            "sequence": index,
            "source_boundary_id": assurance.get("source_boundary_id"),
            "source_ledger_entry_sha256": assurance.get("source_ledger_entry_sha256"),
            "verdict": EXPECTED_VERDICT,
        }
        entry_sha = sha_value(entry)
        expected_entries.append({"entry": entry, "entry_sha256": entry_sha})
        previous = entry_sha

    if candidate.get("ledger") != {"entries": expected_entries, "head_sequence": 2, "head_sha256": previous}:
        errors.append("Phase 40 assurance ledger drift")
    checkpoint = candidate.get("checkpoint", {})
    expected_checkpoint = {
        "assurance_check_count": 168,
        "assurance_record_count": 2,
        "authorization_decision_candidate_created_count": 0,
        "authorization_decision_recorded_count": 0,
        "authorization_granted_count": 0,
        "authorization_token_issued_count": 0,
        "execution_run_count": 0,
        "failed_assurance_check_count": 0,
        "ledger_sha256": previous,
        "response_envelope_received_count": 0,
        "status_change_count": 0,
    }
    if checkpoint != expected_checkpoint:
        errors.append("Phase 40 checkpoint drift")
    result = candidate.get("result", {})
    if result.get("assured_candidate_boundary_readiness_record_count") != 2 or result.get("assurance_check_count") != 168 or result.get("failed_assurance_check_count") != 0:
        errors.append("Phase 40 result assurance counts drift")
    zero_keys = [
        "authorization_decision_candidate_created_count", "authorization_decision_recorded_count",
        "authorization_granted_count", "authorization_token_issued_count", "execution_ticket_issued_count",
        "execution_run_count", "response_envelope_received_count", "reviewer_contact_count",
        "status_change_count", "audit_event_recorded_count", "human_gate_satisfied_count",
    ]
    if any(result.get(k) != 0 for k in zero_keys):
        errors.append("Phase 40 result zero-effect drift")
    authority = candidate.get("authority", {})
    if authority.get("local_authorization_decision_candidate_boundary_readiness_assurance_permitted") is not True:
        errors.append("Phase 40 local assurance authority missing")
    for key, value in authority.items():
        if key == "local_authorization_decision_candidate_boundary_readiness_assurance_permitted" or key == "status_inheritance":
            continue
        if value is not False:
            errors.append(f"Phase 40 authority drift: {key}")
    if authority.get("status_inheritance") != "prohibited":
        errors.append("Phase 40 status inheritance drift")
    recovery = candidate.get("recovery", {})
    if recovery.get("accepted_count") != 1 or recovery.get("rejected_count") != 209 or recovery.get("scenario_count") != 210:
        errors.append("Phase 40 recovery counts drift")
    if len(set(recovery.get("rejected", []))) != 209:
        errors.append("Phase 40 recovery labels drift")
    return errors


def validate() -> list[str]:
    if not CANDIDATE.is_file():
        return ["Phase 40 candidate missing"]
    if hashlib.sha256(CANDIDATE.read_bytes()).hexdigest() != EXPECTED_SHA:
        return ["Phase 40 candidate digest drift"]
    return validate_payload(load(CANDIDATE), load(SOURCE), load(SOURCE_POST))


def main() -> int:
    errors = validate()
    if errors:
        print("Phase 40 candidate errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Phase 40 candidate passed: sha256={EXPECTED_SHA}, assurances=2, checks=168, recovery=210.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
