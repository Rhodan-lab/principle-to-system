---
title: "Semiconductors, electronics, and computer hardware"
slug: 18-semiconductors-electronics-explore
module: "Module 18"
domain: technology
status: reviewed
prerequisites: [06-matter-quantum, 10-electricity-magnetism, 17-materials-manufacturing]
connections: [19-software-ai, 20-sensors-control-infrastructure]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

## 1. Observation prompts

*   Examine a modern smartphone or laptop. Identify the areas that become warmest during heavy use. What does this heat distribution suggest about the location and power consumption of the main processor compared to other components like the battery or screen?
*   Look closely at a solar panel (if accessible) or a high-quality photograph of one. Notice the grid of thin metal lines on the surface. Why are these lines necessary, and why do they only cover a small fraction of the surface area rather than the whole panel?
*   Observe the behaviour of an LED light bulb when it is turned on and off. Does it fade out slowly like an incandescent bulb, or does it switch off instantly? What does this imply about the mechanism of light generation?

## 2. Prediction questions

- Compare intrinsic and doped silicon over a stated temperature range. Why can resistance trends depend on carrier generation, dopant activation, mobility, contacts, geometry, and self-heating?
- In a diode model, reverse bias usually widens the depletion region, but predict leakage, capacitance, and possible breakdown only after device type, voltage range, temperature, and circuit resistance are specified.
- Treat Moore's observation as historical data: given an assumed doubling interval, calculate a backward extrapolation and then explain why node economics, design choices, and product categories make it an unreliable prediction for a specific processor.

## 3. Worked reasoning examples

**Question:** Why does a high-performance processor often need substantial cooling while a calculator does not?

1. Identify workload, supply voltage, clocking, active capacitance, leakage, memory, display, and duty cycle rather than counting transistors alone.
2. Dynamic switching power is approximated by $P_{dyn}=\alpha C V^2 f$ at a chosen boundary; leakage and supporting circuits add power.
3. A calculator operates intermittently at low throughput and power, while a processor may sustain dense computation and data movement.
4. Packaging and cooling determine temperature rise. Thermal throttling or shutdown protects many systems before destructive temperatures occur.
5. Cooling need therefore follows total and local power, thermal resistance, allowable junction temperature, acoustics, reliability, and workload—not simply “billions times gigahertz.”

## 4. Thought experiments

*   **The Mechanical Computer:** Imagine trying to build a modern smartphone processor using mechanical relays (electromagnetically operated switches) instead of microscopic transistors. If a relay is $1 \text{ cm}^3$ in volume, how large would a 10-billion-relay processor be? How much power would it consume to physically move those metal contacts billions of times per second?
*   **The Perfect Insulator:** Suppose you could create a material with an infinitely large band gap. Would it be possible to dope this material to make it a semiconductor? Why or why not?
*   **The Shrinking Limit:** Imagine continuing to shrink transistors until the gate oxide is only one atom thick. What quantum mechanical phenomena would dominate the behaviour of the transistor, and why would the classical models of field-effect conductivity break down?

## 5. Household and browser-based explorations

- **Logic simulation:** Build gates and a half-adder in a browser simulator. Add propagation delay or unknown states where supported, and distinguish Boolean function from electrical implementation.
- **Virtual teardown:** Use manufacturer diagrams, repair documentation, or high-resolution board photographs rather than opening discarded electronics. Identify packages, connectors, power sections, traces, and uncertainty about hidden layers.
- **Thermal observation:** Use built-in operating-system temperature or power telemetry only when available, without bypassing safety limits. Compare idle and ordinary workloads and note that sensor placement and software estimates introduce uncertainty.
- **Semiconductor metrology:** Explore NIST material on critical dimension, overlay, and process measurement. Explain why fabrication success cannot be inferred from a nominal node label alone.

## 6. Model-building prompts

*   Using physical objects (like marbles, coins, or drawn symbols), create a visual model of a p-n junction. Show the p-type side with excess "holes" and the n-type side with excess "electrons". Demonstrate what happens at the boundary to form the depletion region.
*   Draw a diagram showing the energy bands (valence and conduction) for a conductor, a semiconductor, and an insulator. Add arrows to represent the thermal excitation of electrons across the band gap at room temperature for each material.
*   Construct a truth table for a NAND gate (NOT AND). Then, using only NAND gates in a logic simulator, try to build an inverter (NOT gate) and an AND gate. This demonstrates that NAND is a "universal gate" from which any logic circuit can be built.

## 7. Self-explanation questions

*   Explain in your own words why doping a semiconductor with a tiny amount of impurity can increase its conductivity by orders of magnitude.
*   Describe the sequence of events that occurs in a MOSFET when a voltage is applied to the gate, leading to current flowing between the source and drain.
*   Why is silicon the dominant material used in the semiconductor industry, rather than germanium (which was used in the first transistors) or diamond (which has a larger band gap)?

## 8. Transfer questions

*   The principles of p-n junctions are used in solar cells to convert light into electricity. How might these same principles be applied to create a sensor that detects specific chemical molecules in the air?
*   If we reach the physical limits of shrinking silicon transistors (the end of Moore's law), what alternative physical mechanisms or materials might be used to continue increasing computing power? (Consider quantum computing, optical computing, or carbon nanotubes).
*   How does the architecture of the human brain, with its billions of interconnected neurons, compare and contrast with the architecture of a modern CPU with its billions of interconnected transistors?

## 9. Suggested learning paths

*   **To understand the physics deeper:** Study quantum mechanics, specifically the Schrödinger equation and how it applies to periodic potentials in crystal lattices (Bloch's theorem).
*   **To understand the manufacturing:** Investigate the specific steps of photolithography, chemical vapour deposition, and plasma etching used in a semiconductor fabrication plant.
*   **To understand the computing:** Learn about digital logic design, Boolean algebra, and computer architecture (how logic gates are assembled into a functioning CPU).

## 10. Reasoning notes

When reasoning about semiconductors, it is crucial to maintain the distinction between the macroscopic behaviour of the device (voltage, current, logic state) and the microscopic quantum phenomena that enable it (band gaps, carrier mobility, depletion regions). A common pitfall is trying to apply classical mechanics (like billiard balls bouncing through a pipe) to electrons in a crystal lattice; the wave nature of electrons and the concept of energy bands are essential for accurate causal explanations. Furthermore, always consider the scale: a single transistor's behaviour is governed by physics, but the behaviour of a billion transistors is governed by architecture and statistical reliability.

## Phase 9 review boundaries and validity limits

- Band, carrier, junction, and compact-device equations assume specified equilibrium, statistics, geometry, temperature, and bias regimes.
- Threshold voltage is a model parameter, not a hard microscopic on/off boundary; leakage, short-channel effects, variability, and parasitics matter.
- Technology-node names are industrial labels rather than literal dimensions of every device feature.
- Device performance, yield, reliability, and scaling claims require metrology, architecture, packaging, workload, and thermal context.

## 11. Sources

1. Massachusetts Institute of Technology OpenCourseWare. *Integrated Microelectronic Devices*. https://ocw.mit.edu/courses/6-720j-integrated-microelectronic-devices-spring-2007/
2. National Institute of Standards and Technology. *Semiconductors*. https://www.nist.gov/semiconductors
3. Intel. *Moore's Law*. https://www.intel.com/content/www/us/en/history/virtual-vault/articles/moores-law.html
4. National Institute of Standards and Technology. *CHIPS for America Metrology Program*. https://www.nist.gov/chips/research-development-programs/metrology-program
5. Orji, N. G., et al. *Metrology for the Next Generation of Semiconductor Devices*. https://www.nist.gov/publications/metrology-next-generation-semiconductor-devices
6. Postek, M. T., and Bennett, M. H. *Critical Dimension and Overlay Metrology*. https://www.nist.gov/publications/critical-dimension-and-overlay-metrology
