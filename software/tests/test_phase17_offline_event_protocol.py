from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from generate_phase17_offline_event_protocol import (  # noqa: E402
    build_acknowledgement_stream,
    build_chain,
    build_event_stream,
    build_recovery,
    check_outputs,
    sha256_document,
)
from validate_phase17_offline_event_protocol import (  # noqa: E402
    validate_acknowledgements,
    validate_chain,
    validate_event_stream,
    validate_recovery,
)


class Phase17OfflineEventProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.events = build_event_stream()
        self.acks = build_acknowledgement_stream(self.events)

    def test_committed_outputs_are_deterministic(self) -> None:
        self.assertEqual(check_outputs(), 0)

    def test_valid_event_and_acknowledgement_chain(self) -> None:
        validate_event_stream(self.events)
        validate_acknowledgements(self.acks, self.events)
        validate_chain(build_chain(self.events, self.acks), self.events, self.acks)
        validate_recovery(build_recovery(self.events, self.acks), self.events, self.acks)

    def test_live_event_stream_is_rejected(self) -> None:
        value = copy.deepcopy(self.events)
        value["live"] = True
        with self.assertRaisesRegex(ValueError, "E-P17-LIVE-FROZEN"):
            validate_event_stream(value)

    def test_status_inheritance_is_rejected(self) -> None:
        value = copy.deepcopy(self.events)
        value["events"][0]["event"]["knowledge_status"] = "deprecated"
        value["events"][0]["event_sha256"] = sha256_document(value["events"][0]["event"])
        with self.assertRaisesRegex(ValueError, "E-P17-STATUS-INHERITANCE"):
            validate_event_stream(value)

    def test_weakened_retraction_acknowledgement_is_rejected(self) -> None:
        value = copy.deepcopy(self.acks)
        value["acknowledgements"][1]["acknowledgement"]["required_action"] = "inspect"
        value["acknowledgements"][1]["acknowledgement_sha256"] = sha256_document(
            value["acknowledgements"][1]["acknowledgement"]
        )
        with self.assertRaisesRegex(ValueError, "E-P17-ACK-ACTION"):
            validate_acknowledgements(value, self.events)


if __name__ == "__main__":
    unittest.main()
