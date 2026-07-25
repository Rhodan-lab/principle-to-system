---
title: "Semiconductors, electronics, and computer hardware"
slug: 18-semiconductors-electronics-technology
module: "Module 18"
domain: technology
status: reviewed
prerequisites: [06-matter-quantum, 10-electricity-magnetism, 17-materials-manufacturing]
connections: [19-software-ai, 20-sensors-control-infrastructure]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

## 1. Scientific principles used

Electronics uses quantum and statistical descriptions of solids, electrostatics, carrier transport, electromagnetism, thermodynamics, materials science, and circuit theory. Doping is one method of controlling carrier populations; heterostructures, gates, contacts, geometry, strain, defects, illumination, temperature, and phase also matter. Diodes and transistors implement nonlinear current–voltage and charge–voltage relations; “one-way valve,” “variable resistor,” and “perfect switch” are limited circuit analogies.

## 2. The engineering problem

Hardware engineering must realise specified computation, memory, communication, sensing, or power-conversion functions within limits on correctness, delay, energy, temperature, area, manufacturability, yield, reliability, cost, supply, and lifecycle impact. Device scaling is only one strategy. Architecture, memory hierarchy, interconnect, packaging, accelerators, redundancy, software, and workload mapping determine whether device capability becomes useful system performance.

## 3. Main components

- **Substrates and active materials:** Silicon is widespread, but compound semiconductors, wide-band-gap materials, thin films, and heterogeneous integration serve different functions.
- **Devices:** MOSFETs, diodes, bipolar devices, memory elements, photonic devices, sensors, and power devices use different structures and operating regimes.
- **Interconnect and dielectrics:** Conductors, barriers, vias, insulators, and interfaces connect and isolate devices while adding resistance, capacitance, inductance, stress, and failure modes.
- **Circuits and architecture:** Standard cells, analog blocks, memories, clocking, power delivery, processors, accelerators, and interfaces organise device behaviour.
- **Package and board:** Mechanical support, cooling, power, signal escape, protection, test access, and external connections extend beyond the die.
- **Manufacturing and test:** Crystal growth, deposition, patterning, doping, etching, cleaning, planarisation, metrology, inspection, packaging, and electrical test create and screen the product.

## 4. How the components interact

In a CMOS inverter, complementary devices share an input and drive an output node. Input-voltage ranges, transistor sizing, load capacitance, supply, temperature, leakage, and process variation determine transfer characteristic, delay, energy, and noise margin. “On” and “off” describe useful operating regions, not perfect conduction and insulation. Gates combine into sequential and combinational circuits, but processors also require clocks, memories, interconnect, power delivery, I/O, verification, firmware, and software.

## 5. Matter, energy, force, or information flow

- **Information:** Logical states are encoded in voltage, charge, current, resistance, phase, or other physical variables within specified noise margins and timing windows.
- **Charge and fields:** Carriers move and nodes charge or discharge through device and interconnect fields; information is not itself a substance flowing through the chip.
- **Energy:** Dynamic power approximately scales as $P_{dyn}=\alpha C V^2 f$ for a stated switched capacitance and activity factor, while leakage, short-circuit current, memory, interconnect, clocking, and I/O add other terms.
- **Heat:** Dissipated energy raises temperatures according to packaging, thermal resistance, cooling, workload, and spatial power density.

## 6. System architecture

One useful hierarchy is material and interface → device → circuit → functional block → microarchitecture → instruction-set interface → software-visible system. The mapping is many-to-many: one physical principle supports several devices, one logic function has several circuit implementations, and one instruction set can have many microarchitectures. Analog, mixed-signal, memory, photonic, power, and sensor systems do not follow one CPU-centred chain. Verification and metrology connect every level back to requirements.

## 7. Design constraints

- **Power, temperature, and reliability:** Voltage, frequency, workload, cooling, and ageing mechanisms constrain sustained operation.
- **Electrostatics and leakage:** Thin barriers, short channels, variability, and tunnelling limit off-state control.
- **Lithography and pattern transfer:** Resolution depends on optics, masks, resist, process windows, multiple patterning, etch, overlay, and metrology; EUV is one part of the system.
- **Interconnect and memory:** Resistance, capacitance, inductance, congestion, data movement, and memory latency can dominate device switching time.
- **Yield and variability:** Defects and process variation turn nominal design into statistical production; redundancy, design rules, testing, and process control are required.
- **Packaging:** Power delivery, signal integrity, thermal paths, mechanical stress, chiplets, and advanced integration shape system performance.

## 8. Performance and efficiency

No single metric describes processor performance. Report workload, precision, compiler, memory, batch size, latency, throughput, energy, thermal limit, and comparison baseline. Transistor count and Moore's observation do not guarantee proportional performance. Dennard-style constant-field scaling was an approximate design framework whose power benefits weakened as leakage, voltage scaling, variability, interconnect, and other constraints became dominant. Modern improvements use architecture, parallelism, accelerators, packaging, memory, software, and workload specialisation as well as device scaling.

## 9. Reliability and failure modes

- **Interconnect degradation:** Current density, temperature, stress, microstructure, interfaces, and geometry influence electromigration and related void or extrusion formation.
- **Dielectric and interface degradation:** Electric field, temperature, defects, charge trapping, and time contribute to breakdown and threshold drift.
- **Bias and hot-carrier ageing:** Operating bias can create or activate defects and change device parameters.
- **Thermomechanical damage:** Temperature gradients and cycling interact with package geometry, solder, underfill, dielectrics, and coefficients of thermal expansion.
- **Radiation and transient faults:** Ionising particles or electrical transients can disturb stored or computed state without permanent damage; sensitivity depends on technology, node, circuit, environment, and protection.
- **Systematic and random defects:** Design errors, process excursions, contamination, variation, and test escape require prevention, screening, redundancy, correction, and field monitoring.

## 10. Safety principles

Semiconductor fabrication uses specialised high-energy equipment, vacuum systems, ionising and non-ionising radiation sources, corrosive and toxic chemicals, pyrophoric gases, pressure systems, and cleanroom controls. These are professional environments governed by engineered containment, monitoring, interlocks, ventilation, compatible materials, emergency systems, trained personnel, and regulation. Learners should use simulations, packaged low-voltage educational hardware, or documented fabrication data rather than attempting chemical processing or opening mains-powered devices.

## 11. Environmental and lifecycle considerations

Semiconductor footprints depend on fab location, electricity mix, process gases, abatement, ultrapure water, yield, wafer size, device complexity, packaging, use-phase energy, lifetime, repair, and end-of-life pathways. “Rare earth” is not a sufficient summary of material dependence; critical inputs include many metals, gases, polymers, ceramics, and high-purity chemicals. E-waste risk depends on product composition and treatment. Longer support, efficient software, modularity, reuse, refurbishment, and responsible recycling can reduce impacts but involve trade-offs.

## 12. Connections to other technologies

*   **Photolithography:** The optical technology used to pattern the silicon wafers, relying on advanced lasers, lenses, and photoresists.
*   **Telecommunications:** High-speed internet and wireless networks rely on specialized semiconductor devices (like gallium arsenide or indium phosphide amplifiers) for transmitting and receiving high-frequency signals.
*   **Power Electronics:** Specialized, robust transistors (like IGBTs) are used to manage and convert high voltages and currents in electric vehicles, solar inverters, and power grids.

## Phase 9 review boundaries and validity limits

- Band, carrier, junction, and compact-device equations assume specified equilibrium, statistics, geometry, temperature, and bias regimes.
- Threshold voltage is a model parameter, not a hard microscopic on/off boundary; leakage, short-channel effects, variability, and parasitics matter.
- Technology-node names are industrial labels rather than literal dimensions of every device feature.
- Device performance, yield, reliability, and scaling claims require metrology, architecture, packaging, workload, and thermal context.

## 13. Sources

1. Massachusetts Institute of Technology OpenCourseWare. *Integrated Microelectronic Devices*. https://ocw.mit.edu/courses/6-720j-integrated-microelectronic-devices-spring-2007/
2. National Institute of Standards and Technology. *Semiconductors*. https://www.nist.gov/semiconductors
3. Intel. *Moore's Law*. https://www.intel.com/content/www/us/en/history/virtual-vault/articles/moores-law.html
4. National Institute of Standards and Technology. *CHIPS for America Metrology Program*. https://www.nist.gov/chips/research-development-programs/metrology-program
5. Orji, N. G., et al. *Metrology for the Next Generation of Semiconductor Devices*. https://www.nist.gov/publications/metrology-next-generation-semiconductor-devices
6. Postek, M. T., and Bennett, M. H. *Critical Dimension and Overlay Metrology*. https://www.nist.gov/publications/critical-dimension-and-overlay-metrology
