#!/usr/bin/env python3
"""Validate the deterministic Phase 29 response-intake envelope readiness candidate."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
GENERATOR = ROOT / "scripts/generate_phase29_offline_consequence_plan_review_response_intake_envelope_readiness.py"
CANDIDATE = ROOT / "release/phase-29-offline-consequence-plan-review-response-intake-envelope-readiness.json"


def load_generator():
    spec = importlib.util.spec_from_file_location("phase29_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load Phase 29 generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def main() -> int:
    errors: list[str] = []
    if not GENERATOR.is_file():
        errors.append("missing generator")
    if not CANDIDATE.is_file():
        errors.append("missing candidate")
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
    records = candidate.get("envelope_readiness_records", [])
    if len(records) != 2:
        errors.append("expected two envelope readiness records")
    result = candidate.get("result", {})
    expected_counts = {
        "blank_required_envelope_field_count": 12,
        "duplicate_envelope_count": 0,
        "envelope_readiness_record_count": 2,
        "envelope_section_count": 14,
        "envelope_spec_count": 2,
        "envelope_template_count": 2,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
        "integrity_failure_count": 0,
        "integrity_rule_count": 20,
        "quarantine_reason_code_count": 20,
        "quarantine_record_count": 0,
        "required_envelope_field_count": 28,
        "response_envelope_created_count": 0,
        "response_envelope_processed_count": 0,
        "response_envelope_received_count": 0,
        "response_received_count": 0,
        "response_validated_count": 0,
        "review_started_count": 0,
        "status_change_count": 0,
    }
    for key, expected_value in expected_counts.items():
        if result.get(key) != expected_value:
            errors.append(f"result {key}")
    recovery = candidate.get("recovery", {})
    if recovery.get("scenario_count") != 87 or recovery.get("accepted_count") != 1 or recovery.get("rejected_count") != 86:
        errors.append("recovery counts")
    if errors:
        print("Phase 29 candidate errors:", file=sys.stderr)
        for error in sorted(set(errors)):
            print(f"- {error}", file=sys.stderr)
        return 1
    raw = actual.encode()
    print(
        f"Phase 29 candidate passed: {len(raw)} bytes, sha256={hashlib.sha256(raw).hexdigest()}, "
        "2 envelope readiness records, 20 integrity rules, 20 quarantine reasons, 0 responses received."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
