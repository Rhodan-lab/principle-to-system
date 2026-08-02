from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DIAGNOSIS_RUNTIME = REPO_ROOT / "software" / "tests" / "test_product_alpha_diagnosis_runtime.py"
LEARNER_RUNTIME = REPO_ROOT / "software" / "tests" / "test_product_alpha_learner_runtime.py"


class ProductAlphaWarningPolicyTests(unittest.TestCase):
    def test_runtime_harnesses_are_raw_f_strings(self) -> None:
        for path in (DIAGNOSIS_RUNTIME, LEARNER_RUNTIME):
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertIn('harness = rf"""', source)
                self.assertNotIn('harness = f"""', source)

    def test_runtime_tests_compile_with_syntax_warnings_as_errors(self) -> None:
        subprocess.run(
            [
                sys.executable,
                "-W",
                "error::SyntaxWarning",
                "-m",
                "py_compile",
                str(DIAGNOSIS_RUNTIME),
                str(LEARNER_RUNTIME),
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
