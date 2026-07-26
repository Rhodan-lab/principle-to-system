#!/usr/bin/env python3
"""Validate the Phase 15 offline Principia–Atlas integration pilot."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Mapping

from generate_phase15_offline_pilot import (
    EXPECTED_DEPENDENCIES,
    EXPORT_PATH,
    IMPACT_PATH,
    RECEIPT_PATH,
    ROOT,
    SNAPSHOT_PATH,
    check_outputs,
    load_json,
    validate_inputs,
)

REPORT_PATH = ROOT / "reports" / "phase-15-offline-integration-pilot.md"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "validate-phase-15-offline-pilot.yml"
PROJECT_STATE_PATH = ROOT / "PROJECT_STATE.md"
README_PATH = ROOT / "integration" / "principia-atlas" / "README.md"

PROHIBITED_STATUS_KEYS = {
    "status",
    "pedagogical_status",
    "release_status",
    "knowledge_status",
    "atlas_status",
    "review_status",
}

EXPECTED_SCENARIOS = {
    ("current", "current"): ("inspect", "principia-declared-policy"),
    ("deprecated", "current"): ("revalidate", "atlas-entity-deprecated"),
    ("draft", "review-required"): (
        "revalidate",
        "atlas-staleness-review-required",
    ),
    ("draft", "confirmed-stale"): (
        "revalidate",
        "atlas-staleness-confirmed-stale",
    ),
    ("retracted", "current"): ("block-release", "atlas-entity-retracted"),
}


def find_prohibited_key(value: Any, path: str = "$") -> str | None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            if key_text in PROHIBITED_STATUS_KEYS:
                return f"{path}.{key_text}"
            found = find_prohibited_key(item, f"{path}.{key_text}")
            if found:
                return found
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found = find_prohibited_key(item, f"{path}[{index}]")
            if found:
                return found
    return None


def validate_receipt(receipt: Mapping[str, Any]) -> None:
    if receipt.get("contract") != "principia-atlas-offline-import-receipt/0.1":
        raise ValueError("E-PILOT-CONTRACT")
    if receipt.get("mode") != "offline-pilot" or receipt.get("live") is not False:
        raise ValueError("E-PILOT-LIVE")
    prohibited = find_prohibited_key(receipt)
    if prohibited:
        raise ValueError(f"E-PILOT-STATUS:{prohibited}")
    importer = receipt.get("atlas_importer")
    if not isinstance(importer, Mapping):
        raise ValueError("E-PILOT-ATLAS-PIN")
    if (
        importer.get("repository") != "Rhodan-lab/Atlas"
        or importer.get("pull_request") != 20
        or importer.get("head_commit")
        != "379d88d620469a749cebb88b0b41d9960e667558"
        or importer.get("merge_commit")
        != "1cc4aec6908a8703a7f505478329c633a23b4ef9"
    ):
        raise ValueError("E-PILOT-ATLAS-PIN")
    result = receipt.get("result")
    if not isinstance(result, Mapping) or result.get("accepted") is not True:
        raise ValueError("E-PILOT-RECEIPT")
    if result.get("status_inheritance") != "prohibited":
        raise ValueError("E-PILOT-AUTHORITY")
    dependencies = result.get("dependencies")
    if not isinstance(dependencies, list):
        raise ValueError("E-PILOT-DEPENDENCIES")
    exact = {
        str(item.get("id")): item.get("revision")
        for item in dependencies
        if isinstance(item, Mapping)
    }
    if exact != EXPECTED_DEPENDENCIES:
        raise ValueError("E-PILOT-REVISION")
    if any(item.get("resolution") != "current" for item in dependencies):
        raise ValueError("E-PILOT-RESOLUTION")
    authority = receipt.get("authority")
    if not isinstance(authority, Mapping):
        raise ValueError("E-PILOT-AUTHORITY")
    if any(
        authority.get(key) is not False
        for key in (
            "automatic_status_change",
            "automatic_release_action",
            "repository_mutation",
        )
    ):
        raise ValueError("E-PILOT-AUTHORITY")


def validate_lifecycle_matrix(matrix: Mapping[str, Any]) -> None:
    if matrix.get("contract") != "principia-atlas-offline-lifecycle-matrix/0.1":
        raise ValueError("E-PILOT-IMPACT-CONTRACT")
    if matrix.get("mode") != "offline-pilot" or matrix.get("live") is not False:
        raise ValueError("E-PILOT-IMPACT-LIVE")
    if matrix.get("target") != "model:en:delayed-correction-recurrence@2":
        raise ValueError("E-PILOT-IMPACT-TARGET")
    if matrix.get("automatic_status_change") is not False:
        raise ValueError("E-PILOT-IMPACT-MUTATION")
    if matrix.get("automatic_release_action") is not False:
        raise ValueError("E-PILOT-IMPACT-MUTATION")
    scenarios = matrix.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != len(EXPECTED_SCENARIOS):
        raise ValueError("E-PILOT-IMPACT-SCENARIOS")
    observed = {}
    for scenario in scenarios:
        if not isinstance(scenario, Mapping):
            raise ValueError("E-PILOT-IMPACT-SCENARIO")
        key = (scenario.get("atlas_entity_state"), scenario.get("atlas_staleness"))
        observed[key] = (scenario.get("effective_action"), scenario.get("reason"))
    if observed != EXPECTED_SCENARIOS:
        raise ValueError("E-PILOT-IMPACT-POLICY")


def validate_negative_paths(receipt: Mapping[str, Any]) -> None:
    mutations = []

    live = copy.deepcopy(receipt)
    live["live"] = True
    mutations.append((live, "E-PILOT-LIVE"))

    inherited = copy.deepcopy(receipt)
    inherited["result"]["pedagogical_status"] = "reviewed"
    mutations.append((inherited, "E-PILOT-STATUS"))

    stale_revision = copy.deepcopy(receipt)
    for dependency in stale_revision["result"]["dependencies"]:
        if dependency["id"] == "model:en:delayed-correction-recurrence":
            dependency["revision"] = 1
            dependency["key"] = "model:en:delayed-correction-recurrence@1"
    mutations.append((stale_revision, "E-PILOT-REVISION"))

    unpinned = copy.deepcopy(receipt)
    unpinned["atlas_importer"]["merge_commit"] = ""
    mutations.append((unpinned, "E-PILOT-ATLAS-PIN"))

    mutating = copy.deepcopy(receipt)
    mutating["authority"]["automatic_status_change"] = True
    mutations.append((mutating, "E-PILOT-AUTHORITY"))

    for payload, expected in mutations:
        try:
            validate_receipt(payload)
        except ValueError as exc:
            if expected not in str(exc):
                raise ValueError(
                    f"E-PILOT-NEGATIVE-EXPECTED:{expected}:got:{exc}"
                ) from exc
        else:
            raise ValueError(f"E-PILOT-NEGATIVE-ACCEPTED:{expected}")


def validate_records(errors: list[str]) -> None:
    required = [
        EXPORT_PATH,
        SNAPSHOT_PATH,
        RECEIPT_PATH,
        IMPACT_PATH,
        REPORT_PATH,
        WORKFLOW_PATH,
        PROJECT_STATE_PATH,
        README_PATH,
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing required Phase 15 file: {path.relative_to(ROOT)}")

    if errors:
        return

    export = load_json(EXPORT_PATH)
    snapshot = load_json(SNAPSHOT_PATH)
    receipt = load_json(RECEIPT_PATH)
    matrix = load_json(IMPACT_PATH)
    try:
        validate_inputs(export, snapshot)
        validate_receipt(receipt)
        validate_lifecycle_matrix(matrix)
        validate_negative_paths(receipt)
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(str(exc))

    observation = snapshot.get("governance_observation")
    if not isinstance(observation, Mapping) or observation.get("blocking") is not False:
        errors.append("Atlas governance wording observation must remain explicit and non-blocking")

    state = PROJECT_STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "Phase 15 — Offline Integration Pilot",
        "offline-pilot-validated",
        "live: false",
        "Atlas PR #20",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 15 marker: {marker}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        "principia-atlas-offline-import-receipt/0.1",
        "1cc4aec6908a8703a7f505478329c633a23b4ef9",
        "No live cross-repository call",
    ):
        if marker not in report:
            errors.append(f"Phase 15 report missing marker: {marker}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    if "contents: read" not in workflow:
        errors.append("Phase 15 workflow must use contents: read")
    forbidden = (
        "contents" + ": write",
        "git " + "push",
        "git " + "commit",
        "pull_request" + "_target",
        "actions/checkout" + "@v4\n        with:\n          repository: Rhodan-lab/Atlas",
        "curl ",
        "wget ",
    )
    for token in forbidden:
        if token in workflow:
            errors.append(f"Phase 15 workflow contains forbidden token: {token}")


def main() -> int:
    errors: list[str] = []
    if check_outputs() != 0:
        errors.append("Phase 15 deterministic artifacts are stale")
    validate_records(errors)
    if errors:
        print("Phase 15 offline pilot errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "Phase 15 offline pilot passed: exact Principia export, pinned Atlas PR #20 "
        "import receipt, lifecycle matrix, status separation, and live=false boundary."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
