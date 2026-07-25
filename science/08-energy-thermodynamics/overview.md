---
title: "Energy, Heat, Entropy, and Thermodynamics"
slug: 08-energy-thermodynamics
module: "Module 08"
domain: science
status: draft
prerequisites: [03-mathematical-models, 06-matter-quantum]
connections: [12-fluids-materials, 13-cells-bioenergetics, 16-earth-planetary]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Energy, Heat, Entropy, and Thermodynamics

## 1. The central questions

Why does a hot cup of coffee always cool down, but a cold cup never spontaneously heats up? Why can we never build a machine that runs forever without consuming fuel? How does the microscopic motion of countless invisible particles translate into the macroscopic forces that drive engines, weather systems, and life itself? Thermodynamics is the study of energy, its transformations, and the fundamental limits on how it can be used. It answers these questions by establishing the universal rules governing heat, work, and the inevitable progression of systems toward disorder.

## 2. Observable phenomena

The principles of thermodynamics manifest in everyday phenomena. When ice melts in a glass of water, heat flows from the warmer liquid to the colder solid until thermal equilibrium is reached. A bicycle pump becomes warm as air is compressed inside it, demonstrating the conversion of mechanical work into thermal energy. A steam locomotive moves forward because the expansion of hot gas pushes against a piston. Conversely, a refrigerator keeps food cold by using electrical energy to pump heat from a cold interior to a warmer exterior, a process that never occurs spontaneously. Even the weather—driven by the uneven heating of the Earth's surface by the Sun—is a massive thermodynamic engine.

## 3. Essential concepts

**Energy** is the capacity of a physical system to perform work. It exists in many forms, including kinetic (motion), potential (position or configuration), thermal (microscopic kinetic energy), and chemical (energy stored in molecular bonds).

**Heat** is the transfer of thermal energy between systems due to a temperature difference. It is not a substance contained within an object, but a process of energy in transit.

**Work** is the transfer of energy by any mechanism other than a temperature difference, typically involving a macroscopic force acting over a distance (such as a piston compressing a gas).

**Temperature** is a measure of the average translational kinetic energy of the microscopic particles in a system. It determines the direction of spontaneous heat flow.

**Entropy** is a measure of the number of specific microscopic configurations (microstates) that correspond to a macroscopic state (macrostate). It is often conceptualised as a measure of disorder or the unavailability of a system's thermal energy for conversion into mechanical work.

**Free Energy** (such as Gibbs or Helmholtz free energy) is the portion of a system's internal energy that is available to perform thermodynamic work at a constant temperature. It determines whether a process will occur spontaneously.

**Phase Transitions** are transformations of a thermodynamic system from one phase or state of matter to another (e.g., solid to liquid, liquid to gas) characterised by abrupt changes in physical properties, driven by the competition between internal energy and entropy.

## 4. Mechanisms and causal chains

### Heat Transfer Mechanisms
Thermal energy moves through three primary mechanisms:
1.  **Conduction:** The transfer of heat through a stationary medium by the microscopic collisions of particles and movement of electrons. When one end of a metal rod is heated, the energetic particles vibrate more vigorously, colliding with adjacent particles and passing the kinetic energy along the rod.
2.  **Convection:** The transfer of heat by the macroscopic movement of a fluid (liquid or gas). When a fluid is heated from below, it expands, becomes less dense, and rises, while cooler, denser fluid sinks to replace it, creating a circulating convection current.
3.  **Radiation:** The transfer of energy via electromagnetic waves. Unlike conduction and convection, radiation does not require a medium and can travel through a vacuum. All objects emit thermal radiation proportional to the fourth power of their absolute temperature.

### The Laws of Thermodynamics
The causal chains of energy transformation are governed by four fundamental laws:
*   **Zeroth Law:** If system A is in thermal equilibrium with system B, and system B is in thermal equilibrium with system C, then A is in thermal equilibrium with C. This establishes temperature as a measurable, fundamental property.
*   **First Law (Conservation of Energy):** Energy cannot be created or destroyed, only transformed from one form to another. The change in a system's internal energy is equal to the heat added to the system minus the work done by the system.
*   **Second Law:** The total entropy of an isolated system can never decrease over time. Heat flows spontaneously from hot to cold, and no process is possible whose sole result is the complete conversion of heat into work. This law establishes the "arrow of time" and the fundamental limits on engine efficiency.
*   **Third Law:** As the temperature of a system approaches absolute zero ($0\text{ K}$), the entropy of the system approaches a constant minimum value.

## 5. Important quantities

| Quantity | Symbol | SI Unit | Definition |
| :--- | :---: | :--- | :--- |
| Internal Energy | $U$ | Joule ($\text{J}$) | Total microscopic kinetic and potential energy of a system. |
| Heat | $Q$ | Joule ($\text{J}$) | Energy transferred due to a temperature difference. |
| Work | $W$ | Joule ($\text{J}$) | Energy transferred by macroscopic forces. |
| Temperature | $T$ | Kelvin ($\text{K}$) | Measure of average microscopic kinetic energy. |
| Entropy | $S$ | Joule per Kelvin ($\text{J/K}$) | Measure of the number of accessible microstates. |
| Enthalpy | $H$ | Joule ($\text{J}$) | Total heat content of a system ($H = U + pV$). |
| Gibbs Free Energy | $G$ | Joule ($\text{J}$) | Energy available to do non-expansion work at constant $T$ and $p$. |
| Thermal Conductivity | $k$ | Watt per metre-Kelvin ($\text{W/(m}\cdot\text{K)}$) | Material property indicating ability to conduct heat. |
| Heat Capacity | $C$ | Joule per Kelvin ($\text{J/K}$) | Energy required to raise the temperature of a system by $1\text{ K}$. |

## 6. Mathematical models and equations

### The First Law of Thermodynamics
The conservation of energy for a closed system is expressed as:
$$ \Delta U = Q - W $$
Where $\Delta U$ is the change in internal energy, $Q$ is the heat added to the system, and $W$ is the work done *by* the system. For a fluid expanding against a constant pressure $p$, the work done is $W = p\Delta V$, where $\Delta V$ is the change in volume.

### The Second Law and Entropy
The macroscopic definition of the change in entropy ($\Delta S$) for a reversible process at absolute temperature $T$ is:
$$ \Delta S = \int \frac{dQ_{\text{rev}}}{T} $$
For any spontaneous (irreversible) process in an isolated system, the Second Law dictates:
$$ \Delta S_{\text{universe}} = \Delta S_{\text{system}} + \Delta S_{\text{surroundings}} > 0 $$

The microscopic (statistical) definition of entropy, formulated by Ludwig Boltzmann, connects the macroscopic state to the number of possible microscopic configurations ($\Omega$):
$$ S = k_B \ln \Omega $$
Where $k_B$ is the Boltzmann constant.

### Heat Transfer Equations
**Fourier's Law of Heat Conduction:**
$$ \dot{Q}_{\text{cond}} = -k A \frac{dT}{dx} $$
Where $\dot{Q}_{\text{cond}}$ is the rate of heat transfer ($\text{W}$), $k$ is the thermal conductivity, $A$ is the cross-sectional area, and $dT/dx$ is the temperature gradient.

**Stefan-Boltzmann Law of Thermal Radiation:**
$$ \dot{Q}_{\text{rad}} = \varepsilon \sigma A T^4 $$
Where $\dot{Q}_{\text{rad}}$ is the radiated power, $\varepsilon$ is the emissivity of the surface ($0 \le \varepsilon \le 1$), $\sigma$ is the Stefan-Boltzmann constant, $A$ is the surface area, and $T$ is the absolute temperature.

### Free Energy and Phase Transitions
The Gibbs free energy ($G$) is crucial for processes occurring at constant temperature and pressure:
$$ G = H - TS $$
Where $H$ is enthalpy, $T$ is temperature, and $S$ is entropy. A process is spontaneous if the change in Gibbs free energy is negative ($\Delta G < 0$). During a phase transition (like ice melting at $0^\circ\text{C}$), the two phases are in equilibrium, and $\Delta G = 0$. The transition is driven by the balance between minimizing enthalpy (favoring the solid state) and maximizing entropy (favoring the liquid state).

### Carnot Efficiency
The maximum theoretical efficiency ($\eta_{\text{Carnot}}$) of a heat engine operating between a hot reservoir at temperature $T_H$ and a cold reservoir at temperature $T_C$ is:
$$ \eta_{\text{Carnot}} = 1 - \frac{T_C}{T_H} $$
This demonstrates that no heat engine can be $100\%$ efficient unless the cold reservoir is at absolute zero, which is practically impossible.

## 7. Definitions of symbols and units

*   $U$: Internal energy, measured in Joules ($\text{J}$).
*   $Q$: Heat transferred, measured in Joules ($\text{J}$).
*   $W$: Work done, measured in Joules ($\text{J}$).
*   $p$: Pressure, measured in Pascals ($\text{Pa}$ or $\text{N/m}^2$).
*   $V$: Volume, measured in cubic metres ($\text{m}^3$).
*   $T$: Absolute temperature, measured in Kelvin ($\text{K}$).
*   $S$: Entropy, measured in Joules per Kelvin ($\text{J/K}$).
*   $k_B$: Boltzmann constant, exactly $1.380649 \times 10^{-23}\text{ J/K}$.
*   $\Omega$: Number of microstates (dimensionless).
*   $\dot{Q}$: Rate of heat transfer, measured in Watts ($\text{W}$ or $\text{J/s}$).
*   $k$: Thermal conductivity, measured in $\text{W/(m}\cdot\text{K)}$.
*   $A$: Area, measured in square metres ($\text{m}^2$).
*   $x$: Distance, measured in metres ($\text{m}$).
*   $\varepsilon$: Emissivity, a dimensionless property of a material's surface.
*   $\sigma$: Stefan-Boltzmann constant, exactly $5.670374419 \times 10^{-8}\text{ W/(m}^2\cdot\text{K}^4)$.
*   $H$: Enthalpy, measured in Joules ($\text{J}$).
*   $G$: Gibbs free energy, measured in Joules ($\text{J}$).
*   $\eta$: Efficiency, a dimensionless ratio (often expressed as a percentage).

## 8. Assumptions and approximations

*   **Ideal Gas Assumption:** Many introductory thermodynamic models assume gases behave ideally, meaning the particles have no volume and exert no intermolecular forces other than perfectly elastic collisions. This breaks down at high pressures and low temperatures.
*   **Reversibility:** The concept of a reversible process (one that can be reversed by an infinitesimal change in conditions without increasing the entropy of the universe) is an idealisation. All real macroscopic processes are irreversible due to friction, turbulence, and finite temperature gradients.
*   **Continuum Assumption:** Macroscopic thermodynamics assumes matter is a continuous medium, ignoring its discrete atomic structure. This is valid when the system size is vastly larger than the mean free path of the particles.
*   **Constant Properties:** Equations like Fourier's law often assume thermal conductivity ($k$) is constant, though it typically varies with temperature.

## 9. Spatial and temporal scales

Thermodynamics bridges the microscopic and macroscopic worlds.
*   **Spatial:** The principles apply from the scale of individual molecules (statistical mechanics, nanometres) to everyday engineering systems (engines, metres), up to planetary atmospheres and the entire universe (cosmology, billions of light-years).
*   **Temporal:** Thermodynamic processes span vast time scales. Molecular collisions occur in picoseconds ($10^{-12}\text{ s}$), while the cooling of a star or the heat transfer through the Earth's mantle takes billions of years. The Second Law defines the macroscopic direction of time itself.

## 10. Common misconceptions

*   **Misconception:** "Heat rises." **Correction:** Hot *fluids* (like air or water) rise due to buoyancy because they are less dense than the surrounding cooler fluid (convection). Heat itself transfers in all directions from hot to cold.
*   **Misconception:** "Cold flows into a room when a window is opened." **Correction:** Cold is not a substance; it is the absence of thermal energy. Heat flows *out* of the warm room into the cold exterior.
*   **Misconception:** "Entropy means things always get messy." **Correction:** While often likened to "disorder," entropy is strictly a measure of the number of accessible microstates. A system can spontaneously become more structurally ordered (like water freezing into an ice crystal) if it releases enough heat to increase the entropy of its surroundings by a greater amount.
*   **Misconception:** "Energy is used up." **Correction:** Energy is never destroyed (First Law); it is simply converted into less useful forms, typically low-temperature thermal energy, increasing the entropy of the universe (Second Law).

## 11. Connections to other modules

*   **03-mathematical-models:** Provides the calculus and statistical frameworks necessary to derive thermodynamic equations and understand probability distributions of microstates.
*   **06-matter-quantum:** Explains the atomic and molecular structures that store internal energy and dictate properties like heat capacity and thermal conductivity.
*   **09-fluid-dynamics:** Essential for understanding convection, the behavior of working fluids in engines, and atmospheric thermodynamics.
*   **12-chemical-kinetics:** Relies on thermodynamics (specifically free energy) to determine whether chemical reactions will occur spontaneously and where equilibrium lies.

## 12. Sources

1.  Kaviany, M. (2014). *Heat Transfer Physics* (2nd ed.). Cambridge University Press. [1]
2.  Cengel, Y. A., & Boles, M. A. (2015). *Thermodynamics: An Engineering Approach* (8th ed.). McGraw-Hill Education. [2]
3.  Frenkel, D. (1999). Entropy-driven phase transitions. *Physica A: Statistical Mechanics and its Applications*, 263(1-4), 26-38. [3]
4.  Baus, M., & Tejero, C. F. (2008). *Equilibrium Statistical Physics: Phases of Matter and Phase Transitions*. Springer. [4]
