#!/usr/bin/env python3
"""Generate or verify Phase 18 offline reconciliation evidence."""
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
EVENTS_PATH = PILOT_ROOT / "thermal-control.lifecycle-events.v01.json"
ACKS_PATH = PILOT_ROOT / "thermal-control.lifecycle-acknowledgements.v01.json"
CHAIN_PATH = PILOT_ROOT / "thermal-control.event-protocol-chain.v01.json"
PHASE16_MATRIX_PATH = PILOT_ROOT / "thermal-control.lifecycle-matrix.v02.json"
PHASE17_POSTMERGE_PATH = ROOT / "release" / "phase-17-postmerge.json"
REPORT_PATH = PILOT_ROOT / "thermal-control.reconciliation-report.v01.json"
CHECKPOINT_PATH = PILOT_ROOT / "thermal-control.reconciliation-checkpoint.v01.json"
RECOVERY_PATH = PILOT_ROOT / "thermal-control.reconciliation-recovery.v01.json"

REPORT_CONTRACT = "principia-atlas-offline-reconciliation-report/0.1"
CHECKPOINT_CONTRACT = "principia-atlas-offline-reconciliation-checkpoint/0.1"
RECOVERY_CONTRACT = "principia-atlas-offline-reconciliation-recovery/0.1"
MODE = "offline-reconciliation-simulation"
RECONCILIATION_ID = "principia-atlas:offline-reconciliation:thermal-control:0001"
PHASE17_HEAD = "e260417ef7631ebf4f87c89faff7da45d571b63c"
PHASE17_MERGE = "c9fba79f821d59b36030924e5c388f71a56f7787"
PHASE17_FINALIZATION_MERGE = "806b03335a1d0b43e5a32ffecce8439350564152"

ARTIFACT_PATHS = {
    "principia:failure-pattern:feedback-instability": ROOT / "failure-atlas" / "feedback-instability.md",
    "principia:investigation:room-cooling": ROOT / "investigations" / "room-cooling.md",
    "principia:system-dossier:refrigerator": ROOT / "system-dossiers" / "refrigerator.md",
}

PROHIBITED_KEYS = {
    "knowledge_status_inheritance",
    "atlas_status_inheritance",
    "pedagogical_status_inheritance",
    "release_status_inheritance",
}


@dataclass(frozen=True)
class ReconciliationError(ValueError):
    code: str

    def __str__(self) -> str:
        return self.code


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def render_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_document(value: Mapping[str, Any]) -> str:
    return sha256_bytes(render_json(value).encode("utf-8"))


def frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing front matter")
    end = next((index for index, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if end is None:
        raise ValueError(f"{path}: unclosed front matter")
    result: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line or line.lstrip().startswith("-"):
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def current_inventory() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for artifact_id, path in sorted(ARTIFACT_PATHS.items()):
        metadata = frontmatter(path)
        result[artifact_id] = {
            "artifact_id": artifact_id,
            "artifact_revision": int(metadata["artifact_revision"]),
            "pedagogical_status": metadata["status"],
            "release_status": metadata["release_status"],
            "source_path": path.relative_to(ROOT).as_posix(),
            "source_sha256": sha256_file(path),
        }
    return result


def find_prohibited(value: Any, path: str = "$") -> str | None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            if key_text in PROHIBITED_KEYS:
                return f"{path}.{key_text}"
            found = find_prohibited(item, f"{path}.{key_text}")
            if found:
                return found
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found = find_prohibited(item, f"{path}[{index}]")
            if found:
                return found
    return None


def validate_authority(value: Any) -> None:
    if not isinstance(value, Mapping):
        raise ReconciliationError("E-P18-AUTHORITY")
    for key in ("automatic_status_change", "automatic_release_action", "repository_mutation"):
        if value.get(key) is not False:
            raise ReconciliationError("E-P18-AUTOMATIC-MUTATION")


def matrix_scenario(matrix: Mapping[str, Any], subject_id: str, transition_to: str) -> dict[str, Any]:
    scenario_id = {
        ("concept:en:feedback", "deprecated"): "feedback-deprecated",
        ("claim:en:model-oscillation-does-not-prove-real-system", "retracted"): "claim-retracted",
    }.get((subject_id, transition_to))
    if scenario_id is None:
        raise ReconciliationError("E-P18-SCENARIO-MISSING")
    scenarios = matrix.get("scenarios")
    if not isinstance(scenarios, list):
        raise ReconciliationError("E-P18-MATRIX-SHAPE")
    for scenario in scenarios:
        if isinstance(scenario, dict) and scenario.get("scenario_id") == scenario_id:
            return scenario
    raise ReconciliationError("E-P18-SCENARIO-MISSING")


def stream_entries(stream: Mapping[str, Any], key: str, inner: str) -> list[dict[str, Any]]:
    values = stream.get(key)
    if not isinstance(values, list):
        raise ReconciliationError("E-P18-STREAM-SHAPE")
    result: list[dict[str, Any]] = []
    for wrapper in values:
        if not isinstance(wrapper, Mapping) or not isinstance(wrapper.get(inner), Mapping):
            raise ReconciliationError("E-P18-STREAM-SHAPE")
        result.append(dict(wrapper))
    return result


def reconcile(
    events_stream: Mapping[str, Any],
    acknowledgements_stream: Mapping[str, Any],
    chain: Mapping[str, Any],
    matrix: Mapping[str, Any],
    inventory: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    for document in (events_stream, acknowledgements_stream, chain):
        if document.get("live") is not False:
            raise ReconciliationError("E-P18-LIVE-FROZEN")
        validate_authority(document.get("authority"))
        if find_prohibited(document):
            raise ReconciliationError("E-P18-STATUS-INHERITANCE")

    event_wrappers = stream_entries(events_stream, "events", "event")
    ack_wrappers = stream_entries(acknowledgements_stream, "acknowledgements", "acknowledgement")
    if len(event_wrappers) != len(ack_wrappers):
        raise ReconciliationError("E-P18-COUNT-MISMATCH")

    event_by_id: dict[str, tuple[dict[str, Any], str]] = {}
    event_sequences: list[int] = []
    previous_event_sha: str | None = None
    for wrapper in event_wrappers:
        event = dict(wrapper["event"])
        event_sha = wrapper.get("event_sha256")
        if not isinstance(event_sha, str) or event_sha != sha256_document(event):
            raise ReconciliationError("E-P18-EVENT-DIGEST")
        sequence = event.get("sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool):
            raise ReconciliationError("E-P18-EVENT-ORDER")
        if sequence != len(event_sequences) + 1 or event.get("previous_event_sha256") != previous_event_sha:
            raise ReconciliationError("E-P18-EVENT-ORDER")
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or event_id in event_by_id:
            raise ReconciliationError("E-P18-EVENT-DUPLICATE")
        event_by_id[event_id] = (event, event_sha)
        event_sequences.append(sequence)
        previous_event_sha = event_sha

    ack_by_event: dict[str, tuple[dict[str, Any], str]] = {}
    ack_sequences: list[int] = []
    previous_ack_sha: str | None = None
    for wrapper in ack_wrappers:
        ack = dict(wrapper["acknowledgement"])
        ack_sha = wrapper.get("acknowledgement_sha256")
        if not isinstance(ack_sha, str) or ack_sha != sha256_document(ack):
            raise ReconciliationError("E-P18-ACK-DIGEST")
        sequence = ack.get("sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool):
            raise ReconciliationError("E-P18-ACK-ORDER")
        if sequence != len(ack_sequences) + 1 or ack.get("previous_acknowledgement_sha256") != previous_ack_sha:
            raise ReconciliationError("E-P18-ACK-ORDER")
        event_id = ack.get("event_id")
        if not isinstance(event_id, str) or event_id not in event_by_id:
            raise ReconciliationError("E-P18-ACK-ORPHAN")
        if event_id in ack_by_event:
            raise ReconciliationError("E-P18-ACK-DUPLICATE")
        event, event_sha = event_by_id[event_id]
        if ack.get("event_sha256") != event_sha:
            raise ReconciliationError("E-P18-ACK-EVENT-DIGEST")
        if ack.get("sequence") != event.get("sequence"):
            raise ReconciliationError("E-P18-SEQUENCE-MISMATCH")
        ack_by_event[event_id] = (ack, ack_sha)
        ack_sequences.append(sequence)
        previous_ack_sha = ack_sha

    if set(ack_by_event) != set(event_by_id):
        raise ReconciliationError("E-P18-ACK-MISSING")

    links = chain.get("links")
    if not isinstance(links, list) or len(links) != len(event_wrappers):
        raise ReconciliationError("E-P18-CHAIN-SHAPE")
    if chain.get("event_head_sequence") != len(event_wrappers) or chain.get("event_head_sha256") != previous_event_sha:
        raise ReconciliationError("E-P18-CHAIN-EVENT-HEAD")
    if chain.get("acknowledgement_head_sequence") != len(ack_wrappers) or chain.get("acknowledgement_head_sha256") != previous_ack_sha:
        raise ReconciliationError("E-P18-CHAIN-ACK-HEAD")

    records: list[dict[str, Any]] = []
    for sequence, link in enumerate(links, 1):
        if not isinstance(link, Mapping) or link.get("sequence") != sequence:
            raise ReconciliationError("E-P18-CHAIN-LINK")
        event_id = link.get("event_id")
        if not isinstance(event_id, str) or event_id not in event_by_id:
            raise ReconciliationError("E-P18-CHAIN-LINK")
        event, event_sha = event_by_id[event_id]
        ack, ack_sha = ack_by_event[event_id]
        if link.get("event_sha256") != event_sha or link.get("acknowledgement_sha256") != ack_sha:
            raise ReconciliationError("E-P18-CHAIN-LINK")

        subject = event.get("subject")
        transition = event.get("transition")
        if not isinstance(subject, Mapping) or not isinstance(transition, Mapping):
            raise ReconciliationError("E-P18-EVENT-SHAPE")
        scenario = matrix_scenario(matrix, str(subject.get("id")), str(transition.get("to")))
        expected_dependents = scenario.get("external_dependents")
        if not isinstance(expected_dependents, list):
            raise ReconciliationError("E-P18-MATRIX-SHAPE")
        expected_action = {
            str(item["artifact_id"]): str(item["effective_action"])
            for item in expected_dependents
            if isinstance(item, Mapping)
        }
        expected_refs = sorted(
            (str(item["artifact_id"]), int(item["artifact_revision"]))
            for item in expected_dependents
            if isinstance(item, Mapping)
        )
        ack_refs_raw = ack.get("affected_artifacts")
        if not isinstance(ack_refs_raw, list):
            raise ReconciliationError("E-P18-AFFECTED-SET")
        ack_refs = sorted(
            (str(item.get("id")), int(item.get("revision")))
            for item in ack_refs_raw
            if isinstance(item, Mapping)
        )
        if ack_refs != expected_refs:
            raise ReconciliationError("E-P18-AFFECTED-SET")
        required_actions = sorted(set(expected_action.values()))
        if len(required_actions) != 1 or ack.get("required_action") != required_actions[0]:
            raise ReconciliationError("E-P18-ACTION-MISMATCH")

        current_refs: list[dict[str, Any]] = []
        for artifact_id, revision in ack_refs:
            current = inventory.get(artifact_id)
            if not isinstance(current, Mapping):
                raise ReconciliationError("E-P18-ARTIFACT-MISSING")
            if current.get("artifact_revision") != revision:
                raise ReconciliationError("E-P18-ARTIFACT-REVISION")
            current_refs.append(
                {
                    "artifact_id": artifact_id,
                    "acknowledged_revision": revision,
                    "current_revision": current["artifact_revision"],
                    "pedagogical_status": current["pedagogical_status"],
                    "release_status": current["release_status"],
                    "source_path": current["source_path"],
                    "source_sha256": current["source_sha256"],
                    "reconciliation_state": "current",
                }
            )

        records.append(
            {
                "sequence": sequence,
                "event_id": event_id,
                "event_sha256": event_sha,
                "acknowledgement_id": ack["acknowledgement_id"],
                "acknowledgement_sha256": ack_sha,
                "subject": dict(subject),
                "transition": dict(transition),
                "required_action": ack["required_action"],
                "affected_artifacts": current_refs,
                "result": "reconciled",
            }
        )

    return {
        "contract": REPORT_CONTRACT,
        "reconciliation_id": RECONCILIATION_ID,
        "mode": MODE,
        "live": False,
        "source": {
            "phase17_candidate_head_commit": PHASE17_HEAD,
            "phase17_merge_commit": PHASE17_MERGE,
            "phase17_finalization_merge_commit": PHASE17_FINALIZATION_MERGE,
            "events_path": EVENTS_PATH.relative_to(ROOT).as_posix(),
            "events_sha256": sha256_file(EVENTS_PATH),
            "acknowledgements_path": ACKS_PATH.relative_to(ROOT).as_posix(),
            "acknowledgements_sha256": sha256_file(ACKS_PATH),
            "chain_path": CHAIN_PATH.relative_to(ROOT).as_posix(),
            "chain_sha256": sha256_file(CHAIN_PATH),
            "phase17_postmerge_path": PHASE17_POSTMERGE_PATH.relative_to(ROOT).as_posix(),
            "phase17_postmerge_sha256": sha256_file(PHASE17_POSTMERGE_PATH),
        },
        "summary": {
            "event_count": len(event_wrappers),
            "acknowledgement_count": len(ack_wrappers),
            "reconciled_count": len(records),
            "unacknowledged_count": 0,
            "orphan_acknowledgement_count": 0,
            "stale_artifact_reference_count": 0,
            "action_mismatch_count": 0,
            "decision": "reconciled-no-mutation",
        },
        "records": records,
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


def build_checkpoint(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "contract": CHECKPOINT_CONTRACT,
        "reconciliation_id": RECONCILIATION_ID,
        "mode": MODE,
        "live": False,
        "event_head": {
            "sequence": 2,
            "sha256": "61ca082c74330aaff8391af0937096d12d64f9ac92010e982bb93f4e811144c9",
        },
        "acknowledgement_head": {
            "sequence": 2,
            "sha256": "bb5c1fa34595c9c2ea96f5ee7d30fb212db4089ce4436f26d84f351eb30cee7e",
        },
        "report_path": REPORT_PATH.relative_to(ROOT).as_posix(),
        "report_sha256": sha256_document(report),
        "inventory_sha256": sha256_document({"artifacts": current_inventory()}),
        "decision": "reconciled-no-mutation",
        "next_expected_event_sequence": 3,
        "next_expected_acknowledgement_sequence": 3,
        "authority": report["authority"],
    }


def observed(candidate: tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]]) -> dict[str, Any]:
    try:
        reconcile(*candidate)
        return {"accepted": True, "outcome": "reconciled", "error_code": None}
    except ReconciliationError as exc:
        return {"accepted": False, "outcome": "divergence-detected", "error_code": exc.code}


def build_recovery(
    events: dict[str, Any],
    acks: dict[str, Any],
    chain: dict[str, Any],
    matrix: dict[str, Any],
    inventory: dict[str, dict[str, Any]],
    checkpoint: Mapping[str, Any],
) -> dict[str, Any]:
    scenarios: list[tuple[str, tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]]]] = []
    base = (events, acks, chain, matrix, inventory)
    scenarios.append(("exact-reconciliation", copy.deepcopy(base)))

    missing_ack = copy.deepcopy(base)
    missing_ack[1]["acknowledgements"].pop()
    scenarios.append(("missing-acknowledgement", missing_ack))

    orphan_ack = copy.deepcopy(base)
    orphan_ack[1]["acknowledgements"][1]["acknowledgement"]["event_id"] = "atlas:lifecycle-event:unknown:0002"
    scenarios.append(("orphan-acknowledgement", orphan_ack))

    wrong_event_digest = copy.deepcopy(base)
    wrong_event_digest[1]["acknowledgements"][1]["acknowledgement"]["event_sha256"] = "0" * 64
    wrong_event_digest[1]["acknowledgements"][1]["acknowledgement_sha256"] = sha256_document(
        wrong_event_digest[1]["acknowledgements"][1]["acknowledgement"]
    )
    scenarios.append(("ack-event-digest-mismatch", wrong_event_digest))

    action_weakening = copy.deepcopy(base)
    action_weakening[1]["acknowledgements"][1]["acknowledgement"]["required_action"] = "revalidate"
    action_weakening[1]["acknowledgements"][1]["acknowledgement_sha256"] = sha256_document(
        action_weakening[1]["acknowledgements"][1]["acknowledgement"]
    )
    scenarios.append(("action-weakening", action_weakening))

    affected_mismatch = copy.deepcopy(base)
    affected_mismatch[1]["acknowledgements"][0]["acknowledgement"]["affected_artifacts"].pop()
    affected_mismatch[1]["acknowledgements"][0]["acknowledgement_sha256"] = sha256_document(
        affected_mismatch[1]["acknowledgements"][0]["acknowledgement"]
    )
    scenarios.append(("affected-artifact-mismatch", affected_mismatch))

    stale_revision = copy.deepcopy(base)
    stale_revision[4]["principia:failure-pattern:feedback-instability"]["artifact_revision"] = 2
    scenarios.append(("stale-artifact-revision", stale_revision))

    missing_artifact = copy.deepcopy(base)
    del missing_artifact[4]["principia:investigation:room-cooling"]
    scenarios.append(("missing-current-artifact", missing_artifact))

    event_reorder = copy.deepcopy(base)
    event_reorder[0]["events"].reverse()
    scenarios.append(("event-stream-reordered", event_reorder))

    ack_reorder = copy.deepcopy(base)
    ack_reorder[1]["acknowledgements"].reverse()
    scenarios.append(("acknowledgement-stream-reordered", ack_reorder))

    event_head = copy.deepcopy(base)
    event_head[2]["event_head_sha256"] = "1" * 64
    scenarios.append(("event-chain-head-mismatch", event_head))

    ack_head = copy.deepcopy(base)
    ack_head[2]["acknowledgement_head_sha256"] = "2" * 64
    scenarios.append(("acknowledgement-chain-head-mismatch", ack_head))

    status_inheritance = copy.deepcopy(base)
    status_inheritance[1]["pedagogical_status_inheritance"] = "reviewed"
    scenarios.append(("status-inheritance-injection", status_inheritance))

    automatic_mutation = copy.deepcopy(base)
    automatic_mutation[2]["authority"]["automatic_release_action"] = True
    scenarios.append(("automatic-release-mutation", automatic_mutation))

    live = copy.deepcopy(base)
    live[0]["live"] = True
    scenarios.append(("live-activation", live))

    results = []
    for scenario_id, candidate in scenarios:
        results.append({"scenario_id": scenario_id, **observed(candidate)})

    return {
        "contract": RECOVERY_CONTRACT,
        "reconciliation_id": RECONCILIATION_ID,
        "mode": MODE,
        "live": False,
        "checkpoint_sha256": sha256_document(checkpoint),
        "scenarios": results,
        "authority": checkpoint["authority"],
    }


def build_outputs() -> dict[Path, dict[str, Any]]:
    events = load_json(EVENTS_PATH)
    acks = load_json(ACKS_PATH)
    chain = load_json(CHAIN_PATH)
    matrix = load_json(PHASE16_MATRIX_PATH)
    inventory = current_inventory()
    report = reconcile(events, acks, chain, matrix, inventory)
    checkpoint = build_checkpoint(report)
    recovery = build_recovery(events, acks, chain, matrix, inventory, checkpoint)
    return {
        REPORT_PATH: report,
        CHECKPOINT_PATH: checkpoint,
        RECOVERY_PATH: recovery,
    }


def check_outputs(outputs: Mapping[Path, Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
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
    print("Phase 18 reconciliation report, checkpoint, and recovery matrix are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
