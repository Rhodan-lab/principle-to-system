#!/usr/bin/env python3
"""Validate the immutable Phase 35 post-merge record and project-state transition."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent.parent
CANDIDATE=ROOT/"release/phase-35-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness.json"
POST=ROOT/"release/phase-35-postmerge.json"
REPORT=ROOT/"reports/phase-35-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness.md"
STATE=ROOT/"PROJECT_STATE.md"
WORKFLOW=ROOT/".github/workflows/validate-phase-35-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness.yml"
CANDIDATE_SHA="539bfd832f157b54d491998c0438c67d284d1250bd57a5f3d54d623815a1e7a3"
POST_SHA="97e0b7c8b2ea718b8c29fdd98340d8e699791e1a7cd3d19bdbb5bdd6e5ff3fc2"
HEAD="f0f97245f9c0b4057a55d43d9a2d7b4a26dc8391"
MERGE="4cc3c5dcf3ad1d48c15ee3468ff75b08634bd866"
NEXT="offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-assurance-candidate"
def sha_file(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path:Path)->dict[str,Any]:
 v=json.loads(path.read_text())
 if not isinstance(v,dict):raise ValueError(path)
 return v
def validate()->list[str]:
 errors=[]
 for path,label in ((CANDIDATE,"candidate"),(POST,"postmerge"),(REPORT,"report"),(STATE,"project state"),(WORKFLOW,"workflow")):
  if not path.is_file():errors.append(f"Phase 35 {label} missing")
 if errors:return errors
 if sha_file(CANDIDATE)!=CANDIDATE_SHA:errors.append("Phase 35 candidate digest drift")
 if sha_file(POST)!=POST_SHA:errors.append("Phase 35 postmerge digest drift")
 candidate,post=load(CANDIDATE),load(POST)
 if candidate.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-candidate" or candidate.get("next_gate")!=NEXT:errors.append("Phase 35 candidate gate drift")
 if post.get("contract")!="principia-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-finalization/0.1":errors.append("Phase 35 finalization contract drift")
 if post.get("state")!="offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-validated" or post.get("next_gate")!=NEXT:errors.append("Phase 35 final state drift")
 if post.get("candidate_record")!={"path":"release/phase-35-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness.json","sha256":CANDIDATE_SHA}:errors.append("Phase 35 candidate binding drift")
 if post.get("principia")!={"candidate_head_commit":HEAD,"merge_commit":MERGE,"pull_request":61,"repository":"Rhodan-lab/principle-to-system"}:errors.append("Phase 35 merge provenance drift")
 if post.get("validation")!={"applicable_workflows":29,"candidate_head_commit":HEAD,"status":"success"}:errors.append("Phase 35 workflow provenance drift")
 if post.get("result")!=candidate.get("result"):errors.append("Phase 35 result binding drift")
 if post.get("authority")!=candidate.get("authority") or post.get("live") is not False or post.get("real_authorization_claimed") is not False:errors.append("Phase 35 authority drift")
 state=STATE.read_text()
 required=("**Phase 35 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Readiness merged and validated through PR #61.**","Phase 35 state: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-validated**","| 35 | Offline consequence-plan review-response intake envelope validation execution authorization readiness | Merged and validated through PR #61 |",f"Phase 35 exact candidate validation passed at `{HEAD}`",f"PR #61 was merged into `main` at commit `{MERGE}`","Historical Phase 34 finalization marker: **Phase 34 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Readiness Assurance merged and validated through PR #59.**","Historical Phase 35 candidate marker: `exact-head validation pending`","Historical Phase 35 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-candidate`","Atlas remains unchanged by Principia Phase 35","## Phase 35 result — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Readiness",CANDIDATE_SHA,HEAD,MERGE,"all 29 applicable workflows","135 deterministic scenarios","134 mutations",f"Next gate: **{NEXT}**")
 for marker in required:
  if marker not in state:errors.append(f"Phase 35 project-state marker missing: {marker}")
 if "Principia and Atlas remain separate repositories with separate lifecycle authority." not in state:errors.append("Repository authority separation lost")
 report=REPORT.read_text()
 for marker in ("# Phase 35 — Offline Consequence-Plan Review-Response Intake Envelope Validation Execution Authorization Readiness","State: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-readiness-validated`",f"Candidate SHA-256: `{CANDIDATE_SHA}`",f"Exact tested head: `{HEAD}`","Candidate PR: `#61`",f"Candidate merge: `{MERGE}`","Applicable candidate workflows: `29`",f"Post-merge SHA-256: `{POST_SHA}`",f"Next gate: `{NEXT}`","135 deterministic scenarios","134 rejected mutations","No authorization candidate was created"):
  if marker not in report:errors.append(f"Phase 35 report marker missing: {marker}")
 workflow=WORKFLOW.read_text()
 if "contents: read" not in workflow:errors.append("Phase 35 workflow is not read-only")
 if "validate_phase35_postmerge_record.py" not in workflow:errors.append("Phase 35 workflow does not validate postmerge record")
 for token in ("contents: write","pull_request_target","git push","git commit","repository: Rhodan-lab/Atlas"):
  if token in workflow:errors.append(f"Phase 35 workflow forbidden token: {token}")
 return errors
def main()->int:
 errors=validate()
 if errors:
  print("Phase 35 post-merge record errors:",file=sys.stderr)
  for error in errors:print(f"- {error}",file=sys.stderr)
  return 1
 print(f"Phase 35 post-merge record passed: candidate={CANDIDATE_SHA}, postmerge={POST_SHA}, head={HEAD}, merge={MERGE}, workflows=29.")
 return 0
if __name__=="__main__":raise SystemExit(main())
