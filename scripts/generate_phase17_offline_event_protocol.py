#!/usr/bin/env python3
"""Generate or verify the Phase 17 digest-bound offline event protocol evidence."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
PILOT_ROOT = ROOT / "integration" / "principia-atlas" / "pilot"
SOURCE_CHAIN_PATH = PILOT_ROOT / "thermal-control.receipt-chain.v02.json"
SOURCE_MATRIX_PATH = PILOT_ROOT / "thermal-control.lifecycle-matrix.v02.json"
PHASE16_RELEASE_PATH = ROOT / "release" / "phase-16-offline-multi-artifact-pilot.json"
EVENT_PATH = PILOT_ROOT / "thermal-control.lifecycle-event.v03.json"
ACK_PATH = PILOT_ROOT / "thermal-control.lifecycle-event-ack.v03.json"
LOG_PATH = PILOT_ROOT / "thermal-control.event-log.v03.json"
RECOVERY_PATH = PILOT_ROOT / "thermal-control.event-recovery-matrix.v03.json"

EVENT_CONTRACT = "principia-atlas-offline-lifecycle-event/0.3"
ACK_CONTRACT = "principia-atlas-offline-event-ack/0.3"
LOG_CONTRACT = "principia-atlas-offline-event-log/0.3"
RECOVERY_CONTRACT = "principia-atlas-offline-event-recovery/0.3"
PROTOCOL_ID = "principia-atlas:offline-event-protocol:thermal-control"
MODE = "offline-event-protocol"
PHASE16_PR = 20
PHASE16_MERGE = "c493bf879a7945f9991e13592d42424138a0879b"
PHASE16_RECORD_PR = 21
PHASE16_RECORD_MERGE = "44410d47d318c5aaedb7716e4ef3bdefae09b442"
ATLAS_IMPLEMENTATION_MERGE = "1cc4aec6908a8703a7f505478329c633a23b4ef9"
ATLAS_GOVERNANCE_MERGE = "9370cc746e9756e433ac3772d56d079c9803b144"

PROHIBITED_PRINCIPIA_STATUS_KEYS = {
    "pedagogical_status",
    "release_status",
    "principia_status",
    "principia_release_status",
    "knowledge_status_inheritance",
}


@dataclass(frozen=True)
class ProtocolError(ValueError):
    code: str

    def __str__(self) -> str:
        return self.code


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def render_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_document(value: Mapping[str, Any]) -> str:
    return sha256_bytes(render_json(value).encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def find_prohibited_status(value: Any, path: str = "$") -> str | None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            if key_text in PROHIBITED_PRINCIPIA_STATUS_KEYS:
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


def scenario_by_id(matrix: Mapping[str, Any], scenario_id: str) -> dict[str, Any]:
    scenarios = matrix.get("scenarios")
    if not isinstance(scenarios, list):
        raise ValueError("E-P17-MATRIX-SHAPE")
    for scenario in scenarios:
        if isinstance(scenario, dict) and scenario.get("scenario_id") == scenario_id:
            return scenario
    raise ValueError(f"E-P17-SCENARIO-MISSING:{scenario_id}")


def validate_sources(
    chain: Mapping[str, Any],
    matrix: Mapping[str, Any],
    release: Mapping[str, Any],
) -> None:
    if chain.get("contract") != "principia-atlas-offline-receipt-chain/0.2":
        raise ValueError("E-P17-CHAIN-CONTRACT")
    if chain.get("head_sequence") != 1 or chain.get("live") is not False:
        raise ValueError("E-P17-CHAIN-STATE")
    if chain.get("head_receipt_sha256") != "af529bc6c866be889e6a0b552dffedd81a5e46466cdae08e234472031617b562":
        raise ValueError("E-P17-CHAIN-HEAD")
    if matrix.get("contract") != "principia-atlas-offline-multi-impact-matrix/0.2":
        raise ValueError("E-P17-MATRIX-CONTRACT")
    if matrix.get("live") is not False:
        raise ValueError("E-P17-MATRIX-LIVE")
    if release.get("state") != "offline-multi-artifact-validated":
        raise ValueError("E-P17-PHASE16-STATE")
    if release.get("mode") != "offline-multi-artifact-pilot" or release.get("live") is not False:
        raise ValueError("E-P17-PHASE16-LIVE")
    principia = release.get("principia")
    if not isinstance(principia, Mapping):
        raise ValueError("E-P17-PHASE16-PROVENANCE")
    if principia.get("pull_request") != PHASE16_PR or principia.get("merge_commit") != PHASE16_MERGE:
        raise ValueError("E-P17-PHASE16-PIN")
    atlas = release.get("atlas")
    if not isinstance(atlas, Mapping):
        raise ValueError("E-P17-ATLAS-PROVENANCE")
    if (
        atlas.get("implementation_merge_commit") != ATLAS_IMPLEMENTATION_MERGE
        or atlas.get("governance_merge_commit") != ATLAS_GOVERNANCE_MERGE
        or atlas.get("live") is not False
    ):
        raise ValueError("E-P17-ATLAS-PIN")


def event_from_scenario(
    scenario: Mapping[str, Any],
    *,
    sequence: int,
    previous_event_sha256: str | None,
    chain: Mapping[str, Any],
    release: Mapping[str, Any],
) -> dict[str, Any]:
    entity = scenario.get("entity")
    dependents = scenario.get("external_dependents")
    if not isinstance(entity, Mapping) or not isinstance(dependents, list):
        raise ValueError("E-P17-SCENARIO-SHAPE")
    affected = []
    for item in dependents:
        if not isinstance(item, Mapping):
            raise ValueError("E-P17-AFFECTED-SHAPE")
        affected.append(
            {
                "artifact_id": item["artifact_id"],
                "artifact_revision": item["artifact_revision"],
                "declared_action": item["declared_action"],
                "effective_action": item["effective_action"],
                "reason": item["reason"],
            }
        )
    affected.sort(key=lambda item: (item["artifact_id"], item["artifact_revision"]))
    return {
        "contract": EVENT_CONTRACT,
        "protocol_id": PROTOCOL_ID,
        "event_id": f"principia-atlas:lifecycle-event:thermal-control:{sequence:04d}",
        "sequence": sequence,
        "previous_event_sha256": previous_event_sha256,
        "mode": MODE,
        "live": False,
        "source_checkpoint": {
            "phase16_release_path": PHASE16_RELEASE_PATH.relative_to(ROOT).as_posix(),
            "phase16_release_sha256": sha256_file(PHASE16_RELEASE_PATH),
            "phase16_pull_request": PHASE16_PR,
            "phase16_merge_commit": PHASE16_MERGE,
            "phase16_record_pull_request": PHASE16_RECORD_PR,
            "phase16_record_merge_commit": PHASE16_RECORD_MERGE,
            "receipt_chain_path": SOURCE_CHAIN_PATH.relative_to(ROOT).as_posix(),
            "receipt_chain_head_sequence": chain["head_sequence"],
            "receipt_chain_head_sha256": chain["head_receipt_sha256"],
            "atlas_implementation_merge_commit": ATLAS_IMPLEMENTATION_MERGE,
            "atlas_governance_merge_commit": ATLAS_GOVERNANCE_MERGE,
        },
        "event_type": "atlas-lifecycle-impact",
        "atlas_entity": {
            "id": entity["id"],
            "revision": entity["revision"],
            "lifecycle_status": entity["status"],
            "staleness": entity["staleness"],
        },
        "affected_principia_artifacts": affected,
        "authority": {
            "atlas_knowledge_status_authority": "Atlas",
            "principia_pedagogical_status_authority": "Principia",
            "principia_release_status_authority": "Principia",
            "status_inheritance": "prohibited",
            "automatic_status_change": False,
            "automatic_release_action": False,
            "repository_mutation": False,
        },
    }


def build_ack(event: Mapping[str, Any]) -> dict[str, Any]:
    affected = event["affected_principia_artifacts"]
    return {
        "contract": ACK_CONTRACT,
        "protocol_id": PROTOCOL_ID,
        "ack_id": f"principia-atlas:lifecycle-event-ack:thermal-control:{event['sequence']:04d}",
        "event_id": event["event_id"],
        "event_sequence": event["sequence"],
        "event_sha256": sha256_document(event),
        "mode": MODE,
        "live": False,
        "decision": "accepted-for-offline-impact-recording",
        "observed": {
            "receipt_chain_head_sha256": event["source_checkpoint"]["receipt_chain_head_sha256"],
            "atlas_entity": event["atlas_entity"],
            "affected_artifact_count": len(affected),
            "affected_artifacts_sha256": sha256_document({"items": affected}),
        },
        "authority": {
            "status_inheritance": "prohibited",
            "automatic_status_change": False,
            "automatic_release_action": False,
            "repository_mutation": False,
        },
    }


def build_log(event: Mapping[str, Any], ack: Mapping[str, Any]) -> dict[str, Any]:
    event_sha = sha256_document(event)
    ack_sha = sha256_document(ack)
    return {
        "contract": LOG_CONTRACT,
        "protocol_id": PROTOCOL_ID,
        "mode": MODE,
        "live": False,
        "source_receipt_chain_head_sha256": event["source_checkpoint"]["receipt_chain_head_sha256"],
        "entries": [
            {
                "sequence": event["sequence"],
                "previous_event_sha256": event["previous_event_sha256"],
                "event_path": EVENT_PATH.relative_to(ROOT).as_posix(),
                "event_sha256": event_sha,
                "ack_path": ACK_PATH.relative_to(ROOT).as_posix(),
                "ack_sha256": ack_sha,
                "decision": ack["decision"],
            }
        ],
        "head_sequence": event["sequence"],
        "head_event_sha256": event_sha,
        "head_ack_sha256": ack_sha,
    }


def validate_event_candidate(
    candidate: Mapping[str, Any],
    log: Mapping[str, Any],
    chain: Mapping[str, Any],
    matrix: Mapping[str, Any],
) -> str:
    if candidate.get("contract") != EVENT_CONTRACT:
        raise ProtocolError("E-P17-EVENT-CONTRACT")
    if candidate.get("protocol_id") != PROTOCOL_ID:
        raise ProtocolError("E-P17-PROTOCOL-ID")
    if candidate.get("mode") != MODE or candidate.get("live") is not False:
        raise ProtocolError("E-P17-LIVE-FROZEN")
    prohibited = find_prohibited_status(candidate)
    if prohibited:
        raise ProtocolError("E-P17-STATUS-INHERITANCE")
    authority = candidate.get("authority")
    if not isinstance(authority, Mapping) or any(
        authority.get(key) is not False
        for key in ("automatic_status_change", "automatic_release_action", "repository_mutation")
    ):
        raise ProtocolError("E-P17-AUTOMATIC-MUTATION")
    checkpoint = candidate.get("source_checkpoint")
    if not isinstance(checkpoint, Mapping):
        raise ProtocolError("E-P17-CHECKPOINT")
    if checkpoint.get("receipt_chain_head_sha256") != chain.get("head_receipt_sha256"):
        raise ProtocolError("E-P17-RECEIPT-HEAD")
    if checkpoint.get("receipt_chain_head_sequence") != chain.get("head_sequence"):
        raise ProtocolError("E-P17-RECEIPT-SEQUENCE")

    sequence = candidate.get("sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        raise ProtocolError("E-P17-SEQUENCE")
    head_sequence = int(log.get("head_sequence", 0))
    head_sha = log.get("head_event_sha256")
    candidate_sha = sha256_document(candidate)
    if sequence == head_sequence:
        entries = log.get("entries")
        if isinstance(entries, list):
            for entry in entries:
                if isinstance(entry, Mapping) and entry.get("sequence") == sequence:
                    if entry.get("event_sha256") == candidate_sha:
                        return "idempotent-noop"
                    raise ProtocolError("E-P17-EQUIVOCATION")
        raise ProtocolError("E-P17-EQUIVOCATION")
    if sequence < head_sequence:
        raise ProtocolError("E-P17-STALE-SEQUENCE")
    if sequence > head_sequence + 1:
        raise ProtocolError("E-P17-SKIPPED-SEQUENCE")
    if candidate.get("previous_event_sha256") != head_sha:
        raise ProtocolError("E-P17-PREDECESSOR")

    atlas_entity = candidate.get("atlas_entity")
    if not isinstance(atlas_entity, Mapping):
        raise ProtocolError("E-P17-ENTITY")
    scenario = None
    scenarios = matrix.get("scenarios")
    if isinstance(scenarios, list):
        for item in scenarios:
            if not isinstance(item, Mapping):
                continue
            entity = item.get("entity")
            if (
                isinstance(entity, Mapping)
                and entity.get("id") == atlas_entity.get("id")
                and entity.get("revision") == atlas_entity.get("revision")
                and entity.get("status") == atlas_entity.get("lifecycle_status")
                and entity.get("staleness") == atlas_entity.get("staleness")
            ):
                scenario = item
                break
    if scenario is None:
        raise ProtocolError("E-P17-ENTITY-STATE")
    expected_event = event_from_scenario(
        scenario,
        sequence=sequence,
        previous_event_sha256=head_sha,
        chain=chain,
        release=load_json(PHASE16_RELEASE_PATH),
    )
    if candidate.get("affected_principia_artifacts") != expected_event.get("affected_principia_artifacts"):
        raise ProtocolError("E-P17-AFFECTED-SET")
    return "accept"


def validate_ack(ack: Mapping[str, Any], event: Mapping[str, Any]) -> None:
    if ack.get("contract") != ACK_CONTRACT or ack.get("protocol_id") != PROTOCOL_ID:
        raise ProtocolError("E-P17-ACK-CONTRACT")
    if ack.get("mode") != MODE or ack.get("live") is not False:
        raise ProtocolError("E-P17-ACK-LIVE")
    if ack.get("event_id") != event.get("event_id") or ack.get("event_sequence") != event.get("sequence"):
        raise ProtocolError("E-P17-ACK-EVENT")
    if ack.get("event_sha256") != sha256_document(event):
        raise ProtocolError("E-P17-ACK-DIGEST")
    if ack.get("decision") != "accepted-for-offline-impact-recording":
        raise ProtocolError("E-P17-ACK-DECISION")
    authority = ack.get("authority")
    if not isinstance(authority, Mapping) or authority.get("status_inheritance") != "prohibited":
        raise ProtocolError("E-P17-ACK-AUTHORITY")
    if any(
        authority.get(key) is not False
        for key in ("automatic_status_change", "automatic_release_action", "repository_mutation")
    ):
        raise ProtocolError("E-P17-ACK-AUTOMATIC-MUTATION")


def outcome(candidate: Mapping[str, Any], log: Mapping[str, Any], chain: Mapping[str, Any], matrix: Mapping[str, Any]) -> dict[str, Any]:
    try:
        result = validate_event_candidate(candidate, log, chain, matrix)
        return {"accepted": True, "result": result, "error_code": None}
    except ProtocolError as exc:
        return {"accepted": False, "result": "reject", "error_code": exc.code}


def build_recovery_matrix(
    event: Mapping[str, Any],
    ack: Mapping[str, Any],
    log: Mapping[str, Any],
    chain: Mapping[str, Any],
    matrix: Mapping[str, Any],
    release: Mapping[str, Any],
) -> dict[str, Any]:
    feedback = scenario_by_id(matrix, "feedback-deprecated")
    oscillation = scenario_by_id(matrix, "oscillation-confirmed-stale")
    valid_next = event_from_scenario(
        oscillation,
        sequence=2,
        previous_event_sha256=log["head_event_sha256"],
        chain=chain,
        release=release,
    )

    scenarios: list[tuple[str, dict[str, Any]]] = []
    scenarios.append(("duplicate-exact-replay", copy.deepcopy(event)))

    equivocation = copy.deepcopy(event)
    equivocation["atlas_entity"]["staleness"] = "review-required"
    scenarios.append(("same-sequence-different-digest", equivocation))

    stale = copy.deepcopy(valid_next)
    stale["sequence"] = 0
    stale["event_id"] = "principia-atlas:lifecycle-event:thermal-control:0000"
    scenarios.append(("stale-sequence", stale))

    skipped = copy.deepcopy(valid_next)
    skipped["sequence"] = 3
    skipped["event_id"] = "principia-atlas:lifecycle-event:thermal-control:0003"
    scenarios.append(("skipped-sequence", skipped))

    wrong_predecessor = copy.deepcopy(valid_next)
    wrong_predecessor["previous_event_sha256"] = "0" * 64
    scenarios.append(("wrong-predecessor", wrong_predecessor))

    wrong_receipt = copy.deepcopy(valid_next)
    wrong_receipt["source_checkpoint"]["receipt_chain_head_sha256"] = "1" * 64
    scenarios.append(("wrong-receipt-chain-head", wrong_receipt))

    unknown_entity = copy.deepcopy(valid_next)
    unknown_entity["atlas_entity"]["id"] = "concept:en:unknown-event-entity"
    scenarios.append(("unknown-entity-state", unknown_entity))

    wrong_affected = copy.deepcopy(valid_next)
    wrong_affected["affected_principia_artifacts"] = wrong_affected["affected_principia_artifacts"][:-1]
    scenarios.append(("affected-set-mismatch", wrong_affected))

    inherited = copy.deepcopy(valid_next)
    inherited["affected_principia_artifacts"][0]["release_status"] = "released"
    scenarios.append(("status-inheritance-injection", inherited))

    automatic = copy.deepcopy(valid_next)
    automatic["authority"]["automatic_release_action"] = True
    scenarios.append(("automatic-release-mutation", automatic))

    live = copy.deepcopy(valid_next)
    live["live"] = True
    scenarios.append(("live-activation", live))

    scenarios.append(("valid-next-event", valid_next))

    recovery = []
    for scenario_id, candidate in scenarios:
        observed = outcome(candidate, log, chain, matrix)
        recovery.append(
            {
                "scenario_id": scenario_id,
                "candidate_event_sha256": sha256_document(candidate),
                **observed,
            }
        )

    bad_ack = copy.deepcopy(ack)
    bad_ack["event_sha256"] = "f" * 64
    try:
        validate_ack(bad_ack, event)
        ack_outcome = {"accepted": True, "result": "accept", "error_code": None}
    except ProtocolError as exc:
        ack_outcome = {"accepted": False, "result": "reject", "error_code": exc.code}
    recovery.append(
        {
            "scenario_id": "ack-event-digest-mismatch",
            "candidate_event_sha256": sha256_document(event),
            **ack_outcome,
        }
    )

    return {
        "contract": RECOVERY_CONTRACT,
        "protocol_id": PROTOCOL_ID,
        "mode": MODE,
        "live": False,
        "event_log_head_sequence": log["head_sequence"],
        "event_log_head_sha256": log["head_event_sha256"],
        "scenarios": recovery,
        "authority": {
            "automatic_status_change": False,
            "automatic_release_action": False,
            "repository_mutation": False,
        },
    }


def build_outputs() -> dict[Path, dict[str, Any]]:
    chain = load_json(SOURCE_CHAIN_PATH)
    matrix = load_json(SOURCE_MATRIX_PATH)
    release = load_json(PHASE16_RELEASE_PATH)
    validate_sources(chain, matrix, release)
    scenario = scenario_by_id(matrix, "feedback-deprecated")
    event = event_from_scenario(
        scenario,
        sequence=1,
        previous_event_sha256=None,
        chain=chain,
        release=release,
    )
    ack = build_ack(event)
    validate_ack(ack, event)
    log = build_log(event, ack)
    recovery = build_recovery_matrix(event, ack, log, chain, matrix, release)
    return {
        EVENT_PATH: event,
        ACK_PATH: ack,
        LOG_PATH: log,
        RECOVERY_PATH: recovery,
    }


def check_outputs(outputs: Mapping[Path, Mapping[str, Any]]) -> list[str]:
    errors = []
    for path, value in outputs.items():
        expected = render_json(value)
        if not path.is_file():
            errors.append(f"missing output: {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != expected:
            errors.append(f"stale output: {path.relative_to(ROOT)}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    outputs = build_outputs()
    if args.write:
        for path, value in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(render_json(value), encoding="utf-8")
            print(f"wrote={path.relative_to(ROOT)}")
        return 0

    errors = check_outputs(outputs)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(
        "Phase 17 deterministic event, acknowledgement, append-only log, and recovery matrix are current."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
