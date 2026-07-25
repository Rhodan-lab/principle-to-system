#!/usr/bin/env python3
"""Run the complete Phase 6 gate while accepting reviewed Modules 01–20."""
from __future__ import annotations

import re

import validate_foundations_review as phase6

INDEX_RE = re.compile(r"^\|\s*(\d{2})\s*\|.*\|\s*(Draft|Reviewed|Complete|Blocked)\s*\|\s*$", re.I)


def check_index(result, _allow_downstream_reviewed=False):
    path = phase6.ROOT / "INDEX.md"
    if not path.exists():
        result.errors.append("INDEX.md: missing")
        return
    statuses: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.match(line)
        if match:
            number, status = match.groups()
            statuses[number] = status.lower()
    for number in [f"{value:02d}" for value in range(1, 21)]:
        if statuses.get(number) != "reviewed":
            result.errors.append(f"INDEX.md: Module {number} must be Reviewed in Phase 9 continuity mode")
    if any(status == "complete" for status in statuses.values()):
        result.errors.append("INDEX.md: no module may be Complete before repository-wide release validation")


phase6.check_index = check_index

if __name__ == "__main__":
    raise SystemExit(phase6.main())
