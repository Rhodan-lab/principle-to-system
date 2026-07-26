from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from generate_phase15_offline_pilot import (  # noqa: E402
    IMPACT_PATH,
    RECEIPT_PATH,
    generated_documents,
    load_json,
    render_json,
)
from validate_phase15_offline_pilot import (  # noqa: E402
    validate_lifecycle_matrix,
    validate_receipt,
)


class Phase15OfflinePilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receipt = load_json(RECEIPT_PATH)
        cls.matrix = load_json(IMPACT_PATH)

    def test_committed_outputs_match_deterministic_generator(self) -> None:
        generated = generated_documents()
        self.assertEqual(
            RECEIPT_PATH.read_text(encoding="utf-8"),
            render_json(generated[RECEIPT_PATH]),
        )
        self.assertEqual(
            IMPACT_PATH.read_text(encoding="utf-8"),
            render_json(generated[IMPACT_PATH]),
        )

    def test_valid_receipt_and_lifecycle_matrix(self) -> None:
        validate_receipt(self.receipt)
        validate_lifecycle_matrix(self.matrix)

    def test_live_activation_is_rejected(self) -> None:
        payload = copy.deepcopy(self.receipt)
        payload["live"] = True
        with self.assertRaisesRegex(ValueError, "E-PILOT-LIVE"):
            validate_receipt(payload)

    def test_status_inheritance_is_rejected(self) -> None:
        payload = copy.deepcopy(self.receipt)
        payload["result"]["release_status"] = "draft"
        with self.assertRaisesRegex(ValueError, "E-PILOT-STATUS"):
            validate_receipt(payload)

    def test_model_revision_rollback_is_rejected(self) -> None:
        payload = copy.deepcopy(self.receipt)
        for dependency in payload["result"]["dependencies"]:
            if dependency["id"] == "model:en:delayed-correction-recurrence":
                dependency["revision"] = 1
                dependency["key"] = "model:en:delayed-correction-recurrence@1"
        with self.assertRaisesRegex(ValueError, "E-PILOT-REVISION"):
            validate_receipt(payload)

    def test_unpinned_atlas_merge_is_rejected(self) -> None:
        payload = copy.deepcopy(self.receipt)
        payload["atlas_importer"]["merge_commit"] = "latest"
        with self.assertRaisesRegex(ValueError, "E-PILOT-ATLAS-PIN"):
            validate_receipt(payload)

    def test_automatic_status_mutation_is_rejected(self) -> None:
        payload = copy.deepcopy(self.receipt)
        payload["authority"]["automatic_status_change"] = True
        with self.assertRaisesRegex(ValueError, "E-PILOT-AUTHORITY"):
            validate_receipt(payload)


if __name__ == "__main__":
    unittest.main()
