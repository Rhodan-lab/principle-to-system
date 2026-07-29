#!/usr/bin/env python3
"""Validate deterministic Phase 34 execution-readiness assurance evidence."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import generate_phase34_offline_consequence_plan_review_response_intake_envelope_validation_execution_readiness_assurance as gen

ROOT=Path(__file__).resolve().parent.parent
CANDIDATE=ROOT/"release/phase-34-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance.json"
EXPECTED_SHA="2ca9b454124b1fb42f91f09479d9aed1d0c54f9ef443f121caa3a7ee67823828"

def main()->int:
    errors=gen.verify_sources()
    if not CANDIDATE.is_file(): errors.append("Phase 34 candidate missing")
    else:
        try: doc=json.loads(CANDIDATE.read_text())
        except Exception as exc: errors.append(f"Phase 34 JSON invalid: {exc}")
        else:
            errors.extend(gen.validate_document(doc))
            exact=gen.render(gen.build_document())
            if CANDIDATE.read_text()!=exact: errors.append("Phase 34 bytes are not deterministic")
            if hashlib.sha256(CANDIDATE.read_bytes()).hexdigest()!=EXPECTED_SHA: errors.append("Phase 34 candidate digest drift")
            records=doc.get("assurances",[])
            if len(records)!=2: errors.append("Phase 34 assurance count drift")
            if any(r.get("assurance_check_count")!=44 or not all(r.get("assurance_checks",{}).values()) for r in records): errors.append("Phase 34 assurance checks drift")
            if any(r.get("verdict")!="response-envelope-validation-execution-readiness-assured-no-envelope" for r in records): errors.append("Phase 34 verdict drift")
            if any(r.get(x) is not False for r in records for x in gen.ZERO_FIELDS): errors.append("Phase 34 frozen state drift")
            if doc.get("result",{}).get("assurance_check_count")!=88 or doc.get("result",{}).get("failed_assurance_count")!=0: errors.append("Phase 34 result drift")
            if doc.get("authority")!=gen.AUTHORITY: errors.append("Phase 34 authority drift")
    if errors:
        print("Phase 34 validation errors:",file=sys.stderr)
        for error in errors: print(f"- {error}",file=sys.stderr)
        return 1
    print(f"Phase 34 validation passed: sha256={EXPECTED_SHA}, 2 assurances, 88 checks, frozen zero-execution authority.")
    return 0
if __name__=="__main__": raise SystemExit(main())
