#!/usr/bin/env python3
"""Finalize or verify the Phase 15 offline-pilot project-state transition."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "PROJECT_STATE.md"

REPLACEMENTS = (
    (
        "**Phase 14 — Principia–Atlas bridge candidate merged and validated through PR #16; ready for Atlas Phase 2 importer testing while live integration remains disabled.**",
        "**Phase 15 — Offline Integration Pilot implemented and machine-validated on draft PR #18; live integration remains disabled.**",
    ),
    (
        "Bridge state: **candidate-ready** (`mode: bridge-candidate`, `live: false`).",
        "Bridge state: **candidate-ready** (`mode: bridge-candidate`, `live: false`).  \nPilot state: **offline-pilot-validated** (`mode: offline-pilot`, `live: false`).",
    ),
    (
        "| 14 | Principia–Atlas bridge candidate | Merged and validated through PR #16 |",
        "| 14 | Principia–Atlas bridge candidate | Merged and validated through PR #16 |\n| 15 | Offline integration pilot | Implemented and machine-validated on draft PR #18; merge pending |",
    ),
    (
        "- the non-live exact-revision bridge candidate for the Atlas Phase 2 importer.",
        "- the non-live exact-revision bridge candidate for the Atlas Phase 2 importer;\n- the pinned Atlas PR #20 importer snapshot, deterministic offline receipt, and lifecycle-impact matrix.",
    ),
    (
        "Phase 12 was merged through PR #14 and remains the validated material baseline. Phase 13 was merged through PR #15 and provides the content-native static software layer. Phase 14 was merged through PR #16 and provides the validated exact-revision importer candidate. The candidate changes only Principia-side materials, manifests, exports, governance records, tests, and read-only CI.",
        "Phase 12 was merged through PR #14 and remains the validated material baseline. Phase 13 was merged through PR #15 and provides the content-native static software layer. Phase 14 was merged through PR #16 and provides the validated exact-revision importer candidate. Phase 15 pins the Atlas PR #20 importer evidence and validates a deterministic receipt plus lifecycle-impact matrix entirely offline. The phase changes only Principia-side integration evidence, governance records, tests, and read-only CI.",
    ),
    (
        "Candidate-ready means Atlas Phase 2 may inspect the committed export through its own read-only importer. Atlas remains unchanged, has not accepted the external dependent, and no live cross-repository call is enabled.",
        "Candidate-ready means Atlas Phase 2 may inspect the committed export through its own read-only importer. Atlas PR #20 subsequently accepted the exact export through a pinned read-only adapter. Principia Phase 15 verifies the resulting contract offline; no live cross-repository call is enabled.",
    ),
    (
        "python3 scripts/validate_principia_atlas_audit.py\npython3 scripts/validate_phase12_release_candidate.py",
        "python3 scripts/validate_principia_atlas_audit.py\npython3 scripts/generate_phase15_offline_pilot.py --check\npython3 scripts/validate_phase15_offline_pilot.py\npython3 scripts/validate_phase12_release_candidate.py",
    ),
    (
        "The exact PR #16 head passed source, scientific-review, synthesis, applied-material, compatibility, strict-repository, release-candidate, software, revision-impact, deterministic-export, and workflow-immutability gates before merge. Permanent CI remains read-only and cannot clone Atlas, write, commit, push, merge, promote lifecycle state, or activate integration.",
        "The exact PR #16 head passed source, scientific-review, synthesis, applied-material, compatibility, strict-repository, release-candidate, software, revision-impact, deterministic-export, and workflow-immutability gates before merge. Phase 15 additionally validates the pinned Atlas PR #20 importer, deterministic receipt, lifecycle scenarios, negative paths, and software continuity. Permanent CI remains read-only and cannot clone Atlas, write, commit, push, merge, promote lifecycle state, or activate integration.",
    ),
    (
        "## Next phase\n\nAtlas Phase 2 may now consume the committed `principia-atlas-external-dependent/0.2` file through its own read-only importer. Importer acceptance remains Atlas-owned. Live calls require a later, separate contract transition.",
        "## Phase 15 result — Offline Integration Pilot\n\n`release/phase-15-offline-pilot.json` defines the active `offline-pilot-validated` state. The pilot pins Atlas PR #20 at merge commit `1cc4aec6908a8703a7f505478329c633a23b4ef9`, verifies the exact Principia export digest, records an accepted four-dependency receipt, and exercises current, deprecated, stale, and retracted lifecycle outcomes.\n\nThe Atlas importer implementation is technically accepted. Atlas `PROJECT_STATE.md` still contains pre-merge wording for PR #20; Phase 15 records this as an explicit non-blocking governance observation rather than treating mutable prose as protocol authority.\n\n## Next phase\n\nThe next gate is a broader offline multi-artifact pilot with receipt versioning, multiple external dependents, mixed lifecycle states, and deterministic recovery scenarios. Live calls require a later, separate contract transition and remain disabled.",
    ),
)

FINAL_MARKERS = (
    "Phase 15 — Offline Integration Pilot",
    "offline-pilot-validated",
    "| 15 | Offline integration pilot |",
    "Atlas PR #20",
    "1cc4aec6908a8703a7f505478329c633a23b4ef9",
    "python3 scripts/validate_phase15_offline_pilot.py",
    "live: false",
)


def transformed(text: str) -> str:
    result = text
    for old, new in REPLACEMENTS:
        if old in result:
            result = result.replace(old, new, 1)
        elif new not in result:
            raise ValueError(f"missing Phase 15 transition anchor: {old[:80]}")
    return result


def check(text: str) -> None:
    expected = transformed(text)
    if expected != text:
        raise ValueError("PROJECT_STATE.md has not been finalized for Phase 15")
    for marker in FINAL_MARKERS:
        if marker not in text:
            raise ValueError(f"PROJECT_STATE.md missing Phase 15 marker: {marker}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = STATE_PATH.read_text(encoding="utf-8")
    if args.write:
        output = transformed(text)
        STATE_PATH.write_text(output, encoding="utf-8")
        print("Phase 15 project state finalized.")
        return 0
    check(text)
    print("Phase 15 project state is finalized and idempotent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
