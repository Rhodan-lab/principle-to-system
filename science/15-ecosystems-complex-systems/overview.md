---
title: "Ecosystems, Feedback, Networks, and Complex Systems"
slug: "15-ecosystems-complex-systems"
module: "Module 15: Ecosystems, feedback, networks, and complex systems"
domain: "science"
status: draft
prerequisites: ["04-probability-statistics", "13-cells-bioenergetics", "14-dna-evolution"]
connections: ["16-climate-earth-systems", "17-social-dynamics"]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Ecosystems, Feedback, Networks, and Complex Systems

## 1. The central questions

How do vast numbers of interacting biological organisms and their physical environments self-organise into stable, enduring structures? Why do some ecosystems absorb massive disturbances and recover, while others collapse abruptly into entirely different states? How do local interactions between predators, prey, and nutrients give rise to emergent properties that cannot be predicted by studying individual species in isolation? 

## 2. Observable phenomena

Ecosystems exhibit phenomena that span multiple scales of space and time. A classic observation is the cyclical fluctuation of predator and prey populations, such as the lynx and snowshoe hare in the boreal forest, where the abundance of one species drives the rise and fall of the other. Another phenomenon is the sudden "greening" of a lake, where clear water abruptly turns into a turbid, algae-dominated state due to nutrient runoff, demonstrating a regime shift. In forests, the spontaneous emergence of spatial patterns, such as the regular spacing of trees in arid environments (e.g., "tiger bush"), reveals self-organisation. Furthermore, the resilience of a coral reef after a hurricane, slowly rebuilding its intricate food web, contrasts sharply with its rapid bleaching and structural collapse under sustained thermal stress.

## 3. Essential concepts

**Complex Adaptive Systems (CAS):** Ecosystems are complex adaptive systems composed of many interacting agents (organisms) that adapt to their environment and to each other. These systems are characterised by non-linear dynamics, where small changes can have disproportionately large effects.

**Trophic Levels and Food Webs:** Organisms are categorised by their trophic level—their position in the flow of energy and matter. Primary producers (plants, algae) form the base, followed by primary consumers (herbivores), secondary consumers (carnivores), and decomposers. A food web is the network topology of these feeding relationships.

**Feedback Loops:** Feedback mechanisms regulate ecosystem dynamics. Positive feedback amplifies changes, driving a system away from its current state (e.g., melting ice reducing albedo, causing more warming). Negative feedback dampens changes, promoting stability (e.g., increased prey density leading to higher predator populations, which then reduce the prey density).

**Emergence and Self-Organisation:** Emergence refers to macroscopic properties arising from microscopic interactions, such that the whole is greater than the sum of its parts. Self-organisation is the process by which structure and order emerge spontaneously without external direction, driven by local rules and feedback.

**Resilience and Regime Shifts:** Ecological resilience is the capacity of a system to absorb disturbance and reorganise while undergoing change so as to still retain essentially the same function, structure, identity, and feedbacks [1]. When a threshold is crossed, a regime shift occurs, moving the ecosystem into an alternative stable state.

## 4. Mechanisms and causal chains

The flow of energy and the cycling of nutrients are the fundamental mechanisms driving ecosystems. Solar energy is captured by autotrophs through photosynthesis, converting carbon dioxide and water into organic compounds. This energy flows unidirectionally through trophic levels, with significant losses at each transfer (typically around 90% lost as heat, following the laws of thermodynamics). In contrast, nutrients such as carbon, nitrogen, and phosphorus cycle continuously between the biotic and abiotic components of the system.

Population dynamics are governed by the balance between birth rates, death rates, immigration, and emigration. When resources are abundant, populations can grow exponentially. However, as population density increases, negative feedback mechanisms—such as resource depletion, increased disease transmission, and higher predation rates—intensify. This density dependence constrains growth, leading to a carrying capacity.

In complex networks, the topology of interactions determines stability. High connectance (the proportion of possible links that are realised) and modularity (the degree to which a network is compartmentalised) influence how disturbances propagate. A highly modular food web can contain the impact of a species extinction within a single module, preventing a cascading collapse across the entire ecosystem.

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

This model produces continuous oscillations in both populations, illustrating a simple dynamic equilibrium driven by coupled feedback loops.

### The Logistic Map and Chaos

To understand how simple deterministic systems can exhibit unpredictable, chaotic behaviour, ecologists use discrete-time models like the logistic map.

$$ x_{n+1} = r x_n (1 - x_n) $$

Where:
- $x_n$ is the population ratio at time step $n$ (a value between 0 and 1, representing the fraction of the carrying capacity).
- $r$ is a parameter representing the combined rate of reproduction and starvation.

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

The logistic growth model assumes that the carrying capacity $K$ is constant, which is rarely true in nature as environments fluctuate. It also assumes an immediate response to density changes, ignoring time lags in reproduction or resource depletion. The basic Lotka-Volterra model assumes that prey have unlimited food (no carrying capacity for prey) and that predators have an insatiable appetite (linear functional response), which leads to structurally unstable oscillations. Real ecosystems feature complex functional responses (e.g., predators becoming satiated) and spatial heterogeneity, which dampen these oscillations and promote stability.

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
- **16-climate-earth-systems:** Ecosystems are deeply coupled with the climate system through biogeochemical cycles (e.g., the carbon cycle) and feedback loops (e.g., albedo changes).

## 12. Sources

[1] Holling, C. S. (1973). Resilience and stability of ecological systems. *Annual Review of Ecology and Systematics*, 4(1), 1-23.
[2] May, R. M. (1972). Will a large complex system be stable? *Nature*, 238(5364), 413-414.
[3] Levin, S. A. (1998). Ecosystems and the biosphere as complex adaptive systems. *Ecosystems*, 1(5), 431-436.
[4] Scheffer, M., et al. (2001). Catastrophic shifts in ecosystems. *Nature*, 413(6856), 591-596.
[5] Dunne, J. A., Williams, R. J., & Martinez, N. D. (2002). Food-web structure and network theory: the role of connectance and size. *Proceedings of the National Academy of Sciences*, 99(20), 12917-12922.
