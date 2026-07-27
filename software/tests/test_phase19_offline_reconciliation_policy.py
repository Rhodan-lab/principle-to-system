from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_phase19_offline_reconciliation_policy import (
    HOLD_PROPOSALS_PATH,
    LEDGER_PATH,
    RECOVERY_PATH,
    REVIEW_QUEUE_PATH,
    PolicyError,
    build_bundle,
    load_json,
    render_json,
    validate_policy_bundle,
)


class Phase19OfflineReconciliationPolicyTests(unittest.TestCase):
    def bundle(self):
        outputs = build_bundle()
        return (
            outputs[REVIEW_QUEUE_PATH],
            outputs[HOLD_PROPOSALS_PATH],
            outputs[LEDGER_PATH],
            outputs[RECOVERY_PATH],
        )

    def assert_code(self, expected, queue, holds, ledger, recovery):
        with self.assertRaises(PolicyError) as context:
            validate_policy_bundle(queue, holds, ledger, recovery)
        self.assertEqual(expected, context.exception.code)

    def test_generated_outputs_are_deterministic(self):
        first = build_bundle()
        second = build_bundle()
        self.assertEqual(
            {path: render_json(value) for path, value in first.items()},
            {path: render_json(value) for path, value in second.items()},
        )

    def test_committed_bundle_is_valid(self):
        queue = load_json(REVIEW_QUEUE_PATH)
        holds = load_json(HOLD_PROPOSALS_PATH)
        ledger = load_json(LEDGER_PATH)
        recovery = load_json(RECOVERY_PATH)
        validate_policy_bundle(queue, holds, ledger, recovery)
        self.assertEqual(14, recovery["summary"]["scenario_count"])
        self.assertEqual("proposals-recorded-no-mutation", ledger["decision"])

    def test_live_activation_is_rejected(self):
        queue, holds, ledger, recovery = self.bundle()
        queue["live"] = True
        self.assert_code("E-P19-LIVE-FROZEN", queue, holds, ledger, recovery)

    def test_revalidate_cannot_be_weakened(self):
        queue, holds, ledger, recovery = self.bundle()
        queue["items"][0]["policy_action"] = "inspect"
        self.assert_code("E-P19-ACTION-MAPPING", queue, holds, ledger, recovery)

    def test_release_hold_cannot_become_effective(self):
        queue, holds, ledger, recovery = self.bundle()
        holds["items"][0]["effective"] = True
        self.assert_code("E-P19-HOLD-EFFECTIVE", queue, holds, ledger, recovery)

    def test_affected_artifact_set_cannot_drift(self):
        queue, holds, ledger, recovery = self.bundle()
        queue["items"][0]["affected_artifacts"].pop()
        self.assert_code("E-P19-AFFECTED-SET", queue, holds, ledger, recovery)

    def test_status_inheritance_is_rejected(self):
        queue, holds, ledger, recovery = self.bundle()
        queue["atlas_status_inheritance"] = "deprecated"
        self.assert_code("E-P19-STATUS-INHERITANCE", queue, holds, ledger, recovery)

    def test_ledger_predecessor_drift_is_rejected(self):
        queue, holds, ledger, recovery = self.bundle()
        ledger["entries"][1]["entry"]["previous_entry_sha256"] = None
        self.assert_code("E-P19-LEDGER-ORDER", queue, holds, ledger, recovery)


if __name__ == "__main__":
    unittest.main()
