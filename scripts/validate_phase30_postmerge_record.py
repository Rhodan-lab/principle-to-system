#!/usr/bin/env python3
"""Validate finalized Phase 30 envelope-readiness assurance provenance."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from typing import Any, Mapping
ROOT=Path(__file__).resolve().parent.parent
STATE=ROOT/"PROJECT_STATE.md"
CANDIDATE=ROOT/"release/phase-30-offline-consequence-plan-review-response-intake-envelope-readiness-assurance.json"
FINAL=ROOT/"release/phase-30-postmerge.json"
REPORT=ROOT/"reports/phase-30-offline-consequence-plan-review-response-intake-envelope-readiness-assurance.md"
WORKFLOW=ROOT/".github/workflows/validate-phase-30-offline-consequence-plan-review-response-intake-envelope-readiness-assurance.yml"
HEAD="3b6e0531572589e43fa3a57dd20d8062e6b7f247";MERGE="74582568efa727617cc83d9dd93ba81f0692bdc7";SHA="f3a232a6895b153020a2ce49bf5a4cbc10d7adabb5b9780da4edfe4d1f764ce5"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:
 v=json.loads(p.read_text());
 if not isinstance(v,dict):raise ValueError(p)
 return v
def main()->int:
 errors=[]
 for p in (STATE,CANDIDATE,FINAL,REPORT,WORKFLOW):
  if not p.is_file():errors.append(f"missing {p.relative_to(ROOT)}")
 if errors:return fail(errors)
 if sha(CANDIDATE)!=SHA:errors.append("candidate digest")
 f=load(FINAL)
 expected={"contract":"principia-offline-consequence-plan-review-response-intake-envelope-readiness-assurance-finalization/0.1","phase":30,"state":"offline-consequence-plan-review-response-intake-envelope-readiness-assurance-validated","mode":"offline-consequence-plan-review-response-intake-envelope-readiness-assurance","fixture_kind":"bounded-synthetic","decision":"response-intake-envelope-readiness-assured-no-envelope-received","live":False,"next_gate":"offline-consequence-plan-review-response-intake-envelope-validation-readiness-candidate","live_activation_permitted":False,"real_authorization_claimed":False}
 for k,v in expected.items():
  if f.get(k)!=v:errors.append(f"{k} drift")
 if f.get("candidate_record")!={"path":CANDIDATE.relative_to(ROOT).as_posix(),"sha256":SHA}:errors.append("candidate pin")
 if f.get("principia")!={"repository":"Rhodan-lab/principle-to-system","pull_request":51,"candidate_head_commit":HEAD,"merge_commit":MERGE}:errors.append("provenance")
 if f.get("validation")!={"applicable_workflows":24,"candidate_head_commit":HEAD,"status":"success"}:errors.append("validation provenance")
 r=f.get("result",{})
 for k,v in {"assurance_check_count":48,"assured_envelope_readiness_record_count":2,"failed_assurance_count":0,"envelope_section_count":14,"required_envelope_field_count":28,"blank_response_field_count":12,"integrity_rule_count":20,"quarantine_reason_code_count":20,"human_gate_pending_count":8,"human_gate_satisfied_count":0,"response_envelope_created_count":0,"response_envelope_received_count":0,"response_envelope_processed_count":0,"response_received_count":0,"response_validated_count":0,"review_started_count":0,"status_change_count":0,"real_authorization_claimed":False}.items():
  if r.get(k)!=v:errors.append(f"result {k}")
 a=f.get("authority")
 if not isinstance(a,Mapping):errors.append("authority")
 else:
  for k in ("atlas_call_permitted","automatic_release_action","automatic_status_change","external_delivery_permitted","external_network_required","human_authorization_claimed","repository_mutation","response_envelope_creation_permitted","response_envelope_processing_authorized","response_intake_authorized","response_quarantine_execution_authorized","response_receipt_permitted","response_validation_authorized","review_execution_authorized","review_request_dispatch_authorized","reviewer_contact_permitted"):
   if a.get(k) is not False:errors.append(f"authority {k}")
  if a.get("local_response_envelope_assurance_permitted") is not True or a.get("status_inheritance")!="prohibited":errors.append("authority boundary")
 state=STATE.read_text()
 for m in ("**Phase 30 — Offline Consequence-Plan Review-Response Intake Envelope Readiness Assurance merged and validated through PR #51.**","Phase 30 state: **offline-consequence-plan-review-response-intake-envelope-readiness-assurance-validated**","| 30 | Offline consequence-plan review-response intake envelope readiness assurance | Merged and validated through PR #51 |",f"Phase 30 exact candidate validation passed at `{HEAD}`",f"PR #51 was merged into `main` at commit `{MERGE}`","release/phase-30-postmerge.json","Historical Phase 30 candidate marker: `exact-head validation pending`","offline-consequence-plan-review-response-intake-envelope-validation-readiness-candidate","response-intake-envelope-readiness-assured-no-envelope-received","response-envelope-readiness-assured-no-envelope","assured_envelope_readiness_record_count: 2","assurance_check_count: 48","response_envelope_received_count: 0","human_gate_pending_count: 8","real_authorization_claimed: false","Atlas remains unchanged by Principia Phase 30.","live: false"):
  if m not in state:errors.append(f"state marker {m}")
 report=REPORT.read_text()
 for m in ("# Phase 30 — Offline Consequence-Plan Review-Response Intake Envelope Readiness Assurance",f"> Exact tested head: `{HEAD}`",f"> Merge commit: `{MERGE}`","> Final state: `offline-consequence-plan-review-response-intake-envelope-readiness-assurance-validated`","release/phase-30-postmerge.json","2 assured envelope readiness records","48 passing invariant checks","8 pending human gates","response-intake-envelope-readiness-assured-no-envelope-received","> Live: `false`"):
  if m not in report:errors.append(f"report marker {m}")
 workflow=WORKFLOW.read_text()
 for m in ("agent/finalize-phase-30-record","scripts/validate_phase30_postmerge_record.py","release/phase-30-postmerge.json","contents: read"):
  if m not in workflow:errors.append(f"workflow marker {m}")
 for x in ("contents: write","git push","git commit","pull_request_target","repository: Rhodan-lab/Atlas","curl ","wget "):
  if x in workflow:errors.append(f"forbidden {x}")
 if errors:return fail(sorted(set(errors)))
 print("Phase 30 post-merge record passed: exact candidate and PR pinned, two envelope-readiness records assured, 48 checks passing, zero envelopes received.");return 0
def fail(errors:list[str])->int:
 print("Phase 30 post-merge record errors:",file=sys.stderr);[print(f"- {x}",file=sys.stderr) for x in errors];return 1
if __name__=="__main__":raise SystemExit(main())
