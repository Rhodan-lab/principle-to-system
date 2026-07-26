#!/usr/bin/env python3
"""Validate the Phase 16 offline multi-artifact pilot."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Mapping

from export_principia_atlas_dependents import build_export, render
from generate_phase16_offline_multi_artifact import (
    BATCH_PATH,
    CHAIN_PATH,
    EXPECTED_DEPENDENCIES,
    EXPORT_PATHS,
    IMPACT_PATH,
    RECEIPT_PATH,
    RECOVERY_PATH,
    ROOT,
    SNAPSHOT_PATH,
    check_outputs,
    find_prohibited_status,
    load_json,
    sha256_document,
    sha256_file,
    validate_export,
    validate_snapshot,
)

MANIFEST_EXPORTS = {
    ROOT / "integration/principia-atlas/manifests/feedback-instability.fixture.json":
        ROOT / "integration/principia-atlas/exports/feedback-instability.external-dependent.fixture.json",
    ROOT / "integration/principia-atlas/manifests/refrigerator.fixture.json":
        ROOT / "integration/principia-atlas/exports/refrigerator.external-dependent.fixture.json",
    ROOT / "integration/principia-atlas/manifests/room-cooling.fixture.json":
        ROOT / "integration/principia-atlas/exports/room-cooling.external-dependent.fixture.json",
}
ARTIFACT_PATHS = {
    "principia:failure-pattern:feedback-instability": ROOT / "failure-atlas/feedback-instability.md",
    "principia:investigation:room-cooling": ROOT / "investigations/room-cooling.md",
    "principia:system-dossier:refrigerator": ROOT / "system-dossiers/refrigerator.md",
}
RELEASE_PATH = ROOT / "release/phase-16-offline-multi-artifact-pilot.json"
REPORT_PATH = ROOT / "reports/phase-16-offline-multi-artifact-pilot.md"
WORKFLOW_PATH = ROOT / ".github/workflows/validate-phase-16-offline-multi-artifact.yml"
PROJECT_STATE_PATH = ROOT / "PROJECT_STATE.md"
README_PATH = ROOT / "integration/principia-atlas/README.md"

EXPECTED_RECOVERY = {
    "duplicate-replay": (True, "idempotent-noop", None),
    "stale-sequence": (False, "rejected", "E-RECEIPT-SEQUENCE"),
    "skipped-sequence": (False, "rejected", "E-RECEIPT-SEQUENCE"),
    "wrong-predecessor": (False, "rejected", "E-RECEIPT-PREVIOUS-DIGEST"),
    "valid-next-checkpoint": (True, "accepted-recovery-checkpoint", None),
    "partial-batch": (False, "rejected", "E-BATCH-ATOMICITY"),
    "export-digest-corruption": (False, "rejected", "E-BATCH-DIGEST"),
    "status-inheritance-injection": (False, "rejected", "E-BATCH-STATUS-INHERITANCE"),
    "live-activation": (False, "rejected", "E-BATCH-LIVE-FROZEN"),
}
EXPECTED_IMPACT = {
    "claim-current": (3, {"block-release"}),
    "feedback-deprecated": (3, {"revalidate"}),
    "oscillation-confirmed-stale": (3, {"revalidate"}),
    "model-current": (1, {"inspect"}),
    "model-retracted": (1, {"block-release"}),
    "claim-retracted": (3, {"block-release"}),
}


def parse_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError(f"E-P16-FRONTMATTER:{path.relative_to(ROOT)}")
    end = text.find("\n---\n", 4)
    result: dict[str, object] = {}
    for raw in text[4:end].splitlines():
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        scalar = value.strip().strip('"').strip("'")
        result[key.strip()] = int(scalar) if scalar.isdigit() else scalar
    return result


def validate_manifest_export_pairs() -> None:
    for manifest_path, export_path in MANIFEST_EXPORTS.items():
        manifest = load_json(manifest_path)
        export = load_json(export_path)
        if manifest.get("mode") != "bridge-candidate" or manifest.get("live") is not False:
            raise ValueError(f"E-P16-MANIFEST-LIVE:{manifest_path.name}")
        if export_path.read_text(encoding="utf-8") != render(build_export(manifest)):
            raise ValueError(f"E-P16-EXPORT-STALE:{export_path.name}")
        artifact = manifest.get("principia")
        if not isinstance(artifact, Mapping):
            raise ValueError(f"E-P16-MANIFEST-ARTIFACT:{manifest_path.name}")
        artifact_id = artifact.get("artifact_id")
        artifact_path = artifact.get("path")
        if artifact_id not in ARTIFACT_PATHS or not isinstance(artifact_path, str):
            raise ValueError(f"E-P16-MANIFEST-ARTIFACT:{manifest_path.name}")
        if ARTIFACT_PATHS[str(artifact_id)] != ROOT / artifact_path:
            raise ValueError(f"E-P16-MANIFEST-PATH:{manifest_path.name}")
        metadata = parse_frontmatter(ROOT / artifact_path)
        comparisons = (
            ("artifact_revision", "artifact_revision", "REVISION"),
            ("pedagogical_status", "status", "PEDAGOGY"),
            ("release_status", "release_status", "RELEASE"),
        )
        for manifest_key, metadata_key, code in comparisons:
            if artifact.get(manifest_key) != metadata.get(metadata_key):
                raise ValueError(f"E-P16-MANIFEST-{code}:{manifest_path.name}")
        validate_export(str(artifact_id), export)


def validate_batch_payload(batch: Mapping[str, Any]) -> None:
    if batch.get("contract") != "principia-atlas-offline-import-batch/0.2":
        raise ValueError("E-P16-BATCH-CONTRACT")
    if batch.get("mode") != "offline-multi-artifact-pilot" or batch.get("live") is not False:
        raise ValueError("E-P16-BATCH-LIVE")
    if batch.get("sequence") != 1 or batch.get("previous_receipt_sha256") is not None:
        raise ValueError("E-P16-BATCH-SEQUENCE")
    if batch.get("atomic") is not True:
        raise ValueError("E-P16-BATCH-ATOMICITY")
    prohibited = find_prohibited_status(batch)
    if prohibited:
        raise ValueError(f"E-P16-BATCH-STATUS:{prohibited}")
    inputs = batch.get("inputs")
    if not isinstance(inputs, list) or len(inputs) != 3:
        raise ValueError("E-P16-BATCH-ATOMICITY")
    observed_ids = []
    for item in inputs:
        if not isinstance(item, Mapping) or item.get("artifact_id") not in EXPORT_PATHS:
            raise ValueError("E-P16-BATCH-INPUT")
        artifact_id = str(item["artifact_id"])
        path = EXPORT_PATHS[artifact_id]
        if item.get("export_path") != path.relative_to(ROOT).as_posix():
            raise ValueError("E-P16-BATCH-PATH")
        if item.get("export_sha256") != sha256_file(path):
            raise ValueError("E-P16-BATCH-DIGEST")
        if item.get("dependency_count") != len(EXPECTED_DEPENDENCIES[artifact_id]):
            raise ValueError("E-P16-BATCH-DEPENDENCY-COUNT")
        observed_ids.append(artifact_id)
    if observed_ids != sorted(EXPORT_PATHS):
        raise ValueError("E-P16-BATCH-ORDER")
    snapshot = batch.get("atlas_snapshot")
    if not isinstance(snapshot, Mapping) or snapshot.get("sha256") != sha256_file(SNAPSHOT_PATH):
        raise ValueError("E-P16-BATCH-SNAPSHOT")


def validate_receipt_payload(receipt: Mapping[str, Any], batch: Mapping[str, Any]) -> None:
    if receipt.get("contract") != "principia-atlas-offline-batch-receipt/0.2":
        raise ValueError("E-P16-RECEIPT-CONTRACT")
    if receipt.get("mode") != "offline-multi-artifact-pilot" or receipt.get("live") is not False:
        raise ValueError("E-P16-RECEIPT-LIVE")
    if receipt.get("sequence") != 1 or receipt.get("previous_receipt_sha256") is not None:
        raise ValueError("E-P16-RECEIPT-SEQUENCE")
    if receipt.get("batch_sha256") != sha256_document(batch):
        raise ValueError("E-P16-RECEIPT-BATCH-DIGEST")
    prohibited = find_prohibited_status(receipt)
    if prohibited:
        raise ValueError(f"E-P16-RECEIPT-STATUS:{prohibited}")
    result = receipt.get("result")
    if not isinstance(result, Mapping):
        raise ValueError("E-P16-RECEIPT-RESULT")
    if result.get("accepted") is not True or result.get("atomic") is not True:
        raise ValueError("E-P16-RECEIPT-RESULT")
    if result.get("accepted_count") != 3 or result.get("rejected_count") != 0:
        raise ValueError("E-P16-RECEIPT-COUNT")
    if result.get("status_inheritance") != "prohibited":
        raise ValueError("E-P16-RECEIPT-AUTHORITY")
    records = result.get("records")
    if not isinstance(records, list) or len(records) != 3:
        raise ValueError("E-P16-RECEIPT-COUNT")
    ids = []
    for record in records:
        if not isinstance(record, Mapping) or record.get("id") not in EXPECTED_DEPENDENCIES:
            raise ValueError("E-P16-RECEIPT-RECORD")
        artifact_id = str(record["id"])
        if record.get("contract") != "atlas-external-dependent/0.1":
            raise ValueError("E-P16-RECEIPT-RECORD-CONTRACT")
        if record.get("source_contract") != "principia-atlas-external-dependent/0.2":
            raise ValueError("E-P16-RECEIPT-SOURCE-CONTRACT")
        if record.get("status_inheritance") != "prohibited" or record.get("live") is not False:
            raise ValueError("E-P16-RECEIPT-AUTHORITY")
        dependencies = record.get("dependencies")
        if not isinstance(dependencies, list):
            raise ValueError("E-P16-RECEIPT-DEPENDENCIES")
        observed = {
            str(item.get("id")): item.get("revision")
            for item in dependencies
            if isinstance(item, Mapping)
        }
        if observed != EXPECTED_DEPENDENCIES[artifact_id]:
            raise ValueError("E-P16-RECEIPT-DEPENDENCIES")
        if any(item.get("resolution") != "current" for item in dependencies):
            raise ValueError("E-P16-RECEIPT-RESOLUTION")
        ids.append(artifact_id)
    if ids != sorted(EXPECTED_DEPENDENCIES):
        raise ValueError("E-P16-RECEIPT-ORDER")
    authority = receipt.get("authority")
    if not isinstance(authority, Mapping):
        raise ValueError("E-P16-RECEIPT-AUTHORITY")
    if any(authority.get(key) is not False for key in (
        "automatic_status_change", "automatic_release_action", "repository_mutation"
    )):
        raise ValueError("E-P16-RECEIPT-AUTHORITY")


def validate_chain(chain: Mapping[str, Any], receipt: Mapping[str, Any]) -> None:
    if chain.get("contract") != "principia-atlas-offline-receipt-chain/0.2":
        raise ValueError("E-P16-CHAIN-CONTRACT")
    if chain.get("mode") != "offline-multi-artifact-pilot" or chain.get("live") is not False:
        raise ValueError("E-P16-CHAIN-LIVE")
    digest = sha256_document(receipt)
    if chain.get("head_sequence") != 1 or chain.get("head_receipt_sha256") != digest:
        raise ValueError("E-P16-CHAIN-HEAD")
    entries = chain.get("entries")
    if not isinstance(entries, list) or len(entries) != 1:
        raise ValueError("E-P16-CHAIN-ENTRIES")
    entry = entries[0]
    if not isinstance(entry, Mapping):
        raise ValueError("E-P16-CHAIN-ENTRY")
    if entry.get("sequence") != 1 or entry.get("receipt_sha256") != digest:
        raise ValueError("E-P16-CHAIN-ENTRY")
    if entry.get("previous_receipt_sha256") is not None:
        raise ValueError("E-P16-CHAIN-ENTRY")


def validate_impact(matrix: Mapping[str, Any]) -> None:
    if matrix.get("contract") != "principia-atlas-offline-multi-impact-matrix/0.2":
        raise ValueError("E-P16-IMPACT-CONTRACT")
    if matrix.get("mode") != "offline-multi-artifact-pilot" or matrix.get("live") is not False:
        raise ValueError("E-P16-IMPACT-LIVE")
    scenarios = matrix.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != len(EXPECTED_IMPACT):
        raise ValueError("E-P16-IMPACT-SCENARIOS")
    observed = {}
    for scenario in scenarios:
        if not isinstance(scenario, Mapping):
            raise ValueError("E-P16-IMPACT-SCENARIO")
        if scenario.get("automatic_status_change") is not False:
            raise ValueError("E-P16-IMPACT-AUTHORITY")
        if scenario.get("automatic_release_action") is not False:
            raise ValueError("E-P16-IMPACT-AUTHORITY")
        dependents = scenario.get("external_dependents")
        if not isinstance(dependents, list):
            raise ValueError("E-P16-IMPACT-DEPENDENTS")
        actions = {
            str(item.get("effective_action"))
            for item in dependents
            if isinstance(item, Mapping)
        }
        observed[str(scenario.get("scenario_id"))] = (len(dependents), actions)
    if observed != EXPECTED_IMPACT:
        raise ValueError("E-P16-IMPACT-POLICY")


def validate_recovery(matrix: Mapping[str, Any], receipt: Mapping[str, Any]) -> None:
    if matrix.get("contract") != "principia-atlas-offline-recovery-matrix/0.2":
        raise ValueError("E-P16-RECOVERY-CONTRACT")
    if matrix.get("mode") != "offline-multi-artifact-pilot" or matrix.get("live") is not False:
        raise ValueError("E-P16-RECOVERY-LIVE")
    if matrix.get("expected_next_sequence") != 2:
        raise ValueError("E-P16-RECOVERY-SEQUENCE")
    head = matrix.get("current_head")
    if not isinstance(head, Mapping):
        raise ValueError("E-P16-RECOVERY-HEAD")
    if head.get("sequence") != 1 or head.get("receipt_sha256") != sha256_document(receipt):
        raise ValueError("E-P16-RECOVERY-HEAD")
    if any(matrix.get(key) is not False for key in (
        "automatic_status_change", "automatic_release_action", "repository_mutation"
    )):
        raise ValueError("E-P16-RECOVERY-AUTHORITY")
    scenarios = matrix.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != len(EXPECTED_RECOVERY):
        raise ValueError("E-P16-RECOVERY-SCENARIOS")
    observed = {}
    for scenario in scenarios:
        if not isinstance(scenario, Mapping):
            raise ValueError("E-P16-RECOVERY-SCENARIO")
        observed[str(scenario.get("scenario_id"))] = (
            scenario.get("accepted"), scenario.get("outcome"), scenario.get("error_code")
        )
    if observed != EXPECTED_RECOVERY:
        raise ValueError("E-P16-RECOVERY-POLICY")


def validate_negative_paths(batch: Mapping[str, Any], receipt: Mapping[str, Any]) -> None:
    cases = []
    live_batch = copy.deepcopy(batch)
    live_batch["live"] = True
    cases.append((validate_batch_payload, (live_batch,), "E-P16-BATCH-LIVE"))
    partial = copy.deepcopy(batch)
    partial["inputs"].pop()
    cases.append((validate_batch_payload, (partial,), "E-P16-BATCH-ATOMICITY"))
    inherited = copy.deepcopy(batch)
    inherited["pedagogical_status"] = "reviewed"
    cases.append((validate_batch_payload, (inherited,), "E-P16-BATCH-STATUS"))
    corrupt = copy.deepcopy(batch)
    corrupt["inputs"][0]["export_sha256"] = "0" * 64
    cases.append((validate_batch_payload, (corrupt,), "E-P16-BATCH-DIGEST"))
    live_receipt = copy.deepcopy(receipt)
    live_receipt["live"] = True
    cases.append((validate_receipt_payload, (live_receipt, batch), "E-P16-RECEIPT-LIVE"))
    short_receipt = copy.deepcopy(receipt)
    short_receipt["result"]["records"].pop()
    cases.append((validate_receipt_payload, (short_receipt, batch), "E-P16-RECEIPT-COUNT"))
    for function, args, expected in cases:
        try:
            function(*args)
        except ValueError as exc:
            if expected not in str(exc):
                raise ValueError(f"E-P16-NEGATIVE-EXPECTED:{expected}:got:{exc}") from exc
        else:
            raise ValueError(f"E-P16-NEGATIVE-ACCEPTED:{expected}")


def validate_records(errors: list[str]) -> None:
    required = [
        SNAPSHOT_PATH, BATCH_PATH, RECEIPT_PATH, CHAIN_PATH, IMPACT_PATH,
        RECOVERY_PATH, RELEASE_PATH, REPORT_PATH, WORKFLOW_PATH,
        PROJECT_STATE_PATH, README_PATH, *MANIFEST_EXPORTS.keys(),
        *MANIFEST_EXPORTS.values(),
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing Phase 16 file: {path.relative_to(ROOT)}")
    if errors:
        return
    try:
        validate_snapshot(load_json(SNAPSHOT_PATH))
        validate_manifest_export_pairs()
        batch = load_json(BATCH_PATH)
        receipt = load_json(RECEIPT_PATH)
        validate_batch_payload(batch)
        validate_receipt_payload(receipt, batch)
        validate_chain(load_json(CHAIN_PATH), receipt)
        validate_impact(load_json(IMPACT_PATH))
        validate_recovery(load_json(RECOVERY_PATH), receipt)
        validate_negative_paths(batch, receipt)
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(str(exc))

    release = load_json(RELEASE_PATH)
    expected_release = {
        "phase": 16,
        "state": "offline-multi-artifact-validated",
        "mode": "offline-multi-artifact-pilot",
        "live": False,
    }
    for key, expected in expected_release.items():
        if release.get(key) != expected:
            errors.append(f"release/phase-16 record has invalid {key}")
    validation = release.get("validation")
    if not isinstance(validation, Mapping):
        errors.append("release/phase-16 validation record is missing")
    else:
        expected_validation = {
            "status": "success",
            "pull_request": 20,
            "tested_head_commit": "67d6ec98c51188dabcffd48dad968a83653ea584",
            "merge_commit": None,
        }
        for key, expected in expected_validation.items():
            if validation.get(key) != expected:
                errors.append(f"release/phase-16 validation has invalid {key}")

    state = PROJECT_STATE_PATH.read_text(encoding="utf-8")
    for marker in (
        "Phase 16 — Offline Multi-Artifact Integration Pilot",
        "offline-multi-artifact-validated",
        "live: false",
        "Atlas PR #21",
        "67d6ec98c51188dabcffd48dad968a83653ea584",
    ):
        if marker not in state:
            errors.append(f"PROJECT_STATE.md missing Phase 16 marker: {marker}")

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in (
        "principia-atlas-offline-batch-receipt/0.2",
        "9370cc746e9756e433ac3772d56d079c9803b144",
        "67d6ec98c51188dabcffd48dad968a83653ea584",
        "No live cross-repository call",
    ):
        if marker not in report:
            errors.append(f"Phase 16 report missing marker: {marker}")

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    if "contents: read" not in workflow:
        errors.append("Phase 16 workflow must use contents: read")
    forbidden = (
        "contents" + ": write", "git " + "push", "git " + "commit",
        "pull_request" + "_target", "repository: Rhodan-lab/Atlas",
        "curl ", "wget ",
    )
    for token in forbidden:
        if token in workflow:
            errors.append(f"Phase 16 workflow contains forbidden token: {token}")


def main() -> int:
    errors: list[str] = []
    if check_outputs() != 0:
        errors.append("Phase 16 deterministic outputs are stale")
    validate_records(errors)
    if errors:
        print("Phase 16 offline multi-artifact errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "Phase 16 passed: three exact-revision external dependents, atomic receipt "
        "v0.2, receipt chain, mixed lifecycle impact, deterministic recovery, "
        "status separation, and live=false."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
