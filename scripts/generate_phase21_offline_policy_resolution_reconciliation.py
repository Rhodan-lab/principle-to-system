#!/usr/bin/env python3
"""Generate deterministic Phase 21 policy-resolution reconciliation evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "integration" / "principia-atlas" / "pilot"
MODE = "offline-policy-resolution-reconciliation"

AUTHORITY = {
    "atlas_knowledge_status_authority": "Atlas",
    "automatic_release_action": False,
    "automatic_status_change": False,
    "principia_pedagogical_status_authority": "Principia",
    "principia_release_status_authority": "Principia",
    "repository_mutation": False,
    "status_inheritance": "prohibited",
}
ARTIFACT_KEYS = [
    "principia:failure-pattern:feedback-instability@1",
    "principia:investigation:room-cooling@1",
    "principia:system-dossier:refrigerator@1",
]
P20_FINALIZATION_MERGE = "c8c0f83850d7e6c29f53239f84003263f02cbe43"
P20_POST_SHA = "0c1157c86371c264592e3f49d55d94072c97d24ab2d1282fa1e36df327ebebe8"
P20_CANDIDATE_SHA = "3cf082a2c468163936f894a55dd4e555097adf1b0b85cdba27b1931c530d0a0f"
POLICY_LEDGER_FILE_SHA = "238b22591dcddfb66a17bc7ea3726dc8b98e8963e7593c8d8e5b3474e0265f21"
RESOLUTION_STREAM_FILE_SHA = "8b9d9412a0ff33cc986914379375a6d389bbc74e3f2378beaf8e7a52a3d96760"
RESOLUTION_STREAM_DOC_SHA = "e161e0e9151f2187800df7dd683e08fe30aa6e9b6efc7854cec541961fe262b6"
RESOLUTION_LEDGER_FILE_SHA = "04eaf9c1a446cfb0166b052564725c39aeedee15dba1c55d865c9ae24f717791"
RESOLUTION_LEDGER_DOC_SHA = "cc96ef7811e15bf3050e2ca38be51fd354370ce969fac8a5781ed6dcc18209b8"
RESOLUTION_CHECKPOINT_FILE_SHA = "38e4c918ac08bb13b0667cb0962f65cc2311faf493e21cb29e736efdbe65a518"
RESOLUTION_CHECKPOINT_DOC_SHA = "bb2ee7a8850094612c4a23c48fe419d348f7316a6ab5d66194886fa319372b47"

REPORT_PATH = PILOT / "thermal-control.policy-resolution-reconciliation-report.v01.json"
LEDGER_PATH = PILOT / "thermal-control.policy-resolution-reconciliation-ledger.v01.json"
CHECKPOINT_PATH = PILOT / "thermal-control.policy-resolution-reconciliation-checkpoint.v01.json"
RECOVERY_PATH = PILOT / "thermal-control.policy-resolution-reconciliation-recovery.v01.json"
RELEASE_PATH = ROOT / "release" / "phase-21-offline-policy-resolution-reconciliation.json"

SCENARIOS = [
    ("baseline", "accepted", None),
    ("phase20-postmerge-drift", "rejected", "E-P21-SOURCE-PIN"),
    ("phase20-candidate-drift", "rejected", "E-P21-SOURCE-PIN"),
    ("policy-ledger-file-drift", "rejected", "E-P21-PROPOSAL-PIN"),
    ("resolution-stream-file-drift", "rejected", "E-P21-RESOLUTION-PIN"),
    ("resolution-stream-document-drift", "rejected", "E-P21-RESOLUTION-PIN"),
    ("resolution-ledger-file-drift", "rejected", "E-P21-LEDGER-PIN"),
    ("resolution-ledger-document-drift", "rejected", "E-P21-LEDGER-PIN"),
    ("resolution-checkpoint-file-drift", "rejected", "E-P21-CHECKPOINT-PIN"),
    ("resolution-checkpoint-document-drift", "rejected", "E-P21-CHECKPOINT-PIN"),
    ("proposal-id-mismatch", "rejected", "E-P21-PROPOSAL-ID"),
    ("resolution-id-mismatch", "rejected", "E-P21-RESOLUTION-ID"),
    ("missing-resolution", "rejected", "E-P21-MISSING"),
    ("orphan-resolution", "rejected", "E-P21-ORPHAN"),
    ("duplicate-resolution", "rejected", "E-P21-DUPLICATE"),
    ("sequence-drift", "rejected", "E-P21-SEQUENCE"),
    ("predecessor-drift", "rejected", "E-P21-PREDECESSOR"),
    ("decision-mismatch", "rejected", "E-P21-DECISION"),
    ("affected-set-drift", "rejected", "E-P21-AFFECTED-SET"),
    ("reconciliation-ledger-head-drift", "rejected", "E-P21-LEDGER"),
    ("checkpoint-count-drift", "rejected", "E-P21-CHECKPOINT"),
    ("real-authorization-claimed", "rejected", "E-P21-AUTHORIZATION"),
    ("effective-hold", "rejected", "E-P21-EFFECT"),
    ("operational-effect", "rejected", "E-P21-EFFECT"),
    ("status-change", "rejected", "E-P21-EFFECT"),
    ("status-inheritance", "rejected", "E-P21-AUTHORITY"),
    ("repository-mutation", "rejected", "E-P21-AUTHORITY"),
    ("live-activation", "rejected", "E-P21-LIVE-FROZEN"),
]


def render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def document_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def file_sha256(value: Any) -> str:
    return hashlib.sha256(render(value).encode("utf-8")).hexdigest()


def source() -> dict[str, Any]:
    return {
        "phase20_candidate_path": "release/phase-20-offline-manual-policy-resolution.json",
        "phase20_candidate_sha256": P20_CANDIDATE_SHA,
        "phase20_finalization_merge_commit": P20_FINALIZATION_MERGE,
        "phase20_postmerge_path": "release/phase-20-postmerge.json",
        "phase20_postmerge_sha256": P20_POST_SHA,
        "policy_ledger_path": "integration/principia-atlas/pilot/thermal-control.policy-ledger.v01.json",
        "policy_ledger_sha256": POLICY_LEDGER_FILE_SHA,
        "resolution_checkpoint_document_sha256": RESOLUTION_CHECKPOINT_DOC_SHA,
        "resolution_checkpoint_file_sha256": RESOLUTION_CHECKPOINT_FILE_SHA,
        "resolution_checkpoint_path": "integration/principia-atlas/pilot/thermal-control.manual-policy-resolution-checkpoint.v01.json",
        "resolution_ledger_document_sha256": RESOLUTION_LEDGER_DOC_SHA,
        "resolution_ledger_file_sha256": RESOLUTION_LEDGER_FILE_SHA,
        "resolution_ledger_path": "integration/principia-atlas/pilot/thermal-control.manual-policy-resolution-ledger.v01.json",
        "resolution_stream_document_sha256": RESOLUTION_STREAM_DOC_SHA,
        "resolution_stream_file_sha256": RESOLUTION_STREAM_FILE_SHA,
        "resolution_stream_path": "integration/principia-atlas/pilot/thermal-control.manual-policy-resolutions.v01.json",
    }


def matches() -> list[dict[str, Any]]:
    first = {
        "affected_artifacts": ARTIFACT_KEYS,
        "authorization_effect": False,
        "decision": "accept",
        "hold_effect": False,
        "match_status": "matched",
        "outcome": "accepted-for-manual-review",
        "proposal_document_sha256": "54c6b77d6a63d5325288249c2a3e1cb1d28945bca53e856f79e8a890d0a67008",
        "proposal_entry_sha256": "6b2e86669b0bc6aad74f9ebd9d767a03aa9339fb8aaffebab0caefa7102b3424",
        "proposal_id": "principia:policy-review:feedback-deprecation:0001",
        "proposal_kind": "manual-review-item",
        "proposal_sequence": 1,
        "real_authorization_claimed": False,
        "resolution_id": "principia:manual-policy-resolution:feedback-deprecation:0001",
        "resolution_previous_sha256": None,
        "resolution_sequence": 1,
        "resolution_sha256": "affb786c2c40fa7db159639bfb913ce79d878948efd4f7a1952c596e33f9a2c4",
        "status_effect": False,
    }
    second = {
        "affected_artifacts": ARTIFACT_KEYS,
        "authorization_effect": False,
        "decision": "defer",
        "hold_effect": False,
        "match_status": "matched",
        "outcome": "deferred-no-hold-activation",
        "proposal_document_sha256": "8c4f8f5ec11ad30af2b53fa2aac614af938fe91855d831a8d181b6647400a12f",
        "proposal_entry_sha256": "e45b8d0b234d188ef9bfbe4664d0f68cc1d652e21e57f2c6b0d80a48bbde0296",
        "proposal_id": "principia:release-hold-proposal:model-boundary-retraction:0001",
        "proposal_kind": "release-hold-proposal",
        "proposal_sequence": 2,
        "real_authorization_claimed": False,
        "resolution_id": "principia:manual-policy-resolution:model-boundary-retraction:0002",
        "resolution_previous_sha256": first["resolution_sha256"],
        "resolution_sequence": 2,
        "resolution_sha256": "bc8c2c6ab751401d24352ee56dc9fafdcd3616d1357380ec7a8b4f6a4e467b1e",
        "status_effect": False,
    }
    return [first, second]


def build() -> dict[Path, dict[str, Any]]:
    reconciliation = {
        "authority": AUTHORITY,
        "contract": "principia-offline-policy-resolution-reconciliation/0.1",
        "fixture_kind": "bounded-synthetic",
        "findings": {
            "affected_set_mismatch_count": 0,
            "authorization_claim_count": 0,
            "decision_mismatch_count": 0,
            "duplicate_proposal_count": 0,
            "duplicate_resolution_count": 0,
            "effective_hold_count": 0,
            "missing_resolution_count": 0,
            "operational_effect_count": 0,
            "orphan_resolution_count": 0,
            "predecessor_mismatch_count": 0,
            "status_change_count": 0,
        },
        "live": False,
        "matches": matches(),
        "mode": MODE,
        "real_authorization_claimed": False,
        "reconciliation_id": "principia:offline-policy-resolution-reconciliation:thermal-control:0001",
        "result": {
            "decision": "reconciled-resolutions-no-mutation",
            "matched_resolution_count": 2,
            "missing_resolution_count": 0,
            "orphan_resolution_count": 0,
            "proposal_count": 2,
            "resolution_count": 2,
            "unique_affected_artifact_count": 3,
        },
        "source": source(),
    }

    ledger_entries: list[dict[str, Any]] = []
    previous: str | None = None
    for sequence, match in enumerate(reconciliation["matches"], start=1):
        entry = {
            "match_sha256": document_sha256(match),
            "previous_entry_sha256": previous,
            "proposal_id": match["proposal_id"],
            "resolution_id": match["resolution_id"],
            "sequence": sequence,
        }
        entry_sha = document_sha256(entry)
        ledger_entries.append({"entry": entry, "entry_sha256": entry_sha})
        previous = entry_sha

    ledger = {
        "authority": AUTHORITY,
        "contract": "principia-offline-policy-resolution-reconciliation-ledger/0.1",
        "decision": "reconciled-resolutions-no-mutation",
        "entries": ledger_entries,
        "head_sequence": 2,
        "head_sha256": previous,
        "ledger_id": "principia:offline-policy-resolution-reconciliation-ledger:thermal-control:0001",
        "live": False,
        "mode": MODE,
        "source_reconciliation_sha256": document_sha256(reconciliation),
    }

    checkpoint = {
        "authority": AUTHORITY,
        "checkpoint_id": "principia:offline-policy-resolution-reconciliation-checkpoint:thermal-control:0001",
        "contract": "principia-offline-policy-resolution-reconciliation-checkpoint/0.1",
        "decision": "reconciled-resolutions-no-mutation",
        "effective_hold_count": 0,
        "ledger_sha256": document_sha256(ledger),
        "live": False,
        "matched_resolution_count": 2,
        "missing_resolution_count": 0,
        "mode": MODE,
        "operational_effect_count": 0,
        "orphan_resolution_count": 0,
        "proposal_count": 2,
        "real_authorization_claimed": False,
        "reconciliation_sha256": document_sha256(reconciliation),
        "resolution_count": 2,
        "status_change_count": 0,
    }

    recovery = {
        "authority": AUTHORITY,
        "baseline": {
            "checkpoint_sha256": document_sha256(checkpoint),
            "ledger_sha256": document_sha256(ledger),
            "reconciliation_sha256": document_sha256(reconciliation),
        },
        "contract": "principia-offline-policy-resolution-reconciliation-recovery/0.1",
        "live": False,
        "mode": MODE,
        "recovery_id": "principia:offline-policy-resolution-reconciliation-recovery:thermal-control:0001",
        "scenarios": [
            {
                "expected_error": error,
                "expected_outcome": outcome,
                "scenario_id": scenario,
            }
            for scenario, outcome, error in SCENARIOS
        ],
        "summary": {
            "accepted_count": 1,
            "rejected_count": len(SCENARIOS) - 1,
            "scenario_count": len(SCENARIOS),
        },
    }

    release = {
        "artifacts": {
            "checkpoint": {
                "path": CHECKPOINT_PATH.relative_to(ROOT).as_posix(),
                "sha256": file_sha256(checkpoint),
            },
            "ledger": {
                "path": LEDGER_PATH.relative_to(ROOT).as_posix(),
                "sha256": file_sha256(ledger),
            },
            "reconciliation": {
                "path": REPORT_PATH.relative_to(ROOT).as_posix(),
                "sha256": file_sha256(reconciliation),
            },
            "recovery": {
                "path": RECOVERY_PATH.relative_to(ROOT).as_posix(),
                "sha256": file_sha256(recovery),
            },
        },
        "authority": AUTHORITY,
        "contract": "principia-offline-policy-resolution-reconciliation-release/0.1",
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-offline-policy-resolution-reconciliation-thermal-control",
        "live": False,
        "live_activation_permitted": False,
        "mode": MODE,
        "next_gate": "offline-policy-resolution-assurance-candidate",
        "phase": 21,
        "real_authorization_claimed": False,
        "result": {
            **reconciliation["result"],
            "effective_hold_count": 0,
            "operational_effect_count": 0,
            "status_change_count": 0,
        },
        "source_phase20": source(),
        "state": "offline-policy-resolution-reconciliation-candidate",
        "validation": {
            "pull_request": None,
            "status": "pending",
            "tested_head_commit": None,
        },
    }

    return {
        REPORT_PATH: reconciliation,
        LEDGER_PATH: ledger,
        CHECKPOINT_PATH: checkpoint,
        RECOVERY_PATH: recovery,
        RELEASE_PATH: release,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    for path, value in build().items():
        expected = render(value)
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                errors.append(f"generated file drift: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")

    if errors:
        for error in errors:
            print(error)
        return 1
    print("Phase 21 reconciliation evidence is deterministic.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
