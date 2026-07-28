#!/usr/bin/env python3
"""Validate Phase 23 consequence-plan assurance evidence and boundaries."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import generate_phase23_offline_consequence_plan_assurance as gen  # noqa: E402

REPORT_MD_PATH = ROOT / "reports/phase-23-offline-consequence-plan-assurance.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-23-offline-consequence-plan-assurance.yml"


class ValidationError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def authority(value: Any) -> None:
    if value != gen.AUTHORITY:
        raise ValidationError("E-P23-AUTHORITY")


def validate_plan_sources() -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]]]:
    plans_doc = load(gen.PILOT / "thermal-control.resolution-consequence-plans.v01.json")
    ledger_doc = load(gen.PILOT / "thermal-control.resolution-consequence-plan-ledger.v01.json")
    plans = plans_doc.get("plans")
    entries = ledger_doc.get("entries")
    if not isinstance(plans, list) or len(plans) != 2:
        raise ValidationError("E-P23-SOURCE-PIN")
    if not isinstance(entries, list) or len(entries) != 2:
        raise ValidationError("E-P23-SOURCE-LEDGER")
    return plans, entries


def validate_report(report: Mapping[str, Any], plans: list[Mapping[str, Any]],
                    source_entries: list[Mapping[str, Any]]) -> None:
    expected_top = {
        "contract": "principia-offline-consequence-plan-assurance-report/0.1",
        "decision": gen.DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "mode": gen.MODE,
        "source": gen.SOURCE,
    }
    for key, value in expected_top.items():
        if report.get(key) != value:
            if key == "live":
                raise ValidationError("E-P23-LIVE-FROZEN")
            if key == "source":
                raise ValidationError("E-P23-SOURCE-PIN")
            raise ValidationError("E-P23-CONTRACT")
    authority(report.get("authority"))
    assessments = report.get("assessments")
    if not isinstance(assessments, list):
        raise ValidationError("E-P23-MISSING")
    if len(assessments) < 2:
        raise ValidationError("E-P23-MISSING")
    if len(assessments) > 2:
        raise ValidationError("E-P23-ORPHAN")
    seen: set[str] = set()
    expected_checks = {
        "affected_artifact_set_exact", "authority_boundary_preserved",
        "execution_disabled_for_all_steps", "ledger_entry_digest_valid",
        "ledger_plan_digest_matches", "plan_identity_valid",
        "plan_state_planned_not_started", "source_binding_valid",
        "step_sequence_contiguous", "zero_effect_boundary_preserved",
    }
    for index, (assessment, plan, source_wrapper, expected) in enumerate(
        zip(assessments, plans, source_entries, gen.EXPECTED_PLANS), start=1
    ):
        if not isinstance(assessment, Mapping) or not isinstance(plan, Mapping):
            raise ValidationError("E-P23-SHAPE")
        aid = assessment.get("assurance_id")
        if not isinstance(aid, str) or aid in seen:
            raise ValidationError("E-P23-DUPLICATE")
        seen.add(aid)
        if assessment.get("sequence") != index:
            raise ValidationError("E-P23-SEQUENCE")
        if assessment.get("assurance_id") != expected["assurance_id"]:
            raise ValidationError("E-P23-PLAN-ID")
        if assessment.get("plan_id") != expected["plan_id"]:
            raise ValidationError("E-P23-PLAN-ID")
        if assessment.get("plan_kind") != expected["plan_kind"]:
            raise ValidationError("E-P23-PLAN-ID")
        if gen.doc_sha(plan) != expected["plan_sha256"]:
            raise ValidationError("E-P23-PLAN-DIGEST")
        if assessment.get("plan_sha256") != expected["plan_sha256"]:
            raise ValidationError("E-P23-PLAN-DIGEST")
        if not isinstance(source_wrapper, Mapping):
            raise ValidationError("E-P23-SOURCE-LEDGER")
        source_entry = source_wrapper.get("entry")
        source_digest = source_wrapper.get("entry_sha256")
        if not isinstance(source_entry, Mapping) or gen.doc_sha(source_entry) != source_digest:
            raise ValidationError("E-P23-SOURCE-LEDGER")
        if source_digest != expected["source_ledger_entry_sha256"]:
            raise ValidationError("E-P23-SOURCE-LEDGER")
        if assessment.get("source_ledger_entry_sha256") != source_digest:
            raise ValidationError("E-P23-SOURCE-LEDGER")
        if assessment.get("source_proposal_id") != expected["source_proposal_id"]:
            raise ValidationError("E-P23-SOURCE-BINDING")
        if assessment.get("source_resolution_id") != expected["source_resolution_id"]:
            raise ValidationError("E-P23-SOURCE-BINDING")
        if plan.get("source_proposal_id") != expected["source_proposal_id"]:
            raise ValidationError("E-P23-SOURCE-BINDING")
        if plan.get("source_resolution_id") != expected["source_resolution_id"]:
            raise ValidationError("E-P23-SOURCE-BINDING")
        if assessment.get("affected_artifacts") != gen.ARTIFACTS:
            raise ValidationError("E-P23-AFFECTED-SET")
        if plan.get("affected_artifacts") != gen.ARTIFACTS:
            raise ValidationError("E-P23-AFFECTED-SET")
        steps = plan.get("steps")
        if not isinstance(steps, list) or assessment.get("step_count") != 3 or len(steps) != 3:
            raise ValidationError("E-P23-STEPS")
        for step_index, step in enumerate(steps, start=1):
            if not isinstance(step, Mapping) or step.get("sequence") != step_index:
                raise ValidationError("E-P23-STEPS")
            if step.get("execution_permitted") is not False:
                raise ValidationError("E-P23-EXECUTION")
            if step.get("state") != "planned-not-started":
                raise ValidationError("E-P23-EXECUTION")
        if plan.get("state") != "planned-not-started":
            raise ValidationError("E-P23-EXECUTION")
        if plan.get("review_completed") is not False:
            raise ValidationError("E-P23-EXECUTION")
        for key in ("content_change_proposed", "effective_hold", "operational_effect",
                    "status_recommendation_recorded"):
            if plan.get(key) is not False:
                raise ValidationError("E-P23-EFFECT")
        if plan.get("real_authorization_claimed") is not False:
            raise ValidationError("E-P23-AUTHORIZATION")
        checks = assessment.get("checks")
        if not isinstance(checks, Mapping) or set(checks) != expected_checks:
            raise ValidationError("E-P23-CHECKS")
        if not all(value is True for value in checks.values()):
            raise ValidationError("E-P23-CHECKS")
        if assessment.get("verdict") != "assured-planning-only":
            raise ValidationError("E-P23-VERDICT")
        if assessment.get("execution_permitted") is not False:
            raise ValidationError("E-P23-EXECUTION")
        for key in ("effective_hold", "operational_effect", "status_change"):
            if assessment.get(key) is not False:
                raise ValidationError("E-P23-EFFECT")
        if assessment.get("real_authorization_claimed") is not False:
            raise ValidationError("E-P23-AUTHORIZATION")
    expected_summary = {
        "assured_plan_count": 2,
        "assured_step_count": 6,
        "effective_hold_count": 0,
        "failed_assurance_count": 0,
        "operational_effect_count": 0,
        "plan_count": 2,
        "real_authorization_claimed": False,
        "started_plan_count": 0,
        "status_change_count": 0,
    }
    if report.get("summary") != expected_summary:
        raise ValidationError("E-P23-SUMMARY")


def validate_bundle(bundle: Mapping[Path, Mapping[str, Any]]) -> None:
    report = bundle[gen.REPORT_PATH]
    ledger = bundle[gen.LEDGER_PATH]
    checkpoint = bundle[gen.CHECKPOINT_PATH]
    recovery = bundle[gen.RECOVERY_PATH]
    release = bundle[gen.RELEASE_PATH]
    plans, source_entries = validate_plan_sources()
    validate_report(report, plans, source_entries)
    authority(ledger.get("authority"))
    if ledger.get("contract") != "principia-offline-consequence-plan-assurance-ledger/0.1":
        raise ValidationError("E-P23-LEDGER")
    entries = ledger.get("entries")
    assessments = report["assessments"]
    if not isinstance(entries, list) or len(entries) != 2:
        raise ValidationError("E-P23-LEDGER")
    previous = None
    for index, (wrapper, assessment) in enumerate(zip(entries, assessments), start=1):
        if not isinstance(wrapper, Mapping) or not isinstance(assessment, Mapping):
            raise ValidationError("E-P23-LEDGER")
        entry = wrapper.get("entry")
        digest = wrapper.get("entry_sha256")
        if not isinstance(entry, Mapping) or gen.doc_sha(entry) != digest:
            raise ValidationError("E-P23-LEDGER")
        if entry.get("sequence") != index or entry.get("previous_entry_sha256") != previous:
            raise ValidationError("E-P23-LEDGER")
        if entry.get("assurance_id") != assessment.get("assurance_id"):
            raise ValidationError("E-P23-LEDGER")
        if entry.get("assurance_sha256") != gen.doc_sha(assessment):
            raise ValidationError("E-P23-LEDGER")
        previous = digest
    if ledger.get("source_assurance_report_sha256") != gen.doc_sha(report):
        raise ValidationError("E-P23-LEDGER")
    if ledger.get("head_sha256") != previous or ledger.get("head_sequence") != 2:
        raise ValidationError("E-P23-LEDGER")
    authority(checkpoint.get("authority"))
    if checkpoint.get("contract") != "principia-offline-consequence-plan-assurance-checkpoint/0.1":
        raise ValidationError("E-P23-CHECKPOINT")
    expected_checkpoint = {
        "assurance_count": 2,
        "assurance_report_sha256": gen.doc_sha(report),
        "assured_plan_count": 2,
        "assured_step_count": 6,
        "effective_hold_count": 0,
        "failed_assurance_count": 0,
        "ledger_sha256": gen.doc_sha(ledger),
        "operational_effect_count": 0,
        "plan_count": 2,
        "real_authorization_claimed": False,
        "started_plan_count": 0,
        "status_change_count": 0,
    }
    for key, value in expected_checkpoint.items():
        if checkpoint.get(key) != value:
            raise ValidationError("E-P23-CHECKPOINT")
    authority(recovery.get("authority"))
    expected_scenarios = [
        {"expected_error": error, "expected_outcome": outcome, "scenario_id": scenario}
        for scenario, outcome, error in gen.SCENARIOS
    ]
    if recovery.get("scenarios") != expected_scenarios:
        raise ValidationError("E-P23-RECOVERY")
    if recovery.get("baseline") != {
        "assurance_report_sha256": gen.doc_sha(report),
        "checkpoint_sha256": gen.doc_sha(checkpoint),
        "ledger_sha256": gen.doc_sha(ledger),
    }:
        raise ValidationError("E-P23-RECOVERY")
    authority(release.get("authority"))
    if release.get("contract") != "principia-offline-consequence-plan-assurance/0.1":
        raise ValidationError("E-P23-RELEASE")
    if release.get("state") != "offline-consequence-plan-assurance-candidate":
        raise ValidationError("E-P23-RELEASE")
    if release.get("mode") != gen.MODE or release.get("live") is not False:
        raise ValidationError("E-P23-LIVE-FROZEN")
    if release.get("source_phase22") != gen.SOURCE:
        raise ValidationError("E-P23-SOURCE-PIN")
    if release.get("result") != report.get("summary"):
        raise ValidationError("E-P23-RELEASE")
    if release.get("validation") != {
        "pull_request": None, "status": "pending", "tested_head_commit": None
    }:
        raise ValidationError("E-P23-RELEASE")
    for name, path in {
        "report": gen.REPORT_PATH, "ledger": gen.LEDGER_PATH,
        "checkpoint": gen.CHECKPOINT_PATH, "recovery": gen.RECOVERY_PATH,
    }.items():
        if release.get("artifacts", {}).get(name) != {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": gen.file_sha_value(bundle[path]),
        }:
            raise ValidationError("E-P23-RELEASE")


def main() -> int:
    errors: list[str] = []
    for path, expected in gen.SOURCE_FILES.items():
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"E-P23-SOURCE-PIN: {path.relative_to(ROOT)}")
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
            errors.append(f"missing Phase 23 file: {path.relative_to(ROOT)}")
    if not errors:
        report_md = REPORT_MD_PATH.read_text(encoding="utf-8")
        headings = (
            "# Phase 23 — Offline Consequence-Plan Assurance Candidate",
            "# Phase 23 — Offline Consequence-Plan Assurance",
        )
        if not any(heading in report_md for heading in headings):
            errors.append("Phase 23 report missing candidate or finalized heading")
        for marker in (
            "`principia-offline-consequence-plan-assurance-report/0.1`",
            "2 assured plans", "6 assured steps", "0 failed assurances",
            "consequence-plans-assured-no-execution", "bounded-synthetic",
            "Live: `false`",
        ):
            if marker not in report_md:
                errors.append(f"Phase 23 report missing marker: {marker}")
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        for marker in (
            "agent/phase-23-offline-consequence-plan-assurance",
            "scripts/generate_phase23_offline_consequence_plan_assurance.py --check",
            "scripts/validate_phase23_offline_consequence_plan_assurance.py",
            "software.tests.test_phase23_offline_consequence_plan_assurance",
            "scripts/validate_phase22_postmerge_record.py", "contents: read",
        ):
            if marker not in workflow:
                errors.append(f"Phase 23 workflow missing marker: {marker}")
        for token in ("contents: write", "git push", "git commit", "pull_request_target",
                      "repository: Rhodan-lab/Atlas", "curl ", "wget "):
            if token in workflow:
                errors.append(f"Phase 23 workflow contains prohibited operation: {token}")
    if errors:
        print("Phase 23 validation errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Phase 23 passed: two plans and six steps are assured as planning-only, "
          "non-executing, non-mutating, and live=false.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
