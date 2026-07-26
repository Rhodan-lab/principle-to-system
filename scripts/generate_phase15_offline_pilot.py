#!/usr/bin/env python3
"""Generate or verify the Phase 15 offline Principia–Atlas pilot artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
EXPORT_PATH = ROOT / "integration/principia-atlas/exports/feedback-instability.external-dependent.fixture.json"
SNAPSHOT_PATH = ROOT / "integration/principia-atlas/pilot/atlas-phase2-importer.snapshot.json"
RECEIPT_PATH = ROOT / "integration/principia-atlas/pilot/feedback-instability.import-receipt.json"
IMPACT_PATH = ROOT / "integration/principia-atlas/pilot/feedback-instability.lifecycle-matrix.json"

EXPECTED_DEPENDENCIES = {
    "claim:en:model-oscillation-does-not-prove-real-system": 1,
    "concept:en:feedback": 1,
    "concept:en:oscillation": 1,
    "model:en:delayed-correction-recurrence": 2,
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def render_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_inputs(export: Mapping[str, Any], snapshot: Mapping[str, Any]) -> None:
    if export.get("contract") != "principia-atlas-external-dependent/0.2":
        raise ValueError("E-EXPORT-CONTRACT")
    if export.get("bridge_mode") != "bridge-candidate" or export.get("live") is not False:
        raise ValueError("E-EXPORT-STATE")
    if snapshot.get("contract") != "principia-atlas-offline-importer-snapshot/0.1":
        raise ValueError("E-SNAPSHOT-CONTRACT")
    if snapshot.get("live") is not False:
        raise ValueError("E-SNAPSHOT-LIVE")
    principia_source = snapshot.get("principia_source")
    if not isinstance(principia_source, Mapping):
        raise ValueError("E-SNAPSHOT-SOURCE")
    if principia_source.get("sha256") != sha256_file(EXPORT_PATH):
        raise ValueError("E-EXPORT-DIGEST")
    exact = export.get("depends_on_exact")
    legacy = export.get("depends_on")
    if not isinstance(exact, list) or not isinstance(legacy, list):
        raise ValueError("E-DEPENDENCY-SHAPE")
    exact_map: dict[str, int] = {}
    exact_ids: list[str] = []
    for dependency in exact:
        if not isinstance(dependency, Mapping):
            raise ValueError("E-DEPENDENCY-OBJECT")
        entity_id = dependency.get("id")
        revision = dependency.get("revision")
        if not isinstance(entity_id, str) or not isinstance(revision, int):
            raise ValueError("E-DEPENDENCY-EXACT")
        exact_map[entity_id] = revision
        exact_ids.append(entity_id)
    if exact_map != EXPECTED_DEPENDENCIES:
        raise ValueError("E-DEPENDENCY-REVISION-MAP")
    if legacy != exact_ids or legacy != sorted(legacy):
        raise ValueError("E-DEPENDENCY-INDEX")


def build_receipt(export: Mapping[str, Any], snapshot: Mapping[str, Any]) -> dict[str, Any]:
    validate_inputs(export, snapshot)
    dependencies = []
    for dependency in export["depends_on_exact"]:
        dependencies.append(
            {
                "id": dependency["id"],
                "revision": dependency["revision"],
                "key": f"{dependency['id']}@{dependency['revision']}",
                "entity_type": dependency["entity_type"],
                "role": dependency["role"],
                "use": dependency["use"],
                "change_policy": dependency["change_policy"],
                "resolution": "current",
            }
        )
    return {
        "contract": "principia-atlas-offline-import-receipt/0.1",
        "pilot_id": "principia-atlas:offline-pilot:feedback-instability",
        "mode": "offline-pilot",
        "live": False,
        "input": {
            "contract": export["contract"],
            "path": EXPORT_PATH.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(EXPORT_PATH),
            "artifact_id": export["id"],
            "artifact_revision": export["revision"],
        },
        "atlas_importer": {
            "repository": snapshot["atlas_repository"],
            "pull_request": snapshot["source_pull_request"],
            "head_commit": snapshot["source_head_commit"],
            "merge_commit": snapshot["source_merge_commit"],
            "accepted_wire_contract": snapshot["accepted_wire_contract"],
            "adapter_contract": snapshot["adapter_contract"],
            "operational_record_contract": snapshot["operational_record_contract"],
        },
        "result": {
            "accepted": True,
            "operational_record_contract": snapshot["operational_record_contract"],
            "source_contract": export["contract"],
            "adapter_contract": snapshot["adapter_contract"],
            "source_shape": "depends_on+depends_on_exact",
            "legacy_id_index_verified": True,
            "status_inheritance": "prohibited",
            "dependencies": dependencies,
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


def build_lifecycle_matrix(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    capabilities = snapshot["capabilities"]
    scenarios = [
        {
            "atlas_entity_state": "current",
            "atlas_staleness": "current",
            "declared_action": "inspect",
            "effective_action": "inspect",
            "reason": "principia-declared-policy",
        },
        {
            "atlas_entity_state": "deprecated",
            "atlas_staleness": "current",
            "declared_action": "inspect",
            "effective_action": capabilities["deprecated_escalates_to"],
            "reason": "atlas-entity-deprecated",
        },
        {
            "atlas_entity_state": "draft",
            "atlas_staleness": "review-required",
            "declared_action": "inspect",
            "effective_action": capabilities["review_required_stale_escalates_to"],
            "reason": "atlas-staleness-review-required",
        },
        {
            "atlas_entity_state": "draft",
            "atlas_staleness": "confirmed-stale",
            "declared_action": "inspect",
            "effective_action": capabilities["confirmed_stale_escalates_to"],
            "reason": "atlas-staleness-confirmed-stale",
        },
        {
            "atlas_entity_state": "retracted",
            "atlas_staleness": "current",
            "declared_action": "inspect",
            "effective_action": capabilities["retracted_escalates_to"],
            "reason": "atlas-entity-retracted",
        },
    ]
    return {
        "contract": "principia-atlas-offline-lifecycle-matrix/0.1",
        "pilot_id": "principia-atlas:offline-pilot:feedback-instability",
        "target": "model:en:delayed-correction-recurrence@2",
        "mode": "offline-pilot",
        "live": False,
        "scenarios": scenarios,
        "automatic_status_change": False,
        "automatic_release_action": False,
    }


def generated_documents() -> dict[Path, dict[str, Any]]:
    export = load_json(EXPORT_PATH)
    snapshot = load_json(SNAPSHOT_PATH)
    return {
        RECEIPT_PATH: build_receipt(export, snapshot),
        IMPACT_PATH: build_lifecycle_matrix(snapshot),
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
        print("Phase 15 generated artifacts are stale:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Phase 15 deterministic receipt and lifecycle matrix are current.")
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
