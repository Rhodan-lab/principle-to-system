#!/usr/bin/env python3
"""Make the Pilot Lab selector helper correct in source and remove packaging repair."""
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


pilot_lab = Path("software/product_alpha/pilot-lab.html")
replace_once(
    pilot_lab,
    ",c=s=>document.querySelector(s);",
    ",q=s=>document.querySelector(s);",
    "Pilot Lab selector helper",
)

build = Path("software/product_alpha/build.py")
replace_once(
    build,
    '''    (\n        b',c=s=>document.querySelector(s);',\n        b',q=s=>document.querySelector(s);',\n        "Pilot Lab selector helper",\n    ),\n''',
    "",
    "selector packaging transform",
)

tests = Path("software/tests/test_product_alpha_cohort_binding.py")
replace_once(
    tests,
    "    def test_packaged_tools_bind_build_identity_and_fix_selector(self) -> None:\n",
    "    def test_source_and_packaged_tools_bind_build_identity(self) -> None:\n",
    "cohort binding test name",
)
replace_once(
    tests,
    '''        with tempfile.TemporaryDirectory() as directory:\n            output = Path(directory)\n            build_module.build(ROOT, output)\n            facilitator = (output / "facilitator.html").read_text(encoding="utf-8")\n            pilot_lab = (output / "pilot-lab.html").read_text(encoding="utf-8")\n\n''',
    '''        source_pilot_lab = (\n            ROOT / "software" / "product_alpha" / "pilot-lab.html"\n        ).read_text(encoding="utf-8")\n        with tempfile.TemporaryDirectory() as directory:\n            output = Path(directory)\n            build_module.build(ROOT, output)\n            facilitator = (output / "facilitator.html").read_text(encoding="utf-8")\n            pilot_lab = (output / "pilot-lab.html").read_text(encoding="utf-8")\n\n''',
    "source Pilot Lab fixture",
)
replace_once(
    tests,
    '''        self.assertIn(",q=s=>document.querySelector(s);", pilot_lab)\n        self.assertNotIn(",c=s=>document.querySelector(s);", pilot_lab)\n\n    def test_packaging_repairs_are_idempotent(self) -> None:\n''',
    '''        self.assertIn(",q=s=>document.querySelector(s);", source_pilot_lab)\n        self.assertNotIn(",c=s=>document.querySelector(s);", source_pilot_lab)\n        self.assertIn(",q=s=>document.querySelector(s);", pilot_lab)\n        self.assertNotIn(",c=s=>document.querySelector(s);", pilot_lab)\n\n    def test_packaging_transforms_are_idempotent(self) -> None:\n''',
    "selector parity assertions",
)
