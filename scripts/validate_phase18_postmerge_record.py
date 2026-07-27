#!/usr/bin/env python3
"""Validate the finalized post-merge Phase 18 governance record."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
CANDIDATE_PATH = ROOT / "release" / "phase-18-offline-reconciliation.json"
FINALIZATION_PATH = ROOT / "release" / "phase-18-postmerge.json"
REPORT_PATH = ROOT / "reports" / "phase-18-offline-reconciliation.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-18-offline-reconciliation.yml"

EXPECTED_CANDIDATE_HEAD = "740ab7752bb03fc7dafe6bb9c076f5cb44a5f44f"
EXPECTED_MERGE = "4ecb41ad4f9f524e83cc0db43f672bd9dcf3b67a"
EXPECTED_CANDIDATE_SHA256 = "bea187d52e42915185903ea298f8ffecc9cc2845387259fa86a606cf7561f4a2"


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
            errors.append(f"missing Phase 18 finalization file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    if sha256_file(CANDIDATE_PATH) != EXPECTED_CANDIDATE_SHA256:
        errors.append("Phase 18 candidate record digest changed after merge")

    finalization = load_json(FINALIZATION_PATH)
    expected_top = {
        "contract": "principia-offline-reconciliation-finalization/0.1",
        "phase": 18,
        "state": "offline-reconciliation-simulation-validated",
        "mode": "offline-reconciliation-simulation",
        "live": False,
        "next_gate": "offline-reconciliation-policy-candidate",
        "live_activation_permitted": False,
    }
    for key, value in expected_top.items():
        if finalization.get(key) != value:
            errors.append(f"Phase 18 finalization {key} must equal {value}")

    if finalization.get("candidate_record") != {
        "path": "release/phase-18-offline-reconciliation.json",
        "sha256": EXPECTED_CANDIDATE_SHA256,
    }:
        errors.append("Phase 18 finalization candidate record pin is invalid")

    principia = finalization.get("principia")
    expected_principia = {
        "repository": "Rhodan-lab/principle-to-system",
        "pull_request": 25,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "merge_commit": EXPECTED_MERGE,
    }
    if not isinstance(principia, Mapping):
        errors.append("Phase 18 Principia provenance is missing")
    else:
        for key, value in expected_principia.items():
            if principia.get(key) != value:
                errors.append(f"Phase 18 Principia {key} must equal {value}")

    if finalization.get("validation") != {
        "applicable_workflows": 14,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "status": "success",
    }:
        errors.append("Phase 18 exact-head validation provenance is invalid")

    authority = finalization.get("authority")
    if not isinstance(authority, Mapping):
        errors.append("Phase 18 authority record is missing")
    else:
        for key in ("automatic_status_change", "automatic_release_action", "repository_mutation"):
            if authority.get(key) is not False:
                errors.append(f"Phase 18 finalization must keep {key}=false")
        if authority.get("status_inheritance") != "prohibited":
            errors.append("Phase 18 finalization must prohibit status inheritance")

    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "Phase 18 state: **offline-reconciliation-simulation-validated**",
        "| 18 | Offline reconciliation simulation | Merged and validated through PR #25 |",
        f"PR #25 was merged into `main` at commit `{EXPECTED_MERGE}`",
        EXPECTED_CANDIDATE_HEAD,
        "release/phase-18-postmerge.json",
        "Historical Phase 18 candidate marker: `exact-head validation pending`",
        "offline-reconciliation-policy-candidate",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 18 finalization marker: {marker}")
    for stale in (
        "**Phase 18 — Offline Reconciliation Simulation Candidate implemented on `agent/phase-18-offline-reconciliation-simulation`; exact-head validation pending.**",
        "| 18 | Offline reconciliation simulation | Implemented; exact-head validation pending |",
        "Phase 18 target state: **offline-reconciliation-simulation-candidate**",
    ):
        if stale in state:
            errors.append(f"PROJECT_STATE.md retains stale Phase 18 wording: {stale}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        f"> Exact tested head: `{EXPECTED_CANDIDATE_HEAD}`",
        f"> Merge commit: `{EXPECTED_MERGE}`",
        "Final state: `offline-reconciliation-simulation-validated`",
        "release/phase-18-postmerge.json",
        "offline reconciliation-policy candidate",
        "> Live: `false`",
    ):
        if marker not in report:
            errors.append(f"Phase 18 report missing finalization marker: {marker}")
    for stale in (
        "> Candidate state: `offline-reconciliation-simulation-candidate`",
        "exact-head validation remains pending",
    ):
        if stale in report:
            errors.append(f"Phase 18 report retains stale candidate wording: {stale}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/finalize-phase-18-governance",
        "scripts/validate_phase18_postmerge_record.py",
        "release/phase-18-postmerge.json",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"Phase 18 workflow missing finalization marker: {marker}")
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
            errors.append(f"Phase 18 workflow contains forbidden token: {forbidden}")

    if errors:
        return fail(errors)
    print(
        "Phase 18 post-merge record passed: PR #25 and exact candidate head pinned, "
        "offline reconciliation integrated, authority separated, and live activation disabled."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("Phase 18 post-merge record errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
