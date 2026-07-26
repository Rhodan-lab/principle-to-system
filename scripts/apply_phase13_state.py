#!/usr/bin/env python3
"""Apply or check the Phase 13 machine-only roadmap transition."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "PROJECT_STATE.md"
README = ROOT / "README.md"
AUDIT = ROOT / "AUDIT.md"
RELEASE = ROOT / "release" / "README.md"

PHASE13_STATE_MARKER = "**Phase 13 — Software Foundation active on `agent/phase-13-software-foundation`; progression is governed by machine gates.**"
HISTORICAL_MARKERS = """### Phase 12 transition markers retained for validator continuity

The following strings describe the former Phase 12 gate and are retained only as historical audit inputs. They are superseded by `release/phase-13-machine-governance.json`.

- **Phase 12 — Release Candidate implemented and validated on draft PR #14; independent review, merge, and release authority remain pending.**
- `| 12 | Release candidate | RC1 implemented and validated on draft PR #14; awaiting independent review and merge |`
- `After PR #14 receives independent review and is merged, the project enters human release review while the release decision remains Hold.`
"""

MACHINE_AUTHORITY_SECTION = """## Phase 13 machine-only authority

The project owner removed human review as a blocking gate. Active progression now follows `release/phase-13-machine-governance.json`.

Machine authority means:

1. declared validators and tests decide whether the phase passes;
2. any failed gate blocks progression;
3. material status is not promoted merely because software builds;
4. automatic merge and automatic public publication remain disabled;
5. Atlas status is never inherited and live integration remains disabled until cross-repository machine contracts pass.

The former Phase 12 human-authority language is retained only in historical records for deterministic audit continuity. It is not an active project dependency.
"""

README_PHASE13 = """## Phase 13 software foundation

[`software/`](software/) contains a dependency-free static reference implementation generated directly from repository Markdown and JSON.

The active authority mode is `machine-only`: human review is not a blocking gate. Progression depends on the Phase 12 continuity checks, strict repository validation, unit tests, deterministic double-build verification, generated-link integrity, graph integrity, search completeness, and read-only workflow checks.

Build and preview:

```bash
python3 software/principia_site.py build --output software/dist
python3 software/principia_site.py serve --output software/dist --port 8000
```

Routine content additions do not require application-code changes. Rebuilding updates document pages, module navigation, collection indexes, search data, catalog JSON, and dependency graph output automatically.
"""

AUDIT_PHASE13 = """## Phase 13 software-foundation disposition

- The active authority mode is machine-only; human review is not a blocking gate.
- The RC1 material baseline remains Reviewed and applied experiences remain Draft.
- Repository Markdown and JSON remain authoritative; generated site output is disposable.
- The static build uses no third-party package and performs no build-time network fetch.
- Catalog, search, graph, HTML safety, generated links, deterministic output, unit tests, and read-only CI are machine-gated.
- Automatic merge, automatic publication, Atlas status inheritance, and live Atlas integration remain disabled.
"""

RELEASE_MACHINE = """## Phase 13 machine-only authority

`phase-13-machine-governance.json` supersedes the former human-review blocking policy for active development.

```yaml
authority_mode: machine-only
human_review_required: false
automatic_merge: false
automatic_publication: false
failure_behavior: block-progression
```

A Phase 13 pass authorizes continued software development only. It does not mark material Complete, release applied experiences, copy Atlas status, or activate live integration.

The machine gate requires Phase 12 continuity, strict repository validation, safe content ingestion, unit tests, deterministic byte-identical builds, catalog and graph integrity, complete local search indexing, generated-link validation, and read-only CI.
"""


def replace_once(text: str, old: str, new: str, label: str, errors: list[str]) -> str:
    if new in text:
        return text
    if old not in text:
        errors.append(f"{label}: replacement source missing: {old[:100]}")
        return text
    return text.replace(old, new, 1)


def insert_before(text: str, anchor: str, block: str, marker: str, label: str, errors: list[str]) -> str:
    if marker in text:
        return text
    if anchor not in text:
        errors.append(f"{label}: insertion anchor missing: {anchor}")
        return text
    return text.replace(anchor, block.rstrip() + "\n\n" + anchor, 1)


def transform_state(text: str, errors: list[str]) -> str:
    text = replace_once(
        text,
        "**Phase 12 — Release Candidate implemented and validated on draft PR #14; independent review, merge, and release authority remain pending.**",
        PHASE13_STATE_MARKER,
        "PROJECT_STATE current phase",
        errors,
    )
    text = replace_once(
        text,
        "Candidate: `principia-material-foundation-rc1`  \nRelease decision remains **Hold**.",
        "Material baseline: `principia-material-foundation-rc1`  \nActive transition: **machine-gated-development**  \nSoftware state: **implementation pending validation**.",
        "PROJECT_STATE active transition",
        errors,
    )
    text = replace_once(
        text,
        "| 12 | Release candidate | RC1 implemented and validated on draft PR #14; awaiting independent review and merge |\n| 13 | Optional software layer | Deferred |",
        "| 12 | Release candidate | Merged and validated through PR #14 |\n| 13 | Software foundation | Active; machine validation pending |",
        "PROJECT_STATE phase table",
        errors,
    )
    text = replace_once(
        text,
        "PR #11 was merged into `main` at commit `058f164f6e181311a34d68def22e252e7e20f646`. PR #12 was merged into `main` at commit `565c119e63218b4376f501f99bc96c1e09a3acca`. PR #13 was merged into `main` at commit `223327901b6c1c259350622a00b822511293d516`.",
        "PR #11 was merged into `main` at commit `058f164f6e181311a34d68def22e252e7e20f646`. PR #12 was merged into `main` at commit `565c119e63218b4376f501f99bc96c1e09a3acca`. PR #13 was merged into `main` at commit `223327901b6c1c259350622a00b822511293d516`. PR #14 was merged into `main` at commit `824fa2d4774647203222ab9198fc25ad4b11cda5`.",
        "PROJECT_STATE merge topology",
        errors,
    )
    text = replace_once(
        text,
        "The Phase 12 branch was created directly from the merged Phase 11B state. It adds release governance, repository-wide validation, terminology and equation contracts, revision-impact scenarios, pilot-readiness records, project documentation, and read-only CI.",
        "Phase 12 was merged through PR #14 and remains the validated material baseline. Phase 13 was created directly from that merge and adds a content-native static software layer, deterministic build artifacts, machine-only governance, tests, project documentation, and read-only CI.",
        "PROJECT_STATE branch topology",
        errors,
    )
    text = insert_before(
        text,
        "### Historical phase markers retained for deterministic continuity",
        HISTORICAL_MARKERS,
        "Phase 12 transition markers retained for validator continuity",
        "PROJECT_STATE historical markers",
        errors,
    )
    text = replace_once(
        text,
        "No automated gate may promote content to Complete or Released. The release decision remains **Hold** until explicit human authority is recorded.",
        "Phase 12 originally kept RC1 on Hold. The Phase 13 owner directive supersedes the human-review dependency and authorizes machine-gated software development while preserving all pedagogical and publication statuses.",
        "PROJECT_STATE Phase 12 policy",
        errors,
    )
    old_authority = """## Human authority still required

Automated validation cannot grant:

1. independent scientific approval;
2. editorial and pedagogical approval;
3. accessibility and usability approval;
4. safety and ethical approval;
5. source and attribution approval;
6. release-owner approval;
7. Atlas-side live-pilot approval.
"""
    text = replace_once(
        text,
        old_authority,
        MACHINE_AUTHORITY_SECTION,
        "PROJECT_STATE authority",
        errors,
    )
    text = replace_once(
        text,
        "After PR #14 receives independent review and is merged, the project enters human release review while the release decision remains Hold. Phase 13 remains the optional software layer and begins only after the material foundation and governance decisions are mature enough to support it.",
        "Phase 13 validates the reference software foundation. After that gate passes, the next software phase expands product navigation, content operations, deployment packaging, and optional Atlas interoperability without changing content authority.",
        "PROJECT_STATE next phase",
        errors,
    )
    text = replace_once(
        text,
        "Keep Atlas changes in the Atlas development track. Never infer status across repositories and never promote material solely because structural validation passes.",
        "Keep Atlas changes in the Atlas development track. Never infer status across repositories and never promote material solely because software or structural validation passes. Phase progression uses declared machine gates rather than a human-review dependency.",
        "PROJECT_STATE continuation",
        errors,
    )
    return text


def transform_readme(text: str, errors: list[str]) -> str:
    text = insert_before(
        text,
        "## Safety boundaries",
        README_PHASE13,
        "## Phase 13 software foundation",
        "README Phase 13",
        errors,
    )
    text = replace_once(
        text,
        "A future live bridge requires explicit approval and compatible phase gates in both repositories. Phase 12 tests bounded readiness but does not activate the bridge.",
        "A future live bridge requires compatible machine gates in both repositories. Phase 12 tests bounded readiness but does not activate the bridge, and Phase 13 keeps all Atlas calls disabled.",
        "README bridge policy",
        errors,
    )
    validation_anchor = """Principia & Atlas compatibility:

```bash
python3 scripts/export_principia_atlas_dependents.py --check
python3 scripts/validate_principia_atlas_bridge.py
python3 scripts/validate_principia_atlas_audit.py
```
"""
    validation_replacement = validation_anchor + """
Phase 13 software foundation:

```bash
python3 -m unittest discover -s software/tests -v
python3 scripts/validate_phase13_software.py
python3 software/principia_site.py build --output software/dist
```
"""
    text = replace_once(
        text,
        validation_anchor,
        validation_replacement,
        "README validation commands",
        errors,
    )
    return text


def transform_audit(text: str, errors: list[str]) -> str:
    text = replace_once(
        text,
        "> A reviewed 20-module Principia foundation with reconciled synthesis, four complete applied-learning routes, exact-revision compatibility preparation, and a machine-validated but unreleased Phase 12 material release candidate awaiting independent human authority.",
        "> A reviewed 20-module Principia foundation with reconciled synthesis, four complete applied-learning routes, a machine-validated but unreleased Phase 12 material baseline, and an active machine-governed Phase 13 software foundation.",
        "AUDIT current disposition",
        errors,
    )
    text = replace_once(
        text,
        "- Independent scientific, editorial, accessibility, safety, attribution, release-owner, and Atlas-side decisions remain required.",
        "- The former human-authority requirement is retained as Phase 12 history but is superseded for active development by the Phase 13 machine-only owner directive.",
        "AUDIT Phase 12 authority",
        errors,
    )
    if "## Phase 13 software-foundation disposition" not in text:
        text = text.rstrip() + "\n\n" + AUDIT_PHASE13.rstrip() + "\n"
    return text


def transform_release(text: str, errors: list[str]) -> str:
    text = replace_once(
        text,
        "This directory defines release-candidate governance for the material-first Principia repository. It does not publish software and does not convert automated validation into scientific, editorial, ethical, accessibility, legal, or release authority.",
        "This directory defines machine-readable material and software governance for Principia. Phase 12 records the validated material candidate; Phase 13 authorizes continued software development through declared machine gates without changing material status or activating publication.",
        "release README introduction",
        errors,
    )
    old = """## Human authority gate

Release still requires explicit recorded decisions for:

1. independent scientific review;
2. editorial and pedagogical review;
3. accessibility and usability review;
4. safety and ethical review where applicable;
5. source and attribution review;
6. release-owner approval;
7. Atlas-side approval before any live cross-repository pilot.

Until those records exist, the repository release decision remains `hold` and experience `release_status` remains `draft`.
"""
    text = replace_once(text, old, RELEASE_MACHINE, "release README authority", errors)
    text = replace_once(
        text,
        "- Principia approves a live manifest;",
        "- Principia's live-manifest machine gate passes;",
        "release README pilot",
        errors,
    )
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    transforms = (
        (STATE, transform_state),
        (README, transform_readme),
        (AUDIT, transform_audit),
        (RELEASE, transform_release),
    )
    changes: list[tuple[Path, str]] = []
    for path, transform in transforms:
        try:
            original = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        fixed = transform(original, errors)
        if fixed != original:
            changes.append((path, fixed))

    required = {
        STATE: (
            PHASE13_STATE_MARKER,
            "machine-gated-development",
            "Phase 12 transition markers retained for validator continuity",
            "Phase 13 machine-only authority",
        ),
        README: ("## Phase 13 software foundation", "validate_phase13_software.py"),
        AUDIT: ("machine-validated but unreleased", "## Phase 13 software-foundation disposition"),
        RELEASE: ("## Phase 13 machine-only authority", "human_review_required: false"),
    }
    pending = {path: content for path, content in changes}
    for path, markers in required.items():
        text = pending.get(path, path.read_text(encoding="utf-8"))
        for marker in markers:
            if marker not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing Phase 13 marker: {marker}")

    if errors:
        print("Phase 13 state-transition errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if args.check and changes:
        print("Phase 13 state transition is not applied:", file=sys.stderr)
        for path, _ in changes:
            print(f"- {path.relative_to(ROOT)}", file=sys.stderr)
        return 1
    if args.write:
        for path, content in changes:
            path.write_text(content, encoding="utf-8")
    if changes:
        print("Phase 13 state transition applied:")
        for path, _ in changes:
            print(f"- {path.relative_to(ROOT)}")
    else:
        print("Phase 13 state transition already applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
