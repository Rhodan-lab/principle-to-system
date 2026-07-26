#!/usr/bin/env python3
"""Validate the finalized post-merge records for the non-live bridge candidate."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "PROJECT_STATE.md"
README = ROOT / "README.md"
AUDIT = ROOT / "AUDIT.md"
RELEASE = ROOT / "release" / "README.md"

REQUIRED: dict[Path, tuple[str, ...]] = {
    STATE: (
        "Phase 14 — Principia–Atlas bridge candidate merged and validated through PR #16",
        "| 14 | Principia–Atlas bridge candidate | Merged and validated through PR #16 |",
        "PR #16 was merged into `main` at commit `eb3a00dfbfdfaa5470cb40505fa213e5349a917f`",
        "model:en:delayed-correction-recurrence@2",
        "mode: bridge-candidate",
        "live: false",
        "candidate-ready",
        "Atlas remains unchanged",
        "status remains separate",
        "Atlas Phase 2 may consume",
        "release decision remains **Hold**",
    ),
    README: (
        "Principia & Atlas compatibility",
        "bridge-candidate",
        "delayed-correction-recurrence@2",
        "principia-atlas-external-dependent/0.2",
        "depends_on_exact",
        "No live cross-repository call is enabled",
    ),
    AUDIT: (
        "Principia–Atlas bridge-candidate disposition",
        "model:en:delayed-correction-recurrence",
        "bounded exact period-6 orbit",
        "artifact_revision: 1",
        "status: reviewed",
        "release_status: draft",
        "Atlas was not modified",
    ),
    RELEASE: (
        "Principia–Atlas bridge candidate",
        "mode: bridge-candidate",
        "live: false",
        "candidate-ready",
        "principia-atlas-external-dependent/0.2",
        "Atlas remains unchanged",
    ),
}

FORBIDDEN: dict[Path, tuple[str, ...]] = {
    STATE: (
        "Active; exact-revision validation pending",
        "After the bridge-candidate gate passes and its pull request is merged",
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    parser.parse_args()

    errors: list[str] = []
    for path, markers in REQUIRED.items():
        if not path.is_file():
            errors.append(f"missing finalized record: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing finalized marker {marker!r}")
        for forbidden in FORBIDDEN.get(path, ()):
            if forbidden in text:
                errors.append(f"{path.relative_to(ROOT)}: stale pre-merge marker remains {forbidden!r}")

    if errors:
        print("Bridge candidate record finalization failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Bridge candidate records finalized: PR #16 merged, exact model revision 2 retained, "
        "status authority separated, Atlas Phase 2 importer-ready, and live integration disabled."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
