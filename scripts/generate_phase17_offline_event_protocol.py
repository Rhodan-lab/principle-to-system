#!/usr/bin/env python3
"""Generate or verify the Phase 17 offline event-protocol evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
PILOT_ROOT = ROOT / "integration" / "principia-atlas" / "pilot"
SOURCE_RECEIPT_PATH = PILOT_ROOT / "thermal-control.multi-artifact.receipt.v02.json"
EVENTS_PATH = PILOT_ROOT / "thermal-control.lifecycle-events.v01.json"
ACKS_PATH = PILOT_ROOT / "thermal-control.lifecycle-acknowledgements.v01.json"
CHAIN_PATH = PILOT_ROOT / "thermal-control.event-protocol-chain.v01.json"
RECOVERY_PATH = PILOT_ROOT / "thermal-control.event-protocol-recovery.v01.json"

SOURCE_RECEIPT_SHA256 = "af529bc6c866be889e6a0b552dffedd81a5e46466cdae08e234472031617b562"
ARTIFACT_IDS = (
    "principia:failure-pattern:feedback-instability",
    "principia:investigation:room-cooling",
    "principia:system-dossier:refrigerator",
)
ATLAS_IMPLEMENTATION_MERGE = "1cc4aec6908a8703a7f505478329c633a23b4ef9"
ATLAS_GOVERNANCE_MERGE = "9370cc746e9756e433ac3772d56d079c9803b144"


def render_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_document(value: Mapping[str, Any]) -> str:
    return sha256_bytes(render_json(value).encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def authority() -> dict[str, Any]:
    return {
        "atlas_knowledge_status_authority": "Atlas",
        "principia_pedagogical_status_authority": "Principia",
        "principia_release_status_authority": "Principia",
        "automatic_status_change": False,
        "automatic_release_action": False,
        "repository_mutation": False,
    }


def base_event() -> dict[str, Any]:
    return {
        "contract": "principia-atlas-offline-lifecycle-event/0.1",
        "mode": "offline-event-protocol",
        "live": False,
        "source_repository": "Rhodan-lab/Atlas",
        "source_baseline": {
            "implementation_merge_commit": ATLAS_IMPLEMENTATION_MERGE,
            "governance_merge_commit": ATLAS_GOVERNANCE_MERGE,
            "mode": "importer-candidate",
            "live": False,
        },
        "fixture_kind": "bounded-synthetic",
        "event_kind": "lifecycle-transition",
        "authority": {
            "knowledge_lifecycle_authority": "Atlas",
            "status_inheritance": "prohibited",
            "automatic_status_change": False,
            "automatic_release_action": False,
            "repository_mutation": False,
        },
    }


def build_event_stream() -> dict[str, Any]:
    first = base_event()
    first.update(
        {
            "event_id": "atlas:lifecycle-event:concept-feedback:deprecated:0001",
            "sequence": 1,
            "previous_event_sha256": None,
            "subject": {
                "id": "concept:en:feedback",
                "revision": 1,
                "key": "concept:en:feedback@1",
                "entity_type": "concept",
            },
            "transition": {
                "from": "current",
                "to": "deprecated",
                "reason_code": "fixture-deprecation",
            },
        }
    )
    first_sha = sha256_document(first)

    second = base_event()
    second.update(
        {
            "event_id": "atlas:lifecycle-event:claim-model-boundary:retracted:0002",
            "sequence": 2,
            "previous_event_sha256": first_sha,
            "subject": {
                "id": "claim:en:model-oscillation-does-not-prove-real-system",
                "revision": 1,
                "key": "claim:en:model-oscillation-does-not-prove-real-system@1",
                "entity_type": "claim",
            },
            "transition": {
                "from": "current",
                "to": "retracted",
                "reason_code": "fixture-retraction",
            },
        }
    )
    second_sha = sha256_document(second)
    return {
        "contract": "principia-atlas-offline-lifecycle-event-stream/0.1",
        "stream_id": "principia-atlas:offline-lifecycle-events:thermal-control:0001",
        "mode": "offline-event-protocol",
        "live": False,
        "source_receipt": {
            "path": SOURCE_RECEIPT_PATH.relative_to(ROOT).as_posix(),
            "sha256": SOURCE_RECEIPT_SHA256,
            "sequence": 1,
        },
        "events": [
            {"event_sha256": first_sha, "event": first},
            {"event_sha256": second_sha, "event": second},
        ],
        "authority": authority(),
    }


def base_acknowledgement() -> dict[str, Any]:
    return {
        "contract": "principia-atlas-offline-lifecycle-acknowledgement/0.1",
        "mode": "offline-event-protocol",
        "live": False,
        "repository": "Rhodan-lab/principle-to-system",
        "affected_artifacts": [{"id": artifact_id, "revision": 1} for artifact_id in ARTIFACT_IDS],
        "outcome": "recorded-no-mutation",
        "status_inheritance": "prohibited",
        "automatic_status_change": False,
        "automatic_release_action": False,
        "repository_mutation": False,
    }


def build_acknowledgement_stream(events: Mapping[str, Any]) -> dict[str, Any]:
    event_entries = events["events"]
    first_event = event_entries[0]
    second_event = event_entries[1]

    first = base_acknowledgement()
    first.update(
        {
            "acknowledgement_id": "principia:lifecycle-ack:concept-feedback:deprecated:0001",
            "sequence": 1,
            "previous_acknowledgement_sha256": None,
            "event_id": first_event["event"]["event_id"],
            "event_sha256": first_event["event_sha256"],
            "required_action": "revalidate",
            "accepted": True,
        }
    )
    first_sha = sha256_document(first)

    second = base_acknowledgement()
    second.update(
        {
            "acknowledgement_id": "principia:lifecycle-ack:claim-model-boundary:retracted:0002",
            "sequence": 2,
            "previous_acknowledgement_sha256": first_sha,
            "event_id": second_event["event"]["event_id"],
            "event_sha256": second_event["event_sha256"],
            "required_action": "block-release",
            "accepted": True,
        }
    )
    second_sha = sha256_document(second)
    return {
        "contract": "principia-atlas-offline-lifecycle-acknowledgement-stream/0.1",
        "stream_id": "principia-atlas:offline-lifecycle-acks:thermal-control:0001",
        "mode": "offline-event-protocol",
        "live": False,
        "acknowledgements": [
            {"acknowledgement_sha256": first_sha, "acknowledgement": first},
            {"acknowledgement_sha256": second_sha, "acknowledgement": second},
        ],
        "authority": authority(),
    }


def build_chain(events: Mapping[str, Any], acknowledgements: Mapping[str, Any]) -> dict[str, Any]:
    event_entries = events["events"]
    ack_entries = acknowledgements["acknowledgements"]
    links = []
    for index in range(2):
        event = event_entries[index]
        ack = ack_entries[index]
        links.append(
            {
                "sequence": index + 1,
                "event_id": event["event"]["event_id"],
                "event_sha256": event["event_sha256"],
                "previous_event_sha256": event["event"]["previous_event_sha256"],
                "acknowledgement_id": ack["acknowledgement"]["acknowledgement_id"],
                "acknowledgement_sha256": ack["acknowledgement_sha256"],
                "previous_acknowledgement_sha256": ack["acknowledgement"][
                    "previous_acknowledgement_sha256"
                ],
            }
        )
    return {
        "contract": "principia-atlas-offline-event-protocol-chain/0.1",
        "chain_id": "principia-atlas:offline-event-protocol-chain:thermal-control:0001",
        "mode": "offline-event-protocol",
        "live": False,
        "event_head_sequence": 2,
        "event_head_sha256": event_entries[-1]["event_sha256"],
        "acknowledgement_head_sequence": 2,
        "acknowledgement_head_sha256": ack_entries[-1]["acknowledgement_sha256"],
        "links": links,
        "authority": authority(),
    }


def build_recovery(events: Mapping[str, Any], acknowledgements: Mapping[str, Any]) -> dict[str, Any]:
    cases = (
        ("duplicate-event-replay", True, "idempotent-noop", None),
        ("stale-event-sequence", False, "rejected", "E-P17-EVENT-SEQUENCE"),
        ("skipped-event-sequence", False, "rejected", "E-P17-EVENT-SEQUENCE"),
        ("wrong-event-predecessor", False, "rejected", "E-P17-EVENT-PREVIOUS-DIGEST"),
        ("event-digest-corruption", False, "rejected", "E-P17-EVENT-DIGEST"),
        ("unknown-subject-revision", False, "rejected", "E-P17-SUBJECT-REVISION"),
        ("status-inheritance-injection", False, "rejected", "E-P17-STATUS-INHERITANCE"),
        ("live-activation", False, "rejected", "E-P17-LIVE-FROZEN"),
        ("valid-next-event", True, "accepted-recovery-checkpoint", None),
        ("ack-wrong-event-digest", False, "rejected", "E-P17-ACK-EVENT-DIGEST"),
        ("ack-out-of-order", False, "rejected", "E-P17-ACK-SEQUENCE"),
        ("ack-action-weakening", False, "rejected", "E-P17-ACK-ACTION"),
    )
    return {
        "contract": "principia-atlas-offline-event-protocol-recovery/0.1",
        "matrix_id": "principia-atlas:offline-event-protocol-recovery:thermal-control:0001",
        "mode": "offline-event-protocol",
        "live": False,
        "current_event_head": {
            "sequence": 2,
            "sha256": events["events"][-1]["event_sha256"],
        },
        "current_acknowledgement_head": {
            "sequence": 2,
            "sha256": acknowledgements["acknowledgements"][-1]["acknowledgement_sha256"],
        },
        "expected_next_sequence": 3,
        "scenarios": [
            {
                "scenario_id": scenario_id,
                "accepted": accepted,
                "outcome": outcome,
                "error_code": error_code,
            }
            for scenario_id, accepted, outcome, error_code in cases
        ],
        "authority": authority(),
    }


def expected_outputs() -> dict[Path, dict[str, Any]]:
    events = build_event_stream()
    acknowledgements = build_acknowledgement_stream(events)
    return {
        EVENTS_PATH: events,
        ACKS_PATH: acknowledgements,
        CHAIN_PATH: build_chain(events, acknowledgements),
        RECOVERY_PATH: build_recovery(events, acknowledgements),
    }


def check_outputs() -> int:
    errors = []
    for path, expected in expected_outputs().items():
        rendered = render_json(expected)
        if not path.is_file():
            errors.append(f"missing generated output: {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != rendered:
            errors.append(f"stale generated output: {path.relative_to(ROOT)}")
    if errors:
        for error in errors:
            print(error)
        return 1
    return 0


def write_outputs() -> None:
    for path, value in expected_outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_json(value), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_outputs()
        return 0
    return check_outputs()


if __name__ == "__main__":
    raise SystemExit(main())
