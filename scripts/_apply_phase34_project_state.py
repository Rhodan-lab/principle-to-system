#!/usr/bin/env python3
"""One-shot exact Phase 34 PROJECT_STATE transition; removed by its workflow."""
from __future__ import annotations
import hashlib
from pathlib import Path

PATH=Path("PROJECT_STATE.md")
SOURCE_SHA="3b142f16cb76ce74f55b2ccfacc16f7a39499ce62d44b6545aa5a7e7b2d00b27"
TARGET_SHA="d3137bcaf84cb9f657e4f4c2c12e323d8434aa4a8d530a8f8a30e7ba6138339d"

def replace_once(text:str, old:str, new:str)->str:
    if text.count(old)!=1:
        raise SystemExit(f"Expected one marker, found {text.count(old)}: {old[:100]}")
    return text.replace(old,new,1)

raw=PATH.read_bytes()
if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:
    raise SystemExit("Unexpected pre-Phase-34 PROJECT_STATE digest")
text=raw.decode()

text=replace_once(text,
"**Phase 33 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Readiness merged and validated through PR #57.**",
"**Phase 34 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Readiness Assurance merged and validated through PR #59.**")

text=replace_once(text,
"Phase 33 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness`, `live: false`).",
"Phase 33 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness`, `live: false`).\nPhase 34 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance`, `live: false`).")

text=replace_once(text,
"| 33 | Offline consequence-plan review-response intake envelope validation execution readiness | Merged and validated through PR #57 |",
"| 33 | Offline consequence-plan review-response intake envelope validation execution readiness | Merged and validated through PR #57 |\n| 34 | Offline consequence-plan review-response intake envelope validation execution readiness assurance | Merged and validated through PR #59 |")

text=replace_once(text,
"- PR #57 was merged into `main` at commit `d05db33982e0001c9ebc636043dc0cc64592c42d`.",
"- PR #57 was merged into `main` at commit `d05db33982e0001c9ebc636043dc0cc64592c42d`.\n- Phase 34 exact candidate validation passed at `99be153a563c0c7dd3c395b90969f3fb2546e91b`.\n- PR #59 was merged into `main` at commit `3878ad9d8ccdb49b05f02c6fdcb89a01cd9f7646`.")

old_tail="and the integrated Phase 33 validation-execution readiness blueprint, profiles, stages, preconditions, blank tickets, ledger, checkpoint, recovery matrix, and immutable finalization record."
new_tail=old_tail[:-1]+", and the integrated Phase 34 execution-readiness assurance records, 88 invariant checks, ledger, checkpoint, recovery matrix, and immutable finalization record."
text=replace_once(text,old_tail,new_tail)

text=replace_once(text,
"- Historical Phase 33 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-candidate`.",
"- Historical Phase 33 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-candidate`.\n- Historical Phase 33 finalization marker: **Phase 33 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Readiness merged and validated through PR #57.**\n- Historical Phase 34 candidate marker: `exact-head validation pending`.\n- Historical Phase 34 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance-candidate`.")

text=replace_once(text,
"- Atlas remains unchanged by Principia Phase 33.",
"- Atlas remains unchanged by Principia Phase 33.\n- Atlas remains unchanged by Principia Phase 34.")

phase34_section='''## Phase 34 result — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Readiness Assurance

Phase 34 independently assured both finalized Phase 33 execution-readiness records and the shared execution blueprint without creating or receiving any envelope and without activating validation execution.

```yaml
candidate_sha256: 2ca9b454124b1fb42f91f09479d9aed1d0c54f9ef443f121caa3a7ee67823828
candidate_tested_head: 99be153a563c0c7dd3c395b90969f3fb2546e91b
candidate_pull_request: 59
candidate_merge_commit: 3878ad9d8ccdb49b05f02c6fdcb89a01cd9f7646
applicable_candidate_workflows: 28
assured_execution_readiness_record_count: 2
assurance_check_count: 88
failed_assurance_count: 0
blueprint_count: 1
execution_profile_count: 2
execution_stage_count: 18
execution_precondition_count: 40
validation_control_count: 36
possible_disposition_count: 6
blank_execution_ticket_count: 2
blank_execution_ticket_field_count: 24
human_gate_pending_count: 8
human_gate_satisfied_count: 0
execution_authorization_present_count: 0
execution_ticket_issued_count: 0
execution_run_count: 0
validation_result_recorded_count: 0
disposition_selected_count: 0
response_envelope_received_count: 0
response_received_count: 0
reviewer_contact_count: 0
review_started_count: 0
status_change_count: 0
real_authorization_claimed: false
decision: response-intake-envelope-validation-execution-readiness-assured-no-envelope-received
live: false
```

The recovery matrix contains 121 deterministic scenarios and rejects 120 mutations involving source provenance, readiness records and ledger bindings, blueprint, engine, stage, precondition, control, disposition, resource-limit and blank-ticket drift; authorization or runtime activity; result or disposition recording; envelope or response activity; reviewer contact; review execution; operational effects; networking; Atlas access; repository mutation; and live activation.

`release/phase-34-postmerge.json` separately pins candidate SHA-256 `2ca9b454124b1fb42f91f09479d9aed1d0c54f9ef443f121caa3a7ee67823828`, exact tested head `99be153a563c0c7dd3c395b90969f3fb2546e91b`, PR #59, merge commit `3878ad9d8ccdb49b05f02c6fdcb89a01cd9f7646`, all 28 applicable workflows, frozen zero-execution authority, `real_authorization_claimed: false`, and final state `offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance-validated`.

'''
text=replace_once(text,"## Validation\n",phase34_section+"## Validation\n")

phase34_commands='''python3 scripts/generate_phase34_offline_consequence_plan_review_response_intake_envelope_validation_execution_readiness_assurance.py --check
python3 scripts/validate_phase34_offline_consequence_plan_review_response_intake_envelope_validation_execution_readiness_assurance.py
python3 scripts/validate_phase34_postmerge_record.py
python3 -m unittest software.tests.test_phase34_offline_consequence_plan_review_response_intake_envelope_validation_execution_readiness_assurance -v
'''
text=replace_once(text,"## Validation\n\n```bash\n","## Validation\n\n```bash\n"+phase34_commands)

text=replace_once(text,
"Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance-candidate**.",
"Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-candidate**.")

text=replace_once(text,
"The next bounded gate may independently assure the two execution-readiness profiles, the shared blueprint, inactive stages, unevaluated preconditions, canonical control order, deterministic engine pin, resource limits, blank tickets, exact Phase 32 bindings, chained evidence, and zero-execution authority. It must not create or receive an envelope, issue a ticket, evaluate a precondition, execute validation, record a result, select a disposition, dispatch a request, identify or contact a reviewer, satisfy a human gate, claim authorization, start or complete review, select an outcome, activate a hold, mutate content or status, call Atlas, require external networking, or write to either repository automatically.",
"The next bounded gate may define deterministic local validation-execution authorization-readiness requirements over the two assured execution profiles. It must not grant authorization, create or receive an envelope, issue a ticket, evaluate a precondition, execute validation, record a result, select a disposition, dispatch a request, identify or contact a reviewer, satisfy a human gate, claim real authorization, start or complete review, select an outcome, activate a hold, mutate content or status, call Atlas, require external networking, or write to either repository automatically.")

out=text.encode()
actual=hashlib.sha256(out).hexdigest()
if actual!=TARGET_SHA:
    raise SystemExit(f"Phase 34 PROJECT_STATE digest mismatch: {actual}")
PATH.write_bytes(out)
print(f"Phase 34 PROJECT_STATE updated: sha256={actual}, bytes={len(out)}")
