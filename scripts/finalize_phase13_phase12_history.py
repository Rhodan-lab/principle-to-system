#!/usr/bin/env python3
"""Retain exact Phase 12 audit strings after the Phase 13 authority transition."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "PROJECT_STATE.md"
AUDIT = ROOT / "AUDIT.md"

STATE_MARKER = "- Historical validation marker: release decision remains **Hold**."
STATE_ANCHOR = (
    "The following strings describe the former Phase 12 gate and are retained only as "
    "historical audit inputs. They are superseded by `release/phase-13-machine-governance.json`."
)
AUDIT_HEADING = "### Retained Phase 12 audit marker"
AUDIT_QUOTE = (
    "> A reviewed 20-module Principia foundation with reconciled synthesis, four complete "
    "applied-learning routes, exact-revision compatibility preparation, and a machine-validated "
    "but unreleased Phase 12 material release candidate awaiting independent human authority."
)
AUDIT_ANCHOR = "## Phase 13 software-foundation disposition"


def finalize_state(text: str, errors: list[str]) -> str:
    if STATE_MARKER in text:
        return text
    if STATE_ANCHOR not in text:
        errors.append("PROJECT_STATE.md: Phase 13 historical-marker anchor is missing")
        return text
    return text.replace(STATE_ANCHOR, STATE_ANCHOR + "\n\n" + STATE_MARKER, 1)


def finalize_audit(text: str, errors: list[str]) -> str:
    if AUDIT_QUOTE in text:
        return text
    if AUDIT_ANCHOR not in text:
        errors.append("AUDIT.md: Phase 13 disposition anchor is missing")
        return text
    block = AUDIT_HEADING + "\n\n" + AUDIT_QUOTE + "\n\n"
    return text.replace(AUDIT_ANCHOR, block + AUDIT_ANCHOR, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    changes: list[tuple[Path, str]] = []
    for path, transform in ((STATE, finalize_state), (AUDIT, finalize_audit)):
        try:
            original = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        fixed = transform(original, errors)
        if fixed != original:
            changes.append((path, fixed))

    pending = {path: content for path, content in changes}
    state_text = pending.get(STATE, STATE.read_text(encoding="utf-8"))
    audit_text = pending.get(AUDIT, AUDIT.read_text(encoding="utf-8"))
    if STATE_MARKER not in state_text:
        errors.append("PROJECT_STATE.md: exact Phase 12 release-decision marker is missing")
    if AUDIT_QUOTE not in audit_text:
        errors.append("AUDIT.md: exact Phase 12 disposition marker is missing")

    if errors:
        print("Phase 13 historical-compatibility errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if args.check and changes:
        print("Phase 13 historical compatibility is not finalized:", file=sys.stderr)
        for path, _ in changes:
            print(f"- {path.relative_to(ROOT)}", file=sys.stderr)
        return 1
    if args.write:
        for path, content in changes:
            path.write_text(content, encoding="utf-8")
    if changes:
        print("Phase 13 historical compatibility finalized:")
        for path, _ in changes:
            print(f"- {path.relative_to(ROOT)}")
    else:
        print("Phase 13 historical compatibility already finalized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
