#!/usr/bin/env python3
"""Validate the finalized post-merge Phase 15 governance record."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
RELEASE_PATH = ROOT / "release" / "phase-15-offline-pilot.json"

EXPECTED_HEAD = "6353aa4d05f48e7247ce0323e4a29183c3a28495"
EXPECTED_MERGE = "beeb4d6d4e71d1d08698a000e720fc88fc730ebc"


def main() -> int:
    errors: list[str] = []
    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "Phase 15 — Offline Integration Pilot merged and validated through PR #18",
        "| 15 | Offline integration pilot | Merged and validated through PR #18 |",
        f"PR #18 was merged into `main` at commit `{EXPECTED_MERGE}`",
        "offline-pilot-validated",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing finalized marker: {marker}")
    for stale in (
        "draft PR #18",
        "merge pending",
        "after Phase 15 merge",
    ):
        if stale in state:
            errors.append(f"PROJECT_STATE.md retains stale pre-merge wording: {stale}")

    try:
        release = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"phase-15 release record cannot be read: {exc}")
        release = {}
    principia = release.get("principia")
    if release.get("state") != "offline-pilot-validated":
        errors.append("phase-15 release state must remain offline-pilot-validated")
    if release.get("mode") != "offline-pilot" or release.get("live") is not False:
        errors.append("phase-15 release record must remain offline and live=false")
    if not isinstance(principia, dict):
        errors.append("phase-15 Principia provenance is missing")
    else:
        expected = {
            "pull_request": 18,
            "head_commit": EXPECTED_HEAD,
            "merge_commit": EXPECTED_MERGE,
        }
        for key, value in expected.items():
            if principia.get(key) != value:
                errors.append(f"phase-15 Principia {key} must equal {value}")
    authority = release.get("authority")
    if not isinstance(authority, dict) or any(
        authority.get(key) is not False
        for key in (
            "automatic_status_change",
            "automatic_release_action",
            "repository_mutation",
        )
    ):
        errors.append("phase-15 post-merge record must prohibit automatic mutations")
    if release.get("live_activation_permitted") is not False:
        errors.append("phase-15 post-merge record must not permit live activation")

    if errors:
        print("Phase 15 post-merge record errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "Phase 15 post-merge record passed: PR #18 provenance pinned, offline pilot validated, "
        "status authority separated, and live activation disabled."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
