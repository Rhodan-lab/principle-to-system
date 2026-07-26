#!/usr/bin/env python3
"""Validate the Principia–Atlas bridge-candidate audit and read-only governance."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "validate-principia-atlas-compatibility.yml"
MANIFEST = ROOT / "integration" / "principia-atlas" / "manifests" / "feedback-instability.fixture.json"
EXPORT = ROOT / "integration" / "principia-atlas" / "exports" / "feedback-instability.external-dependent.fixture.json"
REPORT = ROOT / "reports" / "principia-atlas-bridge-candidate-r2.md"
EXPECTED_REVISIONS = {
    "claim:en:model-oscillation-does-not-prove-real-system": 1,
    "model:en:delayed-correction-recurrence": 2,
    "concept:en:feedback": 1,
    "concept:en:oscillation": 1,
}


def main() -> int:
    errors: list[str] = []
    required = (
        ROOT / "contracts" / "principia-atlas" / "0.1" / "README.md",
        ROOT / "contracts" / "principia-atlas" / "0.1" / "bridge-manifest.schema.json",
        ROOT / "integration" / "principia-atlas" / "README.md",
        MANIFEST,
        EXPORT,
        ROOT / "release" / "phase-12-revision-impact.json",
        ROOT / "release" / "phase-12-pilot-readiness.json",
        REPORT,
        ROOT / "scripts" / "export_principia_atlas_dependents.py",
        ROOT / "scripts" / "validate_principia_atlas_bridge.py",
        Path(__file__),
        ROOT / "software" / "tests" / "test_bridge_candidate.py",
        WORKFLOW,
    )
    for path in required:
        if not path.is_file():
            errors.append(f"missing required bridge-candidate artifact: {path.relative_to(ROOT)}")

    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot validate bridge manifest: {exc}")
        manifest = {}
    if manifest.get("live") is not False or manifest.get("mode") != "bridge-candidate":
        errors.append("bridge manifest must remain non-live bridge-candidate")
    atlas = manifest.get("atlas")
    dependencies = atlas.get("dependencies") if isinstance(atlas, dict) else None
    actual_revisions = {
        item.get("id"): item.get("revision")
        for item in dependencies or []
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    if actual_revisions != EXPECTED_REVISIONS:
        errors.append(f"bridge dependency revisions differ: {actual_revisions}")
    policy = manifest.get("status_policy")
    if not isinstance(policy, dict):
        errors.append("bridge status policy is missing")
    else:
        for key in ("knowledge_status_inheritance", "pedagogical_status_inheritance", "release_status_inheritance"):
            if policy.get(key) != "prohibited":
                errors.append(f"bridge status policy must prohibit {key}")

    try:
        export = json.loads(EXPORT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot validate bridge export: {exc}")
        export = {}
    if export.get("contract") != "principia-atlas-external-dependent/0.2":
        errors.append("bridge export must use candidate contract 0.2")
    if export.get("bridge_mode") != "bridge-candidate" or export.get("live") is not False:
        errors.append("bridge export must remain non-live bridge-candidate")
    forbidden_status = {"status", "pedagogical_status", "release_status", "knowledge_status"} & set(export)
    if forbidden_status:
        errors.append(f"bridge export leaks status authority: {sorted(forbidden_status)}")

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
            "repository: Rhodan-lab/Atlas",
        ):
            if forbidden in workflow:
                errors.append(f"compatibility workflow contains forbidden operation: {forbidden}")
        for required_command in (
            "export_principia_atlas_dependents.py --check",
            "validate_principia_atlas_bridge.py",
            "validate_principia_atlas_audit.py",
            "validate_experiences.py --strict",
            "validate_repo.py --strict",
            "validate_phase12_release_candidate.py",
            "unittest discover -s software/tests",
            "validate_phase13_software.py",
        ):
            if required_command not in workflow:
                errors.append(f"compatibility workflow missing command: {required_command}")

    state = (ROOT / "PROJECT_STATE.md").read_text(encoding="utf-8")
    for marker in (
        "Phase 14 — Principia–Atlas bridge candidate merged and validated through PR #16",
        "| 14 | Principia–Atlas bridge candidate | Merged and validated through PR #16 |",
        "PR #16 was merged into `main` at commit `eb3a00dfbfdfaa5470cb40505fa213e5349a917f`",
        "model:en:delayed-correction-recurrence@2",
        "mode: bridge-candidate",
        "live: false",
        "Atlas remains unchanged",
        "status remains separate",
        "Atlas Phase 2 may now consume",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing bridge-candidate marker: {marker}")
    if "Active; exact-revision validation pending" in state:
        errors.append("PROJECT_STATE.md still reports bridge validation as pending")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for marker in (
        "Principia & Atlas compatibility",
        "bridge-candidate",
        "delayed-correction-recurrence@2",
        "depends_on_exact",
    ):
        if marker not in readme:
            errors.append(f"README.md missing bridge-candidate marker: {marker}")

    if REPORT.is_file():
        report = REPORT.read_text(encoding="utf-8")
        for marker in (
            "Atlas was not modified",
            "oscillation does not prove instability",
            "model:en:delayed-correction-recurrence@2",
            "candidate-ready",
            "live: false",
        ):
            if marker not in report:
                errors.append(f"bridge-candidate report missing marker: {marker}")

    if errors:
        print("Principia–Atlas bridge-candidate audit failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Principia–Atlas audit passed: merged exact-revision candidate, separate status authority, Atlas unchanged, and read-only CI.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
