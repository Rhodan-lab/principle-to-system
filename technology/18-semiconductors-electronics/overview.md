---
title: "Semiconductors, electronics, and computer hardware"
slug: 18-semiconductors-electronics
module: "Module 18"
domain: technology
status: reviewed
prerequisites: [06-matter-quantum, 10-electricity-magnetism, 17-materials-manufacturing]
connections: [19-software-ai, 20-sensors-control-infrastructure]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Semiconductors, electronics, and computer hardware

## 1. The central questions

How do material states, interfaces, fields, and carrier populations create controllable electronic behaviour? How are device characteristics converted into noise-tolerant logic, memory, sensing, communication, and power conversion? How do fabrication, metrology, architecture, packaging, software, workload, and reliability determine system performance beyond the behaviour of one transistor?

## 2. Observable phenomena

The effects of semiconductor physics are ubiquitous in modern life, though the mechanisms operate at a microscopic scale. A smartphone performing many operations while remaining within thermal limits reflects device efficiency, architecture, workload scheduling, packaging, cooling, and power management rather than semiconductor efficiency alone. The illumination of a room by light-emitting diodes (LEDs) demonstrates the conversion of electrical energy into light across a semiconductor junction. The ability of a solar panel to generate electricity when exposed to sunlight is the reverse process. Moore's original observation concerned economical component density. Later performance gains also depended on device design, architecture, memory, software, packaging, and power limits; it is an historical trend, not a physical law or guaranteed forecast.

## 3. Essential concepts

**Bands and Fermi level:** Periodic solids have allowed electronic states whose occupancy is described using band structure and the Fermi level. “Valence” and “conduction” bands are useful labels for many semiconductors, but metals, degenerate semiconductors, surfaces, disorder, and low-dimensional devices need more careful descriptions.

**Semiconductor behaviour:** Conductivity depends on band structure, carrier statistics, temperature, defects, dopants, contacts, fields, illumination, and scattering. A fixed band-gap threshold does not universally separate conductors, semiconductors, and insulators.

**Electrons and holes:** A hole is a quasiparticle description of unoccupied valence-band states and their collective response. Carrier charge, effective mass, mobility, and lifetime are model- and material-dependent.

**Doping and activation:** Donors and acceptors introduce electronic states and shift carrier populations. Dopant concentration is not identical to free-carrier concentration because activation, compensation, degeneracy, defects, and temperature matter.

**Junctions and interfaces:** A p–n junction develops space charge and a built-in electrostatic potential. The depletion approximation neglects mobile charge in a region for tractability; the physical carrier density is not literally zero.

## 4. Mechanisms and causal chains

**Diodes:** Applied bias changes electrostatic barriers and carrier injection. Forward current, reverse leakage, recombination, series resistance, capacitance, and breakdown depend on device structure and operating regime; a diode is not an ideal one-way valve.

**BJTs:** Emitter injection, transport through a thin base, recombination, and collector fields produce current gain. “A small base current controls a large current” is a circuit-level approximation, not the microscopic mechanism.

**MOSFETs:** Gate voltage changes surface potential and carrier density near an insulated interface. Current depends continuously on gate and drain bias, geometry, capacitance, mobility, contacts, leakage, and short-channel effects. Threshold is not a hard on/off boundary.

**Logic and memory:** Circuits assign voltage ranges to logical states with noise margins and timing constraints. Information is encoded in physical states but is not identical to charge flow or energy.

## 5. Important quantities

| Quantity | Symbol | Unit | Boundary |
| :--- | :---: | :--- | :--- |
| Band-gap energy | $E_g$ | J or eV | Depends on material, temperature, strain, composition, and structure. |
| Fermi level | $E_F$ | J or eV | Chemical potential for electrons under equilibrium conditions. |
| Carrier concentration | $n,p$ | $m^{-3}$ | Free-carrier density, not automatically equal to dopant density. |
| Mobility | $\mu_n,\mu_p$ | $m^2/(V\,s)$ | Low-field transport parameter affected by scattering and field. |
| Threshold voltage | $V_{th}$ | V | Extraction- and model-dependent transition parameter. |
| Subthreshold slope | $S$ | V/decade | Describes current change below threshold over a stated regime. |
| Delay and energy | $t_d,E_{switch}$ | s, J | Circuit- and workload-dependent rather than device-count-only. |

## 6. Mathematical models and equations

For a non-degenerate semiconductor with approximately parabolic bands in thermal equilibrium,
$$n_i\approx\sqrt{N_cN_v}\exp\left(-\frac{E_g}{2k_BT}\right),\qquad np=n_i^2.$$
These relations require equilibrium and Maxwell–Boltzmann approximations; degeneracy, band-gap narrowing, nonequilibrium generation, and traps can invalidate them.

In a low-field drift model,
$$\sigma=q(n\mu_n+p\mu_p).$$
Mobility need not remain constant at high field, high doping, or strong confinement.

For an ideal abrupt non-degenerate homojunction with activated dopants,
$$V_{bi}=\frac{k_BT}{q}\ln\left(\frac{N_AN_D}{n_i^2}\right).$$
The built-in potential is not directly measured by placing a voltmeter across equilibrium contacts.

A long-channel square-law MOSFET model can be useful pedagogically, but modern devices require compact models including velocity saturation, mobility degradation, channel-length modulation, leakage, capacitance, variability, and contact effects.

## 7. Definitions of symbols and units

- $E_g$: band-gap energy, J or eV.
- $E_F$: Fermi level or electron chemical potential under equilibrium, J or eV.
- $k_B$: Boltzmann constant, exactly $1.380649\times10^{-23}$ J/K.
- $T$: absolute temperature, K.
- $q$: elementary charge magnitude, exactly $1.602176634\times10^{-19}$ C.
- $n,p$: free electron and hole concentrations, m$^{-3}$.
- $n_i$: intrinsic carrier concentration under the stated model, m$^{-3}$.
- $N_c,N_v$: effective densities of states, m$^{-3}$.
- $N_D,N_A$: activated donor and acceptor concentrations in the ideal junction model, m$^{-3}$.
- $\mu_n,\mu_p$: electron and hole mobility in the stated transport regime, m$^2$/(V$\,$s).
- $\sigma$: electrical conductivity, S/m.
- $V_{bi}$: modelled built-in potential, V.
- $V_{th}$: extraction- and compact-model-dependent threshold voltage, V.

## 8. Assumptions and approximations

- **Equilibrium and non-degenerate statistics:** Carrier formulas change under strong injection, illumination, degeneracy, trapping, and rapid transients.
- **Complete ionisation:** Can fail at low temperature, high doping, compensation, or deep impurity levels.
- **Depletion and abrupt-junction approximations:** Simplify Poisson's equation but omit graded profiles and mobile carriers.
- **Low-field mobility:** Drift mobility is not constant across electric field, temperature, geometry, and carrier density.
- **Long-channel compact models:** Nanoscale transistors include short-channel electrostatics, tunnelling, discrete variability, parasitics, self-heating, and quantum confinement.

## 9. Spatial and temporal scales

Electronic structure begins at atomic and unit-cell scales, while depletion widths, channels, interconnects, vias, packages, boards, and systems span nanometres to metres. Industrial node names do not directly specify one physical dimension. Characteristic times range from carrier scattering and dielectric response through device switching, interconnect propagation, memory access, clock periods, thermal transients, ageing, and product lifetimes. A processor's instruction rate cannot be inferred from transistor transit time or clock frequency alone.

## 10. Common misconceptions

- **“A semiconductor is halfway between a conductor and an insulator.”** The useful feature is controllable carrier population and transport within a designed material and device structure.
- **“Holes are imaginary.”** Holes are quasiparticles that accurately describe collective valence-band transport within a model; they are not tiny empty beads moving through space.
- **“A transistor is either perfectly off or on.”** Current changes continuously, leakage persists, and logic states are defined by circuit thresholds and noise margins.
- **“Electrical information travels at electron drift speed.”** Signal propagation follows electromagnetic fields and circuit geometry, while carrier drift and local charging support that propagation.
- **“Smaller node names equal one literal feature size.”** Node labels bundle technology generations and do not specify every gate, pitch, or interconnect dimension.

## 11. Connections to other modules

- **06-matter-quantum:** Quantum states, statistics, tunnelling, and periodic potentials underpin device models.
- **10-electricity-magnetism:** Fields, capacitance, current continuity, and transmission-line effects connect devices to circuits.
- **17-materials-manufacturing:** Crystal growth, deposition, implantation, etching, patterning, cleaning, packaging, and metrology create devices.
- **19-software-ai:** Instruction sets, memory hierarchies, compilers, workloads, and algorithms determine how hardware capability is used.
- **20-sensors-control-infrastructure:** Sensors, power electronics, embedded controllers, and communication interfaces connect chips to physical systems.

## Phase 9 review boundaries and validity limits

- Band, carrier, junction, and compact-device equations assume specified equilibrium, statistics, geometry, temperature, and bias regimes.
- Threshold voltage is a model parameter, not a hard microscopic on/off boundary; leakage, short-channel effects, variability, and parasitics matter.
- Technology-node names are industrial labels rather than literal dimensions of every device feature.
- Device performance, yield, reliability, and scaling claims require metrology, architecture, packaging, workload, and thermal context.

## 12. Sources

1. Massachusetts Institute of Technology OpenCourseWare. *Integrated Microelectronic Devices*. https://ocw.mit.edu/courses/6-720j-integrated-microelectronic-devices-spring-2007/
2. National Institute of Standards and Technology. *Semiconductors*. https://www.nist.gov/semiconductors
3. Intel. *Moore's Law*. https://www.intel.com/content/www/us/en/history/virtual-vault/articles/moores-law.html
4. National Institute of Standards and Technology. *CHIPS for America Metrology Program*. https://www.nist.gov/chips/research-development-programs/metrology-program
5. Orji, N. G., et al. *Metrology for the Next Generation of Semiconductor Devices*. https://www.nist.gov/publications/metrology-next-generation-semiconductor-devices
6. Postek, M. T., and Bennett, M. H. *Critical Dimension and Overlay Metrology*. https://www.nist.gov/publications/critical-dimension-and-overlay-metrology
