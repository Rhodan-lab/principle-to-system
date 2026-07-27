#!/usr/bin/env python3
"""Validate the finalized post-merge Phase 19 governance record."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
CANDIDATE_PATH = ROOT / "release" / "phase-19-offline-reconciliation-policy.json"
FINALIZATION_PATH = ROOT / "release" / "phase-19-postmerge.json"
REPORT_PATH = ROOT / "reports" / "phase-19-offline-reconciliation-policy.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-19-offline-reconciliation-policy.yml"

EXPECTED_CANDIDATE_HEAD = "da77e4b1a5f6f17e98a38f0438c5531d0fba5aac"
EXPECTED_MERGE = "699689c7a60da645d59cf2bdfe169b89f137a899"
EXPECTED_CANDIDATE_SHA256 = "077bace5a433bafe26550186fb7bc03740125d7af06c406b3745377639275fed"


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
            errors.append(f"missing Phase 19 finalization file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    if sha256_file(CANDIDATE_PATH) != EXPECTED_CANDIDATE_SHA256:
        errors.append("Phase 19 candidate record digest changed after merge")

    finalization = load_json(FINALIZATION_PATH)
    expected_top = {
        "contract": "principia-offline-reconciliation-policy-finalization/0.1",
        "phase": 19,
        "state": "offline-reconciliation-policy-validated",
        "mode": "offline-reconciliation-policy",
        "live": False,
        "next_gate": "offline-manual-policy-resolution-candidate",
        "live_activation_permitted": False,
    }
    for key, value in expected_top.items():
        if finalization.get(key) != value:
            errors.append(f"Phase 19 finalization {key} must equal {value}")

    if finalization.get("candidate_record") != {
        "path": "release/phase-19-offline-reconciliation-policy.json",
        "sha256": EXPECTED_CANDIDATE_SHA256,
    }:
        errors.append("Phase 19 finalization candidate record pin is invalid")

    principia = finalization.get("principia")
    expected_principia = {
        "repository": "Rhodan-lab/principle-to-system",
        "pull_request": 28,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "merge_commit": EXPECTED_MERGE,
    }
    if not isinstance(principia, Mapping):
        errors.append("Phase 19 Principia provenance is missing")
    else:
        for key, value in expected_principia.items():
            if principia.get(key) != value:
                errors.append(f"Phase 19 Principia {key} must equal {value}")

    if finalization.get("validation") != {
        "applicable_workflows": 15,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "status": "success",
    }:
        errors.append("Phase 19 exact-head validation provenance is invalid")

    if finalization.get("result") != {
        "decision": "proposals-recorded-no-mutation",
        "effective_hold_count": 0,
        "hold_proposal_count": 1,
        "manual_review_item_count": 1,
        "unique_affected_artifact_count": 3,
    }:
        errors.append("Phase 19 finalization result is invalid")

    authority = finalization.get("authority")
    if not isinstance(authority, Mapping):
        errors.append("Phase 19 authority record is missing")
    else:
        for key in ("automatic_status_change", "automatic_release_action", "repository_mutation"):
            if authority.get(key) is not False:
                errors.append(f"Phase 19 finalization must keep {key}=false")
        if authority.get("status_inheritance") != "prohibited":
            errors.append("Phase 19 finalization must prohibit status inheritance")

    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "Phase 19 state: **offline-reconciliation-policy-validated**",
        "| 19 | Offline reconciliation policy | Merged and validated through PR #28 |",
        f"PR #28 was merged into `main` at commit `{EXPECTED_MERGE}`",
        EXPECTED_CANDIDATE_HEAD,
        "release/phase-19-postmerge.json",
        "Historical Phase 19 candidate marker: `exact-head validation pending`",
        "offline manual-policy-resolution candidate",
        "proposals-recorded-no-mutation",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 19 finalization marker: {marker}")
    for stale in (
        "**Phase 19 — Offline Reconciliation Policy Candidate implemented on `agent/phase-19-offline-reconciliation-policy`; exact-head validation pending.**",
        "| 19 | Offline reconciliation policy | Implemented; exact-head validation pending |",
        "Phase 19 target state: **offline-reconciliation-policy-candidate**",
    ):
        if stale in state:
            errors.append(f"PROJECT_STATE.md retains stale Phase 19 wording: {stale}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        f"> Exact tested head: `{EXPECTED_CANDIDATE_HEAD}`",
        f"> Merge commit: `{EXPECTED_MERGE}`",
        "Final state: `offline-reconciliation-policy-validated`",
        "release/phase-19-postmerge.json",
        "offline manual-policy-resolution candidate",
        "0 effective holds",
        "proposals-recorded-no-mutation",
        "> Live: `false`",
    ):
        if marker not in report:
            errors.append(f"Phase 19 report missing finalization marker: {marker}")
    for stale in (
        "> Candidate state: `offline-reconciliation-policy-candidate`",
        "exact-head validation remains pending",
    ):
        if stale in report:
            errors.append(f"Phase 19 report retains stale candidate wording: {stale}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/finalize-phase-19-record",
        "scripts/validate_phase19_postmerge_record.py",
        "release/phase-19-postmerge.json",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"Phase 19 workflow missing finalization marker: {marker}")
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
            errors.append(f"Phase 19 workflow contains forbidden token: {forbidden}")

    if errors:
        return fail(errors)
    print(
        "Phase 19 post-merge record passed: PR #28 and exact candidate head pinned, "
        "policy proposals integrated, authority separated, and automatic execution disabled."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("Phase 19 post-merge record errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
