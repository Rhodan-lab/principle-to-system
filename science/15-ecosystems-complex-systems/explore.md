---
title: "Explore: Ecosystems, Feedback, Networks, and Complex Systems"
slug: 15-ecosystems-complex-systems-explore
module: "Module 15"
domain: science
status: draft
prerequisites: [04-probability-statistics, 13-cells-bioenergetics, 14-dna-evolution]
connections: [16-earth-planetary]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Explore: Ecosystems, Feedback, Networks, and Complex Systems

## 1. Observation prompts

- **The Micro-Ecosystem:** Find a small, undisturbed puddle, a birdbath, or a patch of moss. Observe it over several days. Can you identify the primary producers (green algae or moss) and the consumers (insects, larvae)? How does the system change after a heavy rain or a period of drought?
- **Urban Food Webs:** In a city park or garden, trace a simple food chain. Observe a plant, the insects feeding on it, and the birds feeding on the insects. What happens to the dead leaves on the ground? Try to map out the network of interactions you can physically see.
- **Feedback in Action:** Observe the condensation on a cold glass of water on a humid day. As water droplets form, they release latent heat, slightly warming the glass, which in turn affects the rate of further condensation. Consider how this micro-physical feedback loop mirrors larger ecological feedback mechanisms.

## 2. Prediction questions

- If a highly connected, central species (a "keystone species") is removed from a food web, what is the likely cascade of effects compared to removing a species with only one or two connections?
- In a logistic growth model, if the carrying capacity ($K$) of an environment is suddenly halved due to a permanent drought, how will a population currently at the original carrying capacity respond dynamically over time?
- Consider a shallow lake that is currently clear. If agricultural runoff slowly increases the nutrient load (phosphorus) year by year, will the lake's water quality degrade linearly, or might it exhibit a sudden regime shift? Why?

## 3. Worked reasoning examples

**Question:** Why do most food chains rarely extend beyond four or five trophic levels?

**Reasoning:**
1. **Identify the core principle:** The flow of energy through an ecosystem is governed by the laws of thermodynamics.
2. **Apply the mechanism:** At each trophic level, organisms consume energy. However, a large portion of this energy is used for metabolic processes (respiration, movement) and is ultimately lost as heat. Furthermore, not all biomass from the lower level is consumed or digestible.
3. **Quantify the effect:** On average, only about 10% of the energy stored as biomass in one trophic level is converted to biomass in the next level (the 10% rule).
4. **Synthesise the conclusion:** If a primary producer captures 10,000 units of solar energy, the primary consumer stores 1,000 units, the secondary consumer stores 100 units, the tertiary consumer stores 10 units, and a quaternary consumer would only receive 1 unit. Beyond four or five levels, there is simply not enough residual energy to sustain a viable population of apex predators.

## 4. Thought experiments

- **The Closed Jar:** Imagine you have a large, hermetically sealed glass jar. You place soil, water, a small plant, and a few herbivorous insects inside, then seal it and place it in sunlight. Trace the path of a single carbon atom over a month. What must happen for the system to survive indefinitely? What is the most likely cause of failure?
- **The Trophic Cascade:** Imagine a forest where wolves are the apex predators, hunting deer, which in turn eat tree saplings. If the wolves are entirely removed, trace the causal chain of events over the next fifty years. How might the physical geography of the forest (e.g., the path of a river) change as a result of altering the biological network?

## 5. Household and browser-based explorations

- **NetLogo Web (Browser):** Search for "NetLogo Web" and open the "Wolf Sheep Predation" model in the Biology section of the Models Library. Run the simulation. Observe how the populations oscillate. Experiment with changing the grass regrowth rate or the wolf reproduction rate. Can you find a set of parameters that leads to a stable equilibrium? Can you find parameters that cause the system to collapse?
- **The Logistic Map Calculator (Browser/Spreadsheet):** Open a spreadsheet. In cell A1, enter a starting population ratio (e.g., 0.1). In cell B1, enter a growth rate $r$ (start with 2.5). In cell A2, enter the formula `=B$1*A1*(1-A1)`. Drag this formula down for 50 rows. Plot the results on a line graph. Now, change the $r$ value in B1 to 3.1, then 3.5, then 3.8. Observe the transition from a stable state, to periodic oscillations, to deterministic chaos.

## 6. Model-building prompts

- **Constructing a Network:** Using paper and pencil, draw a food web for a hypothetical ecosystem containing 10 species. Ensure there are producers, herbivores, and carnivores. Calculate the connectance ($C$) of your network. Now, simulate a disturbance by "extinguishing" one species. Redraw the network. How did the connectance change?
- **System Dynamics Diagram:** Draw a causal loop diagram for a local ecosystem you are familiar with. Use arrows to connect variables (e.g., "Prey Population" $\rightarrow$ "Predator Population"). Label the arrows with '+' (positive correlation) or '-' (negative correlation). Identify the reinforcing (positive) and balancing (negative) feedback loops.

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
- **To understand global impacts:** Move on to Module 16: Climate and Earth Systems, to see how these ecological principles scale up to govern the entire biosphere and interact with the atmosphere and oceans.

## 10. Reasoning notes

When analysing complex systems, resist the urge to look for single, linear causes for observed events. In highly connected networks with multiple feedback loops, causality is often circular and distributed. A sudden collapse is rarely the result of the final, proximate trigger (the "straw that broke the camel's back"), but rather the culmination of a long-term erosion of resilience. Always ask: "What are the hidden feedback loops?" and "At what scale is this phenomenon occurring?"
