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

The engineering of modern electronics relies on the quantum mechanical band theory of solids, specifically the ability to manipulate the band gap and charge carrier concentration of semiconductor materials through doping. The fundamental principle is the control of electrical conductivity via external electric fields (the field effect) or injected currents, allowing a semiconductor junction to act as a variable resistor, a one-way valve (diode), or an amplifier/switch (transistor).

## 2. The engineering problem

The core engineering problem in computing hardware is how to perform complex logical operations and store vast amounts of information quickly, reliably, and efficiently. Early computers used mechanical relays or vacuum tubes, which were large, fragile, power-hungry, and prone to failure. The challenge was to create a solid-state switch that was microscopic, consumed minimal power, generated little heat, and could be manufactured in massive quantities at low cost. Furthermore, these billions of switches needed to be interconnected reliably without manual wiring.

## 3. Main components

*   **Silicon Wafer:** The foundational substrate, a highly purified, single-crystal slice of silicon.
*   **Transistors (MOSFETs):** The active switching elements. Each consists of a source, drain, and gate.
*   **Logic Gates:** Combinations of transistors wired together to perform basic Boolean logic operations (AND, OR, NOT, NAND, NOR).
*   **Memory Cells:** Circuits designed to store a single bit of data (0 or 1). Static RAM (SRAM) uses multiple transistors to hold a state, while Dynamic RAM (DRAM) uses a transistor and a capacitor.
*   **Interconnects:** Microscopic layers of metal (usually copper or aluminium) wiring that connect the transistors and logic gates.
*   **Dielectric Layers:** Insulating materials (like silicon dioxide) used to separate conducting layers and form the gate insulator in MOSFETs.

## 4. How the components interact

The fundamental interaction is the construction of logic gates from transistors. In Complementary Metal-Oxide-Semiconductor (CMOS) technology, logic gates are built using pairs of p-type and n-type MOSFETs. 

For example, a NOT gate (inverter) consists of one p-MOSFET and one n-MOSFET connected in series between the power supply voltage and ground. The input signal is connected to the gates of both transistors. 
*   When the input is high (Logic 1), the n-MOSFET turns on (conducts) and the p-MOSFET turns off (insulates). The output is pulled to ground (Logic 0).
*   When the input is low (Logic 0), the p-MOSFET turns on and the n-MOSFET turns off. The output is pulled to the supply voltage (Logic 1).

These logic gates are then interconnected to form more complex circuits like adders, multiplexers, and ultimately, the Arithmetic Logic Unit (ALU) of a processor.

## 5. Matter, energy, force, or information flow

- **Information:** Logical states are encoded in voltage, charge, current, resistance, phase, or other physical variables within specified noise margins and timing windows.
- **Charge and fields:** Carriers move and nodes charge or discharge through device and interconnect fields; information is not itself a substance flowing through the chip.
- **Energy:** Dynamic power approximately scales as $P_{dyn}=\alpha C V^2 f$ for a stated switched capacitance and activity factor, while leakage, short-circuit current, memory, interconnect, clocking, and I/O add other terms.
- **Heat:** Dissipated energy raises temperatures according to packaging, thermal resistance, cooling, workload, and spatial power density.

## 6. System architecture

The architecture of a modern processor (CPU) is a hierarchy of abstraction:
1.  **Device Level:** Individual MOSFETs fabricated on the silicon substrate.
2.  **Circuit Level:** Transistors combined into logic gates and memory cells.
3.  **Functional Unit Level:** Logic gates combined into ALUs, registers, and control units.
4.  **Microarchitecture Level:** The arrangement of functional units to execute a specific instruction set architecture (ISA), including pipelines, cache memory hierarchy (L1, L2, L3), and branch prediction logic.
5.  **System Level:** The CPU integrated with main memory (RAM), storage controllers, and input/output interfaces on a motherboard.

**Explicit Principle-to-System Chain:**
Quantum Mechanics (Pauli Exclusion Principle) $\rightarrow$ Band Theory of Solids (Band Gap) $\rightarrow$ Semiconductor Doping (n-type/p-type) $\rightarrow$ p-n Junctions and Depletion Regions $\rightarrow$ Electric Field Control of Conductivity (Field Effect) $\rightarrow$ MOSFET Transistor $\rightarrow$ CMOS Inverter (NOT Gate) $\rightarrow$ NAND Gate $\rightarrow$ Half Adder $\rightarrow$ Arithmetic Logic Unit (ALU) $\rightarrow$ Central Processing Unit (CPU) $\rightarrow$ Computer System.

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

*   **Electromigration:** The momentum of flowing electrons can physically move metal atoms in the interconnects over time, creating voids (open circuits) or hillocks (short circuits).
*   **Time-Dependent Dielectric Breakdown (TDDB):** The gate oxide can degrade over time due to the constant electric field, eventually shorting the gate to the channel.
*   **Thermal Cycling:** Repeated heating and cooling causes mechanical stress due to mismatched coefficients of thermal expansion between different materials, leading to cracking or delamination.
*   **Single-Event Upsets (Soft Errors):** High-energy cosmic rays or alpha particles can strike a memory cell, generating enough electron-hole pairs to flip a bit from 0 to 1 or vice versa, causing a temporary data error.

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
