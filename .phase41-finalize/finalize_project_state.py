#!/usr/bin/env python3
from pathlib import Path

path = Path("PROJECT_STATE.md")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one occurrence, found {count}: {old[:100]!r}")
    text = text.replace(old, new, 1)


replace_once(
    "**Phase 40 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Boundary Readiness Assurance merged and validated through PR #71.**",
    "**Phase 41 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Preparation Readiness merged and validated through PR #73.**",
)

replace_once(
    "Phase 40 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance`, `live: false`).",
    "Phase 40 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance`, `live: false`).\nPhase 41 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness`, `live: false`).",
)

replace_once(
    "| 40 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate boundary readiness assurance | Merged and validated through PR #71 |",
    "| 40 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate boundary readiness assurance | Merged and validated through PR #71 |\n| 41 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate preparation readiness | Merged and validated through PR #73 |",
)

phase40_tail = """`release/phase-40-postmerge.json` pins candidate SHA-256 `a935dbfcc1758b0aab68fb358968801d2b380690a9ebcd6efdc12416d2ef58c8`, exact tested head `89b5ad5efb559bcf5c5f1b6c61621d97ca32c8e2`, PR #71, merge commit `893c00336ddca21c5b5c36d423f6666c0cfb3531`, all 34 applicable workflows, 168 passing assurance checks, frozen zero-candidate authority, and final state `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance-validated`.

## Validation"""

phase41_section = """`release/phase-40-postmerge.json` pins candidate SHA-256 `a935dbfcc1758b0aab68fb358968801d2b380690a9ebcd6efdc12416d2ef58c8`, exact tested head `89b5ad5efb559bcf5c5f1b6c61621d97ca32c8e2`, PR #71, merge commit `893c00336ddca21c5b5c36d423f6666c0cfb3531`, all 34 applicable workflows, 168 passing assurance checks, frozen zero-candidate authority, and final state `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance-validated`.

## Phase 41 result — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Preparation Readiness

Historical Phase 40 finalization marker: **Phase 40 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Boundary Readiness Assurance merged and validated through PR #71.**

Historical Phase 41 candidate marker: `exact-head validation pending`

Historical Phase 41 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-candidate`

Phase 41 exact candidate validation passed at `4700bd61823d66b2296b9513ad7f564d84bb0e73`. PR #73 was merged into `main` at commit `25073fd7765a9faf3f53235cded3356839861917` after all 35 applicable workflows passed.

Atlas remains unchanged by Principia Phase 41. Principia and Atlas retain separate lifecycle authority.

```yaml
candidate_sha256: c45f148554f66bf21db03fa446475e55746086a47da0bb56841b95012be1d33b
candidate_tested_head: 4700bd61823d66b2296b9513ad7f564d84bb0e73
candidate_pull_request: 73
candidate_merge_commit: 25073fd7765a9faf3f53235cded3356839861917
applicable_candidate_workflows: 35
candidate_preparation_policy_count: 1
candidate_preparation_profile_count: 2
candidate_preparation_readiness_record_count: 2
candidate_preparation_stage_count: 28
candidate_preparation_requirement_count: 88
candidate_preparation_requirement_evaluated_count: 0
candidate_field_plan_count: 36
candidate_field_populated_count: 0
preparation_check_count: 180
failed_preparation_check_count: 0
audit_event_recorded_count: 0
human_gate_pending_count: 8
human_gate_satisfied_count: 0
authorization_decision_candidate_created_count: 0
authorization_decision_recorded_count: 0
authorization_granted_count: 0
authorization_token_issued_count: 0
execution_run_count: 0
response_envelope_received_count: 0
reviewer_contact_count: 0
status_change_count: 0
real_authorization_claimed: false
decision: response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-recorded-no-candidate-created
live: false
```

The recovery matrix contains 198 deterministic scenarios and rejects 197 mutations. No candidate creation or population, decision, grant, token, ticket, envelope, execution, reviewer contact, Atlas call, repository effect, or live activation occurred.

`release/phase-41-postmerge.json` pins candidate SHA-256 `c45f148554f66bf21db03fa446475e55746086a47da0bb56841b95012be1d33b`, exact tested head `4700bd61823d66b2296b9513ad7f564d84bb0e73`, PR #73, merge commit `25073fd7765a9faf3f53235cded3356839861917`, all 35 applicable workflows, 180 passing preparation checks, frozen zero-candidate authority, and final state `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-validated`.

## Validation"""
replace_once(phase40_tail, phase41_section)

replace_once(
    "```bash\npython3 scripts/generate_phase40_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_boundary_readiness_assurance.py --check",
    "```bash\npython3 scripts/generate_phase41_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_preparation_readiness.py --check\npython3 scripts/validate_phase41_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_preparation_readiness.py\npython3 scripts/validate_phase41_postmerge_record.py\npython3 -m unittest software.tests.test_phase41_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_preparation_readiness -v\npython3 scripts/generate_phase40_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_boundary_readiness_assurance.py --check",
)

replace_once(
    "Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-candidate**.",
    "Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-candidate**.",
)

replace_once(
    "The next bounded gate may define deterministic preparation requirements for a still-uncreated authorization-decision candidate. It must not create or populate a candidate, record or select a decision, grant authorization, issue a token or execution ticket, receive or process an envelope, execute validation, record a result, identify or contact a reviewer, satisfy a human gate, mutate content or status, call Atlas, require external networking, or write to either repository automatically.",
    "The next bounded gate may independently assure the Phase 41 preparation policy, profiles, field-source plans, exact Phase 40 bindings, chained evidence, and zero-candidate authority. It must not create or populate a candidate, record or select a decision, grant authorization, issue a token or execution ticket, receive or process an envelope, execute validation, record a result, identify or contact a reviewer, satisfy a human gate, mutate content or status, call Atlas, require external networking, or write to either repository automatically.",
)

path.write_text(text, encoding="utf-8")
print("Phase 41 project state promoted deterministically.")
