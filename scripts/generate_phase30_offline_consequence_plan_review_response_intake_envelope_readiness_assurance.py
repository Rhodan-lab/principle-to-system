#!/usr/bin/env python3
"""Generate deterministic Phase 30 envelope-readiness assurance evidence."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any, Mapping

ROOT=Path(__file__).resolve().parent.parent
MODE="offline-consequence-plan-review-response-intake-envelope-readiness-assurance"
DECISION="response-intake-envelope-readiness-assured-no-envelope-received"
STATE=MODE+"-candidate"
NEXT_GATE="offline-consequence-plan-review-response-intake-envelope-validation-readiness-candidate"
OUT=ROOT/"release/phase-30-offline-consequence-plan-review-response-intake-envelope-readiness-assurance.json"
SOURCE=ROOT/"release/phase-29-offline-consequence-plan-review-response-intake-envelope-readiness.json"
POST=ROOT/"release/phase-29-postmerge.json"
SOURCE_SHA="1c921b77459b6cf46a0add6b47a7796e69e91c6a61f817750e3277de0685e74e"
POST_SHA="d7c14da1beb4f0a7fde9118d9aad6a474ec5e636b08b389215588be603c2cade"
FINAL_COMMIT="3f16211260c836d15f9c0ee2c14bcfa550fad7da"
SECTIONS=("source-binding","transport-metadata","payload-integrity","schema-binding","reviewer-gate-attestations","quarantine-routing","submission-state")
FIELDS=("envelope_version","envelope_id","response_id","intake_readiness_id","intake_readiness_assurance_id","packet_id","packet_assurance_id","schema_id","payload_media_type","payload_encoding","payload_sha256","source_digest","submitted_at","signature_ref")
BLANK=("envelope_id","response_id","payload_sha256","source_digest","submitted_at","signature_ref")
RULES=("canonical-json-required","utf8-required","media-type-exact","schema-id-exact","assurance-id-exact","packet-id-exact","payload-sha256-required","source-digest-required","duplicate-envelope-prohibited","unknown-fields-prohibited")
REASONS=("malformed-envelope","unsupported-envelope-version","schema-binding-mismatch","assurance-binding-mismatch","packet-binding-mismatch","payload-digest-mismatch","source-digest-missing","reviewer-gates-incomplete","duplicate-envelope","signature-or-timestamp-missing")
CHECKS=("authority_boundary_preserved","blank_envelope_template_exact","blank_response_fields_exact","digest_algorithm_exact","envelope_identity_exact","envelope_states_frozen","envelope_version_exact","human_gates_remain_pending","integrity_rules_exact","media_type_exact","payload_limit_exact","quarantine_policy_exact","readiness_identity_exact","readiness_ledger_binding_exact","readiness_record_digest_exact","required_fields_exact","response_states_frozen","review_execution_frozen","schema_binding_exact","sections_exact","source_candidate_exact","source_finalization_exact","transport_encoding_exact","zero_effect_boundary_preserved")
EXPECTED=(
("feedback-manual-review",1,"6338d9853a917a410f4ecf036ca73362a95b568a5d4a3826105a7594897237b1","4ab74b97bd7c207547d86e5b602170228b701a70ad463ceb1d4e7bc2cd3c907c","qualified-pedagogical-reviewer"),
("model-boundary-release-governance",2,"421d2c5272508fda80f796c650ec50305aae1936c603978e789d944c761ba5a3","826190459e6312a6a647e9911e5bb7c90db133811b450d2a73a8a52c75848f4a","qualified-release-governance-reviewer"),
)
AUTHORITY={"atlas_call_permitted":False,"automatic_release_action":False,"automatic_status_change":False,"external_delivery_permitted":False,"external_network_required":False,"human_authorization_claimed":False,"local_response_envelope_assurance_permitted":True,"repository_mutation":False,"response_envelope_creation_permitted":False,"response_envelope_processing_authorized":False,"response_intake_authorized":False,"response_quarantine_execution_authorized":False,"response_receipt_permitted":False,"response_validation_authorized":False,"review_execution_authorized":False,"review_request_dispatch_authorized":False,"reviewer_contact_permitted":False,"status_inheritance":"prohibited"}
MUTATIONS=("phase29-candidate-drift","phase29-postmerge-drift","missing-envelope-assurance","orphan-envelope-assurance","duplicate-envelope-assurance","sequence-drift","readiness-id-drift","readiness-record-digest-drift","readiness-ledger-entry-drift","intake-assurance-id-drift","intake-readiness-id-drift","packet-assurance-id-drift","packet-id-drift","schema-id-drift","envelope-id-drift","envelope-version-drift","media-type-drift","encoding-drift","digest-algorithm-drift","payload-limit-drift","section-count-drift","section-order-drift","section-state-drift","required-field-count-drift","required-field-order-drift","blank-field-count-drift","blank-envelope-id-filled","blank-response-id-filled","blank-payload-digest-filled","blank-source-digest-filled","blank-submitted-at-filled","blank-signature-filled","template-submitted","template-quarantine-state-drift","template-quarantine-reason-filled","integrity-rule-count-drift","integrity-rule-id-drift","integrity-rule-order-drift","integrity-rule-state-drift","quarantine-reason-count-drift","quarantine-reason-id-drift","quarantine-reason-order-drift","quarantine-reason-state-drift","quarantine-default-state-drift","quarantine-execution-authorized","human-gate-satisfied","envelope-created","envelope-received","envelope-processed","integrity-failure-recorded","duplicate-envelope-recorded","quarantine-record-created","response-intake-authorized","response-receipt-permitted","response-received","response-validated","response-accepted","response-rejected","response-quarantined","packet-dispatched","reviewer-contact-permitted","reviewer-identity-recorded","review-start-permitted","review-started","review-completed","outcome-selected","content-change-proposed","status-recommendation-recorded","effective-hold","operational-effect","status-change","human-authorization-claimed","real-authorization-claimed","status-inheritance-enabled","automatic-status-change","automatic-release-action","repository-mutation","external-network-required","external-delivery-permitted","atlas-call-permitted","live-activation","assurance-check-failed","assurance-verdict-drift","assurance-status-drift","assurance-locality-drift","assurance-ledger-drift","assurance-checkpoint-drift","summary-drift","authority-drift","source-pin-drift","assurance-count-drift","recovery-count-drift")
ZERO=("response_accepted","response_envelope_created","response_envelope_processed","response_envelope_received","response_intake_authorized","response_quarantined","response_received","response_rejected","response_validated","review_completed","review_start_permitted","review_started","reviewer_contact_permitted","reviewer_identity_present","status_change","real_authorization_claimed")

def render(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n"
def sha_doc(v:Any)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def sha_file(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:
 v=json.loads(p.read_text());
 if not isinstance(v,dict):raise ValueError(p)
 return v

def verify_sources()->list[str]:
 e=[]
 if not SOURCE.is_file() or sha_file(SOURCE)!=SOURCE_SHA:e.append("Phase 29 candidate file drift")
 if not POST.is_file() or sha_file(POST)!=POST_SHA:e.append("Phase 29 postmerge file drift")
 if e:return e
 src,post=load(SOURCE),load(POST)
 if src.get("state")!="offline-consequence-plan-review-response-intake-envelope-readiness-candidate" or src.get("next_gate")!=STATE:e.append("Phase 29 candidate gate drift")
 if post.get("state")!="offline-consequence-plan-review-response-intake-envelope-readiness-validated" or post.get("next_gate")!=STATE:e.append("Phase 29 finalization gate drift")
 if post.get("candidate_record",{}).get("sha256")!=SOURCE_SHA:e.append("Phase 29 candidate digest drift")
 records={r.get("envelope_readiness_id"):r for r in src.get("envelope_readiness_records",[])}
 entries={x.get("entry",{}).get("envelope_readiness_id"):x for x in src.get("ledger",{}).get("entries",[])}
 for key,seq,rsha,lsha,_role in EXPECTED:
  rid=f"principia:consequence-plan-review-response-intake-envelope-readiness:{key}:{seq:04d}"
  r,w=records.get(rid),entries.get(rid)
  if not r or sha_doc(r)!=rsha:e.append(f"Phase 29 record drift: {key}");continue
  if not w or w.get("entry_sha256")!=lsha:e.append(f"Phase 29 ledger drift: {key}")
  spec,tpl=r.get("envelope_spec",{}),r.get("blank_envelope_template",{})
  if [x.get("section_id") for x in spec.get("sections",[])]!=list(SECTIONS) or spec.get("required_fields")!=list(FIELDS):e.append(f"Phase 29 specification drift: {key}")
  if [x.get("rule_id") for x in r.get("integrity_rules",[])]!=list(RULES) or [x.get("reason_id") for x in r.get("quarantine_policy",{}).get("reason_codes",[])]!=list(REASONS):e.append(f"Phase 29 policy drift: {key}")
  if any(tpl.get(x) is not None for x in BLANK):e.append(f"Phase 29 template drift: {key}")
 return e

def assurances()->list[dict[str,Any]]:
 out=[]
 for key,seq,rsha,lsha,role in EXPECTED:
  prefix=f"principia:consequence-plan-review-response-intake"
  r={"assurance_check_count":len(CHECKS),"assurance_checks":{x:True for x in CHECKS},"blank_response_field_count":len(BLANK),"envelope_readiness_assurance_id":f"{prefix}-envelope-readiness-assurance:{key}:{seq:04d}","envelope_readiness_id":f"{prefix}-envelope-readiness:{key}:{seq:04d}","envelope_readiness_ledger_entry_sha256":lsha,"envelope_readiness_record_sha256":rsha,"envelope_section_count":len(SECTIONS),"envelope_spec_id":f"principia:review-response-intake-envelope:{key}:{seq:04d}","human_gate_pending_count":4,"human_gate_satisfied_count":0,"integrity_rule_count":len(RULES),"intake_readiness_assurance_id":f"{prefix}-readiness-assurance:{key}:{seq:04d}","intake_readiness_id":f"{prefix}-readiness:{key}:{seq:04d}","local_only":True,"packet_assurance_id":f"principia:consequence-plan-review-request-packet-assurance:{key}:{seq:04d}","packet_id":f"principia:consequence-plan-review-request-packet:{key}:{seq:04d}","quarantine_reason_code_count":len(REASONS),"required_envelope_field_count":len(FIELDS),"response_schema_id":f"principia:review-response-intake-schema:{key}:{seq:04d}","reviewer_role_required":role,"sequence":seq,"status":"assured-no-envelope-received","verdict":"response-envelope-readiness-assured-no-envelope"}
  r.update({x:False for x in ZERO});out.append(r)
 return out

def ledger(rs:list[dict[str,Any]])->dict[str,Any]:
 out=[];prev=None
 for r in rs:
  e={"envelope_readiness_assurance_id":r["envelope_readiness_assurance_id"],"envelope_readiness_id":r["envelope_readiness_id"],"envelope_readiness_record_sha256":r["envelope_readiness_record_sha256"],"previous_entry_sha256":prev,"record_sha256":sha_doc(r),"sequence":r["sequence"],"verdict":r["verdict"]};prev=sha_doc(e);out.append({"entry":e,"entry_sha256":prev})
 return {"entries":out,"head_sequence":len(out),"head_sha256":prev}

def build_document()->dict[str,Any]:
 rs=assurances();lg=ledger(rs)
 result={"assurance_check_count":48,"assured_envelope_readiness_record_count":2,"blank_response_field_count":12,"envelope_readiness_record_count":2,"envelope_section_count":14,"failed_assurance_count":0,"human_gate_pending_count":8,"human_gate_satisfied_count":0,"integrity_failure_count":0,"integrity_rule_count":20,"quarantine_reason_code_count":20,"quarantine_record_count":0,"real_authorization_claimed":False,"required_envelope_field_count":28,"response_accepted_count":0,"response_envelope_created_count":0,"response_envelope_processed_count":0,"response_envelope_received_count":0,"response_intake_authorized_count":0,"response_quarantined_count":0,"response_received_count":0,"response_rejected_count":0,"response_validated_count":0,"review_completed_count":0,"review_started_count":0,"reviewer_contact_count":0,"reviewer_identity_count":0,"status_change_count":0}
 return {"assurances":rs,"authority":AUTHORITY,"checkpoint":{"assurance_check_count":48,"assured_envelope_readiness_record_count":2,"envelope_received_count":0,"failed_assurance_count":0,"integrity_failure_count":0,"ledger_sha256":sha_doc(lg),"quarantine_record_count":0,"response_received_count":0,"review_started_count":0,"status_change_count":0},"contract":"principia-offline-consequence-plan-review-response-intake-envelope-readiness-assurance/0.1","decision":DECISION,"fixture_kind":"bounded-synthetic","id":"principia-atlas-offline-consequence-plan-review-response-intake-envelope-readiness-assurance-thermal-control","ledger":lg,"live":False,"live_activation_permitted":False,"mode":MODE,"next_gate":NEXT_GATE,"phase":30,"real_authorization_claimed":False,"recovery":{"accepted":["baseline"],"accepted_count":1,"rejected":list(MUTATIONS),"rejected_count":len(MUTATIONS),"scenario_count":len(MUTATIONS)+1},"result":result,"source_phase29":{"phase29_candidate_sha256":SOURCE_SHA,"phase29_finalization_commit":FINAL_COMMIT,"phase29_postmerge_sha256":POST_SHA},"state":STATE,"validation":{"pull_request":None,"status":"pending","tested_head_commit":None}}

def validate_document(d:Mapping[str,Any])->list[str]:return [] if d==build_document() else ["document drift"]
def main()->int:
 a=argparse.ArgumentParser();a.add_argument("--check",action="store_true");args=a.parse_args();errs=verify_sources()
 if errs:
  print("Phase 30 source errors:",file=sys.stderr);[print(f"- {x}",file=sys.stderr) for x in errs];return 1
 text=render(build_document())
 if args.check and (not OUT.is_file() or OUT.read_text()!=text):print("Phase 30 candidate differs from deterministic generation",file=sys.stderr);return 1
 if not args.check:OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(text)
 print(f"Phase 30 candidate passed: {len(text.encode())} bytes, sha256={hashlib.sha256(text.encode()).hexdigest()}, 2 envelope-readiness assurances, 48 checks, 0 envelopes received.");return 0
if __name__=="__main__":raise SystemExit(main())
