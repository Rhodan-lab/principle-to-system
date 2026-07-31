#!/usr/bin/env python3
"""Publish immutable Phase 46 finalization evidence and advance the bounded gate."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / 'release/phase-46-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance.json'
POST = ROOT / "release/phase-46-postmerge.json"
REPORT = ROOT / 'reports/phase-46-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance.md'
STATE = ROOT / "PROJECT_STATE.md"
WORKFLOW = ROOT / '.github/workflows/validate-phase-46-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance.yml'
POST_VALIDATOR = ROOT / "scripts/validate_phase46_postmerge_record.py"
PUBLISHER = ROOT / "scripts/publish_phase46_finalization.py"
CANDIDATE_SHA = '2b7ced60688ff02ea11231bc53bad3e39e0ec22aa10a233e5f270b0d586039ad'
HEAD = 'e108372f76503ca819afd3e6573e7efaf8e5a295'
MERGE = 'd24fee31b04e7e312106cb020116c9b1e753117c'
MODE = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance'
FINAL_STATE = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance-validated'
NEXT = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness-candidate'
OLD_CURRENT_GATE = 'offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance-candidate'
WORKFLOWS = 39


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label} marker count {count}; expected 1")
    return text.replace(old, new, 1)


if digest(CANDIDATE) != CANDIDATE_SHA:
    raise SystemExit("Phase 46 candidate digest drift before finalization")
candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
if candidate.get("phase") != 46 or candidate.get("state") != OLD_CURRENT_GATE:
    raise SystemExit("Phase 46 candidate state drift")
if candidate.get("next_gate") != NEXT:
    raise SystemExit("Phase 46 next-gate drift")

post = {
    "authority": candidate["authority"],
    "candidate_record": {"path": CANDIDATE.relative_to(ROOT).as_posix(), "sha256": CANDIDATE_SHA},
    "contract": "principia-phase46-population-readiness-assurance-finalization/0.1",
    "decision": candidate["decision"],
    "fixture_kind": candidate["fixture_kind"],
    "id": "principia-atlas-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance-finalization",
    "live": False,
    "live_activation_permitted": False,
    "mode": MODE,
    "next_gate": NEXT,
    "phase": 46,
    "principia": {
        "candidate_head_commit": HEAD,
        "merge_commit": MERGE,
        "pull_request": 84,
        "repository": "Rhodan-lab/principle-to-system",
    },
    "real_authorization_claimed": False,
    "result": candidate["result"],
    "state": FINAL_STATE,
    "validation": {"applicable_workflows": WORKFLOWS, "candidate_head_commit": HEAD, "status": "success"},
}
POST.write_bytes(canonical(post))
POST_SHA = digest(POST)

validator = """#!/usr/bin/env python3
\"\"\"Validate immutable Phase 46 finalization provenance and state markers.\"\"\"
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "__CANDIDATE_PATH__"
POST = ROOT / "release/phase-46-postmerge.json"
REPORT = ROOT / "__REPORT_PATH__"
STATE = ROOT / "PROJECT_STATE.md"
WORKFLOW = ROOT / "__WORKFLOW_PATH__"
CANDIDATE_SHA = "__CANDIDATE_SHA__"
POST_SHA = "__POST_SHA__"
HEAD = "__HEAD__"
MERGE = "__MERGE__"
MODE = "__MODE__"
FINAL_STATE = "__FINAL_STATE__"
NEXT = "__NEXT__"
WORKFLOWS = 39

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def validate():
    errors = []
    for path, name in ((CANDIDATE, "candidate"), (POST, "postmerge"), (REPORT, "report"), (STATE, "state"), (WORKFLOW, "workflow")):
        if not path.is_file():
            errors.append("Phase 46 %s missing" % name)
    if errors:
        return errors
    if sha(CANDIDATE) != CANDIDATE_SHA:
        errors.append("Phase 46 candidate digest drift")
    if sha(POST) != POST_SHA:
        errors.append("Phase 46 postmerge digest drift")
    candidate, post = load(CANDIDATE), load(POST)
    if post.get("candidate_record") != {"path": CANDIDATE.relative_to(ROOT).as_posix(), "sha256": CANDIDATE_SHA}:
        errors.append("candidate binding drift")
    if post.get("principia") != {"candidate_head_commit": HEAD, "merge_commit": MERGE, "pull_request": 84, "repository": "Rhodan-lab/principle-to-system"}:
        errors.append("merge provenance drift")
    if post.get("validation") != {"applicable_workflows": WORKFLOWS, "candidate_head_commit": HEAD, "status": "success"}:
        errors.append("workflow provenance drift")
    if post.get("result") != candidate.get("result") or post.get("authority") != candidate.get("authority"):
        errors.append("candidate finalization binding drift")
    if post.get("state") != FINAL_STATE or post.get("next_gate") != NEXT:
        errors.append("final state drift")
    if post.get("decision") != candidate.get("decision") or post.get("live") is not False or post.get("real_authorization_claimed") is not False:
        errors.append("final decision or frozen-state drift")

    state_text = STATE.read_text(encoding="utf-8")
    markers = (
        "**Phase 46 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Population Readiness Assurance merged and validated through PR #84.**",
        "Phase 46 state: **%s**" % FINAL_STATE,
        "| 46 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate population readiness assurance | Merged and validated through PR #84 |",
        "Phase 46 exact candidate validation passed at `%s`" % HEAD,
        "PR #84 was merged into `main` at commit `%s`" % MERGE,
        "Historical Phase 45 finalization marker:",
        "Atlas remains unchanged by Principia Phase 46",
        CANDIDATE_SHA,
        POST_SHA,
        "all 39 applicable workflows",
        "198 deterministic scenarios",
        "197 mutations",
    )
    for marker in markers:
        if marker not in state_text:
            errors.append("state marker missing: %s" % marker)
    if "## Next phase" not in state_text:
        errors.append("current next-phase section missing")
    else:
        section = state_text.rsplit("## Next phase", 1)[1]
        if "Next gate: **%s**." % NEXT not in section:
            errors.append("current Phase 47 population-execution-readiness gate missing")
        if "Next gate: **%s-candidate**." % MODE in section:
            errors.append("historical Phase 46 assurance gate remains current")

    report_text = REPORT.read_text(encoding="utf-8")
    for marker in (
        "State: `%s`" % FINAL_STATE,
        "Phase 46 candidate SHA-256: `%s`" % CANDIDATE_SHA,
        "Phase 46 post-merge SHA-256: `%s`" % POST_SHA,
        "Phase 46 applicable candidate workflows: `39`",
        "Next gate: `%s`" % NEXT,
    ):
        if marker not in report_text:
            errors.append("report marker missing: %s" % marker)

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    if "contents: read" not in workflow_text or "validate_phase46_postmerge_record.py" not in workflow_text:
        errors.append("workflow finalization integration drift")
    for token in ("contents: write", "pull_request_target", "git push", "git commit", "repository: Rhodan-lab/Atlas"):
        if token in workflow_text:
            errors.append("forbidden workflow token: %s" % token)
    return errors

def main():
    errors = validate()
    if errors:
        print("Phase 46 post-merge record errors:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1
    print("Phase 46 post-merge record passed: candidate=%s, postmerge=%s, head=%s, merge=%s, workflows=%s." % (CANDIDATE_SHA, POST_SHA, HEAD, MERGE, WORKFLOWS))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
"""
for old, new in (
    ("__CANDIDATE_PATH__", CANDIDATE.relative_to(ROOT).as_posix()),
    ("__REPORT_PATH__", REPORT.relative_to(ROOT).as_posix()),
    ("__WORKFLOW_PATH__", WORKFLOW.relative_to(ROOT).as_posix()),
    ("__CANDIDATE_SHA__", CANDIDATE_SHA),
    ("__POST_SHA__", POST_SHA),
    ("__HEAD__", HEAD),
    ("__MERGE__", MERGE),
    ("__MODE__", MODE),
    ("__FINAL_STATE__", FINAL_STATE),
    ("__NEXT__", NEXT),
):
    validator = validator.replace(old, new)
POST_VALIDATOR.write_text(validator, encoding="utf-8")

report = f"""# Phase 46 — Offline Candidate Population Readiness Assurance

> Date: 2026-07-31
> Repository: `Rhodan-lab/principle-to-system`
> State: `{FINAL_STATE}`

## Immutable candidate boundary

- Phase 46 candidate SHA-256: `{CANDIDATE_SHA}`
- Phase 46 post-merge SHA-256: `{POST_SHA}`
- Exact tested head: `{HEAD}`
- Candidate PR: `#84`
- Candidate merge commit: `{MERGE}`
- Phase 46 applicable candidate workflows: `{WORKFLOWS}`

## Immutable source boundary

- Phase 45 candidate SHA-256: `3fa7ce42cce65231c394f27f248e68ce40799ba9a5ccf183923c59fa9da851d6`
- Phase 45 post-merge SHA-256: `74a75833b867fa1db0bad3651e2131d0cbc0f9cacff9fa27f5f9498f11810ac1`
- Phase 45 authoritative finalization: `76ad08f04fc1452c0359da40702cd4e86764467a`
- Phase 45 applicable workflows: `38`

## Finalized assurance result

- Population-assurance policies: `1`
- Population-assurance profiles: `2`
- Population-assurance records: `2`
- Assurance checks: `160`
- Failed assurance checks: `0`
- Preserved source checks: `144`; failed: `0`
- Population slots: `36`; populated: `0`; blocked: `36`
- Symbolic unresolved source references: `36`
- Population stages: `36`; active: `0`
- Population requirements: `72`; evaluated: `0`
- Human gates pending: `10`; satisfied: `0`
- Recovery scenarios: `198`; rejected mutations: `197`

## Frozen boundaries

No candidate is created, assembled, populated, persisted, signed, or submitted. No source reference is resolved and no value is inserted. No population run starts. No decision is selected or recorded. No authorization, token, or execution ticket is issued. No envelope is processed, reviewer contacted, validation result recorded, audit event emitted, or status changed. Atlas is not called or modified. External networking is not required.

## Next gate

`{NEXT}`
"""
REPORT.write_text(report, encoding="utf-8")

state = STATE.read_text(encoding="utf-8")
old_current = "**Phase 45 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Population Readiness merged and validated through PR #82.**"
new_current = "**Phase 46 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Population Readiness Assurance merged and validated through PR #84.**"
state = replace_once(state, old_current, new_current, "current phase")

phase45_state = "Phase 45 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-validated** (`mode: offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness`, `live: false`)."
phase46_state = "Phase 46 state: **" + FINAL_STATE + "** (`mode: " + MODE + "`, `live: false`)."
state = replace_once(state, phase45_state, phase45_state + "\n" + phase46_state, "phase state")

row45 = "| 45 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate population readiness | Merged and validated through PR #82 |"
row46 = "| 46 | Offline consequence-plan review-response intake envelope validation execution authorization decision candidate population readiness assurance | Merged and validated through PR #84 |"
state = replace_once(state, row45, row45 + "\n" + row46, "phase table")

if "## Next phase" not in state:
    raise SystemExit("PROJECT_STATE next-phase section missing")
prefix = state.rsplit("## Next phase", 1)[0].rstrip()
block = f"""## Phase 46 result — Offline Candidate Population Readiness Assurance

- Historical Phase 45 finalization marker: **Phase 45 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Decision Candidate Population Readiness merged and validated through PR #82.**
- Phase 46 exact candidate validation passed at `{HEAD}`.
- PR #84 was merged into `main` at commit `{MERGE}`.
- Candidate SHA-256: `{CANDIDATE_SHA}`.
- Post-merge SHA-256: `{POST_SHA}`.
- Candidate validation passed across all {WORKFLOWS} applicable workflows.
- The recovery matrix contains 198 deterministic scenarios and rejects 197 mutations.
- All 36 population slots remain empty and blocked; all 36 source references remain symbolic and unresolved.
- All 36 population stages remain inactive, all 72 requirements remain unevaluated, and all 10 human gates remain pending.
- No candidate, population run, decision, grant, token, ticket, execution, envelope, reviewer contact, validation result, audit event, or status change exists.
- Atlas remains unchanged by Principia Phase 46.

## Next phase

Next gate: **{NEXT}**.

Phase 47 may define deterministic population-execution-readiness preconditions for a still-uncreated and unpopulated authorization-decision candidate. It must keep all population slots empty and blocked; preserve symbolic unresolved references, inactive stages, unevaluated requirements, and pending human gates; and must not create, assemble, populate, persist, sign, or submit a candidate, start a population run, select or record a decision, grant authorization, issue a token or ticket, contact a reviewer, call Atlas, require external networking, or alter repository status.
"""
STATE.write_text(prefix + "\n\n" + block, encoding="utf-8")

new_current_gate = NEXT
for filename in ("validate_phase42_postmerge_record.py", "validate_phase43_postmerge_record.py", "validate_phase44_postmerge_record.py"):
    path = ROOT / "scripts" / filename
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, 'CURRENT_NEXT = "' + OLD_CURRENT_GATE + '"', 'CURRENT_NEXT = "' + new_current_gate + '"', filename + " current gate")
    text = text.replace("current Phase 46 population-readiness assurance gate", "current Phase 47 population-execution-readiness gate")
    path.write_text(text, encoding="utf-8")

phase45 = ROOT / "scripts/validate_phase45_postmerge_record.py"
text = phase45.read_text(encoding="utf-8")
next_line = "NEXT = '" + OLD_CURRENT_GATE + "'"
text = replace_once(text, next_line, next_line + "\nCURRENT_NEXT = '" + new_current_gate + "'", "Phase 45 current gate declaration")
text = replace_once(
    text,
    'if f"Next gate: **{NEXT}**." not in section:\n            errors.append("current Phase 46 assurance gate missing")',
    'if f"Next gate: **{CURRENT_NEXT}**." not in section:\n            errors.append("current Phase 47 population-execution-readiness gate missing")',
    "Phase 45 gate assertion",
)
anchor = '        if f"Next gate: **{MODE}-candidate**." in section:\n            errors.append("historical Phase 45 candidate gate remains current")'
replacement = '        if f"Next gate: **{NEXT}**." in section:\n            errors.append("historical Phase 46 assurance gate remains current")\n' + anchor
text = replace_once(text, anchor, replacement, "Phase 45 historical gate assertion")
phase45.write_text(text, encoding="utf-8")

commands = [
    ("python3", "-m", "py_compile",
     'scripts/generate_phase46_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_readiness_assurance.py',
     'scripts/validate_phase46_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_readiness_assurance.py',
     "scripts/validate_phase46_postmerge_record.py",
     "scripts/validate_phase45_postmerge_record.py",
     "scripts/validate_phase44_postmerge_record.py",
     "scripts/validate_phase43_postmerge_record.py",
     "scripts/validate_phase42_postmerge_record.py"),
    ("python3", 'scripts/generate_phase46_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_readiness_assurance.py', "--check"),
    ("python3", 'scripts/validate_phase46_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_readiness_assurance.py'),
    ("python3", "scripts/validate_phase46_postmerge_record.py"),
    ("python3", "-m", "unittest", "discover", "-s", "software/tests", "-p", 'test_phase46*population_readiness_assurance.py', "-v"),
    ("python3", "scripts/validate_phase45_postmerge_record.py"),
    ("python3", "scripts/validate_phase44_postmerge_record.py"),
    ("python3", "scripts/validate_phase43_postmerge_record.py"),
    ("python3", "scripts/validate_phase42_postmerge_record.py"),
]
for command in commands:
    subprocess.run(command, cwd=ROOT, check=True)

subprocess.run(("git", "diff", "--check"), cwd=ROOT, check=True)
PUBLISHER.unlink()
subprocess.run((
    "git", "add",
    "PROJECT_STATE.md",
    POST.relative_to(ROOT).as_posix(),
    REPORT.relative_to(ROOT).as_posix(),
    POST_VALIDATOR.relative_to(ROOT).as_posix(),
    "scripts/validate_phase45_postmerge_record.py",
    "scripts/validate_phase44_postmerge_record.py",
    "scripts/validate_phase43_postmerge_record.py",
    "scripts/validate_phase42_postmerge_record.py",
    PUBLISHER.relative_to(ROOT).as_posix(),
), cwd=ROOT, check=True)
subprocess.run(("git", "diff", "--cached", "--check"), cwd=ROOT, check=True)
subprocess.run(("git", "config", "user.name", "github-actions[bot]"), cwd=ROOT, check=True)
subprocess.run(("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"), cwd=ROOT, check=True)
subprocess.run(("git", "commit", "-m", "Finalize Phase 46 population-readiness assurance"), cwd=ROOT, check=True)
subprocess.run(("git", "push", "origin", "HEAD"), cwd=ROOT, check=True)
print("Phase 46 finalization published: postmerge_sha256=" + POST_SHA)
