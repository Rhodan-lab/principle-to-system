#!/usr/bin/env python3
"""Normalize known literal mismatches in the Phase 10 reconciler source."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts" / "apply_phase10_synthesis.py"
OLD = '        ("A single hardware design that can execute any algorithm expressed in its instruction set",'
NEW = '        ("a single hardware design that can execute any algorithm expressed in its instruction set",'


def normalized(text: str) -> str:
    return text.replace(OLD, NEW)


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    text = TARGET.read_text(encoding="utf-8")
    fixed = normalized(text)
    if OLD in fixed or NEW not in fixed:
        print("ERROR: Phase 10 reconciler literal normalization failed", file=sys.stderr)
        return 1
    try:
        compile(fixed, str(TARGET), "exec")
    except SyntaxError as exc:
        print(f"ERROR: normalized reconciler does not compile: {exc}", file=sys.stderr)
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
