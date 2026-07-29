from __future__ import annotations

import copy
import unittest
from pathlib import Path

from scripts import generate_phase24_offline_consequence_plan_review_readiness as gen
from scripts import validate_phase24_offline_consequence_plan_review_readiness as val


class Phase24ReviewReadinessTests(unittest.TestCase):
    def baseline(self):
        return gen.build()

    def assert_rejected(self, bundle, code: str) -> None:
        with self.assertRaises(val.ValidationError) as caught:
            val.validate_bundle(bundle)
        self.assertIn(code, str(caught.exception))

    def test_baseline_is_valid(self) -> None:
        bundle = self.baseline()
        val.validate_bundle(bundle)
        self.assertEqual(2, bundle[gen.REPORT_PATH]["summary"]["machine_ready_count"])
        self.assertEqual(0, bundle[gen.REPORT_PATH]["summary"]["human_ready_count"])
        self.assertEqual(8, bundle[gen.REPORT_PATH]["summary"]["unmet_human_gate_count"])

    def test_generated_files_are_exact(self) -> None:
        for path, value in self.baseline().items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(gen.render(value), path.read_text(encoding="utf-8"), path)

    def test_build_is_deterministic(self) -> None:
        first = self.baseline()
        second = self.baseline()
        self.assertEqual(
            {path: gen.render(value) for path, value in first.items()},
            {path: gen.render(value) for path, value in second.items()},
        )

    def test_recovery_registry_is_complete(self) -> None:
        recovery = self.baseline()[gen.RECOVERY_PATH]
        self.assertEqual(45, recovery["summary"]["scenario_count"])
        self.assertEqual(44, recovery["summary"]["rejected_count"])
        self.assertEqual(len(gen.SCENARIOS), len(recovery["scenarios"]))

    def test_human_criterion_cannot_be_satisfied(self) -> None:
        bundle = copy.deepcopy(self.baseline())
        bundle[gen.REPORT_PATH]["readiness_records"][0]["criteria"][4]["state"] = "satisfied"
        self.assert_rejected(bundle, "E-P24-CRITERIA")

    def test_reviewer_identity_cannot_be_invented(self) -> None:
        bundle = copy.deepcopy(self.baseline())
        bundle[gen.REPORT_PATH]["readiness_records"][0]["reviewer_identity"] = "synthetic-reviewer"
        self.assert_rejected(bundle, "E-P24-HUMAN-GATE")

    def test_competence_attestation_cannot_be_invented(self) -> None:
        bundle = copy.deepcopy(self.baseline())
        bundle[gen.REPORT_PATH]["readiness_records"][0]["competence_attestation"] = {"qualified": True}
        self.assert_rejected(bundle, "E-P24-HUMAN-GATE")

    def test_authorization_cannot_be_invented(self) -> None:
        bundle = copy.deepcopy(self.baseline())
        bundle[gen.REPORT_PATH]["readiness_records"][0]["authorization_record"] = {"authorized": True}
        self.assert_rejected(bundle, "E-P24-AUTHORIZATION")

    def test_review_request_cannot_be_dispatched(self) -> None:
        bundle = copy.deepcopy(self.baseline())
        bundle[gen.REPORT_PATH]["readiness_records"][0]["review_request_dispatched"] = True
        self.assert_rejected(bundle, "E-P24-DISPATCH")

    def test_review_cannot_start(self) -> None:
        bundle = copy.deepcopy(self.baseline())
        bundle[gen.REPORT_PATH]["readiness_records"][0]["review_start_permitted"] = True
        self.assert_rejected(bundle, "E-P24-EXECUTION")

    def test_review_cannot_complete(self) -> None:
        bundle = copy.deepcopy(self.baseline())
        bundle[gen.REPORT_PATH]["readiness_records"][1]["review_completed"] = True
        self.assert_rejected(bundle, "E-P24-EXECUTION")

    def test_outcome_cannot_be_selected(self) -> None:
        bundle = copy.deepcopy(self.baseline())
        bundle[gen.REPORT_PATH]["readiness_records"][1]["outcome_selected"] = True
        self.assert_rejected(bundle, "E-P24-OUTCOME")

    def test_effect_cannot_be_introduced(self) -> None:
        bundle = copy.deepcopy(self.baseline())
        bundle[gen.REPORT_PATH]["readiness_records"][0]["effective_hold"] = True
        self.assert_rejected(bundle, "E-P24-EFFECT")

    def test_atlas_call_cannot_be_enabled(self) -> None:
        bundle = copy.deepcopy(self.baseline())
        bundle[gen.REPORT_PATH]["authority"]["atlas_call_permitted"] = True
        self.assert_rejected(bundle, "E-P24-AUTHORITY")

    def test_external_network_cannot_be_required(self) -> None:
        bundle = copy.deepcopy(self.baseline())
        bundle[gen.REPORT_PATH]["authority"]["external_network_required"] = True
        self.assert_rejected(bundle, "E-P24-AUTHORITY")

    def test_live_activation_cannot_be_enabled(self) -> None:
        bundle = copy.deepcopy(self.baseline())
        bundle[gen.RELEASE_PATH]["live"] = True
        self.assert_rejected(bundle, "E-P24-LIVE-FROZEN")

    def test_ledger_chain_tamper_is_rejected(self) -> None:
        bundle = copy.deepcopy(self.baseline())
        bundle[gen.LEDGER_PATH]["entries"][1]["entry"]["previous_entry_sha256"] = "0" * 64
        self.assert_rejected(bundle, "E-P24-LEDGER")

    def test_release_artifact_tamper_is_rejected(self) -> None:
        bundle = copy.deepcopy(self.baseline())
        bundle[gen.RELEASE_PATH]["artifacts"]["report"]["sha256"] = "0" * 64
        self.assert_rejected(bundle, "E-P24-RELEASE")


if __name__ == "__main__":
    unittest.main()
