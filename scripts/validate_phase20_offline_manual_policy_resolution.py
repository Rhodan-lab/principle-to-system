#!/usr/bin/env python3
"""Validate Phase 20 offline manual-policy-resolution evidence and boundaries."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import generate_phase20_offline_manual_policy_resolution as gen  # noqa: E402

REPORT_PATH = ROOT / "reports/phase-20-offline-manual-policy-resolution.md"
STATE_PATH = ROOT / "PROJECT_STATE.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-20-offline-manual-policy-resolution.yml"


class ValidationError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def authority(value: Any) -> None:
    if value != gen.AUTHORITY:
        if isinstance(value, Mapping) and value.get("status_inheritance") != "prohibited":
            raise ValidationError("E-P20-STATUS-INHERITANCE")
        raise ValidationError("E-P20-AUTHORITY")


def artifacts(value: Any) -> None:
    if not isinstance(value, list) or len(value) != 3:
        raise ValidationError("E-P20-AFFECTED-SET")
    keys = tuple(item.get("exact_key") for item in value if isinstance(item, Mapping))
    expected = tuple(item["exact_key"] for item in gen.ARTIFACTS)
    if keys != expected:
        raise ValidationError("E-P20-AFFECTED-SET")
    for item in value:
        if not isinstance(item, Mapping):
            raise ValidationError("E-P20-AFFECTED-SET")
        if item.get("artifact_revision") != 1:
            raise ValidationError("E-P20-AFFECTED-SET")
        if item.get("observed_pedagogical_status") != "reviewed":
            raise ValidationError("E-P20-AFFECTED-SET")
        if item.get("observed_release_status") != "draft":
            raise ValidationError("E-P20-AFFECTED-SET")


def validate_stream(stream: Mapping[str, Any]) -> None:
    if stream.get("contract") != "principia-offline-manual-policy-resolutions/0.1":
        raise ValidationError("E-P20-CONTRACT")
    if stream.get("mode") != gen.MODE or stream.get("live") is not False:
        raise ValidationError("E-P20-LIVE-FROZEN")
    if stream.get("fixture_kind") != "bounded-synthetic":
        raise ValidationError("E-P20-FIXTURE-KIND")
    authority(stream.get("authority"))
    if stream.get("source") != gen.source():
        raise ValidationError("E-P20-SOURCE-PIN")

    entries = stream.get("resolutions")
    if not isinstance(entries, list) or len(entries) != 2:
        raise ValidationError("E-P20-COUNT")
    expected = (
        (
            "accept",
            "accepted-for-manual-review",
            "manual-review-item",
            "principia:policy-review:feedback-deprecation:0001",
            gen.QUEUE_SHA,
        ),
        (
            "defer",
            "deferred-no-hold-activation",
            "release-hold-proposal",
            "principia:release-hold-proposal:model-boundary-retraction:0001",
            gen.HOLD_SHA,
        ),
    )
    seen: set[str] = set()
    previous: str | None = None
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            raise ValidationError("E-P20-SHAPE")
        resolution = entry.get("resolution")
        digest = entry.get("resolution_sha256")
        if not isinstance(resolution, Mapping) or not isinstance(digest, str):
            raise ValidationError("E-P20-SHAPE")
        if gen.doc_sha(resolution) != digest:
            raise ValidationError("E-P20-DIGEST")
        if resolution.get("sequence") != index + 1:
            raise ValidationError("E-P20-SEQUENCE")
        if resolution.get("previous_resolution_sha256") != previous:
            raise ValidationError("E-P20-PREVIOUS-DIGEST")
        rid = resolution.get("resolution_id")
        if not isinstance(rid, str) or rid in seen:
            raise ValidationError("E-P20-DUPLICATE")
        seen.add(rid)

        decision, outcome, kind, proposal_id, proposal_sha = expected[index]
        if resolution.get("decision") != decision or resolution.get("outcome") != outcome:
            raise ValidationError("E-P20-DECISION")
        if resolution.get("proposal_kind") != kind or resolution.get("proposal_id") != proposal_id:
            raise ValidationError("E-P20-PROPOSAL-ID")
        if resolution.get("proposal_document_sha256") != proposal_sha:
            raise ValidationError("E-P20-PROPOSAL-DIGEST")
        if resolution.get("fixture_kind") != "bounded-synthetic":
            raise ValidationError("E-P20-FIXTURE-KIND")
        authority(resolution.get("authority"))
        if resolution.get("status_change") is not False:
            raise ValidationError("E-P20-AUTHORITY")
        if resolution.get("operational_effect") is not False:
            raise ValidationError("E-P20-AUTOMATIC-EXECUTION")
        if resolution.get("hold_effective") is not False:
            raise ValidationError("E-P20-HOLD-EFFECTIVE")
        artifacts(resolution.get("affected_artifacts"))
        previous = digest

    if stream.get("summary") != {
        "accepted_count": 1,
        "deferred_count": 1,
        "effective_hold_count": 0,
        "operational_effect_count": 0,
        "rejected_count": 0,
        "replaced_count": 0,
        "resolution_count": 2,
        "status_change_count": 0,
    }:
        raise ValidationError("E-P20-SUMMARY")


def validate_bundle(bundle: Mapping[Path, Mapping[str, Any]]) -> None:
    stream = bundle[gen.RESOLUTIONS_PATH]
    ledger = bundle[gen.LEDGER_PATH]
    checkpoint = bundle[gen.CHECKPOINT_PATH]
    recovery = bundle[gen.RECOVERY_PATH]
    release = bundle[gen.RELEASE_PATH]

    validate_stream(stream)
    authority(ledger.get("authority"))
    if ledger.get("contract") != "principia-offline-manual-policy-resolution-ledger/0.1":
        raise ValidationError("E-P20-LEDGER")
    if ledger.get("source_resolution_stream_sha256") != gen.doc_sha(stream):
        raise ValidationError("E-P20-LEDGER")
    links = ledger.get("links")
    if not isinstance(links, list) or len(links) != 2:
        raise ValidationError("E-P20-LEDGER")
    if ledger.get("head_resolution_sha256") != links[-1].get("resolution_sha256"):
        raise ValidationError("E-P20-LEDGER")

    authority(checkpoint.get("authority"))
    if checkpoint.get("resolution_stream_sha256") != gen.doc_sha(stream):
        raise ValidationError("E-P20-CHECKPOINT")
    if checkpoint.get("ledger_sha256") != gen.doc_sha(ledger):
        raise ValidationError("E-P20-CHECKPOINT")
    if any(
        checkpoint.get(key) != 0
        for key in ("effective_hold_count", "operational_effect_count", "status_change_count")
    ):
        raise ValidationError("E-P20-CHECKPOINT")

    authority(recovery.get("authority"))
    expected_scenarios = [
        {"expected_error": error, "expected_outcome": outcome, "scenario_id": scenario}
        for scenario, outcome, error in gen.SCENARIOS
    ]
    if recovery.get("scenarios") != expected_scenarios:
        raise ValidationError("E-P20-RECOVERY")

    authority(release.get("authority"))
    if release.get("state") != "offline-manual-policy-resolution-candidate":
        raise ValidationError("E-P20-RELEASE")
    if release.get("mode") != gen.MODE or release.get("live") is not False:
        raise ValidationError("E-P20-LIVE-FROZEN")
    if release.get("source_phase19") != gen.source():
        raise ValidationError("E-P20-SOURCE-PIN")
    if release.get("validation") != {
        "pull_request": None,
        "status": "pending",
        "tested_head_commit": None,
    }:
        raise ValidationError("E-P20-RELEASE")
    for name, path in {
        "checkpoint": gen.CHECKPOINT_PATH,
        "ledger": gen.LEDGER_PATH,
        "recovery": gen.RECOVERY_PATH,
        "resolutions": gen.RESOLUTIONS_PATH,
    }.items():
        if release.get("artifacts", {}).get(name) != {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": gen.file_sha(bundle[path]),
        }:
            raise ValidationError("E-P20-RELEASE")


def main() -> int:
    errors: list[str] = []
    source_files = (
        (ROOT / "release/phase-19-postmerge.json", gen.P19_POST, "E-P20-SOURCE-PIN"),
        (
            gen.PILOT / "thermal-control.policy-review-queue.v01.json",
            gen.QUEUE_SHA,
            "E-P20-PROPOSAL-DIGEST",
        ),
        (
            gen.PILOT / "thermal-control.release-hold-proposals.v01.json",
            gen.HOLD_SHA,
            "E-P20-PROPOSAL-DIGEST",
        ),
        (
            gen.PILOT / "thermal-control.policy-ledger.v01.json",
            gen.POLICY_LEDGER_SHA,
            "E-P20-PROPOSAL-DIGEST",
        ),
    )
    for path, expected, code in source_files:
        if not path.is_file() or gen.hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(code)

    try:
        built = gen.build()
        validate_bundle(built)
        for path, value in built.items():
            if not path.is_file() or path.read_text(encoding="utf-8") != gen.render(value):
                errors.append(f"generated file drift: {path.relative_to(ROOT)}")
    except (OSError, json.JSONDecodeError, KeyError, ValidationError) as exc:
        errors.append(str(exc))

    for path in (REPORT_PATH, STATE_PATH, WORKFLOW_PATH):
        if not path.is_file():
            errors.append(f"missing Phase 20 file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "Phase 20",
        "offline-manual-policy-resolution",
        "| 20 | Offline manual policy resolution |",
        "Historical Phase 20 candidate marker: `exact-head validation pending`",
        "resolutions-recorded-no-mutation",
        "bounded-synthetic",
        "live: false",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 20 marker: {marker}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        "# Phase 20 — Offline Manual Policy Resolution",
        "`principia-offline-manual-policy-resolutions/0.1`",
        "`accept`",
        "`defer`",
        "bounded-synthetic",
        "0 effective holds",
        "resolutions-recorded-no-mutation",
        "Live: `false`",
    ):
        if marker not in report:
            errors.append(f"Phase 20 report missing marker: {marker}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "agent/phase-20-offline-manual-policy-resolution",
        "scripts/generate_phase20_offline_manual_policy_resolution.py --check",
        "scripts/validate_phase20_offline_manual_policy_resolution.py",
        "software.tests.test_phase20_offline_manual_policy_resolution",
        "scripts/validate_phase19_postmerge_record.py",
        "contents: read",
    ):
        if marker not in workflow:
            errors.append(f"Phase 20 workflow missing marker: {marker}")
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
            errors.append(f"Phase 20 workflow contains prohibited operation: {token}")

    if errors:
        return fail(errors)
    print(
        "Phase 20 passed: synthetic accept/defer resolutions are digest-bound, "
        "non-effective, non-mutating, and live=false."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("Phase 20 validation errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
