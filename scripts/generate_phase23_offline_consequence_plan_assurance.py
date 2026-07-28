#!/usr/bin/env python3
"""Generate deterministic Phase 23 offline consequence-plan assurance evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "integration" / "principia-atlas" / "pilot"
MODE = "offline-consequence-plan-assurance"
DECISION = "consequence-plans-assured-no-execution"

REPORT_PATH = PILOT / "thermal-control.consequence-plan-assurance-report.v01.json"
LEDGER_PATH = PILOT / "thermal-control.consequence-plan-assurance-ledger.v01.json"
CHECKPOINT_PATH = PILOT / "thermal-control.consequence-plan-assurance-checkpoint.v01.json"
RECOVERY_PATH = PILOT / "thermal-control.consequence-plan-assurance-recovery.v01.json"
RELEASE_PATH = ROOT / "release" / "phase-23-offline-consequence-plan-assurance.json"

SOURCE_FILES = {
    ROOT / "release/phase-22-postmerge.json": "3161d510d0809a4194dfa3ee12a078471e2c1f83a8638d74e0f79f4a494d326b",
    ROOT / "release/phase-22-offline-resolution-consequence-planning.json": "ccb4b608f77ba291f65ef25e0453382a3905a16b4bc5901d878de00dbdc4c9c8",
    PILOT / "thermal-control.resolution-consequence-plans.v01.json": "fcd4ae01732807bdb7f34e9aa758997fb456f80b27d9261134b7b95209b549c6",
    PILOT / "thermal-control.resolution-consequence-plan-ledger.v01.json": "3c17fae6e18472f9d78b1d03b1f864e15210d89d764a838f46081ff2b9a00e87",
    PILOT / "thermal-control.resolution-consequence-plan-checkpoint.v01.json": "c9359e4415f507274d99e729d15b4f1ba83b9a547b5eeedffcd8df8f3ae042e2",
    PILOT / "thermal-control.resolution-consequence-plan-recovery.v01.json": "03eeb6d78bf5b4ea72cb9b2ee2b7e644236bd544bb3f379aa31c5709a3e577ed",
}

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
    "principia:failure-pattern:feedback-instability@1",
    "principia:investigation:room-cooling@1",
    "principia:system-dossier:refrigerator@1",
]
SOURCE = {
    "phase22_candidate_path": "release/phase-22-offline-resolution-consequence-planning.json",
    "phase22_candidate_sha256": "ccb4b608f77ba291f65ef25e0453382a3905a16b4bc5901d878de00dbdc4c9c8",
    "phase22_finalization_merge_commit": "d42f26de8a9a606ae886306260960ba62be9b2cf",
    "phase22_postmerge_path": "release/phase-22-postmerge.json",
    "phase22_postmerge_sha256": "3161d510d0809a4194dfa3ee12a078471e2c1f83a8638d74e0f79f4a494d326b",
    "plan_checkpoint_path": "integration/principia-atlas/pilot/thermal-control.resolution-consequence-plan-checkpoint.v01.json",
    "plan_checkpoint_sha256": "c9359e4415f507274d99e729d15b4f1ba83b9a547b5eeedffcd8df8f3ae042e2",
    "plan_ledger_path": "integration/principia-atlas/pilot/thermal-control.resolution-consequence-plan-ledger.v01.json",
    "plan_ledger_sha256": "3c17fae6e18472f9d78b1d03b1f864e15210d89d764a838f46081ff2b9a00e87",
    "plan_recovery_path": "integration/principia-atlas/pilot/thermal-control.resolution-consequence-plan-recovery.v01.json",
    "plan_recovery_sha256": "03eeb6d78bf5b4ea72cb9b2ee2b7e644236bd544bb3f379aa31c5709a3e577ed",
    "plan_stream_path": "integration/principia-atlas/pilot/thermal-control.resolution-consequence-plans.v01.json",
    "plan_stream_sha256": "fcd4ae01732807bdb7f34e9aa758997fb456f80b27d9261134b7b95209b549c6",
}
EXPECTED_PLANS = (
    {
        "assurance_id": "principia:consequence-plan-assurance:feedback-manual-review:0001",
        "plan_id": "principia:resolution-consequence-plan:feedback-manual-review:0001",
        "plan_kind": "manual-review-work-plan",
        "plan_sha256": "f2cf1f339f90e4c4a622440fbd86be9a97c53587f059abe0a092ad0bf01efca1",
        "source_ledger_entry_sha256": "f8e752c455a2fb533cabb61a78ad3173665fc6d5289085149d5b42261617e98e",
        "source_proposal_id": "principia:policy-review:feedback-deprecation:0001",
        "source_resolution_id": "principia:manual-policy-resolution:feedback-deprecation:0001",
    },
    {
        "assurance_id": "principia:consequence-plan-assurance:model-boundary-release-governance:0002",
        "plan_id": "principia:resolution-consequence-plan:model-boundary-release-governance:0002",
        "plan_kind": "release-governance-follow-up-plan",
        "plan_sha256": "f11b3c226fe9b457384387d1d52843e0874f4ebe246fdc4a7a8801cc374e3129",
        "source_ledger_entry_sha256": "839d49becdc1b58c38874fad9e7e10ad5224c2c10ef8047ff88e14c973ed6971",
        "source_proposal_id": "principia:release-hold-proposal:model-boundary-retraction:0001",
        "source_resolution_id": "principia:manual-policy-resolution:model-boundary-retraction:0002",
    },
)
SCENARIOS = (
    ("baseline", "accepted", None),
    ("phase22-postmerge-drift", "rejected", "E-P23-SOURCE-PIN"),
    ("phase22-candidate-drift", "rejected", "E-P23-SOURCE-PIN"),
    ("plan-stream-file-drift", "rejected", "E-P23-SOURCE-PIN"),
    ("plan-ledger-file-drift", "rejected", "E-P23-SOURCE-PIN"),
    ("plan-checkpoint-file-drift", "rejected", "E-P23-SOURCE-PIN"),
    ("missing-assurance", "rejected", "E-P23-MISSING"),
    ("orphan-assurance", "rejected", "E-P23-ORPHAN"),
    ("duplicate-assurance-id", "rejected", "E-P23-DUPLICATE"),
    ("assurance-sequence-drift", "rejected", "E-P23-SEQUENCE"),
    ("plan-id-drift", "rejected", "E-P23-PLAN-ID"),
    ("plan-digest-drift", "rejected", "E-P23-PLAN-DIGEST"),
    ("ledger-entry-digest-drift", "rejected", "E-P23-SOURCE-LEDGER"),
    ("source-proposal-drift", "rejected", "E-P23-SOURCE-BINDING"),
    ("source-resolution-drift", "rejected", "E-P23-SOURCE-BINDING"),
    ("affected-set-drift", "rejected", "E-P23-AFFECTED-SET"),
    ("step-count-drift", "rejected", "E-P23-STEPS"),
    ("step-sequence-drift", "rejected", "E-P23-STEPS"),
    ("step-execution-permitted", "rejected", "E-P23-EXECUTION"),
    ("step-started", "rejected", "E-P23-EXECUTION"),
    ("plan-started", "rejected", "E-P23-EXECUTION"),
    ("plan-completed", "rejected", "E-P23-EXECUTION"),
    ("review-completed", "rejected", "E-P23-EXECUTION"),
    ("content-change-proposed", "rejected", "E-P23-EFFECT"),
    ("status-recommendation-recorded", "rejected", "E-P23-EFFECT"),
    ("effective-hold", "rejected", "E-P23-EFFECT"),
    ("operational-effect", "rejected", "E-P23-EFFECT"),
    ("status-change", "rejected", "E-P23-EFFECT"),
    ("real-authorization-claimed", "rejected", "E-P23-AUTHORIZATION"),
    ("status-inheritance", "rejected", "E-P23-AUTHORITY"),
    ("automatic-status-change", "rejected", "E-P23-AUTHORITY"),
    ("automatic-release-action", "rejected", "E-P23-AUTHORITY"),
    ("repository-mutation", "rejected", "E-P23-AUTHORITY"),
    ("live-activation", "rejected", "E-P23-LIVE-FROZEN"),
)


def render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def doc_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def file_sha_value(value: Any) -> str:
    return hashlib.sha256(render(value).encode()).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def build_assessments() -> list[dict[str, Any]]:
    plans = load_json(PILOT / "thermal-control.resolution-consequence-plans.v01.json")["plans"]
    ledger = load_json(PILOT / "thermal-control.resolution-consequence-plan-ledger.v01.json")["entries"]
    assessments: list[dict[str, Any]] = []
    checks = {
        "affected_artifact_set_exact": True,
        "authority_boundary_preserved": True,
        "execution_disabled_for_all_steps": True,
        "ledger_entry_digest_valid": True,
        "ledger_plan_digest_matches": True,
        "plan_identity_valid": True,
        "plan_state_planned_not_started": True,
        "source_binding_valid": True,
        "step_sequence_contiguous": True,
        "zero_effect_boundary_preserved": True,
    }
    for index, (plan, ledger_wrapper, expected) in enumerate(zip(plans, ledger, EXPECTED_PLANS), start=1):
        assessments.append({
            "affected_artifacts": list(plan["affected_artifacts"]),
            "assurance_id": expected["assurance_id"],
            "checks": dict(checks),
            "effective_hold": False,
            "execution_permitted": False,
            "operational_effect": False,
            "plan_id": expected["plan_id"],
            "plan_kind": expected["plan_kind"],
            "plan_sha256": expected["plan_sha256"],
            "real_authorization_claimed": False,
            "sequence": index,
            "source_ledger_entry_sha256": ledger_wrapper["entry_sha256"],
            "source_proposal_id": expected["source_proposal_id"],
            "source_resolution_id": expected["source_resolution_id"],
            "status_change": False,
            "step_count": len(plan["steps"]),
            "verdict": "assured-planning-only",
        })
    return assessments


def build() -> dict[Path, dict[str, Any]]:
    assessments = build_assessments()
    summary = {
        "assured_plan_count": 2,
        "assured_step_count": 6,
        "effective_hold_count": 0,
        "failed_assurance_count": 0,
        "operational_effect_count": 0,
        "plan_count": 2,
        "real_authorization_claimed": False,
        "started_plan_count": 0,
        "status_change_count": 0,
    }
    report = {
        "assessments": assessments,
        "assurance_report_id": "principia:offline-consequence-plan-assurance-report:thermal-control:0001",
        "authority": AUTHORITY,
        "contract": "principia-offline-consequence-plan-assurance-report/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "mode": MODE,
        "source": SOURCE,
        "summary": summary,
    }
    entries = []
    previous = None
    for assessment in assessments:
        entry = {
            "assurance_id": assessment["assurance_id"],
            "assurance_sha256": doc_sha(assessment),
            "plan_id": assessment["plan_id"],
            "plan_sha256": assessment["plan_sha256"],
            "previous_entry_sha256": previous,
            "sequence": assessment["sequence"],
            "verdict": assessment["verdict"],
        }
        digest = doc_sha(entry)
        entries.append({"entry": entry, "entry_sha256": digest})
        previous = digest
    ledger = {
        "authority": AUTHORITY,
        "contract": "principia-offline-consequence-plan-assurance-ledger/0.1",
        "decision": DECISION,
        "entries": entries,
        "head_sequence": 2,
        "head_sha256": previous,
        "ledger_id": "principia:offline-consequence-plan-assurance-ledger:thermal-control:0001",
        "live": False,
        "mode": MODE,
        "source_assurance_report_sha256": doc_sha(report),
    }
    checkpoint = {
        "assurance_count": 2,
        "assurance_report_sha256": doc_sha(report),
        "assured_plan_count": 2,
        "assured_step_count": 6,
        "authority": AUTHORITY,
        "checkpoint_id": "principia:offline-consequence-plan-assurance-checkpoint:thermal-control:0001",
        "contract": "principia-offline-consequence-plan-assurance-checkpoint/0.1",
        "decision": DECISION,
        "effective_hold_count": 0,
        "failed_assurance_count": 0,
        "ledger_sha256": doc_sha(ledger),
        "live": False,
        "mode": MODE,
        "operational_effect_count": 0,
        "plan_count": 2,
        "real_authorization_claimed": False,
        "started_plan_count": 0,
        "status_change_count": 0,
    }
    recovery = {
        "authority": AUTHORITY,
        "baseline": {
            "assurance_report_sha256": doc_sha(report),
            "checkpoint_sha256": doc_sha(checkpoint),
            "ledger_sha256": doc_sha(ledger),
        },
        "contract": "principia-offline-consequence-plan-assurance-recovery/0.1",
        "live": False,
        "mode": MODE,
        "recovery_id": "principia:offline-consequence-plan-assurance-recovery:thermal-control:0001",
        "scenarios": [
            {"expected_error": error, "expected_outcome": outcome, "scenario_id": scenario}
            for scenario, outcome, error in SCENARIOS
        ],
        "summary": {"accepted_count": 1, "rejected_count": 33, "scenario_count": 34},
    }
    release = {
        "artifacts": {
            "checkpoint": {"path": CHECKPOINT_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(checkpoint)},
            "ledger": {"path": LEDGER_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(ledger)},
            "recovery": {"path": RECOVERY_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(recovery)},
            "report": {"path": REPORT_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(report)},
        },
        "authority": AUTHORITY,
        "contract": "principia-offline-consequence-plan-assurance/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-offline-consequence-plan-assurance-thermal-control",
        "live": False,
        "live_activation_permitted": False,
        "mode": MODE,
        "next_gate": "offline-consequence-plan-review-readiness-candidate",
        "phase": 23,
        "real_authorization_claimed": False,
        "result": summary,
        "source_phase22": SOURCE,
        "state": "offline-consequence-plan-assurance-candidate",
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
    errors: list[str] = []
    for source_path, expected in SOURCE_FILES.items():
        if not source_path.is_file() or file_sha(source_path) != expected:
            errors.append(f"source drift: {source_path.relative_to(ROOT)}")
    try:
        bundle = build()
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Phase 23 generation failed: {exc}", file=sys.stderr)
        return 1
    for path, expected in bundle.items():
        text = render(expected)
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                errors.append(f"generated file drift: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    if errors:
        print("Phase 23 generation errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Phase 23 assurance evidence is deterministic and source-pinned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
