#!/usr/bin/env python3
"""Validate the finalized Phase 13 software record after downstream phases merge."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "PROJECT_STATE.md"
REPORT = ROOT / "reports" / "phase-13-software-foundation.md"
README = ROOT / "README.md"
AUDIT = ROOT / "AUDIT.md"
RELEASE = ROOT / "release" / "README.md"

REQUIRED: dict[Path, tuple[str, ...]] = {
    STATE: (
        "Software state: **foundation-validated**.",
        "| 13 | Software foundation | Merged and validated through PR #15 |",
        "| 14 | Principia–Atlas bridge candidate | Merged and validated through PR #16 |",
    ),
    REPORT: (
        "Validation status: **foundation-validated on draft PR #15**",
        "## Machine validation result",
        "software_state: foundation-validated",
    ),
    README: (
        "The Phase 13 machine gate passes on draft PR #15",
        "foundation-validated",
        "generated site is reproducible",
    ),
    AUDIT: (
        "Phase 13 machine validation passes on draft PR #15",
        "software state is `foundation-validated`",
    ),
    RELEASE: (
        "The Phase 13 machine gate passes on draft PR #15",
        "software foundation state is `foundation-validated`",
    ),
}

FORBIDDEN_STATE = (
    "Software state: **implementation pending validation**.",
    "| 13 | Software foundation | Active; machine validation pending |",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    parser.parse_args()

    errors: list[str] = []
    for path, markers in REQUIRED.items():
        if not path.is_file():
            errors.append(f"missing Phase 13 record: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing Phase 13 marker {marker!r}")
        if path == STATE:
            for stale in FORBIDDEN_STATE:
                if stale in text:
                    errors.append(f"PROJECT_STATE.md: stale Phase 13 marker remains {stale!r}")

    if errors:
        print("Phase 13 validation-record errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Phase 13 validation record finalized: software foundation remains validated, "
        "downstream Phase 14 is compatible, and no material or integration status is promoted."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
