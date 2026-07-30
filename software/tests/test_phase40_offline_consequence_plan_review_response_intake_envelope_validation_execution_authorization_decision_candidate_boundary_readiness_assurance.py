from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "scripts/validate_phase40_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_boundary_readiness_assurance.py"
spec = importlib.util.spec_from_file_location("phase40_validator", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(validator)

CANDIDATE = json.loads((ROOT / "release/phase-40-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness-assurance.json").read_text())
SOURCE = json.loads((ROOT / "release/phase-39-offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-boundary-readiness.json").read_text())
POST = json.loads((ROOT / "release/phase-39-postmerge.json").read_text())


class Phase40Tests(unittest.TestCase):
    def assertRejected(self, mutate):
        candidate = copy.deepcopy(CANDIDATE)
        mutate(candidate)
        self.assertTrue(validator.validate_payload(candidate, SOURCE, POST))

    def test_baseline(self):
        self.assertEqual([], validator.validate_payload(CANDIDATE, SOURCE, POST))

    def test_candidate_creation_rejected(self):
        self.assertRejected(lambda d: d["assurances"][0].__setitem__("authorization_decision_candidate_created", True))

    def test_template_digest_drift_rejected(self):
        self.assertRejected(lambda d: d["assurances"][0].__setitem__("candidate_template_sha256", "0" * 64))

    def test_source_digest_drift_rejected(self):
        self.assertRejected(lambda d: d["source_phase39"].__setitem__("phase39_candidate_sha256", "0" * 64))

    def test_check_failure_rejected(self):
        self.assertRejected(lambda d: d["assurances"][0]["assurance_checks"].__setitem__("candidate_absent", False))

    def test_reviewer_contact_rejected(self):
        self.assertRejected(lambda d: d["assurances"][1].__setitem__("reviewer_contact_permitted", True))

    def test_grant_rejected(self):
        self.assertRejected(lambda d: d["assurances"][0].__setitem__("authorization_granted", True))

    def test_human_gate_rejected(self):
        self.assertRejected(lambda d: d["assurances"][0].__setitem__("human_gate_satisfied_count", 1))

    def test_ledger_drift_rejected(self):
        self.assertRejected(lambda d: d["ledger"]["entries"][1]["entry"].__setitem__("previous_entry_sha256", None))

    def test_atlas_authority_rejected(self):
        self.assertRejected(lambda d: d["authority"].__setitem__("atlas_call_permitted", True))

    def test_live_rejected(self):
        self.assertRejected(lambda d: d.__setitem__("live", True))

    def test_next_gate_rejected(self):
        self.assertRejected(lambda d: d.__setitem__("next_gate", "unexpected"))

    def test_recovery_count_rejected(self):
        self.assertRejected(lambda d: d["recovery"].__setitem__("scenario_count", 1))

    def test_status_change_rejected(self):
        self.assertRejected(lambda d: d["result"].__setitem__("status_change_count", 1))


if __name__ == "__main__":
    unittest.main()
