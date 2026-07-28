#!/usr/bin/env python3
"""Generate deterministic Phase 22 offline consequence-planning evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "integration" / "principia-atlas" / "pilot"
MODE = "offline-resolution-consequence-planning"
DECISION = "consequence-plans-recorded-no-execution"

PLANS_PATH = PILOT / "thermal-control.resolution-consequence-plans.v01.json"
LEDGER_PATH = PILOT / "thermal-control.resolution-consequence-plan-ledger.v01.json"
CHECKPOINT_PATH = PILOT / "thermal-control.resolution-consequence-plan-checkpoint.v01.json"
RECOVERY_PATH = PILOT / "thermal-control.resolution-consequence-plan-recovery.v01.json"
RELEASE_PATH = ROOT / "release" / "phase-22-offline-resolution-consequence-planning.json"

PHASE21_POSTMERGE_SHA = "86b51ac5a763ac9fb12b7bc867a93453e29452dbdef927ff76423e780e834961"
PHASE21_CANDIDATE_SHA = "d3485c7941588232121c74fc2d063d51c73aa121c5bd9a8e4fcbc5be2d5ba4af"
RECONCILIATION_REPORT_SHA = "451a3e13e5712122af93a78e370b720627027557dacb4fc3d58fce1a3b461a7b"
RECONCILIATION_LEDGER_SHA = "9f2cd658f00c30e58046653823b13b70a3d25fb06647b79d68a712f47d40df95"
RECONCILIATION_CHECKPOINT_SHA = "8ed03459c77bc9cc2aea387ec9bd9fe7ee1e5e81c5c1169c3dc38edc08ea9cc9"

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
SCENARIOS = [
    ("baseline", "accepted", None),
    ("phase21-postmerge-drift", "rejected", "E-P22-SOURCE-PIN"),
    ("phase21-candidate-drift", "rejected", "E-P22-SOURCE-PIN"),
    ("reconciliation-report-drift", "rejected", "E-P22-SOURCE-PIN"),
    ("unknown-resolution", "rejected", "E-P22-RESOLUTION-ID"),
    ("duplicate-plan", "rejected", "E-P22-DUPLICATE"),
    ("missing-plan", "rejected", "E-P22-MISSING"),
    ("orphan-plan", "rejected", "E-P22-ORPHAN"),
    ("sequence-drift", "rejected", "E-P22-SEQUENCE"),
    ("plan-digest-drift", "rejected", "E-P22-DIGEST"),
    ("ledger-head-drift", "rejected", "E-P22-LEDGER"),
    ("checkpoint-count-drift", "rejected", "E-P22-CHECKPOINT"),
    ("step-count-drift", "rejected", "E-P22-STEPS"),
    ("step-started", "rejected", "E-P22-EXECUTION"),
    ("plan-started", "rejected", "E-P22-EXECUTION"),
    ("plan-completed", "rejected", "E-P22-EXECUTION"),
    ("review-completed", "rejected", "E-P22-EXECUTION"),
    ("content-change-proposed", "rejected", "E-P22-EFFECT"),
    ("status-recommendation-recorded", "rejected", "E-P22-EFFECT"),
    ("effective-hold", "rejected", "E-P22-EFFECT"),
    ("operational-effect", "rejected", "E-P22-EFFECT"),
    ("status-change", "rejected", "E-P22-EFFECT"),
    ("real-authorization-claimed", "rejected", "E-P22-AUTHORIZATION"),
    ("status-inheritance", "rejected", "E-P22-AUTHORITY"),
    ("automatic-status-change", "rejected", "E-P22-AUTHORITY"),
    ("automatic-release-action", "rejected", "E-P22-AUTHORITY"),
    ("repository-mutation", "rejected", "E-P22-AUTHORITY"),
    ("live-activation", "rejected", "E-P22-LIVE-FROZEN"),
]


def render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def doc_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source() -> dict[str, Any]:
    return {
        "phase21_candidate_path": "release/phase-21-offline-policy-resolution-reconciliation.json",
        "phase21_candidate_sha256": PHASE21_CANDIDATE_SHA,
        "phase21_finalization_merge_commit": "1071b59ac6dcccbc2bb3831f7942916b06da8f09",
        "phase21_postmerge_path": "release/phase-21-postmerge.json",
        "phase21_postmerge_sha256": PHASE21_POSTMERGE_SHA,
        "reconciliation_checkpoint_path": "integration/principia-atlas/pilot/thermal-control.policy-resolution-reconciliation-checkpoint.v01.json",
        "reconciliation_checkpoint_sha256": RECONCILIATION_CHECKPOINT_SHA,
        "reconciliation_ledger_path": "integration/principia-atlas/pilot/thermal-control.policy-resolution-reconciliation-ledger.v01.json",
        "reconciliation_ledger_sha256": RECONCILIATION_LEDGER_SHA,
        "reconciliation_report_path": "integration/principia-atlas/pilot/thermal-control.policy-resolution-reconciliation-report.v01.json",
        "reconciliation_report_sha256": RECONCILIATION_REPORT_SHA,
    }


def steps(kind: str) -> list[dict[str, Any]]:
    if kind == "manual":
        values = [
            ("scope-review-questions", "prepare-review-scope-and-questions"),
            ("map-evidence-needs", "document-evidence-needed-for-human-revalidation"),
            ("define-review-outcomes", "define-possible-human-review-outcomes-without-selecting-one"),
        ]
    else:
        values = [
            ("define-authority-inputs", "document-inputs-required-by-independent-release-authority"),
            ("define-decision-options", "describe-activate-defer-replace-or-reject-options-without-selecting-one"),
            ("define-readiness-check", "prepare-non-executing-release-readiness-checklist"),
        ]
    return [
        {
            "action": action,
            "execution_permitted": False,
            "sequence": index,
            "state": "planned-not-started",
            "step_id": step_id,
        }
        for index, (step_id, action) in enumerate(values, start=1)
    ]


def plans() -> list[dict[str, Any]]:
    common = {
        "affected_artifacts": ARTIFACT_KEYS,
        "content_change_proposed": False,
        "effective_hold": False,
        "operational_effect": False,
        "real_authorization_claimed": False,
        "review_completed": False,
        "state": "planned-not-started",
        "status_recommendation_recorded": False,
    }
    return [
        {
            **common,
            "plan_id": "principia:resolution-consequence-plan:feedback-manual-review:0001",
            "plan_kind": "manual-review-work-plan",
            "sequence": 1,
            "source_decision": "accept",
            "source_proposal_id": "principia:policy-review:feedback-deprecation:0001",
            "source_resolution_id": "principia:manual-policy-resolution:feedback-deprecation:0001",
            "steps": steps("manual"),
        },
        {
            **common,
            "plan_id": "principia:resolution-consequence-plan:model-boundary-release-governance:0002",
            "plan_kind": "release-governance-follow-up-plan",
            "sequence": 2,
            "source_decision": "defer",
            "source_proposal_id": "principia:release-hold-proposal:model-boundary-retraction:0001",
            "source_resolution_id": "principia:manual-policy-resolution:model-boundary-retraction:0002",
            "steps": steps("release"),
        },
    ]


def build() -> dict[Path, dict[str, Any]]:
    plan_values = plans()
    stream = {
        "authority": AUTHORITY,
        "contract": "principia-offline-resolution-consequence-plans/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "mode": MODE,
        "plan_stream_id": "principia:offline-resolution-consequence-plans:thermal-control:0001",
        "plans": plan_values,
        "source": source(),
        "summary": {
            "completed_plan_count": 0,
            "effective_hold_count": 0,
            "manual_review_plan_count": 1,
            "operational_effect_count": 0,
            "plan_count": 2,
            "planned_step_count": 6,
            "release_governance_plan_count": 1,
            "started_plan_count": 0,
            "status_change_count": 0,
        },
    }
    entries = []
    previous = None
    for plan in plan_values:
        entry = {
            "plan_id": plan["plan_id"],
            "plan_sha256": doc_sha(plan),
            "previous_entry_sha256": previous,
            "sequence": plan["sequence"],
            "source_resolution_id": plan["source_resolution_id"],
        }
        digest = doc_sha(entry)
        entries.append({"entry": entry, "entry_sha256": digest})
        previous = digest
    ledger = {
        "authority": AUTHORITY,
        "contract": "principia-offline-resolution-consequence-plan-ledger/0.1",
        "decision": DECISION,
        "entries": entries,
        "head_sequence": 2,
        "head_sha256": previous,
        "ledger_id": "principia:offline-resolution-consequence-plan-ledger:thermal-control:0001",
        "live": False,
        "mode": MODE,
        "source_plan_stream_sha256": doc_sha(stream),
    }
    checkpoint = {
        "authority": AUTHORITY,
        "checkpoint_id": "principia:offline-resolution-consequence-plan-checkpoint:thermal-control:0001",
        "completed_plan_count": 0,
        "contract": "principia-offline-resolution-consequence-plan-checkpoint/0.1",
        "decision": DECISION,
        "effective_hold_count": 0,
        "ledger_sha256": doc_sha(ledger),
        "live": False,
        "mode": MODE,
        "operational_effect_count": 0,
        "plan_count": 2,
        "plan_stream_sha256": doc_sha(stream),
        "planned_step_count": 6,
        "real_authorization_claimed": False,
        "started_plan_count": 0,
        "status_change_count": 0,
    }
    recovery = {
        "authority": AUTHORITY,
        "baseline": {
            "checkpoint_sha256": doc_sha(checkpoint),
            "ledger_sha256": doc_sha(ledger),
            "plan_stream_sha256": doc_sha(stream),
        },
        "contract": "principia-offline-resolution-consequence-plan-recovery/0.1",
        "live": False,
        "mode": MODE,
        "recovery_id": "principia:offline-resolution-consequence-plan-recovery:thermal-control:0001",
        "scenarios": [
            {"expected_error": error, "expected_outcome": outcome, "scenario_id": scenario}
            for scenario, outcome, error in SCENARIOS
        ],
        "summary": {"accepted_count": 1, "rejected_count": 27, "scenario_count": 28},
    }
    release = {
        "artifacts": {
            "checkpoint": {"path": CHECKPOINT_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha(CHECKPOINT_PATH)},
            "ledger": {"path": LEDGER_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha(LEDGER_PATH)},
            "plans": {"path": PLANS_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha(PLANS_PATH)},
            "recovery": {"path": RECOVERY_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha(RECOVERY_PATH)},
        },
        "authority": AUTHORITY,
        "contract": "principia-offline-resolution-consequence-planning/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-offline-resolution-consequence-planning-thermal-control",
        "live": False,
        "live_activation_permitted": False,
        "mode": MODE,
        "next_gate": "offline-consequence-plan-assurance-candidate",
        "phase": 22,
        "real_authorization_claimed": False,
        "result": stream["summary"],
        "source_phase21": source(),
        "state": "offline-resolution-consequence-planning-candidate",
        "validation": {"pull_request": None, "status": "pending", "tested_head_commit": None},
    }
    return {PLANS_PATH: stream, LEDGER_PATH: ledger, CHECKPOINT_PATH: checkpoint, RECOVERY_PATH: recovery, RELEASE_PATH: release}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = []
    for path, expected in build().items():
        if args.check:
            try:
                actual = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                errors.append(f"missing or invalid generated file: {path.relative_to(ROOT)}")
                continue
            if actual != expected:
                errors.append(f"generated data drift: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(render(expected), encoding="utf-8")
    if errors:
        print("\n".join(errors))
        return 1
    print("Phase 22 consequence-planning evidence is deterministic.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
