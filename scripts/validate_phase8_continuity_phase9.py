#!/usr/bin/env python3
"""Run the complete Phase 8 content gate with Phase 9 downstream statuses."""
from __future__ import annotations

import json
import sys

import validate_phase8_life_earth_review as phase8

ROOT = phase8.ROOT


def check_index(result: phase8.Result) -> None:
    statuses: dict[str, str] = {}
    for line in (ROOT / "INDEX.md").read_text(encoding="utf-8").splitlines():
        match = phase8.INDEX_RE.match(line)
        if match:
            number, status = match.groups()
            statuses[number] = status.lower()
    for number in [f"{value:02d}" for value in range(1, 21)]:
        if statuses.get(number) != "reviewed":
            result.errors.append(f"INDEX.md: Module {number} must be Reviewed in Phase 9")


def check_artifacts(result: phase8.Result) -> None:
    required = (
        ROOT / "sources" / "phase-8-reviewed-sources.json",
        ROOT / "scripts" / "apply_phase8_review_sources.py",
        ROOT / "scripts" / "apply_phase8_life_earth_review.py",
        ROOT / "scripts" / "finalize_phase8_review.py",
        ROOT / "scripts" / "validate_phase8_life_earth_review.py",
        ROOT / "reports" / "phase-8-life-earth-review.md",
        ROOT / "reports" / "phase-8-life-earth-sources.json",
    )
    for path in required:
        if not path.exists():
            result.errors.append(f"{path.relative_to(ROOT)}: missing")

    source_report = ROOT / "reports" / "phase-8-life-earth-sources.json"
    if source_report.exists():
        try:
            report = json.loads(source_report.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            result.errors.append(f"phase-8 source report invalid JSON: {exc}")
        else:
            if report.get("errors"):
                result.errors.append(f"phase-8 source report contains errors: {report['errors']}")
            if report.get("ledger_records_before") != 121 or report.get("ledger_records_after") != 131:
                result.errors.append("phase-8 source report must preserve the 121-to-131 transition")

    state_path = ROOT / "PROJECT_STATE.md"
    state = state_path.read_text(encoding="utf-8") if state_path.exists() else ""
    for marker in (
        "Phase 8 — Life and Earth Systems Modules 13–16",
        "Modules 13–16: **Reviewed**",
        "Modules 17–20: **Reviewed**",
        "**143 records**",
    ):
        if marker not in state:
            result.errors.append(f"PROJECT_STATE.md: missing Phase 9 continuity marker: {marker}")


def main() -> int:
    result = phase8.Result([], [])
    locators = phase8.ledger_urls(result)
    phase8.check_files(result, locators)
    check_index(result)
    check_artifacts(result)

    if result.warnings:
        print("Phase 8 continuity warnings:")
        for warning in result.warnings:
            print(f"- {warning}")
    if result.errors:
        print("Phase 8 continuity errors:", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Phase 8 continuity passed through Phase 9: 4 modules, 12 reviewed files, {len(locators)} source locators.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
