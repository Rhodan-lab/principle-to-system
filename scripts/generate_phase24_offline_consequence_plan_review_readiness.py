#!/usr/bin/env python3
"""Generate deterministic Phase 24 offline consequence-plan review-readiness evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "integration" / "principia-atlas" / "pilot"
MODE = "offline-consequence-plan-review-readiness"
DECISION = "review-readiness-recorded-no-review-started"

REPORT_PATH = PILOT / "thermal-control.consequence-plan-review-readiness-report.v01.json"
LEDGER_PATH = PILOT / "thermal-control.consequence-plan-review-readiness-ledger.v01.json"
CHECKPOINT_PATH = PILOT / "thermal-control.consequence-plan-review-readiness-checkpoint.v01.json"
RECOVERY_PATH = PILOT / "thermal-control.consequence-plan-review-readiness-recovery.v01.json"
RELEASE_PATH = ROOT / "release" / "phase-24-offline-consequence-plan-review-readiness.json"

SOURCE_FILES = {
    ROOT / "release/phase-23-postmerge.json": "9c92ca19883434982dcebb3966b0368e7571cdfb292e2464d29bd4d031079312",
    ROOT / "release/phase-23-offline-consequence-plan-assurance.json": "7fb1e743dee555e33ccf2d395c589256ecad4748568bc2d92c1256adc135dce6",
    PILOT / "thermal-control.consequence-plan-assurance-report.v01.json": "7bda137c7c378c4beb1a7825c0df2c86c80e5b8732545126787a21029d68d1b7",
    PILOT / "thermal-control.consequence-plan-assurance-ledger.v01.json": "ec43c3194a048f13e0263376d6eb220be039a82e6bf28816510f8f8e1d39f60b",
    PILOT / "thermal-control.consequence-plan-assurance-checkpoint.v01.json": "e6cb3183635805c2d431ce61cc81054941a7db2a829c0da4c1880f36d7b127ce",
    PILOT / "thermal-control.consequence-plan-assurance-recovery.v01.json": "c9e20b0ce4128986f67fdae2ef84676cdf3be9f7a61ad5d3f7988c19dee43cd2",
}

AUTHORITY = {
    "atlas_call_permitted": False,
    "atlas_knowledge_status_authority": "Atlas",
    "automatic_release_action": False,
    "automatic_status_change": False,
    "external_network_required": False,
    "human_authorization_claimed": False,
    "principia_pedagogical_status_authority": "Principia",
    "principia_release_status_authority": "Principia",
    "repository_mutation": False,
    "review_execution_authorized": False,
    "review_request_dispatch_authorized": False,
    "status_inheritance": "prohibited",
}

ARTIFACTS = [
    "principia:failure-pattern:feedback-instability@1",
    "principia:investigation:room-cooling@1",
    "principia:system-dossier:refrigerator@1",
]

SOURCE = {
    "assurance_checkpoint_path": "integration/principia-atlas/pilot/thermal-control.consequence-plan-assurance-checkpoint.v01.json",
    "assurance_checkpoint_sha256": "e6cb3183635805c2d431ce61cc81054941a7db2a829c0da4c1880f36d7b127ce",
    "assurance_ledger_path": "integration/principia-atlas/pilot/thermal-control.consequence-plan-assurance-ledger.v01.json",
    "assurance_ledger_sha256": "ec43c3194a048f13e0263376d6eb220be039a82e6bf28816510f8f8e1d39f60b",
    "assurance_recovery_path": "integration/principia-atlas/pilot/thermal-control.consequence-plan-assurance-recovery.v01.json",
    "assurance_recovery_sha256": "c9e20b0ce4128986f67fdae2ef84676cdf3be9f7a61ad5d3f7988c19dee43cd2",
    "assurance_report_path": "integration/principia-atlas/pilot/thermal-control.consequence-plan-assurance-report.v01.json",
    "assurance_report_sha256": "7bda137c7c378c4beb1a7825c0df2c86c80e5b8732545126787a21029d68d1b7",
    "phase23_candidate_path": "release/phase-23-offline-consequence-plan-assurance.json",
    "phase23_candidate_sha256": "7fb1e743dee555e33ccf2d395c589256ecad4748568bc2d92c1256adc135dce6",
    "phase23_finalization_commit": "094a6fb0455fdf063574823f2f011d0e1b63d87f",
    "phase23_postmerge_path": "release/phase-23-postmerge.json",
    "phase23_postmerge_sha256": "9c92ca19883434982dcebb3966b0368e7571cdfb292e2464d29bd4d031079312",
}

CHECKS = {
    "affected_artifact_set_exact": True,
    "assurance_identity_exact": True,
    "assurance_record_digest_exact": True,
    "authority_boundary_preserved": True,
    "evidence_packet_enumerated": True,
    "human_gates_explicit": True,
    "plan_identity_exact": True,
    "review_protocol_defined": True,
    "review_remains_unstarted": True,
    "zero_effect_boundary_preserved": True,
}

EXPECTED_ASSURANCES = (
    {
        "assurance_id": "principia:consequence-plan-assurance:feedback-manual-review:0001",
        "plan_id": "principia:resolution-consequence-plan:feedback-manual-review:0001",
        "plan_kind": "manual-review-work-plan",
        "plan_sha256": "f2cf1f339f90e4c4a622440fbd86be9a97c53587f059abe0a092ad0bf01efca1",
        "source_ledger_entry_sha256": "f8e752c455a2fb533cabb61a78ad3173665fc6d5289085149d5b42261617e98e",
        "source_proposal_id": "principia:policy-review:feedback-deprecation:0001",
        "source_resolution_id": "principia:manual-policy-resolution:feedback-deprecation:0001",
        "readiness_id": "principia:consequence-plan-review-readiness:feedback-manual-review:0001",
        "reviewer_role_required": "qualified-pedagogical-reviewer",
        "review_purpose": "evaluate the bounded feedback-instability material against the assured manual-review plan without starting or completing review",
    },
    {
        "assurance_id": "principia:consequence-plan-assurance:model-boundary-release-governance:0002",
        "plan_id": "principia:resolution-consequence-plan:model-boundary-release-governance:0002",
        "plan_kind": "release-governance-follow-up-plan",
        "plan_sha256": "f11b3c226fe9b457384387d1d52843e0874f4ebe246fdc4a7a8801cc374e3129",
        "source_ledger_entry_sha256": "839d49becdc1b58c38874fad9e7e10ad5224c2c10ef8047ff88e14c973ed6971",
        "source_proposal_id": "principia:release-hold-proposal:model-boundary-retraction:0001",
        "source_resolution_id": "principia:manual-policy-resolution:model-boundary-retraction:0002",
        "readiness_id": "principia:consequence-plan-review-readiness:model-boundary-release-governance:0002",
        "reviewer_role_required": "qualified-release-governance-reviewer",
        "review_purpose": "evaluate evidence prerequisites for a future release-governance review without selecting or recommending a release outcome",
    },
)

SCENARIOS = (
    ("baseline", "accepted", None),
    ("phase23-postmerge-drift", "rejected", "E-P24-SOURCE-PIN"),
    ("phase23-candidate-drift", "rejected", "E-P24-SOURCE-PIN"),
    ("assurance-report-file-drift", "rejected", "E-P24-SOURCE-PIN"),
    ("assurance-ledger-file-drift", "rejected", "E-P24-SOURCE-PIN"),
    ("assurance-checkpoint-file-drift", "rejected", "E-P24-SOURCE-PIN"),
    ("assurance-recovery-file-drift", "rejected", "E-P24-SOURCE-PIN"),
    ("missing-readiness-record", "rejected", "E-P24-MISSING"),
    ("orphan-readiness-record", "rejected", "E-P24-ORPHAN"),
    ("duplicate-readiness-id", "rejected", "E-P24-DUPLICATE"),
    ("readiness-sequence-drift", "rejected", "E-P24-SEQUENCE"),
    ("assurance-id-drift", "rejected", "E-P24-ASSURANCE"),
    ("assurance-record-digest-drift", "rejected", "E-P24-ASSURANCE"),
    ("plan-id-drift", "rejected", "E-P24-PLAN"),
    ("plan-digest-drift", "rejected", "E-P24-PLAN"),
    ("source-ledger-entry-drift", "rejected", "E-P24-SOURCE-BINDING"),
    ("source-proposal-drift", "rejected", "E-P24-SOURCE-BINDING"),
    ("source-resolution-drift", "rejected", "E-P24-SOURCE-BINDING"),
    ("affected-set-drift", "rejected", "E-P24-AFFECTED-SET"),
    ("criteria-count-drift", "rejected", "E-P24-CRITERIA"),
    ("criteria-sequence-drift", "rejected", "E-P24-CRITERIA"),
    ("machine-criterion-pending", "rejected", "E-P24-CRITERIA"),
    ("human-criterion-satisfied", "rejected", "E-P24-HUMAN-GATE"),
    ("reviewer-identity-recorded", "rejected", "E-P24-HUMAN-GATE"),
    ("competence-attestation-recorded", "rejected", "E-P24-HUMAN-GATE"),
    ("conflict-declaration-recorded", "rejected", "E-P24-HUMAN-GATE"),
    ("authorization-recorded", "rejected", "E-P24-AUTHORIZATION"),
    ("review-request-dispatched", "rejected", "E-P24-DISPATCH"),
    ("review-start-permitted", "rejected", "E-P24-EXECUTION"),
    ("review-started", "rejected", "E-P24-EXECUTION"),
    ("review-completed", "rejected", "E-P24-EXECUTION"),
    ("outcome-selected", "rejected", "E-P24-OUTCOME"),
    ("content-change-proposed", "rejected", "E-P24-EFFECT"),
    ("status-recommendation-recorded", "rejected", "E-P24-EFFECT"),
    ("effective-hold", "rejected", "E-P24-EFFECT"),
    ("operational-effect", "rejected", "E-P24-EFFECT"),
    ("status-change", "rejected", "E-P24-EFFECT"),
    ("real-authorization-claimed", "rejected", "E-P24-AUTHORIZATION"),
    ("status-inheritance", "rejected", "E-P24-AUTHORITY"),
    ("automatic-status-change", "rejected", "E-P24-AUTHORITY"),
    ("automatic-release-action", "rejected", "E-P24-AUTHORITY"),
    ("repository-mutation", "rejected", "E-P24-AUTHORITY"),
    ("external-network-required", "rejected", "E-P24-NETWORK"),
    ("atlas-call-permitted", "rejected", "E-P24-ATLAS"),
    ("live-activation", "rejected", "E-P24-LIVE-FROZEN"),
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


def source_assessment(expected: dict[str, Any], sequence: int) -> dict[str, Any]:
    return {
        "affected_artifacts": list(ARTIFACTS),
        "assurance_id": expected["assurance_id"],
        "checks": {
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
        },
        "effective_hold": False,
        "execution_permitted": False,
        "operational_effect": False,
        "plan_id": expected["plan_id"],
        "plan_kind": expected["plan_kind"],
        "plan_sha256": expected["plan_sha256"],
        "real_authorization_claimed": False,
        "sequence": sequence,
        "source_ledger_entry_sha256": expected["source_ledger_entry_sha256"],
        "source_proposal_id": expected["source_proposal_id"],
        "source_resolution_id": expected["source_resolution_id"],
        "status_change": False,
        "step_count": 3,
        "verdict": "assured-planning-only",
    }


def criteria_for(expected: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"category": "machine", "criterion_id": "source-assurance-exact", "evidence_ref": expected["assurance_id"], "sequence": 1, "state": "satisfied"},
        {"category": "machine", "criterion_id": "affected-artifact-scope-exact", "evidence_ref": "principia:artifact-set:thermal-control:0001", "sequence": 2, "state": "satisfied"},
        {"category": "machine", "criterion_id": "evidence-packet-enumerated", "evidence_ref": "principia:review-evidence-packet-definition:thermal-control:0001", "sequence": 3, "state": "satisfied"},
        {"category": "machine", "criterion_id": "review-protocol-defined", "evidence_ref": "principia:offline-review-protocol:planning-only:0001", "sequence": 4, "state": "satisfied"},
        {"category": "human", "criterion_id": "reviewer-identity-recorded", "evidence_ref": None, "sequence": 5, "state": "pending"},
        {"category": "human", "criterion_id": "reviewer-competence-attested", "evidence_ref": None, "sequence": 6, "state": "pending"},
        {"category": "human", "criterion_id": "conflict-declaration-recorded", "evidence_ref": None, "sequence": 7, "state": "pending"},
        {"category": "human", "criterion_id": "authorization-to-start-recorded", "evidence_ref": None, "sequence": 8, "state": "pending"},
    ]


def build_readiness_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for sequence, expected in enumerate(EXPECTED_ASSURANCES, start=1):
        assessment = source_assessment(expected, sequence)
        records.append({
            "affected_artifacts": list(ARTIFACTS),
            "assurance_id": expected["assurance_id"],
            "assurance_record_sha256": doc_sha(assessment),
            "authorization_record": None,
            "checks": dict(CHECKS),
            "competence_attestation": None,
            "conflict_declaration": None,
            "content_change_proposed": False,
            "criteria": criteria_for(expected),
            "effective_hold": False,
            "human_ready": False,
            "machine_ready": True,
            "operational_effect": False,
            "outcome_selected": False,
            "plan_id": expected["plan_id"],
            "plan_kind": expected["plan_kind"],
            "plan_sha256": expected["plan_sha256"],
            "readiness_id": expected["readiness_id"],
            "readiness_status": "machine-ready-human-gates-pending",
            "real_authorization_claimed": False,
            "review_completed": False,
            "review_purpose": expected["review_purpose"],
            "review_request_dispatch_permitted": False,
            "review_request_dispatched": False,
            "review_request_packet_preparation_permitted": True,
            "review_start_permitted": False,
            "review_started": False,
            "reviewer_identity": None,
            "reviewer_role_required": expected["reviewer_role_required"],
            "sequence": sequence,
            "source_ledger_entry_sha256": expected["source_ledger_entry_sha256"],
            "source_proposal_id": expected["source_proposal_id"],
            "source_resolution_id": expected["source_resolution_id"],
            "status_change": False,
            "status_recommendation_recorded": False,
            "verdict": "readiness-defined-review-not-authorized",
        })
    return records


def build() -> dict[Path, dict[str, Any]]:
    records = build_readiness_records()
    summary = {
        "effective_hold_count": 0,
        "human_authorization_count": 0,
        "human_ready_count": 0,
        "machine_ready_count": 2,
        "operational_effect_count": 0,
        "outcome_selected_count": 0,
        "plan_count": 2,
        "readiness_record_count": 2,
        "real_authorization_claimed": False,
        "review_completed_count": 0,
        "review_request_dispatch_count": 0,
        "review_request_packet_preparation_count": 2,
        "review_started_count": 0,
        "status_change_count": 0,
        "unmet_human_gate_count": 8,
    }
    report = {
        "authority": AUTHORITY,
        "contract": "principia-offline-consequence-plan-review-readiness-report/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "mode": MODE,
        "readiness_records": records,
        "report_id": "principia:offline-consequence-plan-review-readiness-report:thermal-control:0001",
        "source": SOURCE,
        "summary": summary,
    }
    entries = []
    previous = None
    for record in records:
        entry = {
            "assurance_id": record["assurance_id"],
            "plan_id": record["plan_id"],
            "previous_entry_sha256": previous,
            "readiness_id": record["readiness_id"],
            "readiness_record_sha256": doc_sha(record),
            "sequence": record["sequence"],
            "verdict": record["verdict"],
        }
        digest = doc_sha(entry)
        entries.append({"entry": entry, "entry_sha256": digest})
        previous = digest
    ledger = {
        "authority": AUTHORITY,
        "contract": "principia-offline-consequence-plan-review-readiness-ledger/0.1",
        "decision": DECISION,
        "entries": entries,
        "head_sequence": 2,
        "head_sha256": previous,
        "ledger_id": "principia:offline-consequence-plan-review-readiness-ledger:thermal-control:0001",
        "live": False,
        "mode": MODE,
        "source_readiness_report_sha256": doc_sha(report),
    }
    checkpoint = {
        "authority": AUTHORITY,
        "checkpoint_id": "principia:offline-consequence-plan-review-readiness-checkpoint:thermal-control:0001",
        "contract": "principia-offline-consequence-plan-review-readiness-checkpoint/0.1",
        "decision": DECISION,
        "effective_hold_count": 0,
        "human_authorization_count": 0,
        "human_ready_count": 0,
        "ledger_sha256": doc_sha(ledger),
        "live": False,
        "machine_ready_count": 2,
        "mode": MODE,
        "operational_effect_count": 0,
        "outcome_selected_count": 0,
        "plan_count": 2,
        "readiness_record_count": 2,
        "readiness_report_sha256": doc_sha(report),
        "real_authorization_claimed": False,
        "review_completed_count": 0,
        "review_request_dispatch_count": 0,
        "review_started_count": 0,
        "status_change_count": 0,
        "unmet_human_gate_count": 8,
    }
    recovery = {
        "authority": AUTHORITY,
        "baseline": {"checkpoint_sha256": doc_sha(checkpoint), "ledger_sha256": doc_sha(ledger), "readiness_report_sha256": doc_sha(report)},
        "contract": "principia-offline-consequence-plan-review-readiness-recovery/0.1",
        "live": False,
        "mode": MODE,
        "recovery_id": "principia:offline-consequence-plan-review-readiness-recovery:thermal-control:0001",
        "scenarios": [{"expected_error": error, "expected_outcome": outcome, "scenario_id": scenario} for scenario, outcome, error in SCENARIOS],
        "summary": {"accepted_count": 1, "rejected_count": len(SCENARIOS) - 1, "scenario_count": len(SCENARIOS)},
    }
    release = {
        "artifacts": {
            "checkpoint": {"path": CHECKPOINT_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(checkpoint)},
            "ledger": {"path": LEDGER_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(ledger)},
            "recovery": {"path": RECOVERY_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(recovery)},
            "report": {"path": REPORT_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(report)},
        },
        "authority": AUTHORITY,
        "contract": "principia-offline-consequence-plan-review-readiness/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-offline-consequence-plan-review-readiness-thermal-control",
        "live": False,
        "live_activation_permitted": False,
        "mode": MODE,
        "next_gate": "offline-consequence-plan-review-request-packet-candidate",
        "phase": 24,
        "real_authorization_claimed": False,
        "result": summary,
        "source_phase23": SOURCE,
        "state": "offline-consequence-plan-review-readiness-candidate",
        "validation": {"pull_request": None, "status": "pending", "tested_head_commit": None},
    }
    return {REPORT_PATH: report, LEDGER_PATH: ledger, CHECKPOINT_PATH: checkpoint, RECOVERY_PATH: recovery, RELEASE_PATH: release}


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
        print(f"Phase 24 generation failed: {exc}", file=sys.stderr)
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
        print("Phase 24 generation errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Phase 24 review-readiness evidence is deterministic and source-pinned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
