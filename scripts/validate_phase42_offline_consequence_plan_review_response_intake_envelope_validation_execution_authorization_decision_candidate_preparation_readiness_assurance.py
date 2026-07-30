#!/usr/bin/env python3
"""Independently validate Phase 42 candidate-preparation readiness assurance evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "release/phase-42-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance.json"
SOURCE_PATH = ROOT / "release/phase-41-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness.json"
POSTMERGE_PATH = ROOT / "release/phase-41-postmerge.json"

EXPECTED_SOURCE_SHA = "c45f148554f66bf21db03fa446475e55746086a47da0bb56841b95012be1d33b"
EXPECTED_POSTMERGE_SHA = "864ef4e905df2c5a4cc4bac1b9ebdc035211c36a8c927eec9741c45fc6f5d1b0"
EXPECTED_MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance"
EXPECTED_STATE = EXPECTED_MODE + "-candidate"
EXPECTED_DECISION = "response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assured-no-candidate-created"
EXPECTED_NEXT = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-candidate"
EXPECTED_VERDICT = "response-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assured-no-candidate"
EXPECTED_STATUS = "preparation-readiness-assured-no-candidate"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_obj(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def fail(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def validate() -> list[str]:
    errors: list[str] = []
    fail(errors, CANDIDATE_PATH.exists(), "candidate file missing")
    fail(errors, SOURCE_PATH.exists(), "Phase 41 candidate file missing")
    fail(errors, POSTMERGE_PATH.exists(), "Phase 41 post-merge file missing")
    if errors:
        return errors

    raw = CANDIDATE_PATH.read_bytes()
    source_raw = SOURCE_PATH.read_bytes()
    post_raw = POSTMERGE_PATH.read_bytes()
    fail(errors, sha256_bytes(source_raw) == EXPECTED_SOURCE_SHA, "Phase 41 candidate digest drift")
    fail(errors, sha256_bytes(post_raw) == EXPECTED_POSTMERGE_SHA, "Phase 41 post-merge digest drift")

    try:
        candidate = json.loads(raw)
        source = json.loads(source_raw)
        postmerge = json.loads(post_raw)
    except json.JSONDecodeError as exc:
        return [f"JSON parse error: {exc}"]

    fail(errors, raw == canonical_bytes(candidate), "candidate JSON is not canonical")
    fail(errors, candidate.get("phase") == 42, "phase mismatch")
    fail(errors, candidate.get("mode") == EXPECTED_MODE, "mode mismatch")
    fail(errors, candidate.get("state") == EXPECTED_STATE, "state mismatch")
    fail(errors, candidate.get("decision") == EXPECTED_DECISION, "decision mismatch")
    fail(errors, candidate.get("next_gate") == EXPECTED_NEXT, "next gate mismatch")
    fail(errors, candidate.get("live") is False, "live must remain false")
    fail(errors, candidate.get("live_activation_permitted") is False, "live activation must remain disabled")
    fail(errors, candidate.get("real_authorization_claimed") is False, "real authorization must remain unclaimed")

    source_pin = candidate.get("source_phase41", {})
    fail(errors, source_pin.get("phase41_candidate_sha256") == EXPECTED_SOURCE_SHA, "source candidate pin mismatch")
    fail(errors, source_pin.get("phase41_postmerge_sha256") == EXPECTED_POSTMERGE_SHA, "source post-merge pin mismatch")
    fail(errors, source_pin.get("phase41_candidate_head_commit") == "4700bd61823d66b2296b9513ad7f564d84bb0e73", "source candidate head mismatch")
    fail(errors, source_pin.get("phase41_candidate_merge_commit") == "25073fd7765a9faf3f53235cded3356839861917", "source candidate merge mismatch")
    fail(errors, source_pin.get("phase41_finalization_commit") == "e819d08d6dac4ec6fba0943bf8ec0c1e55da01a5", "source finalization commit mismatch")
    fail(errors, source_pin.get("phase41_applicable_workflows") == 35, "source workflow count mismatch")
    fail(errors, source_pin.get("phase41_ledger_head_sha256") == source["ledger"]["head_sha256"], "source ledger head binding mismatch")
    fail(errors, source_pin.get("phase41_checkpoint_sha256") == sha256_obj(source["checkpoint"]), "source checkpoint binding mismatch")
    fail(errors, source_pin.get("phase41_result_sha256") == sha256_obj(source["result"]), "source result binding mismatch")
    fail(errors, source_pin.get("phase41_postmerge_state") == postmerge["state"], "source post-merge state mismatch")

    policy = candidate.get("candidate_preparation_readiness_assurance_policy", {})
    policy_copy = dict(policy)
    policy_digest = policy_copy.pop("assurance_policy_sha256", None)
    fail(errors, policy_digest == sha256_obj(policy_copy), "assurance policy digest mismatch")
    fail(errors, policy.get("candidate_materialization_permitted") is False, "candidate materialization unexpectedly permitted")
    fail(errors, policy.get("candidate_population_permitted") is False, "candidate population unexpectedly permitted")
    fail(errors, policy.get("candidate_assembly_permitted") is False, "candidate assembly unexpectedly permitted")
    fail(errors, len(policy.get("assurance_requirements", [])) == 102, "assurance requirement count mismatch")
    fail(errors, all(x.get("state") == "defined" for x in policy.get("assurance_requirements", [])), "assurance requirements must remain defined-only")

    source_records = source["candidate_preparation_readiness_records"]
    source_by_id = {r["preparation_id"]: r for r in source_records}
    source_ledger = {
        item["entry"]["preparation_id"]: item
        for item in source["ledger"]["entries"]
    }
    records = candidate.get("candidate_preparation_readiness_assurance_records", [])
    fail(errors, len(records) == 2, "assurance record count mismatch")
    previous = None
    ledger_entries = candidate.get("ledger", {}).get("entries", [])
    fail(errors, len(ledger_entries) == len(records), "ledger entry count mismatch")

    for index, record in enumerate(records, start=1):
        rid = record.get("source_preparation_id")
        fail(errors, record.get("sequence") == index, f"record {index} sequence mismatch")
        fail(errors, rid in source_by_id, f"record {index} source preparation missing")
        if rid not in source_by_id:
            continue
        src = source_by_id[rid]
        src_ledger = source_ledger[rid]
        fail(errors, record.get("source_preparation_record_sha256") == src_ledger["entry"]["record_sha256"], f"record {index} source record digest mismatch")
        fail(errors, record.get("source_ledger_entry_sha256") == src_ledger["entry_sha256"], f"record {index} source ledger digest mismatch")
        fail(errors, record.get("source_verdict") == src["verdict"], f"record {index} source verdict mismatch")
        fail(errors, record.get("source_status") == src["status"], f"record {index} source status mismatch")
        fail(errors, record.get("preparation_policy_id") == src["preparation_policy_id"], f"record {index} preparation policy mismatch")
        fail(errors, record.get("preparation_policy_sha256") == src["preparation_policy_sha256"], f"record {index} preparation policy digest mismatch")
        fail(errors, record.get("preparation_profile") == src["preparation_profile"], f"record {index} preparation profile mismatch")
        fail(errors, record.get("preparation_profile_sha256") == src["preparation_profile_sha256"], f"record {index} preparation profile digest mismatch")
        fail(errors, record.get("candidate_field_plan") == src["candidate_field_plan"], f"record {index} field plan mismatch")
        fail(errors, record.get("candidate_field_plan_sha256") == src["candidate_field_plan_sha256"], f"record {index} field plan digest mismatch")
        fail(errors, record.get("candidate_field_plan_count") == 18, f"record {index} field plan count mismatch")
        fail(errors, record.get("candidate_field_populated_count") == 0, f"record {index} populated field count changed")
        fail(errors, all(x.get("state") == "unpopulated" for x in record.get("candidate_field_plan", [])), f"record {index} field plan populated")
        fail(errors, all(x.get("population_permitted") is False for x in record.get("candidate_field_plan", [])), f"record {index} field population permitted")
        checks = record.get("assurance_checks", {})
        fail(errors, record.get("assurance_check_count") == 102, f"record {index} check count mismatch")
        fail(errors, len(checks) == 102, f"record {index} check map size mismatch")
        fail(errors, all(value is True for value in checks.values()), f"record {index} assurance check failed")
        fail(errors, record.get("failed_assurance_check_count") == 0, f"record {index} failed assurance count changed")
        fail(errors, record.get("human_gate_pending_count") == 4, f"record {index} pending gates mismatch")
        fail(errors, record.get("human_gate_satisfied_count") == 0, f"record {index} human gate satisfied")
        for key in [
            "approval_evidence_recorded", "approval_received", "conflict_declaration_evaluated",
            "rationale_populated", "proposed_decision_selected", "validity_window_active",
            "revocation_reference_present", "candidate_id_present", "candidate_signature_present",
            "candidate_assembly_permitted", "authorization_decision_candidate_created",
            "authorization_decision_record_created", "authorization_decision_recorded",
            "authorization_granted", "authorization_token_issued", "execution_ticket_issued",
            "execution_run_created", "response_envelope_received", "reviewer_identity_present",
            "reviewer_contact_permitted", "validation_result_recorded", "disposition_selected",
            "status_change", "real_authorization_claimed",
        ]:
            fail(errors, record.get(key) is False, f"record {index} forbidden state active: {key}")
        fail(errors, record.get("audit_event_recorded_count") == 0, f"record {index} audit event recorded")
        fail(errors, record.get("local_only") is True, f"record {index} local-only boundary lost")
        fail(errors, record.get("status") == EXPECTED_STATUS, f"record {index} status mismatch")
        fail(errors, record.get("verdict") == EXPECTED_VERDICT, f"record {index} verdict mismatch")

        if index <= len(ledger_entries):
            item = ledger_entries[index - 1]
            entry = item.get("entry", {})
            fail(errors, entry.get("sequence") == index, f"ledger {index} sequence mismatch")
            fail(errors, entry.get("assurance_id") == record.get("assurance_id"), f"ledger {index} assurance id mismatch")
            fail(errors, entry.get("record_sha256") == sha256_obj(record), f"ledger {index} record digest mismatch")
            fail(errors, entry.get("previous_entry_sha256") == previous, f"ledger {index} previous digest mismatch")
            fail(errors, item.get("entry_sha256") == sha256_obj(entry), f"ledger {index} entry digest mismatch")
            previous = item.get("entry_sha256")

    fail(errors, candidate.get("ledger", {}).get("head_sequence") == 2, "ledger head sequence mismatch")
    fail(errors, candidate.get("ledger", {}).get("head_sha256") == previous, "ledger head digest mismatch")

    checkpoint = candidate.get("checkpoint", {})
    fail(errors, checkpoint.get("assurance_record_count") == 2, "checkpoint record count mismatch")
    fail(errors, checkpoint.get("assurance_check_count") == 204, "checkpoint check count mismatch")
    fail(errors, checkpoint.get("failed_assurance_check_count") == 0, "checkpoint failed check count mismatch")
    fail(errors, checkpoint.get("candidate_field_populated_count") == 0, "checkpoint populated fields changed")
    fail(errors, checkpoint.get("ledger_sha256") == previous, "checkpoint ledger digest mismatch")

    result = candidate.get("result", {})
    fail(errors, result.get("candidate_preparation_readiness_assurance_record_count") == 2, "result assurance record count mismatch")
    fail(errors, result.get("candidate_preparation_readiness_assurance_check_count") == 204, "result assurance check count mismatch")
    fail(errors, result.get("failed_candidate_preparation_readiness_assurance_check_count") == 0, "result failed assurance count mismatch")
    for key in [
        "candidate_field_populated_count", "authorization_decision_candidate_created_count",
        "authorization_decision_record_created_count", "authorization_decision_recorded_count",
        "authorization_granted_count", "authorization_token_issued_count", "execution_ticket_issued_count",
        "execution_run_count", "response_envelope_received_count", "reviewer_contact_count",
        "status_change_count", "audit_event_recorded_count", "human_gate_satisfied_count",
    ]:
        fail(errors, result.get(key) == 0, f"result zero-effect counter changed: {key}")
    fail(errors, result.get("human_gate_pending_count") == 8, "result pending gates mismatch")
    fail(errors, result.get("real_authorization_claimed") is False, "result authorization claim changed")

    recovery = candidate.get("recovery", {})
    fail(errors, recovery.get("accepted_count") == 1, "recovery accepted count mismatch")
    fail(errors, recovery.get("rejected_count") == 225, "recovery rejected count mismatch")
    fail(errors, recovery.get("scenario_count") == 226, "recovery scenario count mismatch")
    fail(errors, len(recovery.get("rejected", [])) == 225, "recovery rejected list size mismatch")

    authority = candidate.get("authority", {})
    fail(errors, authority.get("local_authorization_decision_candidate_preparation_readiness_assurance_permitted") is True, "local assurance authority missing")
    for key, value in authority.items():
        if key == "local_authorization_decision_candidate_preparation_readiness_assurance_permitted":
            continue
        if key == "status_inheritance":
            fail(errors, value == "prohibited", "status inheritance boundary changed")
        elif key == "human_authorization_claimed":
            fail(errors, value is False, "human authorization claimed")
        else:
            fail(errors, value is False, f"forbidden authority enabled: {key}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Phase 42 candidate errors:")
        for error in errors:
            print(f"- {error}")
        return 1
    raw = CANDIDATE_PATH.read_bytes()
    candidate = json.loads(raw)
    print(
        "Phase 42 candidate passed: "
        f"sha256={sha256_bytes(raw)}, assurances={len(candidate['candidate_preparation_readiness_assurance_records'])}, "
        f"checks={candidate['checkpoint']['assurance_check_count']}, recovery={candidate['recovery']['scenario_count']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
