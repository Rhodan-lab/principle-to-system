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

REPORT_DOC_PATH = ROOT / "reports" / "phase-21-offline-policy-resolution-reconciliation.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-21-offline-policy-resolution-reconciliation.yml"


class ValidationError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authority(value: Any) -> None:
    if value != gen.AUTHORITY:
        if isinstance(value, Mapping) and value.get("status_inheritance") != "prohibited":
            raise ValidationError("E-P21-AUTHORITY")
        raise ValidationError("E-P21-AUTHORITY")


def validate_sources() -> None:
    paths = {
        ROOT / "release/phase-20-postmerge.json": (gen.P20_POST_SHA, "E-P21-SOURCE-PIN"),
        ROOT / "release/phase-20-offline-manual-policy-resolution.json": (
            gen.P20_CANDIDATE_SHA,
            "E-P21-SOURCE-PIN",
        ),
        gen.PILOT / "thermal-control.policy-ledger.v01.json": (
            gen.POLICY_LEDGER_FILE_SHA,
            "E-P21-PROPOSAL-PIN",
        ),
        gen.PILOT / "thermal-control.manual-policy-resolutions.v01.json": (
            gen.RESOLUTION_STREAM_FILE_SHA,
            "E-P21-RESOLUTION-PIN",
        ),
        gen.PILOT / "thermal-control.manual-policy-resolution-ledger.v01.json": (
            gen.RESOLUTION_LEDGER_FILE_SHA,
            "E-P21-LEDGER-PIN",
        ),
        gen.PILOT / "thermal-control.manual-policy-resolution-checkpoint.v01.json": (
            gen.RESOLUTION_CHECKPOINT_FILE_SHA,
            "E-P21-CHECKPOINT-PIN",
        ),
    }
    for path, (expected, code) in paths.items():
        if not path.is_file() or file_sha(path) != expected:
            raise ValidationError(code)

    stream = load(gen.PILOT / "thermal-control.manual-policy-resolutions.v01.json")
    ledger = load(gen.PILOT / "thermal-control.manual-policy-resolution-ledger.v01.json")
    checkpoint = load(
        gen.PILOT / "thermal-control.manual-policy-resolution-checkpoint.v01.json"
    )
    if gen.document_sha256(stream) != gen.RESOLUTION_STREAM_DOC_SHA:
        raise ValidationError("E-P21-RESOLUTION-PIN")
    if gen.document_sha256(ledger) != gen.RESOLUTION_LEDGER_DOC_SHA:
        raise ValidationError("E-P21-LEDGER-PIN")
    if gen.document_sha256(checkpoint) != gen.RESOLUTION_CHECKPOINT_DOC_SHA:
        raise ValidationError("E-P21-CHECKPOINT-PIN")


def validate_reconciliation(value: Mapping[str, Any]) -> None:
    if value.get("contract") != "principia-offline-policy-resolution-reconciliation/0.1":
        raise ValidationError("E-P21-CONTRACT")
    if value.get("mode") != gen.MODE or value.get("live") is not False:
        raise ValidationError("E-P21-LIVE-FROZEN")
    if value.get("fixture_kind") != "bounded-synthetic":
        raise ValidationError("E-P21-FIXTURE")
    if value.get("real_authorization_claimed") is not False:
        raise ValidationError("E-P21-AUTHORIZATION")
    authority(value.get("authority"))
    if value.get("source") != gen.source():
        raise ValidationError("E-P21-SOURCE-PIN")

    matches = value.get("matches")
    if not isinstance(matches, list) or len(matches) != 2:
        raise ValidationError("E-P21-MISSING")
    expected = gen.matches()
    seen_proposals: set[str] = set()
    seen_resolutions: set[str] = set()
    previous: str | None = None
    for index, item in enumerate(matches):
        if not isinstance(item, Mapping):
            raise ValidationError("E-P21-SHAPE")
        exp = expected[index]
        proposal_id = item.get("proposal_id")
        resolution_id = item.get("resolution_id")
        if proposal_id in seen_proposals or resolution_id in seen_resolutions:
            raise ValidationError("E-P21-DUPLICATE")
        seen_proposals.add(str(proposal_id))
        seen_resolutions.add(str(resolution_id))
        if proposal_id != exp["proposal_id"]:
            raise ValidationError("E-P21-PROPOSAL-ID")
        if resolution_id != exp["resolution_id"]:
            raise ValidationError("E-P21-RESOLUTION-ID")
        if item.get("proposal_sequence") != index + 1 or item.get(
            "resolution_sequence"
        ) != index + 1:
            raise ValidationError("E-P21-SEQUENCE")
        if item.get("resolution_previous_sha256") != previous:
            raise ValidationError("E-P21-PREDECESSOR")
        if item.get("decision") != exp["decision"] or item.get("outcome") != exp["outcome"]:
            raise ValidationError("E-P21-DECISION")
        if item.get("affected_artifacts") != gen.ARTIFACT_KEYS:
            raise ValidationError("E-P21-AFFECTED-SET")
        if item.get("proposal_document_sha256") != exp["proposal_document_sha256"]:
            raise ValidationError("E-P21-PROPOSAL-PIN")
        if item.get("proposal_entry_sha256") != exp["proposal_entry_sha256"]:
            raise ValidationError("E-P21-PROPOSAL-PIN")
        if item.get("resolution_sha256") != exp["resolution_sha256"]:
            raise ValidationError("E-P21-RESOLUTION-PIN")
        if item.get("match_status") != "matched":
            raise ValidationError("E-P21-MISSING")
        if item.get("real_authorization_claimed") is not False:
            raise ValidationError("E-P21-AUTHORIZATION")
        if any(
            item.get(key) is not False
            for key in ("authorization_effect", "hold_effect", "status_effect")
        ):
            raise ValidationError("E-P21-EFFECT")
        previous = str(item["resolution_sha256"])

    findings = value.get("findings")
    if not isinstance(findings, Mapping) or any(v != 0 for v in findings.values()):
        raise ValidationError("E-P21-FINDINGS")
    if value.get("result") != {
        "decision": "reconciled-resolutions-no-mutation",
        "matched_resolution_count": 2,
        "missing_resolution_count": 0,
        "orphan_resolution_count": 0,
        "proposal_count": 2,
        "resolution_count": 2,
        "unique_affected_artifact_count": 3,
    }:
        raise ValidationError("E-P21-RESULT")


def validate_bundle(bundle: Mapping[Path, Mapping[str, Any]]) -> None:
    reconciliation = bundle[gen.REPORT_PATH]
    ledger = bundle[gen.LEDGER_PATH]
    checkpoint = bundle[gen.CHECKPOINT_PATH]
    recovery = bundle[gen.RECOVERY_PATH]
    release = bundle[gen.RELEASE_PATH]

    validate_reconciliation(reconciliation)

    authority(ledger.get("authority"))
    if ledger.get("contract") != (
        "principia-offline-policy-resolution-reconciliation-ledger/0.1"
    ):
        raise ValidationError("E-P21-LEDGER")
    if ledger.get("source_reconciliation_sha256") != gen.document_sha256(
        reconciliation
    ):
        raise ValidationError("E-P21-LEDGER")
    entries = ledger.get("entries")
    if not isinstance(entries, list) or len(entries) != 2:
        raise ValidationError("E-P21-LEDGER")
    previous: str | None = None
    for index, wrapper in enumerate(entries):
        if not isinstance(wrapper, Mapping) or not isinstance(wrapper.get("entry"), Mapping):
            raise ValidationError("E-P21-LEDGER")
        entry = wrapper["entry"]
        if entry.get("sequence") != index + 1:
            raise ValidationError("E-P21-SEQUENCE")
        if entry.get("previous_entry_sha256") != previous:
            raise ValidationError("E-P21-PREDECESSOR")
        if entry.get("match_sha256") != gen.document_sha256(
            reconciliation["matches"][index]
        ):
            raise ValidationError("E-P21-LEDGER")
        digest = gen.document_sha256(entry)
        if wrapper.get("entry_sha256") != digest:
            raise ValidationError("E-P21-LEDGER")
        previous = digest
    if ledger.get("head_sequence") != 2 or ledger.get("head_sha256") != previous:
        raise ValidationError("E-P21-LEDGER")

    authority(checkpoint.get("authority"))
    if checkpoint.get("reconciliation_sha256") != gen.document_sha256(reconciliation):
        raise ValidationError("E-P21-CHECKPOINT")
    if checkpoint.get("ledger_sha256") != gen.document_sha256(ledger):
        raise ValidationError("E-P21-CHECKPOINT")
    for key, expected in {
        "proposal_count": 2,
        "resolution_count": 2,
        "matched_resolution_count": 2,
        "missing_resolution_count": 0,
        "orphan_resolution_count": 0,
        "effective_hold_count": 0,
        "operational_effect_count": 0,
        "status_change_count": 0,
    }.items():
        if checkpoint.get(key) != expected:
            raise ValidationError("E-P21-CHECKPOINT")
    if checkpoint.get("real_authorization_claimed") is not False:
        raise ValidationError("E-P21-AUTHORIZATION")

    authority(recovery.get("authority"))
    expected_scenarios = [
        {
            "expected_error": error,
            "expected_outcome": outcome,
            "scenario_id": scenario,
        }
        for scenario, outcome, error in gen.SCENARIOS
    ]
    if recovery.get("scenarios") != expected_scenarios:
        raise ValidationError("E-P21-RECOVERY")
    if recovery.get("baseline") != {
        "checkpoint_sha256": gen.document_sha256(checkpoint),
        "ledger_sha256": gen.document_sha256(ledger),
        "reconciliation_sha256": gen.document_sha256(reconciliation),
    }:
        raise ValidationError("E-P21-RECOVERY")

    authority(release.get("authority"))
    if release.get("contract") != (
        "principia-offline-policy-resolution-reconciliation-release/0.1"
    ):
        raise ValidationError("E-P21-RELEASE")
    if release.get("state") != "offline-policy-resolution-reconciliation-candidate":
        raise ValidationError("E-P21-RELEASE")
    if release.get("mode") != gen.MODE or release.get("live") is not False:
        raise ValidationError("E-P21-LIVE-FROZEN")
    if release.get("real_authorization_claimed") is not False:
        raise ValidationError("E-P21-AUTHORIZATION")
    if release.get("source_phase20") != gen.source():
        raise ValidationError("E-P21-SOURCE-PIN")
    if release.get("validation") != {
        "pull_request": None,
        "status": "pending",
        "tested_head_commit": None,
    }:
        raise ValidationError("E-P21-RELEASE")
    for name, path in {
        "checkpoint": gen.CHECKPOINT_PATH,
        "ledger": gen.LEDGER_PATH,
        "reconciliation": gen.REPORT_PATH,
        "recovery": gen.RECOVERY_PATH,
    }.items():
        expected = {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": gen.file_sha256(bundle[path]),
        }
        if release.get("artifacts", {}).get(name) != expected:
            raise ValidationError("E-P21-RELEASE")


def main() -> int:
    errors: list[str] = []
    try:
        validate_sources()
        built = gen.build()
        validate_bundle(built)
        for path, value in built.items():
            if not path.is_file() or path.read_text(encoding="utf-8") != gen.render(value):
                errors.append(f"generated file drift: {path.relative_to(ROOT)}")
    except (OSError, json.JSONDecodeError, KeyError, ValidationError) as exc:
        errors.append(str(exc))

    for path in (REPORT_DOC_PATH, WORKFLOW_PATH):
        if not path.is_file():
            errors.append(f"missing Phase 21 file: {path.relative_to(ROOT)}")

    if errors:
        return fail(errors)

    report = REPORT_DOC_PATH.read_text(encoding="utf-8")
    for marker in (
        "# Phase 21 — Offline Policy-Resolution Reconciliation Candidate",
        "`principia-offline-policy-resolution-reconciliation/0.1`",
        "2 matched resolutions",
        "0 missing resolutions",
        "0 orphan resolutions",
        "reconciled-resolutions-no-mutation",
        "bounded-synthetic",
        "Live: `false`",
    ):
        if marker not in report:
            errors.append(f"Phase 21 report missing marker: {marker}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/phase-21-offline-policy-resolution-reconciliation",
        "scripts/generate_phase21_offline_policy_resolution_reconciliation.py --check",
        "scripts/validate_phase21_offline_policy_resolution_reconciliation.py",
        "software.tests.test_phase21_offline_policy_resolution_reconciliation",
        "scripts/validate_phase20_postmerge_record.py",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"Phase 21 workflow missing marker: {marker}")
    for token in (
        "contents: write",
        "git push",
        "git commit",
        "pull_request_target",
        "repository: Rhodan-lab/Atlas",
        "curl ",
        "wget ",
    ):
        if token in workflow:
            errors.append(f"Phase 21 workflow contains prohibited operation: {token}")

    if errors:
        return fail(errors)
    print(
        "Phase 21 passed: two proposals reconcile to two bounded-synthetic "
        "resolutions with no authorization, effects, status change, or live integration."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("Phase 21 validation errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
