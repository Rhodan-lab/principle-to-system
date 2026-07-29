#!/usr/bin/env python3
"""Validate Phase 24 consequence-plan review-readiness evidence and boundaries."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import generate_phase24_offline_consequence_plan_review_readiness as gen  # noqa: E402

REPORT_MD_PATH = ROOT / "reports/phase-24-offline-consequence-plan-review-readiness.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-24-offline-consequence-plan-review-readiness.yml"


class ValidationError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValidationError(code)


def validate_authority(value: Any) -> None:
    require(value == gen.AUTHORITY, "E-P24-AUTHORITY")


def validate_phase23_source() -> list[Mapping[str, Any]]:
    source = load(gen.PILOT / "thermal-control.consequence-plan-assurance-report.v01.json")
    require(source.get("contract") == "principia-offline-consequence-plan-assurance-report/0.1", "E-P24-SOURCE-PIN")
    require(source.get("decision") == "consequence-plans-assured-no-execution", "E-P24-SOURCE-PIN")
    require(source.get("live") is False, "E-P24-SOURCE-PIN")
    assessments = source.get("assessments")
    require(isinstance(assessments, list) and len(assessments) == 2, "E-P24-SOURCE-PIN")
    for sequence, (actual, expected) in enumerate(zip(assessments, gen.EXPECTED_ASSURANCES), start=1):
        require(actual == gen.source_assessment(expected, sequence), "E-P24-ASSURANCE")
    return assessments


def validate_criteria(criteria: Any, expected: Mapping[str, Any]) -> None:
    require(criteria == gen.criteria_for(dict(expected)), "E-P24-CRITERIA")
    require(len(criteria) == 8, "E-P24-CRITERIA")
    machine = criteria[:4]
    human = criteria[4:]
    require(all(item["category"] == "machine" and item["state"] == "satisfied" and item["evidence_ref"] for item in machine), "E-P24-CRITERIA")
    require(all(item["category"] == "human" and item["state"] == "pending" and item["evidence_ref"] is None for item in human), "E-P24-HUMAN-GATE")


def validate_record(record: Mapping[str, Any], source_assessment: Mapping[str, Any], expected: Mapping[str, Any], sequence: int) -> None:
    require(record.get("sequence") == sequence, "E-P24-SEQUENCE")
    require(record.get("readiness_id") == expected["readiness_id"], "E-P24-DUPLICATE")
    require(record.get("assurance_id") == expected["assurance_id"], "E-P24-ASSURANCE")
    require(record.get("assurance_record_sha256") == gen.doc_sha(source_assessment), "E-P24-ASSURANCE")
    require(record.get("plan_id") == expected["plan_id"], "E-P24-PLAN")
    require(record.get("plan_kind") == expected["plan_kind"], "E-P24-PLAN")
    require(record.get("plan_sha256") == expected["plan_sha256"], "E-P24-PLAN")
    require(record.get("source_ledger_entry_sha256") == expected["source_ledger_entry_sha256"], "E-P24-SOURCE-BINDING")
    require(record.get("source_proposal_id") == expected["source_proposal_id"], "E-P24-SOURCE-BINDING")
    require(record.get("source_resolution_id") == expected["source_resolution_id"], "E-P24-SOURCE-BINDING")
    require(record.get("affected_artifacts") == gen.ARTIFACTS, "E-P24-AFFECTED-SET")
    require(record.get("reviewer_role_required") == expected["reviewer_role_required"], "E-P24-HUMAN-GATE")
    require(record.get("review_purpose") == expected["review_purpose"], "E-P24-CRITERIA")
    require(record.get("checks") == gen.CHECKS and all(record["checks"].values()), "E-P24-CHECKS")
    validate_criteria(record.get("criteria"), expected)

    require(record.get("machine_ready") is True, "E-P24-CRITERIA")
    require(record.get("human_ready") is False, "E-P24-HUMAN-GATE")
    require(record.get("readiness_status") == "machine-ready-human-gates-pending", "E-P24-HUMAN-GATE")
    require(record.get("verdict") == "readiness-defined-review-not-authorized", "E-P24-VERDICT")

    for field in ("reviewer_identity", "competence_attestation", "conflict_declaration"):
        require(record.get(field) is None, "E-P24-HUMAN-GATE")
    require(record.get("authorization_record") is None, "E-P24-AUTHORIZATION")
    require(record.get("review_request_packet_preparation_permitted") is True, "E-P24-CRITERIA")
    require(record.get("review_request_dispatch_permitted") is False, "E-P24-DISPATCH")
    require(record.get("review_request_dispatched") is False, "E-P24-DISPATCH")
    require(record.get("review_start_permitted") is False, "E-P24-EXECUTION")
    require(record.get("review_started") is False, "E-P24-EXECUTION")
    require(record.get("review_completed") is False, "E-P24-EXECUTION")
    require(record.get("outcome_selected") is False, "E-P24-OUTCOME")
    for field in ("content_change_proposed", "effective_hold", "operational_effect", "status_change", "status_recommendation_recorded"):
        require(record.get(field) is False, "E-P24-EFFECT")
    require(record.get("real_authorization_claimed") is False, "E-P24-AUTHORIZATION")


def expected_summary() -> dict[str, Any]:
    return {
        "effective_hold_count": 0,
        "human_authorization_count": 0,
        "human_ready_count": 0,
        "machine_ready_count": 2,
        "operational_effect_count": 0,
        "outcome_selected_count": 0,
        "plan_count": 2,
        "readiness_record_count": 2,
        "real_authorization_claimed": False,
        "review_completed_count": 0,
        "review_request_dispatch_count": 0,
        "review_request_packet_preparation_count": 2,
        "review_started_count": 0,
        "status_change_count": 0,
        "unmet_human_gate_count": 8,
    }


def validate_report(report: Mapping[str, Any], source_assessments: list[Mapping[str, Any]]) -> None:
    expected_top = {
        "contract": "principia-offline-consequence-plan-review-readiness-report/0.1",
        "decision": gen.DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "mode": gen.MODE,
        "source": gen.SOURCE,
    }
    for key, value in expected_top.items():
        if report.get(key) != value:
            raise ValidationError("E-P24-LIVE-FROZEN" if key == "live" else "E-P24-SOURCE-PIN" if key == "source" else "E-P24-CONTRACT")
    validate_authority(report.get("authority"))
    records = report.get("readiness_records")
    require(isinstance(records, list), "E-P24-MISSING")
    require(len(records) >= 2, "E-P24-MISSING")
    require(len(records) <= 2, "E-P24-ORPHAN")
    seen: set[str] = set()
    for sequence, (record, source_assessment, expected) in enumerate(zip(records, source_assessments, gen.EXPECTED_ASSURANCES), start=1):
        require(isinstance(record, Mapping), "E-P24-SHAPE")
        readiness_id = record.get("readiness_id")
        require(isinstance(readiness_id, str) and readiness_id not in seen, "E-P24-DUPLICATE")
        seen.add(readiness_id)
        validate_record(record, source_assessment, expected, sequence)
    require(report.get("summary") == expected_summary(), "E-P24-SUMMARY")


def validate_ledger(ledger: Mapping[str, Any], report: Mapping[str, Any]) -> None:
    validate_authority(ledger.get("authority"))
    require(ledger.get("contract") == "principia-offline-consequence-plan-review-readiness-ledger/0.1", "E-P24-LEDGER")
    require(ledger.get("decision") == gen.DECISION and ledger.get("mode") == gen.MODE and ledger.get("live") is False, "E-P24-LEDGER")
    require(ledger.get("source_readiness_report_sha256") == gen.doc_sha(report), "E-P24-LEDGER")
    entries = ledger.get("entries")
    records = report["readiness_records"]
    require(isinstance(entries, list) and len(entries) == 2, "E-P24-LEDGER")
    previous = None
    for sequence, (wrapper, record) in enumerate(zip(entries, records), start=1):
        require(isinstance(wrapper, Mapping), "E-P24-LEDGER")
        entry = wrapper.get("entry")
        digest = wrapper.get("entry_sha256")
        require(isinstance(entry, Mapping) and digest == gen.doc_sha(entry), "E-P24-LEDGER")
        require(entry.get("sequence") == sequence and entry.get("previous_entry_sha256") == previous, "E-P24-LEDGER")
        require(entry.get("readiness_id") == record.get("readiness_id"), "E-P24-LEDGER")
        require(entry.get("assurance_id") == record.get("assurance_id"), "E-P24-LEDGER")
        require(entry.get("plan_id") == record.get("plan_id"), "E-P24-LEDGER")
        require(entry.get("readiness_record_sha256") == gen.doc_sha(record), "E-P24-LEDGER")
        require(entry.get("verdict") == record.get("verdict"), "E-P24-LEDGER")
        previous = digest
    require(ledger.get("head_sequence") == 2 and ledger.get("head_sha256") == previous, "E-P24-LEDGER")


def validate_checkpoint(checkpoint: Mapping[str, Any], report: Mapping[str, Any], ledger: Mapping[str, Any]) -> None:
    validate_authority(checkpoint.get("authority"))
    require(checkpoint.get("contract") == "principia-offline-consequence-plan-review-readiness-checkpoint/0.1", "E-P24-CHECKPOINT")
    expected = {
        "decision": gen.DECISION,
        "effective_hold_count": 0,
        "human_authorization_count": 0,
        "human_ready_count": 0,
        "ledger_sha256": gen.doc_sha(ledger),
        "live": False,
        "machine_ready_count": 2,
        "mode": gen.MODE,
        "operational_effect_count": 0,
        "outcome_selected_count": 0,
        "plan_count": 2,
        "readiness_record_count": 2,
        "readiness_report_sha256": gen.doc_sha(report),
        "real_authorization_claimed": False,
        "review_completed_count": 0,
        "review_request_dispatch_count": 0,
        "review_started_count": 0,
        "status_change_count": 0,
        "unmet_human_gate_count": 8,
    }
    for key, value in expected.items():
        require(checkpoint.get(key) == value, "E-P24-CHECKPOINT")


def validate_recovery(recovery: Mapping[str, Any], report: Mapping[str, Any], ledger: Mapping[str, Any], checkpoint: Mapping[str, Any]) -> None:
    validate_authority(recovery.get("authority"))
    require(recovery.get("contract") == "principia-offline-consequence-plan-review-readiness-recovery/0.1", "E-P24-RECOVERY")
    require(recovery.get("mode") == gen.MODE and recovery.get("live") is False, "E-P24-RECOVERY")
    require(recovery.get("baseline") == {
        "checkpoint_sha256": gen.doc_sha(checkpoint),
        "ledger_sha256": gen.doc_sha(ledger),
        "readiness_report_sha256": gen.doc_sha(report),
    }, "E-P24-RECOVERY")
    require(recovery.get("scenarios") == [
        {"expected_error": error, "expected_outcome": outcome, "scenario_id": scenario}
        for scenario, outcome, error in gen.SCENARIOS
    ], "E-P24-RECOVERY")
    require(recovery.get("summary") == {"accepted_count": 1, "rejected_count": 44, "scenario_count": 45}, "E-P24-RECOVERY")


def validate_release(release: Mapping[str, Any], bundle: Mapping[Path, Mapping[str, Any]]) -> None:
    validate_authority(release.get("authority"))
    expected = {
        "contract": "principia-offline-consequence-plan-review-readiness/0.1",
        "decision": gen.DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "live_activation_permitted": False,
        "mode": gen.MODE,
        "next_gate": "offline-consequence-plan-review-request-packet-candidate",
        "phase": 24,
        "real_authorization_claimed": False,
        "source_phase23": gen.SOURCE,
        "state": "offline-consequence-plan-review-readiness-candidate",
        "result": expected_summary(),
        "validation": {"pull_request": None, "status": "pending", "tested_head_commit": None},
    }
    for key, value in expected.items():
        if release.get(key) != value:
            raise ValidationError("E-P24-LIVE-FROZEN" if key in {"live", "live_activation_permitted"} else "E-P24-SOURCE-PIN" if key == "source_phase23" else "E-P24-RELEASE")
    for name, path in {
        "report": gen.REPORT_PATH,
        "ledger": gen.LEDGER_PATH,
        "checkpoint": gen.CHECKPOINT_PATH,
        "recovery": gen.RECOVERY_PATH,
    }.items():
        require(release.get("artifacts", {}).get(name) == {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": gen.file_sha_value(bundle[path]),
        }, "E-P24-RELEASE")


def validate_bundle(bundle: Mapping[Path, Mapping[str, Any]]) -> None:
    report = bundle[gen.REPORT_PATH]
    ledger = bundle[gen.LEDGER_PATH]
    checkpoint = bundle[gen.CHECKPOINT_PATH]
    recovery = bundle[gen.RECOVERY_PATH]
    release = bundle[gen.RELEASE_PATH]
    source_assessments = validate_phase23_source()
    validate_report(report, source_assessments)
    validate_ledger(ledger, report)
    validate_checkpoint(checkpoint, report, ledger)
    validate_recovery(recovery, report, ledger, checkpoint)
    validate_release(release, bundle)


def validate_documentation() -> None:
    require(REPORT_MD_PATH.is_file(), "E-P24-DOCUMENTATION")
    require(WORKFLOW_PATH.is_file(), "E-P24-WORKFLOW")
    report_text = REPORT_MD_PATH.read_text(encoding="utf-8")
    for marker in (
        "machine-ready-human-gates-pending",
        "review-readiness-recorded-no-review-started",
        "review_request_dispatch_permitted: false",
        "review_start_permitted: false",
        "human_authorization_count: 0",
        "external_network_required: false",
        "atlas_call_permitted: false",
    ):
        require(marker in report_text, "E-P24-DOCUMENTATION")
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    require("contents: read" in workflow_text, "E-P24-WORKFLOW")
    for token in ("contents: write", "pull_request_target", "git push", "git commit", "curl ", "wget ", "repository: Rhodan-lab/Atlas"):
        require(token not in workflow_text, "E-P24-WORKFLOW")


def main() -> int:
    errors: list[str] = []
    for path, expected in gen.SOURCE_FILES.items():
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"E-P24-SOURCE-PIN: {path.relative_to(ROOT)}")
    try:
        built = gen.build()
        validate_bundle(built)
        for path, value in built.items():
            if not path.is_file() or path.read_text(encoding="utf-8") != gen.render(value):
                errors.append(f"generated file drift: {path.relative_to(ROOT)}")
        validate_documentation()
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValidationError, ValueError) as exc:
        errors.append(str(exc))
    if errors:
        print("Phase 24 validation errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Phase 24 review-readiness evidence is valid, deterministic, non-executing, and authority-bounded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
