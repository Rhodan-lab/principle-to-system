#!/usr/bin/env python3
"""Validate the finalized post-merge Phase 16 governance record."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
RELEASE_PATH = ROOT / "release" / "phase-16-offline-multi-artifact-pilot.json"
REPORT_PATH = ROOT / "reports" / "phase-16-offline-multi-artifact-pilot.md"

EXPECTED_CANDIDATE = "67d6ec98c51188dabcffd48dad968a83653ea584"
EXPECTED_HEAD = "d37674490f054241ef08ccf7a644247b444fa874"
EXPECTED_MERGE = "c493bf879a7945f9991e13592d42424138a0879b"


def main() -> int:
    errors: list[str] = []
    state = STATE_PATH.read_text(encoding="utf-8")
    report = REPORT_PATH.read_text(encoding="utf-8")

    required_state = (
        "Phase 16 — Offline Multi-Artifact Integration Pilot merged and validated through PR #20",
        "| 16 | Offline multi-artifact integration pilot | Merged and validated through PR #20 |",
        f"PR #20 was merged into `main` at commit `{EXPECTED_MERGE}`",
        EXPECTED_CANDIDATE,
        EXPECTED_HEAD,
        "offline-multi-artifact-validated",
        "live: false",
    )
    for marker in required_state:
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing finalized marker: {marker}")

    for stale in (
        "PR #20; the PR remains unmerged",
        "draft PR #20; unmerged",
        "Repository integration remains a separate explicit action",
    ):
        if stale in state:
            errors.append(f"PROJECT_STATE.md retains stale Phase 16 wording: {stale}")

    for marker in (EXPECTED_HEAD, EXPECTED_MERGE, "offline-multi-artifact-validated"):
        if marker not in report:
            errors.append(f"Phase 16 report missing finalized marker: {marker}")

    try:
        release = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Phase 16 release record cannot be read: {exc}")
        release = {}

    if release.get("state") != "offline-multi-artifact-validated":
        errors.append("Phase 16 state must remain offline-multi-artifact-validated")
    if release.get("mode") != "offline-multi-artifact-pilot" or release.get("live") is not False:
        errors.append("Phase 16 must remain offline and live=false")

    principia = release.get("principia")
    expected_principia = {
        "branch": "main",
        "pull_request": 20,
        "head_commit": EXPECTED_HEAD,
        "merge_commit": EXPECTED_MERGE,
    }
    if not isinstance(principia, dict):
        errors.append("Phase 16 Principia provenance is missing")
    else:
        for key, value in expected_principia.items():
            if principia.get(key) != value:
                errors.append(f"Phase 16 Principia {key} must equal {value}")

    validation = release.get("validation")
    expected_validation = {
        "status": "success",
        "pull_request": 20,
        "candidate_head_commit": EXPECTED_CANDIDATE,
        "tested_head_commit": EXPECTED_HEAD,
        "merge_commit": EXPECTED_MERGE,
    }
    if not isinstance(validation, dict):
        errors.append("Phase 16 validation provenance is missing")
    else:
        for key, value in expected_validation.items():
            if validation.get(key) != value:
                errors.append(f"Phase 16 validation {key} must equal {value}")

    atlas = release.get("atlas")
    if not isinstance(atlas, dict):
        errors.append("Phase 16 Atlas baseline is missing")
    else:
        expected_atlas = {
            "implementation_merge_commit": "1cc4aec6908a8703a7f505478329c633a23b4ef9",
            "governance_merge_commit": "9370cc746e9756e433ac3772d56d079c9803b144",
            "mode": "importer-candidate",
            "live": False,
        }
        for key, value in expected_atlas.items():
            if atlas.get(key) != value:
                errors.append(f"Phase 16 Atlas {key} must equal {value}")

    authority = release.get("authority")
    if not isinstance(authority, dict) or any(
        authority.get(key) is not False
        for key in (
            "automatic_status_change",
            "automatic_release_action",
            "repository_mutation",
        )
    ):
        errors.append("Phase 16 must prohibit automatic status, release, and repository mutation")

    if release.get("live_activation_permitted") is not False:
        errors.append("Phase 16 must not permit live activation")
    if release.get("next_gate") != "offline-event-protocol-candidate":
        errors.append("Phase 16 next gate must remain offline-event-protocol-candidate")

    if errors:
        print("Phase 16 post-merge record errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Phase 16 post-merge record passed: PR #20 provenance pinned, atomic offline pilot "
        "validated, status authority separated, and live activation disabled."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
