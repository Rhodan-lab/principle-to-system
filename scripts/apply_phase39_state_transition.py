#!/usr/bin/env python3
"""Promote the authoritative project state from finalized Phase 38 to finalized Phase 39."""
from pathlib import Path

STATE = Path(__file__).resolve().parent.parent / "PROJECT_STATE.md"
PHASE38_HEADING = "**Phase 38 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Readiness Assurance merged and validated through PR #67.**"
PHASE39_HEADING = "**Phase 39 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Boundary Readiness merged and validated through PR #69.**"
PHASE38_STATE = "Phase 38 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance`, `live: false`)."
PHASE39_STATE = "Phase 39 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness`, `live: false`)."
ROW38 = "| 38 | Offline consequence-plan review-response intake envelope validation execution authorization decision readiness assurance | Merged and validated through PR #67 |"
ROW39 = "| 39 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate boundary readiness | Merged and validated through PR #69 |"
OLD_GATE = "Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-candidate**."
NEW_GATE = "Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance-candidate**."
OLD_PARAGRAPH = "The next bounded gate may define the exact source, role, conflict, approval-evidence, expiry, revocation, audit, and zero-effect boundaries that would have to exist before an authorization-decision candidate could be prepared. It must not create or populate a candidate, record or select a decision, grant authorization, issue a token or execution ticket, receive or process an envelope, evaluate a decision requirement, execute validation, record a result, select a disposition, identify or contact a reviewer, satisfy a human gate, mutate content or status, call Atlas, require external networking, or write to either repository automatically."
NEW_PARAGRAPH = "The next bounded gate may independently assure the Phase 39 boundary policy, profiles, requirements, templates, exact Phase 38 bindings, chained evidence, and zero-candidate authority. It must not create or populate a candidate, record or select a decision, grant authorization, issue a token or execution ticket, receive or process an envelope, execute validation, record a result, identify or contact a reviewer, satisfy a human gate, mutate content or status, call Atlas, require external networking, or write to either repository automatically."

RESULT_BLOCK = """
## Phase 39 result — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Boundary Readiness

Historical Phase 38 finalization marker: **Phase 38 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Readiness Assurance merged and validated through PR #67.**

Historical Phase 39 candidate marker: `exact-head validation pending`

Historical Phase 39 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-candidate`

Phase 39 exact candidate validation passed at `c9bf3c5a0bdab6f6204d8fa8dd571f8d82b01896`. PR #69 was merged into `main` at commit `e2b81e9ac1ff5385ab054392bb0b33f5c3907b55` after all 33 applicable workflows passed.

Atlas remains unchanged by Principia Phase 39. Principia and Atlas retain separate lifecycle authority.

```yaml
candidate_sha256: e15063165a54ced8bbae95f4dcea9c9ff92c540135d67d3a8b10791dbc771c40
candidate_tested_head: c9bf3c5a0bdab6f6204d8fa8dd571f8d82b01896
candidate_pull_request: 69
candidate_merge_commit: e2b81e9ac1ff5385ab054392bb0b33f5c3907b55
applicable_candidate_workflows: 33
boundary_policy_count: 1
boundary_profile_count: 2
candidate_boundary_readiness_record_count: 2
boundary_stage_count: 24
boundary_requirement_count: 60
boundary_requirement_evaluated_count: 0
candidate_template_count: 2
candidate_template_field_count: 36
boundary_check_count: 154
failed_boundary_check_count: 0
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
decision: response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-recorded-no-candidate-created
live: false
```

The recovery matrix contains 181 deterministic scenarios and rejects 180 mutations. No authorization-decision candidate, decision, grant, token, ticket, envelope, execution, reviewer contact, Atlas call, repository effect, or live activation occurred.

`release/phase-39-postmerge.json` pins candidate SHA-256 `e15063165a54ced8bbae95f4dcea9c9ff92c540135d67d3a8b10791dbc771c40`, exact tested head `c9bf3c5a0bdab6f6204d8fa8dd571f8d82b01896`, PR #69, merge commit `e2b81e9ac1ff5385ab054392bb0b33f5c3907b55`, all 33 applicable workflows, 154 passing boundary checks, frozen zero-candidate authority, and final state `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-validated`.

"""

COMMANDS = """python3 scripts/generate_phase39_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_boundary_readiness.py --check
python3 scripts/validate_phase39_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_boundary_readiness.py
python3 scripts/validate_phase39_postmerge_record.py
python3 -m unittest software.tests.test_phase39_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_boundary_readiness -v
"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one marker, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    text = STATE.read_text(encoding="utf-8")
    if PHASE39_HEADING in text or "## Phase 39 result" in text:
        raise SystemExit("Phase 39 state already present")
    text = replace_once(text, PHASE38_HEADING, PHASE39_HEADING, "current heading")
    text = replace_once(text, PHASE38_STATE, PHASE38_STATE + "\n" + PHASE39_STATE, "phase state")
    text = replace_once(text, ROW38, ROW38 + "\n" + ROW39, "phase table")
    text = replace_once(text, "\n## Validation\n", "\n" + RESULT_BLOCK + "## Validation\n", "result insertion")
    text = replace_once(text, "## Validation\n\n```bash\n", "## Validation\n\n```bash\n" + COMMANDS, "validation commands")
    text = replace_once(text, OLD_GATE, NEW_GATE, "next gate")
    text = replace_once(text, OLD_PARAGRAPH, NEW_PARAGRAPH, "next-phase paragraph")
    required = (
        PHASE39_HEADING, PHASE39_STATE, ROW39,
        "Historical Phase 39 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-candidate`",
        "Atlas remains unchanged by Principia Phase 39",
        "all 33 applicable workflows",
        NEW_GATE,
        "Principia and Atlas remain separate repositories with separate lifecycle authority.",
    )
    for marker in required:
        if marker not in text:
            raise SystemExit(f"missing final marker: {marker}")
    STATE.write_text(text, encoding="utf-8")
    print(f"Applied Phase 39 state transition: bytes={len(text.encode('utf-8'))}, lines={len(text.splitlines())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
