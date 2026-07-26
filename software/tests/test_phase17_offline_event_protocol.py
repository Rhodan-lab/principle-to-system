from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import generate_phase17_offline_event_protocol as protocol


class Phase17OfflineEventProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.chain = protocol.load_json(protocol.SOURCE_CHAIN_PATH)
        cls.matrix = protocol.load_json(protocol.SOURCE_MATRIX_PATH)
        cls.release = protocol.load_json(protocol.PHASE16_RELEASE_PATH)
        cls.event = protocol.load_json(protocol.EVENT_PATH)
        cls.ack = protocol.load_json(protocol.ACK_PATH)
        cls.log = protocol.load_json(protocol.LOG_PATH)
        cls.recovery = protocol.load_json(protocol.RECOVERY_PATH)

    def test_committed_outputs_match_deterministic_generator(self) -> None:
        outputs = protocol.build_outputs()
        self.assertEqual(protocol.check_outputs(outputs), [])

    def test_event_ack_and_log_are_digest_bound(self) -> None:
        event_sha = protocol.sha256_document(self.event)
        ack_sha = protocol.sha256_document(self.ack)
        self.assertEqual(self.ack["event_sha256"], event_sha)
        self.assertEqual(self.log["head_event_sha256"], event_sha)
        self.assertEqual(self.log["head_ack_sha256"], ack_sha)
        self.assertEqual(self.log["entries"][0]["event_sha256"], event_sha)
        self.assertEqual(self.log["entries"][0]["ack_sha256"], ack_sha)
        protocol.validate_ack(self.ack, self.event)

    def test_exact_duplicate_replay_is_idempotent(self) -> None:
        result = protocol.validate_event_candidate(
            self.event, self.log, self.chain, self.matrix
        )
        self.assertEqual(result, "idempotent-noop")

    def test_same_sequence_with_different_digest_is_equivocation(self) -> None:
        candidate = copy.deepcopy(self.event)
        candidate["atlas_entity"]["staleness"] = "review-required"
        with self.assertRaisesRegex(protocol.ProtocolError, "E-P17-EQUIVOCATION"):
            protocol.validate_event_candidate(candidate, self.log, self.chain, self.matrix)

    def test_valid_next_event_requires_exact_predecessor(self) -> None:
        scenario = protocol.scenario_by_id(
            self.matrix, "oscillation-confirmed-stale"
        )
        candidate = protocol.event_from_scenario(
            scenario,
            sequence=2,
            previous_event_sha256=self.log["head_event_sha256"],
            chain=self.chain,
            release=self.release,
        )
        self.assertEqual(
            protocol.validate_event_candidate(
                candidate, self.log, self.chain, self.matrix
            ),
            "accept",
        )
        candidate["previous_event_sha256"] = "0" * 64
        with self.assertRaisesRegex(protocol.ProtocolError, "E-P17-PREDECESSOR"):
            protocol.validate_event_candidate(candidate, self.log, self.chain, self.matrix)

    def test_status_inheritance_is_rejected(self) -> None:
        scenario = protocol.scenario_by_id(
            self.matrix, "oscillation-confirmed-stale"
        )
        candidate = protocol.event_from_scenario(
            scenario,
            sequence=2,
            previous_event_sha256=self.log["head_event_sha256"],
            chain=self.chain,
            release=self.release,
        )
        candidate["affected_principia_artifacts"][0]["release_status"] = "released"
        with self.assertRaisesRegex(
            protocol.ProtocolError, "E-P17-STATUS-INHERITANCE"
        ):
            protocol.validate_event_candidate(candidate, self.log, self.chain, self.matrix)

    def test_live_and_automatic_mutation_are_rejected(self) -> None:
        scenario = protocol.scenario_by_id(
            self.matrix, "oscillation-confirmed-stale"
        )
        candidate = protocol.event_from_scenario(
            scenario,
            sequence=2,
            previous_event_sha256=self.log["head_event_sha256"],
            chain=self.chain,
            release=self.release,
        )
        live = copy.deepcopy(candidate)
        live["live"] = True
        with self.assertRaisesRegex(protocol.ProtocolError, "E-P17-LIVE-FROZEN"):
            protocol.validate_event_candidate(live, self.log, self.chain, self.matrix)
        automatic = copy.deepcopy(candidate)
        automatic["authority"]["automatic_release_action"] = True
        with self.assertRaisesRegex(
            protocol.ProtocolError, "E-P17-AUTOMATIC-MUTATION"
        ):
            protocol.validate_event_candidate(
                automatic, self.log, self.chain, self.matrix
            )

    def test_wrong_ack_digest_is_rejected(self) -> None:
        ack = copy.deepcopy(self.ack)
        ack["event_sha256"] = "f" * 64
        with self.assertRaisesRegex(protocol.ProtocolError, "E-P17-ACK-DIGEST"):
            protocol.validate_ack(ack, self.event)

    def test_recovery_matrix_contains_canonical_outcomes(self) -> None:
        observed = {
            item["scenario_id"]: (
                item["accepted"],
                item["result"],
                item["error_code"],
            )
            for item in self.recovery["scenarios"]
        }
        expected = {
            "duplicate-exact-replay": (True, "idempotent-noop", None),
            "same-sequence-different-digest": (False, "reject", "E-P17-EQUIVOCATION"),
            "stale-sequence": (False, "reject", "E-P17-STALE-SEQUENCE"),
            "skipped-sequence": (False, "reject", "E-P17-SKIPPED-SEQUENCE"),
            "wrong-predecessor": (False, "reject", "E-P17-PREDECESSOR"),
            "wrong-receipt-chain-head": (False, "reject", "E-P17-RECEIPT-HEAD"),
            "unknown-entity-state": (False, "reject", "E-P17-ENTITY-STATE"),
            "affected-set-mismatch": (False, "reject", "E-P17-AFFECTED-SET"),
            "status-inheritance-injection": (False, "reject", "E-P17-STATUS-INHERITANCE"),
            "automatic-release-mutation": (False, "reject", "E-P17-AUTOMATIC-MUTATION"),
            "live-activation": (False, "reject", "E-P17-LIVE-FROZEN"),
            "valid-next-event": (True, "accept", None),
            "ack-event-digest-mismatch": (False, "reject", "E-P17-ACK-DIGEST"),
        }
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
