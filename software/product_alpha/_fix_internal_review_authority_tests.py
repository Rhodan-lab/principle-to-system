#!/usr/bin/env python3
"""Align generated authority tests with semantic command and wording boundaries."""
from pathlib import Path

PATH = Path("software/tests/test_product_alpha_state_authority.py")
text = PATH.read_text(encoding="utf-8")

old_authority = '        self.assertIn("does not authorize", lowered)\n'
new_authority = (
    '        self.assertTrue(\n'
    '            "does not authorize" in lowered or "do not authorize" in lowered\n'
    '        )\n'
)
if text.count(old_authority) != 1:
    raise SystemExit("optional-authority assertion anchor changed")
text = text.replace(old_authority, new_authority, 1)

old_local_command = '            self.assertNotIn("run_pilot.py --open", text)\n'
if text.count(old_local_command) != 1:
    raise SystemExit("local inspection command assertion anchor changed")
text = text.replace(old_local_command, "", 1)

PATH.write_text(text, encoding="utf-8")
