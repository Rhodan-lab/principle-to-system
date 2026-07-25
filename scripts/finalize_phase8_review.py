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

phase8.EXACT["science/14-dna-evolution/overview.md"].update(
    {
        "2.  **Natural Selection:** Alleles that confer a survival or reproductive advantage increase in frequency.":
            "2.  **Natural selection:** Heritable variants associated with greater reproductive contribution can change in frequency; the outcome also depends on dominance, environment, drift, migration, and genetic background.",
        "*   $p^2$ is the frequency of the homozygous dominant genotype ($AA$).":
            "*   $p^2$ is the expected frequency of genotype $AA$.",
        "*   $2pq$ is the frequency of the heterozygous genotype ($Aa$).":
            "*   $2pq$ is the expected frequency of genotype $Aa$.",
        "*   $q^2$ is the frequency of the homozygous recessive genotype ($aa$).":
            "*   $q^2$ is the expected frequency of genotype $aa$.",
        "*   $q$: Frequency of the recessive allele (dimensionless).":
            "*   $q$: Frequency of allele $a$ (dimensionless).",
        "*   **16-biotechnology:** The principles of DNA structure and gene expression are applied in genetic engineering, PCR, and sequencing technologies.":
            "*   **19-software-ai:** Bioinformatics and sequencing pipelines use computational models to store, align, annotate, and interpret genetic data while preserving uncertainty and provenance.",
        "*   **13-cells-bioenergetics:** The processes of DNA replication, transcription, and translation are highly energy-dependent, relying on ATP generated through cellular respiration.":
            "*   **13-cells-bioenergetics:** Replication, transcription, translation, repair, and regulation consume nucleotide triphosphates and depend on cellular metabolism, redox state, and molecular transport.",
    }
)

phase8.EXACT.setdefault("science/15-ecosystems-complex-systems/explore.md", {}).update(
    {
        "- If a highly connected, central species (a \"keystone species\") is removed from a food web, what is the likely cascade of effects compared to removing a species with only one or two connections?":
            "- If a species with strong measured effects on ecosystem structure is removed, how might outcomes differ from removing a highly connected species? Why are keystone effect, network degree, biomass, and functional uniqueness different quantities?",
        "Label the arrows with '+' (positive correlation) or '-' (negative correlation).":
            "Label each arrow with '+' when an increase in the cause tends to increase the effect, or '-' when it tends to decrease the effect, holding the stated context fixed; these are hypothesised causal signs, not simple correlations.",
        "Can you find a set of parameters that leads to a stable equilibrium?":
            "Can you find parameters that produce bounded persistence, a steady state, oscillation, or extinction?",
    }
)

phase8.EXACT["science/16-earth-planetary/technology.md"].update(
    {
        "5. **System Output**: The supercomputer outputs petabytes of data representing the simulated future state of the climate, which is then analyzed and visualized.":
            "5. **System output:** The computation produces large multidimensional datasets representing model states, diagnostics, ensembles, and uncertainty information for analysis and visualisation.",
    }
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
