#!/usr/bin/env python3
"""Apply the lossless Phase 36 project-state transition."""
from pathlib import Path
import sys

PATH=Path("PROJECT_STATE.md")
text=PATH.read_text()
replacements=[
(
"**Phase 35 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Readiness merged and validated through PR #61.**",
"**Phase 36 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Readiness Assurance merged and validated through PR #63.**"
),
(
"Phase 35 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness`, `live: false`).",
"Phase 35 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness`, `live: false`).\nPhase 36 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance`, `live: false`)."
),
(
"| 35 | Offline consequence-plan review-response intake envelope validation execution authorization readiness | Merged and validated through PR #61 |",
"| 35 | Offline consequence-plan review-response intake envelope validation execution authorization readiness | Merged and validated through PR #61 |\n| 36 | Offline consequence-plan review-response intake envelope validation execution authorization readiness assurance | Merged and validated through PR #63 |"
),
(
"## Validation\n\n```bash\n",
'## Phase 36 result — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Readiness Assurance\n\nHistorical Phase 35 finalization marker: **Phase 35 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Readiness merged and validated through PR #61.**\n\nHistorical Phase 36 candidate marker: `exact-head validation pending`\n\nHistorical Phase 36 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-candidate`\n\nPhase 36 exact candidate validation passed at `b9443786203f1fce54bef7a4461d659413998fc7`. PR #63 was merged into `main` at commit `2c0f3bc5d01e8f36782108a14a8611e38c4d5ca6` after all 30 applicable workflows passed.\n\nAtlas remains unchanged by Principia Phase 36. Principia and Atlas retain separate lifecycle authority.\n\n```yaml\ncandidate_sha256: c90abcedeffcc66ff1d1e1d615e03cc5e002a76177d3ab8a0754543c4ad1677e\ncandidate_tested_head: b9443786203f1fce54bef7a4461d659413998fc7\ncandidate_pull_request: 63\ncandidate_merge_commit: 2c0f3bc5d01e8f36782108a14a8611e38c4d5ca6\napplicable_candidate_workflows: 30\nauthorization_policy_count: 1\nauthorization_profile_count: 2\nauthorization_readiness_record_count: 2\nassured_authorization_readiness_record_count: 2\nassurance_check_count: 100\nfailed_assurance_count: 0\nauthorization_stage_count: 20\nauthorization_requirement_count: 44\nauthorization_requirement_evaluated_count: 0\nrequired_approval_role_count: 4\ndual_control_profile_count: 2\napproval_received_count: 0\napproval_evidence_recorded_count: 0\nblank_authorization_token_count: 2\nblank_authorization_token_field_count: 28\nhuman_gate_pending_count: 8\nhuman_gate_satisfied_count: 0\nauthorization_candidate_created_count: 0\nauthorization_decision_recorded_count: 0\nauthorization_granted_count: 0\nauthorization_revoked_count: 0\nauthorization_expired_count: 0\nauthorization_token_issued_count: 0\nexecution_authorization_present_count: 0\nexecution_ticket_issued_count: 0\nexecution_run_count: 0\nvalidation_result_recorded_count: 0\nresponse_envelope_received_count: 0\nresponse_received_count: 0\nreviewer_contact_count: 0\nreview_started_count: 0\nstatus_change_count: 0\nreal_authorization_claimed: false\ndecision: response-intake-envelope-validation-execution-authorization-readiness-assured-no-authorization-granted\nlive: false\n```\n\nThe recovery matrix contains 132 deterministic scenarios and rejects 131 mutations involving Phase 35 source provenance, readiness-record and ledger bindings, shared policy, profile and role drift, stage and requirement drift, token population, authorization decision or grant activity, execution activity, envelope and response activity, reviewer contact, status effects, networking, Atlas access, repository mutation, and live activation.\n\n`release/phase-36-postmerge.json` separately pins candidate SHA-256 `c90abcedeffcc66ff1d1e1d615e03cc5e002a76177d3ab8a0754543c4ad1677e`, exact tested head `b9443786203f1fce54bef7a4461d659413998fc7`, PR #63, merge commit `2c0f3bc5d01e8f36782108a14a8611e38c4d5ca6`, all 30 applicable workflows, 100 passing assurance checks, frozen zero-grant authority, `real_authorization_claimed: false`, and final state `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-validated`.\n\n## Validation\n\n```bash\n'
),
(
"```bash\npython3 scripts/generate_phase35_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_readiness.py --check",
"```bash\npython3 scripts/generate_phase36_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_readiness_assurance.py --check\npython3 scripts/validate_phase36_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_readiness_assurance.py\npython3 scripts/validate_phase36_postmerge_record.py\npython3 -m unittest software.tests.test_phase36_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_readiness_assurance -v\npython3 scripts/generate_phase35_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_readiness.py --check"
),
(
"Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-candidate**.",
"Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-candidate**."
),
(
"The next bounded gate may independently assure the two authorization-readiness records, shared policy, dual-control role requirements, inactive stages, unevaluated requirements, blank tokens, expiration and revocation boundaries, exact Phase 34 bindings, chained evidence, and zero-grant authority. It must not grant authorization, create or issue a token, receive an envelope, issue an execution ticket, evaluate a requirement, execute validation, record a result, select a disposition, dispatch a request, identify or contact a reviewer, satisfy a human gate, claim real authorization, start or complete review, select an outcome, activate a hold, mutate content or status, call Atlas, require external networking, or write to either repository automatically.",
"The next bounded gate may define deterministic prerequisites for considering an authorization decision over the two assured authorization-readiness records. It must not create an authorization candidate, record a decision, grant authorization, issue or populate a token, receive an envelope, issue an execution ticket, evaluate a requirement, execute validation, record a result, select a disposition, dispatch a request, identify or contact a reviewer, satisfy a human gate, claim real authorization, start or complete review, select an outcome, activate a hold, mutate content or status, call Atlas, require external networking, or write to either repository automatically."
)
]
for old,new in replacements:
    if old not in text:
        print(f"Missing state marker: {old[:120]}",file=sys.stderr)
        raise SystemExit(1)
    text=text.replace(old,new,1)
required=[
"**Phase 36 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Readiness Assurance merged and validated through PR #63.**",
"Phase 36 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-validated**",
"| 36 | Offline consequence-plan review-response intake envelope validation execution authorization readiness assurance | Merged and validated through PR #63 |",
"Historical Phase 36 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-candidate`",
"Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-candidate**",
"Principia and Atlas remain separate repositories with separate lifecycle authority."
]
for marker in required:
    if marker not in text:
        print(f"Final state marker absent: {marker}",file=sys.stderr)
        raise SystemExit(1)
PATH.write_text(text)
print(f"Phase 36 project state written: {len(text.splitlines())} lines.")
