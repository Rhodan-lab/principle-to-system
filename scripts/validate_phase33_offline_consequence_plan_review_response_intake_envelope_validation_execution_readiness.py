#!/usr/bin/env python3
"""Validate deterministic Phase 33 envelope-validation execution readiness."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from typing import Any
import generate_phase33_offline_consequence_plan_review_response_intake_envelope_validation_execution_readiness as p

ROOT=Path(__file__).resolve().parent.parent
RECORD=ROOT/"release/phase-33-offline-consequence-plan-review-response-intake-envelope-validation-execution-readiness.json"

def sha_doc(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def validate()->list[str]:
    errors=p.verify_sources()
    if not RECORD.is_file(): return errors+["Phase 33 candidate missing"]
    try: d=json.loads(RECORD.read_text())
    except Exception as exc: return errors+[f"Phase 33 candidate unreadable: {exc}"]
    if d!=p.build_document(): errors.append("Phase 33 deterministic document drift")
    if d.get("phase")!=33 or d.get("mode")!=p.MODE or d.get("state")!=p.STATE or d.get("decision")!=p.DECISION or d.get("next_gate")!=p.NEXT_GATE: errors.append("Phase 33 identity or gate drift")
    if d.get("live") is not False or d.get("live_activation_permitted") is not False or d.get("real_authorization_claimed") is not False: errors.append("Phase 33 activation drift")
    if d.get("authority")!=p.AUTHORITY: errors.append("Phase 33 authority drift")

    bp=d.get("execution_blueprint",{})
    if sha_doc(bp)!=sha_doc(p.blueprint()): errors.append("Phase 33 blueprint drift")
    if [x.get("stage_id") for x in bp.get("stages",[])]!=p.EXECUTION_STAGES or any(x.get("state")!="defined-not-active" for x in bp.get("stages",[])): errors.append("Phase 33 stage drift")
    if [x.get("precondition_id") for x in bp.get("preconditions",[])]!=p.PRECONDITIONS or any(x.get("state")!="required-not-evaluated" for x in bp.get("preconditions",[])): errors.append("Phase 33 precondition drift")
    if [x.get("control_id") for x in bp.get("required_validation_controls",[])]!=p.VALIDATION_CONTROLS: errors.append("Phase 33 validation-control drift")
    if [x.get("disposition_id") for x in bp.get("dispositions",[])]!=p.DISPOSITIONS or any(x.get("state")!="defined-not-active" for x in bp.get("dispositions",[])): errors.append("Phase 33 disposition drift")
    if bp.get("resource_limits")!=p.RESOURCE_LIMITS or bp.get("blank_ticket_fields")!=p.BLANK_TICKET_FIELDS: errors.append("Phase 33 resource or ticket blueprint drift")
    if bp.get("deterministic_engine")!={"deterministic":True,"engine_id":"principia-envelope-validator","engine_version":"0.1"}: errors.append("Phase 33 engine drift")

    profiles=d.get("execution_profiles",[])
    records=d.get("execution_readiness_records",[])
    if len(profiles)!=2 or len(records)!=2: return errors+["Phase 33 profile or record count drift"]
    bp_sha=sha_doc(bp)
    for i,(profile,record) in enumerate(zip(profiles,records),1):
        if profile.get("sequence")!=i or profile.get("blueprint_sha256")!=bp_sha: errors.append(f"Phase 33 profile {i} binding drift")
        if record.get("sequence")!=i or record.get("blueprint_sha256")!=bp_sha or record.get("execution_profile_id")!=profile.get("execution_profile_id"): errors.append(f"Phase 33 record {i} binding drift")
        if record.get("status")!="execution-readiness-recorded-no-envelope-received" or record.get("verdict")!="response-envelope-validation-execution-controls-ready-no-envelope" or record.get("local_only") is not True: errors.append(f"Phase 33 record {i} status drift")
        if record.get("human_gate_pending_count")!=4 or record.get("human_gate_satisfied_count")!=0: errors.append(f"Phase 33 record {i} human-gate drift")
        if any(record.get(x) is not False for x in p.ZERO_FIELDS): errors.append(f"Phase 33 record {i} frozen-state drift")
        ticket=record.get("blank_execution_ticket",{})
        if ticket.get("issued") is not False or any(ticket.get(x) is not None for x in p.BLANK_TICKET_FIELDS): errors.append(f"Phase 33 record {i} ticket contamination")

    entries=d.get("ledger",{}).get("entries",[]); prev=None
    if len(entries)!=2: errors.append("Phase 33 ledger count drift")
    for i,w in enumerate(entries,1):
        e=w.get("entry",{})
        if e.get("previous_entry_sha256")!=prev or e.get("sequence")!=i or e.get("record_sha256")!=sha_doc(records[i-1]): errors.append(f"Phase 33 ledger binding drift at {i}")
        prev=sha_doc(e)
        if w.get("entry_sha256")!=prev: errors.append(f"Phase 33 ledger digest drift at {i}")
    if d.get("ledger",{}).get("head_sha256")!=prev or d.get("checkpoint",{}).get("ledger_sha256")!=sha_doc(d.get("ledger",{})): errors.append("Phase 33 ledger checkpoint drift")
    if d.get("result")!=p.build_document().get("result"): errors.append("Phase 33 result drift")
    if d.get("recovery",{}).get("rejected")!=p.MUTATIONS or d.get("recovery",{}).get("scenario_count")!=len(p.MUTATIONS)+1: errors.append("Phase 33 recovery drift")
    return errors

def main()->int:
    errors=validate()
    if errors:
        print("Phase 33 validation errors:",file=sys.stderr)
        for x in errors: print(f"- {x}",file=sys.stderr)
        return 1
    print(f"Phase 33 validation passed: sha256={hashlib.sha256(RECORD.read_bytes()).hexdigest()}, 2 execution-readiness records, 18 stages, 40 preconditions, 0 executions.")
    return 0
if __name__=="__main__": raise SystemExit(main())
