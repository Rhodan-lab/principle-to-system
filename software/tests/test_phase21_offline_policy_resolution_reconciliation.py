from __future__ import annotations

import copy
import unittest

from scripts import generate_phase21_offline_policy_resolution_reconciliation as gen
from scripts.validate_phase21_offline_policy_resolution_reconciliation import (
    ValidationError,
    validate_bundle,
)


class Phase21ValidationTests(unittest.TestCase):
    def bundle(self):
        return copy.deepcopy(gen.build())

    def assert_code(self, bundle, code):
        with self.assertRaisesRegex(ValidationError, code):
            validate_bundle(bundle)

    def test_baseline_passes(self):
        validate_bundle(self.bundle())

    def test_missing_resolution_rejected(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"].pop()
        self.assert_code(bundle, "E-P21-MISSING")

    def test_duplicate_resolution_rejected(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"][1]["resolution_id"] = (
            bundle[gen.REPORT_PATH]["matches"][0]["resolution_id"]
        )
        self.assert_code(bundle, "E-P21-DUPLICATE")

    def test_proposal_id_mismatch_rejected(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"][0]["proposal_id"] = "unknown"
        self.assert_code(bundle, "E-P21-PROPOSAL-ID")

    def test_resolution_id_mismatch_rejected(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"][0]["resolution_id"] = "unknown"
        self.assert_code(bundle, "E-P21-RESOLUTION-ID")

    def test_sequence_drift_rejected(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"][1]["resolution_sequence"] = 3
        self.assert_code(bundle, "E-P21-SEQUENCE")

    def test_predecessor_drift_rejected(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"][1]["resolution_previous_sha256"] = "0" * 64
        self.assert_code(bundle, "E-P21-PREDECESSOR")

    def test_decision_mismatch_rejected(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"][0]["decision"] = "reject"
        self.assert_code(bundle, "E-P21-DECISION")

    def test_affected_set_drift_rejected(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"][0]["affected_artifacts"].pop()
        self.assert_code(bundle, "E-P21-AFFECTED-SET")

    def test_authorization_claim_rejected(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["real_authorization_claimed"] = True
        self.assert_code(bundle, "E-P21-AUTHORIZATION")

    def test_effective_hold_rejected(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"][1]["hold_effect"] = True
        self.assert_code(bundle, "E-P21-EFFECT")

    def test_status_inheritance_rejected(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["authority"]["status_inheritance"] = "allowed"
        self.assert_code(bundle, "E-P21-AUTHORITY")

    def test_live_activation_rejected(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["live"] = True
        self.assert_code(bundle, "E-P21-LIVE-FROZEN")

    def test_ledger_head_drift_rejected(self):
        bundle = self.bundle()
        bundle[gen.LEDGER_PATH]["head_sha256"] = "0" * 64
        self.assert_code(bundle, "E-P21-LEDGER")

    def test_checkpoint_count_drift_rejected(self):
        bundle = self.bundle()
        bundle[gen.CHECKPOINT_PATH]["matched_resolution_count"] = 1
        self.assert_code(bundle, "E-P21-CHECKPOINT")

    def test_release_source_drift_rejected(self):
        bundle = self.bundle()
        bundle[gen.RELEASE_PATH]["source_phase20"]["phase20_finalization_merge_commit"] = (
            "0" * 40
        )
        self.assert_code(bundle, "E-P21-SOURCE-PIN")


if __name__ == "__main__":
    unittest.main()
