#!/usr/bin/env python3
"""Validate the finalized post-merge Phase 22 governance record."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
CANDIDATE_PATH = ROOT / "release" / "phase-22-offline-resolution-consequence-planning.json"
FINALIZATION_PATH = ROOT / "release" / "phase-22-postmerge.json"
REPORT_PATH = ROOT / "reports" / "phase-22-offline-resolution-consequence-planning.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-22-offline-resolution-consequence-planning.yml"

EXPECTED_CANDIDATE_HEAD = "43d10f7a9d24f92f8dcdf0c4c37f4f4d2233e38a"
EXPECTED_MERGE = "54dcbaa12a4ac57ecd31a8936e6549c35393d04b"
EXPECTED_CANDIDATE_SHA256 = "ccb4b608f77ba291f65ef25e0453382a3905a16b4bc5901d878de00dbdc4c9c8"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def main() -> int:
    errors: list[str] = []
    for path in (STATE_PATH, CANDIDATE_PATH, FINALIZATION_PATH, REPORT_PATH, WORKFLOW_PATH):
        if not path.is_file():
            errors.append(f"missing Phase 22 finalization file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    if sha256_file(CANDIDATE_PATH) != EXPECTED_CANDIDATE_SHA256:
        errors.append("Phase 22 candidate record digest changed after merge")

    finalization = load_json(FINALIZATION_PATH)
    for key, value in {
        "contract": "principia-offline-resolution-consequence-planning-finalization/0.1",
        "phase": 22,
        "state": "offline-resolution-consequence-planning-validated",
        "mode": "offline-resolution-consequence-planning",
        "fixture_kind": "bounded-synthetic",
        "decision": "consequence-plans-recorded-no-execution",
        "live": False,
        "next_gate": "offline-consequence-plan-assurance-candidate",
        "live_activation_permitted": False,
        "real_authorization_claimed": False,
    }.items():
        if finalization.get(key) != value:
            errors.append(f"Phase 22 finalization {key} must equal {value}")

    if finalization.get("candidate_record") != {
        "path": "release/phase-22-offline-resolution-consequence-planning.json",
        "sha256": EXPECTED_CANDIDATE_SHA256,
    }:
        errors.append("Phase 22 finalization candidate record pin is invalid")

    principia = finalization.get("principia")
    expected_principia = {
        "repository": "Rhodan-lab/principle-to-system",
        "pull_request": 35,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "merge_commit": EXPECTED_MERGE,
    }
    if not isinstance(principia, Mapping):
        errors.append("Phase 22 Principia provenance is missing")
    elif any(principia.get(key) != value for key, value in expected_principia.items()):
        errors.append("Phase 22 Principia provenance is invalid")

    if finalization.get("validation") != {
        "applicable_workflows": 18,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "status": "success",
    }:
        errors.append("Phase 22 exact-head validation provenance is invalid")

    if finalization.get("result") != {
        "completed_plan_count": 0,
        "effective_hold_count": 0,
        "manual_review_plan_count": 1,
        "operational_effect_count": 0,
        "plan_count": 2,
        "planned_step_count": 6,
        "release_governance_plan_count": 1,
        "started_plan_count": 0,
        "status_change_count": 0,
    }:
        errors.append("Phase 22 finalization result is invalid")

    authority = finalization.get("authority")
    if not isinstance(authority, Mapping):
        errors.append("Phase 22 authority record is missing")
    else:
        for key in ("automatic_status_change", "automatic_release_action", "repository_mutation"):
            if authority.get(key) is not False:
                errors.append(f"Phase 22 finalization must keep {key}=false")
        if authority.get("status_inheritance") != "prohibited":
            errors.append("Phase 22 finalization must prohibit status inheritance")

    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "**Phase 22 — Offline Resolution-Consequence Planning merged and validated through PR #35.**",
        "Phase 22 state: **offline-resolution-consequence-planning-validated**",
        "| 22 | Offline resolution-consequence planning | Merged and validated through PR #35 |",
        f"Phase 22 exact candidate validation passed at `{EXPECTED_CANDIDATE_HEAD}`",
        f"PR #35 was merged into `main` at commit `{EXPECTED_MERGE}`",
        "release/phase-22-postmerge.json",
        "Historical Phase 22 candidate marker: `exact-head validation pending`",
        "offline-consequence-plan-assurance-candidate",
        "consequence-plans-recorded-no-execution",
        "planned-not-started",
        "real_authorization_claimed: false",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 22 finalization marker: {marker}")
    for stale in (
        "**Phase 22 — Offline Resolution-Consequence Planning Candidate implemented on `agent/phase-22-offline-resolution-consequence-planning`; exact-head validation pending.**",
        "| 22 | Offline resolution-consequence planning | Implemented; exact-head validation pending |",
        "Phase 22 target state: **offline-resolution-consequence-planning-candidate**",
    ):
        if stale in state:
            errors.append(f"PROJECT_STATE.md retains stale Phase 22 wording: {stale}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        "# Phase 22 — Offline Resolution-Consequence Planning",
        f"> Exact tested head: `{EXPECTED_CANDIDATE_HEAD}`",
        f"> Merge commit: `{EXPECTED_MERGE}`",
        "> Final state: `offline-resolution-consequence-planning-validated`",
        "release/phase-22-postmerge.json",
        "1 manual-review work plan",
        "1 release-governance follow-up plan",
        "6 planned steps",
        "0 started plans",
        "consequence-plans-recorded-no-execution",
        "> Live: `false`",
    ):
        if marker not in report:
            errors.append(f"Phase 22 report missing finalization marker: {marker}")
    if "> Candidate state: `offline-resolution-consequence-planning-candidate`" in report:
        errors.append("Phase 22 report retains stale candidate-state wording")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/finalize-phase-22-record",
        "scripts/validate_phase22_postmerge_record.py",
        "release/phase-22-postmerge.json",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"Phase 22 workflow missing finalization marker: {marker}")
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
            errors.append(f"Phase 22 workflow contains forbidden token: {forbidden}")

    if errors:
        return fail(errors)
    print(
        "Phase 22 post-merge record passed: PR #35 and exact candidate head pinned, "
        "two plans and six non-executing steps integrated, authorization absent, and effects disabled."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("Phase 22 post-merge record errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
