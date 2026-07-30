#!/usr/bin/env python3
"""Apply the lossless Phase 37 -> Phase 38 PROJECT_STATE transition."""
from __future__ import annotations

from pathlib import Path

STATE = Path("PROJECT_STATE.md")
OLD_CURRENT = "**Phase 37 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Readiness merged and validated through PR #65.**"
NEW_CURRENT = "**Phase 38 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Readiness Assurance merged and validated through PR #67.**"
PHASE37_STATE = "Phase 37 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness`, `live: false`)."
PHASE38_STATE = "Phase 38 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance`, `live: false`)."
ROW37 = "| 37 | Offline consequence-plan review-response intake envelope validation execution authorization decision readiness | Merged and validated through PR #65 |"
ROW38 = "| 38 | Offline consequence-plan review-response intake envelope validation execution authorization decision readiness assurance | Merged and validated through PR #67 |"
VALIDATION_MARKER = "## Validation\n\n```bash\n"
PHASE38_COMMANDS = """python3 scripts/generate_phase38_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_readiness_assurance.py --check
python3 scripts/validate_phase38_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_readiness_assurance.py
python3 scripts/validate_phase38_postmerge_record.py
python3 -m unittest software.tests.test_phase38_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_readiness_assurance -v
"""
PHASE38_RESULT = """## Phase 38 result — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Readiness Assurance

Historical Phase 37 finalization marker: **Phase 37 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Readiness merged and validated through PR #65.**

Historical Phase 38 candidate marker: `exact-head validation pending`

Historical Phase 38 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-candidate`

Phase 38 exact candidate validation passed at `08b75c7d280f3482b746a5de9c5c6d48541e3cf6`. PR #67 was merged into `main` at commit `be3f305f7234875be541e6f5e2bb8fb1bf0c0f43` after all 32 applicable workflows passed.

Atlas remains unchanged by Principia Phase 38. Principia and Atlas retain separate lifecycle authority.

```yaml
candidate_sha256: b3c5d8ea8da88cd2975531ccd149b0dde980dc480b9e7385425cafad3e024ec8
candidate_tested_head: 08b75c7d280f3482b746a5de9c5c6d48541e3cf6
candidate_pull_request: 67
candidate_merge_commit: be3f305f7234875be541e6f5e2bb8fb1bf0c0f43
applicable_candidate_workflows: 32
decision_policy_count: 1
decision_profile_count: 2
decision_readiness_record_count: 2
assured_decision_readiness_record_count: 2
assurance_check_count: 144
failed_assurance_check_count: 0
decision_stage_count: 24
decision_requirement_count: 52
decision_requirement_evaluated_count: 0
decision_option_count: 3
decision_option_selected_count: 0
blank_decision_record_count: 2
blank_decision_record_field_count: 32
required_decision_role_count: 4
dual_control_profile_count: 2
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
decision: response-intake-envelope-validation-execution-authorization-decision-readiness-assured-no-decision-candidate-created
live: false
```

The recovery matrix contains 206 deterministic scenarios and rejects 205 mutations. No decision candidate, decision, grant, token, ticket, envelope, execution, reviewer contact, Atlas call, repository effect, or live activation occurred.

`release/phase-38-postmerge.json` pins candidate SHA-256 `b3c5d8ea8da88cd2975531ccd149b0dde980dc480b9e7385425cafad3e024ec8`, exact tested head `08b75c7d280f3482b746a5de9c5c6d48541e3cf6`, PR #67, merge commit `be3f305f7234875be541e6f5e2bb8fb1bf0c0f43`, all 32 applicable workflows, 144 passing assurance checks, frozen zero-decision authority, and final state `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-validated`.

"""
NEXT_PHASE = """## Next phase

Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-candidate**.

The next bounded gate may define the exact source, role, conflict, approval-evidence, expiry, revocation, audit, and zero-effect boundaries that would have to exist before an authorization-decision candidate could be prepared. It must not create or populate a candidate, record or select a decision, grant authorization, issue a token or execution ticket, receive or process an envelope, evaluate a decision requirement, execute validation, record a result, select a disposition, identify or contact a reviewer, satisfy a human gate, mutate content or status, call Atlas, require external networking, or write to either repository automatically.
"""


def require_once(text: str, marker: str, label: str) -> None:
    count = text.count(marker)
    if count != 1:
        raise SystemExit(f"{label} marker count must be 1, got {count}")


def main() -> int:
    text = STATE.read_text(encoding="utf-8")
    require_once(text, OLD_CURRENT, "current phase")
    require_once(text, PHASE37_STATE, "Phase 37 state")
    require_once(text, ROW37, "Phase 37 table row")
    require_once(text, VALIDATION_MARKER, "validation")
    require_once(text, "## Next phase\n", "next phase")
    if "## Phase 38 result —" in text or PHASE38_STATE in text or ROW38 in text:
        raise SystemExit("Phase 38 state already present")

    text = text.replace(OLD_CURRENT, NEW_CURRENT, 1)
    text = text.replace(PHASE37_STATE, PHASE37_STATE + "\n" + PHASE38_STATE, 1)
    text = text.replace(ROW37, ROW37 + "\n" + ROW38, 1)
    text = text.replace(VALIDATION_MARKER, PHASE38_RESULT + VALIDATION_MARKER + PHASE38_COMMANDS, 1)
    prefix, _ = text.split("## Next phase\n", 1)
    text = prefix + NEXT_PHASE

    required = (
        NEW_CURRENT,
        PHASE38_STATE,
        ROW38,
        "Historical Phase 38 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-candidate`",
        "Phase 38 exact candidate validation passed at `08b75c7d280f3482b746a5de9c5c6d48541e3cf6`",
        "all 32 applicable workflows",
        "206 deterministic scenarios",
        "205 mutations",
        "Principia and Atlas remain separate repositories with separate lifecycle authority.",
        "Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-candidate**",
    )
    for marker in required:
        if marker not in text:
            raise SystemExit(f"required marker missing after transition: {marker}")
    STATE.write_text(text, encoding="utf-8")
    print(f"Applied Phase 38 state transition: lines={len(text.splitlines())}, bytes={len(text.encode('utf-8'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
