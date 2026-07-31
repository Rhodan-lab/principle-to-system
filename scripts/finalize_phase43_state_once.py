#!/usr/bin/env python3
"""One-shot, marker-checked PROJECT_STATE transition for Phase 43."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "PROJECT_STATE.md"
SELF = ROOT / "scripts/finalize_phase43_state_once.py"
SELF_WORKFLOW = ROOT / ".github/workflows/finalize-phase-43-state-once.yml"

CANDIDATE_SHA = "5ffd6005a907742ac0c02c4077d68d8f1f646963a030405e53daed2219802ef3"
HEAD = "faa7b7f698767722bc58cd8785e04f1ac278f927"
MERGE = "0c1938169137ef9b5eead27f39e2b7c07f614f5b"
POST_SHA = "bbec0856c15c3286e9698d1a738cd9a7e77b13fc110b8aa0571cd4f9632d8488"
PREVIOUS_GATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-candidate"
NEXT_GATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-assurance-candidate"
FINAL_STATE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-validated"
MODE = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one marker, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    text = STATE.read_text(encoding="utf-8")
    text = replace_once(text, "> Last updated: 2026-07-30", "> Last updated: 2026-07-31", "date")
    text = replace_once(
        text,
        "**Phase 42 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Preparation Readiness Assurance merged and validated through PR #75.**",
        "**Phase 43 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Assembly Readiness merged and validated through PR #78.**",
        "current phase",
    )

    phase42_state = "Phase 42 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance`, `live: false`)."
    phase43_state = f"Phase 43 state: **{FINAL_STATE}** (`mode: {MODE}`, `live: false`)."
    text = replace_once(text, phase42_state, phase42_state + "\n" + phase43_state, "phase state")

    phase42_row = "| 42 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate preparation readiness assurance | Merged and validated through PR #75 |"
    phase43_row = "| 43 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate assembly readiness | Merged and validated through PR #78 |"
    text = replace_once(text, phase42_row, phase42_row + "\n" + phase43_row, "phase row")

    block = f'''## Phase 43 result — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Assembly Readiness

Historical Phase 42 finalization marker: **Phase 42 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Preparation Readiness Assurance merged and validated through PR #75.**

Historical Phase 43 candidate marker: `exact-head validation pending`

Historical Phase 43 target marker: `{PREVIOUS_GATE}`

Historical Phase 42 next-gate marker: Next gate: **{PREVIOUS_GATE}**.

Phase 43 exact candidate validation passed at `{HEAD}`. PR #78 was merged into `main` at commit `{MERGE}` after all 37 applicable workflows passed.

Atlas remains unchanged by Principia Phase 43. Principia and Atlas retain separate lifecycle authority.

```yaml
candidate_sha256: {CANDIDATE_SHA}
candidate_tested_head: {HEAD}
candidate_pull_request: 78
candidate_merge_commit: {MERGE}
applicable_candidate_workflows: 37
assembly_readiness_policy_count: 1
assembly_readiness_profile_count: 2
assembly_readiness_record_count: 2
assembly_check_count: 128
failed_assembly_check_count: 0
assembly_slot_count: 36
populated_slot_count: 0
assembly_stage_count: 32
active_stage_count: 0
assembly_requirement_count: 64
evaluated_requirement_count: 0
human_gate_pending_count: 8
human_gate_satisfied_count: 0
audit_event_count: 0
authorization_decision_candidate_count: 0
decision_record_count: 0
authorization_grant_count: 0
authorization_token_count: 0
execution_ticket_count: 0
execution_run_count: 0
response_envelope_count: 0
reviewer_identity_count: 0
reviewer_contact_count: 0
validation_result_count: 0
status_change_count: 0
real_authorization_claimed: false
decision: response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-defined-no-candidate-assembled
live: false
```

The recovery matrix contains 150 deterministic scenarios and rejects 149 mutations. No candidate creation, population, assembly, persistence, signing, submission, decision, grant, token, ticket, envelope, execution, reviewer identity, reviewer contact, human-gate satisfaction, Atlas call, repository effect, or live activation occurred.

`release/phase-43-postmerge.json` pins candidate SHA-256 `{CANDIDATE_SHA}`, post-merge SHA-256 `{POST_SHA}`, exact tested head `{HEAD}`, PR #78, merge commit `{MERGE}`, all 37 applicable workflows, 128 passing assembly checks, frozen zero-candidate authority, and final state `{FINAL_STATE}`.

'''
    text = replace_once(text, "## Validation\n", block + "## Validation\n", "result block")

    prefix = '''```bash
python3 scripts/generate_phase43_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_assembly_readiness.py --check
python3 scripts/validate_phase43_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_assembly_readiness.py
python3 scripts/validate_phase43_postmerge_record.py
python3 -m unittest software.tests.test_phase43_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_assembly_readiness -v
'''
    text = replace_once(text, "```bash\npython3 scripts/generate_phase42_", prefix + "python3 scripts/generate_phase42_", "validation chain")

    old_tail = f'''Next gate: **{PREVIOUS_GATE}**.

The next bounded gate may define deterministic assembly requirements for a still-uncreated authorization-decision candidate. It must not create, populate, assemble, persist, sign, or submit a candidate; record or select a decision; grant authorization; issue a token or execution ticket; receive or process an envelope; execute validation; record a result; identify or contact a reviewer; satisfy a human gate; mutate content or status; call Atlas; require external networking; or write to either repository automatically.'''
    new_tail = f'''Next gate: **{NEXT_GATE}**.

The next bounded gate may independently assure the deterministic Phase 43 assembly-readiness policy, profiles, symbolic slot plans, inactive stages, unevaluated requirements, exact Phase 42 bindings, chained evidence, and zero-candidate authority. It must not create, populate, assemble, persist, sign, or submit a candidate; record or select a decision; grant authorization; issue a token or execution ticket; receive or process an envelope; execute validation; record a result; identify or contact a reviewer; satisfy a human gate; mutate content or status; call Atlas; require external networking; or write to either repository automatically.'''
    text = replace_once(text, old_tail, new_tail, "next phase")

    STATE.write_text(text, encoding="utf-8")
    SELF.unlink()
    SELF_WORKFLOW.unlink()
    print("Phase 43 PROJECT_STATE transition materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
