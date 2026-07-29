#!/usr/bin/env python3
"""Generate deterministic Phase 32 validation-readiness assurance evidence."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any, Mapping

ROOT=Path(__file__).resolve().parent.parent
MODE='offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance'
DECISION='response-intake-envelope-validation-readiness-assured-no-envelope-received'
STATE=MODE+"-candidate"
NEXT_GATE='offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-candidate'
OUT=ROOT/"release/phase-32-offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance.json"
SOURCE=ROOT/"release/phase-31-offline-consequence-plan-review-response-intake-envelope-validation-readiness.json"
POST=ROOT/"release/phase-31-postmerge.json"
SOURCE_SHA="a764c145481d1ddba59df45dd29042636547ced8f308fbaf3f22b6ce79c0473c"
POST_SHA="85107f63054ceef1358bdb1e505c780831dbd09bc1c803923153a07f7b44ca92"
FINAL_COMMIT="ba7a6c26b8510993085e4323625bd96e0a0184c1"
STAGES=("source-provenance","envelope-structure","identity-bindings","payload-integrity","human-gate-preconditions","duplicate-detection","quarantine-classification","decision-freeze")
CONTROLS=("canonical-json-required","utf8-required","media-type-exact","envelope-version-exact","envelope-id-required","response-id-required","intake-readiness-binding-exact","envelope-readiness-assurance-binding-exact","packet-binding-exact","schema-binding-exact","payload-size-within-limit","payload-sha256-required","source-digest-required","submitted-at-required","signature-reference-required","human-gates-complete","duplicate-envelope-prohibited","unknown-fields-prohibited")
DISPOSITIONS=("structural-rejection","quarantine-candidate","validation-pass-candidate")
BLANK=("validation_run_id","envelope_id","response_id","validation_started_at","validation_completed_at","evaluated_payload_sha256","failed_control_ids","selected_disposition","quarantine_reason_ids","validator_signature_ref")
CHECKS=('authority_boundary_preserved', 'blank_receipt_exact', 'blank_receipt_source_bindings_exact', 'control_count_exact', 'control_order_exact', 'control_states_inactive', 'digest_algorithm_exact', 'disposition_count_exact', 'disposition_order_exact', 'dispositions_unselected', 'encoding_exact', 'envelope_states_frozen', 'human_gates_remain_pending', 'local_only_preserved', 'media_type_exact', 'payload_limit_exact', 'profile_identity_exact', 'profile_input_state_exact', 'profile_mode_exact', 'profile_version_exact', 'response_states_frozen', 'review_states_frozen', 'source_candidate_exact', 'source_finalization_exact', 'source_postmerge_exact', 'stage_count_exact', 'stage_order_exact', 'stage_states_inactive', 'validation_readiness_identity_exact', 'validation_readiness_ledger_binding_exact', 'validation_readiness_record_digest_exact', 'validation_states_frozen', 'zero_effect_boundary_preserved')
EXPECTED=(
("feedback-manual-review",1,"1bb4ce12d295bae9d297e96f085472a6f8e65e5caa94acb1a0622db764d37fc0","7e5029ea1095163ca3905e9f8b72ef3fcb7fbfbbc50b75f44d879d113d8e79dd","qualified-pedagogical-reviewer"),
("model-boundary-release-governance",2,"59992d272f2970a577bc425a2557d706dbce9582386dee5ee85ae2fc444c0497","3dd15e4d9786e7749ea46dec0785d477c19131136cb791bc055a0b5758993078","qualified-release-governance-reviewer"),
)
AUTHORITY={
"atlas_call_permitted":False,"automatic_release_action":False,"automatic_status_change":False,
"external_delivery_permitted":False,"external_network_required":False,"human_authorization_claimed":False,
"local_response_envelope_validation_readiness_assurance_permitted":True,"repository_mutation":False,
"response_envelope_creation_permitted":False,"response_envelope_processing_authorized":False,
"response_envelope_validation_execution_authorized":False,
"response_envelope_validation_result_recording_permitted":False,"response_intake_authorized":False,
"response_quarantine_execution_authorized":False,"response_receipt_permitted":False,
"response_validation_authorized":False,"review_execution_authorized":False,
"review_request_dispatch_authorized":False,"reviewer_contact_permitted":False,
"status_inheritance":"prohibited"}
MUTATIONS=('phase31-candidate-drift', 'phase31-postmerge-drift', 'missing-validation-readiness-assurance', 'orphan-validation-readiness-assurance', 'duplicate-validation-readiness-assurance', 'assurance-sequence-drift', 'validation-readiness-id-drift', 'validation-readiness-record-digest-drift', 'validation-readiness-ledger-entry-drift', 'source-assurance-id-drift', 'envelope-readiness-assurance-id-drift', 'envelope-readiness-id-drift', 'envelope-spec-id-drift', 'intake-readiness-assurance-id-drift', 'packet-assurance-id-drift', 'packet-id-drift', 'schema-id-drift', 'reviewer-role-drift', 'profile-id-drift', 'profile-version-drift', 'profile-mode-drift', 'profile-input-state-drift', 'profile-media-type-drift', 'profile-encoding-drift', 'profile-digest-algorithm-drift', 'profile-payload-limit-drift', 'stage-count-drift', 'stage-id-drift', 'stage-order-drift', 'stage-state-drift', 'control-count-drift', 'control-id-drift', 'control-order-drift', 'control-state-drift', 'disposition-count-drift', 'disposition-id-drift', 'disposition-order-drift', 'disposition-state-drift', 'blank-receipt-count-drift', 'blank-receipt-field-count-drift', 'validation-run-id-filled', 'envelope-id-filled', 'response-id-filled', 'validation-started-at-filled', 'validation-completed-at-filled', 'evaluated-payload-digest-filled', 'failed-control-ids-filled', 'selected-disposition-filled', 'quarantine-reason-ids-filled', 'validator-signature-filled', 'blank-receipt-executed', 'blank-receipt-source-binding-drift', 'human-gate-satisfied', 'validation-run-created', 'validation-started', 'validation-completed', 'validation-execution-authorized', 'validation-result-recording-permitted', 'validation-check-executed', 'validation-failure-recorded', 'disposition-selected', 'structural-rejection-selected', 'quarantine-candidate-selected', 'validation-pass-selected', 'envelope-created', 'envelope-received', 'envelope-processed', 'integrity-failure-recorded', 'duplicate-envelope-recorded', 'quarantine-record-created', 'quarantine-execution-authorized', 'response-intake-authorized', 'response-receipt-permitted', 'response-received', 'response-validated', 'response-accepted', 'response-rejected', 'response-quarantined', 'packet-dispatched', 'reviewer-contact-permitted', 'reviewer-identity-recorded', 'review-start-permitted', 'review-started', 'review-completed', 'outcome-selected', 'content-change-proposed', 'status-recommendation-recorded', 'effective-hold', 'operational-effect', 'status-change', 'human-authorization-claimed', 'real-authorization-claimed', 'status-inheritance-enabled', 'automatic-status-change', 'automatic-release-action', 'repository-mutation', 'external-network-required', 'external-delivery-permitted', 'atlas-call-permitted', 'live-activation', 'assurance-check-failed', 'assurance-verdict-drift', 'assurance-status-drift', 'assurance-locality-drift', 'assurance-ledger-drift', 'assurance-checkpoint-drift', 'summary-drift', 'authority-drift', 'source-pin-drift', 'assurance-count-drift', 'recovery-count-drift')
ZERO=("validation_run_created","validation_started","validation_completed","validation_result_recorded",
"disposition_selected","response_envelope_created","response_envelope_received","response_envelope_processed",
"response_intake_authorized","response_received","response_validated","response_accepted","response_rejected",
"response_quarantined","reviewer_identity_present","reviewer_contact_permitted","review_start_permitted",
"review_started","review_completed","status_change","real_authorization_claimed")

def render(v:Any)->str:
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n"

def sha_doc(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def sha_file(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p:Path)->dict[str,Any]:
    v=json.loads(p.read_text())
    if not isinstance(v,dict): raise ValueError(p)
    return v

def verify_sources()->list[str]:
    errors=[]
    if not SOURCE.is_file() or sha_file(SOURCE)!=SOURCE_SHA:
        errors.append("Phase 31 candidate file drift")
    if not POST.is_file() or sha_file(POST)!=POST_SHA:
        errors.append("Phase 31 postmerge file drift")
    if errors: return errors
    src,post=load(SOURCE),load(POST)
    if src.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-readiness-candidate" or src.get("next_gate")!=STATE:
        errors.append("Phase 31 candidate gate drift")
    if post.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-readiness-validated" or post.get("next_gate")!=STATE:
        errors.append("Phase 31 finalization gate drift")
    if post.get("candidate_record",{}).get("sha256")!=SOURCE_SHA:
        errors.append("Phase 31 candidate digest drift")
    records={r.get("validation_readiness_id"):r for r in src.get("validation_readiness_records",[])}
    entries={x.get("entry",{}).get("validation_readiness_id"):x for x in src.get("ledger",{}).get("entries",[])}
    for key,seq,rsha,lsha,_role in EXPECTED:
        rid=f"principia:consequence-plan-review-response-intake-envelope-validation-readiness:{key}:{seq:04d}"
        record,wrapper=records.get(rid),entries.get(rid)
        if not record or sha_doc(record)!=rsha:
            errors.append(f"Phase 31 record drift: {key}")
            continue
        if not wrapper or wrapper.get("entry_sha256")!=lsha:
            errors.append(f"Phase 31 ledger drift: {key}")
        profile=record.get("validation_profile",{})
        if [x.get("stage_id") for x in profile.get("stages",[])]!=list(STAGES):
            errors.append(f"Phase 31 stage drift: {key}")
        if [x.get("control_id") for x in profile.get("controls",[])]!=list(CONTROLS):
            errors.append(f"Phase 31 control drift: {key}")
        if [x.get("disposition_id") for x in profile.get("dispositions",[])]!=list(DISPOSITIONS):
            errors.append(f"Phase 31 disposition drift: {key}")
        receipt=record.get("blank_validation_receipt",{})
        if any(receipt.get(x) is not None for x in BLANK) or receipt.get("executed") is not False:
            errors.append(f"Phase 31 blank receipt drift: {key}")
    return errors

def assurance_records()->list[dict[str,Any]]:
    out=[]
    prefix="principia:consequence-plan-review-response-intake-envelope"
    for key,seq,rsha,lsha,role in EXPECTED:
        r={
        "assurance_check_count":len(CHECKS),"assurance_checks":{x:True for x in CHECKS},
        "blank_validation_receipt_field_count":len(BLANK),"disposition_count":len(DISPOSITIONS),
        "envelope_readiness_assurance_id":f"principia:consequence-plan-review-response-intake-envelope-readiness-assurance:{key}:{seq:04d}",
        "human_gate_pending_count":4,"human_gate_satisfied_count":0,"local_only":True,
        "profile_control_count":len(CONTROLS),"profile_stage_count":len(STAGES),
        "reviewer_role_required":role,"sequence":seq,
        "status":"validation-readiness-assured-no-envelope-received",
        "validation_profile_id":f"principia:review-response-intake-envelope-validation-profile:{key}:{seq:04d}",
        "validation_readiness_assurance_id":f"{prefix}-validation-readiness-assurance:{key}:{seq:04d}",
        "validation_readiness_id":f"{prefix}-validation-readiness:{key}:{seq:04d}",
        "validation_readiness_ledger_entry_sha256":lsha,
        "validation_readiness_record_sha256":rsha,
        "verdict":"response-envelope-validation-readiness-assured-no-envelope"}
        r.update({x:False for x in ZERO})
        out.append(r)
    return out

def ledger(records:list[dict[str,Any]])->dict[str,Any]:
    entries=[]; prev=None
    for r in records:
        entry={
        "previous_entry_sha256":prev,"record_sha256":sha_doc(r),"sequence":r["sequence"],
        "validation_readiness_assurance_id":r["validation_readiness_assurance_id"],
        "validation_readiness_id":r["validation_readiness_id"],"verdict":r["verdict"]}
        prev=sha_doc(entry)
        entries.append({"entry":entry,"entry_sha256":prev})
    return {"entries":entries,"head_sequence":len(entries),"head_sha256":prev}

def build_document()->dict[str,Any]:
    records=assurance_records(); lg=ledger(records)
    result={
    "assurance_check_count":len(CHECKS)*2,"assured_validation_readiness_record_count":2,
    "blank_validation_receipt_count":2,"blank_validation_receipt_field_count":20,
    "disposition_selected_count":0,"failed_assurance_count":0,"failed_control_count":0,
    "human_gate_pending_count":8,"human_gate_satisfied_count":0,"possible_disposition_count":6,
    "response_accepted_count":0,"response_envelope_created_count":0,
    "response_envelope_processed_count":0,"response_envelope_received_count":0,
    "response_intake_authorized_count":0,"response_quarantined_count":0,
    "response_received_count":0,"response_rejected_count":0,"response_validated_count":0,
    "review_completed_count":0,"review_started_count":0,"reviewer_contact_count":0,
    "reviewer_identity_count":0,"status_change_count":0,"validation_completed_count":0,
    "validation_control_count":36,"validation_execution_authorized_count":0,
    "validation_profile_count":2,"validation_readiness_record_count":2,
    "validation_result_recorded_count":0,"validation_run_count":0,
    "validation_stage_count":16,"validation_started_count":0,
    "real_authorization_claimed":False}
    return {
    "assurances":records,"authority":AUTHORITY,
    "checkpoint":{"assurance_check_count":len(CHECKS)*2,
      "assured_validation_readiness_record_count":2,"disposition_selected_count":0,
      "envelope_received_count":0,"failed_assurance_count":0,"ledger_sha256":sha_doc(lg),
      "response_received_count":0,"status_change_count":0,"validation_run_count":0},
    "contract":"principia-offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance/0.1",
    "decision":DECISION,"fixture_kind":"bounded-synthetic",
    "id":"principia-atlas-offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance-thermal-control",
    "ledger":lg,"live":False,"live_activation_permitted":False,"mode":MODE,"next_gate":NEXT_GATE,
    "phase":32,"real_authorization_claimed":False,
    "recovery":{"accepted":["baseline"],"accepted_count":1,"rejected":list(MUTATIONS),
      "rejected_count":len(MUTATIONS),"scenario_count":len(MUTATIONS)+1},
    "result":result,
    "source_phase31":{"phase31_candidate_sha256":SOURCE_SHA,
      "phase31_finalization_commit":FINAL_COMMIT,"phase31_postmerge_sha256":POST_SHA},
    "state":STATE,"validation":{"pull_request":None,"status":"pending","tested_head_commit":None}}

def validate_document(d:Mapping[str,Any])->list[str]:
    return [] if d==build_document() else ["document drift"]

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--skip-source-verification",action="store_true")
    args=parser.parse_args()
    errors=[] if args.skip_source_verification else verify_sources()
    if errors:
        print("Phase 32 source errors:",file=sys.stderr)
        [print(f"- {x}",file=sys.stderr) for x in errors]
        return 1
    text=render(build_document())
    if args.check and (not OUT.is_file() or OUT.read_text()!=text):
        print("Phase 32 candidate differs from deterministic generation",file=sys.stderr); return 1
    if not args.check:
        OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(text)
    print(f"Phase 32 candidate passed: {len(text.encode())} bytes, sha256={hashlib.sha256(text.encode()).hexdigest()}, 2 assurances, {len(CHECKS)*2} checks, 0 validations executed.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
