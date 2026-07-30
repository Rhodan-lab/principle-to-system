#!/usr/bin/env python3
"""Apply the lossless Phase 41 to Phase 42 authoritative state transition."""
from pathlib import Path

state_path = Path("PROJECT_STATE.md")
state = state_path.read_text(encoding="utf-8")
old_heading = "**Phase 41 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Preparation Readiness merged and validated through PR #73.**"
new_heading = "**Phase 42 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Preparation Readiness Assurance merged and validated through PR #75.**"
assert old_heading in state and new_heading not in state
state = state.replace(old_heading, new_heading, 1)

p41 = "Phase 41 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness`, `live: false`)."
p42 = "Phase 42 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance`, `live: false`)."
assert p41 in state and p42 not in state
state = state.replace(p41, p41 + "\n" + p42, 1)

row41 = "| 41 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate preparation readiness | Merged and validated through PR #73 |"
row42 = "| 42 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate preparation readiness assurance | Merged and validated through PR #75 |"
assert row41 in state and row42 not in state
state = state.replace(row41, row41 + "\n" + row42, 1)

section = """## Phase 42 result — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Preparation Readiness Assurance

Historical Phase 41 finalization marker: **Phase 41 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Preparation Readiness merged and validated through PR #73.**

Historical Phase 42 candidate marker: `exact-head validation pending`

Historical Phase 42 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-candidate`

Historical Phase 41 next-gate marker: Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-candidate**.

Phase 42 exact candidate validation passed at `0597916365d489b2738fbb905f0f40991f42a4b7`. PR #75 was merged into `main` at commit `057da54503e2c3b1ea1e86150c4015a99628dfed` after all 36 applicable workflows passed.

Atlas remains unchanged by Principia Phase 42. Principia and Atlas retain separate lifecycle authority.

```yaml
candidate_sha256: 6fb602bc5ef863765ceb50ba66124b843381fd15c6dac9da9250429e18e76f26
candidate_tested_head: 0597916365d489b2738fbb905f0f40991f42a4b7
candidate_pull_request: 75
candidate_merge_commit: 057da54503e2c3b1ea1e86150c4015a99628dfed
applicable_candidate_workflows: 36
candidate_preparation_readiness_assurance_policy_count: 1
candidate_preparation_readiness_assurance_record_count: 2
candidate_preparation_readiness_assurance_check_count: 204
failed_candidate_preparation_readiness_assurance_check_count: 0
candidate_preparation_policy_count: 1
candidate_preparation_profile_count: 2
candidate_preparation_readiness_record_count: 2
candidate_preparation_stage_count: 28
candidate_preparation_requirement_count: 88
candidate_preparation_requirement_evaluated_count: 0
candidate_field_plan_count: 36
candidate_field_populated_count: 0
audit_event_recorded_count: 0
human_gate_pending_count: 8
human_gate_satisfied_count: 0
authorization_decision_candidate_created_count: 0
authorization_decision_recorded_count: 0
authorization_granted_count: 0
authorization_token_issued_count: 0
execution_ticket_issued_count: 0
execution_run_count: 0
response_envelope_received_count: 0
reviewer_contact_count: 0
status_change_count: 0
real_authorization_claimed: false
decision: response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assured-no-candidate-created
live: false
```

The recovery matrix contains 226 deterministic scenarios and rejects 225 mutations. No candidate creation, population, assembly, persistence, signing, submission, decision, grant, token, ticket, envelope, execution, reviewer contact, Atlas call, repository effect, or live activation occurred.

`release/phase-42-postmerge.json` pins candidate SHA-256 `6fb602bc5ef863765ceb50ba66124b843381fd15c6dac9da9250429e18e76f26`, exact tested head `0597916365d489b2738fbb905f0f40991f42a4b7`, PR #75, merge commit `057da54503e2c3b1ea1e86150c4015a99628dfed`, all 36 applicable workflows, 204 passing assurance checks, frozen zero-candidate authority, and final state `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-validated`.

"""
assert "## Phase 42 result —" not in state
state = state.replace("## Validation\n", section + "## Validation\n", 1)

commands = "python3 scripts/generate_phase42_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_preparation_readiness_assurance.py --check\npython3 scripts/validate_phase42_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_preparation_readiness_assurance.py\npython3 scripts/validate_phase42_postmerge_record.py\npython3 -m unittest software.tests.test_phase42_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_preparation_readiness_assurance -v\n"
anchor = "python3 scripts/generate_phase41_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_preparation_readiness.py --check\n"
assert anchor in state and commands not in state
state = state.replace(anchor, commands + anchor, 1)

old_next = "Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-candidate**."
new_next = "Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-candidate**."
assert old_next in state
state = state.replace(old_next, new_next, 1)

old_desc = "The next bounded gate may independently assure the Phase 41 preparation policy, profiles, field-source plans, exact Phase 40 bindings, chained evidence, and zero-candidate authority. It must not create or populate a candidate, record or select a decision, grant authorization, issue a token or execution ticket, receive or process an envelope, execute validation, record a result, identify or contact a reviewer, satisfy a human gate, mutate content or status, call Atlas, require external networking, or write to either repository automatically."
new_desc = "The next bounded gate may define deterministic assembly requirements for a still-uncreated authorization-decision candidate. It must not create, populate, assemble, persist, sign, or submit a candidate; record or select a decision; grant authorization; issue a token or execution ticket; receive or process an envelope; execute validation; record a result; identify or contact a reviewer; satisfy a human gate; mutate content or status; call Atlas; require external networking; or write to either repository automatically."
assert old_desc in state
state = state.replace(old_desc, new_desc, 1)
state_path.write_text(state, encoding="utf-8")

validator = Path("scripts/validate_phase41_postmerge_record.py")
text = validator.read_text(encoding="utf-8")
old = '        f"Next gate: **{NEXT}**",'
new = '        "Historical Phase 42 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-candidate`",'
assert old in text
validator.write_text(text.replace(old, new, 1), encoding="utf-8")
