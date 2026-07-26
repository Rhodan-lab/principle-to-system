#!/usr/bin/env python3
"""Validate Phase 11A audit records and read-only compatibility governance."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "validate-principia-atlas-compatibility.yml"
MANIFEST = ROOT / "integration" / "principia-atlas" / "manifests" / "feedback-instability.fixture.json"


def main() -> int:
    errors: list[str] = []

    required = (
        ROOT / "contracts" / "principia-atlas" / "0.1" / "README.md",
        ROOT / "contracts" / "principia-atlas" / "0.1" / "bridge-manifest.schema.json",
        ROOT / "integration" / "principia-atlas" / "README.md",
        MANIFEST,
        ROOT / "integration" / "principia-atlas" / "exports" / "feedback-instability.external-dependent.fixture.json",
        ROOT / "reports" / "phase-11a-principia-atlas-compatibility.md",
        ROOT / "scripts" / "export_principia_atlas_dependents.py",
        ROOT / "scripts" / "validate_principia_atlas_bridge.py",
        ROOT / "scripts" / "validate_principia_atlas_audit.py",
        WORKFLOW,
    )
    for path in required:
        if not path.is_file():
            errors.append(f"missing required Phase 11A artifact: {path.relative_to(ROOT)}")

    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot validate bridge manifest: {exc}")
        manifest = {}
    if manifest.get("live") is not False or manifest.get("mode") != "compatibility-fixture":
        errors.append("Phase 11A manifest must remain non-live compatibility-fixture")

    if WORKFLOW.is_file():
        workflow = WORKFLOW.read_text(encoding="utf-8")
        if "contents: read" not in workflow:
            errors.append("compatibility workflow must declare contents: read")
        for forbidden in (
            "contents: write",
            "git push",
            "git commit",
            "pull_request_target",
            "Rhodan-lab/Atlas.git",
            "actions/checkout@v4\n        with:\n          repository: Rhodan-lab/Atlas",
        ):
            if forbidden in workflow:
                errors.append(f"compatibility workflow contains forbidden operation: {forbidden}")
        for required_command in (
            "export_principia_atlas_dependents.py --check",
            "validate_principia_atlas_bridge.py",
            "validate_principia_atlas_audit.py",
            "validate_experiences.py --strict",
            "validate_phase10_synthesis.py",
            "validate_repo.py",
        ):
            if required_command not in workflow:
                errors.append(f"compatibility workflow missing command: {required_command}")

    state = (ROOT / "PROJECT_STATE.md").read_text(encoding="utf-8")
    for marker in (
        "Phase 11A — Principia & Atlas Compatibility Foundation",
        "PR #11 was merged",
        "artifact_revision",
        "release_status",
        "No live Atlas dependency",
        "Phase 11B",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 11A marker: {marker}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for marker in (
        "future product identity **Principia**",
        "Principia & Atlas compatibility",
        "contracts/principia-atlas/0.1",
        "artifact_revision",
        "release_status",
    ):
        if marker not in readme:
            errors.append(f"README.md missing compatibility marker: {marker}")

    report = (ROOT / "reports" / "phase-11a-principia-atlas-compatibility.md").read_text(encoding="utf-8")
    for marker in (
        "Atlas remains unchanged",
        "No status crosses the boundary automatically",
        "No live dependency",
        "Phase 11B",
    ):
        if marker not in report:
            errors.append(f"Phase 11A report missing marker: {marker}")

    if errors:
        print("Principia–Atlas audit failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Principia–Atlas audit passed: non-live fixture, separate status authority, and read-only CI.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
