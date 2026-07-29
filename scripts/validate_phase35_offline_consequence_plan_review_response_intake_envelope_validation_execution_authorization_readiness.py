#!/usr/bin/env python3
"""Independently validate the deterministic Phase 35 authorization-readiness record."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
GENERATOR_PATH = ROOT / "scripts/generate_phase35_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_readiness.py"
MANIFEST_PATH = ROOT / "release/phase-35-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness.json"

spec = importlib.util.spec_from_file_location("phase35_generator", GENERATOR_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Unable to load Phase 35 generator")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


def load_manifest() -> dict[str, Any]:
    value = json.loads(MANIFEST_PATH.read_text())
    if not isinstance(value, dict):
        raise ValueError("Phase 35 manifest must be an object")
    return value


def validate_document(document: Mapping[str, Any], *, verify_source_files: bool = False) -> list[str]:
    errors = generator.validate_document(document)
    if verify_source_files:
        errors.extend(generator.verify_sources())
    if document.get("phase") != 35 or document.get("state") != generator.STATE or document.get("next_gate") != generator.NEXT_GATE:
        errors.append("Phase 35 identity or gate drift")
    records = document.get("authorization_readiness_records", [])
    if len(records) != 2:
        errors.append("Phase 35 authorization-readiness record count drift")
    for record in records:
        if record.get("authorization_requirement_evaluated_count") != 0:
            errors.append("Phase 35 requirement evaluation occurred")
        if record.get("approval_received_count") != 0 or record.get("human_gate_satisfied_count") != 0:
            errors.append("Phase 35 approval or human gate was satisfied")
        token = record.get("blank_authorization_token", {})
        if token.get("issued") is not False:
            errors.append("Phase 35 authorization token was issued")
        if any(token.get(field) is not None for field in generator.BLANK_AUTHORIZATION_TOKEN_FIELDS):
            errors.append("Phase 35 authorization token field was filled")
        if any(record.get(field) is not False for field in generator.ZERO_FIELDS):
            errors.append("Phase 35 frozen state was activated")
    authority = document.get("authority", {})
    if authority != generator.AUTHORITY:
        errors.append("Phase 35 authority drift")
    if document.get("live") is not False or document.get("real_authorization_claimed") is not False:
        errors.append("Phase 35 live or real authorization claim")
    return sorted(set(errors))


def main() -> int:
    if not MANIFEST_PATH.is_file():
        print("Phase 35 manifest missing", file=sys.stderr)
        return 1
    errors = validate_document(load_manifest(), verify_source_files=True)
    if errors:
        print("Phase 35 validation errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Phase 35 validation passed: 2 authorization-readiness records, 44 unevaluated requirements, 0 grants.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
