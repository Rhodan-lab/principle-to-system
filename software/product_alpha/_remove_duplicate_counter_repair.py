#!/usr/bin/env python3
"""Make the Pilot Lab duplicate counter correct in source and remove build-time repair."""
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
    "state.duplicates=+1;",
    "state.duplicates+=1;",
    "Pilot Lab additive duplicate counter",
)

build = Path("software/product_alpha/build.py")
replace_once(
    build,
    'PILOT_LAB_DUPLICATE_COUNTER_BUG = b"state.duplicates=+1;"\nPILOT_LAB_DUPLICATE_COUNTER_FIX = b"state.duplicates+=1;"\n\n',
    "",
    "duplicate counter repair constants",
)
replace_once(
    build,
    '    data = _replace_once(\n        data,\n        PILOT_LAB_DUPLICATE_COUNTER_BUG,\n        PILOT_LAB_DUPLICATE_COUNTER_FIX,\n        "Pilot Lab duplicate counter",\n    )\n',
    "",
    "duplicate counter packaging repair",
)
replace_once(
    build,
    '    """Apply bounded packaging repairs and reject ambiguous asset states."""',
    '    """Apply bounded route packaging transforms and reject ambiguous asset states."""',
    "prepare_static_asset docstring",
)

tests = Path("software/tests/test_product_alpha.py")
replace_once(
    tests,
    '''    def test_build_normalizes_duplicate_counter_to_additive_increment(self) -> None:\n        output = self.root / "dist"\n        source = self.root / "software" / "product_alpha" / "pilot-lab.html"\n        build_module.build(self.root, output)\n        source_bytes = source.read_bytes()\n        built_bytes = (output / "pilot-lab.html").read_bytes()\n        self.assertEqual(\n            source_bytes.count(build_module.PILOT_LAB_DUPLICATE_COUNTER_BUG),\n            1,\n        )\n        self.assertNotIn(\n            build_module.PILOT_LAB_DUPLICATE_COUNTER_BUG,\n            built_bytes,\n        )\n        self.assertEqual(\n            built_bytes.count(build_module.PILOT_LAB_DUPLICATE_COUNTER_FIX),\n            1,\n        )\n\n''',
    '''    def test_source_and_build_preserve_additive_duplicate_counter(self) -> None:\n        output = self.root / "dist"\n        source = self.root / "software" / "product_alpha" / "pilot-lab.html"\n        build_module.build(self.root, output)\n        source_bytes = source.read_bytes()\n        built_bytes = (output / "pilot-lab.html").read_bytes()\n        bug = b"state.duplicates=+1;"\n        additive = b"state.duplicates+=1;"\n        self.assertNotIn(bug, source_bytes)\n        self.assertNotIn(bug, built_bytes)\n        self.assertEqual(source_bytes.count(additive), 1)\n        self.assertEqual(built_bytes.count(additive), 1)\n\n''',
    "duplicate counter build test",
)
replace_once(
    tests,
    '''        with self.assertRaisesRegex(ValueError, "route identity must occur exactly once"):\n            build_module.prepare_static_asset(\n                "pilot-lab.html",\n                build_module.PILOT_LAB_DUPLICATE_COUNTER_BUG * 2,\n            )\n''',
    "",
    "obsolete duplicate counter ambiguity test",
)
