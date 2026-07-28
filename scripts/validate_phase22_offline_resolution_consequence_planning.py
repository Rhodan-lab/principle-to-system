#!/usr/bin/env python3
"""Validate Phase 22 offline resolution-consequence planning evidence."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import generate_phase22_offline_resolution_consequence_planning as gen  # noqa: E402

STATE_PATH = ROOT / "PROJECT_STATE.md"
REPORT_PATH = ROOT / "reports" / "phase-22-offline-resolution-consequence-planning.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-22-offline-resolution-consequence-planning.yml"


class ValidationError(ValueError):
    pass


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authority(value: Any) -> None:
    if value != gen.AUTHORITY:
        raise ValidationError("E-P22-AUTHORITY")


def validate_stream(stream: Mapping[str, Any]) -> None:
    expected_top = {
        "contract": "principia-offline-resolution-consequence-plans/0.1",
        "decision": gen.DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "mode": gen.MODE,
        "source": gen.source(),
    }
    for key, expected in expected_top.items():
        if stream.get(key) != expected:
            if key == "live":
                raise ValidationError("E-P22-LIVE-FROZEN")
            if key == "source":
                raise ValidationError("E-P22-SOURCE-PIN")
            raise ValidationError("E-P22-CONTRACT")
    authority(stream.get("authority"))
    plans = stream.get("plans")
    if not isinstance(plans, list):
        raise ValidationError("E-P22-SHAPE")
    if len(plans) < 2:
        raise ValidationError("E-P22-MISSING")
    if len(plans) > 2:
        raise ValidationError("E-P22-ORPHAN")
    expected = gen.plans()
    seen: set[str] = set()
    for index, (actual, target) in enumerate(zip(plans, expected), start=1):
        if not isinstance(actual, Mapping):
            raise ValidationError("E-P22-SHAPE")
        plan_id = actual.get("plan_id")
        if not isinstance(plan_id, str) or plan_id in seen:
            raise ValidationError("E-P22-DUPLICATE")
        seen.add(plan_id)
        if plan_id != target["plan_id"] or actual.get("plan_kind") != target["plan_kind"]:
            raise ValidationError("E-P22-PLAN-ID")
        if actual.get("sequence") != index:
            raise ValidationError("E-P22-SEQUENCE")
        if actual.get("source_resolution_id") != target["source_resolution_id"]:
            raise ValidationError("E-P22-RESOLUTION-ID")
        if actual.get("source_proposal_id") != target["source_proposal_id"]:
            raise ValidationError("E-P22-PROPOSAL-ID")
        if actual.get("source_decision") != target["source_decision"]:
            raise ValidationError("E-P22-DECISION")
        if actual.get("affected_artifacts") != gen.ARTIFACT_KEYS:
            raise ValidationError("E-P22-AFFECTED-SET")
        if actual.get("state") != "planned-not-started":
            raise ValidationError("E-P22-EXECUTION")
        if actual.get("real_authorization_claimed") is not False:
            raise ValidationError("E-P22-AUTHORIZATION")
        if actual.get("review_completed") is not False:
            raise ValidationError("E-P22-EXECUTION")
        for key in ("content_change_proposed", "effective_hold", "operational_effect", "status_recommendation_recorded"):
            if actual.get(key) is not False:
                raise ValidationError("E-P22-EFFECT")
        steps = actual.get("steps")
        if not isinstance(steps, list) or len(steps) != 3:
            raise ValidationError("E-P22-STEPS")
        for step_index, step in enumerate(steps, start=1):
            if not isinstance(step, Mapping) or step.get("sequence") != step_index:
                raise ValidationError("E-P22-STEPS")
            if step.get("state") != "planned-not-started" or step.get("execution_permitted") is not False:
                raise ValidationError("E-P22-EXECUTION")
    expected_summary = {
        "completed_plan_count": 0,
        "effective_hold_count": 0,
        "manual_review_plan_count": 1,
        "operational_effect_count": 0,
        "plan_count": 2,
        "planned_step_count": 6,
        "release_governance_plan_count": 1,
        "started_plan_count": 0,
        "status_change_count": 0,
    }
    if stream.get("summary") != expected_summary:
        raise ValidationError("E-P22-SUMMARY")


def validate_bundle(bundle: Mapping[Path, Mapping[str, Any]]) -> None:
    stream = bundle[gen.PLANS_PATH]
    ledger = bundle[gen.LEDGER_PATH]
    checkpoint = bundle[gen.CHECKPOINT_PATH]
    recovery = bundle[gen.RECOVERY_PATH]
    release = bundle[gen.RELEASE_PATH]
    validate_stream(stream)
    authority(ledger.get("authority"))
    if ledger.get("contract") != "principia-offline-resolution-consequence-plan-ledger/0.1":
        raise ValidationError("E-P22-LEDGER")
    if ledger.get("source_plan_stream_sha256") != gen.doc_sha(stream):
        raise ValidationError("E-P22-LEDGER")
    entries = ledger.get("entries")
    if not isinstance(entries, list) or len(entries) != 2:
        raise ValidationError("E-P22-LEDGER")
    previous: str | None = None
    for index, wrapper in enumerate(entries, start=1):
        if not isinstance(wrapper, Mapping) or not isinstance(wrapper.get("entry"), Mapping):
            raise ValidationError("E-P22-LEDGER")
        entry = wrapper["entry"]
        digest = wrapper.get("entry_sha256")
        if digest != gen.doc_sha(entry):
            raise ValidationError("E-P22-DIGEST")
        if entry.get("sequence") != index:
            raise ValidationError("E-P22-SEQUENCE")
        if entry.get("previous_entry_sha256") != previous:
            raise ValidationError("E-P22-LEDGER")
        target = gen.plans()[index - 1]
        if entry.get("plan_id") != target["plan_id"] or entry.get("plan_sha256") != gen.doc_sha(target):
            raise ValidationError("E-P22-DIGEST")
        if entry.get("source_resolution_id") != target["source_resolution_id"]:
            raise ValidationError("E-P22-RESOLUTION-ID")
        previous = str(digest)
    if ledger.get("head_sequence") != 2 or ledger.get("head_sha256") != previous:
        raise ValidationError("E-P22-LEDGER")
    authority(checkpoint.get("authority"))
    if checkpoint.get("contract") != "principia-offline-resolution-consequence-plan-checkpoint/0.1":
        raise ValidationError("E-P22-CHECKPOINT")
    if checkpoint.get("plan_stream_sha256") != gen.doc_sha(stream) or checkpoint.get("ledger_sha256") != gen.doc_sha(ledger):
        raise ValidationError("E-P22-CHECKPOINT")
    expected_counts = {
        "plan_count": 2,
        "planned_step_count": 6,
        "started_plan_count": 0,
        "completed_plan_count": 0,
        "effective_hold_count": 0,
        "operational_effect_count": 0,
        "status_change_count": 0,
        "real_authorization_claimed": False,
    }
    for key, expected in expected_counts.items():
        if checkpoint.get(key) != expected:
            if key == "real_authorization_claimed":
                raise ValidationError("E-P22-AUTHORIZATION")
            if key in ("started_plan_count", "completed_plan_count"):
                raise ValidationError("E-P22-EXECUTION")
            if key in ("effective_hold_count", "operational_effect_count", "status_change_count"):
                raise ValidationError("E-P22-EFFECT")
            raise ValidationError("E-P22-CHECKPOINT")
    authority(recovery.get("authority"))
    expected_scenarios = [
        {"expected_error": error, "expected_outcome": outcome, "scenario_id": scenario}
        for scenario, outcome, error in gen.SCENARIOS
    ]
    if recovery.get("scenarios") != expected_scenarios:
        raise ValidationError("E-P22-RECOVERY")
    if recovery.get("baseline") != {
        "checkpoint_sha256": gen.doc_sha(checkpoint),
        "ledger_sha256": gen.doc_sha(ledger),
        "plan_stream_sha256": gen.doc_sha(stream),
    }:
        raise ValidationError("E-P22-RECOVERY")
    authority(release.get("authority"))
    expected_release = {
        "contract": "principia-offline-resolution-consequence-planning/0.1",
        "decision": gen.DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "live_activation_permitted": False,
        "mode": gen.MODE,
        "next_gate": "offline-consequence-plan-assurance-candidate",
        "phase": 22,
        "real_authorization_claimed": False,
        "source_phase21": gen.source(),
        "state": "offline-resolution-consequence-planning-candidate",
    }
    for key, expected in expected_release.items():
        if release.get(key) != expected:
            if key == "live":
                raise ValidationError("E-P22-LIVE-FROZEN")
            if key == "real_authorization_claimed":
                raise ValidationError("E-P22-AUTHORIZATION")
            if key == "source_phase21":
                raise ValidationError("E-P22-SOURCE-PIN")
            raise ValidationError("E-P22-RELEASE")
    if release.get("result") != stream.get("summary"):
        raise ValidationError("E-P22-RELEASE")
    if release.get("validation") != {"pull_request": None, "status": "pending", "tested_head_commit": None}:
        raise ValidationError("E-P22-RELEASE")
    for name, path in {"checkpoint": gen.CHECKPOINT_PATH, "ledger": gen.LEDGER_PATH, "plans": gen.PLANS_PATH, "recovery": gen.RECOVERY_PATH}.items():
        if release.get("artifacts", {}).get(name) != {"path": path.relative_to(ROOT).as_posix(), "sha256": file_sha(path)}:
            raise ValidationError("E-P22-RELEASE")


def main() -> int:
    errors: list[str] = []
    source_files = (
        (ROOT / "release/phase-21-postmerge.json", gen.PHASE21_POSTMERGE_SHA),
        (ROOT / "release/phase-21-offline-policy-resolution-reconciliation.json", gen.PHASE21_CANDIDATE_SHA),
        (gen.PILOT / "thermal-control.policy-resolution-reconciliation-report.v01.json", gen.RECONCILIATION_REPORT_SHA),
        (gen.PILOT / "thermal-control.policy-resolution-reconciliation-ledger.v01.json", gen.RECONCILIATION_LEDGER_SHA),
        (gen.PILOT / "thermal-control.policy-resolution-reconciliation-checkpoint.v01.json", gen.RECONCILIATION_CHECKPOINT_SHA),
    )
    for path, expected in source_files:
        if not path.is_file() or file_sha(path) != expected:
            errors.append("E-P22-SOURCE-PIN")
    try:
        built = gen.build()
        validate_bundle(built)
        for path, expected in built.items():
            if not path.is_file() or json.loads(path.read_text(encoding="utf-8")) != expected:
                errors.append(f"generated data drift: {path.relative_to(ROOT)}")
    except (OSError, json.JSONDecodeError, KeyError, ValidationError) as exc:
        errors.append(str(exc))
    for path in (STATE_PATH, REPORT_PATH, WORKFLOW_PATH):
        if not path.is_file():
            errors.append(f"missing Phase 22 file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)
    state = STATE_PATH.read_text(encoding="utf-8")
    candidate_markers = (
        "**Phase 22 — Offline Resolution-Consequence Planning Candidate implemented",
        "Phase 22 target state: **offline-resolution-consequence-planning-candidate**",
        "| 22 | Offline resolution-consequence planning | Implemented; exact-head validation pending |",
    )
    final_markers = (
        "Phase 22 state: **offline-resolution-consequence-planning-validated**",
        "| 22 | Offline resolution-consequence planning | Merged and validated",
    )
    if not all(marker in state for marker in candidate_markers) and not all(marker in state for marker in final_markers):
        errors.append("PROJECT_STATE.md missing Phase 22 state markers")
    for marker in (
        "Phase 21 state: **offline-policy-resolution-reconciliation-validated**",
        "consequence-plans-recorded-no-execution",
        "planned-not-started",
        "real_authorization_claimed: false",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 22 marker: {marker}")
    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        "# Phase 22 — Offline Resolution-Consequence Planning Candidate",
        "`principia-offline-resolution-consequence-plans/0.1`",
        "1 manual-review work plan",
        "1 release-governance follow-up plan",
        "6 planned steps",
        "0 started plans",
        "consequence-plans-recorded-no-execution",
        "> Live: `false`",
    ):
        if marker not in report:
            errors.append(f"Phase 22 report missing marker: {marker}")
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/phase-22-offline-resolution-consequence-planning",
        "scripts/generate_phase22_offline_resolution_consequence_planning.py --check",
        "scripts/validate_phase22_offline_resolution_consequence_planning.py",
        "software.tests.test_phase22_offline_resolution_consequence_planning",
        "scripts/validate_phase21_postmerge_record.py",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"Phase 22 workflow missing marker: {marker}")
    for token in ("contents: write", "git push", "git commit", "pull_request_target", "repository: Rhodan-lab/Atlas", "curl ", "wget "):
        if token in workflow:
            errors.append(f"Phase 22 workflow contains prohibited operation: {token}")
    if errors:
        return fail(errors)
    print("Phase 22 passed: two consequence plans and six steps remain planned-not-started, non-authorizing, non-effective, non-mutating, and live=false.")
    return 0


def fail(errors: list[str]) -> int:
    print("Phase 22 validation errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
