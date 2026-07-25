#!/usr/bin/env python3
"""Run the Phase 7 review while preserving or creating source headings."""
from __future__ import annotations

import re

import apply_phase7_physical_science_review as phase7

for module, block in tuple(phase7.SOURCES.items()):
    lines = block.splitlines()
    if lines and re.match(r"^## (?:12|13)\. Sources$", lines[0]):
        phase7.SOURCES[module] = "\n".join(lines[1:]).lstrip()

# Corrective explanations may name a misconception. Ban the exact legacy claims
# or unsafe instructions rather than banning the educational phrase everywhere.
phase7.BANNED = tuple(
    phrase
    for phrase in phase7.BANNED
    if phrase not in {
        "virtual particles popping in and out",
        "path of least resistance",
        "upper lip",
    }
) + (
    "vacuum is teeming with fluctuating quantum fields and virtual particles",
    "Current takes the path of least resistance",
    "Hold it loosely against your upper lip",
)


def source_match(text: str):
    return re.search(r"(?m)^#{1,2} \d+\. Sources\s*$", text)


def insert_boundaries(text: str, module: str) -> str:
    if "## Phase 7 review boundaries and validity limits" in text:
        return text
    marker = source_match(text)
    if marker:
        return text[: marker.start()] + phase7.BOUNDARIES[module].rstrip() + "\n\n" + text[marker.start():]
    return (
        text.rstrip()
        + "\n\n"
        + phase7.BOUNDARIES[module].rstrip()
        + "\n\n## 11. Sources\n"
    )


def replace_sources(text: str, module: str) -> str:
    pattern = re.compile(r"(?ms)^(#{1,2} \d+\. Sources\s*\n).*\Z")
    match = pattern.search(text)
    if not match:
        text = text.rstrip() + "\n\n## 11. Sources\n"
        match = pattern.search(text)
    assert match is not None
    return pattern.sub(match.group(1) + "\n" + phase7.SOURCES[module].rstrip() + "\n", text)


_original_transform = phase7.transform


def transform(path, module):
    text, notes = _original_transform(path, module)
    if path.relative_to(phase7.ROOT).as_posix() == "science/08-energy-thermodynamics/explore.md":
        safe_activity = (
            "*   **Elastocaloric model:** Use published temperature–extension data "
            "or a classroom simulation for a rubber elastomer. Plot the qualitative "
            "temperature response during rapid extension, thermal equilibration, and "
            "release. Do not snap stretched bands near the face or skin."
        )
        text = re.sub(
            r"(?ms)^\*   \*\*The Rubber Band Refrigerator:\*\*.*?(?=\n\*   \*\*Online Simulation:)",
            safe_activity,
            text,
        )
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return text, notes


phase7.insert_boundaries = insert_boundaries
phase7.replace_sources = replace_sources
phase7.transform = transform

if __name__ == "__main__":
    raise SystemExit(phase7.main())
