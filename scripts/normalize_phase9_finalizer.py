#!/usr/bin/env python3
"""Normalize the Phase 9 finalizer for literal-safe markers and boundaries."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts" / "finalize_phase9_review.py"
WRITE_LINE = '    path.write_text(text.rstrip() + "\\n", encoding="utf-8")'
BOUNDARY_WRITE = (
    '    text = phase9.insert_boundaries(text, module)\n'
    '    path.write_text(text.rstrip() + "\\n", encoding="utf-8")'
)
THETA_PATTERN = re.compile(r'(?<!r)"\\theta_k"')
RAW_THETA = 'r"\\theta_k"'
UPPER_PHOTO = '"Photovoltaic cells are energy-conversion devices"'
LOWER_PHOTO = '"photovoltaic cells are energy-conversion devices"'


def normalized(text: str) -> str:
    fixed = text
    if BOUNDARY_WRITE not in fixed:
        fixed = fixed.replace(WRITE_LINE, BOUNDARY_WRITE, 1)
    fixed = THETA_PATTERN.sub(lambda _match: RAW_THETA, fixed)
    fixed = fixed.replace(UPPER_PHOTO, LOWER_PHOTO)
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
    if BOUNDARY_WRITE not in fixed:
        errors.append("boundary reinsertion is missing")
    if THETA_PATTERN.search(fixed) or RAW_THETA not in fixed:
        errors.append("theta marker is not in the required raw form")
    if UPPER_PHOTO in fixed or LOWER_PHOTO not in fixed:
        errors.append("photovoltaic marker does not match reviewed text")
    try:
        compile(fixed, str(TARGET), "exec")
    except SyntaxError as exc:
        errors.append(f"normalized finalizer does not compile: {exc}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.write and fixed != text:
        TARGET.write_text(fixed, encoding="utf-8")
    elif args.check and fixed != text:
        print("ERROR: Phase 9 finalizer source is not normalized", file=sys.stderr)
        return 1

    print("Phase 9 finalizer normalization passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
