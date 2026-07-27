#!/usr/bin/env python3
"""Apply or verify the Phase 17 project-state transition."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"

CURRENT_16 = "**Phase 16 — Offline Multi-Artifact Integration Pilot merged and validated through PR #20.**"
CURRENT_17 = (
    "**Phase 17 — Offline Event-Protocol Candidate implemented on "
    "`agent/phase-17-offline-event-protocol-candidate`; exact-head validation pending.**"
)
PHASE17_SECTION = """## Phase 17 result — Offline Event-Protocol Candidate

`release/phase-17-offline-event-protocol.json` defines the target state `offline-event-protocol-validated`.

The protocol is anchored to the Phase 16 receipt-chain head and contains:

- one digest-bound lifecycle event for `concept:en:feedback@1` in the deprecated state;
- one acknowledgement that pins the exact event digest and affected-artifact digest;
- one append-only event-log entry;
- one deterministic replay, ordering, equivocation, authority, and recovery matrix.

The event reports `revalidate` for the exact three thermal-control artifacts but executes no action. Atlas knowledge lifecycle, Principia pedagogical status, and Principia release status remain separate. No repository is mutated and `live: false` remains mandatory.

"""


def transform(text: str) -> str:
    if CURRENT_17 not in text:
        if CURRENT_16 not in text:
            raise ValueError("missing Phase 16 current-phase anchor")
        text = text.replace(CURRENT_16, CURRENT_17, 1)

    phase16_state = (
        "Phase 16 state: **offline-multi-artifact-validated** "
        "(`mode: offline-multi-artifact-pilot`, `live: false`)."
    )
    phase17_state = (
        "Phase 17 target state: **offline-event-protocol-validated** "
        "(`mode: offline-event-protocol`, `live: false`)."
    )
    if phase17_state not in text:
        if phase16_state not in text:
            raise ValueError("missing Phase 16 state anchor")
        text = text.replace(phase16_state, phase16_state + "  \n" + phase17_state, 1)

    phase16_row = "| 16 | Offline multi-artifact integration pilot | Merged and validated through PR #20 |"
    phase17_row = "| 17 | Offline event-protocol candidate | Implemented; exact-head validation pending |"
    if phase17_row not in text:
        if phase16_row not in text:
            raise ValueError("missing Phase 16 table anchor")
        text = text.replace(phase16_row, phase16_row + "\n" + phase17_row, 1)

    pr20_line = "- PR #20 was merged into `main` at commit `c493bf879a7945f9991e13592d42424138a0879b`."
    pr21_line = "- PR #21 finalized the Phase 16 record at `44410d47d318c5aaedb7716e4ef3bdefae09b442`."
    if pr21_line not in text:
        if pr20_line not in text:
            raise ValueError("missing PR #20 topology anchor")
        text = text.replace(pr20_line, pr20_line + "\n" + pr21_line, 1)

    old_main = (
        "Main contains the reviewed material foundation, synthesis layer, four applied-learning routes, "
        "static software foundation, non-live exact-revision bridge candidate, pinned Atlas importer "
        "baseline, deterministic Phase 15 receipt, and the integrated Phase 16 atomic three-artifact "
        "batch, receipt chain, lifecycle matrix, and recovery matrix."
    )
    new_main = (
        old_main[:-1]
        + ", plus the Phase 17 digest-bound lifecycle event, acknowledgement, append-only event log, "
        "and recovery matrix candidate."
    )
    if new_main not in text:
        if old_main not in text:
            raise ValueError("missing main-content anchor")
        text = text.replace(old_main, new_main, 1)

    historical16 = (
        "- Historical Phase 16 marker: `Phase 16 — Offline Multi-Artifact Integration Pilot "
        "implemented and validated on draft PR #20`."
    )
    merged16 = "- Phase 16 — Offline Multi-Artifact Integration Pilot merged and validated through PR #20."
    if merged16 not in text:
        if historical16 not in text:
            raise ValueError("missing Phase 16 historical anchor")
        text = text.replace(historical16, historical16 + "\n" + merged16, 1)

    text = text.replace(
        "- Atlas remains unchanged by Principia Phase 16.",
        "- Atlas remains unchanged by Principia Phase 17.",
        1,
    )

    validation_heading = "## Validation\n"
    if PHASE17_SECTION not in text:
        if validation_heading not in text:
            raise ValueError("missing Validation heading")
        text = text.replace(validation_heading, PHASE17_SECTION + validation_heading, 1)

    validation_anchor = "python3 scripts/validate_phase16_postmerge_record.py\n"
    phase17_commands = (
        "python3 scripts/generate_phase17_offline_event_protocol.py --check\n"
        "python3 scripts/validate_phase17_offline_event_protocol.py\n"
        "python3 -m unittest software.tests.test_phase17_offline_event_protocol -v\n"
    )
    if phase17_commands not in text:
        if validation_anchor not in text:
            raise ValueError("missing Phase 16 validation command anchor")
        text = text.replace(validation_anchor, validation_anchor + phase17_commands, 1)

    old_next = (
        "The next bounded gate is **Phase 17 — Offline Event-Protocol Candidate**. It must model "
        "digest-bound lifecycle events, acknowledgements, replay protection, ordering, and recovery "
        "without network synchronization. Live integration remains disabled and requires a distinct "
        "future contract transition."
    )
    new_next = (
        "After Phase 17 integration, the next bounded gate is **offline event-stream scaling**: "
        "multiple ordered events, checkpoint compaction, bounded retention, and long-chain recovery. "
        "Network synchronization and live integration remain disabled and require a distinct future contract."
    )
    if new_next not in text:
        if old_next not in text:
            raise ValueError("missing Phase 17 next-phase anchor")
        text = text.replace(old_next, new_next, 1)

    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    original = STATE_PATH.read_text(encoding="utf-8")
    try:
        transformed = transform(original)
    except ValueError as exc:
        print(f"Phase 17 state finalizer error: {exc}", file=sys.stderr)
        return 1

    if args.write:
        if transformed != original:
            STATE_PATH.write_text(transformed, encoding="utf-8")
            print("wrote=PROJECT_STATE.md")
        else:
            print("Phase 17 project state already finalized.")
        return 0

    if transformed != original:
        print("PROJECT_STATE.md has not been finalized for Phase 17", file=sys.stderr)
        return 1
    print("Phase 17 project state is finalized and idempotent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
