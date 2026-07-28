from __future__ import annotations

import copy
import unittest

from scripts import generate_phase21_offline_policy_resolution_reconciliation as gen
from scripts import validate_phase21_offline_policy_resolution_reconciliation as val


class Phase21ReconciliationTests(unittest.TestCase):
    def bundle(self):
        return copy.deepcopy(gen.build())

    def assert_code(self, bundle, code: str):
        with self.assertRaisesRegex(val.ValidationError, code):
            val.validate_bundle(bundle)

    def test_baseline(self):
        val.validate_bundle(self.bundle())

    def test_missing_resolution(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"].pop()
        self.assert_code(bundle, "E-P21-MISSING")

    def test_orphan_resolution(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"].append(copy.deepcopy(bundle[gen.REPORT_PATH]["matches"][1]))
        self.assert_code(bundle, "E-P21-ORPHAN")

    def test_duplicate_proposal(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"][1]["proposal_id"] = bundle[gen.REPORT_PATH]["matches"][0]["proposal_id"]
        self.assert_code(bundle, "E-P21-DUPLICATE")

    def test_proposal_digest_mismatch(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"][0]["proposal_document_sha256"] = "0" * 64
        self.assert_code(bundle, "E-P21-PROPOSAL-DIGEST")

    def test_resolution_digest_mismatch(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"][0]["resolution_sha256"] = "0" * 64
        self.assert_code(bundle, "E-P21-RESOLUTION-DIGEST")

    def test_decision_mismatch(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"][1]["decision"] = "accept"
        self.assert_code(bundle, "E-P21-DECISION")

    def test_affected_set_drift(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"][0]["affected_artifacts"].pop()
        self.assert_code(bundle, "E-P21-AFFECTED-SET")

    def test_real_authorization_claimed(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["real_authorization_claimed"] = True
        self.assert_code(bundle, "E-P21-AUTHORIZATION")

    def test_effective_hold(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["matches"][1]["effective_hold"] = True
        self.assert_code(bundle, "E-P21-EFFECT")

    def test_status_inheritance(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["authority"]["status_inheritance"] = "allowed"
        self.assert_code(bundle, "E-P21-STATUS-INHERITANCE")

    def test_live_activation(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["live"] = True
        self.assert_code(bundle, "E-P21-LIVE-FROZEN")

    def test_ledger_head_drift(self):
        bundle = self.bundle()
        bundle[gen.LEDGER_PATH]["head_entry_sha256"] = "0" * 64
        self.assert_code(bundle, "E-P21-LEDGER")

    def test_checkpoint_count_drift(self):
        bundle = self.bundle()
        bundle[gen.CHECKPOINT_PATH]["matched_resolution_count"] = 1
        self.assert_code(bundle, "E-P21-CHECKPOINT")

    def test_repository_mutation(self):
        bundle = self.bundle()
        bundle[gen.RELEASE_PATH]["authority"]["repository_mutation"] = True
        self.assert_code(bundle, "E-P21-AUTHORITY")


if __name__ == "__main__":
    unittest.main()
