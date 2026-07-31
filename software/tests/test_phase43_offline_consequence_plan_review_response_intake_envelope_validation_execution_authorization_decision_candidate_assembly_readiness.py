from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/generate_phase43_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_candidate_assembly_readiness.py"
SPEC = importlib.util.spec_from_file_location("phase43_generator", SCRIPT)
assert SPEC and SPEC.loader
GEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GEN)


class Phase43AssemblyReadinessTests(unittest.TestCase):
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
        self.assert_rejected(lambda c: c["source_phase42"].__setitem__("candidate_sha256", "0" * 64))

    def test_missing_record_rejected(self) -> None:
        self.assert_rejected(lambda c: c["assembly_readiness_records"].pop())

    def test_policy_check_set_drift_rejected(self) -> None:
        self.assert_rejected(lambda c: c["assembly_readiness_policy"]["check_ids"].pop())

    def test_slot_schema_drift_rejected(self) -> None:
        self.assert_rejected(lambda c: c["assembly_readiness_policy"]["slot_schema"][0].__setitem__("required", False))

    def test_stage_activation_rejected(self) -> None:
        self.assert_rejected(lambda c: c["assembly_readiness_policy"]["stages"][0].__setitem__("state", "active"))

    def test_requirement_evaluation_rejected(self) -> None:
        self.assert_rejected(lambda c: c["assembly_readiness_policy"]["requirements"][0].__setitem__("state", "satisfied"))

    def test_candidate_assembly_rejected(self) -> None:
        self.assert_rejected(lambda c: c["assembly_readiness_records"][0].__setitem__("candidate_assembled", True))

    def test_candidate_creation_permission_rejected(self) -> None:
        self.assert_rejected(lambda c: c["authority"].__setitem__("candidate_creation_permitted", True))

    def test_human_gate_satisfaction_rejected(self) -> None:
        self.assert_rejected(lambda c: c["assembly_readiness_records"][0].__setitem__("human_gate_satisfied_count", 1))

    def test_atlas_permission_rejected(self) -> None:
        self.assert_rejected(lambda c: c["authority"].__setitem__("atlas_call_permitted", True))

    def test_live_activation_rejected(self) -> None:
        self.assert_rejected(lambda c: c.__setitem__("live", True))

    def test_ledger_digest_drift_rejected(self) -> None:
        self.assert_rejected(lambda c: c["ledger"]["entries"][0].__setitem__("entry_sha256", "f" * 64))

    def test_result_counter_drift_rejected(self) -> None:
        self.assert_rejected(lambda c: c["result"].__setitem__("authorization_grant_count", 1))

    def test_next_gate_drift_rejected(self) -> None:
        self.assert_rejected(lambda c: c.__setitem__("next_gate", "unsafe-next-gate"))

    def test_semantic_validation_change_rejected(self) -> None:
        candidate = json.loads(json.dumps(self.baseline))
        candidate["validation"]["status"] = "success"
        self.assertTrue(GEN.evaluate_candidate(candidate))


if __name__ == "__main__":
    unittest.main()
