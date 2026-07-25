#!/usr/bin/env python3
"""Normalize multiline literals and literal-safe substitutions in Phase 9."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts" / "apply_phase9_technology_review.py"
MULTILINE_PATTERN = re.compile(r'(:\s*)"""')
UNSAFE_SUBSTITUTION = 'return pattern.sub(replacement.rstrip() + "\\n\\n", text, count=1)'
SAFE_SUBSTITUTION = 'return pattern.sub(lambda _match: replacement.rstrip() + "\\n\\n", text, count=1)'


def normalized(text: str) -> str:
    fixed = MULTILINE_PATTERN.sub(r'\1r"""', text)
    fixed = fixed.replace(UNSAFE_SUBSTITUTION, SAFE_SUBSTITUTION)
    return fixed


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    text = TARGET.read_text(encoding="utf-8")
    fixed = normalized(text)
    remaining = len(MULTILINE_PATTERN.findall(fixed))
    if remaining:
        print(f"ERROR: {remaining} non-raw multiline mapping literals remain", file=sys.stderr)
        return 1
    if UNSAFE_SUBSTITUTION in fixed:
        print("ERROR: regex replacement still interprets Markdown backslashes", file=sys.stderr)
        return 1
    if SAFE_SUBSTITUTION not in fixed:
        print("ERROR: literal-safe section replacement is missing", file=sys.stderr)
        return 1

    if args.write and fixed != text:
        TARGET.write_text(fixed, encoding="utf-8")
    elif args.check and fixed != text:
        print("ERROR: Phase 9 transformer source is not normalized", file=sys.stderr)
        return 1

    try:
        compile(fixed, str(TARGET), "exec")
    except SyntaxError as exc:
        print(f"ERROR: normalized Phase 9 transformer does not compile: {exc}", file=sys.stderr)
        return 1

    print("Phase 9 transformer source normalization passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
