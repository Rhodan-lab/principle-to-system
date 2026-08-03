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


CANDIDATE = {
    "pilot_build_id": "a" * 64,
    "route_id": "refrigerator-v1",
    "evidence_status": "ready-for-human-review",
    "sessions": 1,
    "primary_action": "record-observation-context",
}


class ProductAlphaHandoffCheckStateTests(unittest.TestCase):
    def test_check_rejects_partial_output_pair_before_rebuilding_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prefix = root / "handoff" / "candidate"
            json_path = prefix.with_suffix(".json")
            json_path.parent.mkdir(parents=True)
            json_path.write_text("{}\n", encoding="utf-8")

            with mock.patch.object(
                prepare_handoff,
                "build_handoff_candidate",
                return_value=CANDIDATE,
            ) as build_candidate:
                with self.assertRaisesRegex(ValueError, "output pair is incomplete"):
                    prepare_handoff.check_handoff(root / "workspace", prefix)

            build_candidate.assert_not_called()
            self.assertTrue(json_path.exists())
            self.assertFalse(prefix.with_suffix(".md").exists())

    def test_check_reports_only_complete_pairs_as_existing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prefix = root / "handoff" / "candidate"

            with mock.patch.object(
                prepare_handoff,
                "build_handoff_candidate",
                return_value=CANDIDATE,
            ):
                empty = prepare_handoff.check_handoff(root / "workspace", prefix)
                self.assertFalse(empty["outputs_exist"])
                self.assertFalse(empty["outputs_complete"])

                json_path = prefix.with_suffix(".json")
                markdown_path = prefix.with_suffix(".md")
                json_path.parent.mkdir(parents=True)
                json_path.write_text("{}\n", encoding="utf-8")
                markdown_path.write_text("candidate\n", encoding="utf-8")

                complete = prepare_handoff.check_handoff(root / "workspace", prefix)
                self.assertTrue(complete["outputs_exist"])
                self.assertTrue(complete["outputs_complete"])


if __name__ == "__main__":
    unittest.main()
