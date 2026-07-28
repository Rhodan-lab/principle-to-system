#!/usr/bin/env python3
"""Validate the immutable Phase 19 offline reconciliation-policy candidate."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_phase19_offline_reconciliation_policy import (  # noqa: E402
    AUTHORITY,
    HOLD_PROPOSALS_PATH,
    LEDGER_PATH,
    PHASE18_FINALIZATION_MERGE,
    PHASE18_POSTMERGE_SHA256,
    RECOVERY_PATH,
    RELEASE_PATH,
    REVIEW_QUEUE_PATH,
    SOURCE_REPORT_SHA256,
    PolicyError,
    build_bundle,
    load_json,
    render_json,
    validate_policy_bundle,
)

REPORT_PATH = ROOT / "reports" / "phase-19-offline-reconciliation-policy.md"
STATE_PATH = ROOT / "PROJECT_STATE.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-19-offline-reconciliation-policy.yml"


def main() -> int:
    errors: list[str] = []
    for path in (
        REVIEW_QUEUE_PATH,
        HOLD_PROPOSALS_PATH,
        LEDGER_PATH,
        RECOVERY_PATH,
        RELEASE_PATH,
        REPORT_PATH,
        STATE_PATH,
        WORKFLOW_PATH,
    ):
        if not path.is_file():
            errors.append(f"missing Phase 19 file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    try:
        queue = load_json(REVIEW_QUEUE_PATH)
        holds = load_json(HOLD_PROPOSALS_PATH)
        ledger = load_json(LEDGER_PATH)
        recovery = load_json(RECOVERY_PATH)
        validate_policy_bundle(queue, holds, ledger, recovery)
        for path, value in build_bundle().items():
            if path.read_text(encoding="utf-8") != render_json(value):
                errors.append(f"Phase 19 generated artifact drift: {path.relative_to(ROOT)}")
    except (OSError, json.JSONDecodeError, KeyError, PolicyError, ValueError) as exc:
        errors.append(f"Phase 19 policy validation failed: {exc}")

    release = load_json(RELEASE_PATH)
    expected_top = {
        "contract": "principia-offline-reconciliation-policy/0.1",
        "phase": 19,
        "state": "offline-reconciliation-policy-candidate",
        "mode": "offline-reconciliation-policy",
        "live": False,
        "live_activation_permitted": False,
        "next_gate": "offline-manual-policy-resolution-candidate",
    }
    for key, value in expected_top.items():
        if release.get(key) != value:
            errors.append(f"Phase 19 release {key} must equal {value}")
    if release.get("authority") != AUTHORITY:
        errors.append("Phase 19 release authority boundary is invalid")
    if release.get("source_phase18") != {
        "phase18_finalization_merge_commit": PHASE18_FINALIZATION_MERGE,
        "phase18_postmerge_path": "release/phase-18-postmerge.json",
        "phase18_postmerge_sha256": PHASE18_POSTMERGE_SHA256,
        "reconciliation_id": "principia-atlas:offline-reconciliation:thermal-control:0001",
        "reconciliation_path": "integration/principia-atlas/pilot/thermal-control.reconciliation-report.v01.json",
        "reconciliation_sha256": SOURCE_REPORT_SHA256,
    }:
        errors.append("Phase 19 release does not pin finalized Phase 18")
    if release.get("result") != {
        "decision": "proposals-recorded-no-mutation",
        "effective_hold_count": 0,
        "hold_proposal_count": 1,
        "manual_review_item_count": 1,
        "unique_affected_artifact_count": 3,
    }:
        errors.append("Phase 19 release result is invalid")
    if release.get("validation") != {
        "pull_request": None,
        "status": "pending",
        "tested_head_commit": None,
    }:
        errors.append("Phase 19 candidate validation fields must remain pending")

    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "Phase 19 state: **offline-reconciliation-policy-validated**",
        "| 19 | Offline reconciliation policy | Merged and validated through PR #28 |",
        "Historical Phase 19 candidate marker: `exact-head validation pending`",
        PHASE18_FINALIZATION_MERGE,
        "proposals-recorded-no-mutation",
        "release-hold proposal",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 19 marker: {marker}")
    # Later phases may describe the same immutable record as either a queue or an item.
    # Accept both phrases while retaining all machine-readable policy checks above.
    if "manual review queue" not in state and "manual review item" not in state:
        errors.append(
            "PROJECT_STATE.md missing Phase 19 marker: manual review queue or manual review item"
        )

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        "# Phase 19 — Offline Reconciliation Policy",
        "`principia-offline-review-queue/0.1`",
        "`principia-offline-release-hold-proposals/0.1`",
        "`principia-offline-reconciliation-policy-ledger/0.1`",
        "1 manual review item",
        "1 release-hold proposal",
        "0 effective holds",
        "proposals-recorded-no-mutation",
        "live: false",
    ):
        if marker not in report:
            errors.append(f"Phase 19 report missing marker: {marker}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/phase-19-offline-reconciliation-policy",
        "scripts/generate_phase19_offline_reconciliation_policy.py --check",
        "scripts/validate_phase19_offline_reconciliation_policy.py",
        "software.tests.test_phase19_offline_reconciliation_policy",
        "scripts/validate_phase18_postmerge_record.py",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"Phase 19 workflow missing marker: {marker}")
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
        "Phase 19 policy candidate passed: manual review and non-effective hold proposals "
        "are digest-bound to finalized Phase 18 with no mutation or live integration."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("Phase 19 validation errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
