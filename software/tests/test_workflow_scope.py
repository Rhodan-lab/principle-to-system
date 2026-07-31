#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import apply_ci_product_alpha_scope as scope  # noqa: E402


class WorkflowScopeTests(unittest.TestCase):
    def test_inline_events_are_expanded_and_scoped(self) -> None:
        original = "name: test\n\non: [pull_request, push]\n\njobs: {}\n"
        updated = scope.transform_workflow(original, "legacy.yml")
        self.assertIn("pull_request:\n    paths-ignore:", updated)
        self.assertIn("push:\n    paths-ignore:", updated)
        self.assertFalse(
            scope.event_runs_for_paths(
                updated, "pull_request", scope.PRODUCT_FIXTURE_PATHS
            )
        )

    def test_existing_positive_paths_remain_unchanged(self) -> None:
        original = """name: test

on:
  push:
    paths:
      - 'scripts/**'
  pull_request:
    branches:
      - main
  workflow_dispatch:

jobs: {}
"""
        updated = scope.transform_workflow(original, "legacy.yml")
        self.assertEqual(updated.count("paths-ignore:"), 1)
        self.assertIn("push:\n    paths:\n      - 'scripts/**'", updated)
        self.assertIn(
            "pull_request:\n    branches:\n      - main\n    paths-ignore:", updated
        )
        self.assertEqual(scope.transform_workflow(updated, "legacy.yml"), updated)

    def test_mixed_change_keeps_legacy_event_eligible(self) -> None:
        workflow = scope.transform_workflow(
            "name: test\n\non: [pull_request, push]\n\njobs: {}\n",
            "legacy.yml",
        )
        changed = (
            "software/product_alpha/index.html",
            "scripts/validate_repo.py",
        )
        self.assertTrue(scope.event_runs_for_paths(workflow, "pull_request", changed))

    def test_repository_policy_is_current(self) -> None:
        self.assertEqual(scope.apply(write=False), [])
        summary = scope.validate_policy()
        self.assertEqual(
            summary["product_alpha_only_expected_checks"],
            ["validate-product-alpha.yml"],
        )


if __name__ == "__main__":
    unittest.main()
