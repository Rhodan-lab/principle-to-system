#!/usr/bin/env python3
"""Validate the Phase 17 offline lifecycle-event protocol candidate."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Mapping

from generate_phase17_offline_event_protocol import (
    ACKS_PATH,
    ARTIFACT_IDS,
    ATLAS_GOVERNANCE_MERGE,
    ATLAS_IMPLEMENTATION_MERGE,
    CHAIN_PATH,
    EVENTS_PATH,
    RECOVERY_PATH,
    ROOT,
    SOURCE_RECEIPT_PATH,
    SOURCE_RECEIPT_SHA256,
    check_outputs,
    sha256_document,
    sha256_file,
)

RELEASE_PATH = ROOT / "release" / "phase-17-offline-event-protocol.json"
REPORT_PATH = ROOT / "reports" / "phase-17-offline-event-protocol.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-17-offline-event-protocol.yml"
PROJECT_STATE_PATH = ROOT / "PROJECT_STATE.md"

PROHIBITED_STATUS_KEYS = {
    "status",
    "pedagogical_status",
    "release_status",
    "knowledge_status",
    "atlas_status",
    "review_status",
}
EXPECTED_TRANSITIONS = (
    ("concept:en:feedback", 1, "current", "deprecated", "revalidate"),
    (
        "claim:en:model-oscillation-does-not-prove-real-system",
        1,
        "current",
        "retracted",
        "block-release",
    ),
)
EXPECTED_RECOVERY = {
    "duplicate-event-replay": (True, "idempotent-noop", None),
    "stale-event-sequence": (False, "rejected", "E-P17-EVENT-SEQUENCE"),
    "skipped-event-sequence": (False, "rejected", "E-P17-EVENT-SEQUENCE"),
    "wrong-event-predecessor": (False, "rejected", "E-P17-EVENT-PREVIOUS-DIGEST"),
    "event-digest-corruption": (False, "rejected", "E-P17-EVENT-DIGEST"),
    "unknown-subject-revision": (False, "rejected", "E-P17-SUBJECT-REVISION"),
    "status-inheritance-injection": (False, "rejected", "E-P17-STATUS-INHERITANCE"),
    "live-activation": (False, "rejected", "E-P17-LIVE-FROZEN"),
    "valid-next-event": (True, "accepted-recovery-checkpoint", None),
    "ack-wrong-event-digest": (False, "rejected", "E-P17-ACK-EVENT-DIGEST"),
    "ack-out-of-order": (False, "rejected", "E-P17-ACK-SEQUENCE"),
    "ack-action-weakening": (False, "rejected", "E-P17-ACK-ACTION"),
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def find_prohibited_status(value: Any, path: str = "$") -> str | None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            if key_text in PROHIBITED_STATUS_KEYS:
                return f"{path}.{key_text}"
            found = find_prohibited_status(item, f"{path}.{key_text}")
            if found:
                return found
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found = find_prohibited_status(item, f"{path}[{index}]")
            if found:
                return found
    return None


def validate_authority(value: Any, code: str) -> None:
    if not isinstance(value, Mapping):
        raise ValueError(code)
    if any(
        value.get(key) is not False
        for key in (
            "automatic_status_change",
            "automatic_release_action",
            "repository_mutation",
        )
    ):
        raise ValueError(code)


def validate_event_stream(stream: Mapping[str, Any]) -> list[dict[str, Any]]:
    if stream.get("contract") != "principia-atlas-offline-lifecycle-event-stream/0.1":
        raise ValueError("E-P17-EVENT-STREAM-CONTRACT")
    if stream.get("mode") != "offline-event-protocol" or stream.get("live") is not False:
        raise ValueError("E-P17-LIVE-FROZEN")
    validate_authority(stream.get("authority"), "E-P17-EVENT-AUTHORITY")

    source = stream.get("source_receipt")
    if not isinstance(source, Mapping):
        raise ValueError("E-P17-SOURCE-RECEIPT")
    if source.get("path") != SOURCE_RECEIPT_PATH.relative_to(ROOT).as_posix():
        raise ValueError("E-P17-SOURCE-RECEIPT")
    if source.get("sha256") != SOURCE_RECEIPT_SHA256 or source.get("sequence") != 1:
        raise ValueError("E-P17-SOURCE-RECEIPT")

    entries = stream.get("events")
    if not isinstance(entries, list) or len(entries) != 2:
        raise ValueError("E-P17-EVENT-COUNT")

    events: list[dict[str, Any]] = []
    previous_digest: str | None = None
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            raise ValueError("E-P17-EVENT-SHAPE")
        event = entry.get("event")
        digest = entry.get("event_sha256")
        if not isinstance(event, dict) or not isinstance(digest, str):
            raise ValueError("E-P17-EVENT-SHAPE")
        if sha256_document(event) != digest:
            raise ValueError("E-P17-EVENT-DIGEST")
        if event.get("contract") != "principia-atlas-offline-lifecycle-event/0.1":
            raise ValueError("E-P17-EVENT-CONTRACT")
        if event.get("mode") != "offline-event-protocol" or event.get("live") is not False:
            raise ValueError("E-P17-LIVE-FROZEN")
        if event.get("fixture_kind") != "bounded-synthetic":
            raise ValueError("E-P17-FIXTURE-KIND")
        if event.get("source_repository") != "Rhodan-lab/Atlas":
            raise ValueError("E-P17-EVENT-SOURCE")
        baseline = event.get("source_baseline")
        expected_baseline = {
            "implementation_merge_commit": ATLAS_IMPLEMENTATION_MERGE,
            "governance_merge_commit": ATLAS_GOVERNANCE_MERGE,
            "mode": "importer-candidate",
            "live": False,
        }
        if not isinstance(baseline, Mapping) or dict(baseline) != expected_baseline:
            raise ValueError("E-P17-EVENT-SOURCE")
        if event.get("sequence") != index + 1:
            raise ValueError("E-P17-EVENT-SEQUENCE")
        if event.get("previous_event_sha256") != previous_digest:
            raise ValueError("E-P17-EVENT-PREVIOUS-DIGEST")
        prohibited = find_prohibited_status(event)
        if prohibited:
            raise ValueError(f"E-P17-STATUS-INHERITANCE:{prohibited}")
        event_authority = event.get("authority")
        validate_authority(event_authority, "E-P17-EVENT-AUTHORITY")
        if not isinstance(event_authority, Mapping) or event_authority.get("status_inheritance") != "prohibited":
            raise ValueError("E-P17-STATUS-INHERITANCE")

        subject = event.get("subject")
        transition = event.get("transition")
        if not isinstance(subject, Mapping) or not isinstance(transition, Mapping):
            raise ValueError("E-P17-EVENT-PAYLOAD")
        expected = EXPECTED_TRANSITIONS[index]
        if subject.get("id") != expected[0] or subject.get("revision") != expected[1]:
            raise ValueError("E-P17-SUBJECT-REVISION")
        if subject.get("key") != f"{expected[0]}@{expected[1]}":
            raise ValueError("E-P17-SUBJECT-REVISION")
        if transition.get("from") != expected[2] or transition.get("to") != expected[3]:
            raise ValueError("E-P17-EVENT-TRANSITION")

        previous_digest = digest
        events.append(event)
    return events


def validate_acknowledgements(
    stream: Mapping[str, Any],
    event_stream: Mapping[str, Any],
) -> list[dict[str, Any]]:
    if stream.get("contract") != "principia-atlas-offline-lifecycle-acknowledgement-stream/0.1":
        raise ValueError("E-P17-ACK-STREAM-CONTRACT")
    if stream.get("mode") != "offline-event-protocol" or stream.get("live") is not False:
        raise ValueError("E-P17-LIVE-FROZEN")
    validate_authority(stream.get("authority"), "E-P17-ACK-AUTHORITY")

    event_entries = event_stream.get("events")
    entries = stream.get("acknowledgements")
    if not isinstance(event_entries, list) or not isinstance(entries, list) or len(entries) != 2:
        raise ValueError("E-P17-ACK-COUNT")

    expected_artifacts = [{"id": artifact_id, "revision": 1} for artifact_id in ARTIFACT_IDS]
    acknowledgements: list[dict[str, Any]] = []
    previous_digest: str | None = None
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            raise ValueError("E-P17-ACK-SHAPE")
        acknowledgement = entry.get("acknowledgement")
        digest = entry.get("acknowledgement_sha256")
        if not isinstance(acknowledgement, dict) or not isinstance(digest, str):
            raise ValueError("E-P17-ACK-SHAPE")
        if sha256_document(acknowledgement) != digest:
            raise ValueError("E-P17-ACK-DIGEST")
        if acknowledgement.get("contract") != "principia-atlas-offline-lifecycle-acknowledgement/0.1":
            raise ValueError("E-P17-ACK-CONTRACT")
        if acknowledgement.get("mode") != "offline-event-protocol" or acknowledgement.get("live") is not False:
            raise ValueError("E-P17-LIVE-FROZEN")
        if acknowledgement.get("sequence") != index + 1:
            raise ValueError("E-P17-ACK-SEQUENCE")
        if acknowledgement.get("previous_acknowledgement_sha256") != previous_digest:
            raise ValueError("E-P17-ACK-SEQUENCE")
        event_entry = event_entries[index]
        if acknowledgement.get("event_id") != event_entry.get("event", {}).get("event_id"):
            raise ValueError("E-P17-ACK-EVENT-DIGEST")
        if acknowledgement.get("event_sha256") != event_entry.get("event_sha256"):
            raise ValueError("E-P17-ACK-EVENT-DIGEST")
        if acknowledgement.get("required_action") != EXPECTED_TRANSITIONS[index][4]:
            raise ValueError("E-P17-ACK-ACTION")
        if acknowledgement.get("accepted") is not True:
            raise ValueError("E-P17-ACK-RESULT")
        if acknowledgement.get("outcome") != "recorded-no-mutation":
            raise ValueError("E-P17-ACK-RESULT")
        if acknowledgement.get("affected_artifacts") != expected_artifacts:
            raise ValueError("E-P17-ACK-DEPENDENTS")
        if acknowledgement.get("status_inheritance") != "prohibited":
            raise ValueError("E-P17-STATUS-INHERITANCE")
        validate_authority(acknowledgement, "E-P17-ACK-AUTHORITY")
        prohibited = find_prohibited_status(acknowledgement)
        if prohibited:
            raise ValueError(f"E-P17-STATUS-INHERITANCE:{prohibited}")
        previous_digest = digest
        acknowledgements.append(acknowledgement)
    return acknowledgements


def validate_chain(
    chain: Mapping[str, Any],
    event_stream: Mapping[str, Any],
    acknowledgement_stream: Mapping[str, Any],
) -> None:
    if chain.get("contract") != "principia-atlas-offline-event-protocol-chain/0.1":
        raise ValueError("E-P17-CHAIN-CONTRACT")
    if chain.get("mode") != "offline-event-protocol" or chain.get("live") is not False:
        raise ValueError("E-P17-LIVE-FROZEN")
    validate_authority(chain.get("authority"), "E-P17-CHAIN-AUTHORITY")

    events = event_stream["events"]
    acknowledgements = acknowledgement_stream["acknowledgements"]
    if chain.get("event_head_sequence") != 2 or chain.get("event_head_sha256") != events[-1]["event_sha256"]:
        raise ValueError("E-P17-CHAIN-EVENT-HEAD")
    if (
        chain.get("acknowledgement_head_sequence") != 2
        or chain.get("acknowledgement_head_sha256") != acknowledgements[-1]["acknowledgement_sha256"]
    ):
        raise ValueError("E-P17-CHAIN-ACK-HEAD")
    links = chain.get("links")
    if not isinstance(links, list) or len(links) != 2:
        raise ValueError("E-P17-CHAIN-LINKS")
    for index, link in enumerate(links):
        if not isinstance(link, Mapping):
            raise ValueError("E-P17-CHAIN-LINKS")
        event_entry = events[index]
        ack_entry = acknowledgements[index]
        expected = {
            "sequence": index + 1,
            "event_id": event_entry["event"]["event_id"],
            "event_sha256": event_entry["event_sha256"],
            "previous_event_sha256": event_entry["event"]["previous_event_sha256"],
            "acknowledgement_id": ack_entry["acknowledgement"]["acknowledgement_id"],
            "acknowledgement_sha256": ack_entry["acknowledgement_sha256"],
            "previous_acknowledgement_sha256": ack_entry["acknowledgement"][
                "previous_acknowledgement_sha256"
            ],
        }
        if dict(link) != expected:
            raise ValueError("E-P17-CHAIN-LINKS")


def validate_recovery(
    matrix: Mapping[str, Any],
    event_stream: Mapping[str, Any],
    acknowledgement_stream: Mapping[str, Any],
) -> None:
    if matrix.get("contract") != "principia-atlas-offline-event-protocol-recovery/0.1":
        raise ValueError("E-P17-RECOVERY-CONTRACT")
    if matrix.get("mode") != "offline-event-protocol" or matrix.get("live") is not False:
        raise ValueError("E-P17-LIVE-FROZEN")
    validate_authority(matrix.get("authority"), "E-P17-RECOVERY-AUTHORITY")
    scenarios = matrix.get("scenarios")
    if not isinstance(scenarios, list):
        raise ValueError("E-P17-RECOVERY-SCENARIOS")
    actual = {
        scenario.get("scenario_id"): (
            scenario.get("accepted"),
            scenario.get("outcome"),
            scenario.get("error_code"),
        )
        for scenario in scenarios
        if isinstance(scenario, Mapping)
    }
    if actual != EXPECTED_RECOVERY:
        raise ValueError("E-P17-RECOVERY-SCENARIOS")


def validate_negative_paths(
    event_stream: Mapping[str, Any],
    acknowledgement_stream: Mapping[str, Any],
) -> None:
    duplicate = copy.deepcopy(event_stream)
    duplicate["events"][1]["event"]["sequence"] = 1
    try:
        validate_event_stream(duplicate)
    except ValueError as exc:
        if str(exc) != "E-P17-EVENT-DIGEST":
            raise
    else:
        raise ValueError("E-P17-NEGATIVE-EVENT")

    weakened = copy.deepcopy(acknowledgement_stream)
    weakened["acknowledgements"][1]["acknowledgement"]["required_action"] = "inspect"
    try:
        validate_acknowledgements(weakened, event_stream)
    except ValueError as exc:
        if str(exc) != "E-P17-ACK-DIGEST":
            raise
    else:
        raise ValueError("E-P17-NEGATIVE-ACK")


def validate_records(errors: list[str]) -> None:
    required = (
        EVENTS_PATH,
        ACKS_PATH,
        CHAIN_PATH,
        RECOVERY_PATH,
        RELEASE_PATH,
        REPORT_PATH,
        WORKFLOW_PATH,
        PROJECT_STATE_PATH,
    )
    for path in required:
        if not path.is_file():
            errors.append(f"missing Phase 17 file: {path.relative_to(ROOT)}")
    if errors:
        return

    if sha256_file(SOURCE_RECEIPT_PATH) != SOURCE_RECEIPT_SHA256:
        errors.append("Phase 17 source receipt digest does not match the validated Phase 16 receipt")
        return

    try:
        event_stream = load_json(EVENTS_PATH)
        acknowledgement_stream = load_json(ACKS_PATH)
        validate_event_stream(event_stream)
        validate_acknowledgements(acknowledgement_stream, event_stream)
        validate_chain(load_json(CHAIN_PATH), event_stream, acknowledgement_stream)
        validate_recovery(load_json(RECOVERY_PATH), event_stream, acknowledgement_stream)
        validate_negative_paths(event_stream, acknowledgement_stream)
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(str(exc))

    release = load_json(RELEASE_PATH)
    expected_release = {
        "contract": "principia-offline-event-protocol/0.1",
        "phase": 17,
        "state": "offline-event-protocol-candidate",
        "mode": "offline-event-protocol",
        "live": False,
    }
    for key, expected in expected_release.items():
        if release.get(key) != expected:
            errors.append(f"release/phase-17 record has invalid {key}")
    if release.get("source_phase16_merge_commit") != "44410d47d318c5aaedb7716e4ef3bdefae09b442":
        errors.append("release/phase-17 source Phase 16 merge is not pinned")
    validation = release.get("validation")
    if not isinstance(validation, Mapping):
        errors.append("release/phase-17 validation record is missing")
    elif validation.get("status") != "pending" or validation.get("tested_head_commit") is not None:
        errors.append("release/phase-17 candidate must remain pending before exact-head validation")
    try:
        validate_authority(release.get("authority"), "release/phase-17 authority is invalid")
    except ValueError as exc:
        errors.append(str(exc))
    if release.get("live_activation_permitted") is not False:
        errors.append("release/phase-17 must not permit live activation")

    artifact_paths = release.get("artifacts")
    if not isinstance(artifact_paths, Mapping):
        errors.append("release/phase-17 artifact pins are missing")
    else:
        expected_paths = {
            "events": EVENTS_PATH,
            "acknowledgements": ACKS_PATH,
            "chain": CHAIN_PATH,
            "recovery": RECOVERY_PATH,
        }
        for key, path in expected_paths.items():
            value = artifact_paths.get(key)
            if not isinstance(value, Mapping):
                errors.append(f"release/phase-17 missing {key} artifact pin")
                continue
            if value.get("path") != path.relative_to(ROOT).as_posix():
                errors.append(f"release/phase-17 {key} path is invalid")
            if value.get("sha256") != sha256_file(path):
                errors.append(f"release/phase-17 {key} digest is invalid")

    state = PROJECT_STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "| 17 | Offline event-protocol candidate | Merged and validated through PR #22 |",
        "offline-event-protocol-validated",
        "mode: offline-event-protocol",
        "live: false",
        "Historical Phase 17 candidate marker: `exact-head validation pending`",
        "44410d47d318c5aaedb7716e4ef3bdefae09b442",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 17 marker: {marker}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        "principia-atlas-offline-lifecycle-event/0.1",
        "principia-atlas-offline-lifecycle-acknowledgement/0.1",
        "bounded-synthetic",
        "No network synchronization",
        "live: false",
    ):
        if marker not in report:
            errors.append(f"Phase 17 report missing marker: {marker}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    if "contents: read" not in workflow:
        errors.append("Phase 17 workflow must use contents: read")
    forbidden = (
        "contents" + ": write",
        "git " + "push",
        "git " + "commit",
        "pull_request" + "_target",
        "repository: Rhodan-lab/Atlas",
        "curl ",
        "wget ",
    )
    for token in forbidden:
        if token in workflow:
            errors.append(f"Phase 17 workflow contains forbidden token: {token}")


def main() -> int:
    errors: list[str] = []
    if check_outputs() != 0:
        errors.append("Phase 17 deterministic outputs are stale")
    validate_records(errors)
    if errors:
        print("Phase 17 offline event-protocol errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "Phase 17 passed: two digest-bound synthetic lifecycle events, exact acknowledgements, "
        "ordered chains, replay and recovery policy, separated status authority, and live=false."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
