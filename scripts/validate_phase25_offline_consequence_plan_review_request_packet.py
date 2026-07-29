#!/usr/bin/env python3
"""Validate Phase 25 offline review-request packet evidence and frozen authority boundaries."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_phase25_offline_consequence_plan_review_request_packet import (
    ARTIFACTS,
    AUTHORITY,
    CHECKPOINT_PATH,
    DECISION,
    EXPECTED_READINESS,
    LEDGER_PATH,
    MODE,
    NEXT_GATE,
    PENDING_HUMAN_GATES,
    RECOVERY_PATH,
    RELEASE_PATH,
    REPORT_PATH,
    SCENARIOS,
    STATE,
    build,
    doc_sha,
    file_sha_value,
    render,
    verify_sources,
)


def error(errors: list[str], code: str, message: str) -> None:
    errors.append(f"{code}: {message}")


def validate_bundle(bundle: dict[Path, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    try:
        report = bundle[REPORT_PATH]
        ledger = bundle[LEDGER_PATH]
        checkpoint = bundle[CHECKPOINT_PATH]
        recovery = bundle[RECOVERY_PATH]
        release = bundle[RELEASE_PATH]
    except KeyError as exc:
        return [f"E-P25-MISSING: missing generated artifact {exc}"]

    if report.get("contract") != "principia-offline-consequence-plan-review-request-packet-report/0.1":
        error(errors, "E-P25-CONTRACT", "report contract drift")
    if report.get("mode") != MODE or report.get("decision") != DECISION or report.get("live") is not False:
        error(errors, "E-P25-CONTRACT", "report mode, decision, or live boundary drift")
    if report.get("authority") != AUTHORITY:
        error(errors, "E-P25-AUTHORITY", "report authority drift")

    packets = report.get("packets")
    if not isinstance(packets, list):
        return errors + ["E-P25-MISSING: packets are absent"]
    if len(packets) != len(EXPECTED_READINESS):
        error(errors, "E-P25-MISSING", "packet count must equal two")
    ids = [packet.get("packet_id") for packet in packets]
    if len(ids) != len(set(ids)):
        error(errors, "E-P25-DUPLICATE", "packet identities must be unique")
    if [packet.get("sequence") for packet in packets] != list(range(1, len(packets) + 1)):
        error(errors, "E-P25-SEQUENCE", "packet sequence must be contiguous")

    expected_by_id = {
        f"principia:consequence-plan-review-request-packet:{item['key']}:{sequence:04d}": item
        for sequence, item in enumerate(EXPECTED_READINESS, start=1)
    }
    observed_ids = set(ids)
    expected_ids = set(expected_by_id)
    if observed_ids - expected_ids:
        error(errors, "E-P25-ORPHAN", "orphan packet identity")
    if expected_ids - observed_ids:
        error(errors, "E-P25-MISSING", "expected packet identity missing")

    for packet in packets:
        packet_id = packet.get("packet_id")
        expected = expected_by_id.get(packet_id)
        if expected is None:
            continue
        if packet.get("readiness_id") != expected["readiness_id"]:
            error(errors, "E-P25-READINESS", f"readiness identity drift for {packet_id}")
        if packet.get("readiness_record_sha256") != expected["readiness_record_sha256"]:
            error(errors, "E-P25-READINESS", f"readiness digest drift for {packet_id}")
        if packet.get("readiness_ledger_entry_sha256") != expected["readiness_ledger_entry_sha256"]:
            error(errors, "E-P25-READINESS", f"readiness ledger binding drift for {packet_id}")
        source_fields = (
            ("assurance_id", "E-P25-SOURCE-BINDING"),
            ("plan_id", "E-P25-SOURCE-BINDING"),
            ("plan_kind", "E-P25-SOURCE-BINDING"),
            ("plan_sha256", "E-P25-SOURCE-BINDING"),
            ("source_proposal_id", "E-P25-SOURCE-BINDING"),
            ("source_resolution_id", "E-P25-SOURCE-BINDING"),
            ("packet_kind", "E-P25-PACKET"),
            ("reviewer_role_required", "E-P25-PACKET"),
            ("review_purpose", "E-P25-PACKET"),
        )
        for field, code in source_fields:
            if packet.get(field) != expected[field]:
                error(errors, code, f"{field} drift for {packet_id}")
        if packet.get("affected_artifacts") != ARTIFACTS:
            error(errors, "E-P25-AFFECTED-SET", f"affected artifact drift for {packet_id}")
        if packet.get("packet_status") != "prepared-local-not-dispatched":
            error(errors, "E-P25-PACKET", f"packet status drift for {packet_id}")
        if packet.get("packet_prepared") is not True or packet.get("local_only") is not True:
            error(errors, "E-P25-PACKET", f"packet preparation boundary drift for {packet_id}")

        sections = packet.get("packet_sections", [])
        if len(sections) != 6:
            error(errors, "E-P25-SECTION", f"section count drift for {packet_id}")
        if [item.get("sequence") for item in sections] != list(range(1, len(sections) + 1)):
            error(errors, "E-P25-SECTION", f"section sequence drift for {packet_id}")
        if any(item.get("state") != "prepared" for item in sections):
            error(errors, "E-P25-SECTION", f"section state drift for {packet_id}")

        questions = packet.get("questions", [])
        if len(questions) != 3:
            error(errors, "E-P25-QUESTION", f"question count drift for {packet_id}")
        if [item.get("sequence") for item in questions] != list(range(1, len(questions) + 1)):
            error(errors, "E-P25-QUESTION", f"question sequence drift for {packet_id}")
        if any(item.get("response") is not None for item in questions):
            error(errors, "E-P25-RESPONSE", f"question response recorded for {packet_id}")

        gates = packet.get("human_gates", [])
        if [item.get("criterion_id") for item in gates] != PENDING_HUMAN_GATES:
            error(errors, "E-P25-HUMAN-GATE", f"human gate identity drift for {packet_id}")
        if any(item.get("state") != "pending" or item.get("evidence_ref") is not None for item in gates):
            error(errors, "E-P25-HUMAN-GATE", f"human gate state drift for {packet_id}")

        response = packet.get("response_template", {})
        if response.get("submitted") is not False:
            error(errors, "E-P25-RESPONSE", f"response submission drift for {packet_id}")
        if response.get("review_observations") != []:
            error(errors, "E-P25-RESPONSE", f"review observations must remain blank for {packet_id}")
        for field in (
            "authorization_to_start",
            "competence_attestation",
            "conflict_declaration",
            "review_recommendation",
            "reviewer_identity",
        ):
            if response.get(field) is not None:
                code = "E-P25-OUTCOME" if field == "review_recommendation" else "E-P25-RESPONSE"
                error(errors, code, f"response field {field} must remain blank for {packet_id}")

        dispatch = packet.get("dispatch", {})
        if dispatch.get("authorized") is not False or dispatch.get("dispatched") is not False:
            error(errors, "E-P25-DISPATCH", f"dispatch state drift for {packet_id}")
        for field in ("channel", "dispatched_at", "recipient", "recipient_identifier"):
            if dispatch.get(field) is not None:
                error(errors, "E-P25-DISPATCH", f"dispatch field {field} must remain blank for {packet_id}")
        if packet.get("reviewer_contact_permitted") is not False:
            error(errors, "E-P25-DISPATCH", f"reviewer contact enabled for {packet_id}")
        if packet.get("reviewer_identity") is not None:
            error(errors, "E-P25-HUMAN-GATE", f"reviewer identity fabricated for {packet_id}")
        if packet.get("competence_attestation") is not None or packet.get("conflict_declaration") is not None:
            error(errors, "E-P25-HUMAN-GATE", f"human attestations fabricated for {packet_id}")
        if packet.get("authorization_record") is not None or packet.get("real_authorization_claimed") is not False:
            error(errors, "E-P25-AUTHORIZATION", f"authorization boundary drift for {packet_id}")
        if packet.get("review_start_permitted") is not False or packet.get("review_started") is not False or packet.get("review_completed") is not False:
            error(errors, "E-P25-EXECUTION", f"review execution boundary drift for {packet_id}")
        if packet.get("outcome_selected") is not False:
            error(errors, "E-P25-OUTCOME", f"outcome selected for {packet_id}")
        if packet.get("content_change_proposed") is not False or packet.get("status_recommendation_recorded") is not False:
            error(errors, "E-P25-EFFECT", f"content or status proposal recorded for {packet_id}")
        if packet.get("effective_hold") is not False or packet.get("operational_effect") is not False or packet.get("status_change") is not False:
            error(errors, "E-P25-EFFECT", f"operational effect recorded for {packet_id}")
        if packet.get("verdict") != "packet-prepared-local-not-dispatched":
            error(errors, "E-P25-PACKET", f"verdict drift for {packet_id}")
        checks = packet.get("checks", {})
        if len(checks) != 12 or any(value is not True for value in checks.values()):
            error(errors, "E-P25-PACKET", f"packet checks drift for {packet_id}")

    summary = report.get("summary", {})
    expected_summary = {
        "effective_hold_count": 0,
        "human_authorization_count": 0,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
        "operational_effect_count": 0,
        "outcome_selected_count": 0,
        "packet_count": 2,
        "packet_dispatch_count": 0,
        "packet_local_only_count": 2,
        "packet_prepared_count": 2,
        "question_count": 6,
        "real_authorization_claimed": False,
        "response_submission_count": 0,
        "review_completed_count": 0,
        "review_started_count": 0,
        "reviewer_contact_count": 0,
        "reviewer_identity_count": 0,
        "section_count": 12,
        "status_change_count": 0,
    }
    if summary != expected_summary:
        error(errors, "E-P25-SUMMARY", "report summary drift")

    if ledger.get("authority") != AUTHORITY or ledger.get("mode") != MODE or ledger.get("decision") != DECISION:
        error(errors, "E-P25-AUTHORITY", "ledger authority or identity drift")
    entries = ledger.get("entries", [])
    if len(entries) != len(packets):
        error(errors, "E-P25-LEDGER", "ledger entry count drift")
    previous = None
    for sequence, (packet, wrapped) in enumerate(zip(packets, entries), start=1):
        entry = wrapped.get("entry", {})
        if entry.get("sequence") != sequence or entry.get("previous_entry_sha256") != previous:
            error(errors, "E-P25-LEDGER", "ledger sequence or chain drift")
        if entry.get("packet_id") != packet.get("packet_id") or entry.get("readiness_id") != packet.get("readiness_id"):
            error(errors, "E-P25-LEDGER", "ledger identity drift")
        if entry.get("packet_record_sha256") != doc_sha(packet):
            error(errors, "E-P25-LEDGER", "ledger packet digest drift")
        if wrapped.get("entry_sha256") != doc_sha(entry):
            error(errors, "E-P25-LEDGER", "ledger entry digest drift")
        previous = wrapped.get("entry_sha256")
    if ledger.get("head_sequence") != len(entries) or ledger.get("head_sha256") != previous:
        error(errors, "E-P25-LEDGER", "ledger head drift")
    if ledger.get("source_packet_report_sha256") != doc_sha(report):
        error(errors, "E-P25-LEDGER", "ledger report binding drift")

    if checkpoint.get("authority") != AUTHORITY or checkpoint.get("mode") != MODE or checkpoint.get("decision") != DECISION:
        error(errors, "E-P25-AUTHORITY", "checkpoint authority or identity drift")
    if checkpoint.get("packet_report_sha256") != doc_sha(report) or checkpoint.get("ledger_sha256") != doc_sha(ledger):
        error(errors, "E-P25-CHECKPOINT", "checkpoint digest binding drift")
    for field, expected_value in (
        ("packet_count", 2),
        ("packet_prepared_count", 2),
        ("packet_dispatch_count", 0),
        ("human_gate_pending_count", 8),
        ("human_gate_satisfied_count", 0),
        ("reviewer_identity_count", 0),
        ("reviewer_contact_count", 0),
        ("response_submission_count", 0),
        ("review_started_count", 0),
        ("review_completed_count", 0),
        ("outcome_selected_count", 0),
        ("human_authorization_count", 0),
        ("effective_hold_count", 0),
        ("operational_effect_count", 0),
        ("status_change_count", 0),
    ):
        if checkpoint.get(field) != expected_value:
            error(errors, "E-P25-CHECKPOINT", f"checkpoint {field} drift")

    if recovery.get("authority") != AUTHORITY or recovery.get("mode") != MODE or recovery.get("live") is not False:
        error(errors, "E-P25-AUTHORITY", "recovery authority or identity drift")
    expected_baseline = {
        "checkpoint_sha256": doc_sha(checkpoint),
        "ledger_sha256": doc_sha(ledger),
        "packet_report_sha256": doc_sha(report),
    }
    if recovery.get("baseline") != expected_baseline:
        error(errors, "E-P25-RECOVERY", "recovery baseline drift")
    scenarios = recovery.get("scenarios", [])
    expected_scenarios = [
        {"expected_error": code, "expected_outcome": outcome, "scenario_id": scenario}
        for scenario, outcome, code in SCENARIOS
    ]
    if scenarios != expected_scenarios:
        error(errors, "E-P25-RECOVERY", "recovery scenario matrix drift")
    if recovery.get("summary") != {
        "accepted_count": 1,
        "rejected_count": len(SCENARIOS) - 1,
        "scenario_count": len(SCENARIOS),
    }:
        error(errors, "E-P25-RECOVERY", "recovery summary drift")

    if release.get("authority") != AUTHORITY:
        error(errors, "E-P25-AUTHORITY", "release authority drift")
    if release.get("phase") != 25 or release.get("mode") != MODE or release.get("state") != STATE:
        error(errors, "E-P25-RELEASE", "release identity drift")
    if release.get("decision") != DECISION or release.get("next_gate") != NEXT_GATE:
        error(errors, "E-P25-RELEASE", "release decision or next gate drift")
    if release.get("live") is not False or release.get("live_activation_permitted") is not False:
        error(errors, "E-P25-LIVE-FROZEN", "release live boundary drift")
    if release.get("real_authorization_claimed") is not False or release.get("result") != expected_summary:
        error(errors, "E-P25-RELEASE", "release result drift")
    expected_artifacts = {
        "checkpoint": {"path": CHECKPOINT_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(checkpoint)},
        "ledger": {"path": LEDGER_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(ledger)},
        "recovery": {"path": RECOVERY_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(recovery)},
        "report": {"path": REPORT_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(report)},
    }
    if release.get("artifacts") != expected_artifacts:
        error(errors, "E-P25-RELEASE", "release artifact digest drift")
    validation = release.get("validation", {})
    if validation != {"pull_request": None, "status": "pending", "tested_head_commit": None}:
        error(errors, "E-P25-RELEASE", "candidate validation state drift")

    authority = report.get("authority", {})
    if authority.get("external_network_required") is not False:
        error(errors, "E-P25-NETWORK", "external networking enabled")
    if authority.get("atlas_call_permitted") is not False:
        error(errors, "E-P25-ATLAS", "Atlas call enabled")
    if authority.get("repository_mutation") is not False:
        error(errors, "E-P25-AUTHORITY", "repository mutation enabled")
    if authority.get("automatic_status_change") is not False or authority.get("automatic_release_action") is not False:
        error(errors, "E-P25-AUTHORITY", "automatic authority enabled")
    if authority.get("status_inheritance") != "prohibited":
        error(errors, "E-P25-AUTHORITY", "status inheritance enabled")
    return errors


def load_bundle() -> dict[Path, dict[str, Any]]:
    paths = (REPORT_PATH, LEDGER_PATH, CHECKPOINT_PATH, RECOVERY_PATH, RELEASE_PATH)
    return {path: json.loads(path.read_text(encoding="utf-8")) for path in paths}


def main() -> int:
    errors = verify_sources()
    try:
        actual = load_bundle()
        expected = build()
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"Phase 25 validation failed to load evidence: {exc}", file=sys.stderr)
        return 1
    for path, value in expected.items():
        if render(actual[path]) != render(value):
            errors.append(f"E-P25-DETERMINISM: generated file drift: {path.relative_to(ROOT)}")
    errors.extend(validate_bundle(actual))
    if errors:
        print("Phase 25 validation errors:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1
    print(
        "Phase 25 validated: 2 local-only packets, 0 dispatches, 8 pending human gates, "
        f"{len(SCENARIOS)} recovery scenarios, and no review or authority effect."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
