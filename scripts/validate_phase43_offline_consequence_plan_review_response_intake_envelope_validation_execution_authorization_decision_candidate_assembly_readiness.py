#!/usr/bin/env python3
"""Independently validate Phase 43 candidate-assembly readiness evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "release/phase-43-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness.json"
SOURCE = ROOT / "release/phase-42-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance.json"
POSTMERGE = ROOT / "release/phase-42-postmerge.json"

MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness"
SOURCE_SHA = "6fb602bc5ef863765ceb50ba66124b843381fd15c6dac9da9250429e18e76f26"
POST_SHA = "887aa4a6c23be70b0c619c09b024e58f4321acf19ea2181bbb0f5734c1fe5cf4"
NEXT = MODE + "-assurance-candidate"


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def validate() -> list[str]:
    errors: list[str] = []
    for path, label in ((CANDIDATE, "candidate"), (SOURCE, "Phase 42 candidate"), (POSTMERGE, "Phase 42 post-merge")):
        require(errors, path.exists(), f"{label} missing")
    if errors:
        return errors

    require(errors, file_digest(SOURCE) == SOURCE_SHA, "Phase 42 candidate digest drift")
    require(errors, file_digest(POSTMERGE) == POST_SHA, "Phase 42 post-merge digest drift")
    try:
        raw = CANDIDATE.read_bytes()
        candidate = json.loads(raw)
        source = json.loads(SOURCE.read_text())
        post = json.loads(POSTMERGE.read_text())
    except json.JSONDecodeError as exc:
        return [f"JSON parse error: {exc}"]

    require(errors, raw == canonical(candidate), "candidate JSON is not canonical")
    require(errors, candidate.get("phase") == 43, "phase mismatch")
    require(errors, candidate.get("mode") == MODE, "mode mismatch")
    require(errors, candidate.get("state") == MODE + "-candidate", "state mismatch")
    require(errors, candidate.get("next_gate") == NEXT, "next gate mismatch")
    require(errors, candidate.get("live") is False, "live enabled")
    require(errors, candidate.get("live_activation_permitted") is False, "live activation enabled")
    require(errors, candidate.get("real_authorization_claimed") is False, "authorization claimed")

    require(errors, source.get("phase") == 42, "source phase mismatch")
    require(errors, source.get("next_gate") == MODE + "-candidate", "source next gate mismatch")
    require(errors, post.get("next_gate") == MODE + "-candidate", "post-merge next gate mismatch")
    require(errors, post.get("candidate_record", {}).get("sha256") == SOURCE_SHA, "post-merge source binding mismatch")

    pin = candidate.get("source_phase42", {})
    require(errors, pin.get("candidate_sha256") == SOURCE_SHA, "candidate source pin mismatch")
    require(errors, pin.get("postmerge_sha256") == POST_SHA, "post-merge source pin mismatch")
    require(errors, pin.get("assurance_record_count") == 2, "source record count mismatch")
    require(errors, pin.get("assurance_check_count") == 204, "source check count mismatch")
    require(errors, pin.get("candidate_field_plan_count") == 36, "source field-plan count mismatch")
    require(errors, pin.get("candidate_field_populated_count") == 0, "source field population changed")
    require(errors, pin.get("human_gate_pending_count") == 8, "source pending-gate count mismatch")
    require(errors, pin.get("human_gate_satisfied_count") == 0, "source human gate satisfied")

    policy = candidate.get("assembly_readiness_policy", {})
    policy_copy = dict(policy)
    policy_sha = policy_copy.pop("sha256", None)
    require(errors, policy_sha == digest(policy_copy), "policy digest mismatch")
    require(errors, len(policy.get("check_ids", [])) == 64, "check family count mismatch")
    require(errors, len(policy.get("slot_schema", [])) == 18, "slot schema count mismatch")
    require(errors, len(policy.get("stages", [])) == 16, "stage count mismatch")
    require(errors, len(policy.get("requirements", [])) == 32, "requirement count mismatch")
    require(errors, all(x.get("state") == "inactive" for x in policy.get("stages", [])), "stage activated")
    require(errors, all(x.get("state") == "unevaluated" for x in policy.get("requirements", [])), "requirement evaluated")
    for key in (
        "candidate_creation_permitted",
        "candidate_population_permitted",
        "candidate_assembly_permitted",
        "candidate_persistence_permitted",
        "candidate_submission_permitted",
    ):
        require(errors, policy.get(key) is False, f"policy enabled {key}")

    profiles = candidate.get("assembly_readiness_profiles", [])
    records = candidate.get("assembly_readiness_records", [])
    require(errors, len(profiles) == 2, "profile count mismatch")
    require(errors, len(records) == 2, "record count mismatch")

    previous = None
    ledger_entries = candidate.get("ledger", {}).get("entries", [])
    require(errors, len(ledger_entries) == 2, "ledger length mismatch")
    for sequence, (profile, record) in enumerate(zip(profiles, records), start=1):
        profile_copy = dict(profile)
        profile_sha = profile_copy.pop("sha256", None)
        require(errors, profile_sha == digest(profile_copy), f"profile {sequence} digest mismatch")
        require(errors, profile.get("sequence") == sequence, f"profile {sequence} order mismatch")
        require(errors, profile.get("assembly_permitted") is False, f"profile {sequence} assembly enabled")

        require(errors, record.get("sequence") == sequence, f"record {sequence} order mismatch")
        require(errors, record.get("profile_sha256") == profile_sha, f"record {sequence} profile binding mismatch")
        require(errors, record.get("passed_check_count") == 64, f"record {sequence} check count mismatch")
        require(errors, record.get("failed_check_count") == 0, f"record {sequence} failed checks")
        require(errors, record.get("slot_count") == 18, f"record {sequence} slot count mismatch")
        require(errors, record.get("populated_slot_count") == 0, f"record {sequence} slot populated")
        require(errors, record.get("stage_count") == 16 and record.get("active_stage_count") == 0, f"record {sequence} stage active")
        require(errors, record.get("requirement_count") == 32 and record.get("evaluated_requirement_count") == 0, f"record {sequence} requirement evaluated")
        require(errors, record.get("human_gate_pending_count") == 4, f"record {sequence} pending gates mismatch")
        require(errors, record.get("human_gate_satisfied_count") == 0, f"record {sequence} gate satisfied")
        for key in (
            "candidate_id_present",
            "candidate_body_present",
            "candidate_signature_present",
            "candidate_persisted",
            "candidate_submitted",
            "candidate_assembled",
            "decision_recorded",
            "authorization_granted",
            "authorization_token_issued",
            "execution_ticket_issued",
            "execution_run_created",
            "response_envelope_received",
            "reviewer_identity_present",
            "reviewer_contact_permitted",
            "validation_result_recorded",
            "status_change",
            "real_authorization_claimed",
        ):
            require(errors, record.get(key) is False, f"record {sequence} forbidden state active: {key}")
        require(errors, record.get("audit_event_count") == 0, f"record {sequence} audit event recorded")
        require(errors, record.get("local_only") is True, f"record {sequence} local boundary lost")

        if sequence <= len(ledger_entries):
            item = ledger_entries[sequence - 1]
            entry = item.get("entry", {})
            require(errors, entry.get("sequence") == sequence, f"ledger {sequence} order mismatch")
            require(errors, entry.get("record_sha256") == digest(record), f"ledger {sequence} record digest mismatch")
            require(errors, entry.get("previous_entry_sha256") == previous, f"ledger {sequence} previous digest mismatch")
            require(errors, item.get("entry_sha256") == digest(entry), f"ledger {sequence} entry digest mismatch")
            previous = item.get("entry_sha256")

    require(errors, candidate.get("ledger", {}).get("head_sha256") == previous, "ledger head mismatch")
    checkpoint = candidate.get("checkpoint", {})
    require(errors, checkpoint.get("check_count") == 128, "checkpoint check count mismatch")
    require(errors, checkpoint.get("failed_check_count") == 0, "checkpoint failed checks")
    require(errors, checkpoint.get("candidate_count") == 0, "checkpoint candidate created")
    require(errors, checkpoint.get("ledger_sha256") == previous, "checkpoint ledger mismatch")

    result = candidate.get("result", {})
    expected_zero = (
        "failed_assembly_check_count",
        "populated_slot_count",
        "active_stage_count",
        "evaluated_requirement_count",
        "human_gate_satisfied_count",
        "authorization_decision_candidate_count",
        "decision_record_count",
        "authorization_grant_count",
        "authorization_token_count",
        "execution_ticket_count",
        "execution_run_count",
        "response_envelope_count",
        "reviewer_identity_count",
        "reviewer_contact_count",
        "validation_result_count",
        "audit_event_count",
        "status_change_count",
    )
    require(errors, result.get("assembly_readiness_record_count") == 2, "result record count mismatch")
    require(errors, result.get("assembly_check_count") == 128, "result check count mismatch")
    require(errors, all(result.get(key) == 0 for key in expected_zero), "result zero-effect counter changed")
    require(errors, result.get("real_authorization_claimed") is False, "result authorization claimed")

    recovery = candidate.get("recovery", {})
    require(errors, recovery.get("accepted_count") == 1, "recovery baseline mismatch")
    require(errors, recovery.get("rejected_count") == 149, "recovery rejected count mismatch")
    require(errors, recovery.get("scenario_count") == 150, "recovery scenario count mismatch")

    authority = candidate.get("authority", {})
    require(errors, authority.get("local_assembly_readiness_definition_permitted") is True, "local definition authority missing")
    for key, value in authority.items():
        if key == "local_assembly_readiness_definition_permitted":
            continue
        if key == "status_inheritance":
            require(errors, value == "prohibited", "status inheritance changed")
        else:
            require(errors, value is False, f"forbidden authority enabled: {key}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Phase 43 candidate errors:")
        for error in errors:
            print(f"- {error}")
        return 1
    raw = CANDIDATE.read_bytes()
    candidate = json.loads(raw)
    print(
        "Phase 43 candidate passed: "
        f"sha256={hashlib.sha256(raw).hexdigest()}, "
        f"records={len(candidate['assembly_readiness_records'])}, "
        f"checks={candidate['checkpoint']['check_count']}, "
        f"recovery={candidate['recovery']['scenario_count']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
