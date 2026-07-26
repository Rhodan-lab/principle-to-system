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

# Semiconductors, electronics, and computer hardware

## 1. Observation prompts

- Use built-in telemetry during ordinary use only; do not intentionally overheat or stress a device. Compare reported temperature, power, utilisation, brightness, charging, and workload while recognising that sensor placement and software estimates limit interpretation.
- Study a manufacturer diagram or safe photograph of a photovoltaic module. Identify cells, busbars, fingers, encapsulation, bypass elements, and shading trade-offs without touching installed electrical equipment.
- Compare recorded LED and incandescent turn-off transients. Driver capacitance, phosphor persistence, thermal inertia, and camera exposure can affect the observation, so turn-off appearance alone does not identify one emission mechanism.

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

- **Relay scaling model:** Given a specified relay volume, switching time, coil energy, contact life, and component count, calculate size, delay, power, and reliability. Which assumptions fail when extrapolated to a processor?
- **Large-gap limit:** Increase band-gap energy in a model while keeping defects, contacts, fields, and dopants specified. Why does “infinite band gap” leave the model's physical domain rather than define a manufacturable perfect insulator?
- **Ultrathin gate stack:** As dimensions approach atomic scales, discuss tunnelling, interface states, variability, quantum confinement, electrostatics, reliability, and the limits of a classical long-channel model.

## 5. Household and browser-based explorations

- **Logic simulation:** Build gates and a half-adder in a browser simulator. Add propagation delay or unknown states where supported, and distinguish Boolean function from electrical implementation.
- **Virtual teardown:** Use manufacturer diagrams, repair documentation, or high-resolution board photographs rather than opening discarded electronics. Identify packages, connectors, power sections, traces, and uncertainty about hidden layers.
- **Thermal observation:** Use built-in operating-system temperature or power telemetry only when available, without bypassing safety limits. Compare idle and ordinary workloads and note that sensor placement and software estimates introduce uncertainty.
- **Semiconductor metrology:** Explore NIST material on critical dimension, overlay, and process measurement. Explain why fabrication success cannot be inferred from a nominal node label alone.

## 6. Model-building prompts

- Build a charge-accounting model of an abrupt p–n junction. Represent ionised dopants, reduced mobile-carrier density, electric field, and potential separately; do not portray holes as empty beads that simply disappear at the boundary.
- Compare schematic band diagrams for a metal, intrinsic semiconductor, doped semiconductor, and insulator under stated temperature and equilibrium conditions. Mark Fermi level and explain why a class label is not determined by band gap alone.
- Construct NAND-based Boolean functions in a simulator, then add propagation delay, fan-out, unknown state, or noise-margin constraints to separate logical universality from a physical implementation.

## 7. Self-explanation questions

*   Explain in your own words why doping a semiconductor with a tiny amount of impurity can increase its conductivity by orders of magnitude.
*   Describe the sequence of events that occurs in a MOSFET when a voltage is applied to the gate, leading to current flowing between the source and drain.
*   Why is silicon the dominant material used in the semiconductor industry, rather than germanium (which was used in the first transistors) or diamond (which has a larger band gap)?

## 8. Transfer questions

- Compare a photovoltaic junction with a chemical or biological field-effect sensor. Which parts of the transduction chain involve carrier generation, surface potential, selective chemistry, amplification, calibration, and interference?
- Instead of one “end of Moore's law,” identify separate limits and opportunities in devices, interconnect, memory, packaging, architecture, algorithms, photonics, quantum systems, and economics.
- Compare an artificial neural-network computation graph with biological neural tissue only at explicitly chosen levels such as connectivity, dynamics, learning signal, energy, and embodiment. Why do matching component counts not establish functional or cognitive equivalence?

## 9. Suggested learning paths

*   **To understand the physics deeper:** Study quantum mechanics, specifically the Schrödinger equation and how it applies to periodic potentials in crystal lattices (Bloch's theorem).
*   **To understand the manufacturing:** Investigate the specific steps of photolithography, chemical vapour deposition, and plasma etching used in a semiconductor fabrication plant.
*   **To understand the computing:** Learn about digital logic design, Boolean algebra, and computer architecture (how logic gates are assembled into a functioning CPU).

## 10. Reasoning notes

Separate electronic structure from semiclassical transport, device behaviour from compact models, Boolean function from circuit voltage, and transistor count from system performance. Classical circuit and transport models remain useful within validated regimes; quantum theory does not replace every engineering abstraction. State temperature, bias, geometry, statistics, contacts, measurement, and uncertainty before extending a device explanation to an integrated system.

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
