#!/usr/bin/env python3
"""Publish the validated Phase 47 candidate package, then remove this bootstrap."""
from __future__ import annotations
import base64
import hashlib
import io
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PART_DIR = ROOT / ".phase47"
PARTS = [PART_DIR / f"payload.part{index:02d}" for index in range(5)]
PATHS = [
    "release/phase-47-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness.json",
    "reports/phase-47-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-population-execution-readiness.md",
    "scripts/generate_phase47_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_execution_readiness.py",
    "scripts/validate_phase47_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_execution_readiness.py",
    "software/tests/test_phase47_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_execution_readiness.py",
]

encoded = "".join(path.read_text(encoding="utf-8") for path in PARTS)
if hashlib.sha256(encoded.encode()).hexdigest() != "3a4bbaba34822a5ee05fb875c6e3aea59dc6c0585d19ee782977e0ad61b06336":
    raise SystemExit("Phase 47 payload-part digest drift")
archive_bytes = base64.b64decode(encoded)
if hashlib.sha256(archive_bytes).hexdigest() != "59382c46f3d4ab48d9d4b19738e1ee1a3eda999bab857a566dcedc8e37a478c1":
    raise SystemExit("Phase 47 archive digest drift")
with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
    archive.extractall(ROOT)

commands = [
    (
        "python3", "-m", "py_compile",
        "scripts/generate_phase47_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_execution_readiness.py",
        "scripts/validate_phase47_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_execution_readiness.py",
        "scripts/validate_phase46_postmerge_record.py",
    ),
    ("python3", "scripts/generate_phase47_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_execution_readiness.py", "--check"),
    ("python3", "scripts/validate_phase47_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_population_execution_readiness.py"),
    ("python3", "-m", "unittest", "discover", "-s", "software/tests", "-p", "test_phase47*population_execution_readiness.py", "-v"),
    ("python3", "scripts/validate_phase46_postmerge_record.py"),
    ("git", "diff", "--check"),
]
for command in commands:
    subprocess.run(command, cwd=ROOT, check=True)

bootstrap = Path(__file__)
for path in PARTS:
    path.unlink()
bootstrap.unlink()
subprocess.run(("git", "config", "user.name", "github-actions[bot]"), cwd=ROOT, check=True)
subprocess.run(("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"), cwd=ROOT, check=True)
subprocess.run(("git", "add", "-f", *PATHS), cwd=ROOT, check=True)
subprocess.run(("git", "add", "-u", ".phase47", bootstrap.relative_to(ROOT).as_posix()), cwd=ROOT, check=True)
subprocess.run(("git", "diff", "--cached", "--check"), cwd=ROOT, check=True)
subprocess.run(("git", "commit", "-m", "Add Phase 47 population execution readiness"), cwd=ROOT, check=True)
subprocess.run(("git", "push", "origin", "HEAD"), cwd=ROOT, check=True)
print("Phase 47 candidate package published: manifest_sha256=31b57486ca590cd066642981e640c21cc306869f99241d0fa81013d681df5065")
