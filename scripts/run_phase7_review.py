#!/usr/bin/env python3
"""Run the Phase 7 review while preserving each file's source heading."""
from __future__ import annotations

import re

import apply_phase7_physical_science_review as phase7

for module, block in tuple(phase7.SOURCES.items()):
    lines = block.splitlines()
    if lines and re.match(r"^## (?:12|13)\. Sources$", lines[0]):
        phase7.SOURCES[module] = "\n".join(lines[1:]).lstrip()


def replace_sources(text: str, module: str) -> str:
    pattern = re.compile(r"(?ms)^(#{1,2} (?:12|13)\. Sources\s*\n).*\Z")
    match = pattern.search(text)
    if not match:
        raise ValueError("source section not found")
    return pattern.sub(match.group(1) + "\n" + phase7.SOURCES[module].rstrip() + "\n", text)


phase7.replace_sources = replace_sources

if __name__ == "__main__":
    raise SystemExit(phase7.main())
