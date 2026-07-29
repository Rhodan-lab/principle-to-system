#!/usr/bin/env python3
"""Validate deterministic Phase 32 validation-readiness assurance evidence."""
from __future__ import annotations
import json, sys
from pathlib import Path
from generate_phase32_offline_consequence_plan_review_response_intake_envelope_validation_readiness_assurance import (
    OUT, build_document, render, validate_document, verify_sources
)

def main()->int:
    errors=verify_sources()
    if not OUT.is_file():
        errors.append("Phase 32 candidate missing")
    else:
        try:
            document=json.loads(OUT.read_text())
        except Exception as exc:
            errors.append(f"Phase 32 candidate JSON invalid: {exc}")
        else:
            errors.extend(validate_document(document))
            if OUT.read_text()!=render(build_document()):
                errors.append("Phase 32 candidate bytes are not canonical")
    if errors:
        print("Phase 32 validation errors:",file=sys.stderr)
        for error in errors: print(f"- {error}",file=sys.stderr)
        return 1
    print("Phase 32 validation passed: exact sources, 2 assurances, 66 checks, frozen zero-validation authority.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
