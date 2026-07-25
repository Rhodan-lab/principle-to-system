#!/usr/bin/env python3
"""Apply the focused Phase 8 scientific review to Modules 13–16."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW_DATE = "2026-07-26"
FILENAMES = ("overview.md", "technology.md", "explore.md")
MODULES = {
    "13-cells-bioenergetics": {
        "prerequisites": ["07-chemical-bonding", "08-energy-thermodynamics"],
        "connections": ["14-dna-evolution", "15-ecosystems-complex-systems"],
    },
    "14-dna-evolution": {
        "prerequisites": ["07-chemical-bonding", "13-cells-bioenergetics"],
        "connections": ["15-ecosystems-complex-systems"],
    },
    "15-ecosystems-complex-systems": {
        "prerequisites": ["04-probability-statistics", "13-cells-bioenergetics", "14-dna-evolution"],
        "connections": ["16-earth-planetary"],
    },
    "16-earth-planetary": {
        "prerequisites": ["08-energy-thermodynamics", "09-motion-forces", "12-fluids-materials", "15-ecosystems-complex-systems"],
        "connections": [],
    },
}

ALIASES = {
    "14-genetics-molecular-biology": "14-dna-evolution",
    "15-physiology-systems": "15-ecosystems-complex-systems",
    "15-ecology-systems": "15-ecosystems-complex-systems",
    "16-climate-earth-systems": "16-earth-planetary",
    "Module 14 (Genetics and Molecular Biology)": "Module 14 (DNA, Gene Expression, Inheritance, and Evolution)",
    "Module 15 (Physiology and Systems)": "Module 15 (Ecosystems, Feedback, Networks, and Complex Systems)",
    "Module 16: Climate and Earth Systems": "Module 16: Earth and Planetary Systems",
    "18-agricultural-engineering": "20-sensors-control-infrastructure",
    "22-environmental-control-systems": "20-sensors-control-infrastructure",
}

EXACT = {
    "science/13-cells-bioenergetics/overview.md": {
        "How do living systems extract, transform, and utilize energy to maintain order in a universe that tends toward entropy?":
            "How do living systems acquire and transform energy while exporting entropy and matter to maintain organised, non-equilibrium states?",
        "**Adenosine Triphosphate (ATP)** serves as the primary energy currency of the cell. The hydrolysis of its terminal phosphoanhydride bond releases a significant amount of free energy, which is used to drive unfavorable reactions, transport molecules, and perform mechanical work.":
            "**Adenosine triphosphate (ATP)** is a widely used intermediate in cellular energy coupling. ATP hydrolysis is favourable under many cellular conditions because the products have lower Gibbs free energy; coupling mechanisms, rather than bond breaking alone, allow that free-energy change to drive synthesis, transport, and mechanical work.",
        "**Enzymes** are biological catalysts, predominantly proteins, that accelerate chemical reactions by lowering the activation energy barrier. They do not alter the thermodynamic equilibrium of a reaction but dictate the rate at which equilibrium is approached.":
            "**Enzymes** are biological catalysts, usually proteins but sometimes RNA, that accelerate reactions by stabilising transition-state pathways and organising reacting groups. They change kinetics, not the equilibrium constant or overall reaction Gibbs free energy.",
        "Passive transport (facilitated diffusion) allows molecules to move down their electrochemical gradients without energy input.":
            "Facilitated diffusion moves solutes down electrochemical-potential gradients without direct coupling to metabolic energy, although the gradients themselves may have been established by energy-consuming processes.",
        "Pyruvate is transported into the mitochondrial matrix, oxidized to acetyl-CoA, and fully degraded to $CO_2$.":
            "Pyruvate oxidation produces acetyl-CoA before the cycle; the acetyl groups entering the cycle are oxidised, while carbon accounting across individual turns is more subtle than a one-turn ‘complete degradation’ picture.",
        "The light-independent reactions (Calvin cycle) in the stroma use this ATP and NADPH to fix $CO_2$ into organic molecules.":
            "Carbon-fixation reactions in the stroma use ATP and reducing power from the light reactions; they are not directly photon-driven, but they are not independent of light-supplied products and regulation.",
        "- **Gibbs Free Energy Change ($\\Delta G$):** Determines the spontaneity of a reaction. $\\Delta G < 0$ indicates an exergonic, spontaneous process.":
            "- **Gibbs free-energy change ($\\Delta G$):** Under stated temperature, pressure, composition, and work constraints, its sign indicates thermodynamic direction relative to equilibrium; it does not determine reaction rate.",
        "- **Michaelis Constant ($K_M$):** The substrate concentration at which the reaction rate is half of $V_{\\max}$. It is an inverse measure of the enzyme's affinity for its substrate.":
            "- **Michaelis constant ($K_M$):** For the simple Michaelis–Menten mechanism, the substrate concentration giving half of $V_{\\max}$. It is a compound kinetic parameter and equals a dissociation constant only under additional conditions.",
        "- **ATP Yield:** The theoretical maximum yield of ATP from the complete oxidation of one glucose molecule is approximately 30-32 ATP in eukaryotes, though the actual yield is often lower due to proton leakage and transport costs.":
            "- **ATP yield:** A model-dependent accounting quantity. Textbook estimates for aerobic glucose oxidation depend on shuttle use, proton-to-ATP stoichiometry, transport costs, substrate, tissue, and coupling efficiency; cells do not realise one universal integer yield.",
        "$$ \\Delta G = \\Delta G^\\circ + RT \\ln Q $$":
            "$$ \\Delta G = \\Delta G^\\circ + RT \\ln Q $$",
        "Where $C_{in}$ and $C_{out}$ are the concentrations of the ion inside and outside the cell, $z$ is the charge of the ion, $F$ is Faraday's constant, and $\\Delta \\psi$ is the membrane potential.":
            "For transport from outside to inside, $C_{in}/C_{out}$ is an ideal dilute-solution approximation to the activity ratio, $z$ is ionic charge number, and $\\Delta\\psi=\\psi_{in}-\\psi_{out}$; reversing direction reverses the free-energy change.",
    },
    "science/13-cells-bioenergetics/technology.md": {
        "Synthetic membranes may be integrated into the system to continuously separate the product from the reaction mixture, preventing product inhibition and driving the reaction forward.":
            "Synthetic membranes may continuously separate products from the broth, reducing inhibition or simplifying downstream processing. Product removal changes reaction driving force only when it changes relevant activities and the process is thermodynamically coupled.",
        "- **Thermodynamic Limits:** The overall process must be exergonic. Energy inputs (e.g., aeration, agitation) must not exceed the value of the product.":
            "- **Thermodynamic and energy constraints:** Endergonic transformations can operate when coupled to external energy or favourable reactions. Design therefore tracks free-energy requirements, heat removal, oxygen transfer, exergy losses, and the chosen economic boundary rather than requiring every overall process to be exergonic.",
        "Metabolic engineering aims to maximize the theoretical yield by eliminating competing pathways and optimizing ATP and redox balances.":
            "Metabolic engineering balances product yield, titre, rate, redox and ATP demands, growth, robustness, and genetic stability. Removing a competing pathway can improve yield but can also create toxic accumulation or reduce cellular resilience.",
        "Bioprocesses must adhere to biosafety regulations to prevent the release of genetically modified organisms (GMOs) into the environment.":
            "Bioprocess containment and oversight are selected through organism-, construct-, scale-, and process-specific risk assessment; requirements differ across jurisdictions and applications.",
    },
    "science/13-cells-bioenergetics/explore.md": {
        "Place a few drops of food coloring into a glass of cold water and another into a glass of hot water.":
            "Place equal drops of food colouring into room-temperature water and safely warmed water prepared by an adult or teacher; do not handle near-boiling water.",
        "$K_M$ is the substrate concentration required to reach half of $V_{\\max}$, reflecting the enzyme's affinity for the substrate.":
            "$K_M$ is the substrate concentration giving half of $V_{\\max}$ in the simple model; it is not automatically a direct affinity measurement.",
        "An increased apparent $K_M$ means more substrate is needed to reach the same reaction rate, indicating a lower effective affinity.":
            "An increased apparent $K_M$ means more substrate is needed to reach half-maximal rate under these conditions; the parameter shift is consistent with the competitive-inhibition model without making $K_M$ a universal binding constant.",
    },
    "science/14-dna-evolution/overview.md": {
        "At the cellular level, cells divide and replicate, requiring the exact duplication of their genetic material.":
            "Before cell division, genetic material is copied with high fidelity, while proofreading and repair reduce—but do not eliminate—replication errors.",
        "**Gene Expression:** The process by which the information encoded in a gene is used to direct the assembly of a protein molecule. It involves two main stages: transcription and translation.":
            "**Gene expression:** The regulated use of gene information to produce a functional RNA or, for protein-coding genes, an RNA that is translated into protein. Expression includes transcription, RNA processing and turnover, translation where applicable, and multiple layers of regulation.",
        "**Mutation:** A change in the nucleotide sequence of an organism's DNA. Mutations are the ultimate source of genetic variation.":
            "**Mutation:** A heritable change in genetic sequence or structure. Mutation creates new variants, while recombination, segregation, drift, selection, and gene flow redistribute or filter variation.",
        "**Natural Selection:** The differential survival and reproduction of individuals due to differences in phenotype. It is a key mechanism of evolution.":
            "**Natural selection:** Differential reproductive contribution associated with heritable phenotypic differences in a particular environment; survival matters only insofar as it affects reproduction or inclusive fitness.",
        "DNA polymerase III then adds deoxyribonucleotides to the 3' end of the primer, synthesizing the new strand in the 5' to 3' direction. On the leading strand, synthesis is continuous. On the lagging strand, synthesis is discontinuous, occurring in short segments called Okazaki fragments. DNA polymerase I later replaces the RNA primers with DNA, and DNA ligase seals the nicks between the fragments [2].":
            "Replicative DNA polymerases extend primers in the 5' to 3' direction. Leading-strand synthesis is largely continuous and lagging-strand synthesis forms Okazaki fragments; primer removal, gap filling, proofreading, repair, and ligation involve different protein systems in bacteria, archaea, and eukaryotes, so bacterial polymerase names are not universal [2].",
        "| Mutation Rate | The frequency of new mutations in a single gene or organism over time. | $\\sim 10^{-8}$ per base pair per generation (Human) |":
            "| Mutation Rate | Frequency of new variants per site, genome, cell division, or generation; estimates depend on organism, genomic region, and method. | Context-dependent |",
        "| Translation Rate | The speed at which a ribosome synthesizes a polypeptide. | $\\sim 10-20$ amino acids per second (Prokaryotes) |":
            "| Translation Rate | Polypeptide elongation rate, dependent on organism, cell state, transcript, codon context, and measurement method. | Context-dependent |",
        "*   $p$: Frequency of the dominant allele (dimensionless).":
            "*   $p$: Frequency of allele $A$ (dimensionless); dominance is a phenotype relationship, not a frequency label.",
        "*   $w$: Relative fitness, a measure of reproductive success (dimensionless, $0 \\le w \\le 1$).":
            "*   $w$: Relative fitness on a chosen non-negative scale; it is often normalised, but the symbols are not inherently restricted to $0$–$1$.",
    },
    "science/14-dna-evolution/technology.md": {
        "*   **The Central Dogma:** The predictable flow of information from DNA to RNA to protein enables the engineering of organisms to produce specific proteins by introducing the corresponding DNA sequences.":
            "*   **Information flow and regulation:** DNA can be transcribed into coding or non-coding RNA, and coding RNA can be translated into protein. Reverse transcription and RNA genomes are important extensions, and expression requires compatible regulatory context.",
        "*   **Evolutionary Conservation:** Because the fundamental mechanisms of gene expression are conserved across all domains of life, genes from one organism can often be expressed in a completely different organism (e.g., human insulin produced in bacteria).":
            "*   **Evolutionary conservation with context:** Shared molecular machinery permits cross-species expression in many cases, but promoter recognition, RNA processing, codon use, protein folding, modification, localisation, and toxicity can prevent functional expression.",
        "Because each cycle doubles the amount of target DNA, 30 cycles can produce over a billion copies of a specific DNA sequence from a single starting molecule":
            "Under an ideal efficiency of two, each cycle doubles target molecules and $2^{30}$ is about one billion; real amplification efficiency falls below the ideal and contamination, inhibitors, primer design, and stochastic effects matter",
        "*   **Plasmid Loss:** Host cells may eject recombinant plasmids if they do not provide a selective advantage (which is why antibiotic resistance genes are often included in vectors to force the cells to retain them).":
            "*   **Construct loss:** Cells can lose or rearrange engineered DNA when it imposes a burden. Regulated laboratory systems may use selectable markers or chromosomal integration, with marker choice governed by biosafety and application constraints.",
    },
    "science/14-dna-evolution/explore.md": {
        "This is known as a \"silent mutation.\" It alters the genotype (the DNA sequence) but does not affect the phenotype (the protein sequence and function).":
            "This is a synonymous substitution: the encoded amino-acid sequence is unchanged. It may still affect RNA structure, splicing, translation rate, expression, or fitness, so unchanged protein sequence does not guarantee no phenotypic effect.",
    },
    "science/15-ecosystems-complex-systems/overview.md": {
        "How do vast numbers of interacting biological organisms and their physical environments self-organise into stable, enduring structures?":
            "How do interacting organisms and physical environments generate changing patterns, functions, and feedbacks across scales?",
        "with significant losses at each transfer (typically around 90% lost as heat, following the laws of thermodynamics).":
            "with transfer efficiency varying among organisms, resources, ecosystems, and definitions; respiration, unconsumed biomass, waste, and decomposer pathways all affect the accounting.",
        "This density dependence constrains growth, leading to a carrying capacity.":
            "Density dependence can constrain growth, but the effective carrying-capacity parameter changes with resources, climate, interactions, behaviour, and spatial structure.",
        "A highly modular food web can contain the impact of a species extinction within a single module, preventing a cascading collapse across the entire ecosystem.":
            "Modularity and weak cross-module links can sometimes limit disturbance propagation, but outcomes depend on interaction strengths, redundancy, directionality, adaptive responses, and which nodes or functions are lost.",
        "This model produces continuous oscillations in both populations, illustrating a simple dynamic equilibrium driven by coupled feedback loops.":
            "Under its ideal assumptions, the classical model has neutrally stable closed orbits whose amplitude depends on initial conditions; this is not a generally attracting equilibrium and is structurally fragile to added realism.",
        "$r$ is a parameter representing the combined rate of reproduction and starvation.":
            "$r$ is a dimensionless control parameter of the discrete map; mapping it to biological rates requires an explicit derivation and time-step definition.",
        "Real ecosystems feature complex functional responses (e.g., predators becoming satiated) and spatial heterogeneity, which dampen these oscillations and promote stability.":
            "Real ecosystems include nonlinear functional responses, delays, stochasticity, evolution, spatial structure, and resource limits; these additions may damp, amplify, destabilise, or qualitatively change oscillations depending on parameters.",
    },
    "science/15-ecosystems-complex-systems/technology.md": {
        "The principle of competitive exclusion is used to manage microbial populations, while the concept of carrying capacity dictates the sizing and loading rates of biological reactors.":
            "Competition, facilitation, predation, metabolic complementarity, residence time, and substrate loading all shape microbial communities. Reactor sizing uses kinetic, hydraulic, stoichiometric, mass-transfer, and reliability models rather than a single fixed carrying capacity.",
        "where every atom of carbon, oxygen, and water must be continuously recycled to sustain human life indefinitely.":
            "where material loops must be regenerated for long missions while leakage, accumulation, trace contaminants, component ageing, and backup requirements are explicitly managed; indefinite closure is not assumed.",
        "Complex organic molecules (measured as Biological Oxygen Demand, or BOD) are broken down":
            "Biodegradable organic loading, partly characterised by biochemical oxygen demand (BOD), is transformed",
        "A well-designed constructed wetland can achieve >90% removal of BOD and suspended solids, and 70-90% removal of nitrogen.":
            "Removal performance varies widely with influent, wetland type, climate, hydraulic loading, residence time, media, vegetation, season, maintenance, and the chosen statistical boundary; design must use site-specific evidence rather than universal percentages.",
        "Engineered ecosystems are generally highly reliable due to their internal redundancy; if one microbial species fails, another often fills its niche.":
            "Functional diversity can provide redundancy, but engineered ecosystems can also fail through correlated stress, missing functions, slow recovery, hidden dependencies, or loss of key populations; reliability must be demonstrated rather than assumed.",
    },
    "science/16-earth-planetary/overview.md": {
        "This process is the primary driver of **plate tectonics**, the theory that Earth's outer shell is divided into several plates that glide over the mantle.":
            "Mantle dynamics, slab buoyancy, ridge forces, plate-boundary stresses, and lithospheric rheology are coupled in **plate tectonics**; no single mechanism explains every plate's motion.",
        "**Thermohaline circulation** is a part of the large-scale ocean circulation that is driven by global density gradients created by surface heat and freshwater fluxes [2].":
            "Large-scale overturning circulation is shaped by wind, tides, mixing, basin geometry, and buoyancy changes from heat and freshwater fluxes; density-driven overturning is one component, not an isolated conveyor [2].",
        "**Radiative forcing** is the difference between incoming energy from the sun and outgoing energy radiated back to space [3].":
            "**Effective radiative forcing** is the change in net downward radiative flux at the top of the atmosphere after rapid adjustments but before the surface-temperature response; planetary energy imbalance is a related but distinct quantity [3].",
        "This convective flow exerts a drag on the overlying lithospheric plates, contributing to their movement.":
            "Mantle flow and plates interact mechanically in both directions, while negative buoyancy of subducting slabs, ridge forces, boundary stresses, and lithospheric strength contribute differently among plates.",
        "Greenhouse gases in the atmosphere, such as water vapor, carbon dioxide, and methane, are transparent to shortwave radiation but absorb and re-emit longwave radiation, trapping heat in the lower atmosphere.":
            "Greenhouse gases have wavelength-dependent absorption and emission. By altering infrared optical depth and the altitude and temperature from which radiation escapes to space, concentration changes perturb the top-of-atmosphere energy balance; ‘trapping heat’ is only a shorthand.",
        "- **Radiative forcing**: Measured in watts per square meter ($W/m^2$), quantifying the change in the net, downward minus upward, radiative flux at the tropopause [3].":
            "- **Effective radiative forcing**: Measured in watts per square metre ($W/m^2$), conventionally evaluated at the top of atmosphere after rapid adjustments and before the surface-temperature response [3].",
        "Solving for $T_e$ gives the temperature the Earth would have without a greenhouse effect.":
            "Solving for $T_e$ gives an effective emission temperature for this uniform blackbody-like balance, not a direct prediction of surface temperature and not a complete ‘no-greenhouse Earth’ model.",
        "The logarithmic approximation for $CO_2$ radiative forcing assumes that the absorption bands of $CO_2$ are saturated at the center and forcing increases primarily through the broadening of these bands.":
            "The logarithmic approximation is an empirical fit over a specified concentration range and spectral atmosphere; band wings, overlap with other gases, temperature structure, and rapid adjustments make the coefficient model- and definition-dependent.",
        "Climate models are just guesses.":
            "Climate models are unconstrained guesses.",
        "they successfully reproduce past and present climate trends and provide robust projections of future warming under different emission scenarios [4].":
            "their credibility is assessed through conservation checks, process tests, hindcasts, intercomparison, observations, emergent behaviour, and quantified uncertainty; projections are conditional on forcing scenarios and model structure [4].",
    },
    "science/16-earth-planetary/technology.md": {
        "Doubling the resolution of a 3D model requires roughly an eight-fold increase in computing power.":
            "Increasing three-dimensional resolution raises grid-cell count steeply and can require shorter time steps, more communication, and more expensive parameterisations; the total cost increase is architecture- and solver-dependent and can exceed the simple cell-count factor.",
        "The Argo array, for example, maintains over 3,800 active floats, providing unprecedented coverage of the upper 2,000 meters of the ocean [2].":
            "The Argo programme maintains a changing international array of profiling floats; core floats typically sample temperature, salinity, and pressure through the upper ocean, while Deep and biogeochemical extensions broaden depth and variables [2].",
        "- **Model Divergence**: In climate modeling, small errors in initial conditions or parameterizations can grow over time due to the chaotic nature of the fluid equations, leading to inaccurate long-term projections.":
            "- **Forecast and projection uncertainty:** Initial-condition errors limit detailed weather prediction, while long-term climate projections focus on distributions and forced responses. Structural assumptions, parameterisations, forcing scenarios, internal variability, and numerical choices contribute distinct uncertainties.",
        "Supercomputers used for climate modeling consume massive amounts of electricity (often megawatts), contributing to carbon emissions unless powered by renewable energy.":
            "High-performance computing has substantial electricity, cooling, hardware, and embodied-material demands; lifecycle impact depends on workload, facility efficiency, electricity mix, hardware utilisation, and replacement cycle.",
    },
}

SOURCE_BLOCKS = {
    "13-cells-bioenergetics": """1. NCBI Bookshelf. *Electron-Transport Chains and Their Proton Pumps*. https://www.ncbi.nlm.nih.gov/books/NBK26904/
2. NCBI Bookshelf. *Principles of Membrane Transport*. https://www.ncbi.nlm.nih.gov/books/NBK26815/
3. NCBI Bookshelf. *Protein Function*. https://www.ncbi.nlm.nih.gov/books/NBK26911/
4. OpenStax. *Regulation of Cellular Respiration*. https://openstax.org/books/biology-2e/pages/7-7-regulation-of-cellular-respiration
5. NCBI Bookshelf. *Bioenergetics and Metabolism*. https://www.ncbi.nlm.nih.gov/books/NBK9911/
6. NCBI Bookshelf. *Cell Membranes*. https://www.ncbi.nlm.nih.gov/books/NBK9928/""",
    "14-dna-evolution": """1. NCBI Bookshelf. *DNA Replication Mechanisms*. https://www.ncbi.nlm.nih.gov/books/NBK26850/
2. Nature Education. *DNA Transcription*. https://www.nature.com/scitable/topicpage/dna-transcription-426/
3. Nature Education. *Translation: DNA to mRNA to Protein*. https://www.nature.com/scitable/topicpage/translation-dna-to-mrna-to-protein-393/
4. OpenStax. *Mechanisms of Evolution*. https://openstax.org/books/concepts-biology/pages/11-2-mechanisms-of-evolution
5. National Human Genome Research Institute. *DNA Replication*. https://www.genome.gov/genetics-glossary/DNA-Replication
6. National Human Genome Research Institute. *Gene Expression*. https://www.genome.gov/genetics-glossary/Gene-Expression
7. National Human Genome Research Institute. *Evolution*. https://www.genome.gov/genetics-glossary/Evolution""",
    "15-ecosystems-complex-systems": """1. Holling, C. S. *Resilience and Stability of Ecological Systems*. https://www.annualreviews.org/doi/abs/10.1146/annurev.es.04.110173.000245
2. May, R. M. *Will a Large Complex System Be Stable?* https://www.nature.com/articles/238413a0
3. Scheffer, M., et al. *Catastrophic Shifts in Ecosystems*. https://www.nature.com/articles/35098000
4. Dunne, J. A., et al. *Food-web Structure and Network Theory*. https://www.pnas.org/doi/abs/10.1073/pnas.192407699
5. U.S. Environmental Protection Agency. *Guiding Principles for Constructed Treatment Wetlands*. https://www.epa.gov/wetlands/guiding-principles-constructed-treatment-wetlands-providing-water-quality-and-wildlife
6. European Space Agency. *MELiSSA Environmental Control and Life Support Research*. https://www.esa.int/Enabling_Support/Space_Engineering_Technology/Life_Support_and_Physical_Sciences/Research_and_development""",
    "16-earth-planetary": """1. U.S. Geological Survey. *This Dynamic Earth: The Story of Plate Tectonics*. https://pubs.usgs.gov/gip/dynamic/dynamic.html
2. Intergovernmental Panel on Climate Change. *AR6 WGI Chapter 7: Earth's Energy Budget, Climate Feedbacks, and Climate Sensitivity*. https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-7/
3. NOAA Atlantic Oceanographic and Meteorological Laboratory. *Argo Program*. https://www.aoml.noaa.gov/argo/
4. Ramaswamy, V., et al. *Radiative Forcing of Climate*. https://journals.ametsoc.org/view/journals/amsm/59/1/amsmonographs-d-19-0001.1.xml
5. Bercovici, D. *The Generation of Plate Tectonics from Mantle Convection*. https://www.sciencedirect.com/science/article/pii/S0012821X02010099
6. Ringler, A. T., et al. *The Global Seismographic Network*. https://journals.sagepub.com/doi/10.1193/060414EQS082M""",
}

SECTION_REPLACEMENTS = {
    ("science/13-cells-bioenergetics/explore.md", 5): """## 5. Household and browser-based explorations

- **Potato-strip osmosis:** Cut equal potato strips with adult or teacher supervision. Place them in labelled cups containing water and pre-prepared salt solutions, then measure mass or length changes. Do not taste laboratory samples. Compare observations with water-potential and membrane models rather than saying water moves to ‘balance solute concentrations.’
- **Yeast gas-production observation:** Use a small, flexible balloon or a loosely covered cup rather than a rigid sealed vessel. Compare room-temperature mixtures with different sugar conditions, keep quantities small, and stop if pressure or foaming becomes excessive. Gas production is evidence of metabolism but does not by itself measure ATP yield.
- **Browser exploration:** Use an institutional animation or simulation of oxidative phosphorylation. Track electron transfer, proton pumping, membrane potential, ATP synthase, oxygen consumption, and heat separately; identify which variables the model omits.
""",
    ("science/13-cells-bioenergetics/explore.md", 8): """## 8. Transfer questions

- In a model, block electron transfer to the terminal acceptor without naming or handling any real inhibitor. Predict changes in proton pumping, membrane potential, oxygen consumption, NADH oxidation, ATP synthesis, and heat production. Which predictions depend on cell type and timescale?
- In industrial biotechnology, how would changing enzyme expression alter flux, burden, redox balance, growth, byproducts, and stability rather than simply ‘maximising one pathway’?
- How do electrochemical gradients and selective channels contribute to an action potential, and why is a membrane voltage not itself a flow of electrical current?
""",
    ("science/14-dna-evolution/explore.md", 1): """## 1. Observation prompts

- Use an anonymised or fictional pedigree containing clearly defined single-gene traits. Which inheritance patterns are consistent with the data, and which alternatives remain possible? Avoid inferring sensitive family or health information from appearance.
- Observe visible variation in a common local plant or animal population without touching, feeding, or disturbing organisms. Which differences are measurable, and which environmental variables could also explain them?
- Compare published diagrams or museum images of homologous structures. Separate similarity due to common ancestry from similarity caused by convergent function.
""",
    ("science/14-dna-evolution/explore.md", 2): """## 2. Prediction questions

- In a digital population model, suppose one heritable variant has higher reproductive success under a changed environment. Predict allele-frequency trajectories while varying population size, dominance, migration, and drift.
- A promoter mutation changes transcription-factor or polymerase occupancy. Why can expression increase, decrease, remain unchanged, or become condition-dependent rather than following a single ‘tighter binding means more expression’ rule?
- If a small group colonises an isolated habitat, how might sampling, drift, inbreeding, migration, and later selection alter diversity relative to the source population?
""",
    ("science/14-dna-evolution/explore.md", 5): """## 5. Household and browser-based explorations

- **Genome-browser exploration:** Use an official genome browser or NCBI sequence record for a non-sensitive example gene, such as a plant pigment or bacterial metabolic gene. Identify exons or coding regions, strand direction, transcripts, and evidence annotations. Do not treat a database label as proof of function without checking evidence.
- **Population-genetics simulation:** Use a browser simulator or spreadsheet to compare drift, migration, selection, and mutation. Run repeated trials; a single stochastic trajectory is not a general result.
- **Replication-fidelity model:** Simulate copying a symbolic sequence with a defined error probability, then add proofreading and repair stages. Compare per-copy error, total errors, and the distribution across many trials.
""",
    ("science/15-ecosystems-complex-systems/explore.md", 1): """## 1. Observation prompts

- Observe a puddle, birdbath, moss patch, or leaf-litter area from a safe distance without touching standing water, larvae, fungi, or unknown organisms. Record light, moisture, visible producers, consumers, and disturbance, while recognising that many interactions are not directly observable.
- In a city park or garden, map a provisional interaction network from repeated observations. Distinguish direct evidence of feeding from co-occurrence, and include decomposers and non-feeding interactions where evidence exists.
- Compare time-series photographs or public sensor data before and after rainfall, drought, mowing, fire, or nutrient change. Which feedbacks are plausible, and what additional measurements would distinguish them?
""",
    ("science/15-ecosystems-complex-systems/explore.md", 3): """## 3. Worked reasoning examples

**Question:** Why are very long food chains uncommon, and why is a universal ‘10% rule’ inadequate?

**Reasoning:**
1. Define the measured quantity: ingestion, assimilation, production, biomass, or energy flow give different efficiencies.
2. At each transfer, some production is not consumed, some ingested material is not assimilated, and organisms use assimilated energy for maintenance, movement, reproduction, and respiration.
3. Transfer efficiency varies with temperature, body size, food quality, metabolic strategy, ecosystem, and timescale.
4. Build a sensitivity table using several plausible efficiencies rather than one fixed percentage. Repeated multiplication still reduces energy or production available to higher levels, but chain length also depends on habitat size, productivity, omnivory, subsidies, and population viability.
""",
    ("science/15-ecosystems-complex-systems/explore.md", 4): """## 4. Thought experiments

- **Closed-system accounting model:** Draw a sealed-material but open-energy system containing producers, consumers, decomposers, water, gases, and mineral nutrients. Track carbon, nitrogen, oxygen, water, heat, and stored chemical energy. Which reservoirs or trace compounds accumulate, and why does material recycling not imply unlimited stability?
- **Trophic-cascade uncertainty:** Model predator removal as a set of competing causal pathways involving herbivore behaviour, abundance, vegetation, climate, hunting, disease, and spatial movement. Which observations would be needed before claiming downstream geomorphic change?
""",
    ("science/16-earth-planetary/explore.md", 5): """## 5. Household and browser-based explorations

- **Convection simulation:** Use a browser-based fluid or mantle-convection simulation rather than heating a dish on a stove. Change viscosity, heating location, boundary conditions, and density contrast; explain why a low-viscosity water model does not reproduce solid-mantle rheology.
- **Rotation on a sphere:** Use a digital globe or removable tape on a ball rather than a permanent marker. Compare a straight path in an inertial frame with its apparent deflection in a rotating frame.
- **Earth-data exploration:** Use an institutional wind, ocean, earthquake, or climate-data viewer. Record variable definitions, units, timestamps, coverage gaps, and whether the display shows observations, reanalysis, or model output.
""",
    ("science/16-earth-planetary/explore.md", 8): """## 8. Transfer questions

- How would rotation rate, planetary radius, atmospheric depth, heating pattern, and friction jointly affect circulation on another planet? Avoid attributing every difference to Coriolis effects alone.
- Compare hypothetical changes in atmospheric composition using a radiative-transfer model. Why does increasing a greenhouse gas not translate directly into a fixed surface-temperature change without feedbacks and ocean heat uptake?
- For a rocky exoplanet, list the unknown material properties and boundary conditions required before inferring plate tectonics from planet mass alone.
""",
}

BANNED = (
    "Wikipedia contributors",
    "cyanide",
    "rubbing alcohol",
    "stretch a balloon over the mouth of the bottle",
    "hermetically sealed glass jar",
    "10% rule",
    "exact duplication of their genetic material",
    "DNA polymerase III then",
    "primary driver of **plate tectonics**",
    "transparent to shortwave radiation",
    "over 3,800 active floats",
    ">90% removal of BOD",
    "70-90% removal of nitrogen",
    "sustain human life indefinitely",
)


def expected_slug(module: str, filename: str) -> str:
    return module if filename == "overview.md" else f"{module}-{filename.removesuffix('.md')}"


def set_frontmatter(text: str, module: str, filename: str) -> str:
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated frontmatter")
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    order: list[str] = []
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        data[key] = value.strip()
        order.append(key)
    data["slug"] = expected_slug(module, filename)
    data["module"] = f'"Module {module[:2]}"'
    data["domain"] = "science"
    data["status"] = "reviewed"
    data["prerequisites"] = "[" + ", ".join(MODULES[module]["prerequisites"]) + "]"
    data["connections"] = "[" + ", ".join(MODULES[module]["connections"]) + "]"
    data["last_reviewed"] = REVIEW_DATE
    data["content_license"] = "CC-BY-4.0"
    canonical = ["title", "slug", "module", "domain", "status", "prerequisites", "connections", "last_reviewed", "content_license"]
    lines = []
    for key in canonical:
        if key in data:
            lines.append(f"{key}: {data[key]}")
    for key in order:
        if key not in canonical:
            lines.append(f"{key}: {data[key]}")
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def replace_section(text: str, number: int, replacement: str, rel: str) -> str:
    marker = f"## {number}. "
    if replacement.strip() in text:
        return text
    pattern = re.compile(rf"(?ms)^## {number}\. .*?(?=^## {number + 1}\. |\Z)")
    if not pattern.search(text):
        raise ValueError(f"{rel}: section {number} not found")
    return pattern.sub(replacement.rstrip() + "\n\n", text, count=1)


def replace_sources(text: str, module: str, filename: str, rel: str) -> str:
    number = {"overview.md": 12, "technology.md": 13, "explore.md": 11}[filename]
    replacement = f"## {number}. Sources\n\n{SOURCE_BLOCKS[module]}\n"
    pattern = re.compile(rf"(?ms)^## {number}\. Sources\s*\n.*\Z")
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    return text.rstrip() + "\n\n" + replacement


def transform_file(path: Path, module: str) -> tuple[str, list[str]]:
    rel = path.relative_to(ROOT).as_posix()
    filename = path.name
    original = path.read_text(encoding="utf-8")
    text = set_frontmatter(original, module, filename)
    notes: list[str] = []

    for old, new in ALIASES.items():
        if old in text:
            text = text.replace(old, new)
            notes.append(f"alias:{old}")

    for old, new in EXACT.get(rel, {}).items():
        if old in text:
            text = text.replace(old, new)
            notes.append(f"replace:{old[:45]}")
        elif new not in text:
            raise ValueError(f"{rel}: expected legacy text not found: {old[:80]}")

    for (section_rel, number), replacement in SECTION_REPLACEMENTS.items():
        if section_rel == rel:
            text = replace_section(text, number, replacement, rel)
            notes.append(f"section:{number}")

    text = replace_sources(text, module, filename, rel)
    text = text.rstrip() + "\n"
    return text, notes


def update_index(write: bool) -> list[str]:
    path = ROOT / "INDEX.md"
    text = path.read_text(encoding="utf-8")
    updated = text
    for number in ("13", "14", "15", "16"):
        updated, count = re.subn(
            rf"(?m)^(\|\s*{number}\s*\|.*\|\s*)(Draft|Reviewed|Complete|Blocked)(\s*\|\s*)$",
            rf"\1Reviewed\3",
            updated,
        )
        if count != 1:
            raise ValueError(f"INDEX.md: expected one Module {number} status row, found {count}")
    if write and updated != text:
        path.write_text(updated, encoding="utf-8")
    return ["INDEX.md changed"] if updated != text else []


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    changed: list[str] = []
    for module in MODULES:
        module_dir = ROOT / "science" / module
        for filename in FILENAMES:
            path = module_dir / filename
            try:
                transformed, _ = transform_file(path, module)
            except (OSError, ValueError) as exc:
                errors.append(str(exc))
                continue
            original = path.read_text(encoding="utf-8")
            if transformed != original:
                changed.append(path.relative_to(ROOT).as_posix())
                if args.write:
                    path.write_text(transformed, encoding="utf-8")
    try:
        changed.extend(update_index(write=args.write))
    except (OSError, ValueError) as exc:
        errors.append(str(exc))

    if errors:
        print("Phase 8 transformation errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if args.check and changed:
        print("Phase 8 review is not idempotent:", file=sys.stderr)
        for item in changed:
            print(f"- {item}", file=sys.stderr)
        return 1
    print(f"Phase 8 transformation passed; changed={len(changed)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
