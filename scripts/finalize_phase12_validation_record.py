#!/usr/bin/env python3
"""Validate the finalized Phase 12 record after downstream phases have merged."""
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

REQUIRED: dict[Path, tuple[str, ...]] = {
    STATE: (
        "| 12 | Release candidate | Merged and validated through PR #14 |",
        "Phase 12 — Release Candidate implemented and validated on draft PR #14",
        "release decision remains **Hold**",
        "principia-material-foundation-rc1",
    ),
    REPORT: (
        "Validation status: implemented and validated on draft PR #14",
        "Automated conformance does not change the release decision",
        "Release decision: **Hold**",
    ),
    README: (
        "The Phase 12 validator passes on draft PR #14",
        "release decision remains Hold",
        "principia-material-foundation-rc1",
    ),
    AUDIT: (
        "machine-validated but unreleased Phase 12 material release candidate",
        "RC1 scope is frozen",
        "The release decision is **Hold**",
    ),
    VALIDATOR: (
        "release_candidate_gate",
        "live Atlas integration",
    ),
    WORKFLOW: (
        "contents: read",
        "finalize_phase12_validation_record.py --check",
        "validate_phase12_release_candidate.py",
    ),
}

FORBIDDEN_WORKFLOW = (
    "contents: write",
    "git push",
    "git commit",
    "pull_request_target",
    "Rhodan-lab/Atlas.git",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    parser.parse_args()

    errors: list[str] = []
    for path, markers in REQUIRED.items():
        if not path.is_file():
            errors.append(f"missing Phase 12 record: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing Phase 12 marker {marker!r}")

    try:
        pilot = json.loads(PILOT.read_text(encoding="utf-8"))
        readiness = pilot.get("principia_readiness")
        integration = pilot.get("integration_state")
        if not isinstance(readiness, dict) or readiness.get("release_candidate_gate") != "validated":
            errors.append("phase-12 pilot must retain release_candidate_gate=validated")
        if not isinstance(integration, dict) or integration.get("live") is not False:
            errors.append("phase-12 pilot must remain non-live")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"phase-12 pilot readiness: {exc}")

    if WORKFLOW.is_file():
        workflow = WORKFLOW.read_text(encoding="utf-8")
        for token in FORBIDDEN_WORKFLOW:
            if token in workflow:
                errors.append(f"Phase 12 workflow contains forbidden token: {token}")

    if errors:
        print("Phase 12 validation-record errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Phase 12 validation record finalized: RC1 remains machine-validated and on Hold, "
        "pilot remains non-live, and downstream phases preserve the historical contract."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
