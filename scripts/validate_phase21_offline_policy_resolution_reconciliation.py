#!/usr/bin/env python3
"""Validate Phase 21 offline policy-resolution reconciliation evidence."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import generate_phase21_offline_policy_resolution_reconciliation as gen  # noqa: E402

STATE_PATH = ROOT / "PROJECT_STATE.md"
REPORT_DOC_PATH = ROOT / "reports" / "phase-21-offline-policy-resolution-reconciliation.md"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "validate-phase-21-offline-policy-resolution-reconciliation.yml"
FINALIZATION_PATH = ROOT / "release" / "phase-21-postmerge.json"


class ValidationError(ValueError):
    pass


def authority(value: Any) -> None:
    if value != gen.AUTHORITY:
        if isinstance(value, Mapping) and value.get("status_inheritance") != "prohibited":
            raise ValidationError("E-P21-STATUS-INHERITANCE")
        raise ValidationError("E-P21-AUTHORITY")


def validate_report(report: Mapping[str, Any]) -> None:
    expected_top = {
        "contract": "principia-offline-policy-resolution-reconciliation-report/0.1",
        "decision": gen.DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "mode": gen.MODE,
        "real_authorization_claimed": False,
        "reconciliation_id": "principia:offline-policy-resolution-reconciliation:thermal-control:0001",
        "source": gen.source(),
    }
    for key, value in expected_top.items():
        if report.get(key) != value:
            if key == "live":
                raise ValidationError("E-P21-LIVE-FROZEN")
            if key == "real_authorization_claimed":
                raise ValidationError("E-P21-AUTHORIZATION")
            if key == "source":
                raise ValidationError("E-P21-SOURCE-PIN")
            raise ValidationError("E-P21-CONTRACT")
    authority(report.get("authority"))

    matches = report.get("matches")
    if not isinstance(matches, list):
        raise ValidationError("E-P21-SHAPE")
    if len(matches) < 2:
        raise ValidationError("E-P21-MISSING")
    if len(matches) > 2:
        raise ValidationError("E-P21-ORPHAN")

    seen_proposals: set[str] = set()
    seen_resolutions: set[str] = set()
    for index, (actual, expected) in enumerate(zip(matches, gen.MATCHES), start=1):
        if not isinstance(actual, Mapping):
            raise ValidationError("E-P21-SHAPE")
        if actual.get("sequence") != index:
            raise ValidationError("E-P21-SEQUENCE")
        proposal_id = actual.get("proposal_id")
        resolution_id = actual.get("resolution_id")
        if proposal_id in seen_proposals or resolution_id in seen_resolutions:
            raise ValidationError("E-P21-DUPLICATE")
        seen_proposals.add(str(proposal_id))
        seen_resolutions.add(str(resolution_id))
        if proposal_id != expected["proposal_id"] or actual.get("proposal_kind") != expected["proposal_kind"]:
            raise ValidationError("E-P21-PROPOSAL-ID")
        if actual.get("proposal_document_sha256") != expected["proposal_document_sha256"]:
            raise ValidationError("E-P21-PROPOSAL-DIGEST")
        if resolution_id != expected["resolution_id"]:
            raise ValidationError("E-P21-ORPHAN")
        if actual.get("resolution_sha256") != expected["resolution_sha256"]:
            raise ValidationError("E-P21-RESOLUTION-DIGEST")
        if actual.get("decision") != expected["decision"] or actual.get("outcome") != expected["outcome"]:
            raise ValidationError("E-P21-DECISION")
        if actual.get("affected_artifacts") != gen.ARTIFACT_KEYS:
            raise ValidationError("E-P21-AFFECTED-SET")
        if actual.get("matched") is not True:
            raise ValidationError("E-P21-MISSING")
        if actual.get("real_authorization_claimed") is not False:
            raise ValidationError("E-P21-AUTHORIZATION")
        if any(actual.get(key) is not False for key in ("effective_hold", "operational_effect", "status_change")):
            raise ValidationError("E-P21-EFFECT")

    expected_summary = {
        "checkpoint_mismatch_count": 0,
        "effective_hold_count": 0,
        "ledger_mismatch_count": 0,
        "matched_resolution_count": 2,
        "missing_resolution_count": 0,
        "operational_effect_count": 0,
        "orphan_resolution_count": 0,
        "proposal_count": 2,
        "proposal_digest_mismatch_count": 0,
        "resolution_count": 2,
        "resolution_digest_mismatch_count": 0,
        "status_change_count": 0,
        "unique_affected_artifact_count": 3,
    }
    if report.get("summary") != expected_summary:
        raise ValidationError("E-P21-SUMMARY")


def validate_bundle(bundle: Mapping[Path, Mapping[str, Any]]) -> None:
    report = bundle[gen.REPORT_PATH]
    ledger = bundle[gen.LEDGER_PATH]
    checkpoint = bundle[gen.CHECKPOINT_PATH]
    recovery = bundle[gen.RECOVERY_PATH]
    release = bundle[gen.RELEASE_PATH]
    validate_report(report)

    authority(ledger.get("authority"))
    if ledger.get("contract") != "principia-offline-policy-resolution-reconciliation-ledger/0.1":
        raise ValidationError("E-P21-LEDGER")
    if ledger.get("mode") != gen.MODE or ledger.get("live") is not False:
        raise ValidationError("E-P21-LIVE-FROZEN")
    if ledger.get("source_reconciliation_report_sha256") != gen.doc_sha(report):
        raise ValidationError("E-P21-LEDGER")
    entries = ledger.get("entries")
    if not isinstance(entries, list) or len(entries) != 2:
        raise ValidationError("E-P21-LEDGER")
    previous: str | None = None
    for index, item in enumerate(entries, start=1):
        if not isinstance(item, Mapping) or not isinstance(item.get("entry"), Mapping):
            raise ValidationError("E-P21-LEDGER")
        entry = item["entry"]
        digest = item.get("entry_sha256")
        if digest != gen.doc_sha(entry):
            raise ValidationError("E-P21-LEDGER")
        if entry.get("match_sequence") != index:
            raise ValidationError("E-P21-SEQUENCE")
        if entry.get("previous_entry_sha256") != previous:
            raise ValidationError("E-P21-LEDGER")
        expected = gen.MATCHES[index - 1]
        for key in ("proposal_id", "proposal_document_sha256", "resolution_id", "resolution_sha256", "decision"):
            if entry.get(key) != expected[key]:
                raise ValidationError("E-P21-LEDGER")
        previous = str(digest)
    if ledger.get("head_sequence") != 2 or ledger.get("head_entry_sha256") != previous:
        raise ValidationError("E-P21-LEDGER")

    authority(checkpoint.get("authority"))
    if checkpoint.get("contract") != "principia-offline-policy-resolution-reconciliation-checkpoint/0.1":
        raise ValidationError("E-P21-CHECKPOINT")
    if checkpoint.get("reconciliation_report_sha256") != gen.doc_sha(report):
        raise ValidationError("E-P21-CHECKPOINT")
    if checkpoint.get("ledger_sha256") != gen.doc_sha(ledger):
        raise ValidationError("E-P21-CHECKPOINT")
    if checkpoint.get("source_resolution_checkpoint_sha256") != gen.RESOLUTION_CHECKPOINT_SHA:
        raise ValidationError("E-P21-CHECKPOINT")
    counts = {
        "proposal_count": 2,
        "resolution_count": 2,
        "matched_resolution_count": 2,
        "missing_resolution_count": 0,
        "orphan_resolution_count": 0,
        "effective_hold_count": 0,
        "operational_effect_count": 0,
        "status_change_count": 0,
        "real_authorization_claimed": False,
    }
    for key, value in counts.items():
        if checkpoint.get(key) != value:
            if key == "real_authorization_claimed":
                raise ValidationError("E-P21-AUTHORIZATION")
            if key in ("effective_hold_count", "operational_effect_count", "status_change_count"):
                raise ValidationError("E-P21-EFFECT")
            raise ValidationError("E-P21-CHECKPOINT")

    authority(recovery.get("authority"))
    expected_scenarios = [
        {"expected_error": error, "expected_outcome": outcome, "scenario_id": scenario}
        for scenario, outcome, error in gen.SCENARIOS
    ]
    if recovery.get("scenarios") != expected_scenarios:
        raise ValidationError("E-P21-RECOVERY")
    if recovery.get("baseline") != {
        "checkpoint_sha256": gen.doc_sha(checkpoint),
        "ledger_sha256": gen.doc_sha(ledger),
        "reconciliation_report_sha256": gen.doc_sha(report),
    }:
        raise ValidationError("E-P21-RECOVERY")

    authority(release.get("authority"))
    expected_release = {
        "contract": "principia-offline-policy-resolution-reconciliation/0.1",
        "decision": gen.DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "mode": gen.MODE,
        "next_gate": "offline-resolution-consequence-planning-candidate",
        "phase": 21,
        "real_authorization_claimed": False,
        "source_phase20": gen.source(),
        "state": "offline-policy-resolution-reconciliation-candidate",
    }
    for key, value in expected_release.items():
        if release.get(key) != value:
            if key == "live":
                raise ValidationError("E-P21-LIVE-FROZEN")
            if key == "real_authorization_claimed":
                raise ValidationError("E-P21-AUTHORIZATION")
            if key == "source_phase20":
                raise ValidationError("E-P21-SOURCE-PIN")
            raise ValidationError("E-P21-RELEASE")
    if release.get("result") != report.get("summary"):
        raise ValidationError("E-P21-RELEASE")
    if release.get("validation") != {"pull_request": None, "status": "pending", "tested_head_commit": None}:
        raise ValidationError("E-P21-RELEASE")
    paths = {
        "checkpoint": gen.CHECKPOINT_PATH,
        "ledger": gen.LEDGER_PATH,
        "reconciliation_report": gen.REPORT_PATH,
        "recovery": gen.RECOVERY_PATH,
    }
    for name, path in paths.items():
        if release.get("artifacts", {}).get(name) != {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": gen.file_sha(bundle[path]),
        }:
            raise ValidationError("E-P21-RELEASE")


def main() -> int:
    errors: list[str] = []
    sources = (
        (ROOT / "release/phase-20-postmerge.json", gen.PHASE20_POSTMERGE_SHA, "E-P21-SOURCE-PIN"),
        (ROOT / "release/phase-20-offline-manual-policy-resolution.json", gen.PHASE20_CANDIDATE_SHA, "E-P21-SOURCE-PIN"),
        (gen.PILOT / "thermal-control.policy-review-queue.v01.json", gen.REVIEW_QUEUE_SHA, "E-P21-PROPOSAL-DIGEST"),
        (gen.PILOT / "thermal-control.release-hold-proposals.v01.json", gen.HOLD_PROPOSALS_SHA, "E-P21-PROPOSAL-DIGEST"),
        (gen.PILOT / "thermal-control.policy-ledger.v01.json", gen.POLICY_LEDGER_SHA, "E-P21-SOURCE-PIN"),
        (gen.PILOT / "thermal-control.manual-policy-resolutions.v01.json", gen.RESOLUTION_STREAM_SHA, "E-P21-RESOLUTION-DIGEST"),
        (gen.PILOT / "thermal-control.manual-policy-resolution-ledger.v01.json", gen.RESOLUTION_LEDGER_SHA, "E-P21-LEDGER"),
        (gen.PILOT / "thermal-control.manual-policy-resolution-checkpoint.v01.json", gen.RESOLUTION_CHECKPOINT_SHA, "E-P21-CHECKPOINT"),
    )
    for path, expected, code in sources:
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(code)
    try:
        built = gen.build()
        validate_bundle(built)
        for path, value in built.items():
            if not path.is_file() or path.read_text(encoding="utf-8") != gen.render(value):
                errors.append(f"generated file drift: {path.relative_to(ROOT)}")
    except (OSError, json.JSONDecodeError, KeyError, ValidationError) as exc:
        errors.append(str(exc))

    for path in (STATE_PATH, REPORT_DOC_PATH, WORKFLOW_PATH):
        if not path.is_file():
            errors.append(f"missing Phase 21 file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    finalized = FINALIZATION_PATH.is_file()
    state = STATE_PATH.read_text(encoding="utf-8")
    state_markers = (
        (
            "Phase 21 state: **offline-policy-resolution-reconciliation-validated**",
            "| 21 | Offline policy-resolution reconciliation | Merged and validated through PR #32 |",
            "release/phase-21-postmerge.json",
        )
        if finalized
        else (
            "**Phase 21 — Offline Policy-Resolution Reconciliation Candidate implemented",
            "Phase 21 target state: **offline-policy-resolution-reconciliation-candidate**",
            "| 21 | Offline policy-resolution reconciliation | Implemented; exact-head validation pending |",
        )
    )
    for marker in (*state_markers, "Phase 20 state: **offline-manual-policy-resolution-validated**",
                   "reconciled-resolutions-no-mutation", "bounded-synthetic",
                   "real_authorization_claimed: false", "live: false"):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 21 marker: {marker}")

    report_doc = REPORT_DOC_PATH.read_text(encoding="utf-8")
    report_markers = (
        (
            "# Phase 21 — Offline Policy-Resolution Reconciliation",
            "Final state: `offline-policy-resolution-reconciliation-validated`",
            "release/phase-21-postmerge.json",
        )
        if finalized
        else (
            "# Phase 21 — Offline Policy-Resolution Reconciliation Candidate",
            "> Candidate state: `offline-policy-resolution-reconciliation-candidate`",
        )
    )
    for marker in (*report_markers, "`principia-offline-policy-resolution-reconciliation-report/0.1`",
                   "2 matched resolutions", "0 missing resolutions", "0 orphan resolutions",
                   "0 effective holds", "real_authorization_claimed: false",
                   "reconciled-resolutions-no-mutation", "> Live: `false`"):
        if marker not in report_doc:
            errors.append(f"Phase 21 report missing marker: {marker}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    workflow_markers = [
        "agent/phase-21-policy-resolution-reconciliation",
        "scripts/generate_phase21_offline_policy_resolution_reconciliation.py --check",
        "scripts/validate_phase21_offline_policy_resolution_reconciliation.py",
        "software.tests.test_phase21_offline_policy_resolution_reconciliation",
        "scripts/validate_phase20_postmerge_record.py",
        "contents: read",
    ]
    if finalized:
        workflow_markers.extend(("agent/finalize-phase-21-record", "scripts/validate_phase21_postmerge_record.py"))
    for marker in workflow_markers:
        if marker not in workflow:
            errors.append(f"Phase 21 workflow missing marker: {marker}")
    for token in ("contents: write", "git push", "git commit", "pull_request_target",
                  "repository: Rhodan-lab/Atlas", "curl ", "wget "):
        if token in workflow:
            errors.append(f"Phase 21 workflow contains prohibited operation: {token}")

    if errors:
        return fail(errors)
    print(
        "Phase 21 passed: two proposal/resolution pairs reconcile exactly, ledger and checkpoint agree, "
        "no real authorization is claimed, and all effects remain disabled."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("Phase 21 validation errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
