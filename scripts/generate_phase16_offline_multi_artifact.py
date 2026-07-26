#!/usr/bin/env python3
"""Generate or verify Phase 16 offline multi-artifact integration evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
PILOT_ROOT = ROOT / "integration" / "principia-atlas" / "pilot"
SNAPSHOT_PATH = PILOT_ROOT / "atlas-phase2-importer.snapshot.v02.json"
BATCH_PATH = PILOT_ROOT / "thermal-control.multi-artifact.batch.v02.json"
RECEIPT_PATH = PILOT_ROOT / "thermal-control.multi-artifact.receipt.v02.json"
CHAIN_PATH = PILOT_ROOT / "thermal-control.receipt-chain.v02.json"
IMPACT_PATH = PILOT_ROOT / "thermal-control.lifecycle-matrix.v02.json"
RECOVERY_PATH = PILOT_ROOT / "thermal-control.recovery-matrix.v02.json"

EXPORT_PATHS = {
    "principia:failure-pattern:feedback-instability": (
        ROOT / "integration/principia-atlas/exports/feedback-instability.external-dependent.fixture.json"
    ),
    "principia:investigation:room-cooling": (
        ROOT / "integration/principia-atlas/exports/room-cooling.external-dependent.fixture.json"
    ),
    "principia:system-dossier:refrigerator": (
        ROOT / "integration/principia-atlas/exports/refrigerator.external-dependent.fixture.json"
    ),
}

EXPECTED_DEPENDENCIES = {
    "principia:failure-pattern:feedback-instability": {
        "claim:en:model-oscillation-does-not-prove-real-system": 1,
        "concept:en:feedback": 1,
        "concept:en:oscillation": 1,
        "model:en:delayed-correction-recurrence": 2,
    },
    "principia:investigation:room-cooling": {
        "claim:en:model-oscillation-does-not-prove-real-system": 1,
        "concept:en:feedback": 1,
        "concept:en:oscillation": 1,
    },
    "principia:system-dossier:refrigerator": {
        "claim:en:model-oscillation-does-not-prove-real-system": 1,
        "concept:en:feedback": 1,
        "concept:en:oscillation": 1,
    },
}

PROHIBITED_STATUS_KEYS = {
    "status",
    "pedagogical_status",
    "release_status",
    "knowledge_status",
    "atlas_status",
    "review_status",
}
ACTION_RANK = {"inspect": 0, "revalidate": 1, "block-release": 2}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def render_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_document(value: Mapping[str, Any]) -> str:
    return sha256_bytes(render_json(value).encode("utf-8"))


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


def validate_snapshot(snapshot: Mapping[str, Any]) -> None:
    if snapshot.get("contract") != "principia-atlas-offline-importer-snapshot/0.2":
        raise ValueError("E-P16-SNAPSHOT-CONTRACT")
    if snapshot.get("atlas_repository") != "Rhodan-lab/Atlas":
        raise ValueError("E-P16-SNAPSHOT-REPOSITORY")
    if snapshot.get("mode") != "offline-importer-snapshot" or snapshot.get("live") is not False:
        raise ValueError("E-P16-SNAPSHOT-LIVE")
    implementation = snapshot.get("implementation")
    governance = snapshot.get("governance_finalization")
    if not isinstance(implementation, Mapping) or not isinstance(governance, Mapping):
        raise ValueError("E-P16-SNAPSHOT-PIN")
    expected_implementation = {
        "pull_request": 20,
        "tested_head_commit": "379d88d620469a749cebb88b0b41d9960e667558",
        "merge_commit": "1cc4aec6908a8703a7f505478329c633a23b4ef9",
    }
    expected_governance = {
        "pull_request": 21,
        "head_commit": "c30bebf6a63263da8a4356f6c4dbc85f11a67bc4",
        "merge_commit": "9370cc746e9756e433ac3772d56d079c9803b144",
        "state": "accepted",
        "mode": "importer-candidate",
    }
    if dict(implementation) != expected_implementation or dict(governance) != expected_governance:
        raise ValueError("E-P16-SNAPSHOT-PIN")
    if snapshot.get("accepted_wire_contract") != "principia-atlas-external-dependent/0.2":
        raise ValueError("E-P16-SNAPSHOT-WIRE")
    capabilities = snapshot.get("capabilities")
    if not isinstance(capabilities, Mapping):
        raise ValueError("E-P16-SNAPSHOT-CAPABILITIES")
    for key in (
        "exact_revision_resolution",
        "legacy_index_verification",
        "status_inheritance_rejected",
        "live_true_rejected",
    ):
        if capabilities.get(key) is not True:
            raise ValueError(f"E-P16-SNAPSHOT-CAPABILITY:{key}")
    for key in ("automatic_status_change", "automatic_release_action"):
        if capabilities.get(key) is not False:
            raise ValueError(f"E-P16-SNAPSHOT-AUTHORITY:{key}")


def validate_export(artifact_id: str, export: Mapping[str, Any]) -> None:
    if export.get("contract") != "principia-atlas-external-dependent/0.2":
        raise ValueError(f"E-P16-EXPORT-CONTRACT:{artifact_id}")
    if export.get("id") != artifact_id or export.get("repository") != "Rhodan-lab/principle-to-system":
        raise ValueError(f"E-P16-EXPORT-IDENTITY:{artifact_id}")
    if export.get("revision") != 1:
        raise ValueError(f"E-P16-EXPORT-REVISION:{artifact_id}")
    if export.get("bridge_mode") != "bridge-candidate" or export.get("live") is not False:
        raise ValueError(f"E-P16-EXPORT-LIVE:{artifact_id}")
    prohibited = find_prohibited_status(export)
    if prohibited:
        raise ValueError(f"E-P16-EXPORT-STATUS:{artifact_id}:{prohibited}")
    exact = export.get("depends_on_exact")
    legacy = export.get("depends_on")
    if not isinstance(exact, list) or not isinstance(legacy, list):
        raise ValueError(f"E-P16-EXPORT-SHAPE:{artifact_id}")
    observed: dict[str, int] = {}
    exact_ids: list[str] = []
    for item in exact:
        if not isinstance(item, Mapping):
            raise ValueError(f"E-P16-EXPORT-DEPENDENCY:{artifact_id}")
        entity_id = item.get("id")
        revision = item.get("revision")
        if not isinstance(entity_id, str) or not isinstance(revision, int):
            raise ValueError(f"E-P16-EXPORT-DEPENDENCY:{artifact_id}")
        if entity_id in observed:
            raise ValueError(f"E-P16-EXPORT-DUPLICATE:{artifact_id}:{entity_id}")
        observed[entity_id] = revision
        exact_ids.append(entity_id)
    if observed != EXPECTED_DEPENDENCIES[artifact_id]:
        raise ValueError(f"E-P16-EXPORT-DEPENDENCY-MAP:{artifact_id}")
    if legacy != exact_ids or legacy != sorted(legacy):
        raise ValueError(f"E-P16-EXPORT-INDEX:{artifact_id}")


def operational_record(export: Mapping[str, Any], snapshot: Mapping[str, Any]) -> dict[str, Any]:
    dependencies = []
    for item in export["depends_on_exact"]:
        dependencies.append(
            {
                "id": item["id"],
                "revision": item["revision"],
                "key": f"{item['id']}@{item['revision']}",
                "entity_type": item["entity_type"],
                "role": item["role"],
                "use": item["use"],
                "change_policy": item["change_policy"],
                "resolution": "current",
            }
        )
    return {
        "contract": snapshot["operational_record_contract"],
        "source_contract": export["contract"],
        "adapter_contract": snapshot["adapter_contract"],
        "source_shape": "depends_on+depends_on_exact",
        "legacy_id_index_verified": True,
        "mode": export["bridge_mode"],
        "live": False,
        "id": export["id"],
        "kind": export["kind"],
        "repository": export["repository"],
        "revision": export["revision"],
        "role": export["role"],
        "dependencies": sorted(
            dependencies,
            key=lambda item: (str(item["id"]), int(item["revision"])),
        ),
        "status_inheritance": "prohibited",
    }


def build_batch(exports: Mapping[str, Mapping[str, Any]], snapshot: Mapping[str, Any]) -> dict[str, Any]:
    validate_snapshot(snapshot)
    inputs = []
    for artifact_id in sorted(exports):
        export = exports[artifact_id]
        validate_export(artifact_id, export)
        path = EXPORT_PATHS[artifact_id]
        inputs.append(
            {
                "artifact_id": artifact_id,
                "artifact_revision": export["revision"],
                "export_path": path.relative_to(ROOT).as_posix(),
                "export_sha256": sha256_file(path),
                "dependency_count": len(export["depends_on_exact"]),
            }
        )
    return {
        "contract": "principia-atlas-offline-import-batch/0.2",
        "batch_id": "principia-atlas:offline-batch:thermal-control:0001",
        "sequence": 1,
        "previous_receipt_sha256": None,
        "mode": "offline-multi-artifact-pilot",
        "live": False,
        "atomic": True,
        "atlas_snapshot": {
            "path": SNAPSHOT_PATH.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(SNAPSHOT_PATH),
            "implementation_pull_request": snapshot["implementation"]["pull_request"],
            "implementation_merge_commit": snapshot["implementation"]["merge_commit"],
            "governance_pull_request": snapshot["governance_finalization"]["pull_request"],
            "governance_merge_commit": snapshot["governance_finalization"]["merge_commit"],
        },
        "inputs": inputs,
    }


def build_receipt(batch: Mapping[str, Any], exports: Mapping[str, Mapping[str, Any]], snapshot: Mapping[str, Any]) -> dict[str, Any]:
    records = [operational_record(exports[artifact_id], snapshot) for artifact_id in sorted(exports)]
    return {
        "contract": "principia-atlas-offline-batch-receipt/0.2",
        "receipt_id": "principia-atlas:offline-receipt:thermal-control:0001",
        "batch_id": batch["batch_id"],
        "sequence": batch["sequence"],
        "previous_receipt_sha256": batch["previous_receipt_sha256"],
        "batch_sha256": sha256_document(batch),
        "mode": batch["mode"],
        "live": False,
        "atlas_importer": {
            "repository": snapshot["atlas_repository"],
            "implementation": snapshot["implementation"],
            "governance_finalization": snapshot["governance_finalization"],
            "accepted_wire_contract": snapshot["accepted_wire_contract"],
            "adapter_contract": snapshot["adapter_contract"],
            "operational_record_contract": snapshot["operational_record_contract"],
        },
        "result": {
            "accepted": True,
            "atomic": True,
            "accepted_count": len(records),
            "rejected_count": 0,
            "status_inheritance": "prohibited",
            "records": records,
        },
        "authority": {
            "atlas_knowledge_status_authority": "Atlas",
            "principia_pedagogical_status_authority": "Principia",
            "principia_release_status_authority": "Principia",
            "automatic_status_change": False,
            "automatic_release_action": False,
            "repository_mutation": False,
        },
    }


def effective_action(declared: str, lifecycle_status: str, staleness: str) -> tuple[str, str]:
    if declared not in ACTION_RANK:
        raise ValueError(f"E-P16-ACTION:{declared}")
    if lifecycle_status == "retracted":
        return "block-release", "atlas-entity-retracted"
    effective = declared
    reason = "principia-declared-policy"
    if lifecycle_status == "deprecated" and ACTION_RANK[effective] < ACTION_RANK["revalidate"]:
        effective = "revalidate"
        reason = "atlas-entity-deprecated"
    if staleness in {"review-required", "confirmed-stale"} and ACTION_RANK[effective] < ACTION_RANK["revalidate"]:
        effective = "revalidate"
        reason = f"atlas-staleness-{staleness}"
    return effective, reason


def impacted_records(exports: Mapping[str, Mapping[str, Any]], entity_id: str, lifecycle_status: str, staleness: str) -> list[dict[str, Any]]:
    records = []
    for artifact_id in sorted(exports):
        export = exports[artifact_id]
        for dependency in export["depends_on_exact"]:
            if dependency["id"] != entity_id:
                continue
            effective, reason = effective_action(str(dependency["change_policy"]), lifecycle_status, staleness)
            records.append(
                {
                    "artifact_id": artifact_id,
                    "artifact_revision": export["revision"],
                    "declared_action": dependency["change_policy"],
                    "effective_action": effective,
                    "reason": reason,
                }
            )
    return records


def build_lifecycle_matrix(exports: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    definitions = [
        ("claim-current", "claim:en:model-oscillation-does-not-prove-real-system", 1, "draft", "current"),
        ("feedback-deprecated", "concept:en:feedback", 1, "deprecated", "current"),
        ("oscillation-confirmed-stale", "concept:en:oscillation", 1, "draft", "confirmed-stale"),
        ("model-current", "model:en:delayed-correction-recurrence", 2, "draft", "current"),
        ("model-retracted", "model:en:delayed-correction-recurrence", 2, "retracted", "current"),
        ("claim-retracted", "claim:en:model-oscillation-does-not-prove-real-system", 1, "retracted", "current"),
    ]
    scenarios = []
    for scenario_id, entity_id, revision, lifecycle_status, staleness in definitions:
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "entity": {
                    "id": entity_id,
                    "revision": revision,
                    "status": lifecycle_status,
                    "staleness": staleness,
                },
                "external_dependents": impacted_records(exports, entity_id, lifecycle_status, staleness),
                "automatic_status_change": False,
                "automatic_release_action": False,
            }
        )
    return {
        "contract": "principia-atlas-offline-multi-impact-matrix/0.2",
        "pilot_id": "principia-atlas:offline-multi-artifact:thermal-control",
        "mode": "offline-multi-artifact-pilot",
        "live": False,
        "scenarios": scenarios,
    }


def build_chain(receipt: Mapping[str, Any]) -> dict[str, Any]:
    digest = sha256_document(receipt)
    return {
        "contract": "principia-atlas-offline-receipt-chain/0.2",
        "chain_id": "principia-atlas:offline-receipt-chain:thermal-control",
        "mode": "offline-multi-artifact-pilot",
        "live": False,
        "head_sequence": 1,
        "head_receipt_sha256": digest,
        "entries": [
            {
                "sequence": 1,
                "receipt_path": RECEIPT_PATH.relative_to(ROOT).as_posix(),
                "receipt_sha256": digest,
                "previous_receipt_sha256": None,
            }
        ],
    }


def build_recovery_matrix(batch: Mapping[str, Any], receipt: Mapping[str, Any]) -> dict[str, Any]:
    receipt_digest = sha256_document(receipt)
    batch_digest = sha256_document(batch)
    scenarios = [
        {"scenario_id": "duplicate-replay", "sequence": 1, "previous_receipt_sha256": None, "batch_sha256": batch_digest, "outcome": "idempotent-noop", "accepted": True, "error_code": None},
        {"scenario_id": "stale-sequence", "sequence": 0, "previous_receipt_sha256": None, "batch_sha256": batch_digest, "outcome": "rejected", "accepted": False, "error_code": "E-RECEIPT-SEQUENCE"},
        {"scenario_id": "skipped-sequence", "sequence": 3, "previous_receipt_sha256": receipt_digest, "batch_sha256": batch_digest, "outcome": "rejected", "accepted": False, "error_code": "E-RECEIPT-SEQUENCE"},
        {"scenario_id": "wrong-predecessor", "sequence": 2, "previous_receipt_sha256": "0" * 64, "batch_sha256": batch_digest, "outcome": "rejected", "accepted": False, "error_code": "E-RECEIPT-PREVIOUS-DIGEST"},
        {"scenario_id": "valid-next-checkpoint", "sequence": 2, "previous_receipt_sha256": receipt_digest, "batch_sha256": batch_digest, "outcome": "accepted-recovery-checkpoint", "accepted": True, "error_code": None},
        {"scenario_id": "partial-batch", "sequence": 2, "previous_receipt_sha256": receipt_digest, "batch_sha256": batch_digest, "outcome": "rejected", "accepted": False, "error_code": "E-BATCH-ATOMICITY"},
        {"scenario_id": "export-digest-corruption", "sequence": 2, "previous_receipt_sha256": receipt_digest, "batch_sha256": "f" * 64, "outcome": "rejected", "accepted": False, "error_code": "E-BATCH-DIGEST"},
        {"scenario_id": "status-inheritance-injection", "sequence": 2, "previous_receipt_sha256": receipt_digest, "batch_sha256": batch_digest, "outcome": "rejected", "accepted": False, "error_code": "E-BATCH-STATUS-INHERITANCE"},
        {"scenario_id": "live-activation", "sequence": 2, "previous_receipt_sha256": receipt_digest, "batch_sha256": batch_digest, "outcome": "rejected", "accepted": False, "error_code": "E-BATCH-LIVE-FROZEN"},
    ]
    return {
        "contract": "principia-atlas-offline-recovery-matrix/0.2",
        "pilot_id": "principia-atlas:offline-multi-artifact:thermal-control",
        "mode": "offline-multi-artifact-pilot",
        "live": False,
        "current_head": {"sequence": 1, "receipt_sha256": receipt_digest},
        "expected_next_sequence": 2,
        "scenarios": scenarios,
        "automatic_status_change": False,
        "automatic_release_action": False,
        "repository_mutation": False,
    }


def generated_documents() -> dict[Path, dict[str, Any]]:
    snapshot = load_json(SNAPSHOT_PATH)
    exports = {artifact_id: load_json(path) for artifact_id, path in EXPORT_PATHS.items()}
    batch = build_batch(exports, snapshot)
    receipt = build_receipt(batch, exports, snapshot)
    return {
        BATCH_PATH: batch,
        RECEIPT_PATH: receipt,
        CHAIN_PATH: build_chain(receipt),
        IMPACT_PATH: build_lifecycle_matrix(exports),
        RECOVERY_PATH: build_recovery_matrix(batch, receipt),
    }


def write_outputs() -> None:
    for path, value in generated_documents().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_json(value), encoding="utf-8")
        print(f"wrote={path.relative_to(ROOT)}")


def check_outputs() -> int:
    failures = []
    for path, value in generated_documents().items():
        expected = render_json(value)
        actual = path.read_text(encoding="utf-8") if path.is_file() else ""
        if actual != expected:
            failures.append(path.relative_to(ROOT).as_posix())
    if failures:
        print("Phase 16 generated artifacts are stale:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Phase 16 deterministic batch, receipt chain, lifecycle matrix, and recovery matrix are current.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_outputs()
        return 0
    return check_outputs()


if __name__ == "__main__":
    raise SystemExit(main())
