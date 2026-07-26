#!/usr/bin/env python3
"""Finalize or check the Phase 13 machine-validation record."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "PROJECT_STATE.md"
REPORT = ROOT / "reports" / "phase-13-software-foundation.md"
README = ROOT / "README.md"
AUDIT = ROOT / "AUDIT.md"
RELEASE = ROOT / "release" / "README.md"

STATE_CHANGES = (
    (
        "Software state: **implementation pending validation**.",
        "Software state: **foundation-validated**.",
    ),
    (
        "| 13 | Software foundation | Active; machine validation pending |",
        "| 13 | Software foundation | Implemented and validated on draft PR #15; awaiting merge |",
    ),
    (
        "Phase 13 validates the reference software foundation. After that gate passes, the next software phase expands product navigation, content operations, deployment packaging, and optional Atlas interoperability without changing content authority.",
        "After PR #15 merges, the next software phase expands product navigation, content operations, deployment packaging, and optional Atlas interoperability without changing content authority.",
    ),
)

REPORT_BLOCK = """## Machine validation result

The Phase 13 workflow passes on draft PR #15. It validates Phase 12 continuity, strict repository structure, all unit tests, the 92-document catalog, 20 module groups, search completeness, graph integrity, generated-link containment, local-only browser assets, two byte-identical builds, the deployable static-site artifact, and workflow immutability.

```yaml
authority_mode: machine-only
software_state: foundation-validated
human_review_required: false
automatic_merge: false
automatic_publication: false
live_atlas_integration: false
```

Machine validation authorizes continuation of the software track without changing pedagogical or applied-experience release status.
"""

README_RESULT = "The Phase 13 machine gate passes on draft PR #15. The reference implementation is `foundation-validated`, and the generated site is reproducible from repository content."
AUDIT_RESULT = "- Phase 13 machine validation passes on draft PR #15 and the software state is `foundation-validated`."
RELEASE_RESULT = "The Phase 13 machine gate passes on draft PR #15, so the software foundation state is `foundation-validated`."


def replace_all(text: str, changes: tuple[tuple[str, str], ...], label: str, errors: list[str]) -> str:
    fixed = text
    for old, new in changes:
        if new in fixed:
            continue
        if old not in fixed:
            errors.append(f"{label}: transition source missing: {old[:100]}")
            continue
        fixed = fixed.replace(old, new, 1)
    return fixed


def insert_after(text: str, anchor: str, addition: str, label: str, errors: list[str]) -> str:
    if addition in text:
        return text
    if anchor not in text:
        errors.append(f"{label}: insertion anchor missing")
        return text
    return text.replace(anchor, anchor + "\n\n" + addition, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    changes: list[tuple[Path, str]] = []

    state = STATE.read_text(encoding="utf-8")
    fixed_state = replace_all(state, STATE_CHANGES, "PROJECT_STATE.md", errors)
    if fixed_state != state:
        changes.append((STATE, fixed_state))

    report = REPORT.read_text(encoding="utf-8")
    fixed_report = report
    if "> Validation status: **foundation-validated on draft PR #15**" not in fixed_report:
        anchor = "> Atlas integration: **non-live**"
        if anchor not in fixed_report:
            errors.append("Phase 13 report: status anchor missing")
        else:
            fixed_report = fixed_report.replace(anchor, anchor + "  \n> Validation status: **foundation-validated on draft PR #15**", 1)
    if "## Machine validation result" not in fixed_report:
        anchor = "## Content operations"
        if anchor not in fixed_report:
            errors.append("Phase 13 report: result anchor missing")
        else:
            fixed_report = fixed_report.replace(anchor, REPORT_BLOCK.rstrip() + "\n\n" + anchor, 1)
    if fixed_report != report:
        changes.append((REPORT, fixed_report))

    readme = README.read_text(encoding="utf-8")
    readme_anchor = "Routine content additions do not require application-code changes. Rebuilding updates document pages, module navigation, collection indexes, search data, catalog JSON, and dependency graph output automatically."
    fixed_readme = insert_after(readme, readme_anchor, README_RESULT, "README.md", errors)
    if fixed_readme != readme:
        changes.append((README, fixed_readme))

    audit = AUDIT.read_text(encoding="utf-8")
    audit_anchor = "- The active authority mode is machine-only; human review is not a blocking gate."
    fixed_audit = insert_after(audit, audit_anchor, AUDIT_RESULT, "AUDIT.md", errors)
    if fixed_audit != audit:
        changes.append((AUDIT, fixed_audit))

    release = RELEASE.read_text(encoding="utf-8")
    release_anchor = "A Phase 13 pass authorizes continued software development only. It does not mark material Complete, release applied experiences, copy Atlas status, or activate live integration."
    fixed_release = insert_after(release, release_anchor, RELEASE_RESULT, "release/README.md", errors)
    if fixed_release != release:
        changes.append((RELEASE, fixed_release))

    pending = {path: text for path, text in changes}
    required = {
        STATE: ("Software state: **foundation-validated**.", "Implemented and validated on draft PR #15"),
        REPORT: ("## Machine validation result", "software_state: foundation-validated"),
        README: (README_RESULT,),
        AUDIT: (AUDIT_RESULT,),
        RELEASE: (RELEASE_RESULT,),
    }
    for path, markers in required.items():
        text = pending.get(path, path.read_text(encoding="utf-8"))
        for marker in markers:
            if marker not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing final marker: {marker[:100]}")

    if errors:
        print("Phase 13 validation-record errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if args.check and changes:
        print("Phase 13 validation record is not finalized:", file=sys.stderr)
        for path, _ in changes:
            print(f"- {path.relative_to(ROOT)}", file=sys.stderr)
        return 1
    if args.write:
        for path, text in changes:
            path.write_text(text, encoding="utf-8")
    if changes:
        print("Phase 13 validation record finalized:")
        for path, _ in changes:
            print(f"- {path.relative_to(ROOT)}")
    else:
        print("Phase 13 validation record already finalized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
