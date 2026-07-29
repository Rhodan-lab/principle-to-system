#!/usr/bin/env python3
"""Validate deterministic Phase 31 response-envelope validation readiness."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
GENERATOR = ROOT / "scripts/generate_phase31_offline_consequence_plan_review_response_intake_envelope_validation_readiness.py"
CANDIDATE = ROOT / "release/phase-31-offline-consequence-plan-review-response-intake-envelope-validation-readiness.json"

def load_generator():
    spec = importlib.util.spec_from_file_location("phase31_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load Phase 31 generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path)
    return value

def main() -> int:
    errors: list[str] = []
    for path in (GENERATOR, CANDIDATE):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    generator = load_generator()
    errors.extend(generator.verify_sources())
    candidate = load(CANDIDATE)
    errors.extend(generator.validate_document(candidate))
    expected = generator.render(generator.build_document())
    actual = CANDIDATE.read_text(encoding="utf-8")
    if actual != expected:
        errors.append("candidate bytes differ from deterministic generation")

    result = candidate.get("result", {})
    expected_counts = {
        "blank_validation_receipt_count": 2,
        "blank_validation_receipt_field_count": 20,
        "disposition_selected_count": 0,
        "envelope_readiness_assurance_record_count": 2,
        "failed_control_count": 0,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
        "possible_disposition_count": 6,
        "response_envelope_created_count": 0,
        "response_envelope_received_count": 0,
        "response_envelope_processed_count": 0,
        "response_received_count": 0,
        "review_started_count": 0,
        "status_change_count": 0,
        "validation_completed_count": 0,
        "validation_control_count": 36,
        "validation_execution_authorized_count": 0,
        "validation_profile_count": 2,
        "validation_readiness_record_count": 2,
        "validation_result_recorded_count": 0,
        "validation_run_count": 0,
        "validation_stage_count": 16,
        "validation_started_count": 0,
    }
    for key, expected_value in expected_counts.items():
        if result.get(key) != expected_value:
            errors.append(f"result {key}")

    records = candidate.get("validation_readiness_records", [])
    if len(records) != 2:
        errors.append("expected two validation-readiness records")
    for record in records:
        profile = record.get("validation_profile", {})
        if len(profile.get("stages", [])) != 8:
            errors.append("stage count")
        if len(profile.get("controls", [])) != 18:
            errors.append("control count")
        if len(profile.get("dispositions", [])) != 3:
            errors.append("disposition count")
        receipt = record.get("blank_validation_receipt", {})
        for field in generator.BLANK_RECEIPT_FIELDS:
            if receipt.get(field) is not None:
                errors.append(f"filled blank receipt field {field}")
        if receipt.get("executed") is not False:
            errors.append("blank receipt executed")

    recovery = candidate.get("recovery", {})
    if recovery.get("accepted_count") != 1:
        errors.append("accepted recovery count")
    if recovery.get("scenario_count") != recovery.get("rejected_count", -1) + 1:
        errors.append("recovery arithmetic")

    if errors:
        print("Phase 31 candidate errors:", file=sys.stderr)
        for error in sorted(set(errors)):
            print(f"- {error}", file=sys.stderr)
        return 1

    raw = actual.encode()
    print(
        f"Phase 31 candidate passed: {len(raw)} bytes, sha256={hashlib.sha256(raw).hexdigest()}, "
        "2 validation profiles, 36 inactive controls, 6 inactive dispositions, 0 envelopes received."
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
