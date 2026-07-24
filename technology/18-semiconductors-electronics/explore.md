---
title: "Semiconductors, electronics, and computer hardware"
slug: "18-semiconductors-electronics"
module: "Module 18: Semiconductors, electronics, and computer hardware"
domain: "technology"
status: draft
prerequisites: ["06-matter-quantum", "10-electricity-magnetism", "17-materials-manufacturing"]
connections: ["19-computing-architecture", "20-software-algorithms"]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

## 1. Observation prompts

*   Examine a modern smartphone or laptop. Identify the areas that become warmest during heavy use. What does this heat distribution suggest about the location and power consumption of the main processor compared to other components like the battery or screen?
*   Look closely at a solar panel (if accessible) or a high-quality photograph of one. Notice the grid of thin metal lines on the surface. Why are these lines necessary, and why do they only cover a small fraction of the surface area rather than the whole panel?
*   Observe the behaviour of an LED light bulb when it is turned on and off. Does it fade out slowly like an incandescent bulb, or does it switch off instantly? What does this imply about the mechanism of light generation?

## 2. Prediction questions

*   If you were to heat a piece of pure silicon, would its electrical resistance increase or decrease? Contrast this with what happens when you heat a copper wire.
*   Imagine a p-n junction diode connected in a circuit. If you reverse the polarity of the battery connected to it, what will happen to the width of the depletion region, and how will this affect the current flowing through the circuit?
*   According to Moore's law, transistor density doubles roughly every two years. If a processor today has 10 billion transistors, approximately how many transistors would a processor of the same size have had 10 years ago?

## 3. Worked reasoning examples

**Question:** Why does a computer processor need a heatsink and a fan, while a simple calculator does not, even though both use transistors to perform logic?

**Reasoning:**
1.  **Identify the fundamental action:** Both devices perform calculations by switching transistors on and off.
2.  **Analyse energy dissipation:** Every time a transistor switches, a small amount of electrical energy is converted into heat due to the resistance of the semiconductor material and the charging/discharging of microscopic capacitances.
3.  **Compare scale and frequency:** A simple calculator contains a few thousand transistors operating at a very low clock frequency (perhaps a few kilohertz). The total heat generated per second is negligible and easily dissipates into the surrounding air.
4.  **Contrast with the processor:** A modern CPU contains billions of transistors switching billions of times per second (gigahertz).
5.  **Synthesise the conclusion:** The power dissipated is proportional to the number of transistors and the switching frequency. The massive scale and speed of a CPU result in a high power density, generating heat faster than it can passively dissipate. Without active cooling (heatsink to increase surface area, fan to move air), the temperature would quickly rise until the silicon melts or the transistors fail.

## 4. Thought experiments

*   **The Mechanical Computer:** Imagine trying to build a modern smartphone processor using mechanical relays (electromagnetically operated switches) instead of microscopic transistors. If a relay is $1 \text{ cm}^3$ in volume, how large would a 10-billion-relay processor be? How much power would it consume to physically move those metal contacts billions of times per second?
*   **The Perfect Insulator:** Suppose you could create a material with an infinitely large band gap. Would it be possible to dope this material to make it a semiconductor? Why or why not?
*   **The Shrinking Limit:** Imagine continuing to shrink transistors until the gate oxide is only one atom thick. What quantum mechanical phenomena would dominate the behaviour of the transistor, and why would the classical models of field-effect conductivity break down?

## 5. Household and browser-based explorations

*   **Logic Gate Simulation:** Use a free online logic circuit simulator (such as Logic.ly or CircuitVerse). Build a simple circuit using AND, OR, and NOT gates. Try to construct a Half Adder circuit (which adds two binary bits) and verify its truth table by toggling the inputs.
*   **Tear Down (Safe):** Find an old, broken electronic device (like a remote control, a cheap toy, or a digital clock) that runs on low-voltage batteries (AA or AAA). Open it up and identify the printed circuit board (PCB). Look for the black, plastic-encapsulated integrated circuits ("chips"). Note how the copper traces on the board connect the different components. *Do not open devices that plug into the mains power or contain large capacitors (like camera flashes).*
*   **Solar Cell Reversibility:** If you have a small solar garden light, cover the solar panel with your hand. The light turns on. The solar panel is a large p-n junction. When light hits it, it generates a voltage. When it's dark, the circuit uses the battery to drive current through an LED (another p-n junction) to create light.

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
