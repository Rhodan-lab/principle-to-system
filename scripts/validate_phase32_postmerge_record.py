#!/usr/bin/env python3
"""Validate the immutable Phase 32 post-merge record and state transition."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
POST=ROOT/"release/phase-32-postmerge.json"
CANDIDATE=ROOT/"release/phase-32-offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance.json"
REPORT=ROOT/"reports/phase-32-offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance.md"
STATE=ROOT/"PROJECT_STATE.md"
WORKFLOW=ROOT/".github/workflows/validate-phase-32-offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance.yml"
CANDIDATE_SHA="b7c178bd026b453dff59f7caff588922206239313155daa59f4fd72c5306f92d"
POST_SHA="910416e3b212039b71d130d07db68872a1d8850dba4b73b173b5fe76e62cf5a5"
EXPECTED={'authority': {'atlas_call_permitted': False, 'automatic_release_action': False, 'automatic_status_change': False, 'external_delivery_permitted': False, 'external_network_required': False, 'human_authorization_claimed': False, 'local_response_envelope_validation_readiness_assurance_permitted': True, 'repository_mutation': False, 'response_envelope_creation_permitted': False, 'response_envelope_processing_authorized': False, 'response_envelope_validation_execution_authorized': False, 'response_envelope_validation_result_recording_permitted': False, 'response_intake_authorized': False, 'response_quarantine_execution_authorized': False, 'response_receipt_permitted': False, 'response_validation_authorized': False, 'review_execution_authorized': False, 'review_request_dispatch_authorized': False, 'reviewer_contact_permitted': False, 'status_inheritance': 'prohibited'}, 'candidate_record': {'path': 'release/phase-32-offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance.json', 'sha256': 'b7c178bd026b453dff59f7caff588922206239313155daa59f4fd72c5306f92d'}, 'contract': 'principia-offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance-finalization/0.1', 'decision': 'response-intake-envelope-validation-readiness-assured-no-envelope-received', 'fixture_kind': 'bounded-synthetic', 'id': 'principia-atlas-offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance-thermal-control-finalization', 'live': False, 'live_activation_permitted': False, 'mode': 'offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance', 'next_gate': 'offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-candidate', 'phase': 32, 'principia': {'candidate_head_commit': '9936f996205ed4637c80bcf8ec2c83203f807f10', 'merge_commit': '645bb4567df6328aa47788b63206192fad2eeef4', 'pull_request': 55, 'repository': 'Rhodan-lab/principle-to-system'}, 'real_authorization_claimed': False, 'result': {'assurance_check_count': 66, 'assured_validation_readiness_record_count': 2, 'blank_validation_receipt_count': 2, 'blank_validation_receipt_field_count': 20, 'disposition_selected_count': 0, 'failed_assurance_count': 0, 'failed_control_count': 0, 'human_gate_pending_count': 8, 'human_gate_satisfied_count': 0, 'possible_disposition_count': 6, 'real_authorization_claimed': False, 'response_accepted_count': 0, 'response_envelope_created_count': 0, 'response_envelope_processed_count': 0, 'response_envelope_received_count': 0, 'response_intake_authorized_count': 0, 'response_quarantined_count': 0, 'response_received_count': 0, 'response_rejected_count': 0, 'response_validated_count': 0, 'review_completed_count': 0, 'review_started_count': 0, 'reviewer_contact_count': 0, 'reviewer_identity_count': 0, 'status_change_count': 0, 'validation_completed_count': 0, 'validation_control_count': 36, 'validation_execution_authorized_count': 0, 'validation_profile_count': 2, 'validation_readiness_record_count': 2, 'validation_result_recorded_count': 0, 'validation_run_count': 0, 'validation_stage_count': 16, 'validation_started_count': 0}, 'state': 'offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance-validated', 'validation': {'applicable_workflows': 26, 'candidate_head_commit': '9936f996205ed4637c80bcf8ec2c83203f807f10', 'status': 'success'}}

def sha_file(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main()->int:
    errors=[]
    if not CANDIDATE.is_file() or sha_file(CANDIDATE)!=CANDIDATE_SHA:
        errors.append("Phase 32 candidate digest drift")
    if not POST.is_file():
        errors.append("Phase 32 post-merge record missing")
    else:
        try: doc=json.loads(POST.read_text())
        except Exception as exc: errors.append(f"Phase 32 post-merge JSON invalid: {exc}")
        else:
            if doc!=EXPECTED: errors.append("Phase 32 post-merge record drift")
            canonical=json.dumps(EXPECTED,indent=2,sort_keys=True)+"\n"
            if POST.read_text()!=canonical: errors.append("Phase 32 post-merge bytes are not canonical")
            if sha_file(POST)!=POST_SHA: errors.append("Phase 32 post-merge digest drift")
    report=REPORT.read_text() if REPORT.is_file() else ""
    for marker in (
        "candidate_pull_request: 55",
        "candidate_tested_head: 9936f996205ed4637c80bcf8ec2c83203f807f10",
        "candidate_merge_commit: 645bb4567df6328aa47788b63206192fad2eeef4",
        f"postmerge_sha256: {POST_SHA}",
        "final_state: offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance-validated",
        "No envelope was created or received",
    ):
        if marker not in report: errors.append(f"Phase 32 report marker missing: {marker}")
    state=STATE.read_text() if STATE.is_file() else ""
    for marker in (
        "**Phase 32 — Offline Consequence-Plan Review-Response Intake Envelope Validation Readiness Assurance merged and validated through PR #55.**",
        "Phase 32 state: **offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance-validated**",
        "| 32 | Offline consequence-plan review-response intake envelope validation readiness assurance | Merged and validated through PR #55 |",
        "Historical Phase 31 finalization marker",
        "Historical Phase 32 candidate marker: `exact-head validation pending`",
        "Atlas remains unchanged by Principia Phase 32.",
        "release/phase-32-postmerge.json",
        "python3 scripts/validate_phase32_postmerge_record.py",
        "Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-candidate**.",
    ):
        if marker not in state: errors.append(f"PROJECT_STATE marker missing: {marker}")
    workflow=WORKFLOW.read_text() if WORKFLOW.is_file() else ""
    if "validate_phase32_postmerge_record.py" not in workflow:
        errors.append("Phase 32 workflow does not include post-merge validation")
    if "contents: read" not in workflow:
        errors.append("Phase 32 workflow is not read-only")
    for forbidden in ("contents: write","git push","git commit","pull_request_target","repository: Rhodan-lab/Atlas","curl ","wget "):
        if forbidden in workflow: errors.append(f"Phase 32 workflow forbidden token: {forbidden}")
    if errors:
        print("Phase 32 post-merge record errors:",file=sys.stderr)
        for error in errors: print(f"- {error}",file=sys.stderr)
        return 1
    print("Phase 32 post-merge validation passed: immutable provenance, state transition, and frozen authority.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
