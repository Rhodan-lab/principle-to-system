from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_STATE = REPO_ROOT / "PRODUCT_STATE.md"
PILOT_REPORT = REPO_ROOT / "reports" / "product-alpha-0-1-pilot-summary.md"

REQUIRED_WORKFLOW_COMMANDS = (
    "software/product_alpha/prepare_pilot.py",
    "software/product_alpha/launch_workspace.py",
    "software/product_alpha/evaluation/workspace_status.py",
    "software/product_alpha/evaluation/assemble_workspace.py check",
    "software/product_alpha/evaluation/review_workspace.py check",
    "software/product_alpha/evaluation/record_decision.py check",
    "software/product_alpha/evaluation/record_decision.py verify",
)


class ProductAlphaStateAuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.product_state = PRODUCT_STATE.read_text(encoding="utf-8")
        self.pilot_report = PILOT_REPORT.read_text(encoding="utf-8")

    def test_authority_documents_use_current_review_date(self) -> None:
        for text in (self.product_state, self.pilot_report):
            self.assertIn("last_reviewed: 2026-08-02", text)
            self.assertIn("real learner", text.lower())
            self.assertIn("not reportable", text.lower())

    def test_authority_documents_name_the_supported_workspace_chain(self) -> None:
        for command in REQUIRED_WORKFLOW_COMMANDS:
            with self.subTest(command=command):
                self.assertIn(command, self.product_state)
                self.assertIn(command, self.pilot_report)

    def test_product_state_tracks_current_merged_operational_boundary(self) -> None:
        for pull_request in range(118, 129):
            with self.subTest(pull_request=pull_request):
                self.assertIn(f"PR #{pull_request}", self.product_state)
        self.assertIn("decision receipt", self.product_state.lower())
        self.assertIn("read-only workspace stage", self.product_state.lower())

    def test_reports_preserve_private_evidence_and_no_claim_boundaries(self) -> None:
        for text in (self.product_state, self.pilot_report):
            lowered = text.lower()
            self.assertIn("not be committed", lowered)
            self.assertIn("may not yet claim", lowered)
            self.assertIn("learning effectiveness", lowered)
            self.assertIn("second route", lowered)

        product_state = self.product_state.lower()
        self.assertTrue(
            "no automatic repository mutation" in product_state
            or "does not automatically mutate the repository" in product_state
            or "none of these commands automatically mutates the repository"
            in product_state,
            "product state must deny automatic repository mutation",
        )
        pilot_report = self.pilot_report.lower()
        self.assertIn("separately reviewed", pilot_report)
        self.assertIn("separately de-identified", pilot_report)

    def test_obsolete_manual_flow_is_not_the_active_workflow(self) -> None:
        for text in (self.product_state, self.pilot_report):
            self.assertNotIn("run_pilot.py --open", text)
            self.assertNotIn("verify_cohort.py \\\n  --input", text)
            self.assertNotIn("prepare_review.py \\\n  --input", text)


if __name__ == "__main__":
    unittest.main()
