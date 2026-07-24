---
title: "Semiconductors, electronics, and computer hardware"
slug: "18-semiconductors-electronics"-technology
module: "Module 18: Semiconductors, electronics, and computer hardware"
domain: "technology"
status: draft
prerequisites: ["06-matter-quantum", "10-electricity-magnetism", "17-materials-manufacturing"]
connections: ["19-computing-architecture", "20-software-algorithms"]
last_reviewed: 2026-07-24
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

In an integrated circuit, the primary flow is **information**, represented by the flow of **energy** (electrical charge). 
1.  **Energy:** Electrical power is supplied to the chip. The movement of electrons and holes through the semiconductor lattice constitutes the current.
2.  **Information:** The presence or absence of a voltage at a specific node represents a binary bit (1 or 0). As transistors switch on and off, they route these voltages through the logic gates, transforming the input data into output data according to the programmed instructions.
3.  **Heat:** The resistance of the semiconductor material and the interconnects causes some electrical energy to be dissipated as heat, which must be removed to prevent the chip from failing.

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

*   **Power Dissipation:** As transistor density increases, the heat generated per unit area (power density) becomes a critical limiting factor. If heat cannot be removed fast enough, the chip will melt.
*   **Quantum Tunnelling:** As gate oxides become thinner (approaching a few atomic layers), electrons can quantum mechanically tunnel through the insulator, causing leakage current even when the transistor is supposed to be off.
*   **Lithographic Limits:** The ability to print smaller features is constrained by the wavelength of light used in photolithography. Extreme Ultraviolet (EUV) lithography is required for the smallest modern nodes.
*   **Interconnect Delay:** As transistors shrink and switch faster, the time it takes for a signal to travel through the microscopic metal wiring (RC delay) becomes a significant bottleneck.

## 8. Performance and efficiency

Performance is typically measured in instructions per second (IPS) or floating-point operations per second (FLOPS). Efficiency is measured in performance per watt. 

Moore's law, the observation that transistor density doubles approximately every two years, has historically driven exponential increases in performance and decreases in cost per computation [1]. Dennard scaling, a corollary to Moore's law, stated that as transistors shrank, their power density remained constant, allowing clock speeds to increase without increasing overall power consumption. However, Dennard scaling broke down in the mid-2000s due to leakage currents, forcing the industry to shift from single-core processors with ever-increasing clock speeds to multi-core architectures [1].

## 9. Reliability and failure modes

*   **Electromigration:** The momentum of flowing electrons can physically move metal atoms in the interconnects over time, creating voids (open circuits) or hillocks (short circuits).
*   **Time-Dependent Dielectric Breakdown (TDDB):** The gate oxide can degrade over time due to the constant electric field, eventually shorting the gate to the channel.
*   **Thermal Cycling:** Repeated heating and cooling causes mechanical stress due to mismatched coefficients of thermal expansion between different materials, leading to cracking or delamination.
*   **Single-Event Upsets (Soft Errors):** High-energy cosmic rays or alpha particles can strike a memory cell, generating enough electron-hole pairs to flip a bit from 0 to 1 or vice versa, causing a temporary data error.

## 10. Safety principles

While the voltages inside a microchip are very low (often around 1 Volt), the manufacturing process involves significant hazards. Semiconductor fabrication plants (fabs) use highly toxic, corrosive, and flammable gases (e.g., silane, phosphine, hydrofluoric acid) and strong acids for etching. Safety relies on extreme isolation, automated handling, continuous gas monitoring, and rigorous cleanroom protocols to protect both the workers and the easily contaminated silicon wafers.

## 11. Environmental and lifecycle considerations

The manufacturing of integrated circuits is highly resource-intensive. It requires vast amounts of ultra-pure water, significant electrical energy, and rare earth elements. The chemicals used in etching and cleaning must be carefully treated before disposal. 

At the end of their lifecycle, electronic devices contribute to e-waste. While the silicon itself is benign, the heavy metals, lead solder (in older devices), and toxic flame retardants in the packaging pose environmental hazards if not properly recycled. The short lifespan of consumer electronics exacerbates this issue.

## 12. Connections to other technologies

*   **Photolithography:** The optical technology used to pattern the silicon wafers, relying on advanced lasers, lenses, and photoresists.
*   **Telecommunications:** High-speed internet and wireless networks rely on specialized semiconductor devices (like gallium arsenide or indium phosphide amplifiers) for transmitting and receiving high-frequency signals.
*   **Power Electronics:** Specialized, robust transistors (like IGBTs) are used to manage and convert high voltages and currents in electric vehicles, solar inverters, and power grids.

## 13. Sources

[1] Wikipedia. "Moore's law." Accessed July 24, 2026. https://en.wikipedia.org/wiki/Moore%27s_law
[2] Wikipedia. "Integrated circuit." Accessed July 24, 2026. https://en.wikipedia.org/wiki/Integrated_circuit
