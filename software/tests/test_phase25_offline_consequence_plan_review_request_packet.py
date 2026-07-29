from __future__ import annotations

import copy
import unittest

from scripts.generate_phase25_offline_consequence_plan_review_request_packet import (
    CHECKPOINT_PATH,
    LEDGER_PATH,
    RECOVERY_PATH,
    RELEASE_PATH,
    REPORT_PATH,
    build,
)
from scripts.validate_phase25_offline_consequence_plan_review_request_packet import validate_bundle


class Phase25ReviewRequestPacketTests(unittest.TestCase):
    def bundle(self):
        return copy.deepcopy(build())

    def assert_code(self, bundle, code: str):
        errors = validate_bundle(bundle)
        self.assertTrue(any(item.startswith(code + ":") for item in errors), errors)

    def test_baseline_is_valid(self):
        self.assertEqual(validate_bundle(self.bundle()), [])

    def test_missing_packet_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"].pop()
        self.assert_code(bundle, "E-P25-MISSING")

    def test_duplicate_packet_identity_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][1]["packet_id"] = bundle[REPORT_PATH]["packets"][0]["packet_id"]
        self.assert_code(bundle, "E-P25-DUPLICATE")

    def test_packet_sequence_drift_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][1]["sequence"] = 3
        self.assert_code(bundle, "E-P25-SEQUENCE")

    def test_readiness_digest_drift_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][0]["readiness_record_sha256"] = "0" * 64
        self.assert_code(bundle, "E-P25-READINESS")

    def test_affected_set_drift_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][0]["affected_artifacts"].pop()
        self.assert_code(bundle, "E-P25-AFFECTED-SET")

    def test_packet_section_drift_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][0]["packet_sections"].pop()
        self.assert_code(bundle, "E-P25-SECTION")

    def test_question_response_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][0]["questions"][0]["response"] = "answer"
        self.assert_code(bundle, "E-P25-RESPONSE")

    def test_satisfied_human_gate_is_rejected(self):
        bundle = self.bundle()
        gate = bundle[REPORT_PATH]["packets"][0]["human_gates"][0]
        gate["state"] = "satisfied"
        gate["evidence_ref"] = "fabricated"
        self.assert_code(bundle, "E-P25-HUMAN-GATE")

    def test_reviewer_identity_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][0]["reviewer_identity"] = "invented-reviewer"
        self.assert_code(bundle, "E-P25-HUMAN-GATE")

    def test_recipient_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][0]["dispatch"]["recipient"] = "someone"
        self.assert_code(bundle, "E-P25-DISPATCH")

    def test_dispatch_authorization_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][0]["dispatch"]["authorized"] = True
        self.assert_code(bundle, "E-P25-DISPATCH")

    def test_reviewer_contact_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][0]["reviewer_contact_permitted"] = True
        self.assert_code(bundle, "E-P25-DISPATCH")

    def test_submitted_response_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][0]["response_template"]["submitted"] = True
        self.assert_code(bundle, "E-P25-RESPONSE")

    def test_review_recommendation_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][1]["response_template"]["review_recommendation"] = "release"
        self.assert_code(bundle, "E-P25-OUTCOME")

    def test_review_start_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][0]["review_started"] = True
        self.assert_code(bundle, "E-P25-EXECUTION")

    def test_content_effect_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][0]["content_change_proposed"] = True
        self.assert_code(bundle, "E-P25-EFFECT")

    def test_authorization_claim_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["packets"][0]["real_authorization_claimed"] = True
        self.assert_code(bundle, "E-P25-AUTHORIZATION")

    def test_network_authority_is_rejected(self):
        bundle = self.bundle()
        bundle[REPORT_PATH]["authority"]["external_network_required"] = True
        self.assert_code(bundle, "E-P25-AUTHORITY")

    def test_ledger_digest_drift_is_rejected(self):
        bundle = self.bundle()
        bundle[LEDGER_PATH]["entries"][0]["entry"]["packet_record_sha256"] = "0" * 64
        self.assert_code(bundle, "E-P25-LEDGER")

    def test_checkpoint_binding_drift_is_rejected(self):
        bundle = self.bundle()
        bundle[CHECKPOINT_PATH]["packet_report_sha256"] = "0" * 64
        self.assert_code(bundle, "E-P25-CHECKPOINT")

    def test_recovery_matrix_drift_is_rejected(self):
        bundle = self.bundle()
        bundle[RECOVERY_PATH]["scenarios"].pop()
        self.assert_code(bundle, "E-P25-RECOVERY")

    def test_release_next_gate_drift_is_rejected(self):
        bundle = self.bundle()
        bundle[RELEASE_PATH]["next_gate"] = "live-review"
        self.assert_code(bundle, "E-P25-RELEASE")


if __name__ == "__main__":
    unittest.main()
