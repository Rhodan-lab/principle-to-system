#!/usr/bin/env python3
"""Generate or verify the immutable Phase 18 candidate release record."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Mapping

import generate_phase18_offline_reconciliation as reconciliation

ROOT = Path(__file__).resolve().parent.parent
RELEASE_PATH = ROOT / "release" / "phase-18-offline-reconciliation.json"
CONTRACT = "principia-offline-reconciliation-simulation/0.1"


def build_release() -> dict[str, Any]:
    outputs = reconciliation.build_outputs()
    report = outputs[reconciliation.REPORT_PATH]
    checkpoint = outputs[reconciliation.CHECKPOINT_PATH]
    recovery = outputs[reconciliation.RECOVERY_PATH]
    return {
        "contract": CONTRACT,
        "id": "principia-atlas-offline-reconciliation-thermal-control",
        "phase": 18,
        "state": "offline-reconciliation-simulation-candidate",
        "mode": reconciliation.MODE,
        "live": False,
        "source_phase17": {
            "candidate_head_commit": reconciliation.PHASE17_HEAD,
            "merge_commit": reconciliation.PHASE17_MERGE,
            "finalization_merge_commit": reconciliation.PHASE17_FINALIZATION_MERGE,
            "postmerge_path": reconciliation.PHASE17_POSTMERGE_PATH.relative_to(ROOT).as_posix(),
            "postmerge_sha256": reconciliation.sha256_file(reconciliation.PHASE17_POSTMERGE_PATH),
        },
        "artifacts": {
            "report": {
                "path": reconciliation.REPORT_PATH.relative_to(ROOT).as_posix(),
                "sha256": reconciliation.sha256_document(report),
            },
            "checkpoint": {
                "path": reconciliation.CHECKPOINT_PATH.relative_to(ROOT).as_posix(),
                "sha256": reconciliation.sha256_document(checkpoint),
            },
            "recovery": {
                "path": reconciliation.RECOVERY_PATH.relative_to(ROOT).as_posix(),
                "sha256": reconciliation.sha256_document(recovery),
            },
        },
        "result": report["summary"],
        "authority": {
            "atlas_knowledge_status_authority": "Atlas",
            "principia_pedagogical_status_authority": "Principia",
            "principia_release_status_authority": "Principia",
            "status_inheritance": "prohibited",
            "automatic_status_change": False,
            "automatic_release_action": False,
            "repository_mutation": False,
        },
        "validation": {
            "status": "pending",
            "pull_request": None,
            "tested_head_commit": None,
        },
        "next_gate": "offline-reconciliation-policy-candidate",
        "live_activation_permitted": False,
    }


def check(value: Mapping[str, Any]) -> list[str]:
    expected = reconciliation.render_json(value)
    if not RELEASE_PATH.is_file():
        return [f"missing output: {RELEASE_PATH.relative_to(ROOT)}"]
    if RELEASE_PATH.read_text(encoding="utf-8") != expected:
        return [f"stale output: {RELEASE_PATH.relative_to(ROOT)}"]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    value = build_release()
    if args.write:
        RELEASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        RELEASE_PATH.write_text(reconciliation.render_json(value), encoding="utf-8")
        print(f"wrote={RELEASE_PATH.relative_to(ROOT)}")
        return 0
    errors = check(value)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Phase 18 candidate release record is current and immutable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
