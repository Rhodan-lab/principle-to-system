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
import prepare_review  # noqa: E402


CANDIDATE: dict[str, object] = {
    "pilot_build_id": "a" * 64,
    "route_id": "refrigerator-v1",
    "evidence_status": "ready-for-human-review",
    "sessions": 1,
    "primary_action": "record-observation-context",
}


class ProductAlphaHandoffExclusivePublishTests(unittest.TestCase):
    def test_second_publish_failure_rolls_back_owned_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prefix = root / "handoff" / "refrigerator-product-change"
            json_path = prefix.with_suffix(".json")
            markdown_path = prefix.with_suffix(".md")
            real_publish = prepare_review.publish_exclusive
            publish_calls = 0

            def fail_second_publish(staged: Path, destination: Path) -> None:
                nonlocal publish_calls
                publish_calls += 1
                if publish_calls == 2:
                    raise OSError("simulated second handoff publish failure")
                real_publish(staged, destination)

            with (
                mock.patch.object(
                    prepare_handoff,
                    "build_handoff_candidate",
                    return_value=CANDIDATE,
                ),
                mock.patch.object(
                    prepare_handoff,
                    "render_markdown",
                    return_value="candidate\n",
                ),
                mock.patch.object(
                    prepare_review,
                    "publish_exclusive",
                    side_effect=fail_second_publish,
                ),
            ):
                with self.assertRaisesRegex(
                    OSError,
                    "simulated second handoff publish failure",
                ):
                    prepare_handoff.write_handoff(root / "workspace", prefix)

            self.assertFalse(json_path.exists())
            self.assertFalse(markdown_path.exists())
            self.assertEqual(list(json_path.parent.glob(".*.tmp-*")), [])

    def test_competing_destination_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prefix = root / "handoff" / "refrigerator-product-change"
            json_path = prefix.with_suffix(".json")
            markdown_path = prefix.with_suffix(".md")
            real_publish = prepare_review.publish_exclusive

            def publish_after_competitor(staged: Path, destination: Path) -> None:
                destination.write_text(
                    "competing handoff output\n",
                    encoding="utf-8",
                )
                real_publish(staged, destination)

            with (
                mock.patch.object(
                    prepare_handoff,
                    "build_handoff_candidate",
                    return_value=CANDIDATE,
                ),
                mock.patch.object(
                    prepare_handoff,
                    "render_markdown",
                    return_value="candidate\n",
                ),
                mock.patch.object(
                    prepare_review,
                    "publish_exclusive",
                    side_effect=publish_after_competitor,
                ),
            ):
                with self.assertRaises(FileExistsError):
                    prepare_handoff.write_handoff(root / "workspace", prefix)

            self.assertEqual(
                json_path.read_text(encoding="utf-8"),
                "competing handoff output\n",
            )
            self.assertFalse(markdown_path.exists())
            self.assertEqual(list(json_path.parent.glob(".*.tmp-*")), [])


if __name__ == "__main__":
    unittest.main()
