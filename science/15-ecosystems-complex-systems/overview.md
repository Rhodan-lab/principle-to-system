---
title: "Ecosystems, Feedback, Networks, and Complex Systems"
slug: 15-ecosystems-complex-systems
module: "Module 15"
domain: science
status: reviewed
prerequisites: [04-probability-statistics, 13-cells-bioenergetics, 14-dna-evolution]
connections: [16-earth-planetary]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Ecosystems, Feedback, Networks, and Complex Systems

## 1. The central questions

How do interacting organisms and physical environments generate changing patterns, functions, and feedbacks across scales? Why do some ecosystems absorb massive disturbances and recover, while others collapse abruptly into entirely different states? How do local interactions between predators, prey, and nutrients give rise to emergent properties that cannot be predicted by studying individual species in isolation? 

## 2. Observable phenomena

Ecosystems exhibit phenomena that span multiple scales of space and time. A classic observation is the cyclical fluctuation of predator and prey populations, such as the lynx and snowshoe hare in the boreal forest, where the abundance of one species drives the rise and fall of the other. Another phenomenon is the sudden "greening" of a lake, where clear water abruptly turns into a turbid, algae-dominated state due to nutrient runoff, demonstrating a regime shift. In forests, the spontaneous emergence of spatial patterns, such as the regular spacing of trees in arid environments (e.g., "tiger bush"), reveals self-organisation. Furthermore, the resilience of a coral reef after a hurricane, slowly rebuilding its intricate food web, contrasts sharply with its rapid bleaching and structural collapse under sustained thermal stress.

## 3. Essential concepts

**Complex Adaptive Systems (CAS):** Ecosystems are complex adaptive systems composed of many interacting agents (organisms) that adapt to their environment and to each other. These systems are characterised by non-linear dynamics, where small changes can have disproportionately large effects.

**Trophic Levels and Food Webs:** Organisms are categorised by their trophic level—their position in the flow of energy and matter. Primary producers (plants, algae) form the base, followed by primary consumers (herbivores), secondary consumers (carnivores), and decomposers. A food web is the network topology of these feeding relationships.

**Feedback Loops:** Feedback mechanisms regulate ecosystem dynamics. Positive feedback amplifies changes, driving a system away from its current state (e.g., melting ice reducing albedo, causing more warming). Negative feedback dampens changes, promoting stability (e.g., increased prey density leading to higher predator populations, which then reduce the prey density).

**Emergence and Self-Organisation:** Emergence refers to macroscopic properties arising from microscopic interactions, such that the whole is greater than the sum of its parts. Self-organisation is the process by which structure and order emerge spontaneously without external direction, driven by local rules and feedback.

**Resilience and Regime Shifts:** Ecological resilience is the capacity of a system to absorb disturbance and reorganise while undergoing change so as to still retain essentially the same function, structure, identity, and feedbacks [1]. When a threshold is crossed, a regime shift occurs, moving the ecosystem into an alternative stable state.

## 4. Mechanisms and causal chains

The flow of energy and the cycling of nutrients are the fundamental mechanisms driving ecosystems. Solar energy is captured by autotrophs through photosynthesis, converting carbon dioxide and water into organic compounds. This energy flows unidirectionally through trophic levels, with transfer efficiency varying among organisms, resources, ecosystems, and definitions; respiration, unconsumed biomass, waste, and decomposer pathways all affect the accounting. In contrast, nutrients such as carbon, nitrogen, and phosphorus cycle continuously between the biotic and abiotic components of the system.

Population dynamics are governed by the balance between birth rates, death rates, immigration, and emigration. When resources are abundant, populations can grow exponentially. However, as population density increases, negative feedback mechanisms—such as resource depletion, increased disease transmission, and higher predation rates—intensify. Density dependence can constrain growth, but the effective carrying-capacity parameter changes with resources, climate, interactions, behaviour, and spatial structure.

In complex networks, the topology of interactions determines stability. High connectance (the proportion of possible links that are realised) and modularity (the degree to which a network is compartmentalised) influence how disturbances propagate. Modularity and weak cross-module links can sometimes limit disturbance propagation, but outcomes depend on interaction strengths, redundancy, directionality, adaptive responses, and which nodes or functions are lost.

## 5. Important quantities

- **Biomass ($B$):** The total mass of living matter within a given area or volume, typically measured in kilograms per square metre ($\text{kg m}^{-2}$).
- **Carrying Capacity ($K$):** The maximum population size of a species that the environment can sustain indefinitely, given the food, habitat, water, and other necessities available.
- **Connectance ($C$):** In a food web, the ratio of actual interactions ($L$) to the maximum possible number of interactions ($S^2$, where $S$ is the number of species).
- **Primary Productivity ($P$):** The rate at which solar energy is converted into organic substances by photosynthetic producers, measured in grams of carbon per square metre per year ($\text{g C m}^{-2} \text{yr}^{-1}$).

## 6. Mathematical models and equations

### The Logistic Growth Model

The logistic equation models population growth with density-dependent negative feedback, capturing the concept of carrying capacity.

$$ \frac{dN}{dt} = rN \left( 1 - \frac{N}{K} \right) $$

Where:
- $N$ is the population size (number of individuals or biomass).
- $t$ is time.
- $r$ is the intrinsic rate of increase (per capita growth rate in the absence of constraints, $\text{time}^{-1}$).
- $K$ is the carrying capacity.

When $N$ is small relative to $K$, the term $(1 - N/K)$ is close to 1, and growth is nearly exponential. As $N$ approaches $K$, the growth rate $dN/dt$ approaches zero.

### The Lotka-Volterra Predator-Prey Model

This system of coupled differential equations models the interaction between a prey population ($x$) and a predator population ($y$).

$$ \frac{dx}{dt} = \alpha x - \beta xy $$
$$ \frac{dy}{dt} = \delta xy - \gamma y $$

Where:
- $x$ is the number of prey.
- $y$ is the number of predators.
- $\alpha$ is the prey growth rate in the absence of predators.
- $\beta$ is the predation rate coefficient.
- $\delta$ is the predator growth rate coefficient (efficiency of converting prey into predator biomass).
- $\gamma$ is the predator mortality rate in the absence of prey.

Under its ideal assumptions, the classical model has neutrally stable closed orbits whose amplitude depends on initial conditions; this is not a generally attracting equilibrium and is structurally fragile to added realism.

### The Logistic Map and Chaos

To understand how simple deterministic systems can exhibit unpredictable, chaotic behaviour, ecologists use discrete-time models like the logistic map.

$$ x_{n+1} = r x_n (1 - x_n) $$

Where:
- $x_n$ is the population ratio at time step $n$ (a value between 0 and 1, representing the fraction of the carrying capacity).
- $r$ is a dimensionless control parameter of the discrete map; mapping it to biological rates requires an explicit derivation and time-step definition.

For low values of $r$ (e.g., $r < 3$), the population settles to a stable equilibrium. As $r$ increases, the system undergoes period-doubling bifurcations, oscillating between two, then four, then eight values. Beyond $r \approx 3.57$, the system enters a chaotic regime, where population sizes fluctuate wildly and are highly sensitive to initial conditions (the "butterfly effect").

## 7. Definitions of symbols and units

| Symbol | Definition | SI Unit / Dimension |
| :--- | :--- | :--- |
| $N$ | Population size | Individuals or $\text{kg}$ |
| $t$ | Time | $\text{s}$ (often expressed in days or years) |
| $r$ | Intrinsic growth rate | $\text{s}^{-1}$ |
| $K$ | Carrying capacity | Individuals or $\text{kg}$ |
| $x$ | Prey population size | Individuals |
| $y$ | Predator population size | Individuals |
| $\alpha, \gamma$ | Growth/mortality rates | $\text{s}^{-1}$ |
| $\beta, \delta$ | Interaction coefficients | $\text{Individuals}^{-1} \text{s}^{-1}$ |
| $C$ | Connectance | Dimensionless |

## 8. Assumptions and approximations

The logistic growth model assumes that the carrying capacity $K$ is constant, which is rarely true in nature as environments fluctuate. It also assumes an immediate response to density changes, ignoring time lags in reproduction or resource depletion. The basic Lotka-Volterra model assumes that prey have unlimited food (no carrying capacity for prey) and that predators have an insatiable appetite (linear functional response), which leads to structurally unstable oscillations. Real ecosystems include nonlinear functional responses, delays, stochasticity, evolution, spatial structure, and resource limits; these additions may damp, amplify, destabilise, or qualitatively change oscillations depending on parameters.

## 9. Spatial and temporal scales

Ecosystem dynamics operate across vast scales. Spatially, they range from a microscopic drop of pond water containing a complete microbial food web, to a local forest stand, up to the entire global biosphere. Temporally, processes vary from the rapid division of bacteria (minutes to hours), to the seasonal cycles of phytoplankton blooms, to the slow succession of a forest over centuries. Regime shifts can occur rapidly (months to years) but are often preceded by a slow, decades-long erosion of resilience, making them difficult to predict.

## 10. Common misconceptions

- **The "Balance of Nature":** A widespread misconception is that ecosystems naturally tend toward a static, perfect equilibrium. In reality, ecosystems are highly dynamic, constantly fluctuating, and often far from equilibrium. Disturbances (like fires or storms) are not unnatural anomalies but essential drivers of renewal and diversity.
- **More Complexity Always Means More Stability:** Early ecological theory assumed that highly complex food webs were inherently more stable. However, mathematical models by Robert May showed that randomly assembled complex networks are actually less stable [2]. Real ecosystems achieve stability not just through complexity, but through specific, non-random network topologies (like modularity and weak interaction strengths).
- **Carrying Capacity is Fixed:** Carrying capacity is often viewed as a hard, unchanging limit. In truth, it fluctuates with climate, resource availability, and the presence of other species.

## 11. Connections to other modules

- **04-probability-statistics:** Essential for understanding the stochastic nature of population fluctuations and the statistical mechanics of complex networks.
- **13-cells-bioenergetics:** Provides the foundation for understanding energy flow and metabolic constraints at the base of the food web.
- **14-dna-evolution:** Explains how species adapt to their environments and to each other, driving the long-term structural changes in ecosystems.
- **16-earth-planetary:** Ecosystems are deeply coupled with the climate system through biogeochemical cycles (e.g., the carbon cycle) and feedback loops (e.g., albedo changes).

## 12. Sources

1. Holling, C. S. *Resilience and Stability of Ecological Systems*. https://www.annualreviews.org/doi/abs/10.1146/annurev.es.04.110173.000245
2. May, R. M. *Will a Large Complex System Be Stable?* https://www.nature.com/articles/238413a0
3. Scheffer, M., et al. *Catastrophic Shifts in Ecosystems*. https://www.nature.com/articles/35098000
4. Dunne, J. A., et al. *Food-web Structure and Network Theory*. https://www.pnas.org/doi/abs/10.1073/pnas.192407699
5. U.S. Environmental Protection Agency. *Guiding Principles for Constructed Treatment Wetlands*. https://www.epa.gov/wetlands/guiding-principles-constructed-treatment-wetlands-providing-water-quality-and-wildlife
6. European Space Agency. *MELiSSA Environmental Control and Life Support Research*. https://www.esa.int/Enabling_Support/Space_Engineering_Technology/Life_Support_and_Physical_Sciences/Research_and_development
