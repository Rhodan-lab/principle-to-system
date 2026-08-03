from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
sys.path.insert(0, str(EVALUATION_DIR))

import workspace_status  # noqa: E402


class ProductAlphaWorkspaceStatusInvariantTests(unittest.TestCase):
    def test_cohort_completion_is_not_inferred_from_evidence_status(self) -> None:
        report: dict[str, object] = {
            "evidence_status": "ready-for-human-review",
            "cohort_complete": False,
        }

        self.assertFalse(
            workspace_status._verified_cohort_complete(report, "test report")
        )

    def test_verified_completion_requires_an_explicit_boolean(self) -> None:
        cases: tuple[dict[str, object], ...] = (
            {"evidence_status": "ready-for-human-review"},
            {
                "evidence_status": "ready-for-human-review",
                "cohort_complete": 1,
            },
            {
                "evidence_status": "ready-for-human-review",
                "cohort_complete": "true",
            },
        )
        for report in cases:
            with self.subTest(report=report):
                with self.assertRaisesRegex(
                    ValueError,
                    "cohort_complete must be boolean",
                ):
                    workspace_status._verified_cohort_complete(
                        report,
                        "test report",
                    )

    def test_verified_completion_preserves_true(self) -> None:
        report: dict[str, object] = {
            "evidence_status": "renamed-status-that-does-not-control-completion",
            "cohort_complete": True,
        }

        self.assertTrue(
            workspace_status._verified_cohort_complete(report, "test report")
        )


if __name__ == "__main__":
    unittest.main()
