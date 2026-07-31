#!/usr/bin/env python3
from __future__ import annotations
import base64, json, subprocess, zlib
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
BRANCH = "agent/phase-46-offline-authorization-decision-candidate-population-readiness-assurance"
PARTS = sorted((ROOT / "scripts").glob(".phase46-payload-*"))
FILES = [
"release/phase-46-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance.json",
"reports/phase-46-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-readiness-assurance.md",
"scripts/generate_phase46_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_readiness_assurance.py",
"scripts/validate_phase46_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_readiness_assurance.py",
"software/tests/test_phase46_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_readiness_assurance.py",
]
def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)
def main() -> int:
    payload = "".join(path.read_text(encoding="utf-8") for path in PARTS)
    data = json.loads(zlib.decompress(base64.b64decode(payload)))
    for relative, encoded in data.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(base64.b64decode(encoded))
    run("python3","-m","py_compile",FILES[2],FILES[3],FILES[4])
    run("python3",FILES[2],"--check")
    run("python3",FILES[3])
    run("python3","-m","unittest","discover","-s","software/tests","-p","test_phase46*population_readiness_assurance.py","-v")
    run("python3","scripts/validate_phase45_postmerge_record.py")
    run("git","diff","--check")
    publisher = Path(__file__).resolve()
    for path in PARTS:
        path.unlink()
    publisher.unlink()
    run("git","config","user.name","github-actions[bot]")
    run("git","config","user.email","41898282+github-actions[bot]@users.noreply.github.com")
    rels=[str(path.relative_to(ROOT)) for path in PARTS]
    run("git","add","-f","--",*FILES,*rels,str(publisher.relative_to(ROOT)))
    run("git","commit","-m","Add Phase 46 population-readiness assurance")
    run("git","push","origin",f"HEAD:{BRANCH}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
