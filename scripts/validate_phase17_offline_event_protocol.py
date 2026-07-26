#!/usr/bin/env python3
"""Validate the Phase 17 digest-bound offline lifecycle event protocol."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping

import generate_phase17_offline_event_protocol as protocol

ROOT = Path(__file__).resolve().parent.parent
RELEASE_PATH = ROOT / "release" / "phase-17-offline-event-protocol.json"
REPORT_PATH = ROOT / "reports" / "phase-17-offline-event-protocol.md"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "validate-phase-17-offline-event-protocol.yml"
TEST_PATH = ROOT / "software" / "tests" / "test_phase17_offline_event_protocol.py"
STATE_PATH = ROOT / "PROJECT_STATE.md"

EXPECTED_SCENARIOS = {
    "duplicate-exact-replay": (True, "idempotent-noop", None),
    "same-sequence-different-digest": (False, "reject", "E-P17-EQUIVOCATION"),
    "stale-sequence": (False, "reject", "E-P17-STALE-SEQUENCE"),
    "skipped-sequence": (False, "reject", "E-P17-SKIPPED-SEQUENCE"),
    "wrong-predecessor": (False, "reject", "E-P17-PREDECESSOR"),
    "wrong-receipt-chain-head": (False, "reject", "E-P17-RECEIPT-HEAD"),
    "unknown-entity-state": (False, "reject", "E-P17-ENTITY-STATE"),
    "affected-set-mismatch": (False, "reject", "E-P17-AFFECTED-SET"),
    "status-inheritance-injection": (False, "reject", "E-P17-STATUS-INHERITANCE"),
    "automatic-release-mutation": (False, "reject", "E-P17-AUTOMATIC-MUTATION"),
    "live-activation": (False, "reject", "E-P17-LIVE-FROZEN"),
    "valid-next-event": (True, "accept", None),
    "ack-event-digest-mismatch": (False, "reject", "E-P17-ACK-DIGEST"),
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def authority_is_non_mutating(value: Any) -> bool:
    return isinstance(value, Mapping) and all(
        value.get(key) is False
        for key in ("automatic_status_change", "automatic_release_action", "repository_mutation")
    )


def main() -> int:
    errors: list[str] = []
    outputs = protocol.build_outputs()
    errors.extend(protocol.check_outputs(outputs))

    required_paths = (
        protocol.EVENT_PATH,
        protocol.ACK_PATH,
        protocol.LOG_PATH,
        protocol.RECOVERY_PATH,
        RELEASE_PATH,
        REPORT_PATH,
        WORKFLOW_PATH,
        TEST_PATH,
        Path(__file__),
    )
    for path in required_paths:
        if not path.is_file():
            errors.append(f"missing Phase 17 artifact: {path.relative_to(ROOT)}")

    if errors:
        print("Phase 17 event-protocol errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    event = load_json(protocol.EVENT_PATH)
    ack = load_json(protocol.ACK_PATH)
    log = load_json(protocol.LOG_PATH)
    recovery = load_json(protocol.RECOVERY_PATH)
    release = load_json(RELEASE_PATH)

    if event.get("contract") != protocol.EVENT_CONTRACT:
        errors.append("event contract is incorrect")
    if event.get("mode") != protocol.MODE or event.get("live") is not False:
        errors.append("event must remain offline-event-protocol and live=false")
    if event.get("sequence") != 1 or event.get("previous_event_sha256") is not None:
        errors.append("first event must be sequence 1 with no event predecessor")
    checkpoint = event.get("source_checkpoint")
    if not isinstance(checkpoint, Mapping):
        errors.append("event source checkpoint is missing")
    else:
        expected_checkpoint = {
            "phase16_pull_request": 20,
            "phase16_merge_commit": protocol.PHASE16_MERGE,
            "phase16_record_pull_request": 21,
            "phase16_record_merge_commit": protocol.PHASE16_RECORD_MERGE,
            "receipt_chain_head_sequence": 1,
            "receipt_chain_head_sha256": "af529bc6c866be889e6a0b552dffedd81a5e46466cdae08e234472031617b562",
            "atlas_implementation_merge_commit": protocol.ATLAS_IMPLEMENTATION_MERGE,
            "atlas_governance_merge_commit": protocol.ATLAS_GOVERNANCE_MERGE,
        }
        for key, value in expected_checkpoint.items():
            if checkpoint.get(key) != value:
                errors.append(f"event source checkpoint {key} must equal {value}")
        if checkpoint.get("phase16_release_sha256") != protocol.sha256_file(protocol.PHASE16_RELEASE_PATH):
            errors.append("event does not pin the exact Phase 16 release bytes")

    entity = event.get("atlas_entity")
    if not isinstance(entity, Mapping) or dict(entity) != {
        "id": "concept:en:feedback",
        "revision": 1,
        "lifecycle_status": "deprecated",
        "staleness": "current",
    }:
        errors.append("event must represent the pinned deprecated feedback concept state")
    affected = event.get("affected_principia_artifacts")
    if not isinstance(affected, list) or len(affected) != 3:
        errors.append("event must affect the exact three Phase 16 artifacts")
    else:
        observed_ids = [item.get("artifact_id") for item in affected if isinstance(item, Mapping)]
        expected_ids = [
            "principia:failure-pattern:feedback-instability",
            "principia:investigation:room-cooling",
            "principia:system-dossier:refrigerator",
        ]
        if observed_ids != expected_ids:
            errors.append("event affected-artifact order or identity is incorrect")
        for item in affected:
            if not isinstance(item, Mapping) or item.get("effective_action") != "revalidate":
                errors.append("deprecated feedback event must report revalidate for every affected artifact")
                break
    if not authority_is_non_mutating(event.get("authority")):
        errors.append("event authority must prohibit automatic mutations")
    if isinstance(event.get("authority"), Mapping) and event["authority"].get("status_inheritance") != "prohibited":
        errors.append("event must prohibit status inheritance")

    try:
        protocol.validate_ack(ack, event)
    except protocol.ProtocolError as exc:
        errors.append(f"acknowledgement validation failed: {exc.code}")
    event_sha = protocol.sha256_document(event)
    ack_sha = protocol.sha256_document(ack)
    if log.get("contract") != protocol.LOG_CONTRACT or log.get("live") is not False:
        errors.append("event log contract or live boundary is incorrect")
    if log.get("head_sequence") != 1 or log.get("head_event_sha256") != event_sha:
        errors.append("event log head does not match the committed event")
    if log.get("head_ack_sha256") != ack_sha:
        errors.append("event log head does not match the committed acknowledgement")
    entries = log.get("entries")
    if not isinstance(entries, list) or len(entries) != 1:
        errors.append("event log must contain exactly the first committed event")
    elif entries[0].get("event_sha256") != event_sha or entries[0].get("ack_sha256") != ack_sha:
        errors.append("event log entry digests are incorrect")

    if recovery.get("contract") != protocol.RECOVERY_CONTRACT or recovery.get("live") is not False:
        errors.append("recovery matrix contract or live boundary is incorrect")
    scenarios = recovery.get("scenarios")
    if not isinstance(scenarios, list):
        errors.append("recovery scenarios are missing")
    else:
        observed: dict[str, tuple[Any, Any, Any]] = {}
        for scenario in scenarios:
            if isinstance(scenario, Mapping) and isinstance(scenario.get("scenario_id"), str):
                observed[scenario["scenario_id"]] = (
                    scenario.get("accepted"),
                    scenario.get("result"),
                    scenario.get("error_code"),
                )
        if observed != EXPECTED_SCENARIOS:
            errors.append("recovery scenario outcomes do not match the canonical Phase 17 matrix")
    if not authority_is_non_mutating(recovery.get("authority")):
        errors.append("recovery matrix must prohibit automatic mutations")

    if release.get("contract") != "principia-offline-event-protocol-candidate/0.3":
        errors.append("Phase 17 release contract is incorrect")
    if release.get("phase") != 17 or release.get("state") != "offline-event-protocol-validated":
        errors.append("Phase 17 release state is incorrect")
    if release.get("mode") != protocol.MODE or release.get("live") is not False:
        errors.append("Phase 17 release must remain offline and live=false")
    if release.get("live_activation_permitted") is not False:
        errors.append("Phase 17 must not permit live activation")
    if release.get("next_gate") != "offline-event-stream-scaling":
        errors.append("Phase 17 next gate must remain offline-event-stream-scaling")
    if not authority_is_non_mutating(release.get("authority")):
        errors.append("Phase 17 release authority must prohibit automatic mutations")
    digests = release.get("digests")
    expected_digests = {
        "event": protocol.sha256_file(protocol.EVENT_PATH),
        "ack": protocol.sha256_file(protocol.ACK_PATH),
        "event_log": protocol.sha256_file(protocol.LOG_PATH),
        "recovery_matrix": protocol.sha256_file(protocol.RECOVERY_PATH),
    }
    if not isinstance(digests, Mapping):
        errors.append("Phase 17 release digests are missing")
    else:
        for key, value in expected_digests.items():
            if digests.get(key) != value:
                errors.append(f"Phase 17 release digest {key} must equal {value}")

    state = STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "Phase 17 — Offline Event-Protocol Candidate",
        "offline-event-protocol-validated",
        "mode: offline-event-protocol",
        "live: false",
        "digest-bound lifecycle event",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 17 marker: {marker}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    if "contents: read" not in workflow:
        errors.append("Phase 17 workflow must use contents: read")
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
            errors.append(f"Phase 17 workflow contains prohibited operation: {forbidden}")

    if errors:
        print("Phase 17 event-protocol errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Phase 17 passed: digest-bound lifecycle event, exact acknowledgement, append-only log, "
        "replay/order recovery matrix, separate status authority, and live=false."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
