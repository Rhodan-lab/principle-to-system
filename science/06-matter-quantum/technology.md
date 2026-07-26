---
title: "Quantum Technologies and Atomic Engineering"
slug: 06-matter-quantum-technology
module: "Module 06"
domain: science
status: reviewed
prerequisites: [01-scientific-reasoning, 02-measurement-uncertainty, 03-mathematical-models]
connections: [07-chemical-bonding, 08-energy-thermodynamics, 10-electricity-magnetism, 17-materials-manufacturing, 18-semiconductors-electronics]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Quantum Technologies and Atomic Engineering

## 1. Scientific principles used

The technologies discussed in this module rely on the fundamental principles of quantum mechanics and atomic structure:
- **Quantised Energy Levels:** Electrons in atoms and molecules can only occupy specific, discrete energy states.
- **Stimulated Emission:** An incoming photon can induce an excited electron to drop to a lower energy state, increasing occupation of the same optical mode, producing radiation matched in frequency and phase relation under the device's mode conditions.
- **Quantum Tunnelling:** A quantum particle has a non-zero probability of passing through a potential energy barrier that it classically should not have enough energy to surmount.
- **Nuclear Magnetic Resonance (NMR):** Atomic nuclei with non-zero spin possess magnetic moments. A static field creates a small population imbalance and net magnetisation; radiofrequency fields drive resonance, and the precessing magnetisation induces signals in receiver coils.

## 2. The engineering problem

How can we harness the discrete, probabilistic nature of the quantum world to build practical macroscopic devices? The engineering challenge lies in isolating, controlling, and amplifying quantum effects that are usually washed out by thermal noise and decoherence at room temperature. For example, how do we create a coherent beam of light from the random emission of billions of atoms? How do we image the internal structure of the human body non-invasively using the quantum spin of protons? How do we image surfaces at the atomic scale?

## 3. Main components

To illustrate these concepts, we examine three distinct technologies: the Laser, the Magnetic Resonance Imaging (MRI) scanner, and the Scanning Tunnelling Microscope (STM).

**The Laser:**
- **Gain Medium:** A material (gas, liquid, or solid) containing atoms or molecules with suitable discrete energy levels.
- **Pump Source:** An energy source (electrical discharge, flashlamp, or another laser) used to excite the electrons in the gain medium.
- **Optical Resonator:** A pair of mirrors (one fully reflective, one partially reflective) surrounding the gain medium to reflect photons back and forth.

**The MRI Scanner:**
- **Main Magnet:** A powerful superconducting electromagnet that generates a strong, uniform static magnetic field ($B_0$).
- **Gradient Coils:** Secondary electromagnets that create controlled spatial variations in the main magnetic field.
- **Radiofrequency (RF) Coils:** Antennas that transmit RF pulses to excite atomic nuclei and receive the resulting RF signals emitted by the nuclei.

**The Scanning Tunnelling Microscope (STM):**
- **Conducting Tip:** An atomically sharp metal needle.
- **Piezoelectric Scanner:** A mechanism that moves the tip in three dimensions with sub-nanometre precision.
- **Feedback Loop:** Electronic circuitry that monitors the tunnelling current and adjusts the tip height to maintain a constant current.

## 4. How the components interact

**Laser:** The pump source injects energy into the gain medium, exciting a large number of electrons to a higher energy state, creating a "population inversion" (more electrons in the excited state than the ground state). When an electron spontaneously drops to a lower state, it emits a photon. Interaction with the optical field can stimulate emission into the same resonator mode, coherently increasing that mode's field amplitude. The optical resonator reflects these photons back and forth through the gain medium, causing an avalanche of stimulated emission. A fraction of this coherent light escapes through the partially reflective mirror as the laser beam.

**MRI:** The main magnet creates a small net nuclear magnetisation from hydrogen nuclei in the patient's body. The RF coils transmit a pulse of radio waves at the specific resonant frequency (Larmor frequency) of the protons, rotating the net magnetisation away from equilibrium. When the RF pulse is turned off, the protons gradually realign with the main magnetic field, inducing a measurable voltage in the receive coil as transverse magnetisation precesses and relaxes. The gradient coils slightly alter the magnetic field strength across the body, causing protons in different locations to resonate at slightly different frequencies. By analysing these frequencies, a computer reconstructs a 3D image of the tissue.

**STM:** The conducting tip is brought extremely close (within a sub-nanometre tunnelling distance) to a conductive sample surface. A small voltage is applied between the tip and the sample. Due to quantum tunnelling, electrons can cross the vacuum gap between the tip and the surface, creating a measurable tunnelling current. Because the tunnelling probability depends exponentially on the distance, the current is highly sensitive to the gap width. As the piezoelectric scanner moves the tip across the surface, the feedback loop adjusts the tip's height to keep the current constant. The recorded height adjustments map a signal that depends on tip–sample distance and local electronic density of states of the surface.

## 5. Matter, energy, force, or information flow

- **Laser:** Energy flows from the pump source into the gain medium (excitation), is temporarily stored in the quantum states of the atoms, and is then extracted as a highly directional, coherent flow of electromagnetic energy (photons).
- **MRI:** Energy flows from the RF coils into the nuclear spins of the patient's tissue. The tissue then releases this energy back as an RF signal. This signal carries spatial information (encoded by the gradient coils) and tissue composition information (encoded by the relaxation times of the spins).
- **STM:** A small applied potential difference produces a tunnelling current across the vacuum barrier; voltage is energy per unit charge, not a mechanical force. The magnitude of this current provides information about the atomic-scale distance and the local density of electronic states.

## 6. System architecture

**Explicit Principle-to-System Chain: The Scanning Tunnelling Microscope**
1. **Scientific Principle:** Quantum Tunnelling. The wavefunction of an electron does not drop abruptly to zero at a potential barrier (like the vacuum between two metals) but decays exponentially.
2. **Mechanism:** When the tip and sample are sufficiently close, their electronic states overlap across the barrier and a bias can produce a measurable tunnelling current.
3. **Component:** An atomically sharp tip and a piezoelectric positioning system capable of sub-nanometre control.
4. **Sub-system:** A feedback circuit that measures the exponentially sensitive tunnelling current and outputs a control voltage to the piezoelectric scanner to maintain a constant current.
5. **System:** The complete STM, which translates the control voltages into a topographical map of individual atoms on a surface.

## 7. Design constraints

- **Laser:** The gain medium must have a specific set of energy levels that allow for a metastable excited state, otherwise population inversion cannot be achieved. The mirrors must be precisely aligned.
- **MRI:** The main magnetic field must be incredibly uniform (homogenous) over the imaging volume. The superconducting coils must be kept at cryogenic temperatures (usually using liquid helium).
- **STM:** The system must be heavily isolated from external vibrations, as even microscopic acoustic noise can cause the tip to crash into the sample. The tip must be atomically sharp.

## 8. Performance and efficiency

- **Laser:** Wall-plug efficiency depends strongly on laser architecture, wavelength, operating point, optical losses, and cooling requirements; performance must be reported for the specific device.
- **MRI:** Performance depends on signal-to-noise ratio, spatial and temporal resolution, sequence design, coil geometry, field homogeneity, scan time, and patient constraints. Higher field can improve available signal but also increases engineering and safety challenges.
- **STM:** Under suitable vibration, thermal, electronic, tip, and sample conditions, STM can resolve atomic-scale electronic and topographic contrast; the result is not a simple geometric height map.

## 9. Reliability and failure modes

- **Laser:** Optical degradation is a primary failure mode. High-intensity light can damage the mirrors or the gain medium itself. In gas lasers, the gas mixture can degrade over time.
- **MRI:** A quench is a serious abnormal event in which part of the superconducting magnet becomes resistive, rapidly depositing stored magnetic energy and potentially venting helium; engineered protection and ventilation are essential.
- **STM:** Tip degradation is the most common failure. The atomically sharp tip can pick up stray atoms from the surface or blunt itself by accidentally touching the sample, instantly ruining the atomic resolution.

## 10. Safety principles

- **Laser:** High-power lasers pose severe eye and skin hazards. Safety protocols involve interlocks, beam enclosures, and specific protective eyewear tailored to the laser's wavelength.
- **MRI:** The immense magnetic field is always on. Ferromagnetic objects (like oxygen tanks, tools, or certain medical implants) can become dangerous projectiles if brought into the scanner room.
- **STM:** Generally safe for the operator, as it operates at low voltages and currents. However, ultra-high vacuum (UHV) STMs require careful handling of vacuum equipment and bake-out procedures.

## 11. Environmental and lifecycle considerations

- **Laser:** Many industrial lasers require significant cooling water and electricity. Disposal of certain gain media (like toxic dyes or heavy-metal-doped glasses) requires specialised waste management.
- **MRI:** The reliance on liquid helium is a major sustainability issue, as helium is a non-renewable resource that is becoming increasingly scarce. Modern designs aim to reduce or eliminate helium boil-off.
- **STM:** STMs are low-volume, highly specialised research tools. Their environmental impact is primarily tied to the energy required to maintain ultra-high vacuum systems and cryogenic cooling for low-temperature experiments.

## 12. Connections to other technologies

- **Semiconductor Manufacturing:** Lasers are essential for photolithography, the process used to pattern nanoscale transistors on silicon wafers.
- **Telecommunications:** Fibre optic networks rely entirely on semiconductor lasers to transmit data across the globe.
- **Materials Science:** STMs and related atomic force microscopes (AFMs) are the foundational tools of nanotechnology, allowing scientists to manipulate matter atom by atom.

## Phase 7 review boundaries and validity limits

- Quantisation means that particular observables have discrete spectra in particular systems; it does not mean every physical quantity is universally restricted to discrete values.
- A wavefunction is a state representation and probability amplitude. The Born rule relates its squared magnitude to probabilities for measurement outcomes; an orbital is not a material cloud or a classical trajectory.
- The uncertainty relation concerns statistical spreads for identically prepared states. It is not merely instrument disturbance and does not imply that every property lacks a state-dependent value in the same way.
- Quantum field theory describes the vacuum as a lowest-energy state with measurable correlations and fluctuations. “Virtual particles popping in and out” is a calculation metaphor, not a literal movie of detectable particles.
- Nonrelativistic equations, independent-particle orbitals, and the Born–Oppenheimer approximation have explicit validity domains. Relativistic, many-body, nuclear, or quantum-field models are needed outside them.

## 13. Sources



1. CERN. *The Standard Model*. https://home.cern/science/physics/standard-model/
2. OpenStax. *Chemistry 2e: Development of Quantum Theory*. https://openstax.org/books/chemistry-2e/pages/6-3-development-of-quantum-theory
3. National Institute of Standards and Technology. *Atomic Spectroscopy Databases*. https://www.nist.gov/pml/atomic-spectroscopy-databases
4. LibreTexts Chemistry. *Quantum Mechanics and Atomic Structure*. https://chem.libretexts.org/Bookshelves/Physical_and_Theoretical_Chemistry_Textbook_Maps/Physical_Chemistry_for_the_Biosciences_(LibreTexts)/11%3A_Quantum_Mechanics_and_Atomic_Structure
5. National Institute of Biomedical Imaging and Bioengineering. *Magnetic Resonance Imaging (MRI)*. https://www.nibib.nih.gov/science-education/science-topics/magnetic-resonance-imaging-mri
6. National Institute of Standards and Technology. *Designing Advanced Scanning Probe Microscopy Instruments*. https://www.nist.gov/programs-projects/designing-advanced-scanning-probe-microscopy-instruments
