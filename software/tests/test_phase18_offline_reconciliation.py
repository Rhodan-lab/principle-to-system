from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import generate_phase18_offline_reconciliation as reconciliation
import generate_phase18_release_record as release_record


class Phase18OfflineReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = reconciliation.load_json(reconciliation.EVENTS_PATH)
        cls.acks = reconciliation.load_json(reconciliation.ACKS_PATH)
        cls.chain = reconciliation.load_json(reconciliation.CHAIN_PATH)
        cls.matrix = reconciliation.load_json(reconciliation.PHASE16_MATRIX_PATH)
        cls.inventory = reconciliation.current_inventory()

    def test_generated_outputs_and_candidate_record_are_current(self) -> None:
        outputs = reconciliation.build_outputs()
        self.assertEqual(reconciliation.check_outputs(outputs), [])
        self.assertEqual(release_record.check(release_record.build_release()), [])

    def test_exact_streams_reconcile_without_mutation(self) -> None:
        report = reconciliation.reconcile(
            self.events, self.acks, self.chain, self.matrix, self.inventory
        )
        self.assertEqual(report["summary"]["decision"], "reconciled-no-mutation")
        self.assertEqual(report["summary"]["reconciled_count"], 2)
        self.assertEqual(report["summary"]["unacknowledged_count"], 0)
        self.assertEqual(report["summary"]["orphan_acknowledgement_count"], 0)
        self.assertFalse(report["live"])
        self.assertFalse(report["authority"]["automatic_status_change"])
        self.assertFalse(report["authority"]["automatic_release_action"])
        self.assertFalse(report["authority"]["repository_mutation"])
        self.assertEqual(report["authority"]["status_inheritance"], "prohibited")

    def test_current_artifact_revisions_are_pinned(self) -> None:
        self.assertEqual(set(self.inventory), {
            "principia:failure-pattern:feedback-instability",
            "principia:investigation:room-cooling",
            "principia:system-dossier:refrigerator",
        })
        for artifact in self.inventory.values():
            self.assertEqual(artifact["artifact_revision"], 1)
            self.assertEqual(artifact["pedagogical_status"], "reviewed")
            self.assertEqual(artifact["release_status"], "draft")

    def assert_reconciliation_error(self, candidate, code: str) -> None:
        with self.assertRaisesRegex(reconciliation.ReconciliationError, code):
            reconciliation.reconcile(*candidate)

    def test_missing_and_orphan_acknowledgements_are_detected(self) -> None:
        base = (
            self.events,
            self.acks,
            self.chain,
            self.matrix,
            self.inventory,
        )
        missing = copy.deepcopy(base)
        missing[1]["acknowledgements"].pop()
        self.assert_reconciliation_error(missing, "E-P18-COUNT-MISMATCH")

        orphan = copy.deepcopy(base)
        orphan[1]["acknowledgements"][1]["acknowledgement"]["event_id"] = "atlas:lifecycle-event:unknown:0002"
        self.assert_reconciliation_error(orphan, "E-P18-ACK-ORPHAN")

    def test_action_and_affected_set_divergence_are_detected(self) -> None:
        base = (
            self.events,
            self.acks,
            self.chain,
            self.matrix,
            self.inventory,
        )
        weakened = copy.deepcopy(base)
        ack = weakened[1]["acknowledgements"][1]["acknowledgement"]
        ack["required_action"] = "revalidate"
        weakened[1]["acknowledgements"][1]["acknowledgement_sha256"] = reconciliation.sha256_document(ack)
        self.assert_reconciliation_error(weakened, "E-P18-ACTION-MISMATCH")

        affected = copy.deepcopy(base)
        ack = affected[1]["acknowledgements"][0]["acknowledgement"]
        ack["affected_artifacts"].pop()
        affected[1]["acknowledgements"][0]["acknowledgement_sha256"] = reconciliation.sha256_document(ack)
        self.assert_reconciliation_error(affected, "E-P18-AFFECTED-SET")

    def test_current_inventory_divergence_is_detected(self) -> None:
        base = (
            self.events,
            self.acks,
            self.chain,
            self.matrix,
            self.inventory,
        )
        stale = copy.deepcopy(base)
        stale[4]["principia:failure-pattern:feedback-instability"]["artifact_revision"] = 2
        self.assert_reconciliation_error(stale, "E-P18-ARTIFACT-REVISION")

        missing = copy.deepcopy(base)
        del missing[4]["principia:investigation:room-cooling"]
        self.assert_reconciliation_error(missing, "E-P18-ARTIFACT-MISSING")

    def test_order_chain_authority_and_live_divergence_are_detected(self) -> None:
        base = (
            self.events,
            self.acks,
            self.chain,
            self.matrix,
            self.inventory,
        )
        reordered = copy.deepcopy(base)
        reordered[0]["events"].reverse()
        self.assert_reconciliation_error(reordered, "E-P18-EVENT-ORDER")

        head = copy.deepcopy(base)
        head[2]["event_head_sha256"] = "0" * 64
        self.assert_reconciliation_error(head, "E-P18-CHAIN-EVENT-HEAD")

        inherited = copy.deepcopy(base)
        inherited[1]["pedagogical_status_inheritance"] = "reviewed"
        self.assert_reconciliation_error(inherited, "E-P18-STATUS-INHERITANCE")

        automatic = copy.deepcopy(base)
        automatic[2]["authority"]["automatic_release_action"] = True
        self.assert_reconciliation_error(automatic, "E-P18-AUTOMATIC-MUTATION")

        live = copy.deepcopy(base)
        live[0]["live"] = True
        self.assert_reconciliation_error(live, "E-P18-LIVE-FROZEN")

    def test_recovery_matrix_has_expected_divergence_classes(self) -> None:
        recovery = reconciliation.load_json(reconciliation.RECOVERY_PATH)
        observed = {
            scenario["scenario_id"]: (
                scenario["accepted"], scenario["outcome"], scenario["error_code"]
            )
            for scenario in recovery["scenarios"]
        }
        self.assertEqual(observed["exact-reconciliation"], (True, "reconciled", None))
        self.assertEqual(observed["missing-acknowledgement"][2], "E-P18-COUNT-MISMATCH")
        self.assertEqual(observed["orphan-acknowledgement"][2], "E-P18-ACK-ORPHAN")
        self.assertEqual(observed["action-weakening"][2], "E-P18-ACTION-MISMATCH")
        self.assertEqual(observed["stale-artifact-revision"][2], "E-P18-ARTIFACT-REVISION")
        self.assertEqual(observed["event-chain-head-mismatch"][2], "E-P18-CHAIN-EVENT-HEAD")
        self.assertEqual(observed["status-inheritance-injection"][2], "E-P18-STATUS-INHERITANCE")
        self.assertEqual(observed["automatic-release-mutation"][2], "E-P18-AUTOMATIC-MUTATION")
        self.assertEqual(observed["live-activation"][2], "E-P18-LIVE-FROZEN")


if __name__ == "__main__":
    unittest.main()
