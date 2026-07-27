#!/usr/bin/env python3
"""Generate deterministic Phase 20 offline manual-policy-resolution evidence."""
from __future__ import annotations
import argparse, copy, hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "integration/principia-atlas/pilot"
RESOLUTIONS_PATH = PILOT / "thermal-control.manual-policy-resolutions.v01.json"
LEDGER_PATH = PILOT / "thermal-control.manual-policy-resolution-ledger.v01.json"
CHECKPOINT_PATH = PILOT / "thermal-control.manual-policy-resolution-checkpoint.v01.json"
RECOVERY_PATH = PILOT / "thermal-control.manual-policy-resolution-recovery.v01.json"
RELEASE_PATH = ROOT / "release/phase-20-offline-manual-policy-resolution.json"

MODE = "offline-manual-policy-resolution"
P19_MERGE = "2ceb502ed8bd4155324b76aed6642229dba18bb7"
P19_POST = "74282ca55dfc21872ecbd2ea5e10821259dd998b8caf72344208299b135ecd57"
QUEUE_SHA = "54c6b77d6a63d5325288249c2a3e1cb1d28945bca53e856f79e8a890d0a67008"
HOLD_SHA = "8c4f8f5ec11ad30af2b53fa2aac614af938fe91855d831a8d181b6647400a12f"
POLICY_LEDGER_SHA = "238b22591dcddfb66a17bc7ea3726dc8b98e8963e7593c8d8e5b3474e0265f21"
AUTHORITY = {
    "atlas_knowledge_status_authority": "Atlas",
    "automatic_release_action": False,
    "automatic_status_change": False,
    "principia_pedagogical_status_authority": "Principia",
    "principia_release_status_authority": "Principia",
    "repository_mutation": False,
    "status_inheritance": "prohibited",
}
ARTIFACTS = [
    {"artifact_id": "principia:failure-pattern:feedback-instability", "artifact_revision": 1,
     "exact_key": "principia:failure-pattern:feedback-instability@1",
     "observed_pedagogical_status": "reviewed", "observed_release_status": "draft"},
    {"artifact_id": "principia:investigation:room-cooling", "artifact_revision": 1,
     "exact_key": "principia:investigation:room-cooling@1",
     "observed_pedagogical_status": "reviewed", "observed_release_status": "draft"},
    {"artifact_id": "principia:system-dossier:refrigerator", "artifact_revision": 1,
     "exact_key": "principia:system-dossier:refrigerator@1",
     "observed_pedagogical_status": "reviewed", "observed_release_status": "draft"},
]
SCENARIOS = [
    ("baseline", "accepted", None),
    ("phase19-postmerge-drift", "rejected", "E-P20-SOURCE-PIN"),
    ("review-queue-drift", "rejected", "E-P20-PROPOSAL-DIGEST"),
    ("hold-proposal-drift", "rejected", "E-P20-PROPOSAL-DIGEST"),
    ("unknown-proposal-id", "rejected", "E-P20-PROPOSAL-ID"),
    ("duplicate-resolution-id", "rejected", "E-P20-DUPLICATE"),
    ("resolution-sequence-drift", "rejected", "E-P20-SEQUENCE"),
    ("resolution-predecessor-drift", "rejected", "E-P20-PREVIOUS-DIGEST"),
    ("accept-review-auto-execution", "rejected", "E-P20-AUTOMATIC-EXECUTION"),
    ("deferred-hold-effective", "rejected", "E-P20-HOLD-EFFECTIVE"),
    ("unsupported-decision", "rejected", "E-P20-DECISION"),
    ("affected-set-drift", "rejected", "E-P20-AFFECTED-SET"),
    ("status-inheritance", "rejected", "E-P20-STATUS-INHERITANCE"),
    ("automatic-status-change", "rejected", "E-P20-AUTHORITY"),
    ("automatic-release-action", "rejected", "E-P20-AUTHORITY"),
    ("repository-mutation", "rejected", "E-P20-AUTHORITY"),
    ("live-activation", "rejected", "E-P20-LIVE-FROZEN"),
]

def render(v: Any) -> str:
    return json.dumps(v, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

def doc_sha(v: Any) -> str:
    raw = json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def file_sha(v: Any) -> str:
    return hashlib.sha256(render(v).encode()).hexdigest()

def source() -> dict[str, Any]:
    return {
        "phase19_finalization_merge_commit": P19_MERGE,
        "phase19_postmerge_path": "release/phase-19-postmerge.json",
        "phase19_postmerge_sha256": P19_POST,
        "policy_ledger_path": "integration/principia-atlas/pilot/thermal-control.policy-ledger.v01.json",
        "policy_ledger_sha256": POLICY_LEDGER_SHA,
        "release_hold_proposals_path": "integration/principia-atlas/pilot/thermal-control.release-hold-proposals.v01.json",
        "release_hold_proposals_sha256": HOLD_SHA,
        "review_queue_path": "integration/principia-atlas/pilot/thermal-control.policy-review-queue.v01.json",
        "review_queue_sha256": QUEUE_SHA,
    }

def resolution(seq: int, previous: str | None) -> dict[str, Any]:
    if seq == 1:
        fields = ("accept", "accepted-for-manual-review", QUEUE_SHA,
                  "principia:policy-review:feedback-deprecation:0001",
                  "manual-review-item", "fixture-accept-manual-review",
                  "principia:manual-policy-resolution:feedback-deprecation:0001",
                  "manual-review")
    else:
        fields = ("defer", "deferred-no-hold-activation", HOLD_SHA,
                  "principia:release-hold-proposal:model-boundary-retraction:0001",
                  "release-hold-proposal", "fixture-defer-release-hold",
                  "principia:manual-policy-resolution:model-boundary-retraction:0002",
                  "propose-release-hold")
    decision, outcome, proposal_sha, proposal_id, kind, rationale, rid, action = fields
    return {
        "affected_artifacts": copy.deepcopy(ARTIFACTS),
        "authority": copy.deepcopy(AUTHORITY),
        "decision": decision,
        "fixture_kind": "bounded-synthetic",
        "hold_effective": False,
        "operational_effect": False,
        "outcome": outcome,
        "previous_resolution_sha256": previous,
        "proposal_document_sha256": proposal_sha,
        "proposal_id": proposal_id,
        "proposal_kind": kind,
        "rationale_code": rationale,
        "resolution_id": rid,
        "sequence": seq,
        "source_policy_action": action,
        "status_change": False,
    }

def build() -> dict[Path, dict[str, Any]]:
    r1 = resolution(1, None); d1 = doc_sha(r1)
    r2 = resolution(2, d1); d2 = doc_sha(r2)
    stream = {
        "authority": copy.deepcopy(AUTHORITY),
        "contract": "principia-offline-manual-policy-resolutions/0.1",
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "mode": MODE,
        "resolution_stream_id": "principia:offline-manual-policy-resolutions:thermal-control:0001",
        "resolutions": [{"resolution": r1, "resolution_sha256": d1},
                        {"resolution": r2, "resolution_sha256": d2}],
        "source": source(),
        "summary": {"accepted_count": 1, "deferred_count": 1, "effective_hold_count": 0,
                    "operational_effect_count": 0, "rejected_count": 0, "replaced_count": 0,
                    "resolution_count": 2, "status_change_count": 0},
    }
    ledger = {
        "authority": copy.deepcopy(AUTHORITY),
        "contract": "principia-offline-manual-policy-resolution-ledger/0.1",
        "decision": "resolutions-recorded-no-mutation",
        "head_resolution_sequence": 2,
        "head_resolution_sha256": d2,
        "ledger_id": "principia:offline-manual-policy-resolution-ledger:thermal-control:0001",
        "links": [
            {"decision": "accept", "previous_resolution_sha256": None,
             "proposal_id": r1["proposal_id"], "resolution_id": r1["resolution_id"],
             "resolution_sha256": d1, "sequence": 1},
            {"decision": "defer", "previous_resolution_sha256": d1,
             "proposal_id": r2["proposal_id"], "resolution_id": r2["resolution_id"],
             "resolution_sha256": d2, "sequence": 2},
        ],
        "live": False, "mode": MODE, "source_resolution_stream_sha256": doc_sha(stream),
    }
    checkpoint = {
        "authority": copy.deepcopy(AUTHORITY),
        "checkpoint_id": "principia:offline-manual-policy-resolution-checkpoint:thermal-control:0001",
        "contract": "principia-offline-manual-policy-resolution-checkpoint/0.1",
        "decision": "resolutions-recorded-no-mutation",
        "effective_hold_count": 0, "ledger_sha256": doc_sha(ledger), "live": False,
        "mode": MODE, "operational_effect_count": 0, "resolution_count": 2,
        "resolution_stream_sha256": doc_sha(stream), "status_change_count": 0,
    }
    recovery = {
        "authority": copy.deepcopy(AUTHORITY),
        "baseline": {"checkpoint_sha256": doc_sha(checkpoint), "ledger_sha256": doc_sha(ledger),
                     "resolution_stream_sha256": doc_sha(stream)},
        "contract": "principia-offline-manual-policy-resolution-recovery/0.1",
        "live": False, "mode": MODE,
        "recovery_id": "principia:offline-manual-policy-resolution-recovery:thermal-control:0001",
        "scenarios": [{"expected_error": e, "expected_outcome": o, "scenario_id": s}
                      for s, o, e in SCENARIOS],
        "summary": {"accepted_count": 1, "rejected_count": 16, "scenario_count": 17},
    }
    bundle = {RESOLUTIONS_PATH: stream, LEDGER_PATH: ledger,
              CHECKPOINT_PATH: checkpoint, RECOVERY_PATH: recovery}
    release = {
        "artifacts": {k: {"path": p.relative_to(ROOT).as_posix(), "sha256": file_sha(bundle[p])}
                      for k, p in {"checkpoint": CHECKPOINT_PATH, "ledger": LEDGER_PATH,
                                   "recovery": RECOVERY_PATH, "resolutions": RESOLUTIONS_PATH}.items()},
        "authority": copy.deepcopy(AUTHORITY),
        "contract": "principia-offline-manual-policy-resolution/0.1",
        "id": "principia-atlas-offline-manual-policy-resolution-thermal-control",
        "live": False, "live_activation_permitted": False, "mode": MODE,
        "next_gate": "offline-policy-resolution-reconciliation-candidate", "phase": 20,
        "result": {"accepted_count": 1, "decision": "resolutions-recorded-no-mutation",
                   "deferred_count": 1, "effective_hold_count": 0,
                   "operational_effect_count": 0, "resolution_count": 2,
                   "status_change_count": 0},
        "source_phase19": source(), "state": "offline-manual-policy-resolution-candidate",
        "validation": {"pull_request": None, "status": "pending", "tested_head_commit": None},
    }
    bundle[RELEASE_PATH] = release
    return bundle

def check(bundle: dict[Path, dict[str, Any]]) -> list[str]:
    return [f"generated file drift: {p.relative_to(ROOT)}" for p, v in bundle.items()
            if not p.is_file() or p.read_text(encoding="utf-8") != render(v)]

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    bundle = build()
    if args.write:
        for path, value in bundle.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(render(value), encoding="utf-8")
        print("Phase 20 deterministic outputs written.")
        return 0
    errors = check(bundle)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Phase 20 deterministic outputs are current.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
