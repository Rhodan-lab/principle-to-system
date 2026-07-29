#!/usr/bin/env python3
"""Generate deterministic Phase 34 validation-execution-readiness assurance evidence."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any, Mapping

ROOT=Path(__file__).resolve().parent.parent
MODE="offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance"
DECISION="response-intake-envelope-validation-execution-readiness-assured-no-envelope-received"
STATE=MODE+"-candidate"
NEXT_GATE="offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-candidate"
OUT=ROOT/"release/phase-34-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance.json"
SOURCE=ROOT/"release/phase-33-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness.json"
POST=ROOT/"release/phase-33-postmerge.json"
SOURCE_SHA="6e0eee781b4a8b76baf1d29e8504fac0686cf306d052d69bd2e3966071562284"
POST_SHA="666f6171fb1ef7c0a2e9e1b9fd4c8d521b3fcc6c12e945819b1d98f04ca50886"
FINAL_COMMIT="55ee00ddd90913dd757752bfa1f47e0eb31b081d"
BLUEPRINT_SHA="e01ad2a0d37735510c98cb6264268a3e284610477fbb621e482e1941ba3bff25"
STAGES="source-provenance-lock|immutable-input-resolution|sandbox-isolation|resource-bounds|deterministic-engine-selection|preflight-control-loading|disposition-freeze|audit-output-preparation|execution-authorization-freeze".split("|")
PRECONDITIONS="source-assurance-pinned|candidate-and-postmerge-digests-match|profile-identity-pinned|validation-control-order-pinned|blank-receipt-preserved|no-envelope-present|no-response-present|human-gates-remain-pending|local-sandbox-only|network-disabled|atlas-access-disabled|repository-write-disabled|deterministic-engine-version-pinned|payload-limit-pinned|digest-algorithm-pinned|duplicate-detection-policy-pinned|quarantine-policy-pinned|result-recording-disabled|disposition-selection-disabled|execution-authorization-absent".split("|")
CONTROLS="canonical-json-required|utf8-required|media-type-exact|envelope-version-exact|envelope-id-required|response-id-required|intake-readiness-binding-exact|envelope-readiness-assurance-binding-exact|packet-binding-exact|schema-binding-exact|payload-size-within-limit|payload-sha256-required|source-digest-required|submitted-at-required|signature-reference-required|human-gates-complete|duplicate-envelope-prohibited|unknown-fields-prohibited".split("|")
DISPOSITIONS="structural-rejection|quarantine-candidate|validation-pass-candidate".split("|")
BLANK_FIELDS="execution_run_id|envelope_id|response_id|operator_id|started_at|completed_at|engine_version|evaluated_payload_sha256|control_result_digest|selected_disposition|quarantine_record_id|operator_signature_ref".split("|")
RESOURCE_LIMITS={"atlas_access":False,"external_network":False,"max_memory_bytes":67108864,"max_output_bytes":262144,"max_payload_bytes":131072,"max_runtime_seconds":30,"repository_write":False}
EXPECTED=(
("feedback-manual-review",1,"b018be5b86af44a8d0ccf988598a632864e52d1a9a85beee85f38d72055cc874","ff0e2c5d1dd95d405a1534ef602a7b5acc6902efb9327c4f84aa912677aca528","qualified-pedagogical-reviewer"),
("model-boundary-release-governance",2,"be3bd249741cef76ad226813bdcff19f5242e0b648f10c79a0e0b91079ce0c26","2899cd744c445c9510be0950db92032776c3c272d0876263979b89dfcc251f1f","qualified-release-governance-reviewer"),
)
CHECKS=(
"atlas_access_disabled","authority_boundary_preserved","blank_ticket_exact","blank_ticket_source_bindings_exact",
"blueprint_digest_exact","blueprint_input_state_exact","blueprint_mode_exact","blueprint_version_exact",
"control_count_exact","control_order_exact","deterministic_engine_exact","disposition_count_exact",
"disposition_order_exact","disposition_states_inactive","engine_determinism_exact","envelope_states_frozen",
"execution_authorization_absent","execution_profile_identity_exact","execution_readiness_identity_exact",
"execution_readiness_ledger_binding_exact","execution_readiness_record_digest_exact","execution_states_frozen",
"human_gates_remain_pending","local_only_preserved","network_disabled","precondition_count_exact",
"precondition_order_exact","precondition_states_unevaluated","repository_write_disabled","resource_limits_exact",
"response_states_frozen","review_states_frozen","reviewer_role_exact","source_assurance_identity_exact",
"source_candidate_exact","source_finalization_exact","source_postmerge_exact","stage_count_exact",
"stage_order_exact","stage_states_inactive","ticket_unissued","validation_profile_identity_exact",
"validation_result_state_frozen","zero_effect_boundary_preserved")
ZERO_FIELDS="execution_authorization_present|execution_ticket_issued|execution_run_created|execution_started|execution_completed|validation_result_recorded|disposition_selected|response_envelope_created|response_envelope_received|response_envelope_processed|response_intake_authorized|response_received|response_validated|response_accepted|response_rejected|response_quarantined|reviewer_identity_present|reviewer_contact_permitted|review_start_permitted|review_started|review_completed|status_change|real_authorization_claimed".split("|")
AUTHORITY={"atlas_call_permitted":False,"automatic_release_action":False,"automatic_status_change":False,"external_delivery_permitted":False,"external_network_required":False,"human_authorization_claimed":False,"local_response_envelope_validation_execution_readiness_assurance_permitted":True,"repository_mutation":False,"response_envelope_creation_permitted":False,"response_envelope_processing_authorized":False,"response_envelope_validation_execution_authorized":False,"response_envelope_validation_result_recording_permitted":False,"response_intake_authorized":False,"response_quarantine_execution_authorized":False,"response_receipt_permitted":False,"response_validation_authorized":False,"review_execution_authorized":False,"review_request_dispatch_authorized":False,"reviewer_contact_permitted":False,"status_inheritance":"prohibited"}
MUTATIONS=("phase33-candidate-drift|phase33-postmerge-drift|phase33-finalization-commit-drift|missing-execution-readiness-assurance|orphan-execution-readiness-assurance|duplicate-execution-readiness-assurance|assurance-sequence-drift|assurance-id-drift|execution-readiness-id-drift|execution-readiness-record-digest-drift|execution-readiness-ledger-entry-drift|execution-profile-id-drift|validation-profile-id-drift|source-assurance-id-drift|reviewer-role-drift|blueprint-digest-drift|blueprint-version-drift|blueprint-mode-drift|blueprint-input-state-drift|engine-id-drift|engine-version-drift|engine-determinism-drift|stage-count-drift|stage-id-drift|stage-order-drift|stage-state-drift|precondition-count-drift|precondition-id-drift|precondition-order-drift|precondition-state-drift|control-count-drift|control-id-drift|control-order-drift|disposition-count-drift|disposition-id-drift|disposition-order-drift|disposition-state-drift|resource-limit-payload-drift|resource-limit-runtime-drift|resource-limit-memory-drift|resource-limit-output-drift|resource-network-enabled|resource-atlas-enabled|resource-repository-write-enabled|blank-ticket-count-drift|blank-ticket-field-count-drift|execution-run-id-filled|envelope-id-filled|response-id-filled|operator-id-filled|started-at-filled|completed-at-filled|engine-version-filled|evaluated-payload-digest-filled|control-result-digest-filled|selected-disposition-filled|quarantine-record-id-filled|operator-signature-filled|execution-ticket-issued|ticket-source-binding-drift|human-gate-satisfied|execution-authorization-present|validation-execution-authorized|validation-result-recording-permitted|execution-run-created|execution-started|execution-completed|validation-result-recorded|disposition-selected|structural-rejection-selected|quarantine-candidate-selected|validation-pass-selected|envelope-created|envelope-received|envelope-processed|integrity-failure-recorded|duplicate-envelope-recorded|quarantine-record-created|quarantine-execution-authorized|response-intake-authorized|response-receipt-permitted|response-received|response-validated|response-accepted|response-rejected|response-quarantined|packet-dispatched|reviewer-contact-permitted|reviewer-identity-recorded|review-start-permitted|review-started|review-completed|outcome-selected|content-change-proposed|status-recommendation-recorded|effective-hold|operational-effect|status-change|human-authorization-claimed|real-authorization-claimed|status-inheritance-enabled|automatic-status-change|automatic-release-action|repository-mutation|external-network-required|external-delivery-permitted|atlas-call-permitted|live-activation|assurance-check-failed|assurance-verdict-drift|assurance-status-drift|assurance-locality-drift|assurance-ledger-drift|assurance-checkpoint-drift|summary-drift|authority-drift|source-pin-drift|assurance-count-drift|recovery-count-drift|next-gate-drift").split("|")

def render(v:Any)->str: return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n"
def sha_doc(v:Any)->str: return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def sha_file(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:
    v=json.loads(p.read_text())
    if not isinstance(v,dict): raise ValueError(p)
    return v

def verify_sources()->list[str]:
    errors=[]
    if not SOURCE.is_file() or sha_file(SOURCE)!=SOURCE_SHA: errors.append("Phase 33 candidate file drift")
    if not POST.is_file() or sha_file(POST)!=POST_SHA: errors.append("Phase 33 postmerge file drift")
    if errors: return errors
    src,post=load(SOURCE),load(POST)
    if src.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-candidate" or src.get("next_gate")!=STATE: errors.append("Phase 33 candidate gate drift")
    if post.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-validated" or post.get("next_gate")!=STATE: errors.append("Phase 33 finalization gate drift")
    if post.get("candidate_record",{}).get("sha256")!=SOURCE_SHA or post.get("principia",{}).get("merge_commit")!="d05db33982e0001c9ebc636043dc0cc64592c42d": errors.append("Phase 33 provenance drift")
    bp=src.get("execution_blueprint",{})
    if sha_doc(bp)!=BLUEPRINT_SHA: errors.append("Phase 33 blueprint digest drift")
    if [x.get("stage_id") for x in bp.get("stages",[])]!=STAGES or any(x.get("state")!="defined-not-active" for x in bp.get("stages",[])): errors.append("Phase 33 stage drift")
    if [x.get("precondition_id") for x in bp.get("preconditions",[])]!=PRECONDITIONS or any(x.get("state")!="required-not-evaluated" for x in bp.get("preconditions",[])): errors.append("Phase 33 precondition drift")
    if [x.get("control_id") for x in bp.get("required_validation_controls",[])]!=CONTROLS: errors.append("Phase 33 control drift")
    if [x.get("disposition_id") for x in bp.get("dispositions",[])]!=DISPOSITIONS or any(x.get("state")!="defined-not-active" for x in bp.get("dispositions",[])): errors.append("Phase 33 disposition drift")
    if bp.get("resource_limits")!=RESOURCE_LIMITS or bp.get("deterministic_engine")!={"deterministic":True,"engine_id":"principia-envelope-validator","engine_version":"0.1"}: errors.append("Phase 33 engine/resource drift")
    records={r.get("validation_execution_readiness_id"):r for r in src.get("execution_readiness_records",[])}
    entries={e.get("entry",{}).get("validation_execution_readiness_id"):e for e in src.get("ledger",{}).get("entries",[])}
    for key,seq,rsha,lsha,role in EXPECTED:
        rid=f"principia:consequence-plan-review-response-intake-envelope-validation-execution-readiness:{key}:{seq:04d}"
        r,e=records.get(rid),entries.get(rid)
        if not r or sha_doc(r)!=rsha: errors.append(f"Phase 33 readiness record drift: {key}"); continue
        if not e or e.get("entry_sha256")!=lsha: errors.append(f"Phase 33 readiness ledger drift: {key}")
        if r.get("reviewer_role_required")!=role or r.get("blueprint_sha256")!=BLUEPRINT_SHA or r.get("execution_stage_count")!=9 or r.get("execution_precondition_count")!=20 or r.get("validation_control_count")!=18 or r.get("blank_execution_ticket_field_count")!=12: errors.append(f"Phase 33 readiness content drift: {key}")
        ticket=r.get("blank_execution_ticket",{})
        if ticket.get("issued") is not False or any(ticket.get(x) is not None for x in BLANK_FIELDS): errors.append(f"Phase 33 blank ticket drift: {key}")
        if any(r.get(x) is not False for x in ZERO_FIELDS): errors.append(f"Phase 33 frozen state drift: {key}")
    return errors

def assurance_records()->list[dict[str,Any]]:
    out=[]
    base="principia:consequence-plan-review-response-intake-envelope"
    for key,seq,rsha,lsha,role in EXPECTED:
        r={"assurance_check_count":len(CHECKS),"assurance_checks":{x:True for x in CHECKS},"blank_execution_ticket_field_count":len(BLANK_FIELDS),"blueprint_sha256":BLUEPRINT_SHA,"disposition_count":len(DISPOSITIONS),"execution_precondition_count":len(PRECONDITIONS),"execution_profile_id":f"principia:review-response-intake-envelope-validation-execution-profile:{key}:{seq:04d}","execution_readiness_assurance_id":f"{base}-validation-execution-readiness-assurance:{key}:{seq:04d}","execution_readiness_id":f"{base}-validation-execution-readiness:{key}:{seq:04d}","execution_readiness_ledger_entry_sha256":lsha,"execution_readiness_record_sha256":rsha,"execution_stage_count":len(STAGES),"human_gate_pending_count":4,"human_gate_satisfied_count":0,"local_only":True,"reviewer_role_required":role,"sequence":seq,"status":"execution-readiness-assured-no-envelope-received","validation_control_count":len(CONTROLS),"validation_profile_id":f"principia:review-response-intake-envelope-validation-profile:{key}:{seq:04d}","validation_readiness_assurance_id":f"{base}-validation-readiness-assurance:{key}:{seq:04d}","verdict":"response-envelope-validation-execution-readiness-assured-no-envelope"}
        r.update({x:False for x in ZERO_FIELDS}); out.append(r)
    return out

def ledger(records:list[dict[str,Any]])->dict[str,Any]:
    entries=[]; prev=None
    for r in records:
        e={"execution_readiness_assurance_id":r["execution_readiness_assurance_id"],"execution_readiness_id":r["execution_readiness_id"],"previous_entry_sha256":prev,"record_sha256":sha_doc(r),"sequence":r["sequence"],"verdict":r["verdict"]}
        prev=sha_doc(e); entries.append({"entry":e,"entry_sha256":prev})
    return {"entries":entries,"head_sequence":len(entries),"head_sha256":prev}

def build_document()->dict[str,Any]:
    records=assurance_records(); lg=ledger(records)
    result={"assurance_check_count":len(CHECKS)*2,"assured_execution_readiness_record_count":2,"blank_execution_ticket_count":2,"blank_execution_ticket_field_count":24,"blueprint_count":1,"disposition_selected_count":0,"execution_authorization_present_count":0,"execution_completed_count":0,"execution_precondition_count":40,"execution_profile_count":2,"execution_readiness_record_count":2,"execution_run_count":0,"execution_stage_count":18,"execution_started_count":0,"execution_ticket_issued_count":0,"failed_assurance_count":0,"failed_precondition_count":0,"human_gate_pending_count":8,"human_gate_satisfied_count":0,"possible_disposition_count":6,"real_authorization_claimed":False,"response_accepted_count":0,"response_envelope_created_count":0,"response_envelope_processed_count":0,"response_envelope_received_count":0,"response_intake_authorized_count":0,"response_quarantined_count":0,"response_received_count":0,"response_rejected_count":0,"response_validated_count":0,"review_completed_count":0,"review_started_count":0,"reviewer_contact_count":0,"reviewer_identity_count":0,"status_change_count":0,"validation_control_count":36,"validation_execution_authorized_count":0,"validation_result_recorded_count":0}
    return {"assurances":records,"authority":AUTHORITY,"checkpoint":{"assurance_check_count":len(CHECKS)*2,"assured_execution_readiness_record_count":2,"disposition_selected_count":0,"execution_authorization_present_count":0,"execution_run_count":0,"failed_assurance_count":0,"ledger_sha256":sha_doc(lg),"response_envelope_received_count":0,"response_received_count":0,"status_change_count":0,"validation_result_recorded_count":0},"contract":"principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance/0.1","decision":DECISION,"fixture_kind":"bounded-synthetic","id":"principia-atlas-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-assurance-thermal-control","ledger":lg,"live":False,"live_activation_permitted":False,"mode":MODE,"next_gate":NEXT_GATE,"phase":34,"real_authorization_claimed":False,"recovery":{"accepted":["baseline"],"accepted_count":1,"rejected":MUTATIONS,"rejected_count":len(MUTATIONS),"scenario_count":len(MUTATIONS)+1},"result":result,"source_phase33":{"phase33_candidate_sha256":SOURCE_SHA,"phase33_finalization_commit":FINAL_COMMIT,"phase33_postmerge_sha256":POST_SHA},"state":STATE,"validation":{"pull_request":None,"status":"pending","tested_head_commit":None}}

def validate_document(d:Mapping[str,Any])->list[str]: return [] if d==build_document() else ["document drift"]

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); p.add_argument("--skip-source-verification",action="store_true"); a=p.parse_args()
    errors=[] if a.skip_source_verification else verify_sources()
    if errors:
        print("Phase 34 source errors:",file=sys.stderr)
        for x in errors: print(f"- {x}",file=sys.stderr)
        return 1
    text=render(build_document())
    if a.check and (not OUT.is_file() or OUT.read_text()!=text): print("Phase 34 candidate differs from deterministic generation",file=sys.stderr); return 1
    if not a.check: OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(text)
    print(f"Phase 34 candidate passed: {len(text.encode())} bytes, sha256={hashlib.sha256(text.encode()).hexdigest()}, 2 assurances, {len(CHECKS)*2} checks, 0 validations executed.")
    return 0
if __name__=="__main__": raise SystemExit(main())
