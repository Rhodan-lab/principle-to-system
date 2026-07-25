#!/usr/bin/env python3
"""Apply the focused Phase 7 scientific review to Modules 06–12.

The transformation is intentionally deterministic and idempotent. It corrects
known conceptual overstatements, replaces unsafe learner activities, aligns
local citations with the normalized central ledger, and promotes files to
Reviewed only as one coordinated 21-file set.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATE = "2026-07-26"
MODULES = {
    "06-matter-quantum": "science/06-matter-quantum",
    "07-chemical-bonding": "science/07-chemical-bonding",
    "08-energy-thermodynamics": "science/08-energy-thermodynamics",
    "09-motion-forces": "science/09-motion-forces",
    "10-electricity-magnetism": "science/10-electricity-magnetism",
    "11-waves-signals": "science/11-waves-signals",
    "12-fluids-materials": "science/12-fluids-materials",
}
ROLES = ("overview.md", "technology.md", "explore.md")

SOURCES = {
"06-matter-quantum": """## 12. Sources

1. CERN. *The Standard Model*. https://home.cern/science/physics/standard-model/
2. OpenStax. *Chemistry 2e: Development of Quantum Theory*. https://openstax.org/books/chemistry-2e/pages/6-3-development-of-quantum-theory
3. National Institute of Standards and Technology. *Atomic Spectroscopy Databases*. https://www.nist.gov/pml/atomic-spectroscopy-databases
4. LibreTexts Chemistry. *Quantum Mechanics and Atomic Structure*. https://chem.libretexts.org/Bookshelves/Physical_and_Theoretical_Chemistry_Textbook_Maps/Physical_Chemistry_for_the_Biosciences_(LibreTexts)/11%3A_Quantum_Mechanics_and_Atomic_Structure
""",
"07-chemical-bonding": """## 12. Sources

1. OpenStax. *Chemistry 2e*. https://openstax.org/books/chemistry-2e/pages/1-introduction
2. Whittingham, M. S. (2004). Introduction: Batteries and Fuel Cells. *Chemical Reviews*. https://pubs.acs.org/doi/10.1021/cr020705e
3. Zhang, J., et al. (2021). Intermolecular and Surface Interactions in Engineering. https://www.sciencedirect.com/science/article/pii/S209580992030360X
4. LibreTexts Chemistry. *Chemistry resources*. https://chem.libretexts.org/
""",
"08-energy-thermodynamics": """## 12. Sources

1. Moran, M. J., et al. *Fundamentals of Engineering Thermodynamics*. https://books.google.com/books?id=y9suEQAAQBAJ
2. Kaviany, M. *Heat Transfer Physics*. https://assets.cambridge.org/97811070/41783/frontmatter/9781107041783_frontmatter.pdf
3. Frenkel, D. (1999). Entropy-driven phase transitions. https://www.sciencedirect.com/science/article/pii/S0378437198005019
4. Bejan, A. *Advanced Engineering Thermodynamics*. https://books.google.com/books?id=j0zSDAAAQBAJ
""",
"09-motion-forces": """## 12. Sources

1. OpenStax. *University Physics Volume 1*. https://openstax.org/details/books/university-physics-volume-1
2. MIT OpenCourseWare. *8.01SC Classical Mechanics*. https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/
3. NASA. *Basics of Space Flight: Gravity and Mechanics*. https://science.nasa.gov/learn/basics-of-space-flight/chapter3-4/
4. Feynman, R. P., Leighton, R. B., and Sands, M. *The Feynman Lectures on Physics, Volume I*. https://www.feynmanlectures.caltech.edu/
""",
"10-electricity-magnetism": """## 12. Sources

1. MIT OpenCourseWare. *8.02 Physics II: Electricity and Magnetism*. https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2019/
2. OpenStax. *University Physics Volume 2*. https://openstax.org/books/university-physics-volume-2/pages/1-introduction
3. OpenStax. *Maxwell's Equations and Electromagnetic Waves*. https://openstax.org/books/university-physics-volume-2/pages/16-1-maxwells-equations-and-electromagnetic-waves
4. Feynman, R. P., Leighton, R. B., and Sands, M. *The Feynman Lectures on Physics, Volume II*. https://www.feynmanlectures.caltech.edu/II_toc.html
""",
"11-waves-signals": """## 12. Sources

1. MIT OpenCourseWare. *8.03SC Physics III: Vibrations and Waves*. https://ocw.mit.edu/courses/8-03sc-physics-iii-vibrations-and-waves-fall-2016/
2. MIT OpenCourseWare. *6.003 Signals and Systems*. https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/
3. OpenStax. *College Physics 2e: Oscillatory Motion and Waves*. https://openstax.org/books/college-physics-2e/pages/16-introduction-to-oscillatory-motion-and-waves
4. Agrawal, G. P. *Fiber-Optic Communication Systems*. https://doi.org/10.1002/9780470918524
""",
"12-fluids-materials": """## 12. Sources

1. Leishman, J. G. *Introduction to Aerospace Flight Vehicles: Energy and Bernoulli Equations*. https://eaglepubs.erau.edu/introductiontoaerospaceflightvehicles/chapter/energy-equation/
2. University of Central Florida. *University Physics Volume 1: Bernoulli's Equation*. https://pressbooks.online.ucf.edu/osuniversityphysics/chapter/14-6-bernoullis-equation/
3. Massachusetts Institute of Technology. *Mechanical Behavior of Materials: Linear Elastic Behavior*. https://mitxonline.mit.edu/courses/course-v1:MITxT+3.032.1x/
4. Nairn, J. A. (2000). Fracture mechanics of composites with residual stresses. https://www.cof.orst.edu/cof/wse/faculty/Nairn/papers/Damage.pdf
""",
}

BOUNDARIES = {
"06-matter-quantum": """## Phase 7 review boundaries and validity limits

- Quantisation means that particular observables have discrete spectra in particular systems; it does not mean every physical quantity is universally restricted to discrete values.
- A wavefunction is a state representation and probability amplitude. The Born rule relates its squared magnitude to probabilities for measurement outcomes; an orbital is not a material cloud or a classical trajectory.
- The uncertainty relation concerns statistical spreads for identically prepared states. It is not merely instrument disturbance and does not imply that every property lacks a state-dependent value in the same way.
- Quantum field theory describes the vacuum as a lowest-energy state with measurable correlations and fluctuations. “Virtual particles popping in and out” is a calculation metaphor, not a literal movie of detectable particles.
- Nonrelativistic equations, independent-particle orbitals, and the Born–Oppenheimer approximation have explicit validity domains. Relativistic, many-body, nuclear, or quantum-field models are needed outside them.
""",
"07-chemical-bonding": """## Phase 7 review boundaries and validity limits

- Ionic, covalent, and metallic bonding are useful limiting descriptions of electron density and many-body interactions, not perfectly separate boxes. “Full shells” are a heuristic rather than a universal cause of bonding.
- VSEPR predicts many main-group molecular shapes qualitatively but does not replace quantum chemistry and is unreliable for several transition-metal, delocalised, or hypervalent systems.
- Equilibrium constants are dimensionless when written using activities relative to standard states. Concentrations and partial pressures are approximations whose validity depends on non-ideality.
- A catalyst changes the reaction mechanism and rate constants but not the equilibrium constant or thermodynamic state difference. It may change chemical form during a catalytic cycle and is regenerated overall rather than literally remaining unchanged at every instant.
- Bond breaking requires energy, while the net energy of a reaction depends on all bonds and interactions broken and formed plus environmental conditions.
""",
"08-energy-thermodynamics": """## Phase 7 review boundaries and validity limits

- Temperature is a thermodynamic state variable defined through equilibrium and an equation of state; it is not generally identical to average translational kinetic energy.
- Entropy is a state function with thermodynamic and statistical definitions. “Disorder” is an unreliable shortcut; spontaneous change depends on the entropy balance of system plus surroundings.
- Heat and work are modes of energy transfer across a boundary, not stored substances. Sign conventions must be stated before using the First Law.
- Gibbs free-energy criteria apply to specified constraints, commonly constant temperature and pressure with only pressure–volume work. Negative ΔG predicts thermodynamic direction, not reaction speed.
- Stefan–Boltzmann emission is not the same as net radiative heat transfer; exchange with surroundings requires a difference such as εσA(T⁴ − T_sur⁴) under simplified view-factor conditions.
""",
"09-motion-forces": """## Phase 7 review boundaries and validity limits

- Newton's second law is fundamentally ΣF_ext = dp/dt. The familiar ma form requires constant mass in an inertial frame.
- Mass is an invariant measure in modern relativity; relativistic momentum and energy, not “relativistic mass,” replace the low-speed formulas as speed approaches c.
- Moment of inertia is generally a tensor. Treating it as a scalar is valid only for rotation about a specified principal or fixed axis.
- Third-law force pairs act on different bodies. Momentum conservation follows from the external-force balance for the chosen system; internal-force cancellation must be justified for the model used.
- Newtonian gravity is an accurate weak-field, low-speed approximation. General relativity is required for strong fields, high precision, or relativistic motion.
""",
"10-electricity-magnetism": """## Phase 7 review boundaries and validity limits

- Electric and magnetic fields are components of one electromagnetic field whose decomposition depends on reference frame. They are not two unrelated substances.
- Ohm's law V = IR is a constitutive relation for approximately ohmic components under specified temperature and operating conditions, not a universal law for every device.
- Current divides among available branches according to circuit impedances and Kirchhoff's laws; it does not choose only a single “path of least resistance.”
- In the 2019 SI, c and e are exact defining constants, while μ₀ and ε₀ are experimentally determined quantities related through c² = 1/(μ₀ε₀).
- Lumped-circuit models are valid when propagation delays and distributed fields are negligible. At high frequency or large physical size, transmission-line and full-field models are required.
""",
"11-waves-signals": """## Phase 7 review boundaries and validity limits

- A wave transports energy and momentum, while material elements in a mechanical medium usually oscillate around equilibrium; some waves and nonlinear flows can also produce net transport.
- Refraction follows phase matching and a change in phase velocity or refractive index, not a vague distinction between “optically dense” and “less dense” matter.
- Fourier series apply to suitably behaved periodic signals; Fourier transforms generalise the idea to non-periodic signals. Real measurements also involve finite windows, sampling, leakage, and noise.
- Destructive interference means local cancellation of the chosen field variable. Energy conservation must be evaluated from flux and boundary conditions; energy may be redistributed, reflected, or stored rather than always appearing at a nearby bright fringe.
- Fiber guidance is described by electromagnetic modes. Total internal reflection is a useful ray approximation, but evanescent fields, bending loss, scattering, absorption, and dispersion remain.
""",
"12-fluids-materials": """## Phase 7 review boundaries and validity limits

- Bernoulli's equation is an energy relation for specified steady-flow assumptions; a constriction does not universally cause a pressure drop without considering elevation, losses, pumps, compressibility, and boundary conditions.
- Aerodynamic lift comes from the complete pressure and shear distribution associated with circulation and momentum deflection. Bernoulli and Newton descriptions are consistent views of the same flow, not competing one-line causes.
- Viscosity relates stress to rate of deformation for a constitutive model. Newtonian behavior is not universal; many polymers, suspensions, and biological fluids are non-Newtonian.
- Stress and strain are tensor quantities in three dimensions. Scalar Hooke-law forms apply to simple uniaxial or shear cases in a linear elastic regime.
- Griffith's ideal brittle-fracture equation is geometry- and assumption-dependent. Engineering fracture assessment normally uses stress-intensity factors, energy-release rates, toughness data, and flaw geometry.
- Polycrystalline metals can be approximately isotropic only when texture and processing support that approximation; single crystals, wood, laminates, and many composites are anisotropic.
""",
}

EXACT_REPLACEMENTS = {
"science/06-matter-quantum/overview.md": {
"- **Quantisation:** Energy is not continuous but comes in discrete packets called quanta. For electromagnetic radiation, these quanta are called photons.": "- **Quantisation:** Measurements of particular observables can have discrete allowed values in bound systems. Electromagnetic radiation exchanges energy in photons, while other observables or free-particle spectra may be continuous.",
"**From Quarks to Nuclei:** The strong nuclear force, mediated by gluons, binds quarks together to form protons and neutrons (nucleons). This force overcomes the immense electrostatic repulsion between positively charged protons, allowing stable atomic nuclei to exist.": "**From Quarks to Nuclei:** Quantum chromodynamics describes gluons binding quarks inside nucleons. A residual strong interaction between nucleons, together with quantum structure and the balance of nuclear and electrostatic energies, permits some nuclei to be stable.",
"$$ \\lambda = \\frac{h}{p} = \\frac{h}{mv} $$": "$$ \\lambda = \\frac{h}{p} $$\nFor a nonrelativistic particle with constant mass, $p \\approx mv$, giving $\\lambda \\approx h/(mv)$.",
"It is impossible to simultaneously know both the exact position and exact momentum of a particle.": "For identically prepared states, the standard deviations of position and momentum outcomes obey a lower bound.",
"- **Misconception:** Empty space is truly empty.\n  **Correction:** According to quantum field theory, a vacuum is teeming with fluctuating quantum fields and virtual particles popping in and out of existence.": "- **Misconception:** Quantum-field vacuum diagrams show literal particles continuously appearing and disappearing.\n  **Correction:** The vacuum is the lowest-energy field state and has measurable correlations; virtual particles are internal terms in perturbative calculations, not directly observed transient objects.",
"- **07-chemical-bonds:**": "- **07-chemical-bonding:**",
"- **12-semiconductors:**": "- **18-semiconductors-electronics:**",
"- **08-thermodynamics:**": "- **08-energy-thermodynamics:**",
},
"science/06-matter-quantum/technology.md": {
"emitting a second photon identical in phase, frequency, and direction to the first": "increasing occupation of the same optical mode, producing radiation matched in frequency and phase relation under the device's mode conditions",
"aligns the quantum spins of hydrogen protons": "creates a small net nuclear magnetisation from hydrogen nuclei",
"flipping their spins": "rotating the net magnetisation away from equilibrium",
"emitting their own RF signal": "inducing a measurable voltage in the receive coil as transverse magnetisation precesses and relaxes",
"within a few nanometres": "within a sub-nanometre tunnelling distance",
"map the atomic topography": "map a signal that depends on tip–sample distance and local electronic density of states",
"rapidly boiling off the liquid helium coolant and destroying the magnetic field": "causing rapid loss of superconductivity and helium venting; engineered quench protection and ventilation are essential",
},
"science/06-matter-quantum/explore.md": {
"- **Schrödinger's Cat:** Imagine a cat in a sealed box with a radioactive atom, a Geiger counter, and a vial of poison gas. If the atom decays, the counter triggers the release of the gas, killing the cat. If it doesn't decay, the cat lives. According to the Copenhagen interpretation of quantum mechanics, until the box is opened and observed, the atom is in a superposition of decayed and undecayed states. Does this mean the macroscopic cat is simultaneously alive and dead? This thought experiment highlights the conceptual difficulties of applying quantum superposition to macroscopic objects and the problem of measurement.": "- **Two-path interferometer:** Imagine a single photon entering an interferometer with two paths. With both paths coherent, the output probabilities depend on their relative phase. If path information becomes recorded in the environment, interference visibility decreases. What does this show about coherence, information, and measurement without requiring a conscious observer?",
"- **Household Exploration (Spectroscopy):** If you have a diffraction grating (often sold cheaply online or found in some educational kits), look at different light sources through it: an incandescent bulb, a fluorescent tube, an LED, and a neon sign. Compare the continuous spectrum of the hot filament with the discrete emission lines of the gases.": "- **Safe spectroscopy:** Use a commercially enclosed classroom spectroscope or a reputable spectrum database to compare incandescent, fluorescent, and LED sources. Never view the Sun, lasers, welding arcs, or other intense sources through an optical device.",
"properties like position and momentum are not definite until they are measured, and the act of measurement inherently disturbs the system": "a quantum state assigns probability distributions to possible outcomes, and measurement interactions can change the state; the uncertainty relation is not explained solely by disturbance",
"Module 12 (Semiconductors)": "Module 18 (Semiconductors and Electronics)",
},
"science/07-chemical-bonding/overview.md": {
"Atoms interact to reach lower energy states, typically by achieving a stable electron configuration (often a full valence shell).": "Atoms form stable structures when the total energy of nuclei and electrons is lower for the combined arrangement under the relevant conditions. Full-valence-shell rules are useful bookkeeping heuristics, not a universal mechanism.",
"- **Ionic bonds** involve the electrostatic attraction between oppositely charged ions, formed when electrons are transferred from a metal to a nonmetal.": "- **Ionic bonding** describes structures dominated by electrostatic interactions between ions; real electron density and polarisation often give partial covalent character.",
"- **Metallic bonds** consist of a lattice of positive metal ions in a \"sea\" of delocalized valence electrons.": "- **Metallic bonding** is a many-electron solid-state interaction with delocalised electronic states; the electron-sea picture is an introductory approximation.",
"$K_c$: Equilibrium constant (dimensionless, though sometimes expressed with concentration units)": "$K$: Thermodynamic equilibrium constant, dimensionless when activities are referenced to standard states",
"- $n$: Number of moles of electrons ($\\text{mol}$)": "- $n$: Stoichiometric number of electrons transferred per reaction as written (dimensionless)",
"- **09-materials-science:**": "- **17-materials-manufacturing:**",
"- **08-thermodynamics:**": "- **08-energy-thermodynamics:**",
},
"science/07-chemical-bonding/technology.md": {
"store electrical energy in chemical bonds": "store recoverable electrochemical free energy in composition and electrode states",
"the thermodynamic instability of the toxic gases": "the Gibbs-energy driving force for the permitted reactions under exhaust conditions",
"Modern converters achieve over 90% efficiency": "Well-controlled modern converters can achieve high conversion after light-off, but performance depends on temperature, air–fuel ratio, ageing, and pollutant species",
},
"science/07-chemical-bonding/explore.md": {
"- Look at the salt (sodium chloride) and sugar (sucrose) in your kitchen. Both are white crystalline solids. If you were to heat them gently in a pan, which would melt first, and what does this tell you about the difference between ionic and covalent bonds?": "- Compare reliable reference data for sodium chloride and sucrose: melting or decomposition temperature, water solubility, and conductivity in solution. Which observations distinguish an ionic lattice from a molecular solid without heating substances at home?",
"- **Reaction Kinetics:** Take two effervescent antacid tablets. Crush one into a powder and leave the other whole. Drop them simultaneously into two identical glasses of water at the same temperature. Time how long it takes for each to stop fizzing. This demonstrates the effect of surface area on reaction rates.": "- **Reaction-rate simulation:** Use a browser-based collision or reaction-rate simulation to compare particle concentration, temperature, surface area, and catalyst pathways. Record which variable changes collision frequency and which changes the energy barrier.",
"- The principles of reaction kinetics are used to design airbags in cars, which must inflate in milliseconds during a crash. What factors might engineers manipulate to ensure the chemical reaction producing the gas is fast enough?": "- Catalytic converters must reach useful conversion quickly after a cold start. Which kinetic, heat-transfer, and surface-area variables influence light-off without changing the equilibrium constant?",
"Module 09: Materials Science": "Module 17: Materials Science and Manufacturing",
},
"science/08-energy-thermodynamics/overview.md": {
"**Temperature** is a measure of the average translational kinetic energy of the microscopic particles in a system. It determines the direction of spontaneous heat flow.": "**Temperature** is a thermodynamic state variable that establishes thermal equilibrium and the direction of spontaneous heat transfer. For an ideal monatomic gas it is proportional to mean translational kinetic energy, but that identity is not general.",
"**Entropy** is a measure of the number of specific microscopic configurations (microstates) that correspond to a macroscopic state (macrostate). It is often conceptualised as a measure of disorder or the unavailability of a system's thermal energy for conversion into mechanical work.": "**Entropy** is a state function defined macroscopically through reversible heat transfer and statistically through probability distributions over microstates. It is related to energy dispersal and multiplicity, but is not simply visual disorder.",
"All objects emit thermal radiation proportional to the fourth power of their absolute temperature.": "All bodies emit thermal radiation; the idealised Stefan–Boltzmann surface-emission model scales with the fourth power of absolute temperature, while net exchange also depends on surroundings and geometry.",
"the entropy of the system approaches a constant minimum value": "the entropy approaches a constant as temperature approaches zero; for a perfect crystal with a unique ground state, that constant is conventionally zero",
"$$ \\dot{Q}_{\\text{rad}} = \\varepsilon \\sigma A T^4 $$": "$$ \\dot{Q}_{\\text{net}} \\approx \\varepsilon \\sigma A (T^4-T_{\\text{sur}}^4) $$",
"- **09-fluid-dynamics:**": "- **12-fluids-materials:**",
"- **12-chemical-kinetics:**": "- **07-chemical-bonding:**",
},
"science/08-energy-thermodynamics/technology.md": {
"Compressing a gas increases its temperature and pressure. Adding heat at constant pressure further increases its volume and enthalpy.": "In an ideal Brayton-cycle model, near-adiabatic compression raises pressure and temperature, approximately constant-pressure heat addition raises enthalpy, and expansion through a turbine extracts work.",
"Modern combined-cycle gas turbine (CCGT) power plants, which use the hot exhaust from a gas turbine to boil water for a steam turbine, can achieve thermal efficiencies exceeding $60\\%$.": "Combined-cycle plants recover gas-turbine exhaust heat in a steam bottoming cycle, raising efficiency above either simple cycle; actual performance depends on load, ambient conditions, fuel, cooling, and plant design.",
},
"science/08-energy-thermodynamics/explore.md": {
"- **The Bicycle Pump:** Vigorously pump up a bicycle tire. Feel the base of the pump cylinder. Why does it feel warm? Which thermodynamic mechanism is responsible for this temperature increase?": "- **Compression observation:** Use a teacher-approved hand pump with no needle attached, or a gas-properties simulation, to compare slow and rapid compression. Do not block outlets or exceed equipment ratings.",
"- Consider a sealed, rigid container half-filled with liquid water and half with water vapor, sitting at room temperature. If you heat the container, what will happen to the pressure inside, and why?": "- In a simulation of a rigid closed vessel containing liquid and vapour, predict how equilibrium pressure changes with temperature. Why would heating a sealed real container be unsafe?",
"Even if your breath is $37^\\circ\\text{C}$, it is much drier than the saturated air above the soup.": "Exhaled air is humid, but moving air still disrupts the warm saturated boundary layer and increases forced convection; evaporation increases when the replacement air is below saturation at the surface temperature.",
"- **The Rubber Band Refrigerator:** Take a thick rubber band. Hold it loosely against your upper lip (which is very sensitive to temperature). Now, rapidly stretch the rubber band and hold it stretched against your lip. It should feel warm. Wait a few seconds for it to cool to room temperature while still stretched. Then, rapidly let it contract and touch it to your lip again. It should feel cool. You have just demonstrated the elastocaloric effect, a thermodynamic cycle driven by the entropy changes of aligning and misaligning polymer chains.": "- **Elastocaloric model:** Use published temperature–extension data or a classroom simulation for a rubber elastomer. Plot the qualitative temperature response during rapid extension, thermal equilibration, and release; do not snap stretched bands near the face or skin.",
"Module 09: Fluid dynamics": "Module 12: Fluids and Materials",
"Module 12: Chemical kinetics": "Module 07: Chemical Bonding",
"Module 11: Materials science": "Module 17: Materials Science and Manufacturing",
},
"science/09-motion-forces/overview.md": {
"| Moment of Inertia | $I$ | $\\text{kg}\\cdot\\text{m}^2$ | Scalar | Resistance to angular acceleration. |": "| Moment of Inertia | $I$ or $\\mathbf{I}$ | $\\text{kg}\\cdot\\text{m}^2$ | Scalar about a fixed axis; tensor generally | Relates angular momentum or torque to rotational motion for a defined geometry and axis. |",
"At relativistic speeds, mass and momentum definitions must be modified.": "At relativistic speeds, invariant mass remains the same while momentum and energy follow relativistic rather than Newtonian formulas.",
"- **10-thermodynamics:**": "- **08-energy-thermodynamics:**",
"- **11-electromagnetism:**": "- **10-electricity-magnetism:**",
"- **12-quantum-mechanics:**": "- **06-matter-quantum:**",
},
"science/09-motion-forces/technology.md": {
"where every kilogram of payload requires exponentially more propellant to launch": "where the rocket equation makes required mass ratio grow exponentially with mission delta-v, making added payload costly in propellant and structure",
"Specific impulse ($I_{sp}$) is a measure of rocket engine efficiency, representing the change in momentum per unit mass of propellant consumed.": "Specific impulse ($I_{sp}$) is thrust divided by propellant weight-flow rate, measured in seconds; equivalently, effective exhaust velocity is $g_0 I_{sp}$.",
"a bridge designed with a factor of safety of three can theoretically hold three times its maximum rated capacity": "a factor of safety compares a defined failure measure with an allowable design measure; it does not guarantee that a complete structure can safely carry that multiple of its posted load",
},
"science/09-motion-forces/explore.md": {
"Notice the trajectory of a tossed object, such as a set of keys; does it follow a straight line or a curve, and what forces are acting on it while it is in the air?": "Use a slow-motion video of a soft foam ball released over a clear area. Does its centre follow a straight line or a curve, and what forces act after release?",
"**Example: The Physics of a Car Crash**": "**Example: Stopping a low-speed cart**",
"Consider a car of mass $m = 1500 \\, \\text{kg}$ traveling at a velocity $v = 20 \\, \\text{m/s}$ (about $45 \\, \\text{mph}$) that collides with a rigid wall and comes to a complete stop in $t = 0.1 \\, \\text{s}$. We want to find the average force exerted on the car during the impact.": "Consider a laboratory cart of mass $m = 1.5 \\, \\text{kg}$ moving at $v = 2.0 \\, \\text{m/s}$ that is brought to rest by a padded bumper over $t = 0.20 \\, \\text{s}$. We want the average horizontal force on the cart.",
"1500 \\, \\text{kg} \\cdot 20 \\, \\text{m/s} = 30,000": "1.5 \\, \\text{kg} \\cdot 2.0 \\, \\text{m/s} = 3.0",
"-30,000 \\, \\text{kg}\\cdot\\text{m/s}": "-3.0 \\, \\text{kg}\\cdot\\text{m/s}",
"\\frac{-30,000 \\, \\text{kg}\\cdot\\text{m/s}}{0.1 \\, \\text{s}} = -300,000 \\, \\text{N}": "\\frac{-3.0 \\, \\text{kg}\\cdot\\text{m/s}}{0.20 \\, \\text{s}} = -15 \\, \\text{N}",
"This force is equivalent to the weight of approximately 30 small cars, illustrating why high-speed collisions are so destructive and why crumple zones (which increase the collision time $t$, thereby decreasing $F_{\\text{avg}}$) are critical for safety.": "The result illustrates that increasing stopping time reduces the magnitude of average force for the same momentum change. Real forces vary during contact, so a force sensor would reveal a time-dependent profile.",
"Now, cut the broom exactly at that balance point (conceptually, or use a prop you don't mind breaking). If you weigh the two pieces, will they weigh the same?": "Without cutting anything, place removable tape markers at the balance point and at estimated centres of mass for the handle and bristle regions. Why can unequal masses balance when their lever arms differ?",
"connections: [03-mathematical-models, 11-waves-signals, 12-fluids-materials, 16-earth-planetary]": "connections: [11-waves-signals, 12-fluids-materials, 16-earth-planetary]",
},
"science/10-electricity-magnetism/overview.md": {
"- $\\mu_0$: Vacuum permeability, $4\\pi \\times 10^{-7}$ T$\\cdot$m/A.": "- $\\mu_0$: Vacuum permeability, experimentally determined in the revised SI (approximately $1.25663706\\times10^{-6}\\,\\text{H/m}$).",
"**Ohm's Law:** Relates voltage $V$, current $I$, and resistance $R$ in a conductor:": "**Ohm's Law for an ohmic element:** Relates voltage $V$, current $I$, and resistance $R$ when the element is approximately linear under specified conditions:",
"- **11-thermodynamics:**": "- **08-energy-thermodynamics:**",
"- **12-optics:**": "- **11-waves-signals:**",
},
"science/10-electricity-magnetism/technology.md": {
"A changing magnetic flux induces an electromotive force (EMF)": "A changing magnetic flux linkage around a circuit induces an electromotive force (EMF)",
"- **13-energy-systems:**": "- **20-sensors-control-infrastructure:**",
"- **14-electronics:**": "- **18-semiconductors-electronics:**",
"- **15-control-systems:**": "- **20-sensors-control-infrastructure:**",
},
"science/10-electricity-magnetism/explore.md": {
"Current takes the path of least resistance. The bird's body has a much higher resistance than the short segment of wire between its feet.": "Current divides among parallel paths according to their impedances. Because the bird's feet are nearly at the same potential, only a tiny voltage appears across its body under ordinary conditions.",
"- **Build an Electromagnet:** Wrap insulated copper wire tightly around an iron nail (at least 20-30 turns). Connect the bare ends of the wire to the terminals of a standard AA or D battery. Use the nail to pick up steel paperclips. Disconnect the battery and observe what happens. *(Caution: The wire may get warm; do not leave it connected for long periods.)*": "- **Electromagnet simulation:** Use a reputable virtual Faraday/electromagnet simulation to vary coil turns, current, and core material. Do not connect loose wire directly across a battery or household supply; a short circuit can overheat cells and conductors.",
"Look at the power cords of different appliances": "With appliances unplugged and without opening or handling damaged cords, compare the external thickness markings of different power cords",
},
"science/11-waves-signals/overview.md": {
"**Diffraction** is the bending and spreading of waves": "**Diffraction** is the spreading and interference of waves",
"**Fourier Analysis** is the mathematical principle that any complex periodic wave can be decomposed": "**Fourier Analysis** represents suitably behaved periodic signals with Fourier series and non-periodic signals with Fourier transforms, decomposing them",
"because light travels at different speeds in different media. When a wavefront enters a denser medium": "because phase velocity and wavelength change across media while boundary conditions preserve frequency. When a wavefront enters a medium with a different refractive index",
"- **12-electromagnetism:**": "- **10-electricity-magnetism:**",
"- **14-quantum-mechanics:**": "- **06-matter-quantum:**",
"- **16-communication-systems:**": "- **20-sensors-control-infrastructure:**",
},
"science/11-waves-signals/technology.md": {
"is completely reflected back": "is reflected in the ideal ray model while an evanescent field and real losses remain",
"zig-zagging down the fibre with minimal loss": "propagating as guided electromagnetic modes determined by the core–cladding index profile",
"Efficiency is measured by the **Bit Error Rate (BER)**": "Reliability is measured in part by the **Bit Error Rate (BER)**",
},
"science/11-waves-signals/explore.md": {
"- **The Doppler Effect:** Stand near a road and listen to the pitch of a car engine or siren as it approaches and then passes you. How does the pitch change? Does the volume change in the same way?": "- **The Doppler effect:** Use a reputable recorded demonstration or simulation of a moving source. Compare observed frequency and amplitude without standing near traffic or emergency vehicles.",
"- **The Silent Bell:** Imagine a bell ringing inside a sealed glass jar. If you use a vacuum pump to slowly remove all the air from the jar, what will happen to the sound of the bell? What will happen to your ability to see the bell? What does this tell you about the nature of sound waves versus light waves?": "- **Sound and vacuum simulation:** In a virtual model, reduce gas density around a vibrating source while keeping the optical path unchanged. Which coupling carries sound, and why can light still propagate?",
"- **Resonance with Wine Glasses:** Wet your finger and rub it gently but firmly around the rim of a thin crystal wine glass. You should hear a clear, sustained tone. This is the resonant frequency of the glass. Add some water to the glass and repeat. Does the pitch go up or down? Why? (The water adds mass to the oscillating system without significantly changing its stiffness).": "- **Resonance simulation:** Use a virtual driven oscillator or recorded spectrum to vary mass, stiffness, and damping. Avoid fragile glass and high sound levels.",
"Play both simultaneously. You will hear": "At a low, comfortable volume, compare or plot both signals. Their sum shows",
"- **Coupled Oscillators:** Tie a string horizontally between two chairs. Hang two identical simple pendulums from this horizontal string. Start one pendulum swinging while the other is at rest. Observe how the energy transfers back and forth between the two pendulums. How would you modify the differential equations of simple harmonic motion to account for this coupling?": "- **Coupled-oscillator model:** Use a simulation or two coupled equations to transfer energy between oscillators. Vary coupling strength and damping, then plot both amplitudes versus time.",
},
"science/12-fluids-materials/overview.md": {
"**Viscosity:** A measure of a fluid's resistance to gradual deformation by shear stress or tensile stress; essentially, fluid friction.": "**Viscosity:** A constitutive measure relating stress to deformation rate; for a Newtonian fluid, shear stress is proportional to the velocity gradient.",
"This causal chain—constriction $\\rightarrow$ acceleration $\\rightarrow$ pressure drop—explains phenomena ranging from the Venturi effect to aerodynamic lift [1].": "For a specified streamline with negligible losses and no added shaft work, continuity and the energy equation relate area, velocity, pressure, and elevation. A constriction often raises speed, but the pressure response depends on the complete boundary conditions. Aerodynamic lift requires the full pressure and shear distribution and momentum deflection, not Bernoulli's equation alone [1].",
"This is generally true for metals but false for wood and composite materials.": "This may approximate some randomly oriented polycrystalline metals, but processing texture, single crystals, wood, and composite laminates can be strongly anisotropic.",
},
"science/12-fluids-materials/technology.md": {
"utilising Bernoulli's principle and viscous losses": "through geometry, control elements, and deliberately introduced irreversible losses",
"Bernoulli's principle and Newton's third law dictate that a fluid moving over a curved surface creates a pressure differential.": "Conservation of momentum, circulation, viscosity, and boundary conditions establish a pressure and shear distribution that deflects airflow and produces lift.",
"e.g., a factor of safety of 1.5 means the structure can hold 150% of its rated load before yielding": "the factor compares a selected failure criterion with an allowable design value; it is not a universal multiplier for whole-system rated load",
"- **16-manufacturing-processes:**": "- **17-materials-manufacturing:**",
"- **17-structural-engineering:**": "- **17-materials-manufacturing:**",
"- **18-aerospace-systems:**": "- **20-sensors-control-infrastructure:**",
},
"science/12-fluids-materials/explore.md": {
"- **The Paperclip Bend:** Take a metal paperclip and bend it slightly, then let go. Now bend it severely until it stays bent. Finally, bend it back and forth rapidly in the same spot until it breaks. What three distinct material behaviours have you just observed?": "- **Stress–strain evidence:** Compare manufacturer curves or a classroom simulation for elastic, yielding, and fracture behaviour. Do not fatigue or break metal objects by hand; fractured ends can be sharp.",
"- If you scratch the surface of a glass rod and then try to bend it, will it break easier if the scratch is on the inside of the bend (under compression) or the outside of the bend (under tension)?": "- In a fracture simulation, place an identical surface flaw on the tensile side and compressive side of a bent specimen. Which orientation produces the larger opening stress at the crack tip?",
"- **The Venturi Tube:** Take a plastic bottle and carefully cut a small hole in the side near the bottom. Fill it with water and watch the stream. Now, attach a hose to a tap, pinch the end of the hose to make the opening smaller, and observe the speed of the water. You are manipulating the continuity equation ($A_1 v_1 = A_2 v_2$).": "- **Continuity and losses simulation:** Use a virtual pipe model to vary cross-section, elevation, flow rate, viscosity, and pump head. Compare ideal continuity/Bernoulli predictions with a model that includes head loss; do not cut pressurised containers or restrict hoses.",
"- **Composite Construction:** Try to break a piece of dry spaghetti. It snaps easily (brittle fracture). Now, take several pieces of spaghetti and wrap them tightly in sticky tape. Try to break the bundle. The tape acts as a ductile matrix, preventing the brittle fracture of individual strands from propagating through the whole structure.": "- **Composite load-sharing model:** Use a diagram or simulation of fibres embedded in a matrix. Remove one fibre and observe how interfacial shear transfers load to neighbours; distinguish this from claiming that taped food is an engineering composite.",
},
}

BANNED = (
    "Wikipedia. (n.d.)",
    "Khan Academy. (n.d.)",
    "virtual particles popping in and out",
    "path of least resistance",
    "Connect the bare ends of the wire",
    "vial of poison gas",
    "upper lip",
    "cut the broom",
    "bend it back and forth rapidly in the same spot until it breaks",
    "thin crystal wine glass",
    "carefully cut a small hole",
)


def replace_sources(text: str, module: str) -> str:
    pattern = re.compile(r"(?ms)^#{1,2} (?:12|13)\. Sources\s*\n.*\Z")
    if not pattern.search(text):
        raise ValueError("source section not found")
    return pattern.sub(SOURCES[module].rstrip() + "\n", text)


def insert_boundaries(text: str, module: str) -> str:
    if "## Phase 7 review boundaries and validity limits" in text:
        return text
    marker = re.search(r"(?m)^#{1,2} (?:12|13)\. Sources\s*$", text)
    if not marker:
        raise ValueError("source marker not found")
    return text[: marker.start()] + BOUNDARIES[module].rstrip() + "\n\n" + text[marker.start():]


def transform(path: Path, module: str) -> tuple[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    notes: list[str] = []
    original = text
    text = text.replace("status: draft", "status: reviewed", 1)
    text = re.sub(r"last_reviewed: \d{4}-\d{2}-\d{2}", f"last_reviewed: {DATE}", text, count=1)
    for old, new in EXACT_REPLACEMENTS.get(path.relative_to(ROOT).as_posix(), {}).items():
        if old in text:
            text = text.replace(old, new)
            notes.append(f"replaced: {old[:70]}")
    text = insert_boundaries(text, module)
    text = replace_sources(text, module)
    if original != text:
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return text, notes


def update_index() -> None:
    path = ROOT / "INDEX.md"
    text = path.read_text(encoding="utf-8")
    for number in range(6, 13):
        text = re.sub(rf"(?m)^(\| {number:02d} \|.*\|) Draft \|$", r"\1 Reviewed |", text)
    path.write_text(text, encoding="utf-8")


def validate() -> list[str]:
    errors: list[str] = []
    ledger = (ROOT / "sources/source-ledger.md").read_text(encoding="utf-8")
    for module, directory in MODULES.items():
        for role in ROLES:
            path = ROOT / directory / role
            if not path.exists():
                errors.append(f"missing {path.relative_to(ROOT)}")
                continue
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(ROOT)
            if "status: reviewed" not in text:
                errors.append(f"{rel}: not reviewed")
            if f"last_reviewed: {DATE}" not in text:
                errors.append(f"{rel}: review date missing")
            if "Phase 7 review boundaries and validity limits" not in text:
                errors.append(f"{rel}: validity-limit section missing")
            urls = re.findall(r"https?://[^\s)]+", SOURCES[module])
            for url in urls:
                if url not in text:
                    errors.append(f"{rel}: missing reviewed source {url}")
                if url not in ledger:
                    errors.append(f"{rel}: source absent from central ledger {url}")
            for phrase in BANNED:
                if phrase.lower() in text.lower():
                    errors.append(f"{rel}: banned legacy phrase remains: {phrase}")
    index = (ROOT / "INDEX.md").read_text(encoding="utf-8")
    for number in range(6, 13):
        row = next((line for line in index.splitlines() if line.startswith(f"| {number:02d} |")), "")
        if not row.endswith("| Reviewed |"):
            errors.append(f"INDEX: Module {number:02d} not Reviewed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        for module, directory in MODULES.items():
            for role in ROLES:
                transform(ROOT / directory / role, module)
        update_index()
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Phase 7 physical-science review validation passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
