#!/usr/bin/env python3
"""Finalize or check the Phase 13 machine-validation record, including downstream phases."""

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


def replace_once(text: str, old: str, new: str, label: str, errors: list[str]) -> str:
    if new in text:
        return text
    if old not in text:
        errors.append(f"{label}: transition source missing: {old[:100]}")
        return text
    return text.replace(old, new, 1)


def insert_after(text: str, anchor: str, addition: str, label: str, errors: list[str]) -> str:
    if addition in text:
        return text
    if anchor not in text:
        errors.append(f"{label}: insertion anchor missing")
        return text
    return text.replace(anchor, anchor + "\n\n" + addition, 1)


def finalize_state(text: str, errors: list[str]) -> str:
    fixed = text
    if "Software state: **foundation-validated**." not in fixed:
        fixed = replace_once(
            fixed,
            "Software state: **implementation pending validation**.",
            "Software state: **foundation-validated**.",
            "PROJECT_STATE.md software state",
            errors,
        )

    phase_pending = "| 13 | Software foundation | Active; machine validation pending |"
    phase_validated = "| 13 | Software foundation | Implemented and validated on draft PR #15; awaiting merge |"
    phase_merged = "| 13 | Software foundation | Merged and validated through PR #15 |"
    if phase_pending in fixed:
        fixed = fixed.replace(phase_pending, phase_validated, 1)
    elif phase_validated not in fixed and phase_merged not in fixed:
        errors.append("PROJECT_STATE.md: Phase 13 validated or merged table marker is missing")

    old_next = "Phase 13 validates the reference software foundation. After that gate passes, the next software phase expands product navigation, content operations, deployment packaging, and optional Atlas interoperability without changing content authority."
    validated_next = "After PR #15 merges, the next software phase expands product navigation, content operations, deployment packaging, and optional Atlas interoperability without changing content authority."
    downstream_next = "After the bridge-candidate gate passes and its pull request is merged, Atlas Phase 2 may consume the committed `principia-atlas-external-dependent/0.2` file through its own importer. Live calls remain a later, separate contract transition."
    if old_next in fixed:
        fixed = fixed.replace(old_next, validated_next, 1)
    elif validated_next not in fixed and downstream_next not in fixed:
        errors.append("PROJECT_STATE.md: Phase 13 or downstream continuation marker is missing")
    return fixed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    changes: list[tuple[Path, str]] = []

    state = STATE.read_text(encoding="utf-8")
    fixed_state = finalize_state(state, errors)
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
        REPORT: ("## Machine validation result", "software_state: foundation-validated"),
        README: (README_RESULT,),
        AUDIT: (AUDIT_RESULT,),
        RELEASE: (RELEASE_RESULT,),
    }
    state_value = pending.get(STATE, STATE.read_text(encoding="utf-8"))
    if "Software state: **foundation-validated**." not in state_value:
        errors.append("PROJECT_STATE.md: missing final marker: Software state foundation-validated")
    if not any(
        marker in state_value
        for marker in (
            "| 13 | Software foundation | Implemented and validated on draft PR #15; awaiting merge |",
            "| 13 | Software foundation | Merged and validated through PR #15 |",
        )
    ):
        errors.append("PROJECT_STATE.md: missing Phase 13 validated lifecycle marker")

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
        print("Phase 13 validation record already finalized, including downstream state.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
