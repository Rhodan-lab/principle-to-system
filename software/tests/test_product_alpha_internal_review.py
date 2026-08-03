from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REVIEW_JSON = REPO_ROOT / "reports" / "product-alpha-0-1-multi-perspective-review.json"
REVIEW_MD = REPO_ROOT / "reports" / "product-alpha-0-1-multi-perspective-review.md"
VALIDATOR = REPO_ROOT / "software" / "product_alpha" / "evaluation" / "validate_internal_review.py"

EXPECTED_PERSPECTIVES = {
    "product-strategy",
    "pedagogy",
    "scientific-integrity",
    "ux-accessibility",
    "privacy-security",
    "operational-reliability",
    "evidence-provenance",
    "maintainability-governance",
}


class ProductAlphaInternalReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.review = json.loads(REVIEW_JSON.read_text(encoding="utf-8"))
        self.markdown = REVIEW_MD.read_text(encoding="utf-8")

    def test_review_covers_all_required_perspectives(self) -> None:
        perspectives = self.review["perspectives"]
        self.assertEqual({item["id"] for item in perspectives}, EXPECTED_PERSPECTIVES)
        self.assertTrue(all(item["status"] in {"pass", "conditional-pass"} for item in perspectives))
        self.assertTrue(all(len(item["evidence"]) >= 2 for item in perspectives))
        self.assertTrue(all(item["residual_risk"] for item in perspectives))
        self.assertTrue(all(item["next_action"] for item in perspectives))

    def test_review_advances_planning_without_empirical_claims(self) -> None:
        self.assertEqual(
            self.review["decision"]["action"],
            "advance-to-next-product-planning-review",
        )
        non_claims = {item.lower() for item in self.review["claim_boundary"]["does_not_establish"]}
        for required in (
            "empirical learning effectiveness",
            "retention",
            "transfer",
            "product-market fit",
            "public production readiness",
        ):
            self.assertIn(required, non_claims)
            self.assertIn(required, self.markdown.lower())
        self.assertIn(
            "does not need external participant sessions as a prerequisite",
            self.markdown.lower(),
        )

    def test_validator_is_read_only_and_passes(self) -> None:
        before = {
            REVIEW_JSON: REVIEW_JSON.read_bytes(),
            REVIEW_MD: REVIEW_MD.read_bytes(),
        }
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "check"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("internal-multi-perspective-review-passed", completed.stdout)
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)


if __name__ == "__main__":
    unittest.main()
