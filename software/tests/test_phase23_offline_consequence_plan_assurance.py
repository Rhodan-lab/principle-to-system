"""Negative and baseline tests for Phase 23 consequence-plan assurance."""
from __future__ import annotations

import copy
import unittest

from scripts import generate_phase23_offline_consequence_plan_assurance as gen
from scripts import validate_phase23_offline_consequence_plan_assurance as val


class Phase23AssuranceTests(unittest.TestCase):
    def bundle(self):
        return copy.deepcopy(gen.build())

    def assert_code(self, bundle, code: str) -> None:
        with self.assertRaisesRegex(val.ValidationError, code):
            val.validate_bundle(bundle)

    def test_baseline(self):
        val.validate_bundle(self.bundle())

    def test_missing_assurance(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"].pop()
        self.assert_code(bundle, "E-P23-MISSING")

    def test_orphan_assurance(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"].append(
            copy.deepcopy(bundle[gen.REPORT_PATH]["assessments"][0])
        )
        self.assert_code(bundle, "E-P23-ORPHAN")

    def test_duplicate_assurance_id(self):
        bundle = self.bundle()
        assessments = bundle[gen.REPORT_PATH]["assessments"]
        assessments[1]["assurance_id"] = assessments[0]["assurance_id"]
        self.assert_code(bundle, "E-P23-DUPLICATE")

    def test_sequence_drift(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"][1]["sequence"] = 3
        self.assert_code(bundle, "E-P23-SEQUENCE")

    def test_plan_id_drift(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"][0]["plan_id"] = "unknown"
        self.assert_code(bundle, "E-P23-PLAN-ID")

    def test_plan_digest_drift(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"][0]["plan_sha256"] = "0" * 64
        self.assert_code(bundle, "E-P23-PLAN-DIGEST")

    def test_source_ledger_drift(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"][0]["source_ledger_entry_sha256"] = "0" * 64
        self.assert_code(bundle, "E-P23-SOURCE-LEDGER")

    def test_source_proposal_drift(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"][0]["source_proposal_id"] = "unknown"
        self.assert_code(bundle, "E-P23-SOURCE-BINDING")

    def test_source_resolution_drift(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"][0]["source_resolution_id"] = "unknown"
        self.assert_code(bundle, "E-P23-SOURCE-BINDING")

    def test_affected_set_drift(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"][0]["affected_artifacts"].pop()
        self.assert_code(bundle, "E-P23-AFFECTED-SET")

    def test_step_count_drift(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"][0]["step_count"] = 2
        self.assert_code(bundle, "E-P23-STEPS")

    def test_execution_permitted(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"][0]["execution_permitted"] = True
        self.assert_code(bundle, "E-P23-EXECUTION")

    def test_effective_hold(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"][1]["effective_hold"] = True
        self.assert_code(bundle, "E-P23-EFFECT")

    def test_operational_effect(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"][0]["operational_effect"] = True
        self.assert_code(bundle, "E-P23-EFFECT")

    def test_status_change(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"][0]["status_change"] = True
        self.assert_code(bundle, "E-P23-EFFECT")

    def test_real_authorization_claimed(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["assessments"][0]["real_authorization_claimed"] = True
        self.assert_code(bundle, "E-P23-AUTHORIZATION")

    def test_live_activation(self):
        bundle = self.bundle()
        bundle[gen.REPORT_PATH]["live"] = True
        self.assert_code(bundle, "E-P23-LIVE-FROZEN")


if __name__ == "__main__":
    unittest.main()
