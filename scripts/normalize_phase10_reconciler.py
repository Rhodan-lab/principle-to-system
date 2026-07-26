#!/usr/bin/env python3
"""Normalize known literal, continuity, and validator requirements for Phase 10."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECONCILER = ROOT / "scripts" / "apply_phase10_synthesis.py"
VALIDATOR = ROOT / "scripts" / "validate_phase10_synthesis.py"

OLD_LITERAL = '        ("A single hardware design that can execute any algorithm expressed in its instruction set",'
NEW_LITERAL = '        ("a single hardware design that can execute any algorithm expressed in its instruction set",'

LEGACY_STATUS = '''## Repository status on the Phase 10 branch

- Modules 01–20: **Reviewed**;
- 6 pathways: **Reviewed**;
- 7 crosscutting concepts: **Reviewed**;
- 3 knowledge maps: **Reviewed**;
- source ledger: **143 records**;
- no core or synthesis artifact is Complete.
'''
CURRENT_STATUS = '''## Repository status on the Phase 10 branch

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
FULL_STATUS = '''## Repository status on the Phase 10 branch

### Foundations Modules 01–05

- Modules 01–05: **Reviewed**;

### Physical Science Modules 06–12

- Modules 06–12: **Reviewed**;

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

## Historical continuity record

- Phase 9 Technology review implemented and validated on draft PR #10 before that pull request was merged.
- Historical pre-merge marker: `Technology review | Implemented and validated on PR #10; awaiting merge`.
- The Phase 9 central-ledger transition was 131 → 143 records.
- Phase 10 Synthesis reconciliation is the current branch-stage audit label.
- Permanent CI is read-only.
- no core module is Complete; synthesis artifacts also remain Reviewed pending Phase 12.
'''

OLD_LEDGER_HEADER = 'cells[0].lower() in {"module", "---"}'
NEW_LEDGER_HEADER = 'cells[0].lower() in {"module", "title", "---"}'


def normalized_reconciler(text: str) -> str:
    fixed = text.replace(OLD_LITERAL, NEW_LITERAL)
    if FULL_STATUS not in fixed:
        fixed = fixed.replace(CURRENT_STATUS, FULL_STATUS)
    if FULL_STATUS not in fixed:
        fixed = fixed.replace(LEGACY_STATUS, FULL_STATUS)
    return fixed


def normalized_validator(text: str) -> str:
    return text.replace(OLD_LEDGER_HEADER, NEW_LEDGER_HEADER)


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    source_text = RECONCILER.read_text(encoding="utf-8")
    source_fixed = normalized_reconciler(source_text)
    validator_text = VALIDATOR.read_text(encoding="utf-8")
    validator_fixed = normalized_validator(validator_text)

    errors: list[str] = []
    if OLD_LITERAL in source_fixed or NEW_LITERAL not in source_fixed:
        errors.append("Phase 10 pathway literal is not normalized")
    if FULL_STATUS not in source_fixed:
        errors.append("historical Phase 6–9 continuity markers are not preserved in generated project state")
    for marker in (
        "Modules 01–05: **Reviewed**",
        "Modules 06–12: **Reviewed**",
        "Phase 8 — Life and Earth Systems Modules 13–16",
        "Modules 13–16: **Reviewed**",
        "Phase 9 Technology review implemented and validated on draft PR #10",
        "Technology review | Implemented and validated on PR #10; awaiting merge",
        "Modules 17–20: **Reviewed**",
        "Modules 01–20: **Reviewed**",
        "131 → 143 records",
        "**143 records**",
        "Phase 10 Synthesis reconciliation",
        "Permanent CI is read-only",
        "no core module is Complete",
    ):
        if marker not in source_fixed:
            errors.append(f"generated project state marker missing: {marker}")
    if OLD_LEDGER_HEADER in validator_fixed or NEW_LEDGER_HEADER not in validator_fixed:
        errors.append("Phase 10 validator does not exclude the source-ledger Title header")

    for path, text in ((RECONCILER, source_fixed), (VALIDATOR, validator_fixed)):
        try:
            compile(text, str(path), "exec")
        except SyntaxError as exc:
            errors.append(f"normalized source does not compile for {path.name}: {exc}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    changed = False
    if source_fixed != source_text:
        changed = True
        if args.write:
            RECONCILER.write_text(source_fixed, encoding="utf-8")
    if validator_fixed != validator_text:
        changed = True
        if args.write:
            VALIDATOR.write_text(validator_fixed, encoding="utf-8")
    if args.check and changed:
        print("ERROR: Phase 10 sources are not normalized", file=sys.stderr)
        return 1

    print("Phase 10 source normalization passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
