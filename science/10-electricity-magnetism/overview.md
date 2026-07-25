---
title: "Electricity, Magnetism, Fields, and Circuits"
slug: 10-electricity-magnetism
module: "Module 10"
domain: science
status: reviewed
prerequisites: [03-mathematical-models, 06-matter-quantum]
connections: [18-semiconductors-electronics, 20-sensors-control-infrastructure]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Electricity, Magnetism, Fields, and Circuits

## 1. The central questions

How do charges interact across empty space? What is the relationship between electricity and magnetism? How can we control the flow of energy and information using these phenomena? These questions drive the study of electromagnetism, a fundamental force that governs the structure of matter and enables modern technology. At its core, electromagnetism explores how stationary and moving charges create fields that exert forces on other charges, and how these fields propagate as waves.

## 2. Observable phenomena

Electromagnetic phenomena are ubiquitous. Static electricity causes hair to stand on end and lightning to strike. Magnets attract iron and align compass needles with the Earth's magnetic field. Electric currents heat wires, produce light, and drive motors. Electromagnetic induction allows generators to convert mechanical work into electrical energy. Radio waves, microwaves, visible light, and X-rays are all manifestations of oscillating electric and magnetic fields propagating through space.

## 3. Essential concepts

**Electric Charge:** A fundamental property of matter, existing in positive and negative forms. Like charges repel; opposite charges attract. Charge is conserved and quantized.

**Electric Field ($\mathbf{E}$):** A vector field created by electric charges that exerts a force on other charges within the field. It represents the force per unit charge.

**Magnetic Field ($\mathbf{B}$):** A vector field created by moving charges (currents) or changing electric fields. It exerts a force on moving charges and magnetic dipoles.

**Electromagnetic Induction:** The process by which a changing magnetic field creates an electric field, which can drive a current in a closed circuit.

**Circuits:** Closed loops through which electric current can flow, comprising sources (like batteries), conductors, and components (resistors, capacitors, inductors) that control the flow of energy.

## 4. Mechanisms and causal chains

The interaction between charges is mediated by fields. A stationary charge creates an electric field in the surrounding space. When another charge enters this field, it experiences a force proportional to the field strength and its own charge. 

When charges move, they constitute an electric current. This current generates a magnetic field. If a charge moves through an existing magnetic field, it experiences a Lorentz force perpendicular to both its velocity and the magnetic field.

A changing magnetic field induces an electric field (Faraday's Law). Conversely, a changing electric field induces a magnetic field (Maxwell's addition to Ampère's Law). This reciprocal induction allows electromagnetic waves to propagate through empty space without a medium.

In a circuit, a voltage source creates an electric field that drives charge carriers (usually electrons) through conductors. Resistors dissipate energy as heat, capacitors store energy in electric fields, and inductors store energy in magnetic fields. The interplay of these components determines the circuit's behavior over time.

## 5. Important quantities

| Quantity | Symbol | SI Unit | Description |
| :--- | :---: | :--- | :--- |
| Electric Charge | $q, Q$ | Coulomb (C) | Fundamental property determining electromagnetic interactions. |
| Electric Field | $\mathbf{E}$ | Volts per meter (V/m) or N/C | Force per unit charge exerted on a test charge. |
| Electric Potential | $V$ | Volt (V) | Potential energy per unit charge. |
| Magnetic Field | $\mathbf{B}$ | Tesla (T) | Force per unit velocity per unit charge. |
| Electric Current | $I$ | Ampere (A) | Rate of flow of electric charge. |
| Resistance | $R$ | Ohm ($\Omega$) | Opposition to current flow. |
| Capacitance | $C$ | Farad (F) | Ability to store charge per unit voltage. |
| Inductance | $L$ | Henry (H) | Opposition to changes in current. |
| Magnetic Flux | $\Phi_B$ | Weber (Wb) | Total magnetic field passing through a given area. |

## 6. Mathematical models and equations

**Coulomb's Law:** Describes the electrostatic force $\mathbf{F}$ between two point charges $q_1$ and $q_2$ separated by a distance $r$:
$$ \mathbf{F} = \frac{1}{4\pi\epsilon_0} \frac{q_1 q_2}{r^2} \mathbf{\hat{r}} $$
where $\epsilon_0$ is the vacuum permittivity and $\mathbf{\hat{r}}$ is the unit vector pointing from one charge to the other.

**Lorentz Force Law:** The total force $\mathbf{F}$ on a charge $q$ moving with velocity $\mathbf{v}$ in the presence of an electric field $\mathbf{E}$ and a magnetic field $\mathbf{B}$:
$$ \mathbf{F} = q(\mathbf{E} + \mathbf{v} \times \mathbf{B}) $$

**Maxwell's Equations (Integral Form):**
1. **Gauss's Law for Electricity:** The electric flux through a closed surface is proportional to the enclosed charge $Q_{enc}$.
   $$ \oint \mathbf{E} \cdot d\mathbf{A} = \frac{Q_{enc}}{\epsilon_0} $$
2. **Gauss's Law for Magnetism:** The magnetic flux through a closed surface is zero (no magnetic monopoles).
   $$ \oint \mathbf{B} \cdot d\mathbf{A} = 0 $$
3. **Faraday's Law of Induction:** A changing magnetic flux induces an electromotive force (EMF).
   $$ \oint \mathbf{E} \cdot d\mathbf{l} = -\frac{d\Phi_B}{dt} $$
4. **Ampère-Maxwell Law:** Magnetic fields are generated by electric currents and changing electric fields.
   $$ \oint \mathbf{B} \cdot d\mathbf{l} = \mu_0 I_{enc} + \mu_0 \epsilon_0 \frac{d\Phi_E}{dt} $$
   where $\mu_0$ is the vacuum permeability.

**Ohm's Law for an ohmic element:** Relates voltage $V$, current $I$, and resistance $R$ when the element is approximately linear under specified conditions:
$$ V = IR $$

## 7. Definitions of symbols and units

- $\mathbf{F}$: Force vector, measured in Newtons (N).
- $q, Q$: Electric charge, measured in Coulombs (C).
- $r$: Distance, measured in meters (m).
- $\epsilon_0$: Vacuum permittivity, $\approx 8.854 \times 10^{-12}$ F/m.
- $\mathbf{E}$: Electric field vector, measured in Volts per meter (V/m).
- $\mathbf{v}$: Velocity vector, measured in meters per second (m/s).
- $\mathbf{B}$: Magnetic field vector, measured in Teslas (T).
- $d\mathbf{A}$: Differential area vector, measured in square meters (m$^2$).
- $d\mathbf{l}$: Differential length vector, measured in meters (m).
- $\Phi_B$: Magnetic flux, measured in Webers (Wb).
- $\Phi_E$: Electric flux, measured in Volt-meters (V$\cdot$m).
- $\mu_0$: Vacuum permeability, experimentally determined in the revised SI (approximately $1.25663706\times10^{-6}\,\text{H/m}$).
- $I$: Electric current, measured in Amperes (A).
- $V$: Electric potential or voltage, measured in Volts (V).
- $R$: Resistance, measured in Ohms ($\Omega$).

## 8. Assumptions and approximations

- **Point Charges:** Coulomb's law assumes charges are concentrated at mathematical points, which is a valid approximation when the distance between objects is much larger than their size.
- **Ideal Components:** Circuit models often assume ideal wires with zero resistance, ideal voltage sources with zero internal resistance, and perfect capacitors/inductors. Real components have parasitic properties.
- **Lumped Element Model:** Circuit theory assumes that the physical size of the circuit is much smaller than the wavelength of the electromagnetic signals it carries, allowing us to treat components as discrete "lumps" rather than distributed systems.
- **Classical Electromagnetism:** Maxwell's equations are classical and do not account for quantum mechanical effects, which become significant at atomic scales (quantum electrodynamics).

## 9. Spatial and temporal scales

Electromagnetism operates across an enormous range of scales. Spatially, it governs interactions from the subatomic level (binding electrons to nuclei at $\sim 10^{-10}$ m) to the galactic scale (magnetic fields shaping galaxies over $10^{21}$ m). Temporally, electromagnetic phenomena range from the incredibly fast oscillations of gamma rays ($\sim 10^{-20}$ s) to the slow variations of the Earth's magnetic field over millennia. In engineering, circuit frequencies range from direct current (DC, 0 Hz) to microwave frequencies ($10^9$ to $10^{11}$ Hz) used in telecommunications.

## 10. Common misconceptions

- **Misconception:** Electrons travel at the speed of light in a wire.
  **Reality:** The *signal* (the electric field) propagates near the speed of light, but the individual electrons drift very slowly, typically on the order of millimeters per second.
- **Misconception:** Batteries supply electrons to a circuit.
  **Reality:** Batteries supply *energy* (voltage) that drives the electrons already present in the conducting wires.
- **Misconception:** Magnetic fields are just a different form of electric fields.
  **Reality:** While intimately connected through relativity, electric and magnetic fields are distinct phenomena in a given reference frame. A stationary charge produces only an electric field, while a moving charge produces both.

## 11. Connections to other modules

- **03-mathematical-models:** Provides the vector calculus framework necessary for Maxwell's equations.
- **06-matter-quantum:** Explains the microscopic origin of charge and magnetism in atoms and materials.
- **08-energy-thermodynamics:** Connects electrical resistance to heat dissipation (Joule heating).
- **11-waves-signals:** Builds on the fact that light is an electromagnetic wave, governed by Maxwell's equations.

## Phase 7 review boundaries and validity limits

- Electric and magnetic fields are components of one electromagnetic field whose decomposition depends on reference frame. They are not two unrelated substances.
- Ohm's law V = IR is a constitutive relation for approximately ohmic components under specified temperature and operating conditions, not a universal law for every device.
- Current divides among available branches according to circuit impedances and Kirchhoff's laws; it does not choose only a single “path of least resistance.”
- In the 2019 SI, c and e are exact defining constants, while μ₀ and ε₀ are experimentally determined quantities related through c² = 1/(μ₀ε₀).
- Lumped-circuit models are valid when propagation delays and distributed fields are negligible. At high frequency or large physical size, transmission-line and full-field models are required.

## 12. Sources


1. MIT OpenCourseWare. *8.02 Physics II: Electricity and Magnetism*. https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2019/
2. OpenStax. *University Physics Volume 2*. https://openstax.org/books/university-physics-volume-2/pages/1-introduction
3. OpenStax. *Maxwell's Equations and Electromagnetic Waves*. https://openstax.org/books/university-physics-volume-2/pages/16-1-maxwells-equations-and-electromagnetic-waves
4. Feynman, R. P., Leighton, R. B., and Sands, M. *The Feynman Lectures on Physics, Volume II*. https://www.feynmanlectures.caltech.edu/II_toc.html
