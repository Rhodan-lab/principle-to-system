#!/usr/bin/env python3
"""Validate Phase 26 review-request packet assurance evidence and authority boundaries."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import generate_phase26_offline_consequence_plan_review_request_packet_assurance as gen  # noqa: E402

REPORT_MD_PATH = ROOT / "reports/phase-26-offline-consequence-plan-review-request-packet-assurance.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-26-offline-consequence-plan-review-request-packet-assurance.yml"


class ValidationError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def require_authority(value: Any) -> None:
    if value != gen.AUTHORITY:
        raise ValidationError("E-P26-AUTHORITY")


def validate_report(report: Mapping[str, Any]) -> None:
    expected_top = {
        "contract": "principia-offline-consequence-plan-review-request-packet-assurance-report/0.1",
        "decision": gen.DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "mode": gen.MODE,
        "source_phase25": gen.SOURCE,
    }
    for key, expected in expected_top.items():
        if report.get(key) != expected:
            if key == "live":
                raise ValidationError("E-P26-LIVE-FROZEN")
            if key == "source_phase25":
                raise ValidationError("E-P26-SOURCE-PIN")
            raise ValidationError("E-P26-CONTRACT")
    require_authority(report.get("authority"))
    assurances = report.get("assurances")
    if not isinstance(assurances, list):
        raise ValidationError("E-P26-MISSING")
    if len(assurances) < 2:
        raise ValidationError("E-P26-MISSING")
    if len(assurances) > 2:
        raise ValidationError("E-P26-ORPHAN")

    expected_checks = {
        "affected_artifact_set_exact",
        "authority_boundary_preserved",
        "blank_question_responses_preserved",
        "blank_response_template_preserved",
        "dispatch_disabled",
        "human_gates_remain_pending",
        "ledger_entry_binding_exact",
        "local_only_state_preserved",
        "packet_identity_exact",
        "packet_record_digest_exact",
        "packet_sections_complete",
        "question_structure_complete",
        "review_execution_disabled",
        "reviewer_unidentified",
        "source_binding_exact",
        "zero_effect_boundary_preserved",
    }
    seen: set[str] = set()
    for sequence, (assurance, expected) in enumerate(zip(assurances, gen.EXPECTED_PACKETS), start=1):
        if not isinstance(assurance, Mapping):
            raise ValidationError("E-P26-SHAPE")
        assurance_id = assurance.get("packet_assurance_id")
        if not isinstance(assurance_id, str) or assurance_id in seen:
            raise ValidationError("E-P26-DUPLICATE")
        seen.add(assurance_id)
        if assurance.get("sequence") != sequence:
            raise ValidationError("E-P26-SEQUENCE")
        for key in (
            "packet_assurance_id", "packet_id", "packet_kind", "packet_record_sha256",
            "packet_ledger_entry_sha256", "readiness_id", "plan_id", "reviewer_role_required",
        ):
            if assurance.get(key) != expected[key]:
                if key in ("packet_id", "packet_record_sha256", "packet_ledger_entry_sha256", "readiness_id"):
                    raise ValidationError("E-P26-PACKET-BINDING")
                raise ValidationError("E-P26-SOURCE-BINDING")
        if assurance.get("affected_artifacts") != gen.ARTIFACTS:
            raise ValidationError("E-P26-SOURCE-BINDING")
        checks = assurance.get("assurance_checks")
        if not isinstance(checks, Mapping) or set(checks) != expected_checks or not all(v is True for v in checks.values()):
            raise ValidationError("E-P26-ASSURANCE")
        for key, expected_value, code in (
            ("section_count", 6, "E-P26-SECTION"),
            ("question_count", 3, "E-P26-QUESTION"),
            ("blank_question_response_count", 3, "E-P26-QUESTION"),
            ("human_gate_pending_count", 4, "E-P26-HUMAN-GATE"),
            ("human_gate_satisfied_count", 0, "E-P26-HUMAN-GATE"),
            ("response_submission_count", 0, "E-P26-RESPONSE"),
        ):
            if assurance.get(key) != expected_value:
                raise ValidationError(code)
        if assurance.get("packet_status") != "prepared-local-not-dispatched":
            raise ValidationError("E-P26-PACKET-STATE")
        if assurance.get("verdict") != "packet-assured-local-no-dispatch":
            raise ValidationError("E-P26-ASSURANCE")
        if assurance.get("packet_prepared") is not True or assurance.get("local_only") is not True:
            raise ValidationError("E-P26-PACKET-STATE")
        for key, code in (
            ("dispatch_permitted", "E-P26-DISPATCH"),
            ("response_template_submitted", "E-P26-RESPONSE"),
            ("review_start_permitted", "E-P26-EXECUTION"),
            ("review_started", "E-P26-EXECUTION"),
            ("review_completed", "E-P26-EXECUTION"),
            ("reviewer_contact_permitted", "E-P26-CONTACT"),
            ("reviewer_identity_present", "E-P26-RESPONSE"),
            ("outcome_selected", "E-P26-OUTCOME"),
            ("effective_hold", "E-P26-EFFECT"),
            ("operational_effect", "E-P26-EFFECT"),
            ("status_change", "E-P26-EFFECT"),
            ("human_authorization_claimed", "E-P26-AUTHORIZATION"),
            ("real_authorization_claimed", "E-P26-AUTHORIZATION"),
        ):
            if assurance.get(key) is not False:
                raise ValidationError(code)

    expected_summary = {
        "assured_packet_count": 2,
        "blank_question_response_count": 6,
        "effective_hold_count": 0,
        "failed_assurance_count": 0,
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
    if report.get("summary") != expected_summary:
        raise ValidationError("E-P26-SUMMARY")


def validate_bundle(bundle: Mapping[Path, Mapping[str, Any]]) -> None:
    report = bundle[gen.REPORT_PATH]
    ledger = bundle[gen.LEDGER_PATH]
    checkpoint = bundle[gen.CHECKPOINT_PATH]
    recovery = bundle[gen.RECOVERY_PATH]
    release = bundle[gen.RELEASE_PATH]
    validate_report(report)

    require_authority(ledger.get("authority"))
    if ledger.get("contract") != "principia-offline-consequence-plan-review-request-packet-assurance-ledger/0.1":
        raise ValidationError("E-P26-LEDGER")
    entries = ledger.get("entries")
    assurances = report["assurances"]
    if not isinstance(entries, list) or len(entries) != 2:
        raise ValidationError("E-P26-LEDGER")
    previous = None
    for sequence, (wrapper, assurance) in enumerate(zip(entries, assurances), start=1):
        if not isinstance(wrapper, Mapping):
            raise ValidationError("E-P26-LEDGER")
        entry = wrapper.get("entry")
        digest = wrapper.get("entry_sha256")
        if not isinstance(entry, Mapping) or gen.doc_sha(entry) != digest:
            raise ValidationError("E-P26-LEDGER")
        if entry.get("sequence") != sequence or entry.get("previous_entry_sha256") != previous:
            raise ValidationError("E-P26-LEDGER")
        if entry.get("packet_assurance_id") != assurance.get("packet_assurance_id"):
            raise ValidationError("E-P26-LEDGER")
        if entry.get("packet_assurance_sha256") != gen.doc_sha(assurance):
            raise ValidationError("E-P26-LEDGER")
        if entry.get("packet_id") != assurance.get("packet_id"):
            raise ValidationError("E-P26-LEDGER")
        previous = digest
    if ledger.get("head_sequence") != 2 or ledger.get("head_sha256") != previous:
        raise ValidationError("E-P26-LEDGER")
    if ledger.get("source_assurance_report_sha256") != gen.doc_sha(report):
        raise ValidationError("E-P26-LEDGER")

    require_authority(checkpoint.get("authority"))
    if checkpoint.get("contract") != "principia-offline-consequence-plan-review-request-packet-assurance-checkpoint/0.1":
        raise ValidationError("E-P26-CHECKPOINT")
    expected_checkpoint = {
        "assurance_report_sha256": gen.doc_sha(report),
        "assured_packet_count": 2,
        "effective_hold_count": 0,
        "failed_assurance_count": 0,
        "human_authorization_count": 0,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
        "ledger_sha256": gen.doc_sha(ledger),
        "operational_effect_count": 0,
        "outcome_selected_count": 0,
        "packet_count": 2,
        "packet_dispatch_count": 0,
        "real_authorization_claimed": False,
        "response_submission_count": 0,
        "review_completed_count": 0,
        "review_started_count": 0,
        "reviewer_contact_count": 0,
        "reviewer_identity_count": 0,
        "status_change_count": 0,
    }
    for key, expected in expected_checkpoint.items():
        if checkpoint.get(key) != expected:
            raise ValidationError("E-P26-CHECKPOINT")

    require_authority(recovery.get("authority"))
    expected_scenarios = [
        {"expected_error": error, "expected_outcome": outcome, "scenario_id": scenario}
        for scenario, outcome, error in gen.SCENARIOS
    ]
    if recovery.get("scenarios") != expected_scenarios:
        raise ValidationError("E-P26-RECOVERY")
    if recovery.get("baseline") != {
        "assurance_report_sha256": gen.doc_sha(report),
        "checkpoint_sha256": gen.doc_sha(checkpoint),
        "ledger_sha256": gen.doc_sha(ledger),
    }:
        raise ValidationError("E-P26-RECOVERY")
    if recovery.get("summary") != {
        "accepted_count": 1,
        "rejected_count": len(gen.SCENARIOS) - 1,
        "scenario_count": len(gen.SCENARIOS),
    }:
        raise ValidationError("E-P26-RECOVERY")

    require_authority(release.get("authority"))
    if release.get("contract") != "principia-offline-consequence-plan-review-request-packet-assurance/0.1":
        raise ValidationError("E-P26-RELEASE")
    for key, expected in {
        "decision": gen.DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "live_activation_permitted": False,
        "mode": gen.MODE,
        "next_gate": gen.NEXT_GATE,
        "phase": 26,
        "real_authorization_claimed": False,
        "source_phase25": gen.SOURCE,
        "state": gen.STATE,
        "validation": {"pull_request": None, "status": "pending", "tested_head_commit": None},
    }.items():
        if release.get(key) != expected:
            if key == "live":
                raise ValidationError("E-P26-LIVE-FROZEN")
            if key == "source_phase25":
                raise ValidationError("E-P26-SOURCE-PIN")
            raise ValidationError("E-P26-RELEASE")
    if release.get("result") != report.get("summary"):
        raise ValidationError("E-P26-RELEASE")
    for name, path in {
        "report": gen.REPORT_PATH,
        "ledger": gen.LEDGER_PATH,
        "checkpoint": gen.CHECKPOINT_PATH,
        "recovery": gen.RECOVERY_PATH,
    }.items():
        if release.get("artifacts", {}).get(name) != {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": gen.file_sha_value(bundle[path]),
        }:
            raise ValidationError("E-P26-RELEASE")


def main() -> int:
    errors: list[str] = []
    for path, expected in gen.SOURCE_FILES.items():
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"E-P26-SOURCE-PIN: {path.relative_to(ROOT)}")
    try:
        built = gen.build()
        validate_bundle(built)
        for path, value in built.items():
            if not path.is_file() or path.read_text(encoding="utf-8") != gen.render(value):
                errors.append(f"generated file drift: {path.relative_to(ROOT)}")
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValidationError, ValueError) as exc:
        errors.append(str(exc))
    for path in (REPORT_MD_PATH, WORKFLOW_PATH):
        if not path.is_file():
            errors.append(f"missing Phase 26 file: {path.relative_to(ROOT)}")
    if not errors:
        report_md = REPORT_MD_PATH.read_text(encoding="utf-8")
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        for marker in (
            "# Phase 26 — Offline Consequence-Plan Review-Request Packet Assurance Candidate",
            "review-request-packets-assured-no-dispatch",
            "71 deterministic scenarios",
            "0 dispatched packets",
            "0 started reviews",
            "live: false",
        ):
            if marker not in report_md:
                errors.append(f"Phase 26 report missing marker: {marker}")
        for marker in (
            "contents: read",
            "generate_phase26_offline_consequence_plan_review_request_packet_assurance.py --check",
            "validate_phase26_offline_consequence_plan_review_request_packet_assurance.py",
        ):
            if marker not in workflow:
                errors.append(f"Phase 26 workflow missing marker: {marker}")
        for forbidden in (
            "contents" + ": write",
            "git " + "push",
            "git " + "commit",
            "pull_request" + "_target",
            "repository: Rhodan-lab/Atlas",
            "curl ",
            "wget ",
        ):
            if forbidden in workflow:
                errors.append(f"Phase 26 workflow contains forbidden token: {forbidden}")
    if errors:
        print("Phase 26 validation errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "Phase 26 passed: two request packets are independently assured, local-only, "
        "non-dispatched, non-executing, non-mutating, and live=false."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
