#!/usr/bin/env python3
"""Validate Phase 9 audit records, immutable artifacts, and read-only CI."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_REPORT = ROOT / "reports" / "phase-9-technology-sources.json"
STATE = ROOT / "PROJECT_STATE.md"
INDEX = ROOT / "INDEX.md"
READ_ONLY_WORKFLOW = ROOT / ".github" / "workflows" / "validate-phase-9-technology.yml"
TEMP_WORKFLOW = ROOT / ".github" / "workflows" / "apply-phase-9-technology-review.yml"
REQUIRED_ARTIFACTS = (
    ROOT / "reports" / "phase-9-technology-review.md",
    SOURCE_REPORT,
    ROOT / "sources" / "phase-9-reviewed-sources.json",
    ROOT / "scripts" / "apply_phase9_review_sources.py",
    ROOT / "scripts" / "apply_phase9_technology_review.py",
    ROOT / "scripts" / "finalize_phase9_review.py",
    ROOT / "scripts" / "normalize_phase9_transformer_literals.py",
    ROOT / "scripts" / "normalize_phase9_finalizer.py",
    ROOT / "scripts" / "validate_foundations_continuity_phase9.py",
    ROOT / "scripts" / "validate_phase8_continuity_phase9.py",
    ROOT / "scripts" / "validate_phase9_technology_review.py",
    ROOT / "scripts" / "validate_phase9_audit.py",
    READ_ONLY_WORKFLOW,
)
INDEX_RE = re.compile(r"^\|\s*(\d{2})\s*\|.*\|\s*(Draft|Reviewed|Complete|Blocked)\s*\|\s*$", re.I)


def validate_source_report(errors: list[str]) -> None:
    if not SOURCE_REPORT.is_file():
        errors.append("reports/phase-9-technology-sources.json: missing")
        return
    try:
        report = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Phase 9 source report is invalid JSON: {exc}")
        return
    expected = {
        "registry_records": 12,
        "ledger_records_before": 131,
        "ledger_records_after": 143,
        "already_present": [],
        "errors": [],
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"Phase 9 source report {key}={report.get(key)!r}; expected {value!r}")
    additions = report.get("records_added")
    if not isinstance(additions, list) or len(additions) != 12:
        errors.append("Phase 9 source report must preserve exactly twelve initial additions")
    elif len(set(additions)) != 12:
        errors.append("Phase 9 source report contains duplicate additions")


def validate_state(errors: list[str]) -> None:
    if not STATE.is_file():
        errors.append("PROJECT_STATE.md: missing")
        return
    text = STATE.read_text(encoding="utf-8")
    required = (
        "Phase 9 Technology review implemented and validated on draft PR #10",
        "Technology review | Implemented and validated on PR #10; awaiting merge",
        "Modules 01–20: **Reviewed**",
        "no core module is Complete",
        "131 → 143 records",
        "**143 records**",
        "Phase 10 Synthesis reconciliation",
        "Permanent CI is read-only",
    )
    for marker in required:
        if marker not in text:
            errors.append(f"PROJECT_STATE.md: missing marker: {marker}")


def validate_index(errors: list[str]) -> None:
    statuses: dict[str, str] = {}
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.match(line)
        if match:
            number, status = match.groups()
            statuses[number] = status.lower()
    for number in [f"{value:02d}" for value in range(1, 21)]:
        if statuses.get(number) != "reviewed":
            errors.append(f"INDEX.md: Module {number} must be Reviewed")
    if any(status == "complete" for status in statuses.values()):
        errors.append("INDEX.md: no core module may be Complete before release validation")


def validate_artifacts(errors: list[str]) -> None:
    for path in REQUIRED_ARTIFACTS:
        if not path.is_file():
            errors.append(f"{path.relative_to(ROOT)}: missing")
    if TEMP_WORKFLOW.exists():
        errors.append("temporary write-capable Phase 9 workflow still exists")


def validate_workflow(errors: list[str]) -> None:
    if not READ_ONLY_WORKFLOW.is_file():
        return
    text = READ_ONLY_WORKFLOW.read_text(encoding="utf-8")
    if "contents: read" not in text:
        errors.append("Phase 9 workflow must declare contents: read")
    for prohibited in ("contents: write", "git push", "git commit", "create-pull-request", "pull_request_target"):
        if prohibited in text:
            errors.append(f"Phase 9 read-only workflow contains prohibited text: {prohibited}")
    for required in (
        "validate_foundations_continuity_phase9.py",
        "finalize_phase7_review.py --check",
        "validate_phase8_continuity_phase9.py",
        "apply_phase9_review_sources.py --check",
        "normalize_phase9_transformer_literals.py --check",
        "normalize_phase9_finalizer.py --check",
        "finalize_phase9_review.py --check",
        "validate_phase9_technology_review.py",
        "validate_phase9_audit.py",
        "validate_repo.py",
    ):
        if required not in text:
            errors.append(f"Phase 9 workflow missing required gate: {required}")


def main() -> int:
    errors: list[str] = []
    validate_source_report(errors)
    validate_state(errors)
    validate_index(errors)
    validate_artifacts(errors)
    validate_workflow(errors)

    if errors:
        print("Phase 9 audit errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Phase 9 audit validation passed: records, status, artifacts, and read-only CI are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
