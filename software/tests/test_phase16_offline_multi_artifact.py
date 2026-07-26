from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from generate_phase16_offline_multi_artifact import (  # noqa: E402
    BATCH_PATH,
    CHAIN_PATH,
    IMPACT_PATH,
    RECEIPT_PATH,
    RECOVERY_PATH,
    generated_documents,
    load_json,
    render_json,
    sha256_document,
)
from validate_phase16_offline_multi_artifact import (  # noqa: E402
    validate_batch_payload,
    validate_chain,
    validate_impact,
    validate_receipt_payload,
    validate_recovery,
)


class Phase16OfflineMultiArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.batch = load_json(BATCH_PATH)
        cls.receipt = load_json(RECEIPT_PATH)
        cls.chain = load_json(CHAIN_PATH)
        cls.impact = load_json(IMPACT_PATH)
        cls.recovery = load_json(RECOVERY_PATH)

    def test_committed_outputs_match_deterministic_generator(self) -> None:
        generated = generated_documents()
        for path in (BATCH_PATH, RECEIPT_PATH, CHAIN_PATH, IMPACT_PATH, RECOVERY_PATH):
            self.assertEqual(
                path.read_text(encoding="utf-8"),
                render_json(generated[path]),
            )

    def test_valid_batch_receipt_chain_impact_and_recovery(self) -> None:
        validate_batch_payload(self.batch)
        validate_receipt_payload(self.receipt, self.batch)
        validate_chain(self.chain, self.receipt)
        validate_impact(self.impact)
        validate_recovery(self.recovery, self.receipt)

    def test_batch_contains_three_distinct_artifacts(self) -> None:
        artifact_ids = [item["artifact_id"] for item in self.batch["inputs"]]
        self.assertEqual(
            artifact_ids,
            [
                "principia:failure-pattern:feedback-instability",
                "principia:investigation:room-cooling",
                "principia:system-dossier:refrigerator",
            ],
        )
        self.assertTrue(self.batch["atomic"])
        self.assertFalse(self.batch["live"])

    def test_receipt_chain_pins_exact_receipt_digest(self) -> None:
        digest = sha256_document(self.receipt)
        self.assertEqual(self.chain["head_sequence"], 1)
        self.assertEqual(self.chain["head_receipt_sha256"], digest)
        self.assertEqual(self.chain["entries"][0]["receipt_sha256"], digest)
        self.assertIsNone(self.chain["entries"][0]["previous_receipt_sha256"])

    def test_model_impact_reaches_only_feedback_failure_pattern(self) -> None:
        scenarios = {item["scenario_id"]: item for item in self.impact["scenarios"]}
        current = scenarios["model-current"]["external_dependents"]
        retracted = scenarios["model-retracted"]["external_dependents"]
        self.assertEqual(
            [item["artifact_id"] for item in current],
            ["principia:failure-pattern:feedback-instability"],
        )
        self.assertEqual(current[0]["effective_action"], "inspect")
        self.assertEqual(retracted[0]["effective_action"], "block-release")

    def test_claim_impact_reaches_all_three_artifacts(self) -> None:
        scenarios = {item["scenario_id"]: item for item in self.impact["scenarios"]}
        dependents = scenarios["claim-retracted"]["external_dependents"]
        self.assertEqual(len(dependents), 3)
        self.assertEqual(
            {item["effective_action"] for item in dependents},
            {"block-release"},
        )

    def test_recovery_matrix_has_version_and_integrity_failures(self) -> None:
        scenarios = {item["scenario_id"]: item for item in self.recovery["scenarios"]}
        self.assertEqual(scenarios["duplicate-replay"]["outcome"], "idempotent-noop")
        self.assertEqual(scenarios["valid-next-checkpoint"]["sequence"], 2)
        self.assertEqual(
            scenarios["wrong-predecessor"]["error_code"],
            "E-RECEIPT-PREVIOUS-DIGEST",
        )
        self.assertEqual(
            scenarios["partial-batch"]["error_code"],
            "E-BATCH-ATOMICITY",
        )
        self.assertEqual(
            scenarios["live-activation"]["error_code"],
            "E-BATCH-LIVE-FROZEN",
        )

    def test_partial_batch_is_rejected(self) -> None:
        payload = copy.deepcopy(self.batch)
        payload["inputs"].pop()
        with self.assertRaisesRegex(ValueError, "E-P16-BATCH-ATOMICITY"):
            validate_batch_payload(payload)

    def test_status_inheritance_is_rejected(self) -> None:
        payload = copy.deepcopy(self.batch)
        payload["release_status"] = "draft"
        with self.assertRaisesRegex(ValueError, "E-P16-BATCH-STATUS"):
            validate_batch_payload(payload)

    def test_live_receipt_is_rejected(self) -> None:
        payload = copy.deepcopy(self.receipt)
        payload["live"] = True
        with self.assertRaisesRegex(ValueError, "E-P16-RECEIPT-LIVE"):
            validate_receipt_payload(payload, self.batch)


if __name__ == "__main__":
    unittest.main()
