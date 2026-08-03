#!/usr/bin/env python3
"""Align loopback smoke with capability-safe Product Alpha build-ID parsing."""
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


marker = 'b"EXPECTED_BUILD_ID=new URLSearchParams"'
replacement = 'b\'EXPECTED_BUILD_ID=query?.get("build_id")\''
replace_once(
    Path("software/product_alpha/run_pilot.py"),
    marker,
    replacement,
    "loopback Pilot Lab packaged marker",
)
replace_once(
    Path("software/tests/test_product_alpha_pilot_smoke.py"),
    marker,
    replacement,
    "loopback missing-marker regression",
)
