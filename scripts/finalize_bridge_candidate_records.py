#!/usr/bin/env python3
"""Finalize or check active records for the non-live Principia–Atlas bridge candidate."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "PROJECT_STATE.md"
README = ROOT / "README.md"
AUDIT = ROOT / "AUDIT.md"
RELEASE = ROOT / "release" / "README.md"


def replace_once(text: str, old: str, new: str, label: str, errors: list[str]) -> str:
    if new in text:
        return text
    if old not in text:
        errors.append(f"{label}: replacement anchor missing: {old[:100]!r}")
        return text
    return text.replace(old, new, 1)


def insert_before(text: str, anchor: str, block: str, marker: str, label: str, errors: list[str]) -> str:
    if marker in text:
        return text
    if anchor not in text:
        errors.append(f"{label}: insertion anchor missing: {anchor!r}")
        return text
    return text.replace(anchor, block.rstrip() + "\n\n" + anchor, 1)


def transform_state(text: str, errors: list[str]) -> str:
    text = replace_once(
        text,
        "**Phase 13 — Software Foundation active on `agent/phase-13-software-foundation`; progression is governed by machine gates.**",
        "**Principia–Atlas bridge candidate active on `agent/bridge-candidate-delayed-correction-r2`; progression is governed by machine gates and live integration remains disabled.**",
        "PROJECT_STATE current phase",
        errors,
    )
    text = replace_once(
        text,
        "Software state: **foundation-validated**.",
        "Software state: **foundation-validated**.  \nBridge state: **candidate-ready** (`mode: bridge-candidate`, `live: false`).",
        "PROJECT_STATE bridge state",
        errors,
    )
    text = replace_once(
        text,
        "| 13 | Software foundation | Implemented and validated on draft PR #15; awaiting merge |",
        "| 13 | Software foundation | Merged and validated through PR #15 |\n| 14 | Principia–Atlas bridge candidate | Active; exact-revision validation pending |",
        "PROJECT_STATE phase table",
        errors,
    )
    text = replace_once(
        text,
        "PR #11 was merged into `main` at commit `058f164f6e181311a34d68def22e252e7e20f646`. PR #12 was merged into `main` at commit `565c119e63218b4376f501f99bc96c1e09a3acca`. PR #13 was merged into `main` at commit `223327901b6c1c259350622a00b822511293d516`. PR #14 was merged into `main` at commit `824fa2d4774647203222ab9198fc25ad4b11cda5`.",
        "PR #11 was merged into `main` at commit `058f164f6e181311a34d68def22e252e7e20f646`. PR #12 was merged into `main` at commit `565c119e63218b4376f501f99bc96c1e09a3acca`. PR #13 was merged into `main` at commit `223327901b6c1c259350622a00b822511293d516`. PR #14 was merged into `main` at commit `824fa2d4774647203222ab9198fc25ad4b11cda5`. PR #15 was merged into `main` at commit `fa9807fcdb649692d9670701211e155ecff21258`.",
        "PROJECT_STATE merge topology",
        errors,
    )
    text = replace_once(
        text,
        "- the non-live `principia-atlas-bridge/0.1` compatibility foundation.",
        "- the non-live `principia-atlas-bridge/0.1` compatibility foundation;\n- the Phase 13 content-native software foundation.",
        "PROJECT_STATE main contents",
        errors,
    )
    text = replace_once(
        text,
        "Phase 12 was merged through PR #14 and remains the validated material baseline. Phase 13 was created directly from that merge and adds a content-native static software layer, deterministic build artifacts, machine-only governance, tests, project documentation, and read-only CI.",
        "Phase 12 was merged through PR #14 and remains the validated material baseline. Phase 13 was merged through PR #15 and provides the content-native static software layer. The bridge-candidate branch was created directly from that integrated state and changes only Principia-side materials, exact-revision manifests, deterministic exports, governance records, tests, and read-only CI.",
        "PROJECT_STATE active topology",
        errors,
    )
    old_bridge = '''The compatibility fixture remains:

```yaml
mode: compatibility-fixture
live: false
```

No status crosses the repository boundary automatically.'''
    new_bridge = '''The active Principia–Atlas bridge candidate is:

```yaml
mode: bridge-candidate
live: false
```

Its exact Atlas references are:

```text
claim:en:model-oscillation-does-not-prove-real-system@1
model:en:delayed-correction-recurrence@2
concept:en:feedback@1
concept:en:oscillation@1
```

Atlas remains unchanged, and status remains separate: Atlas owns knowledge status; Principia owns pedagogical `status` and publication `release_status`. No status crosses the repository boundary automatically.'''
    text = replace_once(text, old_bridge, new_bridge, "PROJECT_STATE bridge contract", errors)
    old_pilot = '''Principia has exact artifact identity, status separation, deterministic export, and revision-impact scenarios. The pilot remains:

```yaml
mode: compatibility-fixture
live: false
decision: hold
```

Atlas remains unchanged. Atlas has not recorded that its direct-integration freeze has ended, accepted the external dependent, or approved a live pilot.'''
    new_pilot = '''Principia has exact artifact identity, status separation, deterministic exact-revision export, and revision-impact scenarios. The current importer candidate is:

```yaml
mode: bridge-candidate
live: false
decision: candidate-ready
```

Candidate-ready means Atlas Phase 2 may inspect the committed export through its own read-only importer. Atlas remains unchanged, has not accepted the external dependent, and no live cross-repository call is enabled.'''
    text = replace_once(text, old_pilot, new_pilot, "PROJECT_STATE pilot state", errors)
    text = replace_once(
        text,
        "After PR #15 merges, the next software phase expands product navigation, content operations, deployment packaging, and optional Atlas interoperability without changing content authority.",
        "After the bridge-candidate gate passes and its pull request is merged, Atlas Phase 2 may consume the committed `principia-atlas-external-dependent/0.2` file through its own importer. Live calls remain a later, separate contract transition.",
        "PROJECT_STATE next phase",
        errors,
    )
    return text


def transform_readme(text: str, errors: list[str]) -> str:
    text = replace_once(
        text,
        "| `integration/principia-atlas/` | Non-live bridge manifests, deterministic exports, and invalid fixtures |",
        "| `integration/principia-atlas/` | Non-live bridge-candidate manifests, exact-revision exports, and invalid fixtures |",
        "README structure",
        errors,
    )
    old = '''[`contracts/principia-atlas/0.1/`](contracts/principia-atlas/0.1/) defines `principia-atlas-bridge/0.1`. It allows Principia to declare exact-revision Atlas dependencies and generate the opaque external-dependent shape already supported by Atlas coverage reporting.

The current integration remains a non-live fixture:

```yaml
mode: compatibility-fixture
live: false
```

Principia does not clone Atlas during validation, and the export contains no Principia pedagogical or release status. A future live bridge requires compatible machine gates in both repositories. Phase 12 tests bounded readiness but does not activate the bridge, and Phase 13 keeps all Atlas calls disabled.'''
    new = '''[`contracts/principia-atlas/0.1/`](contracts/principia-atlas/0.1/) defines `principia-atlas-bridge/0.1`. The current Principia-side state is:

```yaml
mode: bridge-candidate
live: false
```

The candidate pins `model:en:delayed-correction-recurrence@2` while retaining the delayed-feedback claim and concepts at revision 1. Its deterministic `principia-atlas-external-dependent/0.2` export preserves legacy `depends_on` IDs and adds `depends_on_exact` records for Atlas Phase 2 exact-revision lookup and dependency-impact queries.

Principia does not clone or modify Atlas during validation. Atlas knowledge status, Principia pedagogical `status`, and Principia `release_status` remain separate, and the export contains none of those status fields. No live cross-repository call is enabled.'''
    text = replace_once(text, old, new, "README compatibility section", errors)
    return text


def transform_audit(text: str, errors: list[str]) -> str:
    text = replace_once(
        text,
        "> A reviewed 20-module Principia foundation with reconciled synthesis, four complete applied-learning routes, a machine-validated but unreleased Phase 12 material baseline, and an active machine-governed Phase 13 software foundation.",
        "> A reviewed 20-module Principia foundation with reconciled synthesis, four complete applied-learning routes, a validated Phase 13 software foundation, and a non-live exact-revision Principia–Atlas bridge candidate.",
        "AUDIT disposition",
        errors,
    )
    block = '''## Principia–Atlas bridge-candidate disposition

- The bridge uses `mode: bridge-candidate` with `live: false`.
- `model:en:delayed-correction-recurrence` advances from revision 1 to revision 2; the delayed-feedback claim and concepts remain at revision 1.
- The revision-2 recurrence proves a bounded exact period-6 orbit, so oscillation is not treated as proof of instability.
- The Principia failure pattern remains `artifact_revision: 1`, pedagogical `status: reviewed`, and `release_status: draft` because the change clarifies an existing model boundary rather than changing the principal conclusion.
- The deterministic export includes `depends_on_exact` for an Atlas Phase 2 importer while retaining legacy opaque dependency IDs.
- Atlas was not modified, no status is inherited, and no live cross-repository call is enabled.'''
    text = insert_before(
        text,
        "## Phase 13 software-foundation disposition",
        block,
        "## Principia–Atlas bridge-candidate disposition",
        "AUDIT bridge candidate",
        errors,
    )
    return text


def transform_release(text: str, errors: list[str]) -> str:
    text = replace_once(
        text,
        "- the non-live Principia–Atlas bridge fixture.",
        "- the historical non-live Principia–Atlas bridge fixture, now evolved into a non-live bridge candidate.",
        "release README Phase12 scope",
        errors,
    )
    old = '''## First bounded integration pilot

The delayed-feedback slice remains the preferred pilot because it already has an exact-revision compatibility fixture. The pilot may become live only after:

- Atlas exits its direct-integration freeze;
- Principia's live-manifest machine gate passes;
- Atlas accepts the external dependent;
- revision, staleness, deprecation, retraction, and recovery behavior pass end to end;
- neither repository imports the other repository’s status.

Phase 12 tests readiness for that pilot but does not activate it.'''
    new = '''## Principia–Atlas bridge candidate

The delayed-feedback slice is now a Principia-side Atlas Phase 2 importer candidate:

```yaml
mode: bridge-candidate
live: false
decision: candidate-ready
```

The exact dependency set pins `model:en:delayed-correction-recurrence@2` and keeps the related claim and concepts at revision 1. `phase-12-revision-impact.json` records the inspected adoption without changing Principia artifact revision, pedagogical status, or release status.

The deterministic export contract `principia-atlas-external-dependent/0.2` includes `depends_on_exact`. Atlas remains unchanged and decides independently whether its Phase 2 importer accepts the candidate.

A future live bridge still requires a separate validated contract transition. This candidate performs no network call, repository synchronization, status inheritance, automatic merge, or automatic publication.'''
    text = replace_once(text, old, new, "release README bridge candidate", errors)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    targets = (
        (STATE, transform_state),
        (README, transform_readme),
        (AUDIT, transform_audit),
        (RELEASE, transform_release),
    )
    changes: list[tuple[Path, str]] = []
    for path, transform in targets:
        original = path.read_text(encoding="utf-8")
        updated = transform(original, errors)
        if updated != original:
            changes.append((path, updated))

    required_markers = {
        STATE: (
            "Principia–Atlas bridge candidate active",
            "model:en:delayed-correction-recurrence@2",
            "mode: bridge-candidate",
            "live: false",
            "Atlas remains unchanged",
            "status remains separate",
            "release decision remains **Hold**",
        ),
        README: ("bridge-candidate", "delayed-correction-recurrence@2", "depends_on_exact"),
        AUDIT: ("Principia–Atlas bridge-candidate disposition", "bounded exact period-6 orbit"),
        RELEASE: ("principia-atlas-external-dependent/0.2", "candidate-ready"),
    }
    pending = {path: updated for path, updated in changes}
    for path, markers in required_markers.items():
        text = pending.get(path, path.read_text(encoding="utf-8"))
        for marker in markers:
            if marker not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing final marker {marker!r}")

    if errors:
        print("Bridge candidate record finalization failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if args.check and changes:
        print("Bridge candidate records are not finalized:", file=sys.stderr)
        for path, _ in changes:
            print(f"- {path.relative_to(ROOT)}", file=sys.stderr)
        return 1
    if args.write:
        for path, updated in changes:
            path.write_text(updated, encoding="utf-8")
    print("Bridge candidate records finalized." if changes else "Bridge candidate records already finalized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
