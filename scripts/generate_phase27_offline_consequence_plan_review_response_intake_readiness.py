#!/usr/bin/env python3
"""Generate deterministic Phase 27 response-intake readiness evidence."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any, Mapping
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'release/phase-27-offline-consequence-plan-review-response-intake-readiness.json'
MODE='offline-consequence-plan-review-response-intake-readiness'
DECISION='response-intake-readiness-recorded-no-response-received'
STATE=MODE+'-candidate'
NEXT_GATE=MODE+'-assurance-candidate'
SOURCE_FILES={
 ROOT/'release/phase-26-postmerge.json':'3d34c6165e082ed16cf50e00b9d784095625338703e2c3713c72a7a30eccad1c',
 ROOT/'release/phase-26-offline-consequence-plan-review-request-packet-assurance.json':'cdf82f5e4792d43e21b3242fa4114a4063bab9849abb68be25abb44c3a51b22c',
 ROOT/'integration/principia-atlas/pilot/thermal-control.consequence-plan-review-request-packet-assurance-report.v01.json':'1b480d1309c55d87b28aa8eaf347aaa34fb446e53d1c51474c2bc0a1ddc6beb9',
 ROOT/'integration/principia-atlas/pilot/thermal-control.consequence-plan-review-request-packet-assurance-ledger.v01.json':'68dcf4460bdb012ef2edc73d7699968d405d48cd4d6fd7601278989a0df727c1',
 ROOT/'integration/principia-atlas/pilot/thermal-control.consequence-plan-review-request-packet-assurance-checkpoint.v01.json':'f0c9d531206a7fb5ec5b383c7834d4a0df949b4b3fd34122eb7e4a66abddc5de',
 ROOT/'integration/principia-atlas/pilot/thermal-control.consequence-plan-review-request-packet-assurance-recovery.v01.json':'0301d135c6a467afbe57d7a89a354559611f3446eb3fd1bf5abaa257e9d40092',
}
SOURCE={
 'phase26_postmerge_sha256':'3d34c6165e082ed16cf50e00b9d784095625338703e2c3713c72a7a30eccad1c',
 'phase26_candidate_sha256':'cdf82f5e4792d43e21b3242fa4114a4063bab9849abb68be25abb44c3a51b22c',
 'assurance_report_sha256':'1b480d1309c55d87b28aa8eaf347aaa34fb446e53d1c51474c2bc0a1ddc6beb9',
 'assurance_ledger_sha256':'68dcf4460bdb012ef2edc73d7699968d405d48cd4d6fd7601278989a0df727c1',
 'assurance_checkpoint_sha256':'f0c9d531206a7fb5ec5b383c7834d4a0df949b4b3fd34122eb7e4a66abddc5de',
 'assurance_recovery_sha256':'0301d135c6a467afbe57d7a89a354559611f3446eb3fd1bf5abaa257e9d40092',
 'phase26_finalization_commit':'38bd86f9bbf81c7fcd865da51f17987d26c8e84f',
}
AUTHORITY={
 'atlas_call_permitted':False,'automatic_release_action':False,'automatic_status_change':False,
 'external_delivery_permitted':False,'external_network_required':False,'human_authorization_claimed':False,
 'local_response_intake_readiness_permitted':True,'repository_mutation':False,
 'response_intake_authorized':False,'response_receipt_permitted':False,'response_validation_authorized':False,
 'review_execution_authorized':False,'review_request_dispatch_authorized':False,'reviewer_contact_permitted':False,
 'status_inheritance':'prohibited',
}
PACKETS=(
 ('feedback-manual-review','principia:consequence-plan-review-request-packet-assurance:feedback-manual-review:0001','1f92f4ba61d324907b5fbfaa6ee98ed01868d96c0dc00f9d84dfaeb7ff47ea5d','3284030ad30ddbb66c42094cbc27f72a31817cbd7e466d48a82ea9b0c6f06b3c','principia:consequence-plan-review-request-packet:feedback-manual-review:0001','qualified-pedagogical-reviewer',('conceptual-boundary','evidence-sufficiency','unresolved-pedagogical-risk')),
 ('model-boundary-release-governance','principia:consequence-plan-review-request-packet-assurance:model-boundary-release-governance:0002','6fc24790bf3ee693600667c8260c97352b1ba845b87696597d1a7595e41254a6','da7e9e5d354db9907de15207a8702e84ed257f1d1b7f29da9f31aed912d960b7','principia:consequence-plan-review-request-packet:model-boundary-release-governance:0002','qualified-release-governance-reviewer',('governance-evidence-sufficiency','model-boundary-risk','missing-prerequisite')),
)
SECTIONS=('source-provenance','reviewer-identity-and-eligibility','human-gate-attestations','question-responses','review-observations','submission-envelope')
FIELDS=('schema_version','response_id','packet_id','packet_assurance_id','source_digest','reviewer_identity','reviewer_role','competence_attestation','conflict_declaration','authorization_to_start','question_responses','review_observations','review_recommendation','submitted_at','signature_ref')
MUTATIONS=(
 'phase26-source-drift','missing-record','orphan-record','duplicate-record','sequence-drift','assurance-id-drift','assurance-digest-drift','assurance-ledger-drift','packet-id-drift','schema-id-drift','schema-version-drift','schema-format-drift','schema-encoding-drift','section-count-drift','section-order-drift','section-state-drift','field-count-drift','field-order-drift','question-count-drift','question-id-drift','question-filled','question-accepted','template-submitted','response-id-recorded','source-digest-recorded','submitted-at-recorded','signature-recorded','reviewer-identity-recorded','reviewer-role-recorded','competence-recorded','conflict-recorded','authorization-recorded','observation-recorded','recommendation-recorded','human-gate-satisfied','intake-authorized','receipt-permitted','response-received','response-validated','response-accepted','response-rejected','response-quarantined','packet-dispatched','reviewer-contact-permitted','external-delivery-permitted','review-start-permitted','review-started','review-completed','outcome-selected','content-change-proposed','status-recommendation-recorded','effective-hold','operational-effect','status-change','human-authorization-claimed','real-authorization-claimed','status-inheritance','automatic-status-change','automatic-release-action','repository-mutation','external-network-required','atlas-call-permitted','live-activation','ledger-drift','checkpoint-drift','summary-drift','authority-drift','source-pin-drift','template-shape-drift','schema-shape-drift','question-sequence-drift','record-verdict-drift','record-status-drift','record-locality-drift','record-count-drift','recovery-count-drift'
)
def render(v:Any)->str:return json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n'
def sha_doc(v:Any)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def sha_file(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def verify_sources()->list[str]:
 return [f'source drift: {p.relative_to(ROOT)}' for p,s in SOURCE_FILES.items() if not p.is_file() or sha_file(p)!=s]
def template(qs:tuple[str,...])->dict[str,Any]:
 return {'authorization_to_start':None,'competence_attestation':None,'conflict_declaration':None,'packet_assurance_id':None,'packet_id':None,'question_responses':[{'accepted':False,'question_id':q,'response':None,'sequence':i} for i,q in enumerate(qs,1)],'response_id':None,'review_observations':[],'review_recommendation':None,'reviewer_identity':None,'reviewer_role':None,'signature_ref':None,'source_digest':None,'submitted':False,'submitted_at':None}
def build_records()->list[dict[str,Any]]:
 out=[]
 for seq,(key,aid,asha,entry,pid,role,qs) in enumerate(PACKETS,1):
  out.append({'blank_response_template':template(qs),'human_gate_pending_count':4,'human_gate_satisfied_count':0,'intake_readiness_id':f'principia:consequence-plan-review-response-intake-readiness:{key}:{seq:04d}','intake_status':'schema-ready-no-response-received','local_only':True,'packet_assurance_id':aid,'packet_assurance_ledger_entry_sha256':entry,'packet_assurance_sha256':asha,'packet_id':pid,'real_authorization_claimed':False,'response_accepted':False,'response_intake_authorized':False,'response_quarantined':False,'response_receipt_permitted':False,'response_received':False,'response_rejected':False,'response_schema':{'encoding':'utf-8','media_type':'application/json','required_fields':list(FIELDS),'schema_id':f'principia:review-response-intake-schema:{key}:{seq:04d}','schema_version':'0.1','sections':[{'section_id':s,'sequence':i,'state':'defined-not-active'} for i,s in enumerate(SECTIONS,1)]},'response_validated':False,'review_completed':False,'review_start_permitted':False,'review_started':False,'reviewer_contact_permitted':False,'reviewer_identity_present':False,'reviewer_role_required':role,'sequence':seq,'status_change':False,'verdict':'response-intake-schema-ready-no-response'})
 return out
def validate_record(r:Mapping[str,Any])->list[str]:
 e=[];s=r.get('response_schema');t=r.get('blank_response_template')
 if r.get('intake_status')!='schema-ready-no-response-received' or r.get('verdict')!='response-intake-schema-ready-no-response':e.append('schema')
 if not isinstance(s,Mapping) or s.get('required_fields')!=list(FIELDS) or [x.get('section_id') for x in s.get('sections',[])]!=list(SECTIONS):e.append('schema')
 if not isinstance(t,Mapping) or t.get('submitted') is not False or any(t.get(k) is not None for k in ('response_id','reviewer_identity','reviewer_role','competence_attestation','conflict_declaration','authorization_to_start','review_recommendation','signature_ref','source_digest','submitted_at')):e.append('template')
 slots=t.get('question_responses',[]) if isinstance(t,Mapping) else []
 if len(slots)!=3 or any(x.get('response') is not None or x.get('accepted') is not False for x in slots):e.append('question')
 for k in ('response_intake_authorized','response_receipt_permitted','response_received','response_validated','response_accepted','response_rejected','response_quarantined','review_start_permitted','review_started','review_completed','status_change','real_authorization_claimed'):
  if r.get(k) is not False:e.append('authority')
 return sorted(set(e))
def build()->dict[str,Any]:
 records=build_records();entries=[];prev=None
 for r in records:
  entry={'intake_readiness_id':r['intake_readiness_id'],'record_sha256':sha_doc(r),'packet_assurance_id':r['packet_assurance_id'],'previous_entry_sha256':prev,'sequence':r['sequence'],'verdict':r['verdict']};d=sha_doc(entry);entries.append({'entry':entry,'entry_sha256':d});prev=d
 summary={'blank_question_slot_count':6,'human_gate_pending_count':8,'human_gate_satisfied_count':0,'intake_readiness_record_count':2,'packet_count':2,'question_slot_count':6,'required_field_count':30,'response_accepted_count':0,'response_intake_authorized_count':0,'response_quarantined_count':0,'response_received_count':0,'response_rejected_count':0,'response_schema_count':2,'response_schema_section_count':12,'response_template_count':2,'response_validated_count':0,'review_completed_count':0,'review_started_count':0,'reviewer_contact_count':0,'reviewer_identity_count':0,'status_change_count':0,'submitted_template_count':0,'real_authorization_claimed':False}
 ledger={'entries':entries,'head_sequence':2,'head_sha256':prev}
 checkpoint={'record_count':2,'ledger_sha256':sha_doc(ledger),'response_received_count':0,'response_validated_count':0,'review_started_count':0,'status_change_count':0}
 recovery={'accepted_count':1,'rejected_count':len(MUTATIONS),'scenario_count':len(MUTATIONS)+1,'scenarios':[{'expected':'accepted','id':'baseline'}]+[{'expected':'rejected','id':m} for m in MUTATIONS]}
 return {'authority':AUTHORITY,'checkpoint':checkpoint,'contract':'principia-offline-consequence-plan-review-response-intake-readiness/0.1','decision':DECISION,'fixture_kind':'bounded-synthetic','id':'principia-atlas-offline-consequence-plan-review-response-intake-readiness-thermal-control','intake_readiness_records':records,'ledger':ledger,'live':False,'live_activation_permitted':False,'mode':MODE,'next_gate':NEXT_GATE,'phase':27,'real_authorization_claimed':False,'recovery':recovery,'result':summary,'source_phase26':SOURCE,'state':STATE,'validation':{'pull_request':None,'status':'pending','tested_head_commit':None}}
def main()->int:
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();errors=verify_sources();text=render(build())
 if a.check:
  if not OUT.is_file() or OUT.read_text(encoding='utf-8')!=text:errors.append('generated file drift')
 else:OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(text,encoding='utf-8')
 if errors:
  print('Phase 27 generation errors:',file=sys.stderr);[print(f'- {e}',file=sys.stderr) for e in errors];return 1
 print('Phase 27 response-intake readiness is deterministic, blank, local-only, and non-receiving.');return 0
if __name__=='__main__':raise SystemExit(main())
