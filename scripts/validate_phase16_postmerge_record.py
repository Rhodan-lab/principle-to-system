#!/usr/bin/env python3
"""Validate the finalized post-merge Phase 16 governance record."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"
RELEASE_PATH = ROOT / "release" / "phase-16-offline-multi-artifact-pilot.json"
REPORT_PATH = ROOT / "reports" / "phase-16-offline-multi-artifact-pilot.md"

EXPECTED_CANDIDATE_HEAD = "67d6ec98c51188dabcffd48dad968a83653ea584"
EXPECTED_VALIDATED_HEAD = "d37674490f054241ef08ccf7a644247b444fa874"
EXPECTED_MERGE = "c493bf879a7945f9991e13592d42424138a0879b"


def main() -> int:
    errors: list[str] = []

    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "| 16 | Offline multi-artifact integration pilot | Merged and validated through PR #20 |",
        "Phase 16 state: **offline-multi-artifact-validated**",
        f"PR #20 was merged into `main` at commit `{EXPECTED_MERGE}`",
        EXPECTED_CANDIDATE_HEAD,
        EXPECTED_VALIDATED_HEAD,
        "offline-multi-artifact-validated",
        "Phase 17 — Offline Event-Protocol Candidate",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing finalized marker: {marker}")

    for stale in (
        "PR #20; the PR remains unmerged",
        "| 16 | Offline multi-artifact integration pilot | Implemented and validated on draft PR #20; unmerged |",
        "Repository integration remains a separate explicit action",
        "After Phase 16 is integrated",
    ):
        if stale in state:
            errors.append(f"PROJECT_STATE.md retains stale pre-merge wording: {stale}")

    try:
        release = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"phase-16 release record cannot be read: {exc}")
        release = {}

    if release.get("state") != "offline-multi-artifact-validated":
        errors.append("phase-16 release state must remain offline-multi-artifact-validated")
    if release.get("mode") != "offline-multi-artifact-pilot" or release.get("live") is not False:
        errors.append("phase-16 release record must remain offline and live=false")

    principia = release.get("principia")
    if not isinstance(principia, Mapping):
        errors.append("phase-16 Principia provenance is missing")
    else:
        expected_principia = {
            "repository": "Rhodan-lab/principle-to-system",
            "branch": "main",
            "pull_request": 20,
            "head_commit": EXPECTED_VALIDATED_HEAD,
            "merge_commit": EXPECTED_MERGE,
        }
        for key, value in expected_principia.items():
            if principia.get(key) != value:
                errors.append(f"phase-16 Principia {key} must equal {value}")
        artifacts = principia.get("artifacts")
        if not isinstance(artifacts, list) or len(artifacts) != 3:
            errors.append("phase-16 Principia provenance must retain exactly three artifacts")

    validation = release.get("validation")
    if not isinstance(validation, Mapping):
        errors.append("phase-16 validation provenance is missing")
    else:
        expected_validation = {
            "status": "success",
            "pull_request": 20,
            "tested_head_commit": EXPECTED_CANDIDATE_HEAD,
            "validated_record_head_commit": EXPECTED_VALIDATED_HEAD,
            "merge_commit": None,
            "integration_merge_commit": EXPECTED_MERGE,
        }
        for key, value in expected_validation.items():
            if validation.get(key) != value:
                errors.append(f"phase-16 validation {key} must equal {value}")

    atlas = release.get("atlas")
    if not isinstance(atlas, Mapping):
        errors.append("phase-16 Atlas provenance is missing")
    else:
        expected_atlas = {
            "repository": "Rhodan-lab/Atlas",
            "implementation_merge_commit": "1cc4aec6908a8703a7f505478329c633a23b4ef9",
            "governance_merge_commit": "9370cc746e9756e433ac3772d56d079c9803b144",
            "mode": "importer-candidate",
            "live": False,
        }
        for key, value in expected_atlas.items():
            if atlas.get(key) != value:
                errors.append(f"phase-16 Atlas {key} must equal {value}")

    contracts = release.get("contracts")
    if not isinstance(contracts, Mapping) or contracts.get("wire") != "principia-atlas-external-dependent/0.2":
        errors.append("phase-16 wire contract must remain principia-atlas-external-dependent/0.2")

    authority = release.get("authority")
    if not isinstance(authority, Mapping) or any(
        authority.get(key) is not False
        for key in (
            "automatic_status_change",
            "automatic_release_action",
            "repository_mutation",
        )
    ):
        errors.append("phase-16 post-merge record must prohibit automatic mutations")
    if release.get("live_activation_permitted") is not False:
        errors.append("phase-16 post-merge record must not permit live activation")
    if release.get("next_gate") != "offline-event-protocol-candidate":
        errors.append("phase-16 next gate must remain offline-event-protocol-candidate")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        f"> Final tested head: `{EXPECTED_VALIDATED_HEAD}`",
        f"> Merge commit: `{EXPECTED_MERGE}`",
        f"PR #20 was merged into `main` at `{EXPECTED_MERGE}`",
        "offline event-protocol candidate",
        "live: false",
    ):
        if marker not in report:
            errors.append(f"Phase 16 report missing finalized marker: {marker}")
    for stale in (
        "Merge remains a separate explicit repository action",
        "merge remains pending",
        "the PR remains unmerged",
    ):
        if stale in report:
            errors.append(f"Phase 16 report retains stale pre-merge wording: {stale}")

    if errors:
        print("Phase 16 post-merge record errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Phase 16 post-merge record passed: PR #20 provenance pinned, three-artifact "
        "offline pilot integrated, status authority separated, and live activation disabled."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
