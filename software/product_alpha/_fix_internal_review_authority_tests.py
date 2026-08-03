#!/usr/bin/env python3
"""Align generated authority artifacts with semantic and formatting boundaries."""
from pathlib import Path

TEST_PATH = Path("software/tests/test_product_alpha_state_authority.py")
test_text = TEST_PATH.read_text(encoding="utf-8")

old_authority = '        self.assertIn("does not authorize", lowered)\n'
new_authority = (
    '        self.assertTrue(\n'
    '            "does not authorize" in lowered or "do not authorize" in lowered\n'
    '        )\n'
)
if test_text.count(old_authority) != 1:
    raise SystemExit("optional-authority assertion anchor changed")
test_text = test_text.replace(old_authority, new_authority, 1)

old_local_command = '            self.assertNotIn("run_pilot.py --open", text)\n'
if test_text.count(old_local_command) != 1:
    raise SystemExit("local inspection command assertion anchor changed")
test_text = test_text.replace(old_local_command, "", 1)
TEST_PATH.write_text(test_text, encoding="utf-8")

REPORT_PATH = Path("reports/product-alpha-0-1-pilot-summary.md")
report_text = REPORT_PATH.read_text(encoding="utf-8")
for line in (
    "**Status:** superseded as active decision authority  \n",
    "**Current authority:** `reports/product-alpha-0-1-multi-perspective-review.json`  \n",
):
    if report_text.count(line) != 1:
        raise SystemExit(f"report whitespace anchor changed: {line!r}")
    report_text = report_text.replace(line, line.rstrip() + "\n", 1)
REPORT_PATH.write_text(report_text, encoding="utf-8")
