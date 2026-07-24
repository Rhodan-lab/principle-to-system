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

## 1. The central questions

How can we control the flow of electricity with such precision that it can represent information, perform logic, and store memory? Why do certain materials act as insulators under some conditions and conductors under others? How do we manipulate the atomic structure of these materials to create microscopic switches, and how can billions of these switches be integrated into a single chip to form the foundation of modern computing?

## 2. Observable phenomena

The effects of semiconductor physics are ubiquitous in modern life, though the mechanisms operate at a microscopic scale. A smartphone processing billions of operations per second without melting is a direct consequence of semiconductor efficiency. The illumination of a room by light-emitting diodes (LEDs) demonstrates the conversion of electrical energy into light across a semiconductor junction. The ability of a solar panel to generate electricity when exposed to sunlight is the reverse process. The exponential increase in computing power over the last half-century, commonly known as Moore's law, is an observable trend driven by the continuous miniaturisation of semiconductor devices.

## 3. Essential concepts

**Band Theory of Solids:** In isolated atoms, electrons occupy discrete energy levels. When atoms are brought together to form a solid crystal lattice, these discrete levels merge into continuous bands of allowed energy states. The highest energy band that is completely filled with electrons at absolute zero is the **valence band**. The next higher band, which is empty at absolute zero, is the **conduction band**. The energy difference between the top of the valence band and the bottom of the conduction band is the **band gap** ($E_g$).

**Conductors, Insulators, and Semiconductors:** The electrical properties of a material depend on its band structure. In conductors (metals), the valence and conduction bands overlap, allowing electrons to move freely. In insulators, the band gap is large (typically $> 4 \text{ eV}$), preventing thermal excitation of electrons into the conduction band at room temperature. Semiconductors have a small band gap (typically $1 \text{ to } 3 \text{ eV}$), allowing a small but significant number of electrons to be thermally excited into the conduction band at room temperature [1].

**Electrons and Holes:** When an electron is excited from the valence band to the conduction band, it leaves behind a vacancy in the valence band. This vacancy, called a **hole**, acts as a mobile positive charge carrier. Both electrons in the conduction band and holes in the valence band contribute to electrical conductivity.

**Doping:** The intrinsic conductivity of a pure semiconductor is very low. Doping is the intentional introduction of specific impurity atoms into the semiconductor lattice to drastically alter its electrical properties. 
*   **n-type doping:** Introducing atoms with more valence electrons than the host (e.g., phosphorus in silicon) creates extra electrons in the conduction band. The majority charge carriers are electrons.
*   **p-type doping:** Introducing atoms with fewer valence electrons (e.g., boron in silicon) creates extra holes in the valence band. The majority charge carriers are holes.

**The p-n Junction:** The fundamental building block of most semiconductor devices is the p-n junction, formed by joining p-type and n-type semiconductors. At the interface, electrons from the n-side diffuse into the p-side and recombine with holes, while holes from the p-side diffuse into the n-side. This creates a **depletion region** devoid of mobile charge carriers, leaving behind fixed, charged impurity ions. These fixed charges create a built-in electric field that opposes further diffusion, establishing an equilibrium.

## 4. Mechanisms and causal chains

**Diode Action (Rectification):** A p-n junction acts as a diode, allowing current to flow in only one direction. 
*   **Forward Bias:** Applying a positive voltage to the p-side relative to the n-side reduces the built-in electric field and narrows the depletion region. Electrons and holes are pushed toward the junction, where they recombine, allowing a continuous current to flow.
*   **Reverse Bias:** Applying a negative voltage to the p-side increases the built-in electric field and widens the depletion region. The barrier to charge flow increases, and only a negligible leakage current flows.

**Transistor Action (Amplification and Switching):** A transistor uses a small input signal to control a much larger output current.
*   **Bipolar Junction Transistor (BJT):** Consists of three alternating doped regions (e.g., n-p-n). A small current injected into the thin central region (the base) lowers the potential barrier, allowing a large current to flow from the emitter to the collector.
*   **Metal-Oxide-Semiconductor Field-Effect Transistor (MOSFET):** The dominant transistor type in modern integrated circuits. It consists of a source, a drain, and a gate separated from the semiconductor channel by a thin insulating oxide layer. Applying a voltage to the gate creates an electric field that attracts charge carriers to the channel region, changing it from an insulator to a conductor. This allows current to flow between the source and drain. The MOSFET acts as a voltage-controlled switch [2].

## 5. Important quantities

| Quantity | Symbol | SI Unit | Description |
| :--- | :---: | :--- | :--- |
| Band gap energy | $E_g$ | Joule ($\text{J}$) or Electron-volt ($\text{eV}$) | Energy required to excite an electron from the valence band to the conduction band. |
| Carrier concentration | $n, p$ | $\text{m}^{-3}$ | Number of electrons ($n$) or holes ($p$) per unit volume. |
| Doping concentration | $N_D, N_A$ | $\text{m}^{-3}$ | Concentration of donor ($N_D$) or acceptor ($N_A$) impurity atoms. |
| Mobility | $\mu_e, \mu_h$ | $\text{m}^2/(\text{V}\cdot\text{s})$ | How quickly an electron or hole can move through a semiconductor under an applied electric field. |
| Built-in potential | $V_{bi}$ | Volt ($\text{V}$) | The potential difference across a p-n junction in thermal equilibrium. |
| Threshold voltage | $V_{th}$ | Volt ($\text{V}$) | The minimum gate voltage required to create a conducting channel in a MOSFET. |

## 6. Mathematical models and equations

**Intrinsic Carrier Concentration:**
The number of electrons in the conduction band ($n_i$) and holes in the valence band ($p_i$) in a pure semiconductor depends exponentially on temperature and the band gap:
$$n_i = p_i = \sqrt{N_c N_v} \exp\left(-\frac{E_g}{2k_B T}\right)$$
Where $N_c$ and $N_v$ are the effective density of states in the conduction and valence bands, $k_B$ is the Boltzmann constant, and $T$ is the absolute temperature.

**Mass Action Law:**
In thermal equilibrium, the product of electron and hole concentrations is constant for a given semiconductor at a given temperature, regardless of doping:
$$n \cdot p = n_i^2$$

**Conductivity:**
The electrical conductivity ($\sigma$) of a semiconductor depends on the concentration and mobility of both electrons and holes:
$$\sigma = e(n\mu_e + p\mu_h)$$
Where $e$ is the elementary charge.

**Built-in Potential of a p-n Junction:**
The built-in voltage ($V_{bi}$) depends on the doping concentrations on both sides:
$$V_{bi} = \frac{k_B T}{e} \ln\left(\frac{N_A N_D}{n_i^2}\right)$$

**MOSFET Drain Current (Linear Region):**
When the gate voltage ($V_{GS}$) exceeds the threshold voltage ($V_{th}$) and the drain-source voltage ($V_{DS}$) is small, the MOSFET acts like a resistor:
$$I_D = \mu_n C_{ox} \frac{W}{L} \left( (V_{GS} - V_{th})V_{DS} - \frac{V_{DS}^2}{2} \right)$$
Where $\mu_n$ is the electron mobility, $C_{ox}$ is the gate oxide capacitance per unit area, $W$ is the channel width, and $L$ is the channel length.

## 7. Definitions of symbols and units

*   $E_g$: Band gap energy, measured in electron-volts ($\text{eV}$). $1 \text{ eV} \approx 1.602 \times 10^{-19} \text{ J}$.
*   $k_B$: Boltzmann constant, $1.38 \times 10^{-23} \text{ J/K}$.
*   $T$: Absolute temperature, measured in Kelvin ($\text{K}$).
*   $e$: Elementary charge, $1.602 \times 10^{-19} \text{ C}$.
*   $\mu_e, \mu_h$: Electron and hole mobility, measured in $\text{m}^2/(\text{V}\cdot\text{s})$.
*   $C_{ox}$: Oxide capacitance per unit area, measured in Farads per square metre ($\text{F/m}^2$).

## 8. Assumptions and approximations

*   **Thermal Equilibrium:** Many equations (like the mass action law) assume the semiconductor is in thermal equilibrium, meaning no external forces (like light or applied voltage) are generating excess carriers.
*   **Complete Ionisation:** It is typically assumed that at room temperature, all dopant atoms are ionised, meaning every donor atom has given up an electron and every acceptor atom has accepted an electron.
*   **Abrupt Junction Approximation:** When modelling p-n junctions, the transition from p-type to n-type doping is often assumed to be instantaneous, simplifying the calculation of the electric field and depletion width.
*   **Ideal MOSFET:** The basic MOSFET equations assume an ideal structure with no leakage currents, perfect insulators, and constant mobility, which breaks down at nanoscale dimensions.

## 9. Spatial and temporal scales

*   **Spatial:** Semiconductor physics operates at the atomic scale (nanometres, $10^{-9} \text{ m}$). The band gap arises from the spacing of atoms in the crystal lattice. Modern MOSFET transistors have feature sizes (like gate length) on the order of a few nanometres. An integrated circuit chip, however, is on the macroscopic scale (millimetres to centimetres), containing billions of these nanoscale devices.
*   **Temporal:** The movement of charge carriers across a transistor channel happens on the scale of picoseconds ($10^{-12} \text{ s}$) to nanoseconds ($10^{-9} \text{ s}$). This allows modern processors to operate at clock frequencies of several gigahertz ($\text{GHz}$), performing billions of switching operations per second.

## 10. Common misconceptions

*   **Misconception:** Semiconductors are just materials that are halfway between conductors and insulators.
    *   **Correction:** While their conductivity is intermediate, the defining feature of a semiconductor is its band gap, which allows its conductivity to be dynamically controlled by temperature, doping, light, or electric fields.
*   **Misconception:** Holes are actual physical particles.
    *   **Correction:** A hole is the absence of an electron in the valence band. It is treated as a positively charged particle for mathematical convenience because the collective movement of the remaining electrons in the valence band behaves exactly like the movement of a positive charge.
*   **Misconception:** Current in a wire is the speed of light.
    *   **Correction:** The electrical signal propagates near the speed of light, but the actual drift velocity of electrons in a semiconductor or metal is very slow, often fractions of a millimetre per second.

## 11. Connections to other modules

*   **06-matter-quantum:** Quantum mechanics is the foundation of band theory. The Pauli exclusion principle and the wave nature of electrons dictate the formation of energy bands and band gaps.
*   **10-electricity-magnetism:** The behaviour of charge carriers under electric fields, capacitance in MOSFETs, and the built-in potential of p-n junctions rely on classical electromagnetism.
*   **17-materials-manufacturing:** The extreme purity required for semiconductor crystals and the complex photolithography processes used to fabricate integrated circuits are advanced materials science and manufacturing techniques.
*   **19-computing-architecture:** The logic gates and memory cells built from transistors form the physical hardware upon which computer architectures are designed.

## 12. Sources

[1] Wikipedia. "Semiconductor device." Accessed July 24, 2026. https://en.wikipedia.org/wiki/Semiconductor_device
[2] Wikipedia. "Transistor." Accessed July 24, 2026. https://en.wikipedia.org/wiki/Transistor
