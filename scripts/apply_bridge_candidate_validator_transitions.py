#!/usr/bin/env python3
"""Apply or check inherited validator transitions for the non-live bridge candidate."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHASE11 = ROOT / "scripts" / "validate_phase11b_expansion.py"
PHASE12 = ROOT / "scripts" / "validate_phase12_release_candidate.py"

REPLACEMENTS: dict[Path, tuple[tuple[str, str], ...]] = {
    PHASE11: (
        (
            '''            if data.get("live") is not False or data.get("mode") != "compatibility-fixture":
                errors.append("Phase 11B must preserve the non-live Atlas compatibility fixture")''',
            '''            if data.get("live") is not False or data.get("mode") not in {"compatibility-fixture", "bridge-candidate"}:
                errors.append("Phase 11B must preserve a non-live Atlas bridge state")''',
        ),
    ),
    PHASE12: (
        ('        "non-live compatibility fixture",', '        "non-live bridge candidate",'),
        (
            '''    if bridge.get("mode") != "compatibility-fixture" or bridge.get("live") is not False:
        result.error("bridge fixture must remain non-live")''',
            '''    if bridge.get("mode") != "bridge-candidate" or bridge.get("live") is not False:
        result.error("bridge must remain a non-live bridge-candidate")''',
        ),
        (
            '''    scenarios = impact.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 5:''',
            '''    accepted = impact.get("accepted_changes")
    if not isinstance(accepted, list) or len(accepted) != 1:
        result.error("revision-impact contract must record exactly one accepted bridge change")
    else:
        adoption = accepted[0]
        if not isinstance(adoption, dict):
            result.error("accepted bridge change must be an object")
        else:
            expected_adoption = {
                "atlas_entity": "model:en:delayed-correction-recurrence",
                "from_revision": 1,
                "to_revision": 2,
                "inspection_outcome": "adopt-exact-revision",
                "principia_meaning_changed": False,
                "principia_artifact_revision_after": 1,
                "principia_pedagogical_status_after": "reviewed",
                "principia_release_status_after": "draft",
            }
            for key, expected in expected_adoption.items():
                if adoption.get(key) != expected:
                    result.error(f"accepted model revision transition `{key}` must equal {expected!r}")
    scenarios = impact.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 5:''',
        ),
        (
            '''    if scope.get("principia_artifact_revision") != 1:
        result.error("pilot must reference Principia artifact revision 1")''',
            '''    if scope.get("principia_artifact_revision") != 1:
        result.error("pilot must reference Principia artifact revision 1")
    if scope.get("export_contract") != "principia-atlas-external-dependent/0.2":
        result.error("pilot must reference the exact-revision candidate export contract")
    atlas_entities = scope.get("atlas_entities")
    if not isinstance(atlas_entities, list) or "model:en:delayed-correction-recurrence@2" not in atlas_entities:
        result.error("pilot must pin delayed-correction recurrence revision 2")
    for unchanged in (
        "claim:en:model-oscillation-does-not-prove-real-system@1",
        "concept:en:feedback@1",
        "concept:en:oscillation@1",
    ):
        if not isinstance(atlas_entities, list) or unchanged not in atlas_entities:
            result.error(f"pilot must preserve exact dependency {unchanged}")''',
        ),
        (
            '''    if state.get("mode") != "compatibility-fixture" or state.get("live") is not False or state.get("decision") != "hold":
        result.error("pilot integration state must remain compatibility-fixture, non-live, and hold")''',
            '''    if state.get("mode") != "bridge-candidate" or state.get("live") is not False or state.get("decision") != "candidate-ready":
        result.error("pilot integration state must be bridge-candidate, non-live, and candidate-ready")''',
        ),
    ),
}


def apply(text: str, replacements: tuple[tuple[str, str], ...], label: str, errors: list[str]) -> str:
    result = text
    for old, new in replacements:
        if new in result:
            continue
        if old not in result:
            errors.append(f"{label}: transition anchor missing: {old[:100]!r}")
            continue
        result = result.replace(old, new, 1)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    changes: list[tuple[Path, str]] = []
    for path, replacements in REPLACEMENTS.items():
        original = path.read_text(encoding="utf-8")
        updated = apply(original, replacements, str(path.relative_to(ROOT)), errors)
        try:
            compile(updated, str(path), "exec")
        except SyntaxError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
        if updated != original:
            changes.append((path, updated))

    if errors:
        print("Bridge candidate validator transition failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if args.check and changes:
        print("Bridge candidate validator transition is not applied:", file=sys.stderr)
        for path, _ in changes:
            print(f"- {path.relative_to(ROOT)}", file=sys.stderr)
        return 1
    if args.write:
        for path, updated in changes:
            path.write_text(updated, encoding="utf-8")
    print("Bridge candidate validator transition applied." if changes else "Bridge candidate validator transition already applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
