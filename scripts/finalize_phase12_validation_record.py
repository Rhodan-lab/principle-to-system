#!/usr/bin/env python3
"""Finalize or check the Phase 12 automated-validation audit record."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "PROJECT_STATE.md"
REPORT = ROOT / "reports" / "phase-12-release-candidate.md"
README = ROOT / "README.md"
AUDIT = ROOT / "AUDIT.md"
PILOT = ROOT / "release" / "phase-12-pilot-readiness.json"
VALIDATOR = ROOT / "scripts" / "validate_phase12_release_candidate.py"
WORKFLOW = ROOT / ".github" / "workflows" / "validate-phase-12-release-candidate.yml"

STATE_REPLACEMENTS = (
    (
        "**Phase 12 — Release Candidate implemented on `agent/phase-12-release-candidate`; coordinated validation, independent review, and release authority remain pending.**",
        "**Phase 12 — Release Candidate implemented and validated on draft PR #14; independent review, merge, and release authority remain pending.**",
    ),
    (
        "| 12 | Release candidate | RC1 implemented; coordinated validation pending |",
        "| 12 | Release candidate | RC1 implemented and validated on draft PR #14; awaiting independent review and merge |",
    ),
    (
        "The permanent Phase 12 workflow must use `contents: read`, preserve diagnostics, and never clone Atlas, write, commit, push, merge, promote lifecycle state, or activate integration.",
        "The exact draft PR #14 head passes metadata, source, scientific-review, synthesis, applied-material, compatibility, strict-repository, accessibility, terminology, equation, revision-impact, and workflow-immutability gates. The permanent Phase 12 workflow uses `contents: read`, preserves diagnostics, and cannot clone Atlas, write, commit, push, merge, promote lifecycle state, or activate integration.",
    ),
    (
        "After RC1 automated validation, the project enters independent release review.",
        "After PR #14 receives independent review and is merged, the project enters human release review while the release decision remains Hold.",
    ),
)

REPORT_REPLACEMENTS = (
    (
        "> Release decision: **Hold**\n",
        "> Release decision: **Hold**  \n> Validation status: implemented and validated on draft PR #14\n",
    ),
    (
        "The permanent Phase 12 workflow will run:",
        "The permanent Phase 12 workflow runs:",
    ),
    (
        "The workflow must use `contents: read`, preserve diagnostics, and never clone Atlas, write files, commit, push, merge, promote status, or activate integration.",
        "The workflow uses `contents: read`, preserves diagnostics, and cannot clone Atlas, write files, commit, push, merge, promote status, or activate integration.",
    ),
    (
        "## Human authority still required\n",
        "## Automated validation result\n\nThe exact draft PR #14 head passes all inherited Phase 5–11B workflows and the Phase 12 release-candidate workflow. Strict repository validation reports zero warnings and zero errors. RC1 validates 60 core files, 16 synthesis files, 16 draft-release experiences, 143 core sources, 28 experience sources, the ten equation contracts, terminology boundaries, document accessibility heuristics, five revision-impact scenarios, and the non-live pilot record.\n\nAutomated conformance does not change the release decision. It remains **Hold**.\n\n## Human authority still required\n",
    ),
)

README_REPLACEMENTS = (
    (
        "A green Phase 12 validator establishes machine-checkable conformance only. It cannot grant independent scientific, editorial, accessibility, safety, attribution, release-owner, or Atlas-side approval.",
        "The Phase 12 validator passes on draft PR #14 and establishes machine-checkable RC1 conformance only. It cannot grant independent scientific, editorial, accessibility, safety, attribution, release-owner, or Atlas-side approval. The release decision remains Hold.",
    ),
)

AUDIT_REPLACEMENTS = (
    (
        "> A reviewed 20-module Principia foundation with reconciled synthesis, four complete applied-learning routes, exact-revision compatibility preparation, and an unreleased Phase 12 material release candidate awaiting coordinated automated validation and independent human authority.",
        "> A reviewed 20-module Principia foundation with reconciled synthesis, four complete applied-learning routes, exact-revision compatibility preparation, and a machine-validated but unreleased Phase 12 material release candidate awaiting independent human authority.",
    ),
    (
        "- RC1 scope is frozen in `release/phase-12-release-candidate.json`.",
        "- RC1 scope is frozen in `release/phase-12-release-candidate.json` and automated conformance passes on draft PR #14.",
    ),
)

VALIDATOR_OLD = '''    if principia.get("human_release_approval") is not False:
        result.error("pilot must record that human release approval is absent")'''
VALIDATOR_NEW = '''    if principia.get("release_candidate_gate") != "validated":
        result.error("pilot must record a validated Principia release-candidate gate")
    if principia.get("human_release_approval") is not False:
        result.error("pilot must record that human release approval is absent")'''

WORKFLOW_OLD = '''          python3 -m py_compile scripts/validate_principia_atlas_audit.py
          python3 -m py_compile scripts/validate_phase12_release_candidate.py'''
WORKFLOW_NEW = '''          python3 -m py_compile scripts/validate_principia_atlas_audit.py
          python3 -m py_compile scripts/finalize_phase12_validation_record.py
          python3 -m py_compile scripts/validate_phase12_release_candidate.py'''

WORKFLOW_RC_OLD = '''      - name: Validate Phase 12 release candidate
        id: release_candidate
        shell: bash
        run: |
          set +e
          python3 scripts/validate_phase12_release_candidate.py > phase12-validation.log 2>&1'''
WORKFLOW_RC_NEW = '''      - name: Validate Phase 12 release candidate
        id: release_candidate
        shell: bash
        run: |
          set +e
          python3 scripts/finalize_phase12_validation_record.py --check > phase12-validation.log 2>&1
          finalizer_status=$?
          if [ "$finalizer_status" -eq 0 ]; then
            python3 scripts/validate_phase12_release_candidate.py >> phase12-validation.log 2>&1
            validator_status=$?
          else
            validator_status=0
          fi
          if [ "$finalizer_status" -ne 0 ]; then
            status=$finalizer_status
          else
            status=$validator_status
          fi'''

WORKFLOW_RC_TAIL_OLD = '''          status=$?
          echo "status=$status" >> "$GITHUB_OUTPUT"
          cat phase12-validation.log
          exit 0'''
WORKFLOW_RC_TAIL_NEW = '''          echo "status=$status" >> "$GITHUB_OUTPUT"
          cat phase12-validation.log
          exit 0'''


def replace_all(text: str, replacements: tuple[tuple[str, str], ...], label: str, errors: list[str]) -> str:
    fixed = text
    for old, new in replacements:
        if new in fixed:
            continue
        if old not in fixed:
            errors.append(f"{label}: expected transition text is missing: {old[:80]}")
            continue
        fixed = fixed.replace(old, new, 1)
    return fixed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    changes: list[tuple[Path, str]] = []

    text_targets = (
        (STATE, STATE_REPLACEMENTS, "PROJECT_STATE.md"),
        (REPORT, REPORT_REPLACEMENTS, "Phase 12 report"),
        (README, README_REPLACEMENTS, "README.md"),
        (AUDIT, AUDIT_REPLACEMENTS, "AUDIT.md"),
    )
    for path, replacements, label in text_targets:
        try:
            original = path.read_text(encoding="utf-8")
            fixed = replace_all(original, replacements, label, errors)
            if fixed != original:
                changes.append((path, fixed))
        except OSError as exc:
            errors.append(str(exc))

    try:
        original = PILOT.read_text(encoding="utf-8")
        pilot = json.loads(original)
        pilot["principia_readiness"]["release_candidate_gate"] = "validated"
        fixed = json.dumps(pilot, indent=2, ensure_ascii=False) + "\n"
        if fixed != original:
            changes.append((PILOT, fixed))
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        errors.append(f"pilot readiness: {exc}")

    try:
        original = VALIDATOR.read_text(encoding="utf-8")
        fixed = original
        if VALIDATOR_NEW not in fixed:
            if VALIDATOR_OLD not in fixed:
                errors.append("Phase 12 validator: pilot gate insertion point missing")
            else:
                fixed = fixed.replace(VALIDATOR_OLD, VALIDATOR_NEW, 1)
        compile(fixed, str(VALIDATOR), "exec")
        if fixed != original:
            changes.append((VALIDATOR, fixed))
    except (OSError, SyntaxError) as exc:
        errors.append(str(exc))

    try:
        original = WORKFLOW.read_text(encoding="utf-8")
        fixed = original
        if WORKFLOW_NEW not in fixed:
            if WORKFLOW_OLD not in fixed:
                errors.append("Phase 12 workflow: compile insertion point missing")
            else:
                fixed = fixed.replace(WORKFLOW_OLD, WORKFLOW_NEW, 1)
        if WORKFLOW_RC_NEW not in fixed:
            if WORKFLOW_RC_OLD not in fixed:
                errors.append("Phase 12 workflow: RC command insertion point missing")
            else:
                fixed = fixed.replace(WORKFLOW_RC_OLD, WORKFLOW_RC_NEW, 1)
        if WORKFLOW_RC_TAIL_NEW not in fixed:
            if WORKFLOW_RC_TAIL_OLD not in fixed:
                errors.append("Phase 12 workflow: RC status tail missing")
            else:
                fixed = fixed.replace(WORKFLOW_RC_TAIL_OLD, WORKFLOW_RC_TAIL_NEW, 1)
        if fixed != original:
            changes.append((WORKFLOW, fixed))
    except OSError as exc:
        errors.append(str(exc))

    required_markers = {
        STATE: (
            "implemented and validated on draft PR #14",
            "release decision remains **Hold**",
        ),
        REPORT: (
            "Validation status: implemented and validated on draft PR #14",
            "Automated conformance does not change the release decision",
        ),
        README: ("validator passes on draft PR #14", "release decision remains Hold"),
        AUDIT: ("machine-validated but unreleased",),
    }
    pending = {path: fixed for path, fixed in changes}
    for path, markers in required_markers.items():
        try:
            text = pending.get(path, path.read_text(encoding="utf-8"))
        except OSError as exc:
            errors.append(str(exc))
            continue
        for marker in markers:
            if marker not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing final marker: {marker}")

    if errors:
        print("Phase 12 validation-record errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if args.check and changes:
        print("Phase 12 validation record is not finalized:", file=sys.stderr)
        for path, _ in changes:
            print(f"- {path.relative_to(ROOT)}", file=sys.stderr)
        return 1

    if args.write:
        for path, fixed in changes:
            path.write_text(fixed, encoding="utf-8")

    if changes:
        print("Phase 12 validation record finalized:")
        for path, _ in changes:
            print(f"- {path.relative_to(ROOT)}")
    else:
        print("Phase 12 validation record already finalized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
