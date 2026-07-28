#!/usr/bin/env python3
"""Validate the finalized post-merge Phase 21 governance record."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
CANDIDATE_PATH = ROOT / "release" / "phase-21-offline-policy-resolution-reconciliation.json"
FINALIZATION_PATH = ROOT / "release" / "phase-21-postmerge.json"
REPORT_PATH = ROOT / "reports" / "phase-21-offline-policy-resolution-reconciliation.md"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "validate-phase-21-offline-policy-resolution-reconciliation.yml"

EXPECTED_CANDIDATE_HEAD = "ff97a73d8fcba37eaf31220a9480d882c345c7c4"
EXPECTED_MERGE = "7e14b700883018ca11c38d07f82418f165f542f5"
EXPECTED_CANDIDATE_SHA256 = "d3485c7941588232121c74fc2d063d51c73aa121c5bd9a8e4fcbc5be2d5ba4af"


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
            errors.append(f"missing Phase 21 finalization file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    if sha256_file(CANDIDATE_PATH) != EXPECTED_CANDIDATE_SHA256:
        errors.append("Phase 21 candidate record digest changed after merge")

    finalization = load_json(FINALIZATION_PATH)
    expected_top = {
        "contract": "principia-offline-policy-resolution-reconciliation-finalization/0.1",
        "phase": 21,
        "state": "offline-policy-resolution-reconciliation-validated",
        "mode": "offline-policy-resolution-reconciliation",
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "next_gate": "offline-resolution-consequence-planning-candidate",
        "live_activation_permitted": False,
        "real_authorization_claimed": False,
    }
    for key, value in expected_top.items():
        if finalization.get(key) != value:
            errors.append(f"Phase 21 finalization {key} must equal {value}")

    if finalization.get("candidate_record") != {
        "path": "release/phase-21-offline-policy-resolution-reconciliation.json",
        "sha256": EXPECTED_CANDIDATE_SHA256,
    }:
        errors.append("Phase 21 finalization candidate record pin is invalid")

    principia = finalization.get("principia")
    expected_principia = {
        "repository": "Rhodan-lab/principle-to-system",
        "pull_request": 32,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "merge_commit": EXPECTED_MERGE,
    }
    if not isinstance(principia, Mapping):
        errors.append("Phase 21 Principia provenance is missing")
    else:
        for key, value in expected_principia.items():
            if principia.get(key) != value:
                errors.append(f"Phase 21 Principia {key} must equal {value}")

    if finalization.get("validation") != {
        "applicable_workflows": 17,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "status": "success",
    }:
        errors.append("Phase 21 exact-head validation provenance is invalid")

    expected_result = {
        "checkpoint_mismatch_count": 0,
        "decision": "reconciled-resolutions-no-mutation",
        "effective_hold_count": 0,
        "ledger_mismatch_count": 0,
        "matched_resolution_count": 2,
        "missing_resolution_count": 0,
        "operational_effect_count": 0,
        "orphan_resolution_count": 0,
        "proposal_count": 2,
        "proposal_digest_mismatch_count": 0,
        "resolution_count": 2,
        "resolution_digest_mismatch_count": 0,
        "status_change_count": 0,
        "unique_affected_artifact_count": 3,
    }
    if finalization.get("result") != expected_result:
        errors.append("Phase 21 finalization result is invalid")

    authority = finalization.get("authority")
    if not isinstance(authority, Mapping):
        errors.append("Phase 21 authority record is missing")
    else:
        for key in ("automatic_status_change", "automatic_release_action", "repository_mutation"):
            if authority.get(key) is not False:
                errors.append(f"Phase 21 finalization must keep {key}=false")
        if authority.get("status_inheritance") != "prohibited":
            errors.append("Phase 21 finalization must prohibit status inheritance")

    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "Phase 21 state: **offline-policy-resolution-reconciliation-validated**",
        "| 21 | Offline policy-resolution reconciliation | Merged and validated through PR #32 |",
        f"PR #32 was merged into `main` at commit `{EXPECTED_MERGE}`",
        EXPECTED_CANDIDATE_HEAD,
        "release/phase-21-postmerge.json",
        "Historical Phase 21 candidate marker: `exact-head validation pending`",
        "offline-resolution-consequence-planning-candidate",
        "real_authorization_claimed: false",
        "reconciled-resolutions-no-mutation",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 21 finalization marker: {marker}")
    for stale in (
        "**Phase 21 — Offline Policy-Resolution Reconciliation Candidate implemented on `agent/phase-21-policy-resolution-reconciliation`; exact-head validation pending.**",
        "| 21 | Offline policy-resolution reconciliation | Implemented; exact-head validation pending |",
        "Phase 21 target state: **offline-policy-resolution-reconciliation-candidate**",
    ):
        if stale in state:
            errors.append(f"PROJECT_STATE.md retains stale Phase 21 wording: {stale}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        f"> Exact tested head: `{EXPECTED_CANDIDATE_HEAD}`",
        f"> Merge commit: `{EXPECTED_MERGE}`",
        "Final state: `offline-policy-resolution-reconciliation-validated`",
        "release/phase-21-postmerge.json",
        "offline resolution-consequence planning candidate",
        "2 matched resolutions",
        "0 missing resolutions",
        "0 orphan resolutions",
        "real_authorization_claimed: false",
        "reconciled-resolutions-no-mutation",
        "> Live: `false`",
    ):
        if marker not in report:
            errors.append(f"Phase 21 report missing finalization marker: {marker}")
    for stale in (
        "> Candidate state: `offline-policy-resolution-reconciliation-candidate`",
        "exact-head validation remains pending",
    ):
        if stale in report:
            errors.append(f"Phase 21 report retains stale candidate wording: {stale}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/finalize-phase-21-record",
        "scripts/validate_phase21_postmerge_record.py",
        "release/phase-21-postmerge.json",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"Phase 21 workflow missing finalization marker: {marker}")
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
            errors.append(f"Phase 21 workflow contains forbidden token: {forbidden}")

    if errors:
        return fail(errors)
    print(
        "Phase 21 post-merge record passed: PR #32 and exact candidate head pinned, "
        "two proposal/resolution matches integrated, no authorization claimed, and all effects disabled."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("Phase 21 post-merge record errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
