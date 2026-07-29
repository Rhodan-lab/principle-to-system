from __future__ import annotations

import copy
import unittest

from scripts import generate_phase26_offline_consequence_plan_review_request_packet_assurance as gen
from scripts import validate_phase26_offline_consequence_plan_review_request_packet_assurance as val


class Phase26PacketAssuranceTests(unittest.TestCase):
    def build(self):
        return gen.build()

    def test_baseline_is_valid(self) -> None:
        val.validate_bundle(self.build())

    def test_build_is_deterministic(self) -> None:
        first = self.build()
        second = self.build()
        for path in first:
            self.assertEqual(gen.render(first[path]), gen.render(second[path]))

    def test_source_identity_is_pinned(self) -> None:
        bundle = self.build()
        changed = copy.deepcopy(bundle)
        changed[gen.RELEASE_PATH]["source_phase25"]["phase25_candidate_sha256"] = "0" * 64
        with self.assertRaisesRegex(val.ValidationError, "E-P26-SOURCE-PIN"):
            val.validate_bundle(changed)

    def test_missing_assurance_is_rejected(self) -> None:
        bundle = self.build()
        changed = copy.deepcopy(bundle)
        changed[gen.REPORT_PATH]["assurances"].pop()
        with self.assertRaisesRegex(val.ValidationError, "E-P26-MISSING"):
            val.validate_bundle(changed)

    def test_duplicate_assurance_is_rejected(self) -> None:
        bundle = self.build()
        changed = copy.deepcopy(bundle)
        changed[gen.REPORT_PATH]["assurances"][1]["packet_assurance_id"] = changed[gen.REPORT_PATH]["assurances"][0]["packet_assurance_id"]
        with self.assertRaisesRegex(val.ValidationError, "E-P26-DUPLICATE"):
            val.validate_bundle(changed)

    def test_packet_digest_drift_is_rejected(self) -> None:
        bundle = self.build()
        changed = copy.deepcopy(bundle)
        changed[gen.REPORT_PATH]["assurances"][0]["packet_record_sha256"] = "f" * 64
        with self.assertRaisesRegex(val.ValidationError, "E-P26-PACKET-BINDING"):
            val.validate_bundle(changed)

    def test_failed_assurance_check_is_rejected(self) -> None:
        bundle = self.build()
        changed = copy.deepcopy(bundle)
        changed[gen.REPORT_PATH]["assurances"][0]["assurance_checks"]["dispatch_disabled"] = False
        with self.assertRaisesRegex(val.ValidationError, "E-P26-ASSURANCE"):
            val.validate_bundle(changed)

    def test_human_gate_cannot_be_satisfied(self) -> None:
        bundle = self.build()
        changed = copy.deepcopy(bundle)
        changed[gen.REPORT_PATH]["assurances"][0]["human_gate_satisfied_count"] = 1
        with self.assertRaisesRegex(val.ValidationError, "E-P26-HUMAN-GATE"):
            val.validate_bundle(changed)

    def test_response_cannot_be_submitted(self) -> None:
        bundle = self.build()
        changed = copy.deepcopy(bundle)
        changed[gen.REPORT_PATH]["assurances"][0]["response_template_submitted"] = True
        with self.assertRaisesRegex(val.ValidationError, "E-P26-RESPONSE"):
            val.validate_bundle(changed)

    def test_dispatch_cannot_be_enabled(self) -> None:
        bundle = self.build()
        changed = copy.deepcopy(bundle)
        changed[gen.REPORT_PATH]["assurances"][0]["dispatch_permitted"] = True
        with self.assertRaisesRegex(val.ValidationError, "E-P26-DISPATCH"):
            val.validate_bundle(changed)

    def test_review_cannot_start(self) -> None:
        bundle = self.build()
        changed = copy.deepcopy(bundle)
        changed[gen.REPORT_PATH]["assurances"][0]["review_started"] = True
        with self.assertRaisesRegex(val.ValidationError, "E-P26-EXECUTION"):
            val.validate_bundle(changed)

    def test_authorization_cannot_be_invented(self) -> None:
        bundle = self.build()
        changed = copy.deepcopy(bundle)
        changed[gen.REPORT_PATH]["assurances"][0]["human_authorization_claimed"] = True
        with self.assertRaisesRegex(val.ValidationError, "E-P26-AUTHORIZATION"):
            val.validate_bundle(changed)

    def test_ledger_tamper_is_rejected(self) -> None:
        bundle = self.build()
        changed = copy.deepcopy(bundle)
        changed[gen.LEDGER_PATH]["entries"][1]["entry"]["previous_entry_sha256"] = None
        with self.assertRaisesRegex(val.ValidationError, "E-P26-LEDGER"):
            val.validate_bundle(changed)

    def test_atlas_call_cannot_be_enabled(self) -> None:
        bundle = self.build()
        changed = copy.deepcopy(bundle)
        changed[gen.RELEASE_PATH]["authority"]["atlas_call_permitted"] = True
        with self.assertRaisesRegex(val.ValidationError, "E-P26-AUTHORITY"):
            val.validate_bundle(changed)

    def test_live_activation_is_rejected(self) -> None:
        bundle = self.build()
        changed = copy.deepcopy(bundle)
        changed[gen.RELEASE_PATH]["live"] = True
        with self.assertRaisesRegex(val.ValidationError, "E-P26-LIVE-FROZEN"):
            val.validate_bundle(changed)


if __name__ == "__main__":
    unittest.main()
