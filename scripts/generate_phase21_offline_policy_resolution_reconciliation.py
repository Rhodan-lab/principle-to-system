#!/usr/bin/env python3
"""Generate deterministic Phase 21 offline policy-resolution reconciliation evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "integration" / "principia-atlas" / "pilot"
REPORT_PATH = PILOT / "thermal-control.policy-resolution-reconciliation-report.v01.json"
LEDGER_PATH = PILOT / "thermal-control.policy-resolution-reconciliation-ledger.v01.json"
CHECKPOINT_PATH = PILOT / "thermal-control.policy-resolution-reconciliation-checkpoint.v01.json"
RECOVERY_PATH = PILOT / "thermal-control.policy-resolution-reconciliation-recovery.v01.json"
RELEASE_PATH = ROOT / "release" / "phase-21-offline-policy-resolution-reconciliation.json"

MODE = "offline-policy-resolution-reconciliation"
DECISION = "reconciled-resolutions-no-mutation"
PHASE20_FINALIZATION_MERGE = "c8c0f83850d7e6c29f53239f84003263f02cbe43"
PHASE20_POSTMERGE_SHA = "0c1157c86371c264592e3f49d55d94072c97d24ab2d1282fa1e36df327ebebe8"
PHASE20_CANDIDATE_SHA = "3cf082a2c468163936f894a55dd4e555097adf1b0b85cdba27b1931c530d0a0f"
REVIEW_QUEUE_SHA = "54c6b77d6a63d5325288249c2a3e1cb1d28945bca53e856f79e8a890d0a67008"
HOLD_PROPOSALS_SHA = "8c4f8f5ec11ad30af2b53fa2aac614af938fe91855d831a8d181b6647400a12f"
POLICY_LEDGER_SHA = "238b22591dcddfb66a17bc7ea3726dc8b98e8963e7593c8d8e5b3474e0265f21"
RESOLUTION_STREAM_SHA = "8b9d9412a0ff33cc986914379375a6d389bbc74e3f2378beaf8e7a52a3d96760"
RESOLUTION_LEDGER_SHA = "04eaf9c1a446cfb0166b052564725c39aeedee15dba1c55d865c9ae24f717791"
RESOLUTION_CHECKPOINT_SHA = "38e4c918ac08bb13b0667cb0962f65cc2311faf493e21cb29e736efdbe65a518"

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

MATCHES = [
    {
        "sequence": 1,
        "proposal_id": "principia:policy-review:feedback-deprecation:0001",
        "proposal_kind": "manual-review-item",
        "proposal_document_sha256": REVIEW_QUEUE_SHA,
        "proposal_state": "open-proposal",
        "resolution_id": "principia:manual-policy-resolution:feedback-deprecation:0001",
        "resolution_sha256": "affb786c2c40fa7db159639bfb913ce79d878948efd4f7a1952c596e33f9a2c4",
        "decision": "accept",
        "outcome": "accepted-for-manual-review",
        "affected_artifacts": ARTIFACT_KEYS,
        "matched": True,
        "real_authorization_claimed": False,
        "effective_hold": False,
        "operational_effect": False,
        "status_change": False,
    },
    {
        "sequence": 2,
        "proposal_id": "principia:release-hold-proposal:model-boundary-retraction:0001",
        "proposal_kind": "release-hold-proposal",
        "proposal_document_sha256": HOLD_PROPOSALS_SHA,
        "proposal_state": "proposed",
        "resolution_id": "principia:manual-policy-resolution:model-boundary-retraction:0002",
        "resolution_sha256": "bc8c2c6ab751401d24352ee56dc9fafdcd3616d1357380ec7a8b4f6a4e467b1e",
        "decision": "defer",
        "outcome": "deferred-no-hold-activation",
        "affected_artifacts": ARTIFACT_KEYS,
        "matched": True,
        "real_authorization_claimed": False,
        "effective_hold": False,
        "operational_effect": False,
        "status_change": False,
    },
]

SCENARIOS = [
    ("baseline", "accepted", None),
    ("phase20-postmerge-drift", "rejected", "E-P21-SOURCE-PIN"),
    ("phase20-candidate-drift", "rejected", "E-P21-SOURCE-PIN"),
    ("review-queue-drift", "rejected", "E-P21-PROPOSAL-DIGEST"),
    ("hold-proposal-drift", "rejected", "E-P21-PROPOSAL-DIGEST"),
    ("policy-ledger-drift", "rejected", "E-P21-SOURCE-PIN"),
    ("resolution-stream-drift", "rejected", "E-P21-RESOLUTION-DIGEST"),
    ("resolution-ledger-drift", "rejected", "E-P21-LEDGER"),
    ("resolution-checkpoint-drift", "rejected", "E-P21-CHECKPOINT"),
    ("missing-resolution", "rejected", "E-P21-MISSING"),
    ("orphan-resolution", "rejected", "E-P21-ORPHAN"),
    ("duplicate-proposal", "rejected", "E-P21-DUPLICATE"),
    ("unknown-proposal", "rejected", "E-P21-PROPOSAL-ID"),
    ("proposal-digest-mismatch", "rejected", "E-P21-PROPOSAL-DIGEST"),
    ("resolution-digest-mismatch", "rejected", "E-P21-RESOLUTION-DIGEST"),
    ("decision-mismatch", "rejected", "E-P21-DECISION"),
    ("affected-set-drift", "rejected", "E-P21-AFFECTED-SET"),
    ("sequence-drift", "rejected", "E-P21-SEQUENCE"),
    ("ledger-head-drift", "rejected", "E-P21-LEDGER"),
    ("checkpoint-count-drift", "rejected", "E-P21-CHECKPOINT"),
    ("real-authorization-claimed", "rejected", "E-P21-AUTHORIZATION"),
    ("effective-hold", "rejected", "E-P21-EFFECT"),
    ("operational-effect", "rejected", "E-P21-EFFECT"),
    ("status-change", "rejected", "E-P21-EFFECT"),
    ("status-inheritance", "rejected", "E-P21-STATUS-INHERITANCE"),
    ("automatic-status-change", "rejected", "E-P21-AUTHORITY"),
    ("automatic-release-action", "rejected", "E-P21-AUTHORITY"),
    ("repository-mutation", "rejected", "E-P21-AUTHORITY"),
    ("live-activation", "rejected", "E-P21-LIVE-FROZEN"),
]


def render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def doc_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def file_sha(value: Any) -> str:
    return hashlib.sha256(render(value).encode("utf-8")).hexdigest()


def source() -> dict[str, Any]:
    return {
        "phase20_finalization_merge_commit": PHASE20_FINALIZATION_MERGE,
        "phase20_postmerge_path": "release/phase-20-postmerge.json",
        "phase20_postmerge_sha256": PHASE20_POSTMERGE_SHA,
        "phase20_candidate_path": "release/phase-20-offline-manual-policy-resolution.json",
        "phase20_candidate_sha256": PHASE20_CANDIDATE_SHA,
        "review_queue_path": "integration/principia-atlas/pilot/thermal-control.policy-review-queue.v01.json",
        "review_queue_sha256": REVIEW_QUEUE_SHA,
        "release_hold_proposals_path": "integration/principia-atlas/pilot/thermal-control.release-hold-proposals.v01.json",
        "release_hold_proposals_sha256": HOLD_PROPOSALS_SHA,
        "policy_ledger_path": "integration/principia-atlas/pilot/thermal-control.policy-ledger.v01.json",
        "policy_ledger_sha256": POLICY_LEDGER_SHA,
        "resolution_stream_path": "integration/principia-atlas/pilot/thermal-control.manual-policy-resolutions.v01.json",
        "resolution_stream_sha256": RESOLUTION_STREAM_SHA,
        "resolution_ledger_path": "integration/principia-atlas/pilot/thermal-control.manual-policy-resolution-ledger.v01.json",
        "resolution_ledger_sha256": RESOLUTION_LEDGER_SHA,
        "resolution_checkpoint_path": "integration/principia-atlas/pilot/thermal-control.manual-policy-resolution-checkpoint.v01.json",
        "resolution_checkpoint_sha256": RESOLUTION_CHECKPOINT_SHA,
    }


def build() -> dict[Path, dict[str, Any]]:
    report = {
        "authority": AUTHORITY,
        "contract": "principia-offline-policy-resolution-reconciliation-report/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "matches": MATCHES,
        "mode": MODE,
        "real_authorization_claimed": False,
        "reconciliation_id": "principia:offline-policy-resolution-reconciliation:thermal-control:0001",
        "source": source(),
        "summary": {
            "checkpoint_mismatch_count": 0,
            "effective_hold_count": 0,
            "ledger_mismatch_count": 0,
            "matched_resolution_count": 2,
            "missing_resolution_count": 0,
            "operational_effect_count": 0,
            "orphan_resolution_count": 0,
            "proposal_count": 2,
            "proposal_digest_mismatch_count": 0,
            "resolution_count": 2,
            "resolution_digest_mismatch_count": 0,
            "status_change_count": 0,
            "unique_affected_artifact_count": 3,
        },
    }

    entries: list[dict[str, Any]] = []
    previous: str | None = None
    for match in MATCHES:
        entry = {
            "decision": match["decision"],
            "match_sequence": match["sequence"],
            "previous_entry_sha256": previous,
            "proposal_document_sha256": match["proposal_document_sha256"],
            "proposal_id": match["proposal_id"],
            "resolution_id": match["resolution_id"],
            "resolution_sha256": match["resolution_sha256"],
        }
        digest = doc_sha(entry)
        entries.append({"entry": entry, "entry_sha256": digest})
        previous = digest

    ledger = {
        "authority": AUTHORITY,
        "contract": "principia-offline-policy-resolution-reconciliation-ledger/0.1",
        "decision": DECISION,
        "entries": entries,
        "head_entry_sha256": entries[-1]["entry_sha256"],
        "head_sequence": 2,
        "ledger_id": "principia:offline-policy-resolution-reconciliation-ledger:thermal-control:0001",
        "live": False,
        "mode": MODE,
        "source_reconciliation_report_sha256": doc_sha(report),
    }

    checkpoint = {
        "authority": AUTHORITY,
        "checkpoint_id": "principia:offline-policy-resolution-reconciliation-checkpoint:thermal-control:0001",
        "contract": "principia-offline-policy-resolution-reconciliation-checkpoint/0.1",
        "decision": DECISION,
        "effective_hold_count": 0,
        "ledger_sha256": doc_sha(ledger),
        "live": False,
        "matched_resolution_count": 2,
        "missing_resolution_count": 0,
        "mode": MODE,
        "operational_effect_count": 0,
        "orphan_resolution_count": 0,
        "proposal_count": 2,
        "real_authorization_claimed": False,
        "reconciliation_report_sha256": doc_sha(report),
        "resolution_count": 2,
        "source_resolution_checkpoint_sha256": RESOLUTION_CHECKPOINT_SHA,
        "status_change_count": 0,
    }

    recovery = {
        "authority": AUTHORITY,
        "baseline": {
            "checkpoint_sha256": doc_sha(checkpoint),
            "ledger_sha256": doc_sha(ledger),
            "reconciliation_report_sha256": doc_sha(report),
        },
        "contract": "principia-offline-policy-resolution-reconciliation-recovery/0.1",
        "live": False,
        "mode": MODE,
        "recovery_id": "principia:offline-policy-resolution-reconciliation-recovery:thermal-control:0001",
        "scenarios": [
            {"expected_error": error, "expected_outcome": outcome, "scenario_id": scenario}
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
            "checkpoint": {"path": CHECKPOINT_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha(checkpoint)},
            "ledger": {"path": LEDGER_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha(ledger)},
            "reconciliation_report": {"path": REPORT_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha(report)},
            "recovery": {"path": RECOVERY_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha(recovery)},
        },
        "authority": AUTHORITY,
        "contract": "principia-offline-policy-resolution-reconciliation/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-offline-policy-resolution-reconciliation-thermal-control",
        "live": False,
        "mode": MODE,
        "next_gate": "offline-resolution-consequence-planning-candidate",
        "phase": 21,
        "real_authorization_claimed": False,
        "result": report["summary"],
        "source_phase20": source(),
        "state": "offline-policy-resolution-reconciliation-candidate",
        "validation": {"pull_request": None, "status": "pending", "tested_head_commit": None},
    }
    return {
        REPORT_PATH: report,
        LEDGER_PATH: ledger,
        CHECKPOINT_PATH: checkpoint,
        RECOVERY_PATH: recovery,
        RELEASE_PATH: release,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    drift: list[str] = []
    for path, value in build().items():
        expected = render(value)
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                drift.append(path.relative_to(ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
    if drift:
        print("Phase 21 generated-file drift:")
        for item in drift:
            print(f"- {item}")
        return 1
    if args.check:
        print("Phase 21 generated files match deterministic output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
