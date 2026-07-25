#!/usr/bin/env python3
"""Final Phase 8 pass for exact reviewed terminology and legacy-rule removal."""
from __future__ import annotations

import apply_phase8_life_earth_review as phase8

GENE_OLD = (
    "**Gene Expression:** The process by which the information encoded in a gene is used to direct "
    "the assembly of a protein molecule. It involves two main stages: transcription and translation."
)
phase8.EXACT["science/14-dna-evolution/overview.md"][GENE_OLD] = (
    "**Gene expression:** The regulated use of gene information to produce coding or non-coding RNA; "
    "protein-coding RNA can then be translated into protein. Expression includes transcription, RNA "
    "processing and turnover, translation where applicable, and multiple layers of regulation."
)

phase8.SECTION_REPLACEMENTS[("science/15-ecosystems-complex-systems/explore.md", 3)] = """## 3. Worked reasoning examples

**Question:** Why are very long food chains uncommon, and why is one fixed trophic-transfer percentage inadequate?

**Reasoning:**
1. Define the measured quantity: ingestion, assimilation, production, biomass, or energy flow give different efficiencies.
2. At each transfer, some production is not consumed, some ingested material is not assimilated, and organisms use assimilated energy for maintenance, movement, reproduction, and respiration.
3. Transfer efficiency varies with temperature, body size, food quality, metabolic strategy, ecosystem, and timescale.
4. Build a sensitivity table using several plausible efficiencies rather than one fixed percentage. Repeated multiplication still reduces energy or production available to higher levels, but chain length also depends on habitat size, productivity, omnivory, subsidies, and population viability.
"""

if __name__ == "__main__":
    raise SystemExit(phase8.main())
