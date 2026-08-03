from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_STATE = REPO_ROOT / "PRODUCT_STATE.md"
ROOT_README = REPO_ROOT / "README.md"
PRODUCT_README = REPO_ROOT / "software" / "product_alpha" / "README.md"
OPTIONAL_PROTOCOL = REPO_ROOT / "software" / "product_alpha" / "PILOT.md"
LEGACY_REPORT = REPO_ROOT / "reports" / "product-alpha-0-1-pilot-summary.md"
REVIEW_JSON = REPO_ROOT / "reports" / "product-alpha-0-1-multi-perspective-review.json"
REVIEW_MD = REPO_ROOT / "reports" / "product-alpha-0-1-multi-perspective-review.md"

ACTIVE_DOCUMENTS = (PRODUCT_STATE, ROOT_README, PRODUCT_README, REVIEW_MD)
FORBIDDEN_ACTIVE_GATES = (
    "5–8 real learner",
    "5-8 real learner",
    "run and complete the learner pilot",
    "until real cohort evidence exists",
    "real cohort execution and human review",
)


class ProductAlphaStateAuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.review = json.loads(REVIEW_JSON.read_text(encoding="utf-8"))
        self.active = {path: path.read_text(encoding="utf-8") for path in ACTIVE_DOCUMENTS}
        self.optional_protocol = OPTIONAL_PROTOCOL.read_text(encoding="utf-8")
        self.legacy_report = LEGACY_REPORT.read_text(encoding="utf-8")

    def test_current_authority_is_internal_multi_perspective_review(self) -> None:
        product_state = self.active[PRODUCT_STATE]
        self.assertIn("last_reviewed: 2026-08-03", product_state)
        self.assertIn("internal multi-perspective review", product_state.lower())
        self.assertIn("advance-to-next-product-planning-review", product_state)
        self.assertEqual(
            self.review["decision"]["action"],
            "advance-to-next-product-planning-review",
        )
        self.assertEqual(len(self.review["perspectives"]), 8)

    def test_active_documents_remove_external_observation_as_gate(self) -> None:
        for path, text in self.active.items():
            lowered = text.lower()
            with self.subTest(path=path):
                for forbidden in FORBIDDEN_ACTIVE_GATES:
                    self.assertNotIn(forbidden.lower(), lowered)
                self.assertIn("empirical learning effectiveness", lowered)
                self.assertIn("product-market fit", lowered)

    def test_validator_command_is_visible(self) -> None:
        command = "software/product_alpha/evaluation/validate_internal_review.py check"
        for path in (PRODUCT_STATE, ROOT_README, PRODUCT_README, REVIEW_MD):
            with self.subTest(path=path):
                self.assertIn(command, self.active[path])

    def test_optional_protocol_is_not_authority(self) -> None:
        lowered = self.optional_protocol.lower()
        self.assertIn("optional research capability", lowered)
        self.assertIn("not a roadmap gate", lowered)
        self.assertIn("no minimum participant count", lowered)
        self.assertTrue(
            "does not authorize" in lowered or "do not authorize" in lowered
        )
        self.assertIn("outside the repository", lowered)

    def test_legacy_report_is_superseded(self) -> None:
        lowered = self.legacy_report.lower()
        self.assertIn("status: superseded", lowered)
        self.assertIn("no longer required for roadmap progress", lowered)
        self.assertIn("advance-to-next-product-planning-review", lowered)
        self.assertIn("## completion criteria", lowered)

    def test_review_preserves_claim_boundaries_and_residual_risks(self) -> None:
        non_claims = {
            item.lower()
            for item in self.review["claim_boundary"]["does_not_establish"]
        }
        for required in (
            "empirical learning effectiveness",
            "retention",
            "transfer",
            "product-market fit",
            "public production readiness",
        ):
            self.assertIn(required, non_claims)
        for perspective in self.review["perspectives"]:
            self.assertTrue(perspective["residual_risk"])
            self.assertTrue(perspective["next_action"])
            self.assertGreaterEqual(len(perspective["evidence"]), 2)

    def test_obsolete_manual_flow_is_not_reintroduced(self) -> None:
        for text in (*self.active.values(), self.optional_protocol, self.legacy_report):
            self.assertNotIn("verify_cohort.py \
  --input", text)
            self.assertNotIn("prepare_review.py \
  --input", text)


if __name__ == "__main__":
    unittest.main()
