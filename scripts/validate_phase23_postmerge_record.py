#!/usr/bin/env python3
"""Validate the finalized post-merge Phase 23 assurance record."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
CANDIDATE_PATH = ROOT / "release/phase-23-offline-consequence-plan-assurance.json"
FINALIZATION_PATH = ROOT / "release/phase-23-postmerge.json"
REPORT_PATH = ROOT / "reports/phase-23-offline-consequence-plan-assurance.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-23-offline-consequence-plan-assurance.yml"

EXPECTED_CANDIDATE_HEAD = "083e82eeea8e127e6f5b65bb020720b5c1c4edab"
EXPECTED_MERGE = "912a66343d2e262a7651e05ce116dabf747ae152"
EXPECTED_CANDIDATE_SHA256 = "7fb1e743dee555e33ccf2d395c589256ecad4748568bc2d92c1256adc135dce6"


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
            errors.append(f"missing Phase 23 finalization file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)
    if sha256_file(CANDIDATE_PATH) != EXPECTED_CANDIDATE_SHA256:
        errors.append("Phase 23 candidate record digest changed after merge")
    finalization = load_json(FINALIZATION_PATH)
    for key, value in {
        "contract": "principia-offline-consequence-plan-assurance-finalization/0.1",
        "phase": 23,
        "state": "offline-consequence-plan-assurance-validated",
        "mode": "offline-consequence-plan-assurance",
        "fixture_kind": "bounded-synthetic",
        "decision": "consequence-plans-assured-no-execution",
        "live": False,
        "next_gate": "offline-consequence-plan-review-readiness-candidate",
        "live_activation_permitted": False,
        "real_authorization_claimed": False,
    }.items():
        if finalization.get(key) != value:
            errors.append(f"Phase 23 finalization {key} must equal {value}")
    if finalization.get("candidate_record") != {
        "path": "release/phase-23-offline-consequence-plan-assurance.json",
        "sha256": EXPECTED_CANDIDATE_SHA256,
    }:
        errors.append("Phase 23 finalization candidate record pin is invalid")
    principia = finalization.get("principia")
    expected_principia = {
        "repository": "Rhodan-lab/principle-to-system",
        "pull_request": 37,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "merge_commit": EXPECTED_MERGE,
    }
    if not isinstance(principia, Mapping) or any(
        principia.get(key) != value for key, value in expected_principia.items()
    ):
        errors.append("Phase 23 Principia provenance is invalid")
    if finalization.get("validation") != {
        "applicable_workflows": 17,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "status": "success",
    }:
        errors.append("Phase 23 exact-head validation provenance is invalid")
    if finalization.get("result") != {
        "assured_plan_count": 2,
        "assured_step_count": 6,
        "effective_hold_count": 0,
        "failed_assurance_count": 0,
        "operational_effect_count": 0,
        "plan_count": 2,
        "real_authorization_claimed": False,
        "started_plan_count": 0,
        "status_change_count": 0,
    }:
        errors.append("Phase 23 finalization result is invalid")
    authority = finalization.get("authority")
    if not isinstance(authority, Mapping):
        errors.append("Phase 23 authority record is missing")
    else:
        for key in ("automatic_status_change", "automatic_release_action", "repository_mutation"):
            if authority.get(key) is not False:
                errors.append(f"Phase 23 finalization must keep {key}=false")
        if authority.get("status_inheritance") != "prohibited":
            errors.append("Phase 23 finalization must prohibit status inheritance")
    state = STATE_PATH.read_text(encoding="utf-8")
    # Phase 23 may no longer be the current heading after a later phase is validated.
    # Its immutable row, provenance, candidate history, and next-gate record remain required.
    for marker in (
        "Phase 23 state: **offline-consequence-plan-assurance-validated**",
        "| 23 | Offline consequence-plan assurance | Merged and validated through PR #37 |",
        f"Phase 23 exact candidate validation passed at `{EXPECTED_CANDIDATE_HEAD}`",
        f"PR #37 was merged into `main` at commit `{EXPECTED_MERGE}`",
        "release/phase-23-postmerge.json",
        "Historical Phase 23 candidate marker: `exact-head validation pending`",
        "offline-consequence-plan-review-readiness-candidate",
        "consequence-plans-assured-no-execution",
        "assured-planning-only",
        "real_authorization_claimed: false",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 23 finalization marker: {marker}")
    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        "# Phase 23 — Offline Consequence-Plan Assurance",
        f"> Exact tested head: `{EXPECTED_CANDIDATE_HEAD}`",
        f"> Merge commit: `{EXPECTED_MERGE}`",
        "> Final state: `offline-consequence-plan-assurance-validated`",
        "release/phase-23-postmerge.json",
        "2 assured plans", "6 assured steps", "0 failed assurances",
        "consequence-plans-assured-no-execution",
        "> Live: `false`",
    ):
        if marker not in report:
            errors.append(f"Phase 23 report missing finalization marker: {marker}")
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/finalize-phase-23-record",
        "scripts/validate_phase23_postmerge_record.py",
        "release/phase-23-postmerge.json",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"Phase 23 workflow missing finalization marker: {marker}")
    for forbidden in (
        "contents" + ": write", "git " + "push", "git " + "commit",
        "pull_request" + "_target", "repository: Rhodan-lab/Atlas", "curl ", "wget ",
    ):
        if forbidden in workflow:
            errors.append(f"Phase 23 workflow contains forbidden token: {forbidden}")
    if errors:
        return fail(errors)
    print(
        "Phase 23 post-merge record passed: PR #37 and exact candidate head pinned, "
        "two plans and six steps assured, authorization absent, and execution disabled."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("Phase 23 post-merge record errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
