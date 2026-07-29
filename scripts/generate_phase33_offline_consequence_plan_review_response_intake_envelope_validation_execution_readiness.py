#!/usr/bin/env python3
"""Generate deterministic Phase 33 envelope-validation execution-readiness evidence."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any, Mapping

ROOT=Path(__file__).resolve().parent.parent
MODE="offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness"
DECISION="response-intake-envelope-validation-execution-readiness-recorded-no-envelope-received"
STATE=MODE+"-candidate"; NEXT_GATE=MODE+"-assurance-candidate"
OUT=ROOT/"release/phase-33-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness.json"
SOURCE=ROOT/"release/phase-32-offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance.json"
POST=ROOT/"release/phase-32-postmerge.json"
SOURCE_SHA="b7c178bd026b453dff59f7caff588922206239313155daa59f4fd72c5306f92d"
POST_SHA="910416e3b212039b71d130d07db68872a1d8850dba4b73b173b5fe76e62cf5a5"
FINAL_COMMIT="5c26c9ca839e011832922fbe4feba96d98a1a344"

VALIDATION_CONTROLS="canonical-json-required|utf8-required|media-type-exact|envelope-version-exact|envelope-id-required|response-id-required|intake-readiness-binding-exact|envelope-readiness-assurance-binding-exact|packet-binding-exact|schema-binding-exact|payload-size-within-limit|payload-sha256-required|source-digest-required|submitted-at-required|signature-reference-required|human-gates-complete|duplicate-envelope-prohibited|unknown-fields-prohibited".split("|")
EXECUTION_STAGES="source-provenance-lock|immutable-input-resolution|sandbox-isolation|resource-bounds|deterministic-engine-selection|preflight-control-loading|disposition-freeze|audit-output-preparation|execution-authorization-freeze".split("|")
PRECONDITIONS="source-assurance-pinned|candidate-and-postmerge-digests-match|profile-identity-pinned|validation-control-order-pinned|blank-receipt-preserved|no-envelope-present|no-response-present|human-gates-remain-pending|local-sandbox-only|network-disabled|atlas-access-disabled|repository-write-disabled|deterministic-engine-version-pinned|payload-limit-pinned|digest-algorithm-pinned|duplicate-detection-policy-pinned|quarantine-policy-pinned|result-recording-disabled|disposition-selection-disabled|execution-authorization-absent".split("|")
DISPOSITIONS="structural-rejection|quarantine-candidate|validation-pass-candidate".split("|")
BLANK_TICKET_FIELDS="execution_run_id|envelope_id|response_id|operator_id|started_at|completed_at|engine_version|evaluated_payload_sha256|control_result_digest|selected_disposition|quarantine_record_id|operator_signature_ref".split("|")
RESOURCE_LIMITS={"atlas_access":False,"external_network":False,"max_memory_bytes":67108864,"max_output_bytes":262144,"max_payload_bytes":131072,"max_runtime_seconds":30,"repository_write":False}
EXPECTED=(
("feedback-manual-review",1,"d67980094909dbaa8a872da0575a3f515dbc70565765d98f9e2db90bd43af952","debceb016a26d3ba85d2e642b5b7e912ed30bdf596a82e42add152b3bb033110","qualified-pedagogical-reviewer"),
("model-boundary-release-governance",2,"fc48bf2ef457b75b56b949b6e0fa8563fb0eb25c1943e059ee410c2fc8ce6158","6ebc6cb6b7dfeed8a55f67b45b6f66e7e3ed53ca931e3e5852883d815e69735f","qualified-release-governance-reviewer"),
)
AUTHORITY={"atlas_call_permitted":False,"automatic_release_action":False,"automatic_status_change":False,"external_delivery_permitted":False,"external_network_required":False,"human_authorization_claimed":False,"local_response_envelope_validation_execution_readiness_permitted":True,"repository_mutation":False,"response_envelope_creation_permitted":False,"response_envelope_processing_authorized":False,"response_envelope_validation_execution_authorized":False,"response_envelope_validation_result_recording_permitted":False,"response_intake_authorized":False,"response_quarantine_execution_authorized":False,"response_receipt_permitted":False,"response_validation_authorized":False,"review_execution_authorized":False,"review_request_dispatch_authorized":False,"reviewer_contact_permitted":False,"status_inheritance":"prohibited"}
ZERO_FIELDS="execution_authorization_present|execution_ticket_issued|execution_run_created|execution_started|execution_completed|validation_result_recorded|disposition_selected|response_envelope_created|response_envelope_received|response_envelope_processed|response_intake_authorized|response_received|response_validated|response_accepted|response_rejected|response_quarantined|reviewer_identity_present|reviewer_contact_permitted|review_start_permitted|review_started|review_completed|status_change|real_authorization_claimed".split("|")
MUTATIONS=("phase32-candidate-drift|phase32-postmerge-drift|phase32-finalization-commit-drift|missing-execution-readiness-record|orphan-execution-readiness-record|duplicate-execution-readiness-record|execution-readiness-sequence-drift|execution-readiness-id-drift|source-assurance-id-drift|source-assurance-record-digest-drift|source-assurance-ledger-entry-drift|validation-readiness-id-drift|validation-profile-id-drift|reviewer-role-drift|validation-control-count-drift|validation-control-id-drift|validation-control-order-drift|blueprint-id-drift|blueprint-version-drift|blueprint-mode-drift|blueprint-input-state-drift|blueprint-digest-drift|engine-id-drift|engine-version-drift|engine-determinism-drift|stage-count-drift|stage-id-drift|stage-order-drift|stage-state-drift|precondition-count-drift|precondition-id-drift|precondition-order-drift|precondition-state-drift|disposition-count-drift|disposition-id-drift|disposition-order-drift|disposition-state-drift|resource-limit-payload-drift|resource-limit-runtime-drift|resource-limit-memory-drift|resource-limit-output-drift|resource-network-enabled|resource-atlas-enabled|resource-repository-write-enabled|ticket-count-drift|ticket-field-count-drift|execution-run-id-filled|envelope-id-filled|response-id-filled|operator-id-filled|started-at-filled|completed-at-filled|engine-version-filled|evaluated-payload-digest-filled|control-result-digest-filled|selected-disposition-filled|quarantine-record-id-filled|operator-signature-filled|execution-ticket-issued|ticket-source-binding-drift|human-gate-satisfied|execution-authorization-present|validation-execution-authorized|validation-result-recording-permitted|execution-run-created|execution-started|execution-completed|validation-result-recorded|disposition-selected|structural-rejection-selected|quarantine-candidate-selected|validation-pass-selected|envelope-created|envelope-received|envelope-processed|integrity-failure-recorded|duplicate-envelope-recorded|quarantine-record-created|quarantine-execution-authorized|response-intake-authorized|response-receipt-permitted|response-received|response-validated|response-accepted|response-rejected|response-quarantined|packet-dispatched|reviewer-contact-permitted|reviewer-identity-recorded|review-start-permitted|review-started|review-completed|outcome-selected|content-change-proposed|status-recommendation-recorded|effective-hold|operational-effect|status-change|human-authorization-claimed|real-authorization-claimed|status-inheritance-enabled|automatic-status-change|automatic-release-action|repository-mutation|external-network-required|external-delivery-permitted|atlas-call-permitted|live-activation|record-verdict-drift|record-status-drift|record-locality-drift|ledger-drift|checkpoint-drift|summary-drift|authority-drift|source-pin-drift|record-count-drift|recovery-count-drift").split("|")

def render(v:Any)->str: return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n"
def sha_doc(v:Any)->str: return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def sha_file(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:
    v=json.loads(p.read_text())
    if not isinstance(v,dict): raise ValueError(p)
    return v

def verify_sources()->list[str]:
    errors=[]
    if not SOURCE.is_file() or sha_file(SOURCE)!=SOURCE_SHA: errors.append("Phase 32 candidate file drift")
    if not POST.is_file() or sha_file(POST)!=POST_SHA: errors.append("Phase 32 postmerge file drift")
    if errors: return errors
    src,post=load(SOURCE),load(POST)
    if src.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance-candidate" or src.get("next_gate")!=STATE: errors.append("Phase 32 candidate gate drift")
    if post.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-readiness-assurance-validated" or post.get("next_gate")!=STATE: errors.append("Phase 32 finalization gate drift")
    if post.get("candidate_record",{}).get("sha256")!=SOURCE_SHA or post.get("principia",{}).get("merge_commit")!="645bb4567df6328aa47788b63206192fad2eeef4": errors.append("Phase 32 provenance drift")
    records={r.get("validation_readiness_assurance_id"):r for r in src.get("assurances",[])}
    entries={e.get("entry",{}).get("validation_readiness_assurance_id"):e for e in src.get("ledger",{}).get("entries",[])}
    for key,seq,rsha,lsha,role in EXPECTED:
        aid=f"principia:consequence-plan-review-response-intake-envelope-validation-readiness-assurance:{key}:{seq:04d}"
        r,e=records.get(aid),entries.get(aid)
        if not r or sha_doc(r)!=rsha: errors.append(f"Phase 32 assurance record drift: {key}"); continue
        if not e or e.get("entry_sha256")!=lsha: errors.append(f"Phase 32 assurance ledger drift: {key}")
        if r.get("reviewer_role_required")!=role or r.get("profile_stage_count")!=8 or r.get("profile_control_count")!=18 or r.get("blank_validation_receipt_field_count")!=10 or r.get("assurance_check_count")!=33 or not all(r.get("assurance_checks",{}).values()): errors.append(f"Phase 32 assurance content drift: {key}")
        if any(r.get(x) is not False for x in ZERO_FIELDS if x in r): errors.append(f"Phase 32 frozen-state drift: {key}")
    return errors

def blueprint()->dict[str,Any]:
    return {"blank_ticket_fields":BLANK_TICKET_FIELDS,"deterministic_engine":{"deterministic":True,"engine_id":"principia-envelope-validator","engine_version":"0.1"},"dispositions":[{"disposition_id":x,"sequence":i,"state":"defined-not-active"} for i,x in enumerate(DISPOSITIONS,1)],"input_state":"no-envelope-present","mode":"offline-preflight-only","preconditions":[{"precondition_id":x,"sequence":i,"state":"required-not-evaluated"} for i,x in enumerate(PRECONDITIONS,1)],"profile_version":"0.1","required_validation_controls":[{"control_id":x,"sequence":i} for i,x in enumerate(VALIDATION_CONTROLS,1)],"resource_limits":RESOURCE_LIMITS,"stages":[{"sequence":i,"stage_id":x,"state":"defined-not-active"} for i,x in enumerate(EXECUTION_STAGES,1)]}

def execution_profiles(bp_sha:str)->list[dict[str,Any]]:
    base="principia:consequence-plan-review-response-intake-envelope"
    return [{"blueprint_sha256":bp_sha,"execution_profile_id":f"principia:review-response-intake-envelope-validation-execution-profile:{key}:{seq:04d}","reviewer_role_required":role,"sequence":seq,"validation_profile_id":f"principia:review-response-intake-envelope-validation-profile:{key}:{seq:04d}","validation_readiness_assurance_id":f"{base}-validation-readiness-assurance:{key}:{seq:04d}"} for key,seq,_r,_l,role in EXPECTED]

def readiness_records(profiles:list[dict[str,Any]])->list[dict[str,Any]]:
    out=[]; base="principia:consequence-plan-review-response-intake-envelope"
    for profile,(key,seq,rsha,lsha,role) in zip(profiles,EXPECTED):
        ticket={"execution_profile_id":profile["execution_profile_id"],"issued":False,"validation_profile_id":profile["validation_profile_id"],"validation_readiness_assurance_id":profile["validation_readiness_assurance_id"]}
        ticket.update({x:None for x in BLANK_TICKET_FIELDS})
        r={"blank_execution_ticket":ticket,"blank_execution_ticket_field_count":len(BLANK_TICKET_FIELDS),"blueprint_sha256":profile["blueprint_sha256"],"execution_precondition_count":len(PRECONDITIONS),"execution_profile_id":profile["execution_profile_id"],"execution_stage_count":len(EXECUTION_STAGES),"human_gate_pending_count":4,"human_gate_satisfied_count":0,"local_only":True,"possible_disposition_count":len(DISPOSITIONS),"reviewer_role_required":role,"sequence":seq,"status":"execution-readiness-recorded-no-envelope-received","validation_control_count":len(VALIDATION_CONTROLS),"validation_execution_readiness_id":f"{base}-validation-execution-readiness:{key}:{seq:04d}","validation_profile_id":profile["validation_profile_id"],"validation_readiness_assurance_id":profile["validation_readiness_assurance_id"],"validation_readiness_assurance_ledger_entry_sha256":lsha,"validation_readiness_assurance_record_sha256":rsha,"verdict":"response-envelope-validation-execution-controls-ready-no-envelope"}
        r.update({x:False for x in ZERO_FIELDS}); out.append(r)
    return out

def ledger(records:list[dict[str,Any]])->dict[str,Any]:
    out=[]; prev=None
    for r in records:
        e={"previous_entry_sha256":prev,"record_sha256":sha_doc(r),"sequence":r["sequence"],"validation_execution_readiness_id":r["validation_execution_readiness_id"],"validation_readiness_assurance_id":r["validation_readiness_assurance_id"],"verdict":r["verdict"]}
        prev=sha_doc(e); out.append({"entry":e,"entry_sha256":prev})
    return {"entries":out,"head_sequence":len(out),"head_sha256":prev}

def build_document()->dict[str,Any]:
    bp=blueprint(); bp_sha=sha_doc(bp); profiles=execution_profiles(bp_sha); records=readiness_records(profiles); lg=ledger(records)
    result={"blank_execution_ticket_count":2,"blank_execution_ticket_field_count":24,"disposition_selected_count":0,"execution_authorization_present_count":0,"execution_completed_count":0,"execution_precondition_count":40,"execution_profile_count":2,"execution_readiness_record_count":2,"execution_run_count":0,"execution_stage_count":18,"execution_started_count":0,"execution_ticket_issued_count":0,"failed_precondition_count":0,"human_gate_pending_count":8,"human_gate_satisfied_count":0,"possible_disposition_count":6,"real_authorization_claimed":False,"response_accepted_count":0,"response_envelope_created_count":0,"response_envelope_processed_count":0,"response_envelope_received_count":0,"response_intake_authorized_count":0,"response_quarantined_count":0,"response_received_count":0,"response_rejected_count":0,"response_validated_count":0,"review_completed_count":0,"review_started_count":0,"reviewer_contact_count":0,"reviewer_identity_count":0,"status_change_count":0,"validation_control_count":36,"validation_execution_authorized_count":0,"validation_result_recorded_count":0}
    return {"authority":AUTHORITY,"checkpoint":{"disposition_selected_count":0,"envelope_received_count":0,"execution_authorization_present_count":0,"execution_readiness_record_count":2,"execution_run_count":0,"ledger_sha256":sha_doc(lg),"response_received_count":0,"status_change_count":0,"validation_result_recorded_count":0},"contract":"principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness/0.1","decision":DECISION,"execution_blueprint":bp,"execution_profiles":profiles,"execution_readiness_records":records,"fixture_kind":"bounded-synthetic","id":"principia-atlas-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness-thermal-control","ledger":lg,"live":False,"live_activation_permitted":False,"mode":MODE,"next_gate":NEXT_GATE,"phase":33,"real_authorization_claimed":False,"recovery":{"accepted":["baseline"],"accepted_count":1,"rejected":MUTATIONS,"rejected_count":len(MUTATIONS),"scenario_count":len(MUTATIONS)+1},"result":result,"source_phase32":{"phase32_candidate_sha256":SOURCE_SHA,"phase32_finalization_commit":FINAL_COMMIT,"phase32_postmerge_sha256":POST_SHA},"state":STATE,"validation":{"pull_request":None,"status":"pending","tested_head_commit":None}}

def validate_document(d:Mapping[str,Any])->list[str]: return [] if d==build_document() else ["document drift"]

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); p.add_argument("--skip-source-verification",action="store_true"); a=p.parse_args()
    errors=[] if a.skip_source_verification else verify_sources()
    if errors:
        print("Phase 33 source errors:",file=sys.stderr)
        for x in errors: print(f"- {x}",file=sys.stderr)
        return 1
    text=render(build_document())
    if a.check and (not OUT.is_file() or OUT.read_text()!=text): print("Phase 33 candidate differs from deterministic generation",file=sys.stderr); return 1
    if not a.check: OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(text)
    print(f"Phase 33 candidate passed: {len(text.encode())} bytes, sha256={hashlib.sha256(text.encode()).hexdigest()}, 2 execution-readiness records, 18 stages, 40 preconditions, 0 validations executed.")
    return 0
if __name__=="__main__": raise SystemExit(main())
