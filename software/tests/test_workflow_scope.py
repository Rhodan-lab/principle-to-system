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
        for fixture_paths in scope.PRODUCT_FIXTURES.values():
            with self.subTest(fixture_paths=fixture_paths):
                self.assertFalse(
                    scope.event_runs_for_paths(
                        updated, "pull_request", fixture_paths
                    )
                )

    def test_existing_paths_ignore_receives_new_owned_paths(self) -> None:
        original = """name: test

on:
  pull_request:
    paths-ignore:
      - 'software/product_alpha/**'
      - 'software/tests/test_product_alpha*.py'

jobs: {}
"""
        updated = scope.transform_workflow(original, "legacy.yml")
        self.assertIn("- 'software/tests/test_product_alpha*.mjs'", updated)
        self.assertIn(
            "- '.github/workflows/validate-product-alpha.yml'", updated
        )
        for fixture_paths in scope.PRODUCT_FIXTURES.values():
            with self.subTest(fixture_paths=fixture_paths):
                self.assertFalse(
                    scope.event_runs_for_paths(
                        updated, "pull_request", fixture_paths
                    )
                )
        self.assertEqual(scope.transform_workflow(updated, "legacy.yml"), updated)

    def test_existing_positive_paths_remain_narrow(self) -> None:
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

    def test_broad_positive_paths_receive_negative_exclusions(self) -> None:
        original = """name: test

on:
  push:
    paths:
      - 'software/**'
      - '.github/workflows/**'
      - 'scripts/**'

jobs: {}
"""
        updated = scope.transform_workflow(original, "legacy.yml")
        for pattern in scope.PRODUCT_PATHS:
            with self.subTest(pattern=pattern):
                self.assertIn(f"- '!{pattern}'", updated)
        for fixture_paths in scope.PRODUCT_FIXTURES.values():
            with self.subTest(fixture_paths=fixture_paths):
                self.assertFalse(
                    scope.event_runs_for_paths(updated, "push", fixture_paths)
                )
        self.assertTrue(
            scope.event_runs_for_paths(
                updated,
                "push",
                ("software/product_alpha/index.html", "software/principia_site.py"),
            )
        )
        self.assertTrue(
            scope.event_runs_for_paths(
                updated,
                "push",
                (
                    ".github/workflows/validate-product-alpha.yml",
                    ".github/workflows/validate-phase-13-software.yml",
                ),
            )
        )
        self.assertEqual(scope.transform_workflow(updated, "legacy.yml"), updated)

    def test_node_only_change_is_product_alpha_owned(self) -> None:
        workflow = scope.transform_workflow(
            "name: test\n\non: [pull_request, push]\n\njobs: {}\n",
            "legacy.yml",
        )
        self.assertFalse(
            scope.event_runs_for_paths(
                workflow,
                "pull_request",
                ("software/tests/test_product_alpha_learner_state.mjs",),
            )
        )

    def test_product_alpha_ci_change_is_product_alpha_owned(self) -> None:
        workflow = scope.transform_workflow(
            "name: test\n\non: [pull_request, push]\n\njobs: {}\n",
            "legacy.yml",
        )
        self.assertFalse(
            scope.event_runs_for_paths(
                workflow,
                "pull_request",
                (".github/workflows/validate-product-alpha.yml",),
            )
        )

    def test_mixed_change_keeps_legacy_event_eligible(self) -> None:
        workflow = scope.transform_workflow(
            "name: test\n\non: [pull_request, push]\n\njobs: {}\n",
            "legacy.yml",
        )
        changed_sets = (
            (
                "software/product_alpha/index.html",
                "scripts/validate_repo.py",
            ),
            (
                "software/tests/test_product_alpha_learner_state.mjs",
                "software/tests/test_phase15_offline_pilot.py",
            ),
            (
                ".github/workflows/validate-product-alpha.yml",
                ".github/workflows/validate-phase-13-software.yml",
            ),
        )
        for changed in changed_sets:
            with self.subTest(changed=changed):
                self.assertTrue(
                    scope.event_runs_for_paths(
                        workflow, "pull_request", changed
                    )
                )

    def test_exempt_workflows_keep_owned_triggers(self) -> None:
        product = """name: Product

on:
  pull_request:
    paths:
      - 'software/product_alpha/**'
      - 'software/tests/test_product_alpha*.mjs'
      - '.github/workflows/validate-product-alpha.yml'

jobs: {}
"""
        workflow_scope = """name: Scope

on:
  pull_request:
    paths:
      - '.github/workflows/**'

jobs: {}
"""
        self.assertEqual(
            scope.transform_workflow(product, "validate-product-alpha.yml"),
            product,
        )
        self.assertEqual(
            scope.transform_workflow(
                workflow_scope, "validate-workflow-scope.yml"
            ),
            workflow_scope,
        )
        self.assertTrue(
            scope.event_runs_for_paths(
                product,
                "pull_request",
                (".github/workflows/validate-product-alpha.yml",),
            )
        )
        self.assertTrue(
            scope.event_runs_for_paths(
                workflow_scope,
                "pull_request",
                (".github/workflows/validate-product-alpha.yml",),
            )
        )

    def test_repository_policy_is_current(self) -> None:
        self.assertEqual(scope.apply(write=False), [])
        summary = scope.validate_policy()
        self.assertEqual(
            summary["product_alpha_only_expected_checks"],
            {
                "ci": [
                    "validate-product-alpha.yml",
                    "validate-workflow-scope.yml",
                ],
                "runtime": ["validate-product-alpha.yml"],
            },
        )


if __name__ == "__main__":
    unittest.main()
