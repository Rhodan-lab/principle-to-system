---
title: "Atoms to Computers"
slug: pathway-atoms-to-computers
domain: pathway
status: complete
prerequisites: [06-matter-quantum, 10-electricity-magnetism, 17-materials-manufacturing, 18-semiconductors-electronics, 19-software-ai]
connections: [05-computation-algorithms, 11-waves-signals]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Atoms to Computers

This pathway traces the complete dependency chain from atomic physics to a functioning digital computer. At every stage, a scientific principle is exploited, an abstraction is introduced, an engineering problem is solved, and a trade-off appears.

---

## Stage 1: Atomic structure and electron energy levels

**Mechanism used:** Quantum mechanics — electrons in atoms occupy discrete energy levels governed by the Schrödinger equation. The Pauli exclusion principle limits occupancy of each state, producing the shell structure of the periodic table.

**Abstraction introduced:** The concept of *electron configuration* — a compact description of which energy levels are occupied — replaces the full quantum-mechanical wavefunction for practical purposes.

**Engineering problem solved:** Identifying which elements have the right electronic properties (four valence electrons, moderate band gap) to serve as controllable conductors. Silicon and germanium emerge as candidates.

**Trade-off:** Quantum mechanics is exact but computationally intractable for many-electron atoms. Approximations (Hartree–Fock, density functional theory) trade accuracy for tractability.

**Prerequisite knowledge:** [Module 06 — Matter and Quantum Foundations](../science/06-matter-quantum/overview.md)

---

## Stage 2: Band theory and semiconductor behaviour

**Mechanism used:** When atoms form a crystal lattice, their discrete energy levels broaden into continuous *bands*. The gap between the valence band (filled) and conduction band (empty) determines whether the material is a conductor, semiconductor, or insulator.

**Abstraction introduced:** The *band gap* $E_g$ — a single energy value that characterises the material's electrical behaviour. For silicon, $E_g \approx 1.1$ eV at room temperature.

**Engineering problem solved:** Controlling conductivity. By adding impurity atoms (doping) — phosphorus for n-type (extra electrons) or boron for p-type (extra holes) — engineers tune the carrier concentration over many orders of magnitude.

**Trade-off:** Narrower band gaps increase intrinsic carrier concentration (more leakage current at high temperature). Wider band gaps require higher voltages to switch. Silicon's moderate gap is a compromise between switching voltage and thermal stability.

**Prerequisite knowledge:** [Module 06](../science/06-matter-quantum/overview.md), [Module 17 — Materials Science](../technology/17-materials-manufacturing/overview.md)

---

## Stage 3: The p–n junction and diode

**Mechanism used:** At the interface between p-type and n-type silicon, electrons diffuse from n to p and holes from p to n, creating a depletion region with a built-in electric field. This field opposes further diffusion, establishing equilibrium.

**Abstraction introduced:** The *diode* — a two-terminal device that conducts current in one direction (forward bias) and blocks it in the other (reverse bias). Its behaviour is captured by the Shockley equation: $I = I_0(e^{V/nV_T} - 1)$.

**Engineering problem solved:** Rectification — converting AC to DC, protecting circuits from reverse polarity, and enabling voltage regulation.

**Trade-off:** Forward voltage drop ($\sim 0.6$ V for silicon) wastes energy. Lower-drop materials (Schottky diodes, GaN) improve efficiency but add cost or complexity.

**Prerequisite knowledge:** [Module 10 — Electricity and Magnetism](../science/10-electricity-magnetism/overview.md), [Module 18 — Semiconductors](../technology/18-semiconductors-electronics/overview.md)

---

## Stage 4: The transistor as a switch

**Mechanism used:** A MOSFET uses a gate voltage to create or deplete a conducting channel between source and drain. Above the threshold voltage $V_{th}$, an inversion layer forms and current flows; below it, the channel is off.

**Abstraction introduced:** The *binary switch* — the transistor is treated as either fully on (logic 1) or fully off (logic 0), ignoring the analogue transition region. This digital abstraction enables Boolean logic.

**Engineering problem solved:** Amplification and switching with no moving parts, at speeds determined by carrier transit time across the channel (picoseconds for nanometre gates).

**Trade-off:** Smaller transistors switch faster and use less energy per switch, but suffer increased leakage current (quantum tunnelling through thin gate oxides) and greater variability in threshold voltage. This is the fundamental tension driving Moore's law and its eventual slowdown.

**Prerequisite knowledge:** [Module 18 — Semiconductors and Electronics](../technology/18-semiconductors-electronics/overview.md)

---

## Stage 5: Logic gates from transistors

**Mechanism used:** Complementary pairs of NMOS and PMOS transistors (CMOS) implement Boolean functions. A NAND gate, for example, uses two series NMOS and two parallel PMOS transistors: the output is low only when both inputs are high.

**Abstraction introduced:** The *logic gate* — a functional unit with defined truth-table behaviour, independent of the underlying transistor physics. Any Boolean function can be built from NAND gates alone (functional completeness).

**Engineering problem solved:** Composability — complex logic from simple, verified building blocks. Standard cell libraries provide pre-characterised gates with known timing, power, and area.

**Trade-off:** CMOS draws significant power only during switching (dynamic power $P = \alpha C V^2 f$), but static leakage grows as transistors shrink. Power density, not transistor count, is now the primary design constraint.

**Prerequisite knowledge:** [Module 18](../technology/18-semiconductors-electronics/overview.md), [Module 05 — Computation](../foundations/05-computation-algorithms/overview.md)

---

## Stage 6: Processor architecture

**Mechanism used:** Logic gates are composed into functional units — arithmetic logic units (ALUs), register files, control units, caches — connected by buses. A clock signal synchronises operations, and an instruction set architecture (ISA) defines the interface between hardware and software.

**Abstraction introduced:** The *stored-program computer* (von Neumann architecture) — instructions and data share the same memory, and the processor fetches, decodes, and executes instructions sequentially (with pipelining and parallelism for performance).

**Engineering problem solved:** General-purpose computation — a single hardware design that can execute any algorithm expressed in its instruction set, from word processing to climate simulation.

**Trade-off:** The von Neumann bottleneck — memory bandwidth limits throughput because instructions and data compete for the same bus. Caches, out-of-order execution, and multi-core designs mitigate but do not eliminate this fundamental constraint.

**Prerequisite knowledge:** [Module 18](../technology/18-semiconductors-electronics/overview.md), [Module 05](../foundations/05-computation-algorithms/overview.md)

---

## Stage 7: Software and the operating system

**Mechanism used:** The processor executes machine instructions, but humans write in high-level languages. Compilers translate human-readable code into machine code. The operating system manages hardware resources (memory, I/O, scheduling) and provides abstractions (files, processes, virtual memory) that isolate applications from hardware details.

**Abstraction introduced:** The *virtual machine* — each running program behaves as if it has exclusive access to a complete computer, even though physical resources are shared. This enables multitasking, security isolation, and hardware independence.

**Engineering problem solved:** Programmability and portability — software written once runs on any hardware that supports the same OS interface, and multiple programs coexist without interference.

**Trade-off:** Abstraction layers add overhead (context switches, memory management, system calls). Real-time and embedded systems sometimes bypass the OS for deterministic timing, sacrificing generality for predictability.

**Prerequisite knowledge:** [Module 19 — Software and AI Foundations](../technology/19-software-ai/overview.md)

---

## Summary chain

```text
quantum mechanics (electron energy levels)
→ band theory (semiconductor behaviour)
→ doping (controlled conductivity)
→ p–n junction (diode)
→ MOSFET (transistor switch)
→ CMOS logic gates (Boolean functions)
→ processor architecture (general-purpose computation)
→ operating system and software (programmable abstraction)
→ computer
```

Each arrow represents a new abstraction built on the mechanism below it, solving an engineering problem while introducing a new trade-off that constrains the next level.
