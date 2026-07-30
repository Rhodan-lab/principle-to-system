#!/usr/bin/env python3
"""Independently validate Phase 37 authorization-decision readiness evidence."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent.parent
CANDIDATE=ROOT/"release/phase-37-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness.json"
SOURCE=ROOT/"release/phase-36-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance.json"
POST=ROOT/"release/phase-36-postmerge.json"
CANDIDATE_SHA="724a12243300d6c91cf60fef046f5ae40089c98867bba62bdd524e3684aec2ae"
SOURCE_SHA="c90abcedeffcc66ff1d1e1d615e03cc5e002a76177d3ab8a0754543c4ad1677e"
POST_SHA="79b689ad032d29c21e620525cdea665545f0ee9e2e4f633b708a78240b252f52"
FINALIZATION="31a66a144fe605d864b67f89e585b823ff2ae72c"
MODE="offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness"
STATE=MODE+"-candidate"
NEXT=MODE+"-assurance-candidate"
CONTRACT="principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness/0.1"
FALSE_FIELDS=(
 "decision_option_selected","conflict_declaration_evaluated","approval_received","approval_evidence_recorded",
 "decision_candidate_created","decision_record_created","authorization_decision_recorded","authorization_granted",
 "authorization_revoked","authorization_expired","authorization_token_issued","execution_authorization_present",
 "execution_ticket_issued","execution_run_created","execution_started","execution_completed",
 "validation_result_recorded","disposition_selected","response_envelope_created","response_envelope_received",
 "response_envelope_processed","response_received","response_validated","response_accepted","response_rejected",
 "response_quarantined","reviewer_identity_present","reviewer_contact_permitted","review_start_permitted",
 "review_started","review_completed","status_change","real_authorization_claimed",
)
BLANK_FIELDS=(
 "decision_id","authorization_candidate_id","decision_option","primary_decider_identity","primary_decider_role",
 "secondary_decider_identity","secondary_decider_role","decided_at","rationale_code","rationale_text_ref",
 "source_assurance_digest","approval_evidence_digest","authorization_token_id","decision_signature_ref",
 "conflict_declaration_ref","expires_at",
)

def sha_file(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(value:Any)->bytes:return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(value:Any)->str:return hashlib.sha256(canonical(value)).hexdigest()
def load(path:Path)->dict[str,Any]:
 value=json.loads(path.read_text())
 if not isinstance(value,dict):raise ValueError(path)
 return value

def validate_document(doc:dict[str,Any])->list[str]:
 errors=[]
 if doc.get("phase")!=37 or doc.get("contract")!=CONTRACT:errors.append("phase or contract drift")
 if doc.get("mode")!=MODE or doc.get("state")!=STATE or doc.get("next_gate")!=NEXT:errors.append("lifecycle drift")
 if doc.get("decision")!="response-intake-envelope-validation-execution-authorization-decision-readiness-recorded-no-decision-candidate-created":errors.append("decision drift")
 if doc.get("live") is not False or doc.get("live_activation_permitted") is not False or doc.get("real_authorization_claimed") is not False:errors.append("activation drift")
 if doc.get("source_phase36")!={"phase36_candidate_sha256":SOURCE_SHA,"phase36_postmerge_sha256":POST_SHA,"phase36_finalization_commit":FINALIZATION}:errors.append("source pins drift")
 policy=doc.get("decision_policy",{})
 policy_copy=dict(policy); embedded=policy_copy.pop("decision_policy_sha256",None)
 if embedded!=digest(policy_copy):errors.append("policy digest drift")
 if policy.get("decision_policy_id")!="principia-envelope-validation-execution-authorization-decision-policy" or policy.get("decision_policy_version")!="0.1":errors.append("policy identity drift")
 if policy.get("mode")!="offline-authorization-decision-preflight-only" or policy.get("input_state")!="no-envelope-no-authorization-no-decision":errors.append("policy mode drift")
 stages=policy.get("decision_stages",[]); reqs=policy.get("decision_requirements",[]); options=policy.get("decision_options",[])
 if len(stages)!=12 or any(x.get("sequence")!=i+1 or x.get("state")!="defined-not-active" for i,x in enumerate(stages)):errors.append("stage drift")
 if len(reqs)!=26 or any(x.get("sequence")!=i+1 or x.get("state")!="required-not-evaluated" for i,x in enumerate(reqs)):errors.append("requirement drift")
 if [x.get("option") for x in options]!=["grant","deny","defer"] or any(x.get("state")!="defined-not-selectable" for x in options):errors.append("option drift")
 scope=policy.get("decision_scope",{})
 if scope.get("operation")!="consider-one-bound-validation-execution-authorization-decision":errors.append("scope operation drift")
 for key in ("profile_bound","assurance_bound","dual_control_required","conflict_declaration_required"):
  if scope.get(key) is not True:errors.append(f"scope binding drift: {key}")
 for key in ("external_network","atlas_access","repository_write","token_issue_enabled","execution_enabled","result_recording_enabled","disposition_selection_enabled","status_change_enabled"):
  if scope.get(key) is not False:errors.append(f"forbidden scope enabled: {key}")
 profiles=doc.get("decision_profiles",[]); records=doc.get("decision_readiness_records",[]); entries=doc.get("ledger",{}).get("entries",[])
 if len(profiles)!=2:errors.append("profile count drift")
 if len(records)!=2:errors.append("record count drift")
 if len(entries)!=2:errors.append("ledger count drift")
 source=load(SOURCE)
 source_assurances=source.get("assurances",[]); source_entries=source.get("ledger",{}).get("entries",[])
 for i,record in enumerate(records):
  n=i+1
  if record.get("sequence")!=n:errors.append(f"record {n} sequence drift")
  if i>=len(source_assurances):continue
  s=source_assurances[i]
  if record.get("authorization_readiness_assurance_id")!=s.get("authorization_readiness_assurance_id"):errors.append(f"record {n} source assurance drift")
  if record.get("authorization_readiness_assurance_record_sha256")!=digest(s):errors.append(f"record {n} source digest drift")
  if i<len(source_entries) and record.get("authorization_readiness_assurance_ledger_entry_sha256")!=source_entries[i].get("entry_sha256"):errors.append(f"record {n} source ledger drift")
  if record.get("decision_stage_count")!=12 or record.get("decision_requirement_count")!=26 or record.get("decision_requirement_evaluated_count")!=0:errors.append(f"record {n} readiness count drift")
  if record.get("decision_option_count")!=3 or record.get("required_decision_role_count")!=2 or record.get("dual_control_required") is not True:errors.append(f"record {n} option/role drift")
  if record.get("human_gate_pending_count")!=4 or record.get("human_gate_satisfied_count")!=0:errors.append(f"record {n} gate drift")
  checks=record.get("readiness_checks",{})
  if record.get("readiness_check_count")!=58 or len(checks)!=58 or not all(checks.values()):errors.append(f"record {n} check drift")
  blank=record.get("blank_decision_record",{})
  if record.get("blank_decision_record_field_count")!=16 or any(blank.get(k) is not None for k in BLANK_FIELDS) or blank.get("issued") is not False or blank.get("recorded") is not False:errors.append(f"record {n} blank record drift")
  if any(record.get(k) is not False for k in FALSE_FIELDS):errors.append(f"record {n} frozen state drift")
  if record.get("local_only") is not True or record.get("status")!="authorization-decision-readiness-recorded-no-decision-candidate-created" or record.get("verdict")!="response-envelope-validation-execution-authorization-decision-controls-ready-no-decision":errors.append(f"record {n} status drift")
  if i<len(entries):
   item=entries[i]
   if item.get("entry",{}).get("record_sha256")!=digest(record) or item.get("entry_sha256")!=digest(item.get("entry",{})):errors.append(f"record {n} ledger binding drift")
 if len(entries)==2:
  if entries[0]["entry"].get("previous_entry_sha256") is not None or entries[1]["entry"].get("previous_entry_sha256")!=entries[0].get("entry_sha256"):errors.append("ledger chain drift")
  if doc.get("ledger",{}).get("head_sha256")!=entries[1].get("entry_sha256"):errors.append("ledger head drift")
 result=doc.get("result",{})
 expected_nonzero={"decision_policy_count":1,"decision_profile_count":2,"decision_readiness_record_count":2,"decision_stage_count":24,"decision_requirement_count":52,"decision_option_count":3,"required_decision_role_count":4,"dual_control_profile_count":2,"conflict_declaration_required_count":2,"blank_decision_record_count":2,"blank_decision_record_field_count":32,"readiness_check_count":116,"human_gate_pending_count":8}
 for key,value in expected_nonzero.items():
  if result.get(key)!=value:errors.append(f"result count drift: {key}")
 for key,value in result.items():
  if key.endswith("_count") and key not in expected_nonzero and value!=0:errors.append(f"operational count nonzero: {key}")
 authority=doc.get("authority",{})
 if authority.get("local_response_envelope_validation_execution_authorization_decision_readiness_permitted") is not True:errors.append("local authority missing")
 for key,value in authority.items():
  if key in ("local_response_envelope_validation_execution_authorization_decision_readiness_permitted","status_inheritance"):continue
  if value is not False:errors.append(f"forbidden authority enabled: {key}")
 if authority.get("status_inheritance")!="prohibited":errors.append("status inheritance drift")
 recovery=doc.get("recovery",{})
 if recovery.get("accepted")!=["baseline"] or recovery.get("accepted_count")!=1 or recovery.get("rejected_count")!=137 or recovery.get("scenario_count")!=138 or len(recovery.get("rejected",[]))!=137:errors.append("recovery drift")
 checkpoint=doc.get("checkpoint",{})
 if checkpoint.get("decision_readiness_record_count")!=2 or checkpoint.get("readiness_check_count")!=116 or checkpoint.get("failed_readiness_check_count")!=0 or checkpoint.get("authorization_decision_candidate_created_count")!=0 or checkpoint.get("authorization_decision_recorded_count")!=0 or checkpoint.get("authorization_granted_count")!=0 or checkpoint.get("authorization_token_issued_count")!=0 or checkpoint.get("response_envelope_received_count")!=0 or checkpoint.get("execution_run_count")!=0 or checkpoint.get("status_change_count")!=0:errors.append("checkpoint drift")
 return errors

def validate()->list[str]:
 errors=[]
 for path,label in ((CANDIDATE,"candidate"),(SOURCE,"Phase 36 candidate"),(POST,"Phase 36 postmerge")):
  if not path.is_file():errors.append(f"Missing {label}: {path}")
 if errors:return errors
 if sha_file(CANDIDATE)!=CANDIDATE_SHA:errors.append("Phase 37 candidate digest drift")
 if sha_file(SOURCE)!=SOURCE_SHA:errors.append("Phase 36 candidate digest drift")
 if sha_file(POST)!=POST_SHA:errors.append("Phase 36 postmerge digest drift")
 post=load(POST)
 if post.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-validated" or post.get("next_gate")!=MODE+"-candidate":errors.append("Phase 36 final gate drift")
 errors.extend(validate_document(load(CANDIDATE)))
 return errors

def main()->int:
 errors=validate()
 if errors:
  print("Phase 37 authorization-decision readiness errors:",file=sys.stderr)
  for e in errors:print(f"- {e}",file=sys.stderr)
  return 1
 print(f"Phase 37 authorization-decision readiness passed: sha256={CANDIDATE_SHA}, records=2, checks=116, scenarios=138.")
 return 0
if __name__=="__main__":raise SystemExit(main())
