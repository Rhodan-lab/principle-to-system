from __future__ import annotations

import copy
import unittest

from scripts.generate_phase28_offline_consequence_plan_review_response_intake_readiness_assurance import (
    CHECK_NAMES,
    MUTATIONS,
    build,
    build_assurances,
    validate_assurance,
)

class Phase28AssuranceTests(unittest.TestCase):
    def test_build_is_deterministic(self) -> None:
        self.assertEqual(build(), build())

    def test_two_assurances_and_forty_checks(self) -> None:
        value = build()
        self.assertEqual(len(value["assurances"]), 2)
        self.assertEqual(value["result"]["assurance_check_count"], 40)
        self.assertTrue(all(len(a["assurance_checks"]) == len(CHECK_NAMES) for a in value["assurances"]))

    def test_baseline_assurances_pass(self) -> None:
        for assurance in build_assurances():
            self.assertEqual(validate_assurance(assurance), [])

    def test_failed_check_is_rejected(self) -> None:
        assurance = copy.deepcopy(build_assurances()[0])
        assurance["assurance_checks"]["schema_identity_exact"] = False
        self.assertIn("checks", validate_assurance(assurance))

    def test_fabricated_response_is_rejected(self) -> None:
        assurance = copy.deepcopy(build_assurances()[0])
        assurance["response_received"] = True
        self.assertIn("authority", validate_assurance(assurance))

    def test_human_gate_satisfaction_is_rejected(self) -> None:
        assurance = copy.deepcopy(build_assurances()[0])
        assurance["human_gate_satisfied_count"] = 1
        self.assertIn("human-gates", validate_assurance(assurance))

    def test_review_start_is_rejected(self) -> None:
        assurance = copy.deepcopy(build_assurances()[1])
        assurance["review_started"] = True
        self.assertIn("authority", validate_assurance(assurance))

    def test_schema_count_drift_is_rejected(self) -> None:
        assurance = copy.deepcopy(build_assurances()[1])
        assurance["required_field_count"] = 29
        self.assertIn("schema", validate_assurance(assurance))

    def test_recovery_matrix_is_broad(self) -> None:
        self.assertGreaterEqual(len(MUTATIONS), 70)
        self.assertIn("response-received", MUTATIONS)
        self.assertIn("atlas-call-permitted", MUTATIONS)
        self.assertIn("repository-mutation", MUTATIONS)

if __name__ == "__main__":
    unittest.main()
