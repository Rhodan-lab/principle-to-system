#!/usr/bin/env python3
"""Validate the Phase 18 offline reconciliation simulation and governance boundary."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping

import generate_phase18_offline_reconciliation as reconciliation
import generate_phase18_release_record as release_record

ROOT = Path(__file__).resolve().parent.parent
RELEASE_PATH = release_record.RELEASE_PATH
REPORT_DOC_PATH = ROOT / "reports" / "phase-18-offline-reconciliation.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-18-offline-reconciliation.yml"
TEST_PATH = ROOT / "software/tests/test_phase18_offline_reconciliation.py"
STATE_PATH = ROOT / "PROJECT_STATE.md"

EXPECTED_RECOVERY = {
    "exact-reconciliation": (True, "reconciled", None),
    "missing-acknowledgement": (False, "divergence-detected", "E-P18-COUNT-MISMATCH"),
    "orphan-acknowledgement": (False, "divergence-detected", "E-P18-ACK-ORPHAN"),
    "ack-event-digest-mismatch": (False, "divergence-detected", "E-P18-ACK-EVENT-DIGEST"),
    "action-weakening": (False, "divergence-detected", "E-P18-ACTION-MISMATCH"),
    "affected-artifact-mismatch": (False, "divergence-detected", "E-P18-AFFECTED-SET"),
    "stale-artifact-revision": (False, "divergence-detected", "E-P18-ARTIFACT-REVISION"),
    "missing-current-artifact": (False, "divergence-detected", "E-P18-ARTIFACT-MISSING"),
    "event-stream-reordered": (False, "divergence-detected", "E-P18-EVENT-ORDER"),
    "acknowledgement-stream-reordered": (False, "divergence-detected", "E-P18-ACK-ORDER"),
    "event-chain-head-mismatch": (False, "divergence-detected", "E-P18-CHAIN-EVENT-HEAD"),
    "acknowledgement-chain-head-mismatch": (False, "divergence-detected", "E-P18-CHAIN-ACK-HEAD"),
    "status-inheritance-injection": (False, "divergence-detected", "E-P18-STATUS-INHERITANCE"),
    "automatic-release-mutation": (False, "divergence-detected", "E-P18-AUTOMATIC-MUTATION"),
    "live-activation": (False, "divergence-detected", "E-P18-LIVE-FROZEN"),
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def non_mutating(value: Any) -> bool:
    return isinstance(value, Mapping) and all(
        value.get(key) is False
        for key in ("automatic_status_change", "automatic_release_action", "repository_mutation")
    )


def main() -> int:
    errors: list[str] = []
    errors.extend(reconciliation.check_outputs(reconciliation.build_outputs()))
    release = release_record.build_release()
    errors.extend(release_record.check(release))

    required = (
        reconciliation.REPORT_PATH,
        reconciliation.CHECKPOINT_PATH,
        reconciliation.RECOVERY_PATH,
        RELEASE_PATH,
        REPORT_DOC_PATH,
        WORKFLOW_PATH,
        TEST_PATH,
    )
    for path in required:
        if not path.is_file():
            errors.append(f"missing Phase 18 artifact: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    report = load_json(reconciliation.REPORT_PATH)
    checkpoint = load_json(reconciliation.CHECKPOINT_PATH)
    recovery = load_json(reconciliation.RECOVERY_PATH)
    release_file = load_json(RELEASE_PATH)

    expected_summary = {
        "event_count": 2,
        "acknowledgement_count": 2,
        "reconciled_count": 2,
        "unacknowledged_count": 0,
        "orphan_acknowledgement_count": 0,
        "stale_artifact_reference_count": 0,
        "action_mismatch_count": 0,
        "decision": "reconciled-no-mutation",
    }
    if report.get("contract") != reconciliation.REPORT_CONTRACT:
        errors.append("reconciliation report contract is incorrect")
    if report.get("mode") != reconciliation.MODE or report.get("live") is not False:
        errors.append("reconciliation report must remain offline and live=false")
    if report.get("summary") != expected_summary:
        errors.append("reconciliation summary does not match the canonical exact result")
    if not non_mutating(report.get("authority")) or report.get("authority", {}).get("status_inheritance") != "prohibited":
        errors.append("reconciliation report authority boundary is incorrect")

    records = report.get("records")
    if not isinstance(records, list) or len(records) != 2:
        errors.append("reconciliation report must contain exactly two records")
    else:
        for index, record in enumerate(records):
            if record.get("sequence") != index + 1 or record.get("result") != "reconciled":
                errors.append("reconciliation record sequence or result is incorrect")
            if record.get("required_action") != ("revalidate", "block-release")[index]:
                errors.append("reconciliation record action is incorrect")
            artifacts = record.get("affected_artifacts")
            if not isinstance(artifacts, list) or len(artifacts) != 3:
                errors.append("each reconciliation record must pin three artifacts")
            else:
                for artifact in artifacts:
                    if artifact.get("acknowledged_revision") != 1 or artifact.get("current_revision") != 1:
                        errors.append("reconciled artifact revisions must remain exact at revision 1")
                    if artifact.get("pedagogical_status") != "reviewed" or artifact.get("release_status") != "draft":
                        errors.append("Principia status fields changed during reconciliation")

    source = report.get("source", {})
    expected_source = {
        "phase17_candidate_head_commit": reconciliation.PHASE17_HEAD,
        "phase17_merge_commit": reconciliation.PHASE17_MERGE,
        "phase17_finalization_merge_commit": reconciliation.PHASE17_FINALIZATION_MERGE,
        "events_sha256": reconciliation.sha256_file(reconciliation.EVENTS_PATH),
        "acknowledgements_sha256": reconciliation.sha256_file(reconciliation.ACKS_PATH),
        "chain_sha256": reconciliation.sha256_file(reconciliation.CHAIN_PATH),
        "phase17_postmerge_sha256": reconciliation.sha256_file(reconciliation.PHASE17_POSTMERGE_PATH),
    }
    for key, value in expected_source.items():
        if source.get(key) != value:
            errors.append(f"reconciliation source {key} must equal {value}")

    if checkpoint.get("contract") != reconciliation.CHECKPOINT_CONTRACT:
        errors.append("reconciliation checkpoint contract is incorrect")
    if checkpoint.get("decision") != "reconciled-no-mutation" or checkpoint.get("live") is not False:
        errors.append("reconciliation checkpoint boundary is incorrect")
    if checkpoint.get("report_sha256") != reconciliation.sha256_document(report):
        errors.append("reconciliation checkpoint does not pin the exact report")
    if checkpoint.get("next_expected_event_sequence") != 3 or checkpoint.get("next_expected_acknowledgement_sequence") != 3:
        errors.append("reconciliation checkpoint next sequences are incorrect")

    scenarios = recovery.get("scenarios")
    observed = {
        item["scenario_id"]: (item.get("accepted"), item.get("outcome"), item.get("error_code"))
        for item in scenarios or []
        if isinstance(item, Mapping) and isinstance(item.get("scenario_id"), str)
    }
    if recovery.get("contract") != reconciliation.RECOVERY_CONTRACT or observed != EXPECTED_RECOVERY:
        errors.append("reconciliation recovery outcomes differ from the canonical matrix")
    if not non_mutating(recovery.get("authority")) or recovery.get("live") is not False:
        errors.append("reconciliation recovery must remain non-mutating and live=false")

    if release_file != release:
        errors.append("candidate release record differs from deterministic output")
    if release_file.get("state") != "offline-reconciliation-simulation-candidate":
        errors.append("candidate release state is incorrect")
    if release_file.get("mode") != reconciliation.MODE or release_file.get("live") is not False:
        errors.append("candidate release must remain offline and live=false")
    validation = release_file.get("validation")
    if not isinstance(validation, Mapping) or validation.get("status") != "pending" or validation.get("pull_request") is not None or validation.get("tested_head_commit") is not None:
        errors.append("immutable candidate record must remain pending and non-self-referential")

    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "Phase 18 result — Offline Reconciliation Simulation",
        "offline-reconciliation-simulation-validated",
        "mode: offline-reconciliation-simulation",
        "live: false",
        "reconciled-no-mutation",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 18 marker: {marker}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    if "contents: read" not in workflow:
        errors.append("Phase 18 workflow must use contents: read")
    for forbidden in (
        "contents: write",
        "git push",
        "git commit",
        "pull_request_target",
        "repository: Rhodan-lab/Atlas",
        "curl ",
        "wget ",
    ):
        if forbidden in workflow:
            errors.append(f"Phase 18 workflow contains prohibited operation: {forbidden}")

    if errors:
        return fail(errors)
    print(
        "Phase 18 passed: exact event/ack reconciliation, current artifact revisions, digest-bound "
        "checkpoint, deterministic divergence matrix, separate status authority, and live=false."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("Phase 18 reconciliation errors:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
