#!/usr/bin/env python3
"""Generate deterministic Phase 39 authorization-decision candidate-boundary readiness evidence."""
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'release/phase-38-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance.json'
SOURCE_POST=ROOT/'release/phase-38-postmerge.json'
OUTPUT=ROOT/'release/phase-39-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness.json'
SOURCE_SHA256='b3c5d8ea8da88cd2975531ccd149b0dde980dc480b9e7385425cafad3e024ec8'
SOURCE_POST_SHA256='5c6e146edfe4d8e8743b8cbf38bf19593383c5fde34e5111c6eb6a6d28c0b2af'
SOURCE_FINALIZATION_COMMIT='013dab928f00b886899f281540b836b589408fa7'
MODE='offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness'
STATE=MODE+'-candidate'
NEXT_GATE=MODE+'-assurance-candidate'
DECISION='response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-recorded-no-candidate-created'
VERDICT='response-envelope-validation-execution-authorization-decision-candidate-boundary-ready-no-candidate'

STAGES=[
 'source-binding','policy-binding','profile-binding','role-separation','conflict-declaration','approval-evidence',
 'rationale-readiness','validity-window','revocation-boundary','audit-chain','zero-effect-check','candidate-freeze'
]
REQUIREMENTS=[
 'phase38-candidate-digest-exact','phase38-postmerge-digest-exact','phase38-finalization-commit-exact',
 'source-assurance-id-exact','source-assurance-record-digest-exact','source-assurance-ledger-entry-exact',
 'source-verdict-exact','decision-policy-id-exact','decision-policy-version-exact','decision-profile-id-exact',
 'reviewer-role-symbolic','authorization-officer-role-symbolic','dual-control-required','role-independence-required',
 'conflict-declaration-required','conflict-declaration-unevaluated','approval-evidence-required','approval-evidence-absent',
 'rationale-schema-defined','rationale-unpopulated','validity-window-defined','validity-window-inactive',
 'revocation-conditions-defined','revocation-inactive','audit-event-schema-defined','audit-events-unrecorded',
 'candidate-template-blank','candidate-creation-forbidden','zero-effect-boundary-preserved','atlas-boundary-preserved'
]
TEMPLATE_FIELDS=[
 'candidate_version','candidate_id','source_assurance_id','source_readiness_id','policy_id','profile_id',
 'reviewer_role','authorization_officer_role','conflict_declaration_ref','approval_evidence_refs','rationale',
 'proposed_decision','valid_from','expires_at','revocation_ref','audit_chain_head','created_at','signature_ref'
]
CHECK_NAMES=[
 'source_phase38_candidate_exact','source_phase38_postmerge_exact','source_phase38_finalization_exact',
 'source_assurance_identity_exact','source_assurance_record_digest_exact','source_assurance_ledger_binding_exact',
 'source_assurance_verdict_exact','boundary_identity_exact','sequence_exact','boundary_policy_identity_exact',
 'boundary_policy_version_exact','boundary_policy_digest_exact','boundary_policy_computed_digest_exact',
 'boundary_profile_identity_exact','boundary_profile_digest_exact','decision_policy_binding_exact',
 'decision_profile_binding_exact','source_readiness_binding_exact','reviewer_role_exact','authorization_officer_role_exact',
 'required_roles_exact','required_roles_unsatisfied','dual_control_required','role_independence_required',
 'conflict_declaration_required','conflict_declaration_unevaluated','approval_evidence_required',
 'approval_evidence_absent','boundary_stages_exact','boundary_stages_digest_exact','boundary_stages_inactive',
 'boundary_requirements_exact','boundary_requirements_digest_exact','boundary_requirements_unevaluated',
 'candidate_template_schema_exact','candidate_template_blank','candidate_template_digest_exact',
 'candidate_template_field_count_exact','rationale_schema_exact','rationale_unpopulated','validity_window_exact',
 'validity_window_inactive','revocation_conditions_exact','revocation_inactive','audit_schema_exact',
 'audit_events_unrecorded','candidate_absent','decision_record_absent','authorization_decision_absent',
 'authorization_grant_absent','authorization_token_unissued','execution_ticket_unissued','execution_states_frozen',
 'envelope_states_frozen','reviewer_identity_absent','reviewer_contact_forbidden','review_states_frozen',
 'approval_states_frozen','human_gates_remain_pending','disposition_unselected','validation_result_absent',
 'status_effects_frozen','authority_boundary_preserved','atlas_boundary_preserved','external_network_boundary_preserved',
 'repository_mutation_boundary_preserved','zero_effect_boundary_preserved','local_only_preserved',
 'real_authorization_unclaimed','live_activation_disabled','source_result_binding_exact','checkpoint_exact',
 'ledger_chain_exact','next_gate_exact','decision_exact','state_exact','contract_exact'
]
assert len(STAGES)==12 and len(REQUIREMENTS)==30 and len(TEMPLATE_FIELDS)==18 and len(CHECK_NAMES)==77

def canonical_bytes(v:Any)->bytes:
    return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def sha_value(v:Any)->str:return hashlib.sha256(canonical_bytes(v)).hexdigest()
def sha_file(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:
    v=json.loads(p.read_text())
    if not isinstance(v,dict): raise ValueError(p)
    return v

def authority()->dict[str,Any]:
    return {
      'atlas_call_permitted':False,'authorization_decision_candidate_creation_permitted':False,
      'authorization_decision_recording_permitted':False,'automatic_release_action':False,
      'automatic_status_change':False,'external_delivery_permitted':False,'external_network_required':False,
      'human_authorization_claimed':False,'local_authorization_decision_candidate_boundary_readiness_permitted':True,
      'repository_mutation':False,'response_envelope_creation_permitted':False,
      'response_envelope_processing_authorized':False,'response_envelope_validation_execution_authorization_grant_permitted':False,
      'response_envelope_validation_execution_authorized':False,'response_envelope_validation_result_recording_permitted':False,
      'response_intake_authorized':False,'response_quarantine_execution_authorized':False,
      'response_receipt_permitted':False,'response_validation_authorized':False,'review_execution_authorized':False,
      'review_request_dispatch_authorized':False,'reviewer_contact_permitted':False,'status_inheritance':'prohibited'
    }

def policy()->dict[str,Any]:
    p={
      'boundary_policy_id':'principia-envelope-validation-execution-authorization-decision-candidate-boundary-policy',
      'boundary_policy_version':'0.1',
      'boundary_stages':[{'sequence':i,'stage_id':s,'state':'inactive'} for i,s in enumerate(STAGES,1)],
      'boundary_requirements':[{'sequence':i,'requirement_id':r,'state':'unevaluated'} for i,r in enumerate(REQUIREMENTS,1)],
      'candidate_template_schema':{'media_type':'application/json','encoding':'utf-8','unknown_fields':'prohibited','required_fields':TEMPLATE_FIELDS},
      'conflict_declaration':{'required':True,'evaluated':False},
      'approval_evidence':{'required_roles':['qualified-pedagogical-reviewer','qualified-release-governance-reviewer'],'required_count':2,'recorded_count':0},
      'validity_window':{'maximum_seconds':86400,'active':False},
      'revocation_conditions':['source-digest-drift','role-conflict','approval-evidence-invalid','expiry-reached'],
      'audit_event_types':['candidate-preparation-requested','source-bound','roles-bound','conflict-checked','approval-evidence-bound','candidate-prepared','candidate-revoked','candidate-expired'],
    }
    p['boundary_policy_sha256']=sha_value(p)
    return p

def recovery_labels()->list[str]:
    fields=['source-candidate-digest','source-postmerge-digest','source-finalization-commit','source-assurance-order',
      'source-assurance-id','source-assurance-digest','source-ledger-entry','source-verdict','boundary-id','boundary-order',
      'policy-id','policy-version','policy-digest','policy-content','profile-id','profile-content','decision-policy-binding',
      'decision-profile-binding','source-readiness-binding','reviewer-role','authorization-officer-role','required-role-state',
      'dual-control','role-independence','conflict-required','conflict-evaluated','approval-required','approval-recorded',
      'stage-order','stage-id','stage-state','requirement-order','requirement-id','requirement-state','template-schema',
      'template-field','template-population','template-field-count','rationale-schema','rationale-population','validity-window',
      'validity-active','revocation-condition','revocation-active','audit-schema','audit-event-recorded','candidate-created',
      'decision-record-created','decision-recorded','authorization-grant','token-issued','ticket-issued','execution-run',
      'envelope-received','reviewer-identity','reviewer-contact','review-start','approval-received','human-gate-satisfied',
      'disposition-selected','validation-result','status-change','authority','atlas-call','external-network','repository-mutation',
      'automatic-release','automatic-status','real-authorization','live','check-name','check-value','check-count',
      'failed-check-count','verdict','status','ledger-order','ledger-record-digest','ledger-previous','ledger-entry-digest',
      'ledger-head','checkpoint','result-count','next-gate','decision','state','contract']
    labels=[]
    for name in ('feedback-manual-review','model-boundary-release-governance'):
        labels.extend(f'reject-{name}-{field}-drift' for field in fields)
    labels += ['reject-missing-boundary-record','reject-extra-boundary-record','reject-duplicate-boundary-record',
      'reject-boundary-record-order-drift','reject-cross-profile-source-binding','reject-noncanonical-json']
    return labels

def build_manifest(source:dict[str,Any],post:dict[str,Any])->dict[str,Any]:
    if sha_file(SOURCE)!=SOURCE_SHA256: raise ValueError('Phase 38 candidate digest mismatch')
    if sha_file(SOURCE_POST)!=SOURCE_POST_SHA256: raise ValueError('Phase 38 postmerge digest mismatch')
    if source.get('state')!='offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-candidate': raise ValueError('Phase 38 state mismatch')
    if post.get('state')!='offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-readiness-assurance-validated': raise ValueError('Phase 38 postmerge state mismatch')
    if post.get('principia',{}).get('merge_commit')!='be3f305f7234875be541e6f5e2bb8fb1bf0c0f43': raise ValueError('Phase 38 candidate merge mismatch')
    pol=policy(); by_id={e['entry']['assurance_id']:e for e in source['ledger']['entries']}
    records=[]; ledger=[]; previous=None
    for seq,assurance in enumerate(source['assurances'],1):
        source_id=assurance['assurance_id']; src_ledger=by_id[source_id]; src_sha=sha_value(assurance)
        if src_sha!=src_ledger['entry']['record_sha256']: raise ValueError('source assurance digest mismatch')
        suffix=source_id.rsplit(':',2)[-2]
        profile={
          'boundary_profile_id':f'principia:authorization-decision-candidate-boundary-profile:{suffix}:{seq:04d}',
          'source_assurance_id':source_id,'source_readiness_id':assurance['source_decision_readiness_id'],
          'decision_policy_id':assurance['decision_policy_id'],'decision_profile_id':assurance['decision_profile_id'],
          'required_roles':['qualified-pedagogical-reviewer','qualified-release-governance-reviewer'],
          'reviewer_role':'qualified-pedagogical-reviewer' if seq==1 else 'qualified-release-governance-reviewer',
          'authorization_officer_role':'qualified-release-governance-reviewer','dual_control_required':True,
          'role_independence_required':True,'conflict_declaration_required':True,
        }
        template={k:None for k in TEMPLATE_FIELDS}
        checks={n:True for n in CHECK_NAMES}
        boundary_id=f'principia:authorization-decision-candidate-boundary-readiness:{suffix}:{seq:04d}'
        rec={
          'approval_evidence_recorded':False,'approval_received':False,'audit_event_recorded_count':0,
          'authorization_decision_candidate_created':False,'authorization_decision_record_created':False,
          'authorization_decision_recorded':False,'authorization_granted':False,'authorization_token_issued':False,
          'boundary_check_count':len(CHECK_NAMES),'boundary_checks':checks,'boundary_id':boundary_id,
          'boundary_policy_id':pol['boundary_policy_id'],'boundary_policy_sha256':pol['boundary_policy_sha256'],
          'boundary_profile':profile,'boundary_profile_sha256':sha_value(profile),
          'candidate_template':template,'candidate_template_field_count':len(template),'candidate_template_sha256':sha_value(template),
          'conflict_declaration_evaluated':False,'execution_run_created':False,'execution_ticket_issued':False,
          'failed_boundary_check_count':0,'human_gate_pending_count':assurance['human_gate_pending_count'],
          'human_gate_satisfied_count':0,'local_only':True,'real_authorization_claimed':False,
          'response_envelope_received':False,'reviewer_contact_permitted':False,'reviewer_identity_present':False,
          'sequence':seq,'source_assurance_id':source_id,'source_assurance_record_sha256':src_sha,
          'source_ledger_entry_sha256':src_ledger['entry_sha256'],'status':'boundary-ready-no-candidate',
          'status_change':False,'validation_result_recorded':False,'verdict':VERDICT,
        }
        rec_sha=sha_value(rec)
        entry={'boundary_id':boundary_id,'previous_entry_sha256':previous,'record_sha256':rec_sha,'sequence':seq,
          'source_assurance_id':source_id,'source_ledger_entry_sha256':src_ledger['entry_sha256'],'verdict':VERDICT}
        entry_sha=sha_value(entry); ledger.append({'entry':entry,'entry_sha256':entry_sha}); previous=entry_sha; records.append(rec)
    result=copy.deepcopy(source['result'])
    result.update({
      'boundary_policy_count':1,'boundary_profile_count':len(records),'candidate_boundary_readiness_record_count':len(records),
      'boundary_stage_count':len(STAGES)*len(records),'boundary_requirement_count':len(REQUIREMENTS)*len(records),
      'boundary_requirement_evaluated_count':0,'candidate_template_count':len(records),
      'candidate_template_field_count':len(TEMPLATE_FIELDS)*len(records),'boundary_check_count':len(records)*len(CHECK_NAMES),
      'failed_boundary_check_count':0,'audit_event_recorded_count':0,
    })
    rejected=recovery_labels()
    return {
      'authority':authority(),'boundary_policy':pol,'boundary_readiness_records':records,
      'checkpoint':{'boundary_check_count':len(records)*len(CHECK_NAMES),'boundary_record_count':len(records),
        'authorization_decision_candidate_created_count':0,'authorization_decision_recorded_count':0,
        'authorization_granted_count':0,'authorization_token_issued_count':0,'execution_run_count':0,
        'failed_boundary_check_count':0,'ledger_sha256':previous,'response_envelope_received_count':0,'status_change_count':0},
      'contract':'principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness/0.1',
      'decision':DECISION,'fixture_kind':'bounded-synthetic',
      'id':'principia-atlas-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-thermal-control',
      'ledger':{'entries':ledger,'head_sequence':len(ledger),'head_sha256':previous},'live':False,'live_activation_permitted':False,
      'mode':MODE,'next_gate':NEXT_GATE,'phase':39,'real_authorization_claimed':False,
      'recovery':{'accepted':['baseline-phase38-decision-candidate-boundary-readiness'],'accepted_count':1,
        'rejected':rejected,'rejected_count':len(rejected),'scenario_count':len(rejected)+1},
      'result':result,'source_phase38':{'phase38_candidate_sha256':SOURCE_SHA256,
        'phase38_finalization_commit':SOURCE_FINALIZATION_COMMIT,'phase38_postmerge_sha256':SOURCE_POST_SHA256},
      'state':STATE,'validation':{'pull_request':None,'status':'candidate','tested_head_commit':None}
    }

def render(v:dict[str,Any])->bytes:return canonical_bytes(v)+b'\n'
def main()->int:
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    m=build_manifest(load(SOURCE),load(SOURCE_POST)); payload=render(m)
    if a.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes()!=payload: print('Phase 39 candidate drift');return 1
        print(f"Phase 39 candidate passed: bytes={len(payload)}, sha256={hashlib.sha256(payload).hexdigest()}, records={len(m['boundary_readiness_records'])}, checks={m['result']['boundary_check_count']}.")
        return 0
    OUTPUT.write_bytes(payload);print(f'Wrote {OUTPUT}: bytes={len(payload)}, sha256={hashlib.sha256(payload).hexdigest()}');return 0
if __name__=='__main__':raise SystemExit(main())
