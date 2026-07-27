#!/usr/bin/env python3
"""Generate or verify Phase 19 offline reconciliation-policy evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "integration" / "principia-atlas" / "pilot"
SOURCE_REPORT_PATH = PILOT / "thermal-control.reconciliation-report.v01.json"
PHASE18_POSTMERGE_PATH = ROOT / "release" / "phase-18-postmerge.json"
REVIEW_QUEUE_PATH = PILOT / "thermal-control.policy-review-queue.v01.json"
HOLD_PROPOSALS_PATH = PILOT / "thermal-control.release-hold-proposals.v01.json"
LEDGER_PATH = PILOT / "thermal-control.policy-ledger.v01.json"
RECOVERY_PATH = PILOT / "thermal-control.policy-recovery.v01.json"
RELEASE_PATH = ROOT / "release" / "phase-19-offline-reconciliation-policy.json"

SOURCE_REPORT_SHA256 = "b88334407d26fa986818f240b2f1048909fcb8b3443da1f3c05f174f5becbb8d"
PHASE18_POSTMERGE_SHA256 = "5cd15b5aae1eb7211abf3e523b05b3e212712fea6d36e836a9f15c6e70cf6cb7"
PHASE18_FINALIZATION_MERGE = "582117eb9ea9ecf489be5ef24464977195464d93"
MODE = "offline-reconciliation-policy"
AUTHORITY = {
    "atlas_knowledge_status_authority": "Atlas",
    "automatic_release_action": False,
    "automatic_status_change": False,
    "principia_pedagogical_status_authority": "Principia",
    "principia_release_status_authority": "Principia",
    "repository_mutation": False,
    "status_inheritance": "prohibited",
}
EXPECTED_ARTIFACT_KEYS = {
    "principia:failure-pattern:feedback-instability@1",
    "principia:investigation:room-cooling@1",
    "principia:system-dossier:refrigerator@1",
}
PROHIBITED_KEYS = {
    "atlas_status_inheritance",
    "knowledge_status_inheritance",
    "pedagogical_status_inheritance",
    "release_status_inheritance",
}


@dataclass
class PolicyError(ValueError):
    code: str

    def __str__(self) -> str:
        return self.code


def render_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_document(value: Mapping[str, Any]) -> str:
    return sha256_bytes(render_json(value).encode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PolicyError("E-P19-JSON-SHAPE")
    return value


def find_prohibited(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(str(key) in PROHIBITED_KEYS or find_prohibited(item) for key, item in value.items())
    if isinstance(value, list):
        return any(find_prohibited(item) for item in value)
    return False


def source_block() -> dict[str, Any]:
    return {
        "phase18_finalization_merge_commit": PHASE18_FINALIZATION_MERGE,
        "phase18_postmerge_path": "release/phase-18-postmerge.json",
        "phase18_postmerge_sha256": PHASE18_POSTMERGE_SHA256,
        "reconciliation_id": "principia-atlas:offline-reconciliation:thermal-control:0001",
        "reconciliation_path": "integration/principia-atlas/pilot/thermal-control.reconciliation-report.v01.json",
        "reconciliation_sha256": SOURCE_REPORT_SHA256,
    }


def artifact_refs(record: Mapping[str, Any]) -> list[dict[str, Any]]:
    values = record.get("affected_artifacts")
    if not isinstance(values, list):
        raise PolicyError("E-P19-AFFECTED-SET")
    result = []
    for item in values:
        if not isinstance(item, Mapping):
            raise PolicyError("E-P19-AFFECTED-SET")
        artifact_id = item.get("artifact_id")
        revision = item.get("current_revision")
        if not isinstance(artifact_id, str) or not isinstance(revision, int):
            raise PolicyError("E-P19-AFFECTED-SET")
        result.append({
            "artifact_id": artifact_id,
            "artifact_revision": revision,
            "exact_key": f"{artifact_id}@{revision}",
            "observed_pedagogical_status": item.get("pedagogical_status"),
            "observed_release_status": item.get("release_status"),
            "source_path": item.get("source_path"),
            "source_sha256": item.get("source_sha256"),
        })
    result.sort(key=lambda item: item["exact_key"])
    if {item["exact_key"] for item in result} != EXPECTED_ARTIFACT_KEYS:
        raise PolicyError("E-P19-AFFECTED-SET")
    return result


def source_records() -> list[dict[str, Any]]:
    if sha256_file(SOURCE_REPORT_PATH) != SOURCE_REPORT_SHA256:
        raise PolicyError("E-P19-SOURCE-PIN")
    if sha256_file(PHASE18_POSTMERGE_PATH) != PHASE18_POSTMERGE_SHA256:
        raise PolicyError("E-P19-SOURCE-PIN")
    report = load_json(SOURCE_REPORT_PATH)
    postmerge = load_json(PHASE18_POSTMERGE_PATH)
    if report.get("contract") != "principia-atlas-offline-reconciliation-report/0.1":
        raise PolicyError("E-P19-SOURCE-CONTRACT")
    if report.get("summary", {}).get("decision") != "reconciled-no-mutation":
        raise PolicyError("E-P19-SOURCE-SUMMARY")
    if postmerge.get("state") != "offline-reconciliation-simulation-validated":
        raise PolicyError("E-P19-POSTMERGE-STATE")
    records = report.get("records")
    if not isinstance(records, list) or len(records) != 2:
        raise PolicyError("E-P19-SOURCE-COUNT")
    if [record.get("required_action") for record in records] != ["revalidate", "block-release"]:
        raise PolicyError("E-P19-ACTION-MAPPING")
    return [dict(record) for record in records]


def build_queue(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "authority": AUTHORITY,
        "contract": "principia-offline-review-queue/0.1",
        "items": [{
            "acknowledgement_id": record["acknowledgement_id"],
            "acknowledgement_sha256": record["acknowledgement_sha256"],
            "affected_artifacts": artifact_refs(record),
            "automatic_execution": False,
            "event_id": record["event_id"],
            "event_sha256": record["event_sha256"],
            "policy_action": "manual-review",
            "priority": "high",
            "queue_item_id": "principia:policy-review:feedback-deprecation:0001",
            "required_action": "revalidate",
            "requires_manual_resolution": True,
            "sequence": 1,
            "source_record_sequence": 1,
            "state": "open-proposal",
            "subject": record["subject"],
            "transition": record["transition"],
        }],
        "live": False,
        "mode": MODE,
        "queue_id": "principia:offline-review-queue:thermal-control:0001",
        "source": source_block(),
        "summary": {"affected_artifact_count": 3, "automatic_execution_count": 0, "item_count": 1, "open_proposal_count": 1},
    }


def build_holds(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "authority": AUTHORITY,
        "contract": "principia-offline-release-hold-proposals/0.1",
        "items": [{
            "acknowledgement_id": record["acknowledgement_id"],
            "acknowledgement_sha256": record["acknowledgement_sha256"],
            "affected_artifacts": artifact_refs(record),
            "automatic_execution": False,
            "effective": False,
            "event_id": record["event_id"],
            "event_sha256": record["event_sha256"],
            "hold_id": "principia:release-hold-proposal:model-boundary-retraction:0001",
            "policy_action": "propose-release-hold",
            "required_action": "block-release",
            "requires_manual_resolution": True,
            "scope": "release-only",
            "sequence": 1,
            "source_record_sequence": 2,
            "state": "proposed",
            "subject": record["subject"],
            "transition": record["transition"],
        }],
        "live": False,
        "mode": MODE,
        "proposal_stream_id": "principia:offline-release-hold-proposals:thermal-control:0001",
        "source": source_block(),
        "summary": {"affected_artifact_count": 3, "automatic_execution_count": 0, "effective_hold_count": 0, "proposal_count": 1},
    }


def ledger_entry(sequence: int, entry_type: str, policy_id: str, source_sequence: int, document_sha: str, previous: str | None) -> dict[str, Any]:
    entry = {
        "entry_type": entry_type,
        "policy_document_sha256": document_sha,
        "policy_id": policy_id,
        "previous_entry_sha256": previous,
        "sequence": sequence,
        "source_record_sequence": source_sequence,
    }
    return {"entry": entry, "entry_sha256": sha256_document(entry)}


def build_ledger(queue: Mapping[str, Any], holds: Mapping[str, Any]) -> dict[str, Any]:
    first = ledger_entry(1, "review-queue", queue["items"][0]["queue_item_id"], 1, sha256_document(queue), None)
    second = ledger_entry(2, "release-hold-proposal", holds["items"][0]["hold_id"], 2, sha256_document(holds), first["entry_sha256"])
    return {
        "authority": AUTHORITY,
        "contract": "principia-offline-reconciliation-policy-ledger/0.1",
        "decision": "proposals-recorded-no-mutation",
        "entries": [first, second],
        "head_sequence": 2,
        "head_sha256": second["entry_sha256"],
        "ledger_id": "principia:offline-reconciliation-policy-ledger:thermal-control:0001",
        "live": False,
        "mode": MODE,
        "source": source_block(),
    }


RECOVERY = [
    ("baseline", "accepted", None),
    ("source-digest-drift", "rejected", "E-P19-SOURCE-PIN"),
    ("missing-source-record", "rejected", "E-P19-SOURCE-COUNT"),
    ("revalidate-weakened", "rejected", "E-P19-ACTION-MAPPING"),
    ("block-release-weakened", "rejected", "E-P19-ACTION-MAPPING"),
    ("queue-auto-execution", "rejected", "E-P19-AUTOMATIC-EXECUTION"),
    ("queue-auto-resolution", "rejected", "E-P19-MANUAL-RESOLUTION"),
    ("hold-effective", "rejected", "E-P19-HOLD-EFFECTIVE"),
    ("affected-set-drift", "rejected", "E-P19-AFFECTED-SET"),
    ("duplicate-policy-id", "rejected", "E-P19-DUPLICATE"),
    ("ledger-predecessor-drift", "rejected", "E-P19-LEDGER-ORDER"),
    ("status-inheritance", "rejected", "E-P19-STATUS-INHERITANCE"),
    ("automatic-mutation", "rejected", "E-P19-AUTHORITY"),
    ("live-activation", "rejected", "E-P19-LIVE-FROZEN"),
]


def build_recovery(queue: Mapping[str, Any], holds: Mapping[str, Any], ledger: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "authority": AUTHORITY,
        "baseline": {
            "ledger_sha256": sha256_document(ledger),
            "release_hold_proposals_sha256": sha256_document(holds),
            "review_queue_sha256": sha256_document(queue),
        },
        "contract": "principia-offline-reconciliation-policy-recovery/0.1",
        "live": False,
        "mode": MODE,
        "recovery_id": "principia:offline-reconciliation-policy-recovery:thermal-control:0001",
        "scenarios": [{"expected_error": error, "expected_outcome": outcome, "scenario_id": name} for name, outcome, error in RECOVERY],
        "summary": {"accepted_count": 1, "rejected_count": 13, "scenario_count": 14},
    }


def build_release(queue: Mapping[str, Any], holds: Mapping[str, Any], ledger: Mapping[str, Any], recovery: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifacts": {
            "ledger": {"path": "integration/principia-atlas/pilot/thermal-control.policy-ledger.v01.json", "sha256": sha256_document(ledger)},
            "recovery": {"path": "integration/principia-atlas/pilot/thermal-control.policy-recovery.v01.json", "sha256": sha256_document(recovery)},
            "release_hold_proposals": {"path": "integration/principia-atlas/pilot/thermal-control.release-hold-proposals.v01.json", "sha256": sha256_document(holds)},
            "review_queue": {"path": "integration/principia-atlas/pilot/thermal-control.policy-review-queue.v01.json", "sha256": sha256_document(queue)},
        },
        "authority": AUTHORITY,
        "contract": "principia-offline-reconciliation-policy/0.1",
        "id": "principia-atlas-offline-reconciliation-policy-thermal-control",
        "live": False,
        "live_activation_permitted": False,
        "mode": MODE,
        "next_gate": "offline-manual-policy-resolution-candidate",
        "phase": 19,
        "result": {"decision": "proposals-recorded-no-mutation", "effective_hold_count": 0, "hold_proposal_count": 1, "manual_review_item_count": 1, "unique_affected_artifact_count": 3},
        "source_phase18": source_block(),
        "state": "offline-reconciliation-policy-candidate",
        "validation": {"pull_request": None, "status": "pending", "tested_head_commit": None},
    }


def validate_authority(document: Mapping[str, Any]) -> None:
    if document.get("live") is not False:
        raise PolicyError("E-P19-LIVE-FROZEN")
    if document.get("authority") != AUTHORITY:
        raise PolicyError("E-P19-AUTHORITY")
    if find_prohibited(document):
        raise PolicyError("E-P19-STATUS-INHERITANCE")


def validate_set(items: Any) -> None:
    if not isinstance(items, list) or len(items) != 3 or {item.get("exact_key") for item in items if isinstance(item, Mapping)} != EXPECTED_ARTIFACT_KEYS:
        raise PolicyError("E-P19-AFFECTED-SET")


def validate_policy_bundle(queue: Mapping[str, Any], holds: Mapping[str, Any], ledger: Mapping[str, Any], recovery: Mapping[str, Any]) -> None:
    for document in (queue, holds, ledger, recovery):
        validate_authority(document)
    if queue.get("source") != source_block() or holds.get("source") != source_block() or ledger.get("source") != source_block():
        raise PolicyError("E-P19-SOURCE-PIN")
    queue_item = queue.get("items", [{}])[0]
    hold = holds.get("items", [{}])[0]
    if queue_item.get("required_action") != "revalidate" or queue_item.get("policy_action") != "manual-review":
        raise PolicyError("E-P19-ACTION-MAPPING")
    if hold.get("required_action") != "block-release" or hold.get("policy_action") != "propose-release-hold":
        raise PolicyError("E-P19-ACTION-MAPPING")
    if queue_item.get("automatic_execution") is not False or hold.get("automatic_execution") is not False:
        raise PolicyError("E-P19-AUTOMATIC-EXECUTION")
    if queue_item.get("requires_manual_resolution") is not True or hold.get("requires_manual_resolution") is not True:
        raise PolicyError("E-P19-MANUAL-RESOLUTION")
    if hold.get("effective") is not False:
        raise PolicyError("E-P19-HOLD-EFFECTIVE")
    validate_set(queue_item.get("affected_artifacts"))
    validate_set(hold.get("affected_artifacts"))
    if queue_item.get("queue_item_id") == hold.get("hold_id"):
        raise PolicyError("E-P19-DUPLICATE")
    expected_shas = [sha256_document(queue), sha256_document(holds)]
    previous = None
    entries = ledger.get("entries")
    if not isinstance(entries, list) or len(entries) != 2:
        raise PolicyError("E-P19-LEDGER-COUNT")
    for index, wrapper in enumerate(entries, 1):
        entry = wrapper.get("entry", {})
        if entry.get("sequence") != index or entry.get("previous_entry_sha256") != previous:
            raise PolicyError("E-P19-LEDGER-ORDER")
        if entry.get("policy_document_sha256") != expected_shas[index - 1] or wrapper.get("entry_sha256") != sha256_document(entry):
            raise PolicyError("E-P19-LEDGER-DIGEST")
        previous = wrapper["entry_sha256"]
    if ledger.get("head_sha256") != previous or ledger.get("decision") != "proposals-recorded-no-mutation":
        raise PolicyError("E-P19-LEDGER-HEAD")
    if recovery != build_recovery(queue, holds, ledger):
        raise PolicyError("E-P19-RECOVERY")


def build_bundle() -> dict[Path, dict[str, Any]]:
    records = source_records()
    queue = build_queue(records[0])
    holds = build_holds(records[1])
    ledger = build_ledger(queue, holds)
    recovery = build_recovery(queue, holds, ledger)
    validate_policy_bundle(queue, holds, ledger, recovery)
    return {
        REVIEW_QUEUE_PATH: queue,
        HOLD_PROPOSALS_PATH: holds,
        LEDGER_PATH: ledger,
        RECOVERY_PATH: recovery,
        RELEASE_PATH: build_release(queue, holds, ledger, recovery),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        outputs = build_bundle()
        mismatches = []
        for path, value in outputs.items():
            expected = render_json(value)
            if args.write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(expected, encoding="utf-8")
                print(f"wrote={path.relative_to(ROOT)}")
            elif not path.is_file() or path.read_text(encoding="utf-8") != expected:
                mismatches.append(path.relative_to(ROOT).as_posix())
        if mismatches:
            print("Phase 19 generated artifact drift: " + ", ".join(mismatches))
            return 1
        if args.check:
            print("Phase 19 generated artifacts are deterministic and current.")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, PolicyError, ValueError) as exc:
        print(f"Phase 19 generator error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
