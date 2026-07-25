#!/usr/bin/env python3
"""Normalize multiline replacement literals in the Phase 9 transformer."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts" / "apply_phase9_technology_review.py"
PATTERN = re.compile(r'(:\s*)"""')


def normalized(text: str) -> str:
    return PATTERN.sub(r'\1r"""', text)


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    text = TARGET.read_text(encoding="utf-8")
    fixed = normalized(text)
    remaining = len(PATTERN.findall(fixed))
    if remaining:
        print(f"ERROR: {remaining} non-raw multiline mapping literals remain", file=sys.stderr)
        return 1

    if args.write and fixed != text:
        TARGET.write_text(fixed, encoding="utf-8")
    elif args.check and fixed != text:
        print("ERROR: Phase 9 transformer literals are not normalized", file=sys.stderr)
        return 1

    try:
        compile(fixed, str(TARGET), "exec")
    except SyntaxError as exc:
        print(f"ERROR: normalized Phase 9 transformer does not compile: {exc}", file=sys.stderr)
        return 1

    print("Phase 9 transformer literal normalization passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
