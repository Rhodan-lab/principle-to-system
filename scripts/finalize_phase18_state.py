#!/usr/bin/env python3
"""Apply or verify the Phase 18 project-state transition."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"

CURRENT_17 = "**Phase 17 — Offline Event-Protocol Candidate merged and validated through PR #22.**"
CURRENT_18 = (
    "**Phase 18 — Offline Reconciliation Simulation Candidate implemented on "
    "`agent/phase-18-offline-reconciliation-simulation`; exact-head validation pending.**"
)
SECTION = """## Phase 18 result — Offline Reconciliation Simulation

`release/phase-18-offline-reconciliation.json` defines the immutable candidate `offline-reconciliation-simulation-candidate` with `mode: offline-reconciliation-simulation` and `live: false`.

The simulation reconciles the official Phase 17 event stream, acknowledgement stream, digest chain, and current revisions of the three thermal-control artifacts. The exact baseline result is:

```yaml
event_count: 2
acknowledgement_count: 2
reconciled_count: 2
unacknowledged_count: 0
orphan_acknowledgement_count: 0
stale_artifact_reference_count: 0
action_mismatch_count: 0
decision: reconciled-no-mutation
```

The divergence matrix rejects missing or orphan acknowledgements, event-binding errors, weakened actions, affected-set mismatches, stale or missing Principia artifacts, reordered streams, chain-head mismatches, status inheritance, automatic mutation, and `live: true`.

Atlas remains unchanged. Reconciliation observes Principia pedagogical and release state only to verify exact current artifact revisions; it does not inherit or mutate those fields.

"""


def transform(text: str) -> str:
    if CURRENT_18 not in text:
        if CURRENT_17 not in text:
            raise ValueError("missing Phase 17 current-phase anchor")
        text = text.replace(CURRENT_17, CURRENT_18, 1)

    state17 = "Phase 17 state: **offline-event-protocol-validated** (`mode: offline-event-protocol`, `live: false`)."
    state18 = "Phase 18 target state: **offline-reconciliation-simulation-candidate** (`mode: offline-reconciliation-simulation`, `live: false`)."
    if state18 not in text:
        if state17 not in text:
            raise ValueError("missing Phase 17 state anchor")
        text = text.replace(state17, state17 + "  \n" + state18, 1)

    row17 = "| 17 | Offline event-protocol candidate | Merged and validated through PR #22 |"
    row18 = "| 18 | Offline reconciliation simulation | Implemented; exact-head validation pending |"
    if row18 not in text:
        if row17 not in text:
            raise ValueError("missing Phase 17 table anchor")
        text = text.replace(row17, row17 + "\n" + row18, 1)

    topology17 = "- PR #22 was merged into `main` at commit `c9fba79f821d59b36030924e5c388f71a56f7787`."
    topology24 = "- PR #24 finalized the Phase 17 record at `806b03335a1d0b43e5a32ffecce8439350564152`."
    if topology24 not in text:
        if topology17 not in text:
            raise ValueError("missing Phase 17 topology anchor")
        text = text.replace(topology17, topology17 + "\n" + topology24, 1)

    old_main = (
        "Main contains the reviewed material foundation, synthesis layer, four applied-learning routes, "
        "static software foundation, non-live exact-revision bridge candidate, pinned Atlas importer "
        "baseline, deterministic Phase 15 receipt, the integrated Phase 16 atomic three-artifact batch, "
        "and the integrated Phase 17 lifecycle-event stream, acknowledgement stream, digest chains, and recovery matrix."
    )
    new_main = old_main[:-1] + ", plus the Phase 18 reconciliation report, checkpoint, and divergence simulation candidate."
    if new_main not in text:
        if old_main not in text:
            raise ValueError("missing main inventory anchor")
        text = text.replace(old_main, new_main, 1)

    text = text.replace(
        "- Atlas remains unchanged by Principia Phase 17.",
        "- Atlas remains unchanged by Principia Phase 18.",
        1,
    )

    validation_heading = "## Validation\n"
    if SECTION not in text:
        if validation_heading not in text:
            raise ValueError("missing Validation heading")
        text = text.replace(validation_heading, SECTION + validation_heading, 1)

    phase17_command = "python3 scripts/validate_phase17_postmerge_record.py\n"
    phase18_commands = (
        "python3 scripts/generate_phase18_offline_reconciliation.py --check\n"
        "python3 scripts/generate_phase18_release_record.py --check\n"
        "python3 scripts/validate_phase18_offline_reconciliation.py\n"
        "python3 -m unittest software.tests.test_phase18_offline_reconciliation -v\n"
    )
    if phase18_commands not in text:
        if phase17_command not in text:
            raise ValueError("missing Phase 17 validation command anchor")
        text = text.replace(phase17_command, phase17_command + phase18_commands, 1)

    old_next = (
        "The next bounded gate is **Phase 18 — Offline Reconciliation Simulation Candidate**. It may "
        "simulate bounded disagreement, duplicate delivery, missed acknowledgements, and deterministic "
        "convergence using committed fixtures only. It must not activate networking, mutate Atlas, "
        "inherit status, or change `live: false`."
    )
    new_next = (
        "After Phase 18 integration, the next bounded gate is an **offline reconciliation-policy candidate**. "
        "It may convert reconciled findings into explicit non-mutating review queues or release-hold proposals, "
        "but it must not change content status, call Atlas, or activate live synchronization automatically."
    )
    if new_next not in text:
        if old_next not in text:
            raise ValueError("missing Phase 18 next-phase anchor")
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
        print(f"Phase 18 state finalizer error: {exc}", file=sys.stderr)
        return 1
    if args.write:
        if transformed != original:
            STATE_PATH.write_text(transformed, encoding="utf-8")
            print("wrote=PROJECT_STATE.md")
        else:
            print("Phase 18 project state already current.")
        return 0
    if transformed != original:
        print("PROJECT_STATE.md has not been finalized for Phase 18", file=sys.stderr)
        return 1
    print("Phase 18 project state is finalized and idempotent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
