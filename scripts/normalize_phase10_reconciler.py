#!/usr/bin/env python3
"""Normalize known literal and continuity requirements in the Phase 10 reconciler."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts" / "apply_phase10_synthesis.py"

OLD_LITERAL = '        ("A single hardware design that can execute any algorithm expressed in its instruction set",'
NEW_LITERAL = '        ("a single hardware design that can execute any algorithm expressed in its instruction set",'

OLD_STATUS = '''## Repository status on the Phase 10 branch

- Modules 01–20: **Reviewed**;
- 6 pathways: **Reviewed**;
- 7 crosscutting concepts: **Reviewed**;
- 3 knowledge maps: **Reviewed**;
- source ledger: **143 records**;
- no core or synthesis artifact is Complete.
'''
NEW_STATUS = '''## Repository status on the Phase 10 branch

### Phase 8 — Life and Earth Systems Modules 13–16

- Modules 13–16: **Reviewed**;

### Phase 9 Technology review implemented and merged through PR #10

- Modules 17–20: **Reviewed**;
- Modules 01–20: **Reviewed**;

### Reconciled synthesis layer

- 6 pathways: **Reviewed**;
- 7 crosscutting concepts: **Reviewed**;
- 3 knowledge maps: **Reviewed**;
- source ledger: **143 records**;
- no core or synthesis artifact is Complete.
'''


def normalized(text: str) -> str:
    fixed = text.replace(OLD_LITERAL, NEW_LITERAL)
    if NEW_STATUS not in fixed:
        fixed = fixed.replace(OLD_STATUS, NEW_STATUS)
    return fixed


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    text = TARGET.read_text(encoding="utf-8")
    fixed = normalized(text)
    errors: list[str] = []
    if OLD_LITERAL in fixed or NEW_LITERAL not in fixed:
        errors.append("Phase 10 pathway literal is not normalized")
    if NEW_STATUS not in fixed:
        errors.append("Phase 8–9 continuity markers are not preserved in generated project state")
    for marker in (
        "Phase 8 — Life and Earth Systems Modules 13–16",
        "Modules 13–16: **Reviewed**",
        "Phase 9 Technology review implemented",
        "Modules 17–20: **Reviewed**",
        "Modules 01–20: **Reviewed**",
        "**143 records**",
    ):
        if marker not in fixed:
            errors.append(f"generated project state marker missing: {marker}")
    try:
        compile(fixed, str(TARGET), "exec")
    except SyntaxError as exc:
        errors.append(f"normalized reconciler does not compile: {exc}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.write and fixed != text:
        TARGET.write_text(fixed, encoding="utf-8")
    elif args.check and fixed != text:
        print("ERROR: Phase 10 reconciler source is not normalized", file=sys.stderr)
        return 1
    print("Phase 10 reconciler normalization passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
