from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
sys.path.insert(0, str(EVALUATION_DIR))

import prepare_handoff  # noqa: E402
import workspace_status  # noqa: E402


CANDIDATE = {
    "pilot_build_id": "a" * 64,
    "route_id": "refrigerator-v1",
    "evidence_status": "ready-for-human-review",
    "sessions": 1,
    "primary_action": "record-observation-context",
}


def broken_symlink(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.symlink_to(path.parent / "missing-target")
    except OSError as exc:
        raise unittest.SkipTest(f"symlinks unavailable: {exc}") from exc


class ProductAlphaDownstreamOutputPresenceTests(unittest.TestCase):
    def test_handoff_check_rejects_broken_partial_pair_before_candidate_build(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prefix = root / "handoff" / "refrigerator-product-change"
            json_path = prefix.with_suffix(".json")
            broken_symlink(json_path)

            with mock.patch.object(
                prepare_handoff,
                "build_handoff_candidate",
                return_value=CANDIDATE,
            ) as build_candidate:
                with self.assertRaisesRegex(ValueError, "output pair is incomplete"):
                    prepare_handoff.check_handoff(root / "workspace", prefix)

            build_candidate.assert_not_called()
            self.assertTrue(json_path.is_symlink())

    def test_handoff_prefix_leaf_symlink_does_not_redirect_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output_dir = root / "handoff"
            output_dir.mkdir()
            prefix = output_dir / "refrigerator-product-change"
            external = root / "external-prefix"
            try:
                prefix.symlink_to(external)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")

            json_path, markdown_path = prepare_handoff._output_paths(prefix)

            self.assertEqual(
                json_path,
                output_dir / "refrigerator-product-change.json",
            )
            self.assertEqual(
                markdown_path,
                output_dir / "refrigerator-product-change.md",
            )
            self.assertNotEqual(json_path, external.with_suffix(".json"))

    def test_workspace_status_pair_state_sees_broken_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            json_path = root / "review.json"
            markdown_path = root / "review.md"
            broken_symlink(json_path)

            with self.assertRaisesRegex(ValueError, "review pair is incomplete"):
                workspace_status._paired_state(
                    (json_path, markdown_path),
                    "review pair",
                )

    def test_workspace_status_artifact_map_reports_broken_symlink_present(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            combined = root / "combined.jsonl"
            intake = root / "intake.json"
            review_json = root / "review.json"
            review_markdown = root / "review.md"
            decisions = (
                root / "decision.json",
                root / "decision.md",
                root / "decision-receipt.json",
            )
            handoff = (
                root / "handoff.json",
                root / "handoff.md",
            )
            broken_symlink(decisions[0])

            state = workspace_status._artifact_state(
                combined,
                intake,
                review_json,
                review_markdown,
                decisions,
                handoff,
            )

            self.assertTrue(state["decision_json"])
            self.assertFalse(state["decision_markdown"])
            self.assertFalse(state["decision_receipt"])

    def test_workspace_status_decision_prefix_leaf_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            review_prefix = root / "review" / "refrigerator-review"
            review_prefix.parent.mkdir()
            external = root / "external-review-prefix"
            try:
                review_prefix.symlink_to(external)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")

            decision_paths = workspace_status._decision_paths(review_prefix)

            self.assertEqual(
                decision_paths[0],
                review_prefix.parent / "refrigerator-review-decision.json",
            )
            self.assertNotEqual(
                decision_paths[0],
                Path(f"{external}-decision.json"),
            )


if __name__ == "__main__":
    unittest.main()
