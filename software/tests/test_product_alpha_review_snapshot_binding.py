from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = REPO_ROOT / "software" / "product_alpha" / "evaluation"
sys.path.insert(0, str(EVALUATION_DIR))

import prepare_review  # noqa: E402
import summarize  # noqa: E402
import verify_cohort  # noqa: E402

BUILD_ID = "a" * 64
OTHER_BUILD_ID = "b" * 64


def session(build_id: str, session_id: str) -> dict[str, object]:
    return {
        "pilot_build_id": build_id,
        "session_id": session_id,
        "route_id": "refrigerator-v1",
        "started": True,
        "completed_steps": ["observe", "map", "model", "diagnose", "redesign"],
        "duration_minutes": 20,
        "scores": {
            "mechanism_explanation": 2,
            "model_reasoning": 2,
            "failure_diagnosis": 2,
            "evidence_boundary": 2,
            "redesign_tradeoff": 2,
        },
        "confusion_tags": [],
        "voluntary_continue": True,
        "facilitator_notes": "",
    }


def encoded_session(build_id: str, session_id: str) -> bytes:
    return (
        json.dumps(
            session(build_id, session_id),
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


class ProductAlphaReviewSnapshotBindingTests(unittest.TestCase):
    def test_path_and_byte_loaders_validate_the_same_snapshot(self) -> None:
        raw = encoded_session(BUILD_ID, "anonymous-001")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.jsonl"
            path.write_bytes(raw)

            from_path = summarize.load_sessions(path)
            from_bytes = summarize.load_sessions_bytes(raw)

        self.assertEqual(from_path, from_bytes)

    def test_byte_loader_enforces_the_input_limit(self) -> None:
        raw = encoded_session(BUILD_ID, "anonymous-001")
        with mock.patch.object(summarize, "MAX_INPUT_BYTES", len(raw) - 1):
            with self.assertRaisesRegex(ValueError, "Product Alpha session limit"):
                summarize.load_sessions_bytes(raw)

    def test_path_verifier_reads_one_bounded_snapshot(self) -> None:
        raw = encoded_session(BUILD_ID, "anonymous-001")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.jsonl"
            path.write_bytes(raw)
            real_read = verify_cohort.read_cohort_input

            with mock.patch.object(
                verify_cohort,
                "read_cohort_input",
                wraps=real_read,
            ) as bounded_read:
                summary = verify_cohort.verify_cohort(path, BUILD_ID)

        self.assertEqual(summary["pilot_build_id"], BUILD_ID)
        bounded_read.assert_called_once_with(path)

    def test_review_hash_and_summary_use_the_same_snapshot(self) -> None:
        original = encoded_session(BUILD_ID, "anonymous-001")
        replacement = encoded_session(OTHER_BUILD_ID, "anonymous-002")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.jsonl"
            path.write_bytes(original)
            real_read = summarize.read_session_input
            read_count = 0

            def mutate_after_read(input_path: Path) -> bytes:
                nonlocal read_count
                read_count += 1
                raw = real_read(input_path)
                input_path.write_bytes(replacement)
                return raw

            with mock.patch.object(
                summarize,
                "read_session_input",
                side_effect=mutate_after_read,
            ):
                packet = prepare_review.build_review_packet(path, BUILD_ID)

            current_bytes = path.read_bytes()

        self.assertEqual(read_count, 1)
        self.assertEqual(current_bytes, replacement)
        self.assertEqual(packet["pilot_build_id"], BUILD_ID)
        self.assertEqual(packet["aggregate_summary"]["pilot_build_id"], BUILD_ID)
        self.assertEqual(
            packet["evidence_binding"]["input_sha256"],
            hashlib.sha256(original).hexdigest(),
        )
        self.assertEqual(packet["evidence_binding"]["input_byte_count"], len(original))


if __name__ == "__main__":
    unittest.main()
