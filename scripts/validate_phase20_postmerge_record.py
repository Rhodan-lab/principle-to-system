#!/usr/bin/env python3
"""Validate the finalized post-merge Phase 20 governance record."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
CANDIDATE_PATH = ROOT / "release/phase-20-offline-manual-policy-resolution.json"
FINALIZATION_PATH = ROOT / "release/phase-20-postmerge.json"
REPORT_PATH = ROOT / "reports/phase-20-offline-manual-policy-resolution.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-20-offline-manual-policy-resolution.yml"

EXPECTED_CANDIDATE_HEAD = "d128d2c469b43fc07fe1db2f62ce9538841e4463"
EXPECTED_MERGE = "724611a7d7ec0b3723ea217928cba4616ce2bebd"
EXPECTED_CANDIDATE_SHA256 = "3cf082a2c468163936f894a55dd4e555097adf1b0b85cdba27b1931c530d0a0f"


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
            errors.append(f"missing Phase 20 finalization file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    if sha256_file(CANDIDATE_PATH) != EXPECTED_CANDIDATE_SHA256:
        errors.append("Phase 20 candidate record digest changed after merge")

    finalization = load_json(FINALIZATION_PATH)
    expected_top = {
        "contract": "principia-offline-manual-policy-resolution-finalization/0.1",
        "phase": 20,
        "state": "offline-manual-policy-resolution-validated",
        "mode": "offline-manual-policy-resolution",
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "next_gate": "offline-policy-resolution-reconciliation-candidate",
        "live_activation_permitted": False,
        "real_authorization_claimed": False,
    }
    for key, value in expected_top.items():
        if finalization.get(key) != value:
            errors.append(f"Phase 20 finalization {key} must equal {value}")

    if finalization.get("candidate_record") != {
        "path": "release/phase-20-offline-manual-policy-resolution.json",
        "sha256": EXPECTED_CANDIDATE_SHA256,
    }:
        errors.append("Phase 20 finalization candidate record pin is invalid")

    principia = finalization.get("principia")
    expected_principia = {
        "repository": "Rhodan-lab/principle-to-system",
        "pull_request": 30,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "merge_commit": EXPECTED_MERGE,
    }
    if not isinstance(principia, Mapping):
        errors.append("Phase 20 Principia provenance is missing")
    else:
        for key, value in expected_principia.items():
            if principia.get(key) != value:
                errors.append(f"Phase 20 Principia {key} must equal {value}")

    if finalization.get("validation") != {
        "applicable_workflows": 16,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "status": "success",
    }:
        errors.append("Phase 20 exact-head validation provenance is invalid")

    if finalization.get("result") != {
        "accepted_count": 1,
        "decision": "resolutions-recorded-no-mutation",
        "deferred_count": 1,
        "effective_hold_count": 0,
        "operational_effect_count": 0,
        "resolution_count": 2,
        "status_change_count": 0,
    }:
        errors.append("Phase 20 finalization result is invalid")

    authority = finalization.get("authority")
    if not isinstance(authority, Mapping):
        errors.append("Phase 20 authority record is missing")
    else:
        for key in ("automatic_status_change", "automatic_release_action", "repository_mutation"):
            if authority.get(key) is not False:
                errors.append(f"Phase 20 finalization must keep {key}=false")
        if authority.get("status_inheritance") != "prohibited":
            errors.append("Phase 20 finalization must prohibit status inheritance")

    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "Phase 20 state: **offline-manual-policy-resolution-validated**",
        "| 20 | Offline manual policy resolution | Merged and validated through PR #30 |",
        f"PR #30 was merged into `main` at commit `{EXPECTED_MERGE}`",
        EXPECTED_CANDIDATE_HEAD,
        "release/phase-20-postmerge.json",
        "Historical Phase 20 candidate marker: `exact-head validation pending`",
        "offline-policy-resolution-reconciliation-candidate",
        "bounded-synthetic",
        "resolutions-recorded-no-mutation",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 20 finalization marker: {marker}")
    for stale in (
        "**Phase 20 — Offline Manual Policy Resolution Candidate implemented on `agent/phase-20-offline-manual-policy-resolution`; exact-head validation pending.**",
        "| 20 | Offline manual policy resolution | Implemented; exact-head validation pending |",
        "Phase 20 target state: **offline-manual-policy-resolution-candidate**",
    ):
        if stale in state:
            errors.append(f"PROJECT_STATE.md retains stale Phase 20 wording: {stale}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        f"> Exact tested head: `{EXPECTED_CANDIDATE_HEAD}`",
        f"> Merge commit: `{EXPECTED_MERGE}`",
        "Final state: `offline-manual-policy-resolution-validated`",
        "release/phase-20-postmerge.json",
        "offline policy-resolution reconciliation candidate",
        "bounded-synthetic",
        "0 effective holds",
        "resolutions-recorded-no-mutation",
        "> Live: `false`",
    ):
        if marker not in report:
            errors.append(f"Phase 20 report missing finalization marker: {marker}")
    for stale in (
        "> Candidate state: `offline-manual-policy-resolution-candidate`",
        "exact-head validation remains pending",
    ):
        if stale in report:
            errors.append(f"Phase 20 report retains stale candidate wording: {stale}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/finalize-phase-20-record",
        "scripts/validate_phase20_postmerge_record.py",
        "release/phase-20-postmerge.json",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"Phase 20 workflow missing finalization marker: {marker}")
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
            errors.append(f"Phase 20 workflow contains forbidden token: {forbidden}")

    if errors:
        return fail(errors)
    print(
        "Phase 20 post-merge record passed: PR #30 and exact candidate head pinned, "
        "synthetic resolutions integrated, no real authorization claimed, and all effects disabled."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("Phase 20 post-merge record errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
