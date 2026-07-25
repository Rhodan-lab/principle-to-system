#!/usr/bin/env python3
"""Final Phase 7 content pass with direct sources and safe orbital framing."""
from __future__ import annotations

import re

import run_phase7_review  # Applies the main review monkeypatches.

phase7 = run_phase7_review.phase7

EXTRA_SOURCES = {
    "06-matter-quantum": (
        "5. National Institute of Biomedical Imaging and Bioengineering. "
        "*Magnetic Resonance Imaging (MRI)*. "
        "https://www.nibib.nih.gov/science-education/science-topics/magnetic-resonance-imaging-mri\n"
        "6. National Institute of Standards and Technology. "
        "*Designing Advanced Scanning Probe Microscopy Instruments*. "
        "https://www.nist.gov/programs-projects/designing-advanced-scanning-probe-microscopy-instruments"
    ),
    "07-chemical-bonding": (
        "5. United States Environmental Protection Agency. "
        "*Automobile Emissions Overview*. "
        "https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=P10001KF.TXT"
    ),
    "10-electricity-magnetism": (
        "5. Bureau International des Poids et Mesures. "
        "*The International System of Units (SI), 9th edition*. "
        "https://www.bipm.org/documents/20126/41483022/SI-Brochure-9-EN.pdf"
    ),
    "12-fluids-materials": (
        "5. NASA Glenn Research Center. *Bernoulli and Newton*. "
        "https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/bernoulli-and-newton/"
    ),
}

for module, block in EXTRA_SOURCES.items():
    if block.split("https://", 1)[-1] not in phase7.SOURCES[module]:
        phase7.SOURCES[module] = phase7.SOURCES[module].rstrip() + "\n" + block

phase7.BANNED = tuple(phase7.BANNED) + (
    "Newton's Cannonball",
    "powerful cannon",
    "cannonball",
)

_original_transform = phase7.transform


def transform(path, module):
    text, notes = _original_transform(path, module)
    rel = path.relative_to(phase7.ROOT).as_posix()
    if rel == "science/09-motion-forces/explore.md":
        text = text.replace("opposite to the car's initial motion", "opposite to the cart's initial motion")
        replacement = """# 4. Thought experiments

**Orbital free-fall simulation**

Imagine a small test object already above the atmosphere in a simulation. Give it a modest horizontal velocity: gravity curves its path downward until it intersects Earth. Increase the horizontal velocity and the intersection occurs farther away. At the appropriate speed, the object continuously falls toward Earth while the surface curves away beneath it, producing an orbit. How do initial altitude, horizontal speed, and Earth's curvature determine whether the trajectory intersects the surface, forms an ellipse, or escapes?

"""
        text = re.sub(
            r"(?ms)^# 4\. Thought experiments\s*\n.*?(?=^# 5\. Household and browser-based explorations)",
            replacement,
            text,
        )
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return text, notes


phase7.transform = transform

if __name__ == "__main__":
    raise SystemExit(phase7.main())
