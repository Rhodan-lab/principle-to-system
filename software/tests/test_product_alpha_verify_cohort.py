from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "software" / "product_alpha" / "evaluation" / "verify_cohort.py"
BUILD_A = "a" * 64
BUILD_B = "b" * 64
STEPS = ["observe", "map", "model", "diagnose", "redesign"]


def session(session_id: str, build_id: str = BUILD_A) -> dict[str, object]:
    return {
        "pilot_build_id": build_id,
        "session_id": session_id,
        "route_id": "refrigerator-v1",
        "started": True,
        "completed_steps": STEPS,
        "duration_minutes": 28,
        "scores": {
            "mechanism_explanation": 2,
            "model_reasoning": 1,
            "failure_diagnosis": 2,
            "evidence_boundary": 1,
            "redesign_tradeoff": 2,
        },
        "confusion_tags": [],
        "voluntary_continue": True,
        "facilitator_notes": "",
    }


class ProductAlphaVerifyCohortTests(unittest.TestCase):
    def run_cli(
        self,
        records: list[dict[str, object]],
        expected_build_id: str,
        output_format: str = "json",
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.jsonl"
            path.write_text(
                "".join(json.dumps(record) + "\n" for record in records),
                encoding="utf-8",
            )
            return subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(path),
                    "--expect-build-id",
                    expected_build_id,
                    "--format",
                    output_format,
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_matching_expected_build_emits_verified_summary(self) -> None:
        records = [session("anonymous-001"), session("anonymous-002")]
        first = self.run_cli(records, BUILD_A)
        second = self.run_cli(records, BUILD_A)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        payload = json.loads(first.stdout)
        self.assertEqual(payload["contract"], "principia-product-alpha-pilot-summary/0.4")
        self.assertEqual(payload["pilot_build_id"], BUILD_A)
        self.assertEqual(payload["sessions"], 2)

    def test_mismatched_expected_build_is_rejected(self) -> None:
        result = self.run_cli([session("anonymous-001")], BUILD_B)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match the expected launcher build", result.stderr)
        self.assertIn(BUILD_A, result.stderr)
        self.assertIn(BUILD_B, result.stderr)

    def test_malformed_expected_build_is_rejected(self) -> None:
        result = self.run_cli([session("anonymous-001")], "ABC")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("64-character lowercase SHA-256", result.stderr)

    def test_mixed_build_cohort_is_rejected_before_output(self) -> None:
        records = [
            session("anonymous-001", BUILD_A),
            session("anonymous-002", BUILD_B),
        ]
        result = self.run_cli(records, BUILD_A)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("does not match the cohort build", result.stderr)


if __name__ == "__main__":
    unittest.main()
