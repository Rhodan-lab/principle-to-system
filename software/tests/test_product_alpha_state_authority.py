from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_STATE = REPO_ROOT / "PRODUCT_STATE.md"
PILOT_REPORT = REPO_ROOT / "reports" / "product-alpha-0-1-pilot-summary.md"
PRODUCT_README = REPO_ROOT / "software" / "product_alpha" / "README.md"
PILOT_PROTOCOL = REPO_ROOT / "software" / "product_alpha" / "PILOT.md"

REQUIRED_WORKFLOW_COMMANDS = (
    "software/product_alpha/prepare_pilot.py",
    "software/product_alpha/launch_workspace.py",
    "software/product_alpha/evaluation/workspace_status.py",
    "software/product_alpha/evaluation/assemble_workspace.py check",
    "software/product_alpha/evaluation/review_workspace.py check",
    "software/product_alpha/evaluation/record_decision.py check",
    "software/product_alpha/evaluation/record_decision.py verify",
    "software/product_alpha/evaluation/prepare_handoff.py check",
    "software/product_alpha/evaluation/prepare_handoff.py verify",
)

HANDOFF_EXCLUSION_ALIASES = (
    ("raw sessions",),
    ("session identifiers", "session ids"),
    ("facilitator notes",),
    ("custom confusion",),
    ("reviewer identity",),
    ("review date",),
    ("private rationale",),
    ("checkpoint text",),
    ("local workspace paths", "local paths"),
)


class ProductAlphaStateAuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.product_state = PRODUCT_STATE.read_text(encoding="utf-8")
        self.pilot_report = PILOT_REPORT.read_text(encoding="utf-8")
        self.product_readme = PRODUCT_README.read_text(encoding="utf-8")
        self.pilot_protocol = PILOT_PROTOCOL.read_text(encoding="utf-8")
        self.authority_documents = (self.product_state, self.pilot_report)
        self.operator_documents = (self.product_readme, self.pilot_protocol)
        self.all_documents = self.authority_documents + self.operator_documents

    def test_authority_documents_use_current_review_date(self) -> None:
        for text in self.authority_documents:
            self.assertIn("last_reviewed: 2026-08-02", text)
            self.assertIn("real learner", text.lower())
            self.assertIn("not reportable", text.lower())

    def test_all_documents_name_the_supported_workspace_chain(self) -> None:
        for command in REQUIRED_WORKFLOW_COMMANDS:
            for text in self.all_documents:
                with self.subTest(command=command, document=text[:40]):
                    self.assertIn(command, text)

    def test_product_state_tracks_current_merged_operational_boundary(self) -> None:
        for pull_request in range(118, 131):
            with self.subTest(pull_request=pull_request):
                self.assertIn(f"PR #{pull_request}", self.product_state)
        lowered = self.product_state.lower()
        self.assertIn("decision receipt", lowered)
        self.assertIn("read-only workspace stage", lowered)
        self.assertIn("de-identified handoff", lowered)

    def test_handoff_privacy_exclusions_are_operator_visible(self) -> None:
        for text in self.all_documents:
            lowered = text.lower()
            self.assertIn("handoff", lowered)
            self.assertIn("outside the repository", lowered)
            for aliases in HANDOFF_EXCLUSION_ALIASES:
                with self.subTest(aliases=aliases, document=text[:40]):
                    self.assertTrue(
                        any(alias in lowered for alias in aliases),
                        f"missing handoff exclusion: {aliases}",
                    )

    def test_reports_preserve_private_evidence_and_no_claim_boundaries(self) -> None:
        for text in self.authority_documents:
            lowered = text.lower()
            self.assertIn("not be committed", lowered)
            self.assertIn("may not yet claim", lowered)
            self.assertIn("learning effectiveness", lowered)
            self.assertTrue(
                "second route" in lowered
                or "second-route" in lowered
                or "another route" in lowered,
                "authority document must deny an unreviewed additional route",
            )

        product_state = self.product_state.lower()
        self.assertTrue(
            "no automatic repository mutation" in product_state
            or "does not automatically mutate the repository" in product_state
            or "none of these commands automatically mutates the repository"
            in product_state,
            "product state must deny automatic repository mutation",
        )

        pilot_report = self.pilot_report.lower()
        self.assertIn("## completion criteria", pilot_report)
        completion = pilot_report.split("## completion criteria", 1)[1]
        for required in (
            "handoff",
            "separately",
            "de-identified",
            "reviewed",
            "merged",
        ):
            with self.subTest(required=required):
                self.assertIn(required, completion)

    def test_operator_documents_preserve_no_write_and_no_authorization_boundaries(self) -> None:
        for text in self.operator_documents:
            lowered = text.lower()
            self.assertIn("does not authorize", lowered)
            self.assertIn("separate", lowered)
            self.assertIn("human", lowered)
            self.assertIn("pull request", lowered)
            self.assertIn("learning effectiveness", lowered)

    def test_obsolete_manual_flow_is_not_the_active_workflow(self) -> None:
        for text in self.all_documents:
            self.assertNotIn("run_pilot.py --open", text)
            self.assertNotIn("verify_cohort.py \\\n  --input", text)
            self.assertNotIn("prepare_review.py \\\n  --input", text)


if __name__ == "__main__":
    unittest.main()
