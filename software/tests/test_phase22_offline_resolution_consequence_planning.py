from __future__ import annotations

import copy
import unittest

from scripts import generate_phase22_offline_resolution_consequence_planning as gen
from scripts.validate_phase22_offline_resolution_consequence_planning import (
    ValidationError,
    validate_bundle,
)


class Phase22ValidationTests(unittest.TestCase):
    def bundle(self):
        return copy.deepcopy(gen.build())

    def assert_code(self, bundle, code):
        with self.assertRaisesRegex(ValidationError, code):
            validate_bundle(bundle)

    def test_baseline_passes(self):
        validate_bundle(self.bundle())

    def test_missing_plan_rejected(self):
        bundle = self.bundle()
        bundle[gen.PLANS_PATH]["plans"].pop()
        self.assert_code(bundle, "E-P22-MISSING")

    def test_orphan_plan_rejected(self):
        bundle = self.bundle()
        bundle[gen.PLANS_PATH]["plans"].append(copy.deepcopy(bundle[gen.PLANS_PATH]["plans"][0]))
        self.assert_code(bundle, "E-P22-ORPHAN")

    def test_duplicate_plan_rejected(self):
        bundle = self.bundle()
        bundle[gen.PLANS_PATH]["plans"][1]["plan_id"] = bundle[gen.PLANS_PATH]["plans"][0]["plan_id"]
        self.assert_code(bundle, "E-P22-DUPLICATE")

    def test_unknown_resolution_rejected(self):
        bundle = self.bundle()
        bundle[gen.PLANS_PATH]["plans"][0]["source_resolution_id"] = "unknown"
        self.assert_code(bundle, "E-P22-RESOLUTION-ID")

    def test_sequence_drift_rejected(self):
        bundle = self.bundle()
        bundle[gen.PLANS_PATH]["plans"][1]["sequence"] = 3
        self.assert_code(bundle, "E-P22-SEQUENCE")

    def test_step_count_drift_rejected(self):
        bundle = self.bundle()
        bundle[gen.PLANS_PATH]["plans"][0]["steps"].pop()
        self.assert_code(bundle, "E-P22-STEPS")

    def test_step_started_rejected(self):
        bundle = self.bundle()
        bundle[gen.PLANS_PATH]["plans"][0]["steps"][0]["state"] = "started"
        self.assert_code(bundle, "E-P22-EXECUTION")

    def test_execution_permission_rejected(self):
        bundle = self.bundle()
        bundle[gen.PLANS_PATH]["plans"][0]["steps"][0]["execution_permitted"] = True
        self.assert_code(bundle, "E-P22-EXECUTION")

    def test_plan_started_rejected(self):
        bundle = self.bundle()
        bundle[gen.PLANS_PATH]["plans"][0]["state"] = "started"
        self.assert_code(bundle, "E-P22-EXECUTION")

    def test_review_completed_rejected(self):
        bundle = self.bundle()
        bundle[gen.PLANS_PATH]["plans"][0]["review_completed"] = True
        self.assert_code(bundle, "E-P22-EXECUTION")

    def test_content_change_proposed_rejected(self):
        bundle = self.bundle()
        bundle[gen.PLANS_PATH]["plans"][0]["content_change_proposed"] = True
        self.assert_code(bundle, "E-P22-EFFECT")

    def test_effective_hold_rejected(self):
        bundle = self.bundle()
        bundle[gen.PLANS_PATH]["plans"][1]["effective_hold"] = True
        self.assert_code(bundle, "E-P22-EFFECT")

    def test_authorization_claim_rejected(self):
        bundle = self.bundle()
        bundle[gen.PLANS_PATH]["plans"][0]["real_authorization_claimed"] = True
        self.assert_code(bundle, "E-P22-AUTHORIZATION")

    def test_ledger_head_drift_rejected(self):
        bundle = self.bundle()
        bundle[gen.LEDGER_PATH]["head_sha256"] = "0" * 64
        self.assert_code(bundle, "E-P22-LEDGER")

    def test_checkpoint_count_drift_rejected(self):
        bundle = self.bundle()
        bundle[gen.CHECKPOINT_PATH]["started_plan_count"] = 1
        self.assert_code(bundle, "E-P22-EXECUTION")

    def test_live_activation_rejected(self):
        bundle = self.bundle()
        bundle[gen.PLANS_PATH]["live"] = True
        self.assert_code(bundle, "E-P22-LIVE-FROZEN")

    def test_release_source_drift_rejected(self):
        bundle = self.bundle()
        bundle[gen.RELEASE_PATH]["source_phase21"]["phase21_finalization_merge_commit"] = "0" * 40
        self.assert_code(bundle, "E-P22-SOURCE-PIN")


if __name__ == "__main__":
    unittest.main()
