from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.validate_phase38_offline_consequence_plan_review_response_intake_envelope_validation_execution_authorization_decision_readiness_assurance import (
    CANDIDATE,
    SOURCE,
    SOURCE_POST,
    validate_manifest,
)


class Phase38AssuranceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = json.loads(Path(SOURCE).read_text())
        cls.post = json.loads(Path(SOURCE_POST).read_text())
        cls.candidate = json.loads(Path(CANDIDATE).read_text())

    def assert_rejected(self, mutate) -> None:
        value = copy.deepcopy(self.candidate)
        mutate(value)
        self.assertTrue(validate_manifest(value, self.source, self.post))

    def test_baseline_passes(self) -> None:
        self.assertEqual(validate_manifest(copy.deepcopy(self.candidate), self.source, self.post), [])

    def test_source_binding_drift_rejected(self) -> None:
        self.assert_rejected(lambda d: d["source_phase37"].__setitem__("phase37_candidate_sha256", "0" * 64))

    def test_assurance_identity_drift_rejected(self) -> None:
        self.assert_rejected(lambda d: d["assurances"][0].__setitem__("assurance_id", "drift"))

    def test_source_record_digest_drift_rejected(self) -> None:
        self.assert_rejected(lambda d: d["assurances"][0].__setitem__("source_readiness_record_sha256", "0" * 64))

    def test_false_assurance_check_rejected(self) -> None:
        self.assert_rejected(lambda d: d["assurances"][0]["assurance_checks"].__setitem__("atlas_boundary_preserved", False))

    def test_blank_record_digest_drift_rejected(self) -> None:
        self.assert_rejected(lambda d: d["assurances"][1].__setitem__("blank_decision_record_sha256", "0" * 64))

    def test_decision_candidate_rejected(self) -> None:
        self.assert_rejected(lambda d: d["assurances"][0].__setitem__("authorization_decision_candidate_created", True))

    def test_decision_record_rejected(self) -> None:
        self.assert_rejected(lambda d: d["assurances"][0].__setitem__("authorization_decision_recorded", True))

    def test_authorization_grant_rejected(self) -> None:
        self.assert_rejected(lambda d: d["assurances"][1].__setitem__("authorization_granted", True))

    def test_token_issue_rejected(self) -> None:
        self.assert_rejected(lambda d: d["assurances"][1].__setitem__("authorization_token_issued", True))

    def test_atlas_authority_rejected(self) -> None:
        self.assert_rejected(lambda d: d["authority"].__setitem__("atlas_call_permitted", True))

    def test_live_activation_rejected(self) -> None:
        self.assert_rejected(lambda d: d.__setitem__("live", True))

    def test_ledger_drift_rejected(self) -> None:
        self.assert_rejected(lambda d: d["ledger"].__setitem__("head_sha256", "0" * 64))

    def test_next_gate_drift_rejected(self) -> None:
        self.assert_rejected(lambda d: d.__setitem__("next_gate", "authorization-granted"))


if __name__ == "__main__":
    unittest.main()
