#!/usr/bin/env python3
"""Generate deterministic Phase 26 offline review-request packet assurance evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "integration" / "principia-atlas" / "pilot"
MODE = "offline-consequence-plan-review-request-packet-assurance"
DECISION = "review-request-packets-assured-no-dispatch"
STATE = MODE + "-candidate"
NEXT_GATE = "offline-consequence-plan-review-response-intake-readiness-candidate"

REPORT_PATH = PILOT / "thermal-control.consequence-plan-review-request-packet-assurance-report.v01.json"
LEDGER_PATH = PILOT / "thermal-control.consequence-plan-review-request-packet-assurance-ledger.v01.json"
CHECKPOINT_PATH = PILOT / "thermal-control.consequence-plan-review-request-packet-assurance-checkpoint.v01.json"
RECOVERY_PATH = PILOT / "thermal-control.consequence-plan-review-request-packet-assurance-recovery.v01.json"
RELEASE_PATH = ROOT / "release" / "phase-26-offline-consequence-plan-review-request-packet-assurance.json"

SOURCE_FILES = {
    ROOT / "release/phase-25-postmerge.json": "89f161ab427de0e7bd91d6a3759b4bd5ab30270588551a4ac1bf5ec4ba365f2f",
    ROOT / "release/phase-25-offline-consequence-plan-review-request-packet.json": "38862c26ae18dc11c6570c33182c0da158ed8e59a19402073e1c733de6d154f3",
    PILOT / "thermal-control.consequence-plan-review-request-packet-report.v01.json": "1dcacaa08846601b2705f52fd4b10962a69cb568bf9c22e4a40f097a577a36d2",
    PILOT / "thermal-control.consequence-plan-review-request-packet-ledger.v01.json": "d624e228820912b4cb3c7bfbc68b59db7d8fa79b50e8a6cd63b10fe90a10843c",
    PILOT / "thermal-control.consequence-plan-review-request-packet-checkpoint.v01.json": "065dd05f57cc1d933dd2cc24dc0442d1dd5642fa69b1d70241dd391068f14bb7",
    PILOT / "thermal-control.consequence-plan-review-request-packet-recovery.v01.json": "7c4e2b79ae9ab6e0dfa26336b2050c6f8731af6c477f772cbbaa10c042ab18a7",
}

SOURCE = {
    "packet_checkpoint_path": "integration/principia-atlas/pilot/thermal-control.consequence-plan-review-request-packet-checkpoint.v01.json",
    "packet_checkpoint_sha256": "065dd05f57cc1d933dd2cc24dc0442d1dd5642fa69b1d70241dd391068f14bb7",
    "packet_ledger_path": "integration/principia-atlas/pilot/thermal-control.consequence-plan-review-request-packet-ledger.v01.json",
    "packet_ledger_sha256": "d624e228820912b4cb3c7bfbc68b59db7d8fa79b50e8a6cd63b10fe90a10843c",
    "packet_recovery_path": "integration/principia-atlas/pilot/thermal-control.consequence-plan-review-request-packet-recovery.v01.json",
    "packet_recovery_sha256": "7c4e2b79ae9ab6e0dfa26336b2050c6f8731af6c477f772cbbaa10c042ab18a7",
    "packet_report_path": "integration/principia-atlas/pilot/thermal-control.consequence-plan-review-request-packet-report.v01.json",
    "packet_report_sha256": "1dcacaa08846601b2705f52fd4b10962a69cb568bf9c22e4a40f097a577a36d2",
    "phase25_candidate_path": "release/phase-25-offline-consequence-plan-review-request-packet.json",
    "phase25_candidate_sha256": "38862c26ae18dc11c6570c33182c0da158ed8e59a19402073e1c733de6d154f3",
    "phase25_finalization_commit": "46c2b286bde99fd0165f0ec97463ac0fb5af2b5e",
    "phase25_postmerge_path": "release/phase-25-postmerge.json",
    "phase25_postmerge_sha256": "89f161ab427de0e7bd91d6a3759b4bd5ab30270588551a4ac1bf5ec4ba365f2f",
}

AUTHORITY = {
    "atlas_call_permitted": False,
    "atlas_knowledge_status_authority": "Atlas",
    "automatic_release_action": False,
    "automatic_status_change": False,
    "external_delivery_permitted": False,
    "external_network_required": False,
    "human_authorization_claimed": False,
    "local_assurance_permitted": True,
    "local_packet_preparation_permitted": True,
    "principia_pedagogical_status_authority": "Principia",
    "principia_release_status_authority": "Principia",
    "repository_mutation": False,
    "review_execution_authorized": False,
    "review_request_dispatch_authorized": False,
    "reviewer_contact_permitted": False,
    "status_inheritance": "prohibited",
}

ARTIFACTS = [
    "principia:failure-pattern:feedback-instability@1",
    "principia:investigation:room-cooling@1",
    "principia:system-dossier:refrigerator@1",
]

EXPECTED_PACKETS = (
    {
        "key": "feedback-manual-review",
        "packet_assurance_id": "principia:consequence-plan-review-request-packet-assurance:feedback-manual-review:0001",
        "packet_id": "principia:consequence-plan-review-request-packet:feedback-manual-review:0001",
        "packet_kind": "pedagogical-review-request-packet",
        "packet_record_sha256": "4af2c1994563a4cbeeca42637f65f43f2d7d78171e44c6915dbecb13df86bbb4",
        "packet_ledger_entry_sha256": "41293b264ddb9747752803d597815012a097a1a32a6f5fbc381c569300662899",
        "readiness_id": "principia:consequence-plan-review-readiness:feedback-manual-review:0001",
        "plan_id": "principia:resolution-consequence-plan:feedback-manual-review:0001",
        "reviewer_role_required": "qualified-pedagogical-reviewer",
    },
    {
        "key": "model-boundary-release-governance",
        "packet_assurance_id": "principia:consequence-plan-review-request-packet-assurance:model-boundary-release-governance:0002",
        "packet_id": "principia:consequence-plan-review-request-packet:model-boundary-release-governance:0002",
        "packet_kind": "release-governance-review-request-packet",
        "packet_record_sha256": "21019550db55a65950d1b0c07a0c1863307cb25becf679808571f0a90b1901e6",
        "packet_ledger_entry_sha256": "f5c26d7f4308219418f75ef82be6f5a086a475045ab694cd138bd14a55434b9f",
        "readiness_id": "principia:consequence-plan-review-readiness:model-boundary-release-governance:0002",
        "plan_id": "principia:resolution-consequence-plan:model-boundary-release-governance:0002",
        "reviewer_role_required": "qualified-release-governance-reviewer",
    },
)

GROUPS = (
    ("E-P26-SOURCE-PIN", (
        "phase25-postmerge-drift", "phase25-candidate-drift", "packet-report-file-drift",
        "packet-ledger-file-drift", "packet-checkpoint-file-drift", "packet-recovery-file-drift",
    )),
    ("E-P26-MISSING", ("missing-assurance",)),
    ("E-P26-ORPHAN", ("orphan-assurance",)),
    ("E-P26-DUPLICATE", ("duplicate-assurance-id",)),
    ("E-P26-SEQUENCE", ("assurance-sequence-drift",)),
    ("E-P26-PACKET-BINDING", (
        "packet-id-drift", "packet-record-digest-drift", "packet-ledger-entry-drift", "readiness-id-drift",
    )),
    ("E-P26-SOURCE-BINDING", ("plan-id-drift", "packet-kind-drift", "affected-set-drift")),
    ("E-P26-SECTION", ("section-count-drift", "section-sequence-drift", "section-state-drift")),
    ("E-P26-QUESTION", ("question-count-drift", "question-sequence-drift", "question-response-recorded", "question-prompt-drift")),
    ("E-P26-HUMAN-GATE", ("human-gate-count-drift", "human-gate-sequence-drift", "human-gate-satisfied", "human-gate-evidence-recorded")),
    ("E-P26-RESPONSE", (
        "response-template-submitted", "reviewer-identity-recorded", "competence-attestation-recorded",
        "conflict-declaration-recorded", "authorization-recorded", "review-observation-recorded",
        "review-recommendation-recorded",
    )),
    ("E-P26-DISPATCH", (
        "dispatch-authorized", "delivery-channel-recorded", "packet-dispatched", "dispatch-time-recorded",
        "recipient-recorded", "recipient-identifier-recorded",
    )),
    ("E-P26-PACKET-STATE", ("packet-not-local-only", "packet-not-prepared", "packet-status-drift", "packet-verdict-drift")),
    ("E-P26-CONTACT", ("reviewer-contact-permitted", "reviewer-contact-recorded")),
    ("E-P26-EXECUTION", ("review-start-permitted", "review-started", "review-completed")),
    ("E-P26-OUTCOME", ("outcome-selected",)),
    ("E-P26-EFFECT", (
        "content-change-proposed", "status-recommendation-recorded", "effective-hold",
        "operational-effect", "status-change",
    )),
    ("E-P26-AUTHORIZATION", ("human-authorization-claimed", "real-authorization-claimed")),
    ("E-P26-AUTHORITY", (
        "status-inheritance", "automatic-status-change", "automatic-release-action", "repository-mutation",
    )),
    ("E-P26-NETWORK", ("external-network-required", "external-delivery-permitted")),
    ("E-P26-ATLAS", ("atlas-call-permitted",)),
    ("E-P26-LIVE-FROZEN", ("live-activation",)),
    ("E-P26-ASSURANCE", ("assurance-check-failed", "assurance-verdict-drift")),
    ("E-P26-LEDGER", ("assurance-ledger-drift",)),
    ("E-P26-CHECKPOINT", ("assurance-checkpoint-drift",)),
)

SCENARIOS = (("baseline", "accepted", None),) + tuple(
    (name, "rejected", code) for code, names in GROUPS for name in names
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

def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value

def verify_sources() -> list[str]:
    errors = [
        f"source drift: {path.relative_to(ROOT)}"
        for path, expected in SOURCE_FILES.items()
        if not path.is_file() or file_sha(path) != expected
    ]
    if errors:
        return errors
    candidate = load(ROOT / SOURCE["phase25_candidate_path"])
    postmerge = load(ROOT / SOURCE["phase25_postmerge_path"])
    report = load(ROOT / SOURCE["packet_report_path"])
    ledger = load(ROOT / SOURCE["packet_ledger_path"])
    if candidate.get("next_gate") != STATE or postmerge.get("state") != "offline-consequence-plan-review-request-packet-validated":
        errors.append("Phase 25 state drift")
        return errors
    packets = {packet.get("packet_id"): packet for packet in report.get("packets", [])}
    entries = {wrapper.get("entry", {}).get("packet_id"): wrapper for wrapper in ledger.get("entries", [])}
    for expected in EXPECTED_PACKETS:
        packet = packets.get(expected["packet_id"])
        wrapper = entries.get(expected["packet_id"])
        if not packet or doc_sha(packet) != expected["packet_record_sha256"]:
            errors.append("Phase 25 packet binding drift")
        if not wrapper or wrapper.get("entry_sha256") != expected["packet_ledger_entry_sha256"]:
            errors.append("Phase 25 packet ledger binding drift")
    return errors

def build_assurances() -> list[dict[str, Any]]:
    checks = {
        "affected_artifact_set_exact": True,
        "authority_boundary_preserved": True,
        "blank_question_responses_preserved": True,
        "blank_response_template_preserved": True,
        "dispatch_disabled": True,
        "human_gates_remain_pending": True,
        "ledger_entry_binding_exact": True,
        "local_only_state_preserved": True,
        "packet_identity_exact": True,
        "packet_record_digest_exact": True,
        "packet_sections_complete": True,
        "question_structure_complete": True,
        "review_execution_disabled": True,
        "reviewer_unidentified": True,
        "source_binding_exact": True,
        "zero_effect_boundary_preserved": True,
    }
    assurances = []
    for sequence, expected in enumerate(EXPECTED_PACKETS, start=1):
        assurances.append({
            "affected_artifacts": list(ARTIFACTS),
            "assurance_checks": dict(checks),
            "blank_question_response_count": 3,
            "dispatch_permitted": False,
            "effective_hold": False,
            "human_authorization_claimed": False,
            "human_gate_pending_count": 4,
            "human_gate_satisfied_count": 0,
            "local_only": True,
            "operational_effect": False,
            "outcome_selected": False,
            "packet_assurance_id": expected["packet_assurance_id"],
            "packet_id": expected["packet_id"],
            "packet_kind": expected["packet_kind"],
            "packet_ledger_entry_sha256": expected["packet_ledger_entry_sha256"],
            "packet_prepared": True,
            "packet_record_sha256": expected["packet_record_sha256"],
            "packet_status": "prepared-local-not-dispatched",
            "plan_id": expected["plan_id"],
            "question_count": 3,
            "readiness_id": expected["readiness_id"],
            "real_authorization_claimed": False,
            "response_submission_count": 0,
            "response_template_submitted": False,
            "review_completed": False,
            "review_start_permitted": False,
            "review_started": False,
            "reviewer_contact_permitted": False,
            "reviewer_identity_present": False,
            "reviewer_role_required": expected["reviewer_role_required"],
            "section_count": 6,
            "sequence": sequence,
            "status_change": False,
            "verdict": "packet-assured-local-no-dispatch",
        })
    return assurances

def build() -> dict[Path, dict[str, Any]]:
    assurances = build_assurances()
    summary = {
        "assured_packet_count": 2,
        "blank_question_response_count": 6,
        "effective_hold_count": 0,
        "failed_assurance_count": 0,
        "human_authorization_count": 0,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
        "operational_effect_count": 0,
        "outcome_selected_count": 0,
        "packet_count": 2,
        "packet_dispatch_count": 0,
        "packet_local_only_count": 2,
        "packet_prepared_count": 2,
        "question_count": 6,
        "real_authorization_claimed": False,
        "response_submission_count": 0,
        "review_completed_count": 0,
        "review_started_count": 0,
        "reviewer_contact_count": 0,
        "reviewer_identity_count": 0,
        "section_count": 12,
        "status_change_count": 0,
    }
    report = {
        "assurances": assurances,
        "authority": AUTHORITY,
        "contract": "principia-offline-consequence-plan-review-request-packet-assurance-report/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "live": False,
        "mode": MODE,
        "report_id": "principia:offline-consequence-plan-review-request-packet-assurance-report:thermal-control:0001",
        "source_phase25": SOURCE,
        "summary": summary,
    }
    entries = []
    previous = None
    for assurance in assurances:
        entry = {
            "packet_assurance_id": assurance["packet_assurance_id"],
            "packet_assurance_sha256": doc_sha(assurance),
            "packet_id": assurance["packet_id"],
            "packet_record_sha256": assurance["packet_record_sha256"],
            "previous_entry_sha256": previous,
            "sequence": assurance["sequence"],
            "verdict": assurance["verdict"],
        }
        digest = doc_sha(entry)
        entries.append({"entry": entry, "entry_sha256": digest})
        previous = digest
    ledger = {
        "authority": AUTHORITY,
        "contract": "principia-offline-consequence-plan-review-request-packet-assurance-ledger/0.1",
        "decision": DECISION,
        "entries": entries,
        "head_sequence": 2,
        "head_sha256": previous,
        "ledger_id": "principia:offline-consequence-plan-review-request-packet-assurance-ledger:thermal-control:0001",
        "live": False,
        "mode": MODE,
        "source_assurance_report_sha256": doc_sha(report),
    }
    checkpoint = {
        "assurance_report_sha256": doc_sha(report),
        "assured_packet_count": 2,
        "authority": AUTHORITY,
        "checkpoint_id": "principia:offline-consequence-plan-review-request-packet-assurance-checkpoint:thermal-control:0001",
        "contract": "principia-offline-consequence-plan-review-request-packet-assurance-checkpoint/0.1",
        "decision": DECISION,
        "effective_hold_count": 0,
        "failed_assurance_count": 0,
        "human_authorization_count": 0,
        "human_gate_pending_count": 8,
        "human_gate_satisfied_count": 0,
        "ledger_sha256": doc_sha(ledger),
        "live": False,
        "mode": MODE,
        "operational_effect_count": 0,
        "outcome_selected_count": 0,
        "packet_count": 2,
        "packet_dispatch_count": 0,
        "real_authorization_claimed": False,
        "response_submission_count": 0,
        "review_completed_count": 0,
        "review_started_count": 0,
        "reviewer_contact_count": 0,
        "reviewer_identity_count": 0,
        "status_change_count": 0,
    }
    recovery = {
        "authority": AUTHORITY,
        "baseline": {
            "assurance_report_sha256": doc_sha(report),
            "checkpoint_sha256": doc_sha(checkpoint),
            "ledger_sha256": doc_sha(ledger),
        },
        "contract": "principia-offline-consequence-plan-review-request-packet-assurance-recovery/0.1",
        "live": False,
        "mode": MODE,
        "recovery_id": "principia:offline-consequence-plan-review-request-packet-assurance-recovery:thermal-control:0001",
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
            "checkpoint": {"path": CHECKPOINT_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(checkpoint)},
            "ledger": {"path": LEDGER_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(ledger)},
            "recovery": {"path": RECOVERY_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(recovery)},
            "report": {"path": REPORT_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(report)},
        },
        "authority": AUTHORITY,
        "contract": "principia-offline-consequence-plan-review-request-packet-assurance/0.1",
        "decision": DECISION,
        "fixture_kind": "bounded-synthetic",
        "id": "principia-atlas-offline-consequence-plan-review-request-packet-assurance-thermal-control",
        "live": False,
        "live_activation_permitted": False,
        "mode": MODE,
        "next_gate": NEXT_GATE,
        "phase": 26,
        "real_authorization_claimed": False,
        "result": summary,
        "source_phase25": SOURCE,
        "state": STATE,
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
    errors = verify_sources()
    try:
        bundle = build()
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Phase 26 generation failed: {exc}", file=sys.stderr)
        return 1
    for path, value in bundle.items():
        text = render(value)
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                errors.append(f"generated file drift: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    if errors:
        print("Phase 26 generation errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Phase 26 packet assurance evidence is deterministic, source-pinned, local-only, and non-dispatching.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
