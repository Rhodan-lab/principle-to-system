from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/generate_phase42_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_preparation_readiness_assurance.py"
SPEC = importlib.util.spec_from_file_location("phase42_generator", SCRIPT)
assert SPEC and SPEC.loader
GEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GEN)


class Phase42AssuranceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = GEN.build_manifest()

    def assert_rejected(self, mutator) -> None:
        candidate = copy.deepcopy(self.baseline)
        mutator(candidate)
        self.assertTrue(GEN.evaluate_candidate(candidate))

    def test_baseline_is_accepted(self) -> None:
        self.assertEqual(GEN.evaluate_candidate(copy.deepcopy(self.baseline)), [])

    def test_source_digest_drift_rejected(self) -> None:
        self.assert_rejected(lambda c: c["source_phase41"].__setitem__("phase41_candidate_sha256", "0" * 64))

    def test_missing_assurance_record_rejected(self) -> None:
        self.assert_rejected(lambda c: c["candidate_preparation_readiness_assurance_records"].pop())

    def test_assurance_check_failure_rejected(self) -> None:
        self.assert_rejected(lambda c: c["candidate_preparation_readiness_assurance_records"][0]["assurance_checks"].__setitem__("source_candidate_sha_exact", False))

    def test_field_population_rejected(self) -> None:
        self.assert_rejected(lambda c: c["candidate_preparation_readiness_assurance_records"][0]["candidate_field_plan"][0].__setitem__("state", "populated"))

    def test_candidate_creation_rejected(self) -> None:
        self.assert_rejected(lambda c: c["candidate_preparation_readiness_assurance_records"][0].__setitem__("authorization_decision_candidate_created", True))

    def test_candidate_assembly_permission_rejected(self) -> None:
        self.assert_rejected(lambda c: c["candidate_preparation_readiness_assurance_records"][0].__setitem__("candidate_assembly_permitted", True))

    def test_human_gate_satisfaction_rejected(self) -> None:
        self.assert_rejected(lambda c: c["candidate_preparation_readiness_assurance_records"][0].__setitem__("human_gate_satisfied_count", 1))

    def test_atlas_permission_rejected(self) -> None:
        self.assert_rejected(lambda c: c["authority"].__setitem__("atlas_call_permitted", True))

    def test_live_activation_rejected(self) -> None:
        self.assert_rejected(lambda c: c.__setitem__("live", True))

    def test_ledger_digest_drift_rejected(self) -> None:
        self.assert_rejected(lambda c: c["ledger"]["entries"][0].__setitem__("entry_sha256", "f" * 64))

    def test_result_counter_drift_rejected(self) -> None:
        self.assert_rejected(lambda c: c["result"].__setitem__("authorization_granted_count", 1))

    def test_next_gate_drift_rejected(self) -> None:
        self.assert_rejected(lambda c: c.__setitem__("next_gate", "unsafe-next-gate"))

    def test_noncanonical_semantic_change_rejected(self) -> None:
        candidate = json.loads(json.dumps(self.baseline))
        candidate["validation"]["status"] = "success"
        self.assertTrue(GEN.evaluate_candidate(candidate))


if __name__ == "__main__":
    unittest.main()
