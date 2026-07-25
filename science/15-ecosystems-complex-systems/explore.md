---
title: "Explore: Ecosystems, Feedback, Networks, and Complex Systems"
slug: 15-ecosystems-complex-systems-explore
module: "Module 15"
domain: science
status: reviewed
prerequisites: [04-probability-statistics, 13-cells-bioenergetics, 14-dna-evolution]
connections: [16-earth-planetary]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Explore: Ecosystems, Feedback, Networks, and Complex Systems

## 1. Observation prompts

- Observe a puddle, birdbath, moss patch, or leaf-litter area from a safe distance without touching standing water, larvae, fungi, or unknown organisms. Record light, moisture, visible producers, consumers, and disturbance, while recognising that many interactions are not directly observable.
- In a city park or garden, map a provisional interaction network from repeated observations. Distinguish direct evidence of feeding from co-occurrence, and include decomposers and non-feeding interactions where evidence exists.
- Compare time-series photographs or public sensor data before and after rainfall, drought, mowing, fire, or nutrient change. Which feedbacks are plausible, and what additional measurements would distinguish them?

## 2. Prediction questions

- If a species with strong measured effects on ecosystem structure is removed, how might outcomes differ from removing a highly connected species? Why are keystone effect, network degree, biomass, and functional uniqueness different quantities?
- In a logistic growth model, if the carrying capacity ($K$) of an environment is suddenly halved due to a permanent drought, how will a population currently at the original carrying capacity respond dynamically over time?
- Consider a shallow lake that is currently clear. If agricultural runoff slowly increases the nutrient load (phosphorus) year by year, will the lake's water quality degrade linearly, or might it exhibit a sudden regime shift? Why?

## 3. Worked reasoning examples

**Question:** Why are very long food chains uncommon, and why is one fixed trophic-transfer percentage inadequate?

**Reasoning:**
1. Define the measured quantity: ingestion, assimilation, production, biomass, or energy flow give different efficiencies.
2. At each transfer, some production is not consumed, some ingested material is not assimilated, and organisms use assimilated energy for maintenance, movement, reproduction, and respiration.
3. Transfer efficiency varies with temperature, body size, food quality, metabolic strategy, ecosystem, and timescale.
4. Build a sensitivity table using several plausible efficiencies rather than one fixed percentage. Repeated multiplication still reduces energy or production available to higher levels, but chain length also depends on habitat size, productivity, omnivory, subsidies, and population viability.

## 4. Thought experiments

- **Closed-system accounting model:** Draw a sealed-material but open-energy system containing producers, consumers, decomposers, water, gases, and mineral nutrients. Track carbon, nitrogen, oxygen, water, heat, and stored chemical energy. Which reservoirs or trace compounds accumulate, and why does material recycling not imply unlimited stability?
- **Trophic-cascade uncertainty:** Model predator removal as a set of competing causal pathways involving herbivore behaviour, abundance, vegetation, climate, hunting, disease, and spatial movement. Which observations would be needed before claiming downstream geomorphic change?

## 5. Household and browser-based explorations

- **NetLogo Web (Browser):** Search for "NetLogo Web" and open the "Wolf Sheep Predation" model in the Biology section of the Models Library. Run the simulation. Observe how the populations oscillate. Experiment with changing the grass regrowth rate or the wolf reproduction rate. Can you find parameters that produce bounded persistence, a steady state, oscillation, or extinction? Can you find parameters that cause the system to collapse?
- **The Logistic Map Calculator (Browser/Spreadsheet):** Open a spreadsheet. In cell A1, enter a starting population ratio (e.g., 0.1). In cell B1, enter a growth rate $r$ (start with 2.5). In cell A2, enter the formula `=B$1*A1*(1-A1)`. Drag this formula down for 50 rows. Plot the results on a line graph. Now, change the $r$ value in B1 to 3.1, then 3.5, then 3.8. Observe the transition from a stable state, to periodic oscillations, to deterministic chaos.

## 6. Model-building prompts

- **Constructing a Network:** Using paper and pencil, draw a food web for a hypothetical ecosystem containing 10 species. Ensure there are producers, herbivores, and carnivores. Calculate the connectance ($C$) of your network. Now, simulate a disturbance by "extinguishing" one species. Redraw the network. How did the connectance change?
- **System Dynamics Diagram:** Draw a causal loop diagram for a local ecosystem you are familiar with. Use arrows to connect variables (e.g., "Prey Population" $\rightarrow$ "Predator Population"). Label each arrow with '+' when an increase in the cause tends to increase the effect, or '-' when it tends to decrease the effect, holding the stated context fixed; these are hypothesised causal signs, not simple correlations. Identify the reinforcing (positive) and balancing (negative) feedback loops.

## 7. Self-explanation questions

- Explain in your own words the difference between a complex system and a complicated system. (Hint: Think about a mechanical watch versus a flock of birds).
- Why is the concept of "carrying capacity" represented as a negative feedback loop in mathematical models?
- Describe how a regime shift in an ecosystem is analogous to a phase transition in physics (like water freezing into ice).

## 8. Transfer questions

- How can the principles of ecological resilience and network topology be applied to design more robust electrical power grids or global supply chains?
- If an economy is viewed as a complex adaptive system, what might represent the "trophic levels," and what acts as the "energy" flowing through the system?
- How do the concepts of positive and negative feedback loops apply to the regulation of human body temperature (homeostasis)?

## 9. Suggested learning paths

- **To deepen mathematical understanding:** Study non-linear dynamics and chaos theory, focusing on bifurcation diagrams and strange attractors.
- **To explore applications:** Investigate the field of ecological engineering and permaculture, looking at how human agricultural systems can be designed to mimic natural ecosystems.
- **To understand global impacts:** Move on to Module 16: Earth and Planetary Systems, to see how these ecological principles scale up to govern the entire biosphere and interact with the atmosphere and oceans.

## 10. Reasoning notes

When analysing complex systems, resist the urge to look for single, linear causes for observed events. In highly connected networks with multiple feedback loops, causality is often circular and distributed. A sudden collapse is rarely the result of the final, proximate trigger (the "straw that broke the camel's back"), but rather the culmination of a long-term erosion of resilience. Always ask: "What are the hidden feedback loops?" and "At what scale is this phenomenon occurring?"

## 11. Sources

1. Holling, C. S. *Resilience and Stability of Ecological Systems*. https://www.annualreviews.org/doi/abs/10.1146/annurev.es.04.110173.000245
2. May, R. M. *Will a Large Complex System Be Stable?* https://www.nature.com/articles/238413a0
3. Scheffer, M., et al. *Catastrophic Shifts in Ecosystems*. https://www.nature.com/articles/35098000
4. Dunne, J. A., et al. *Food-web Structure and Network Theory*. https://www.pnas.org/doi/abs/10.1073/pnas.192407699
5. U.S. Environmental Protection Agency. *Guiding Principles for Constructed Treatment Wetlands*. https://www.epa.gov/wetlands/guiding-principles-constructed-treatment-wetlands-providing-water-quality-and-wildlife
6. European Space Agency. *MELiSSA Environmental Control and Life Support Research*. https://www.esa.int/Enabling_Support/Space_Engineering_Technology/Life_Support_and_Physical_Sciences/Research_and_development
