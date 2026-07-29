#!/usr/bin/env python3
"""Generate deterministic Phase 25 offline review-request packet evidence."""
from __future__ import annotations

import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "integration/principia-atlas/pilot"
MODE = "offline-consequence-plan-review-request-packet"
DECISION = "review-request-packets-prepared-no-dispatch"
STATE = MODE + "-candidate"
NEXT_GATE = MODE + "-assurance-candidate"
REPORT_PATH = PILOT / "thermal-control.consequence-plan-review-request-packet-report.v01.json"
LEDGER_PATH = PILOT / "thermal-control.consequence-plan-review-request-packet-ledger.v01.json"
CHECKPOINT_PATH = PILOT / "thermal-control.consequence-plan-review-request-packet-checkpoint.v01.json"
RECOVERY_PATH = PILOT / "thermal-control.consequence-plan-review-request-packet-recovery.v01.json"
RELEASE_PATH = ROOT / "release/phase-25-offline-consequence-plan-review-request-packet.json"

SOURCE_FILES = {
    ROOT / "release/phase-24-postmerge.json": "67fdb408b871116fecf97e9c5c88efe9a8fb95dc420ac19adb0184a847a09ed9",
    ROOT / "release/phase-24-offline-consequence-plan-review-readiness.json": "45ca01dd5af4cfc550abcacb4d5b6cf090c7e138ff2b4663a077fde43d615a85",
    PILOT / "thermal-control.consequence-plan-review-readiness-report.v01.json": "94e737822aa958f81e574b4ca7a8aaa4067e1a75096e9b33a6aa27bc96f2c7f7",
    PILOT / "thermal-control.consequence-plan-review-readiness-ledger.v01.json": "d939f334ff5e4a5a0fb40b2a156f42a5cea6349e39278efae8246ac3ddb7d1e8",
    PILOT / "thermal-control.consequence-plan-review-readiness-checkpoint.v01.json": "7cc87aa8087f88e4923b44458c30c3fc700e748d22e2a75fd47453273e8c11f1",
    PILOT / "thermal-control.consequence-plan-review-readiness-recovery.v01.json": "8c79d4fe431c5f2e30a95532e599c3c3ac466c81daa8f23289545ab82fb786a0",
}
SOURCE = {
    "phase24_candidate_path": "release/phase-24-offline-consequence-plan-review-readiness.json",
    "phase24_candidate_sha256": "45ca01dd5af4cfc550abcacb4d5b6cf090c7e138ff2b4663a077fde43d615a85",
    "phase24_checkpoint_path": "integration/principia-atlas/pilot/thermal-control.consequence-plan-review-readiness-checkpoint.v01.json",
    "phase24_checkpoint_sha256": "7cc87aa8087f88e4923b44458c30c3fc700e748d22e2a75fd47453273e8c11f1",
    "phase24_finalization_commit": "46c2b286bde99fd0165f0ec97463ac0fb5af2b5e",
    "phase24_ledger_path": "integration/principia-atlas/pilot/thermal-control.consequence-plan-review-readiness-ledger.v01.json",
    "phase24_ledger_sha256": "d939f334ff5e4a5a0fb40b2a156f42a5cea6349e39278efae8246ac3ddb7d1e8",
    "phase24_postmerge_path": "release/phase-24-postmerge.json",
    "phase24_postmerge_sha256": "67fdb408b871116fecf97e9c5c88efe9a8fb95dc420ac19adb0184a847a09ed9",
    "phase24_recovery_path": "integration/principia-atlas/pilot/thermal-control.consequence-plan-review-readiness-recovery.v01.json",
    "phase24_recovery_sha256": "8c79d4fe431c5f2e30a95532e599c3c3ac466c81daa8f23289545ab82fb786a0",
    "phase24_report_path": "integration/principia-atlas/pilot/thermal-control.consequence-plan-review-readiness-report.v01.json",
    "phase24_report_sha256": "94e737822aa958f81e574b4ca7a8aaa4067e1a75096e9b33a6aa27bc96f2c7f7",
}
AUTHORITY = {
    "atlas_call_permitted": False, "atlas_knowledge_status_authority": "Atlas",
    "automatic_release_action": False, "automatic_status_change": False,
    "external_delivery_permitted": False, "external_network_required": False,
    "human_authorization_claimed": False, "local_packet_preparation_permitted": True,
    "principia_pedagogical_status_authority": "Principia",
    "principia_release_status_authority": "Principia", "repository_mutation": False,
    "review_execution_authorized": False, "review_request_dispatch_authorized": False,
    "reviewer_contact_permitted": False, "status_inheritance": "prohibited",
}
ARTIFACTS = ["principia:failure-pattern:feedback-instability@1", "principia:investigation:room-cooling@1", "principia:system-dossier:refrigerator@1"]
PENDING_HUMAN_GATES = ["reviewer-identity-recorded", "reviewer-competence-attested", "conflict-declaration-recorded", "authorization-to-start-recorded"]
EXPECTED_READINESS = (
    dict(key="feedback-manual-review", assurance_id="principia:consequence-plan-assurance:feedback-manual-review:0001", packet_kind="pedagogical-review-request-packet", plan_id="principia:resolution-consequence-plan:feedback-manual-review:0001", plan_kind="manual-review-work-plan", plan_sha256="f2cf1f339f90e4c4a622440fbd86be9a97c53587f059abe0a092ad0bf01efca1", readiness_id="principia:consequence-plan-review-readiness:feedback-manual-review:0001", readiness_ledger_entry_sha256="f44e21139618175df45499f61c936a7e26750bf69efc0ce83c77574e1b8b3a18", readiness_record_sha256="453be7c298341dcd19d3968645cd49c95e26259b4497510ffd9765aa31ef4c89", review_purpose="evaluate the bounded feedback-instability material against the assured manual-review plan without starting or completing review", reviewer_role_required="qualified-pedagogical-reviewer", source_proposal_id="principia:policy-review:feedback-deprecation:0001", source_resolution_id="principia:manual-policy-resolution:feedback-deprecation:0001", questions=(("conceptual-boundary", "Does the bounded material preserve the distinction between a model result and a claim about a real system?"), ("evidence-sufficiency", "Are the exact source references sufficient for a future pedagogical review of the three affected artifacts?"), ("unresolved-pedagogical-risk", "Which unresolved pedagogical risks would require additional evidence before review could be authorized?"))),
    dict(key="model-boundary-release-governance", assurance_id="principia:consequence-plan-assurance:model-boundary-release-governance:0002", packet_kind="release-governance-review-request-packet", plan_id="principia:resolution-consequence-plan:model-boundary-release-governance:0002", plan_kind="release-governance-follow-up-plan", plan_sha256="f11b3c226fe9b457384387d1d52843e0874f4ebe246fdc4a7a8801cc374e3129", readiness_id="principia:consequence-plan-review-readiness:model-boundary-release-governance:0002", readiness_ledger_entry_sha256="b3e1d3a5a4e99d1a84aca91468b7ea08a9cfc0a17c080c131afceeb7a2f89dcf", readiness_record_sha256="24692de9e01038b79a241e64bd9947443995a2f2b834adedd490b6298a160dbd", review_purpose="evaluate evidence prerequisites for a future release-governance review without selecting or recommending a release outcome", reviewer_role_required="qualified-release-governance-reviewer", source_proposal_id="principia:release-hold-proposal:model-boundary-retraction:0001", source_resolution_id="principia:manual-policy-resolution:model-boundary-retraction:0002", questions=(("governance-evidence-sufficiency", "Are the exact evidence references sufficient to support a future release-governance review?"), ("model-boundary-risk", "Which model-boundary risks remain unresolved without converting them into a release recommendation?"), ("missing-prerequisite", "What additional prerequisite evidence, if any, should exist before review could be authorized?"))),
)
GROUPS = (
    ("E-P25-SOURCE-PIN", ("phase24-postmerge-drift", "phase24-candidate-drift", "phase24-report-drift", "phase24-ledger-drift", "phase24-checkpoint-drift", "phase24-recovery-drift")),
    ("E-P25-MISSING", ("missing-packet",)), ("E-P25-ORPHAN", ("orphan-packet",)), ("E-P25-DUPLICATE", ("duplicate-packet-id",)), ("E-P25-SEQUENCE", ("packet-sequence-drift",)),
    ("E-P25-READINESS", ("readiness-id-drift", "readiness-record-digest-drift", "readiness-ledger-entry-drift")),
    ("E-P25-SOURCE-BINDING", ("assurance-id-drift", "plan-id-drift", "plan-digest-drift", "proposal-id-drift", "resolution-id-drift")),
    ("E-P25-AFFECTED-SET", ("affected-set-drift",)), ("E-P25-PACKET", ("packet-kind-drift", "packet-status-drift", "packet-not-prepared", "packet-not-local-only")),
    ("E-P25-SECTION", ("section-count-drift", "section-sequence-drift")), ("E-P25-QUESTION", ("question-count-drift", "question-sequence-drift")),
    ("E-P25-RESPONSE", ("question-response-recorded", "response-template-submitted", "review-observation-recorded")), ("E-P25-OUTCOME", ("review-recommendation-recorded",)),
    ("E-P25-HUMAN-GATE", ("human-gate-satisfied", "reviewer-identity-recorded", "competence-attestation-recorded", "conflict-declaration-recorded")),
    ("E-P25-AUTHORIZATION", ("authorization-recorded",)), ("E-P25-DISPATCH", ("recipient-recorded", "delivery-channel-recorded", "dispatch-time-recorded", "dispatch-authorized", "packet-dispatched", "reviewer-contact-permitted", "external-delivery-permitted")),
    ("E-P25-NETWORK", ("external-network-required",)), ("E-P25-EXECUTION", ("review-start-permitted", "review-started", "review-completed")), ("E-P25-OUTCOME", ("outcome-selected",)),
    ("E-P25-EFFECT", ("content-change-proposed", "status-recommendation-recorded", "effective-hold", "operational-effect", "status-change")),
    ("E-P25-AUTHORIZATION", ("real-authorization-claimed",)), ("E-P25-AUTHORITY", ("status-inheritance", "automatic-status-change", "automatic-release-action", "repository-mutation")),
    ("E-P25-ATLAS", ("atlas-call-permitted",)), ("E-P25-LIVE-FROZEN", ("live-activation",)),
)
SCENARIOS = (("baseline", "accepted", None),) + tuple((name, "rejected", code) for code, names in GROUPS for name in names)

def render(v: Any) -> str: return json.dumps(v, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
def doc_sha(v: Any) -> str: return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
def file_sha_value(v: Any) -> str: return hashlib.sha256(render(v).encode()).hexdigest()
def file_sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p: Path) -> dict[str, Any]: return json.loads(p.read_text(encoding="utf-8"))

def verify_sources() -> list[str]:
    errors = [f"source drift: {p.relative_to(ROOT)}" for p, sha in SOURCE_FILES.items() if not p.is_file() or file_sha(p) != sha]
    if errors: return errors
    candidate, postmerge, report, ledger = (load(ROOT / SOURCE[k]) for k in ("phase24_candidate_path", "phase24_postmerge_path", "phase24_report_path", "phase24_ledger_path"))
    if candidate.get("next_gate") != "offline-consequence-plan-review-request-packet-candidate" or postmerge.get("state") != "offline-consequence-plan-review-readiness-validated": errors.append("Phase 24 state drift")
    records = {r["readiness_id"]: r for r in report.get("readiness_records", [])}; entries = {e["entry"]["readiness_id"]: e for e in ledger.get("entries", [])}
    for x in EXPECTED_READINESS:
        r, e = records.get(x["readiness_id"]), entries.get(x["readiness_id"])
        if not r or doc_sha(r) != x["readiness_record_sha256"] or not e or e.get("entry_sha256") != x["readiness_ledger_entry_sha256"]: errors.append("Phase 24 readiness binding drift")
    return errors

def build_packets() -> list[dict[str, Any]]:
    attachments = [{"path": p.relative_to(ROOT).as_posix(), "sha256": s} for p, s in SOURCE_FILES.items()]
    sections = ["review-context-and-purpose", "exact-source-bindings", "affected-artifact-scope", "pending-human-gates", "review-questions", "blank-response-template"]
    out = []
    for seq, x in enumerate(EXPECTED_READINESS, 1):
        out.append({
            "affected_artifacts": ARTIFACTS, "assurance_id": x["assurance_id"], "attachment_manifest": attachments,
            "authorization_record": None, "checks": {k: True for k in ("affected_artifact_set_exact", "attachment_manifest_exact", "authority_boundary_preserved", "blank_response_template_preserved", "dispatch_disabled", "human_gates_remain_pending", "packet_sections_complete", "plan_identity_exact", "readiness_identity_exact", "review_execution_disabled", "reviewer_unidentified", "zero_effect_boundary_preserved")},
            "competence_attestation": None, "conflict_declaration": None, "content_change_proposed": False,
            "dispatch": {"authorized": False, "channel": None, "dispatched": False, "dispatched_at": None, "recipient": None, "recipient_identifier": None},
            "effective_hold": False, "human_gates": [{"criterion_id": g, "evidence_ref": None, "sequence": i, "state": "pending"} for i, g in enumerate(PENDING_HUMAN_GATES, 1)],
            "local_only": True, "operational_effect": False, "outcome_selected": False,
            "packet_id": f"principia:consequence-plan-review-request-packet:{x['key']}:{seq:04d}", "packet_kind": x["packet_kind"], "packet_prepared": True,
            "packet_sections": [{"section_id": s, "sequence": i, "state": "prepared"} for i, s in enumerate(sections, 1)], "packet_status": "prepared-local-not-dispatched",
            "plan_id": x["plan_id"], "plan_kind": x["plan_kind"], "plan_sha256": x["plan_sha256"],
            "questions": [{"prompt": p, "question_id": q, "response": None, "sequence": i} for i, (q, p) in enumerate(x["questions"], 1)],
            "readiness_id": x["readiness_id"], "readiness_ledger_entry_sha256": x["readiness_ledger_entry_sha256"], "readiness_record_sha256": x["readiness_record_sha256"],
            "real_authorization_claimed": False, "response_template": {"authorization_to_start": None, "competence_attestation": None, "conflict_declaration": None, "review_observations": [], "review_recommendation": None, "reviewer_identity": None, "submitted": False},
            "review_completed": False, "review_purpose": x["review_purpose"], "review_start_permitted": False, "review_started": False, "reviewer_contact_permitted": False,
            "reviewer_identity": None, "reviewer_role_required": x["reviewer_role_required"], "sequence": seq, "source_proposal_id": x["source_proposal_id"], "source_resolution_id": x["source_resolution_id"],
            "status_change": False, "status_recommendation_recorded": False, "verdict": "packet-prepared-local-not-dispatched",
        })
    return out

def build() -> dict[Path, dict[str, Any]]:
    packets = build_packets(); summary = {"effective_hold_count": 0, "human_authorization_count": 0, "human_gate_pending_count": 8, "human_gate_satisfied_count": 0, "operational_effect_count": 0, "outcome_selected_count": 0, "packet_count": 2, "packet_dispatch_count": 0, "packet_local_only_count": 2, "packet_prepared_count": 2, "question_count": 6, "real_authorization_claimed": False, "response_submission_count": 0, "review_completed_count": 0, "review_started_count": 0, "reviewer_contact_count": 0, "reviewer_identity_count": 0, "section_count": 12, "status_change_count": 0}
    report = {"authority": AUTHORITY, "contract": "principia-offline-consequence-plan-review-request-packet-report/0.1", "decision": DECISION, "fixture_kind": "bounded-synthetic", "live": False, "mode": MODE, "packets": packets, "report_id": "principia:offline-consequence-plan-review-request-packet-report:thermal-control:0001", "source_phase24": SOURCE, "summary": summary}
    entries=[]; previous=None
    for p in packets:
        e={"packet_id": p["packet_id"], "packet_record_sha256": doc_sha(p), "previous_entry_sha256": previous, "readiness_id": p["readiness_id"], "sequence": p["sequence"], "verdict": p["verdict"]}; d=doc_sha(e); entries.append({"entry": e, "entry_sha256": d}); previous=d
    ledger={"authority": AUTHORITY, "contract": "principia-offline-consequence-plan-review-request-packet-ledger/0.1", "decision": DECISION, "entries": entries, "head_sequence": 2, "head_sha256": previous, "ledger_id": "principia:offline-consequence-plan-review-request-packet-ledger:thermal-control:0001", "live": False, "mode": MODE, "source_packet_report_sha256": doc_sha(report)}
    checkpoint={"authority": AUTHORITY, "checkpoint_id": "principia:offline-consequence-plan-review-request-packet-checkpoint:thermal-control:0001", "contract": "principia-offline-consequence-plan-review-request-packet-checkpoint/0.1", "decision": DECISION, "effective_hold_count": 0, "human_authorization_count": 0, "human_gate_pending_count": 8, "human_gate_satisfied_count": 0, "ledger_sha256": doc_sha(ledger), "live": False, "mode": MODE, "operational_effect_count": 0, "outcome_selected_count": 0, "packet_count": 2, "packet_dispatch_count": 0, "packet_prepared_count": 2, "packet_report_sha256": doc_sha(report), "real_authorization_claimed": False, "response_submission_count": 0, "review_completed_count": 0, "review_started_count": 0, "reviewer_contact_count": 0, "reviewer_identity_count": 0, "status_change_count": 0}
    recovery={"authority": AUTHORITY, "baseline": {"checkpoint_sha256": doc_sha(checkpoint), "ledger_sha256": doc_sha(ledger), "packet_report_sha256": doc_sha(report)}, "contract": "principia-offline-consequence-plan-review-request-packet-recovery/0.1", "live": False, "mode": MODE, "recovery_id": "principia:offline-consequence-plan-review-request-packet-recovery:thermal-control:0001", "scenarios": [{"expected_error": c, "expected_outcome": o, "scenario_id": s} for s,o,c in SCENARIOS], "summary": {"accepted_count": 1, "rejected_count": len(SCENARIOS)-1, "scenario_count": len(SCENARIOS)}}
    release={"artifacts": {"checkpoint": {"path": CHECKPOINT_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(checkpoint)}, "ledger": {"path": LEDGER_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(ledger)}, "recovery": {"path": RECOVERY_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(recovery)}, "report": {"path": REPORT_PATH.relative_to(ROOT).as_posix(), "sha256": file_sha_value(report)}}, "authority": AUTHORITY, "contract": "principia-offline-consequence-plan-review-request-packet/0.1", "decision": DECISION, "fixture_kind": "bounded-synthetic", "id": "principia-atlas-offline-consequence-plan-review-request-packet-thermal-control", "live": False, "live_activation_permitted": False, "mode": MODE, "next_gate": NEXT_GATE, "phase": 25, "real_authorization_claimed": False, "result": summary, "source_phase24": SOURCE, "state": STATE, "validation": {"pull_request": None, "status": "pending", "tested_head_commit": None}}
    return {REPORT_PATH: report, LEDGER_PATH: ledger, CHECKPOINT_PATH: checkpoint, RECOVERY_PATH: recovery, RELEASE_PATH: release}

def main() -> int:
    args=argparse.ArgumentParser(); args.add_argument("--check", action="store_true"); check=args.parse_args().check; errors=verify_sources(); bundle=build()
    for p,v in bundle.items():
        t=render(v)
        if check:
            if not p.is_file() or p.read_text(encoding="utf-8") != t: errors.append(f"generated file drift: {p.relative_to(ROOT)}")
        else: p.parent.mkdir(parents=True, exist_ok=True); p.write_text(t, encoding="utf-8")
    if errors:
        print("Phase 25 generation errors:", file=sys.stderr); [print(f"- {e}", file=sys.stderr) for e in errors]; return 1
    print("Phase 25 review-request packet evidence is deterministic, local-only, and source-pinned."); return 0
if __name__ == "__main__": raise SystemExit(main())
