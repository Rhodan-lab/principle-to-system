#!/usr/bin/env python3
"""Validate the Phase 11B controlled material expansion without writing files."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

import validate_experiences as base

ROOT = Path(__file__).resolve().parent.parent
INVENTORY_PATH = ROOT / "experiences" / "phase-11b-inventory.json"
REPORT_PATH = ROOT / "reports" / "phase-11b-controlled-material-expansion.md"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "validate-phase-11b-expansion.yml"

TYPE_TO_DIR = {
    "system-dossier": "system-dossiers",
    "failure-pattern": "failure-atlas",
    "investigation": "investigations",
    "design-challenge": "design-challenges",
}

NEW_ROUTE_IDS = {
    "resilient-energy",
    "water-infrastructure",
    "distributed-information",
}

REQUIRED_ROUTE_MARKERS = {
    "resilient-energy": (
        "solar",
        "Do not",
    ),
    "water-infrastructure": (
        "drinking water",
        "non-potable",
    ),
    "distributed-information": (
        "synthetic",
        "Do not",
    ),
}

BANNED_RELEASE_TEXT = (
    "release_status: released",
    "release_status: complete",
    "status: complete",
)


def parse_inventory(errors: list[str]) -> dict[str, object]:
    try:
        inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{INVENTORY_PATH.relative_to(ROOT)}: invalid inventory: {exc}")
        return {}
    if inventory.get("schema") != "principia-experience-expansion/0.1":
        errors.append("Phase 11B inventory has the wrong schema")
    if inventory.get("phase") != "11B":
        errors.append("Phase 11B inventory must declare phase 11B")
    return inventory


def collect_artifacts(inventory: dict[str, object], errors: list[str]) -> list[dict[str, str]]:
    routes = inventory.get("routes")
    if not isinstance(routes, list):
        errors.append("Phase 11B inventory routes must be a list")
        return []
    if len(routes) != 4:
        errors.append(f"Phase 11B requires exactly 4 routes, found {len(routes)}")

    route_ids: set[str] = set()
    artifacts: list[dict[str, str]] = []
    for route in routes:
        if not isinstance(route, dict):
            errors.append("Phase 11B route entry must be an object")
            continue
        route_id = route.get("id")
        if not isinstance(route_id, str) or not route_id:
            errors.append("Phase 11B route is missing an id")
            continue
        if route_id in route_ids:
            errors.append(f"duplicate route id: {route_id}")
        route_ids.add(route_id)
        if route.get("status") != "reviewed":
            errors.append(f"route {route_id}: status must be reviewed")
        route_artifacts = route.get("artifacts")
        if not isinstance(route_artifacts, list) or len(route_artifacts) != 4:
            errors.append(f"route {route_id}: expected exactly four artifacts")
            continue
        types = Counter()
        for artifact in route_artifacts:
            if not isinstance(artifact, dict):
                errors.append(f"route {route_id}: artifact must be an object")
                continue
            path = artifact.get("path")
            slug = artifact.get("slug")
            artifact_type = artifact.get("type")
            if not all(isinstance(value, str) and value for value in (path, slug, artifact_type)):
                errors.append(f"route {route_id}: artifact is missing path, slug, or type")
                continue
            if artifact_type not in TYPE_TO_DIR:
                errors.append(f"route {route_id}: unknown artifact type {artifact_type}")
                continue
            if not path.startswith(TYPE_TO_DIR[artifact_type] + "/"):
                errors.append(f"route {route_id}: {path} is not in the expected family directory")
            types[artifact_type] += 1
            artifacts.append({
                "route": route_id,
                "path": path,
                "slug": slug,
                "type": artifact_type,
            })
        for expected_type in TYPE_TO_DIR:
            if types[expected_type] != 1:
                errors.append(f"route {route_id}: expected one {expected_type}, found {types[expected_type]}")

    if route_ids != {"thermal-control", *NEW_ROUTE_IDS}:
        errors.append(f"Phase 11B route ids do not match the canonical four routes: {sorted(route_ids)}")
    if len(artifacts) != 16:
        errors.append(f"Phase 11B requires exactly 16 artifacts, found {len(artifacts)}")
    paths = [item["path"] for item in artifacts]
    slugs = [item["slug"] for item in artifacts]
    if len(set(paths)) != len(paths):
        errors.append("Phase 11B inventory contains duplicate artifact paths")
    if len(set(slugs)) != len(slugs):
        errors.append("Phase 11B inventory contains duplicate artifact slugs")
    return artifacts


def configure_base_validator(artifacts: list[dict[str, str]]) -> None:
    base.EXPERIENCE_FILES = {
        item["path"]: item["type"]
        for item in artifacts
    }
    base.REQUIRED_FIELDS = tuple(dict.fromkeys((*base.REQUIRED_FIELDS, "artifact_revision", "release_status")))


def validate_artifact_metadata(artifacts: list[dict[str, str]], errors: list[str]) -> None:
    report = base.Report()
    for item in artifacts:
        path = ROOT / item["path"]
        if not path.is_file():
            errors.append(f"missing experience artifact: {item['path']}")
            continue
        document = base.read_document(path, report)
        if document is None:
            continue
        fm = document.frontmatter
        if fm.get("slug") != item["slug"]:
            errors.append(f"{item['path']}: slug does not match inventory")
        if fm.get("experience_type") != item["type"]:
            errors.append(f"{item['path']}: experience_type does not match inventory")
        if fm.get("status") != "reviewed":
            errors.append(f"{item['path']}: pedagogical status must be reviewed")
        if fm.get("release_status") != "draft":
            errors.append(f"{item['path']}: release_status must remain draft before Phase 12")
        revision = fm.get("artifact_revision")
        try:
            revision_value = int(str(revision))
        except (TypeError, ValueError):
            errors.append(f"{item['path']}: artifact_revision must be a positive integer")
        else:
            if revision_value != 1:
                errors.append(f"{item['path']}: Phase 11B inventory expects artifact_revision 1")
        text = path.read_text(encoding="utf-8")
        for banned in BANNED_RELEASE_TEXT:
            if banned in text:
                errors.append(f"{item['path']}: prohibited premature completion marker: {banned}")
        if item["route"] in NEW_ROUTE_IDS and "last_reviewed: 2026-07-26" not in text:
            errors.append(f"{item['path']}: new Phase 11B artifact must use last_reviewed 2026-07-26")

    errors.extend(report.errors)


def validate_route_boundaries(artifacts: list[dict[str, str]], errors: list[str]) -> None:
    by_route: dict[str, str] = {}
    for item in artifacts:
        path = ROOT / item["path"]
        if path.is_file():
            by_route[item["route"]] = by_route.get(item["route"], "") + "\n" + path.read_text(encoding="utf-8")

    for route_id, markers in REQUIRED_ROUTE_MARKERS.items():
        route_text = by_route.get(route_id, "")
        for marker in markers:
            if marker.lower() not in route_text.lower():
                errors.append(f"route {route_id}: missing safety or scope marker: {marker}")

    energy = by_route.get("resilient-energy", "").lower()
    for marker in ("do not construct", "do not test islanding", "simulation"):
        if marker not in energy:
            errors.append(f"resilient-energy route missing electrical safety boundary: {marker}")

    water = by_route.get("water-infrastructure", "").lower()
    for marker in ("not a procedure for producing safe drinking water", "non-potable use only", "do not drink"):
        if marker not in water:
            errors.append(f"water-infrastructure route missing public-health boundary: {marker}")

    info = by_route.get("distributed-information", "").lower()
    for marker in ("do not send automated traffic", "do not test against a real", "synthetic traffic"):
        if marker not in info:
            errors.append(f"distributed-information route missing live-system boundary: {marker}")


def validate_navigation(artifacts: list[dict[str, str]], errors: list[str]) -> None:
    family_indexes = {
        "system-dossier": ROOT / "system-dossiers" / "README.md",
        "failure-pattern": ROOT / "failure-atlas" / "README.md",
        "investigation": ROOT / "investigations" / "README.md",
        "design-challenge": ROOT / "design-challenges" / "README.md",
    }
    central = ROOT / "experiences" / "README.md"
    central_text = central.read_text(encoding="utf-8") if central.is_file() else ""
    for route_id in ("thermal-control", *sorted(NEW_ROUTE_IDS)):
        if route_id not in central_text:
            errors.append(f"experiences/README.md: missing route id {route_id}")
    for item in artifacts:
        index = family_indexes[item["type"]]
        text = index.read_text(encoding="utf-8") if index.is_file() else ""
        filename = Path(item["path"]).name
        if filename not in text:
            errors.append(f"{index.relative_to(ROOT)}: missing navigation link to {filename}")


def count_ledger_rows(errors: list[str]) -> int:
    path = ROOT / "sources" / "experience-source-ledger.md"
    rows = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8 or cells[0].lower() in {"title", "---"}:
            continue
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows += 1
    if rows != 28:
        errors.append(f"experience source ledger must contain exactly 28 records after Phase 11B, found {rows}")
    return rows


def validate_governance(inventory: dict[str, object], errors: list[str]) -> None:
    governance = inventory.get("governance")
    if not isinstance(governance, dict):
        errors.append("Phase 11B inventory governance section is missing")
        return
    if governance.get("atlas_live_dependency") is not False:
        errors.append("Phase 11B must not activate a live Atlas dependency")
    if governance.get("atlas_status_inheritance") is not False:
        errors.append("Phase 11B must forbid Atlas status inheritance")
    if governance.get("release_gate") != "Phase 12":
        errors.append("Phase 11B release gate must remain Phase 12")

    fixture = ROOT / "integration" / "principia-atlas" / "manifests" / "feedback-instability.fixture.json"
    if not fixture.is_file():
        errors.append("Principia–Atlas compatibility fixture is missing")
    else:
        try:
            data = json.loads(fixture.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"compatibility fixture is invalid JSON: {exc}")
        else:
            if data.get("live") is not False or data.get("mode") != "compatibility-fixture":
                errors.append("Phase 11B must preserve the non-live Atlas compatibility fixture")


def validate_artifacts_and_ci(errors: list[str]) -> None:
    for path in (INVENTORY_PATH, REPORT_PATH, WORKFLOW_PATH, Path(__file__)):
        if not Path(path).is_file():
            errors.append(f"missing Phase 11B artifact: {Path(path).relative_to(ROOT)}")
    if WORKFLOW_PATH.is_file():
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        if "contents: read" not in workflow:
            errors.append("Phase 11B workflow must declare contents: read")
        for forbidden in ("contents: write", "git push", "git commit", "pull_request_target", "Rhodan-lab/Atlas"):
            if forbidden in workflow:
                errors.append(f"Phase 11B workflow contains forbidden write or live-integration text: {forbidden}")


def main() -> int:
    errors: list[str] = []
    inventory = parse_inventory(errors)
    artifacts = collect_artifacts(inventory, errors)
    if artifacts:
        configure_base_validator(artifacts)
        base_result = base.run(strict=True)
        if base_result != 0:
            errors.append("expanded experience layer failed the inherited strict experience validator")
        validate_artifact_metadata(artifacts, errors)
        validate_route_boundaries(artifacts, errors)
        validate_navigation(artifacts, errors)
    ledger_rows = count_ledger_rows(errors)
    validate_governance(inventory, errors)
    validate_artifacts_and_ci(errors)

    if errors:
        print("Phase 11B expansion errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "Phase 11B expansion passed: "
        f"4 complete routes, 16 reviewed artifacts, {ledger_rows} experience-source records, "
        "draft release state, and non-live Atlas compatibility."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
