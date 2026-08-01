from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
MODULE_PATH = EVALUATION_DIR / "prepare_review.py"
if str(EVALUATION_DIR) not in sys.path:
    sys.path.insert(0, str(EVALUATION_DIR))
SPEC = importlib.util.spec_from_file_location("product_alpha_prepare_review", MODULE_PATH)
assert SPEC and SPEC.loader
review_packet = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = review_packet
SPEC.loader.exec_module(review_packet)

BUILD_ID = "a" * 64
OTHER_BUILD_ID = "b" * 64
SCORE_KEYS = (
    "mechanism_explanation",
    "model_reasoning",
    "failure_diagnosis",
    "evidence_boundary",
    "redesign_tradeoff",
)
STEPS = ["observe", "map", "model", "diagnose", "redesign"]


def session(index: int, build_id: str = BUILD_ID, note: str = "private note") -> dict:
    return {
        "pilot_build_id": build_id,
        "session_id": f"anonymous-{index:03d}",
        "route_id": "refrigerator-v1",
        "started": True,
        "completed_steps": list(STEPS),
        "duration_minutes": 25 + index,
        "scores": {key: 2 for key in SCORE_KEYS},
        "confusion_tags": [],
        "voluntary_continue": True,
        "facilitator_notes": note,
    }


def write_sessions(path: Path, count: int = 5, build_id: str = BUILD_ID) -> bytes:
    raw = "".join(
        json.dumps(session(index, build_id), sort_keys=True, separators=(",", ":"))
        + "\n"
        for index in range(1, count + 1)
    ).encode("utf-8")
    path.write_bytes(raw)
    return raw


class ProductAlphaReviewPacketTests(unittest.TestCase):
    def test_complete_packet_is_deterministic_hash_bound_and_deidentified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "sessions.jsonl"
            raw = write_sessions(input_path)
            first = review_packet.build_review_packet(input_path, BUILD_ID)
            second = review_packet.build_review_packet(input_path, BUILD_ID)

        self.assertEqual(first, second)
        self.assertEqual(
            first["contract"],
            "principia-product-alpha-pilot-review-packet/0.1",
        )
        self.assertEqual(
            first["evidence_binding"]["input_sha256"],
            hashlib.sha256(raw).hexdigest(),
        )
        expected_summary_hash = hashlib.sha256(
            review_packet.canonical_json(first["aggregate_summary"])
        ).hexdigest()
        self.assertEqual(
            first["evidence_binding"]["summary_sha256"], expected_summary_hash
        )
        self.assertTrue(first["review"]["planning_review_eligible"])
        self.assertEqual(first["review"]["status"], "human-review-required")
        serialized = json.dumps(first, sort_keys=True)
        self.assertNotIn("private note", serialized)
        self.assertNotIn("facilitator_notes", serialized)
        self.assertFalse(first["boundaries"]["second_route_authorized"])
        self.assertFalse(first["boundaries"]["learning_effectiveness_claimed"])

    def test_incomplete_cohort_stays_pending_and_not_planning_eligible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "sessions.jsonl"
            write_sessions(input_path, count=2)
            packet = review_packet.build_review_packet(input_path, BUILD_ID)

        self.assertEqual(packet["aggregate_summary"]["evidence_status"], "incomplete")
        self.assertFalse(packet["review"]["planning_review_eligible"])
        self.assertEqual(packet["review"]["status"], "human-review-required")
        self.assertGreater(packet["review"]["revision_signal_count"], 0)

    def test_expected_build_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "sessions.jsonl"
            write_sessions(input_path)
            with self.assertRaisesRegex(ValueError, "expected launcher build"):
                review_packet.build_review_packet(input_path, OTHER_BUILD_ID)

    def test_markdown_is_deidentified_and_contains_bounded_decision_options(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "sessions.jsonl"
            write_sessions(input_path)
            packet = review_packet.build_review_packet(input_path, BUILD_ID)
            markdown = review_packet.render_markdown(packet)

        self.assertIn("# Product Alpha Pilot Human Review", markdown)
        self.assertIn("revise-current-route", markdown)
        self.assertIn("advance-to-next-product-planning-review", markdown)
        self.assertIn("does not automatically modify the repository", markdown)
        self.assertNotIn("private note", markdown)
        self.assertNotIn("facilitator_notes", markdown)

    def test_output_paths_reject_repository_and_existing_files(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            review_packet.review_output_paths(
                REPO_ROOT / "software" / "product_alpha" / "review-output"
            )

        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory) / "review"
            prefix.with_suffix(".json").write_text("existing", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                review_packet.review_output_paths(prefix)

    def test_write_outputs_are_deterministic_and_refuse_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "sessions.jsonl"
            write_sessions(input_path)
            packet = review_packet.build_review_packet(input_path, BUILD_ID)
            first_prefix = root / "first" / "review"
            second_prefix = root / "second" / "review"
            first_json, first_md, first_hash = review_packet.write_review_outputs(
                first_prefix, packet
            )
            second_json, second_md, second_hash = review_packet.write_review_outputs(
                second_prefix, packet
            )
            self.assertEqual(first_json.read_bytes(), second_json.read_bytes())
            self.assertEqual(first_md.read_bytes(), second_md.read_bytes())
            self.assertEqual(first_hash, second_hash)
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                review_packet.write_review_outputs(first_prefix, packet)

    def test_subprocess_command_creates_verified_pair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "sessions.jsonl"
            write_sessions(input_path)
            prefix = root / "private" / "refrigerator-review"
            result = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--input",
                    str(input_path),
                    "--expect-build-id",
                    BUILD_ID,
                    "--output-prefix",
                    str(prefix),
                ],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            json_path = prefix.with_suffix(".json")
            markdown_path = prefix.with_suffix(".md")
            packet = json.loads(json_path.read_text(encoding="utf-8"))

        self.assertIn("Product Alpha human-review packet created.", result.stdout)
        self.assertIn("Decision: human-review-required", result.stdout)
        self.assertEqual(packet["pilot_build_id"], BUILD_ID)
        self.assertTrue(markdown_path.name.endswith(".md"))


if __name__ == "__main__":
    unittest.main()
