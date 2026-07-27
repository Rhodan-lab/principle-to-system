#!/usr/bin/env python3
"""Tests for the Phase 20 offline manual-policy-resolution candidate."""
from __future__ import annotations
import copy
import unittest
from scripts import generate_phase20_offline_manual_policy_resolution as gen
from scripts import validate_phase20_offline_manual_policy_resolution as val

class Phase20Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = gen.build()
        self.stream = copy.deepcopy(self.bundle[gen.RESOLUTIONS_PATH])

    def refresh(self, index: int) -> None:
        entry = self.stream["resolutions"][index]
        entry["resolution_sha256"] = gen.doc_sha(entry["resolution"])

    def assert_code(self, expected: str) -> None:
        with self.assertRaises(val.ValidationError) as caught:
            val.validate_stream(self.stream)
        self.assertEqual(str(caught.exception), expected)

    def test_committed_outputs_are_deterministic(self) -> None:
        self.assertEqual(gen.check(self.bundle), [])

    def test_complete_bundle_is_valid(self) -> None:
        val.validate_bundle(self.bundle)

    def test_accept_and_defer_have_no_effect(self) -> None:
        resolutions = self.stream["resolutions"]
        self.assertEqual(resolutions[0]["resolution"]["decision"], "accept")
        self.assertEqual(resolutions[1]["resolution"]["decision"], "defer")
        for entry in resolutions:
            record = entry["resolution"]
            self.assertFalse(record["operational_effect"])
            self.assertFalse(record["hold_effective"])
            self.assertFalse(record["status_change"])

    def test_rejects_live_activation(self) -> None:
        self.stream["live"] = True
        self.assert_code("E-P20-LIVE-FROZEN")

    def test_rejects_automatic_execution(self) -> None:
        self.stream["resolutions"][0]["resolution"]["operational_effect"] = True
        self.refresh(0)
        self.assert_code("E-P20-AUTOMATIC-EXECUTION")

    def test_rejects_effective_deferred_hold(self) -> None:
        self.stream["resolutions"][1]["resolution"]["hold_effective"] = True
        self.refresh(1)
        self.assert_code("E-P20-HOLD-EFFECTIVE")

    def test_rejects_status_inheritance(self) -> None:
        authority = self.stream["resolutions"][0]["resolution"]["authority"]
        authority["status_inheritance"] = "allowed"
        self.refresh(0)
        self.assert_code("E-P20-STATUS-INHERITANCE")

    def test_rejects_predecessor_drift(self) -> None:
        self.stream["resolutions"][1]["resolution"]["previous_resolution_sha256"] = "0" * 64
        self.refresh(1)
        self.assert_code("E-P20-PREVIOUS-DIGEST")

    def test_rejects_duplicate_resolution_id(self) -> None:
        first = self.stream["resolutions"][0]["resolution"]["resolution_id"]
        self.stream["resolutions"][1]["resolution"]["resolution_id"] = first
        self.refresh(1)
        self.assert_code("E-P20-DUPLICATE")

    def test_rejects_affected_set_drift(self) -> None:
        self.stream["resolutions"][0]["resolution"]["affected_artifacts"].pop()
        self.refresh(0)
        self.assert_code("E-P20-AFFECTED-SET")

    def test_rejects_source_pin_drift(self) -> None:
        self.stream["source"]["phase19_postmerge_sha256"] = "f" * 64
        self.assert_code("E-P20-SOURCE-PIN")

if __name__ == "__main__":
    unittest.main()
