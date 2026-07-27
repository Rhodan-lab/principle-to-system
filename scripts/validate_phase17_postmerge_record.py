#!/usr/bin/env python3
"""Validate the finalized post-merge Phase 17 governance record."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
CANDIDATE_PATH = ROOT / "release" / "phase-17-offline-event-protocol.json"
FINALIZATION_PATH = ROOT / "release" / "phase-17-postmerge.json"
REPORT_PATH = ROOT / "reports" / "phase-17-offline-event-protocol.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-17-offline-event-protocol.yml"

EXPECTED_CANDIDATE_HEAD = "e260417ef7631ebf4f87c89faff7da45d571b63c"
EXPECTED_MERGE = "c9fba79f821d59b36030924e5c388f71a56f7787"
EXPECTED_CANDIDATE_SHA256 = "fade774fea05b116f6dad307cdcf5219163b6083b175d3be103259857d409c4f"


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
            errors.append(f"missing Phase 17 finalization file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    if sha256_file(CANDIDATE_PATH) != EXPECTED_CANDIDATE_SHA256:
        errors.append("Phase 17 candidate record digest changed after merge")

    finalization = load_json(FINALIZATION_PATH)
    expected_top = {
        "contract": "principia-offline-event-protocol-finalization/0.1",
        "phase": 17,
        "state": "offline-event-protocol-validated",
        "mode": "offline-event-protocol",
        "live": False,
        "next_gate": "offline-reconciliation-simulation-candidate",
        "live_activation_permitted": False,
    }
    for key, value in expected_top.items():
        if finalization.get(key) != value:
            errors.append(f"Phase 17 finalization {key} must equal {value}")

    candidate = finalization.get("candidate_record")
    if candidate != {
        "path": "release/phase-17-offline-event-protocol.json",
        "sha256": EXPECTED_CANDIDATE_SHA256,
    }:
        errors.append("Phase 17 finalization candidate record pin is invalid")

    principia = finalization.get("principia")
    expected_principia = {
        "repository": "Rhodan-lab/principle-to-system",
        "pull_request": 22,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "merge_commit": EXPECTED_MERGE,
    }
    if not isinstance(principia, Mapping):
        errors.append("Phase 17 Principia provenance is missing")
    else:
        for key, value in expected_principia.items():
            if principia.get(key) != value:
                errors.append(f"Phase 17 Principia {key} must equal {value}")

    validation = finalization.get("validation")
    if validation != {
        "applicable_workflows": 13,
        "candidate_head_commit": EXPECTED_CANDIDATE_HEAD,
        "status": "success",
    }:
        errors.append("Phase 17 exact-head validation provenance is invalid")

    authority = finalization.get("authority")
    if not isinstance(authority, Mapping):
        errors.append("Phase 17 authority record is missing")
    else:
        for key in ("automatic_status_change", "automatic_release_action", "repository_mutation"):
            if authority.get(key) is not False:
                errors.append(f"Phase 17 finalization must keep {key}=false")

    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "Phase 17 — Offline Event-Protocol Candidate merged and validated through PR #22",
        "| 17 | Offline event-protocol candidate | Merged and validated through PR #22 |",
        f"PR #22 was merged into `main` at commit `{EXPECTED_MERGE}`",
        EXPECTED_CANDIDATE_HEAD,
        "offline-event-protocol-validated",
        "Phase 18 — Offline Reconciliation Simulation Candidate",
        "live: false",
        "Historical Phase 17 candidate marker: `exact-head validation pending`",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 17 finalization marker: {marker}")
    for stale in (
        "**Phase 17 — Offline Event-Protocol Candidate implemented; exact-head validation pending.**",
        "| 17 | Offline event-protocol candidate | Implemented; exact-head validation pending |",
        "Phase 17 exact-head validation pending. No synchronization or live activation is enabled.",
        "The current gate is exact-head validation of Phase 17.",
    ):
        if stale in state:
            errors.append(f"PROJECT_STATE.md retains stale Phase 17 wording: {stale}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        f"> Exact tested head: `{EXPECTED_CANDIDATE_HEAD}`",
        f"> Merge commit: `{EXPECTED_MERGE}`",
        f"PR #22 was merged into `main` at `{EXPECTED_MERGE}`",
        "offline-event-protocol-validated",
        "offline reconciliation simulation candidate",
        "live: false",
    ):
        if marker not in report:
            errors.append(f"Phase 17 report missing finalization marker: {marker}")
    for stale in (
        "> Exact-head validation: pending",
        "exact-head validation remains pending",
        "must not be promoted beyond `offline-event-protocol-candidate`",
    ):
        if stale in report:
            errors.append(f"Phase 17 report retains stale candidate wording: {stale}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/finalize-phase-17-record",
        "scripts/validate_phase17_postmerge_record.py",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"Phase 17 workflow missing finalization marker: {marker}")
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
            errors.append(f"Phase 17 workflow contains forbidden token: {forbidden}")

    if errors:
        return fail(errors)
    print(
        "Phase 17 post-merge record passed: PR #22 and exact candidate head pinned, "
        "offline event protocol integrated, authority separated, and live activation disabled."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("Phase 17 post-merge record errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
