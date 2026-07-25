#!/usr/bin/env python3
"""Apply the focused Phase 9 review to Technology Modules 17–20."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW_DATE = "2026-07-26"
FILENAMES = ("overview.md", "technology.md", "explore.md")
MODULES = {
    "17-materials-manufacturing": {
        "prerequisites": ["06-matter-quantum", "07-chemical-bonding", "12-fluids-materials"],
        "connections": ["18-semiconductors-electronics"],
    },
    "18-semiconductors-electronics": {
        "prerequisites": ["06-matter-quantum", "10-electricity-magnetism", "17-materials-manufacturing"],
        "connections": ["19-software-ai", "20-sensors-control-infrastructure"],
    },
    "19-software-ai": {
        "prerequisites": ["04-probability-statistics", "05-computation-algorithms", "18-semiconductors-electronics"],
        "connections": ["20-sensors-control-infrastructure"],
    },
    "20-sensors-control-infrastructure": {
        "prerequisites": ["10-electricity-magnetism", "11-waves-signals", "18-semiconductors-electronics", "19-software-ai"],
        "connections": [],
    },
}

ALIASES = {
    "18-solid-mechanics": "12-fluids-materials",
    "19-thermodynamics": "08-energy-thermodynamics",
    "19-computing-architecture": "19-software-ai",
    "Module 19 (Computing Architecture)": "Module 19 (Software, Information, Networks, and AI Foundations)",
}

EXACT = {
    "technology/18-semiconductors-electronics/overview.md": {
        "A smartphone processing billions of operations per second without melting is a direct consequence of semiconductor efficiency.":
            "A smartphone performing many operations while remaining within thermal limits reflects device efficiency, architecture, workload scheduling, packaging, cooling, and power management rather than semiconductor efficiency alone.",
        "The exponential increase in computing power over the last half-century, commonly known as Moore's law, is an observable trend driven by the continuous miniaturisation of semiconductor devices.":
            "Moore's original observation concerned economical component density. Later performance gains also depended on device design, architecture, memory, software, packaging, and power limits; it is an historical trend, not a physical law or guaranteed forecast.",
    },
    "technology/18-semiconductors-electronics/technology.md": {
        "If heat cannot be removed fast enough, the chip will melt.":
            "If heat is not removed adequately, temperature-dependent delay, leakage, throttling, accelerated ageing, packaging damage, or protective shutdown usually occurs well before bulk silicon melting.",
    },
    "technology/20-sensors-control-infrastructure/overview.md": {
        "How do physical systems perceive their environment, make decisions, and act upon those decisions to achieve desired outcomes?":
            "How do engineered systems measure physical variables, estimate state, compute constrained actions, and affect their environment to meet stated objectives?",
    },
}

SOURCES = {
    "17-materials-manufacturing": """1. Callister, W. D., and Rethwisch, D. G. *Materials Science and Engineering: An Introduction*. https://www.wiley.com/en-us/Materials+Science+and+Engineering%3A+An+Introduction%2C+10th+Edition-p-9781119405498
2. Gong, G., et al. *Research Status of Laser Additive Manufacturing for Metal: A Review*. https://www.sciencedirect.com/science/article/pii/S2238785421008759
3. National Institute of Standards and Technology. *Additive Manufacturing of Metals*. https://www.nist.gov/additive-manufacturing/research-areas/materials/metals
4. National Institute for Occupational Safety and Health. *3D Printing with Metal Powders: Health and Safety Questions to Ask*. https://www.cdc.gov/niosh/docs/2020-114/default.html
5. Occupational Safety and Health Administration. *General Requirements for All Machines*. https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.212
6. Pelin, G., et al. *The Use of Additive Manufacturing Techniques in the Development of Polymer-Based Composites*. https://www.mdpi.com/2073-4360/16/8/1055""",
    "18-semiconductors-electronics": """1. Massachusetts Institute of Technology OpenCourseWare. *Integrated Microelectronic Devices*. https://ocw.mit.edu/courses/6-720j-integrated-microelectronic-devices-spring-2007/
2. National Institute of Standards and Technology. *Semiconductors*. https://www.nist.gov/semiconductors
3. Intel. *Moore's Law*. https://www.intel.com/content/www/us/en/history/virtual-vault/articles/moores-law.html
4. National Institute of Standards and Technology. *CHIPS for America Metrology Program*. https://www.nist.gov/chips/research-development-programs/metrology-program
5. Orji, N. G., et al. *Metrology for the Next Generation of Semiconductor Devices*. https://www.nist.gov/publications/metrology-next-generation-semiconductor-devices
6. Postek, M. T., and Bennett, M. H. *Critical Dimension and Overlay Metrology*. https://www.nist.gov/publications/critical-dimension-and-overlay-metrology""",
    "19-software-ai": """1. Shannon, C. E. *A Mathematical Theory of Communication*. https://doi.org/10.1002/j.1538-7305.1948.tb01338.x
2. Kurose, J. F., and Ross, K. W. *Computer Networking: A Top-Down Approach*. https://www.pearson.com/en-us/subject-catalog/p/computer-networking-a-top-down-approach/P200000013385
3. Goodfellow, I., Bengio, Y., and Courville, A. *Deep Learning*. http://www.deeplearningbook.org
4. Hellerstein, J. M., Stonebraker, M., and Hamilton, J. *Architecture of a Database System*. https://doi.org/10.1561/1900000002
5. National Institute of Standards and Technology. *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
6. National Institute of Standards and Technology. *AI RMF: Generative Artificial Intelligence Profile*. https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
7. Internet Engineering Task Force. *RFC 9293: Transmission Control Protocol*. https://www.rfc-editor.org/info/rfc9293/""",
    "20-sensors-control-infrastructure": """1. WPILib Contributors. *Introduction to State-Space Control*. https://docs.wpilib.org/en/stable/docs/software/advanced-controls/state-space/state-space-intro.html
2. Peng, F. Z., et al. *Envisioning the Future Renewable and Resilient Energy Grids*. https://ieeexplore.ieee.org/abstract/document/10360247/
3. National Institute of Standards and Technology. *Framework for Cyber-Physical Systems: Volume 1, Overview*. https://www.nist.gov/publications/framework-cyber-physical-systems-volume-1-overview
4. National Institute of Standards and Technology. *SP 800-82 Rev. 2: Guide to Industrial Control Systems Security*. https://csrc.nist.gov/pubs/sp/800/82/r2/final
5. United States Department of Energy. *Grid Modernization Initiative*. https://www.energy.gov/gmi/grid-modernization-initiative
6. Filip, F. G., and Leiviskä, K. *Infrastructure and Complex Systems Automation*. https://link.springer.com/chapter/10.1007/978-3-030-96729-1_27""",
}

BOUNDARIES = {
    "17-materials-manufacturing": """## Phase 9 review boundaries and validity limits

- Structure–property–processing relations are conditional on composition, defects, geometry, environment, loading history, manufacturing route, and measurement method.
- Phase diagrams describe equilibrium or specified constrained equilibria; kinetic diagrams and process models are needed for finite-rate transformations.
- Hall–Petch, Fickian diffusion, linear elasticity, and fracture parameters are model- and regime-dependent rather than universal laws across every scale.
- Manufacturing claims require process qualification, traceable metrology, uncertainty reporting, defect acceptance criteria, and lifecycle boundaries.
""",
    "18-semiconductors-electronics": """## Phase 9 review boundaries and validity limits

- Band, carrier, junction, and compact-device equations assume specified equilibrium, statistics, geometry, temperature, and bias regimes.
- Threshold voltage is a model parameter, not a hard microscopic on/off boundary; leakage, short-channel effects, variability, and parasitics matter.
- Technology-node names are industrial labels rather than literal dimensions of every device feature.
- Device performance, yield, reliability, and scaling claims require metrology, architecture, packaging, workload, and thermal context.
""",
    "19-software-ai": """## Phase 9 review boundaries and validity limits

- Information-theory limits are asymptotic results for stated source and channel models; finite systems trade error, latency, energy, complexity, and cost.
- Protocol guarantees apply only under their specifications and assumptions; end-to-end service also depends on applications, networks, implementations, and failures.
- Machine-learning evaluation must address distribution shift, uncertainty, calibration, subgroup performance, robustness, privacy, security, misuse, monitoring, and human oversight.
- Model outputs are evidence requiring verification, not authoritative facts or proof of consciousness, intention, or understanding.
""",
    "20-sensors-control-infrastructure": """## Phase 9 review boundaries and validity limits

- Closed-loop performance depends on sensing, estimation, delay, sampling, quantisation, communication, actuator saturation, disturbances, uncertainty, and model mismatch.
- Stability and safety are properties of a specified operating region and architecture; a controller that works in one regime may fail in another.
- Grid operation couples physics, protection, markets, communications, cybersecurity, regulation, operators, and restoration procedures.
- Cyber-physical and infrastructure designs require defence in depth, fail-safe or fail-operational analysis, human authority, testing, maintenance, and lifecycle governance.
""",
}

SECTION_REPLACEMENTS = {
    ("technology/17-materials-manufacturing/overview.md", 3): """## 3. Essential concepts

**Structure, processing, properties, and performance:** Materials engineering links composition and structure across scales to processing history, measured properties, and performance in a specified environment. None of these links is one-to-one.

**Crystalline, amorphous, and semicrystalline structure:** Crystals exhibit long-range periodic order; amorphous materials lack it; many polymers and multiphase solids contain both ordered and disordered regions. Unit cells, texture, interfaces, and defects are different levels of description.

**Defects and interfaces:** Vacancies, solutes, dislocations, grain boundaries, phase boundaries, pores, inclusions, and cracks influence transport, deformation, corrosion, and failure. Their effects depend on density, arrangement, scale, and loading.

**Phase and transformation diagrams:** Equilibrium phase diagrams indicate stable phases under stated variables and constraints. Time–temperature–transformation, continuous-cooling, solidification, and kinetic models are needed when rates and metastability matter.

**Material classes:** Metals, ceramics, polymers, semiconductors, glasses, and composites contain wide internal variation. Bonding offers useful tendencies, but conductivity, ductility, stiffness, toughness, and temperature resistance cannot be assigned safely from class labels alone.
""",
    ("technology/17-materials-manufacturing/overview.md", 4): """## 4. Mechanisms and causal chains

Metal strengthening often works by changing dislocation nucleation or motion, but deformation can also involve twinning, phase transformation, grain-boundary processes, diffusion, damage, or cracking.

- **Solid-solution strengthening:** Solutes interact with defects and change local elastic and chemical fields.
- **Work hardening:** Plastic strain can raise dislocation density and strength while changing ductility, residual stress, and anisotropy; recovery and recrystallisation may reverse part of the effect.
- **Grain-size effects:** In a stated grain-size regime, boundaries can impede slip and an empirical Hall–Petch relation may fit data. At very small scales or under other mechanisms, the relation can deviate or reverse.
- **Precipitation strengthening:** Coherent, semicoherent, or incoherent particles interact with dislocations through cutting, looping, coherency, modulus, and order effects; over-ageing can reduce strength.

In steels and other alloys, thermal history controls diffusion, nucleation, growth, transformation strain, retained phases, residual stress, and tempering reactions. A microstructure label alone does not determine component performance without composition, geometry, defects, and loading context.
""",
    ("technology/17-materials-manufacturing/overview.md", 5): """## 5. Important quantities

- **Yield or proof strength:** A convention-dependent stress associated with the onset of specified permanent strain.
- **Ultimate tensile strength:** The maximum engineering stress in a tensile test; it is not generally the fracture stress or a universal design limit.
- **Elastic constants:** Parameters such as Young's modulus, shear modulus, and Poisson ratio within a stated linear range and orientation.
- **Ductility:** Plastic-deformation capacity measured by a specified test and geometry.
- **Plane-strain mode-I fracture toughness ($K_{Ic}$):** A valid material property only when specimen, thickness, crack, loading, and linear-elastic conditions satisfy the applicable standard; otherwise report a conditional toughness value.
- **Hardness:** A test-specific resistance to indentation or scratching; conversions to strength are empirical and material-dependent.
- **Fatigue and creep metrics:** Depend on stress history, temperature, environment, surface state, geometry, and statistical scatter.
""",
    ("technology/17-materials-manufacturing/overview.md", 6): """## 6. Mathematical models and equations

**Bragg condition:**
$$n\lambda = 2d\sin\theta$$
This relates wavelength, lattice-plane spacing, and scattering angle for elastic diffraction under the stated geometry; peak position and intensity also depend on structure, texture, instrument response, and sample condition.

**Empirical Hall–Petch relation:**
$$\sigma_y = \sigma_0 + k_y d^{-1/2}$$
The coefficients and useful grain-size range must be fitted for a specified material and processing state. Extrapolation to nanoscale grains is not generally valid.

**Lever rule:** For an equilibrium binary two-phase region with tie-line endpoint compositions $C_\alpha$ and $C_\beta$,
$$W_\alpha=\frac{C_\beta-C_0}{C_\beta-C_\alpha},\qquad W_\beta=\frac{C_0-C_\alpha}{C_\beta-C_\alpha}.$$
The compositions must use one consistent basis, and the result gives equilibrium phase fractions rather than morphology.

**Diffusion:**
$$J=-D\nabla C,\qquad \frac{\partial C}{\partial t}=\nabla\cdot(D\nabla C).$$
The familiar $D\nabla^2C$ form additionally assumes spatially uniform scalar diffusivity; chemical-potential gradients and multicomponent coupling may require more general models.
""",
    ("technology/17-materials-manufacturing/overview.md", 8): """## 8. Assumptions and approximations

- **Equilibrium and local equilibrium:** Diagrams do not require literally infinite time, but they assume equilibrium is reached at the scale being modelled. Real processes can retain metastable phases and gradients.
- **Continuum and representative volume:** Bulk constitutive models average microstructure and fail when component or defect scales are not well separated.
- **Isotropy and homogeneity:** Texture, layering, porosity, residual stress, joints, and additive build direction can make properties anisotropic and spatially variable.
- **Linear elasticity and small-scale yielding:** Fracture and stress-intensity methods require stated geometry and deformation limits.
- **Constant properties:** Diffusivity, heat capacity, flow stress, emissivity, and conductivity often vary with temperature, phase, composition, rate, and history.
""",
    ("technology/17-materials-manufacturing/overview.md", 10): """## 10. Common misconceptions

- **“Stronger is always better.”** Design balances stiffness, toughness, fatigue, corrosion, density, inspectability, repair, joining, cost, and failure consequence.
- **“A perfect pure crystal is soft.”** Annealed engineering metals can be soft because mobile defects are present. An ideal defect-free crystal would approach a much higher theoretical shear strength, although real surfaces nucleate defects and failure.
- **“Phase diagrams predict every cooling path.”** Equilibrium diagrams identify possible equilibria; transformation kinetics, nucleation, segregation, gradients, and processing history determine what forms in practice.
- **“Additive parts are automatically near-net-shape and waste-free.”** Supports, failed builds, powder qualification, machining allowance, heat treatment, inspection, and recycling boundaries can dominate material and energy accounting.
""",
    ("technology/17-materials-manufacturing/overview.md", 11): """## 11. Connections to other modules

- **06-matter-quantum:** Electronic structure and scattering help explain bonding, spectroscopy, conductivity, and diffraction.
- **07-chemical-bonding:** Bonding and chemical thermodynamics contribute to phase stability, corrosion, polymers, and interfaces.
- **08-energy-thermodynamics:** Free energy, heat transfer, entropy production, and kinetics constrain processing and phase transformation.
- **12-fluids-materials:** Stress, strain, fracture, rheology, and flow connect material properties to component and process mechanics.
- **18-semiconductors-electronics:** Semiconductor fabrication depends on crystal growth, deposition, patterning, interfaces, contamination control, and nanometrology.
- **20-sensors-control-infrastructure:** Process sensing, feedback, automation, maintenance, and qualification turn individual operations into manufacturing systems.
""",
    ("technology/17-materials-manufacturing/technology.md", 6): """## 6. System architecture

Manufacturing architectures combine material preparation, transformation, handling, metrology, process control, inspection, and disposition.

- **Casting and moulding:** Shape material through flow and solidification or curing; performance depends on filling, heat transfer, shrinkage, reactions, tooling, and defects.
- **Forming:** Uses controlled plastic flow in rolling, forging, extrusion, or drawing. Grain flow can be beneficial, neutral, or harmful depending on geometry and loading; forged parts are not automatically superior to cast or machined ones.
- **Subtractive processing:** Removes material with defined tools or energy beams; precision depends on machine dynamics, tool wear, thermal effects, fixturing, and measurement.
- **Additive manufacturing:** Builds material selectively. Geometry freedom is constrained by process physics, supports, residual stress, surface finish, inspection access, and qualification.
- **Joining and assembly:** Create interfaces whose metallurgy, geometry, residual stress, contamination, and inspection can govern system reliability.

A digital thread can connect requirements, material lots, process parameters, machine state, inspection, nonconformance, and lifecycle records, but data integrity and configuration control must be demonstrated.
""",
    ("technology/17-materials-manufacturing/technology.md", 8): """## 8. Performance and efficiency

Performance is multi-objective: conformance, yield, capability, throughput, availability, energy, water, material use, labour, cost, and defect escape must be reported with a defined system boundary. Additive manufacturing can reduce buy-to-fly ratio for some geometries, but powder production, supports, failed builds, post-processing, inspection, and limited powder reuse can offset that advantage. Process capability and qualification require representative builds, calibrated measurements, uncertainty, acceptance criteria, and change control rather than one density or surface-finish number.
""",
    ("technology/17-materials-manufacturing/technology.md", 10): """## 10. Safety principles

Manufacturing hazards are controlled through elimination or substitution where possible, engineered enclosure and machine guarding, interlocks, local exhaust, process monitoring, administrative controls, training, and appropriate protective equipment. Learners should not operate furnaces, presses, cutting machinery, lasers, reactive powders, chemical baths, or energized industrial systems.

Metal-powder additive manufacturing can involve inhalation, dermal, fire, explosion, laser, and inert-gas hazards. Safe practice requires professional risk assessment, compatible equipment, containment, ventilation, grounding, housekeeping, emergency planning, and applicable occupational rules. Lockout and verification of hazardous-energy isolation are professional procedures, not household experiments.
""",
    ("technology/17-materials-manufacturing/technology.md", 11): """## 11. Environmental and lifecycle considerations

Lifecycle assessment must state geography, electricity mix, recycled content, allocation, yield, transport, use phase, maintenance, and end-of-life assumptions. Mass reduction can lower use-phase energy in some applications but may increase manufacturing burden or reduce repairability. Circular strategies include longer life, modular repair, remanufacture, alloy and polymer separation, contamination control, and design for disassembly; recycling is constrained by collection, sorting, degradation, and economics.
""",
    ("technology/17-materials-manufacturing/explore.md", 1): """## 1. Observation prompts

- Compare published micrographs of annealed, cold-worked, cast, forged, and additively manufactured samples. Record scale bars, preparation method, and which features are observations versus interpretations.
- Inspect safe, intact household objects without bending, breaking, heating, cutting, or scratching them. Compare visible surface finish, joints, texture direction, mould lines, coatings, and likely manufacturing routes.
- Compare recorded tap sounds from metal, ceramic, polymer, and composite specimens. Explain why geometry, damping, boundary conditions, and excitation matter in addition to elastic properties.
""",
    ("technology/17-materials-manufacturing/explore.md", 2): """## 2. Prediction questions

- Using a published steel transformation diagram, predict how a specified cooling path changes phase fractions and hardness. Treat this as data interpretation; do not heat or quench metal.
- Compare two gears only when material, heat treatment, surface finish, residual stress, geometry, defects, and loading are specified. Which measurements would be needed before predicting fatigue life?
- Increasing cooling rate can change nucleation, growth, segregation, phase selection, and thermal gradients. Under what stated conditions would finer grains be expected, and when could that trend fail?
""",
    ("technology/17-materials-manufacturing/explore.md", 3): """## 3. Worked reasoning examples

**Scenario:** Select an age-hardenable aluminium alloy for a non-safety-critical lightweight bracket, compared with commercially pure aluminium.

1. Define loads, temperature, corrosion environment, joining method, inspection, and acceptable deformation before selecting a material.
2. Alloying and solution treatment can create a supersaturated solid solution after quenching.
3. Controlled ageing forms a sequence of nanoscale solute clusters and precipitates; the exact phases depend on alloy chemistry and treatment, so a single generic `CuAl2` picture is inadequate.
4. Small coherent or semicoherent precipitates impede dislocation motion. Continued ageing can coarsen them and reduce strengthening.
5. The strengthened alloy may improve proof strength but can change toughness, corrosion, fatigue, formability, and residual stress. A bracket choice therefore requires test data and design allowables, not strength alone.
""",
    ("technology/17-materials-manufacturing/explore.md", 5): """## 5. Household and browser-based explorations

- **Chocolate crystallisation as analogy:** Use published cooling curves and food-science references to study polymorphism and tempering. Do not treat cocoa-butter phases as a direct model of steel transformations.
- **Phase-diagram interpretation:** Use a reputable interactive or textbook iron–carbon diagram. State whether compositions are mass fraction, identify phase boundaries, and distinguish equilibrium constituents from finite-rate products.
- **Manufacturing-data exploration:** Compare public NIST additive-manufacturing datasets or videos. Track process input, measured melt-pool or geometry output, calibration, uncertainty, and which defect claims require destructive validation.
""",
    ("technology/17-materials-manufacturing/explore.md", 6): """## 6. Model-building prompts

- Build paper or digital FCC and BCC unit-cell models. Separate lattice geometry from atomic radius assumptions, and explain why atomic packing factor alone does not determine material density.
- Fit the Hall–Petch relation to a supplied dataset with uncertainty bars. Estimate $\sigma_0$ and $k_y$, inspect residuals, and mark the fitted grain-size range. Do not extrapolate the empirical relation toward zero grain size.
- Create a process–structure–property causal diagram that includes measurement, defects, uncertainty, and competing mechanisms rather than a single linear chain.
""",
    ("technology/18-semiconductors-electronics/overview.md", 3): """## 3. Essential concepts

**Bands and Fermi level:** Periodic solids have allowed electronic states whose occupancy is described using band structure and the Fermi level. “Valence” and “conduction” bands are useful labels for many semiconductors, but metals, degenerate semiconductors, surfaces, disorder, and low-dimensional devices need more careful descriptions.

**Semiconductor behaviour:** Conductivity depends on band structure, carrier statistics, temperature, defects, dopants, contacts, fields, illumination, and scattering. A fixed band-gap threshold does not universally separate conductors, semiconductors, and insulators.

**Electrons and holes:** A hole is a quasiparticle description of unoccupied valence-band states and their collective response. Carrier charge, effective mass, mobility, and lifetime are model- and material-dependent.

**Doping and activation:** Donors and acceptors introduce electronic states and shift carrier populations. Dopant concentration is not identical to free-carrier concentration because activation, compensation, degeneracy, defects, and temperature matter.

**Junctions and interfaces:** A p–n junction develops space charge and a built-in electrostatic potential. The depletion approximation neglects mobile charge in a region for tractability; the physical carrier density is not literally zero.
""",
    ("technology/18-semiconductors-electronics/overview.md", 4): """## 4. Mechanisms and causal chains

**Diodes:** Applied bias changes electrostatic barriers and carrier injection. Forward current, reverse leakage, recombination, series resistance, capacitance, and breakdown depend on device structure and operating regime; a diode is not an ideal one-way valve.

**BJTs:** Emitter injection, transport through a thin base, recombination, and collector fields produce current gain. “A small base current controls a large current” is a circuit-level approximation, not the microscopic mechanism.

**MOSFETs:** Gate voltage changes surface potential and carrier density near an insulated interface. Current depends continuously on gate and drain bias, geometry, capacitance, mobility, contacts, leakage, and short-channel effects. Threshold is not a hard on/off boundary.

**Logic and memory:** Circuits assign voltage ranges to logical states with noise margins and timing constraints. Information is encoded in physical states but is not identical to charge flow or energy.
""",
    ("technology/18-semiconductors-electronics/overview.md", 5): """## 5. Important quantities

| Quantity | Symbol | Unit | Boundary |
| :--- | :---: | :--- | :--- |
| Band-gap energy | $E_g$ | J or eV | Depends on material, temperature, strain, composition, and structure. |
| Fermi level | $E_F$ | J or eV | Chemical potential for electrons under equilibrium conditions. |
| Carrier concentration | $n,p$ | $m^{-3}$ | Free-carrier density, not automatically equal to dopant density. |
| Mobility | $\mu_n,\mu_p$ | $m^2/(V\,s)$ | Low-field transport parameter affected by scattering and field. |
| Threshold voltage | $V_{th}$ | V | Extraction- and model-dependent transition parameter. |
| Subthreshold slope | $S$ | V/decade | Describes current change below threshold over a stated regime. |
| Delay and energy | $t_d,E_{switch}$ | s, J | Circuit- and workload-dependent rather than device-count-only. |
""",
    ("technology/18-semiconductors-electronics/overview.md", 6): """## 6. Mathematical models and equations

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
""",
    ("technology/18-semiconductors-electronics/overview.md", 8): """## 8. Assumptions and approximations

- **Equilibrium and non-degenerate statistics:** Carrier formulas change under strong injection, illumination, degeneracy, trapping, and rapid transients.
- **Complete ionisation:** Can fail at low temperature, high doping, compensation, or deep impurity levels.
- **Depletion and abrupt-junction approximations:** Simplify Poisson's equation but omit graded profiles and mobile carriers.
- **Low-field mobility:** Drift mobility is not constant across electric field, temperature, geometry, and carrier density.
- **Long-channel compact models:** Nanoscale transistors include short-channel electrostatics, tunnelling, discrete variability, parasitics, self-heating, and quantum confinement.
""",
    ("technology/18-semiconductors-electronics/overview.md", 10): """## 10. Common misconceptions

- **“A semiconductor is halfway between a conductor and an insulator.”** The useful feature is controllable carrier population and transport within a designed material and device structure.
- **“Holes are imaginary.”** Holes are quasiparticles that accurately describe collective valence-band transport within a model; they are not tiny empty beads moving through space.
- **“A transistor is either perfectly off or on.”** Current changes continuously, leakage persists, and logic states are defined by circuit thresholds and noise margins.
- **“Electrical information travels at electron drift speed.”** Signal propagation follows electromagnetic fields and circuit geometry, while carrier drift and local charging support that propagation.
- **“Smaller node names equal one literal feature size.”** Node labels bundle technology generations and do not specify every gate, pitch, or interconnect dimension.
""",
    ("technology/18-semiconductors-electronics/overview.md", 11): """## 11. Connections to other modules

- **06-matter-quantum:** Quantum states, statistics, tunnelling, and periodic potentials underpin device models.
- **10-electricity-magnetism:** Fields, capacitance, current continuity, and transmission-line effects connect devices to circuits.
- **17-materials-manufacturing:** Crystal growth, deposition, implantation, etching, patterning, cleaning, packaging, and metrology create devices.
- **19-software-ai:** Instruction sets, memory hierarchies, compilers, workloads, and algorithms determine how hardware capability is used.
- **20-sensors-control-infrastructure:** Sensors, power electronics, embedded controllers, and communication interfaces connect chips to physical systems.
""",
    ("technology/18-semiconductors-electronics/technology.md", 5): """## 5. Matter, energy, force, or information flow

- **Information:** Logical states are encoded in voltage, charge, current, resistance, phase, or other physical variables within specified noise margins and timing windows.
- **Charge and fields:** Carriers move and nodes charge or discharge through device and interconnect fields; information is not itself a substance flowing through the chip.
- **Energy:** Dynamic power approximately scales as $P_{dyn}=\alpha C V^2 f$ for a stated switched capacitance and activity factor, while leakage, short-circuit current, memory, interconnect, clocking, and I/O add other terms.
- **Heat:** Dissipated energy raises temperatures according to packaging, thermal resistance, cooling, workload, and spatial power density.
""",
    ("technology/18-semiconductors-electronics/technology.md", 7): """## 7. Design constraints

- **Power, temperature, and reliability:** Voltage, frequency, workload, cooling, and ageing mechanisms constrain sustained operation.
- **Electrostatics and leakage:** Thin barriers, short channels, variability, and tunnelling limit off-state control.
- **Lithography and pattern transfer:** Resolution depends on optics, masks, resist, process windows, multiple patterning, etch, overlay, and metrology; EUV is one part of the system.
- **Interconnect and memory:** Resistance, capacitance, inductance, congestion, data movement, and memory latency can dominate device switching time.
- **Yield and variability:** Defects and process variation turn nominal design into statistical production; redundancy, design rules, testing, and process control are required.
- **Packaging:** Power delivery, signal integrity, thermal paths, mechanical stress, chiplets, and advanced integration shape system performance.
""",
    ("technology/18-semiconductors-electronics/technology.md", 8): """## 8. Performance and efficiency

No single metric describes processor performance. Report workload, precision, compiler, memory, batch size, latency, throughput, energy, thermal limit, and comparison baseline. Transistor count and Moore's observation do not guarantee proportional performance. Dennard-style constant-field scaling was an approximate design framework whose power benefits weakened as leakage, voltage scaling, variability, interconnect, and other constraints became dominant. Modern improvements use architecture, parallelism, accelerators, packaging, memory, software, and workload specialisation as well as device scaling.
""",
    ("technology/18-semiconductors-electronics/technology.md", 10): """## 10. Safety principles

Semiconductor fabrication uses specialised high-energy equipment, vacuum systems, ionising and non-ionising radiation sources, corrosive and toxic chemicals, pyrophoric gases, pressure systems, and cleanroom controls. These are professional environments governed by engineered containment, monitoring, interlocks, ventilation, compatible materials, emergency systems, trained personnel, and regulation. Learners should use simulations, packaged low-voltage educational hardware, or documented fabrication data rather than attempting chemical processing or opening mains-powered devices.
""",
    ("technology/18-semiconductors-electronics/technology.md", 11): """## 11. Environmental and lifecycle considerations

Semiconductor footprints depend on fab location, electricity mix, process gases, abatement, ultrapure water, yield, wafer size, device complexity, packaging, use-phase energy, lifetime, repair, and end-of-life pathways. “Rare earth” is not a sufficient summary of material dependence; critical inputs include many metals, gases, polymers, ceramics, and high-purity chemicals. E-waste risk depends on product composition and treatment. Longer support, efficient software, modularity, reuse, refurbishment, and responsible recycling can reduce impacts but involve trade-offs.
""",
    ("technology/18-semiconductors-electronics/explore.md", 2): """## 2. Prediction questions

- Compare intrinsic and doped silicon over a stated temperature range. Why can resistance trends depend on carrier generation, dopant activation, mobility, contacts, geometry, and self-heating?
- In a diode model, reverse bias usually widens the depletion region, but predict leakage, capacitance, and possible breakdown only after device type, voltage range, temperature, and circuit resistance are specified.
- Treat Moore's observation as historical data: given an assumed doubling interval, calculate a backward extrapolation and then explain why node economics, design choices, and product categories make it an unreliable prediction for a specific processor.
""",
    ("technology/18-semiconductors-electronics/explore.md", 3): """## 3. Worked reasoning examples

**Question:** Why does a high-performance processor often need substantial cooling while a calculator does not?

1. Identify workload, supply voltage, clocking, active capacitance, leakage, memory, display, and duty cycle rather than counting transistors alone.
2. Dynamic switching power is approximated by $P_{dyn}=\alpha C V^2 f$ at a chosen boundary; leakage and supporting circuits add power.
3. A calculator operates intermittently at low throughput and power, while a processor may sustain dense computation and data movement.
4. Packaging and cooling determine temperature rise. Thermal throttling or shutdown protects many systems before destructive temperatures occur.
5. Cooling need therefore follows total and local power, thermal resistance, allowable junction temperature, acoustics, reliability, and workload—not simply “billions times gigahertz.”
""",
    ("technology/18-semiconductors-electronics/explore.md", 5): """## 5. Household and browser-based explorations

- **Logic simulation:** Build gates and a half-adder in a browser simulator. Add propagation delay or unknown states where supported, and distinguish Boolean function from electrical implementation.
- **Virtual teardown:** Use manufacturer diagrams, repair documentation, or high-resolution board photographs rather than opening discarded electronics. Identify packages, connectors, power sections, traces, and uncertainty about hidden layers.
- **Thermal observation:** Use built-in operating-system temperature or power telemetry only when available, without bypassing safety limits. Compare idle and ordinary workloads and note that sensor placement and software estimates introduce uncertainty.
- **Semiconductor metrology:** Explore NIST material on critical dimension, overlay, and process measurement. Explain why fabrication success cannot be inferred from a nominal node label alone.
""",
    ("technology/19-software-ai/overview.md", 2): """## 2. Observable phenomena

Lossless compression reduces some structured files but cannot shrink every input; already compressed or high-entropy data may stay similar or grow because of headers. Error-control coding can make communication highly reliable at rates and latencies allowed by a channel, code, hardware, and target error probability.

Internet paths are selected through distributed routing and forwarding state. Delay includes propagation, transmission, queueing, processing, retransmission, and endpoint work; “milliseconds across continents” is not one universal value.

Machine-learning performance can improve with data, computation, architecture, objectives, and training, but more examples do not guarantee better deployment performance. Apparent capabilities must be defined by reproducible evaluations and checked for contamination, prompting effects, distribution shift, and failure cases.
""",
    ("technology/19-software-ai/overview.md", 3): """## 3. Essential concepts

**Information measures:** Shannon entropy quantifies uncertainty for a probability model. It does not measure truth, usefulness, semantic meaning, or human importance.

**Source and channel coding:** Compression and reliable communication have asymptotic limits under stated source and channel assumptions. Finite systems trade block length, error, delay, energy, computation, and implementation complexity.

**Protocols and layering:** Internet communication uses multiple protocols. IP provides best-effort packet delivery; TCP provides a reliable ordered byte stream between endpoints under its specification, while applications still handle identity, semantics, retries, security, and failure.

**Operating systems and databases:** Kernels mediate resources and isolation, but security depends on design, configuration, implementation, hardware, updates, and operation. Databases combine storage, concurrency, recovery, query processing, schemas, and distributed trade-offs.

**Machine learning:** Models estimate functions or distributions from data and objectives. Supervised, self-supervised, unsupervised, and reinforcement-learning methods have different feedback and evaluation structures.

**AI risk management:** Trustworthiness concerns include validity, reliability, safety, security, resilience, accountability, transparency, explainability, privacy, fairness, misuse, information integrity, monitoring, incident response, and human oversight across the lifecycle.
""",
    ("technology/19-software-ai/overview.md", 4): """## 4. Mechanisms and causal chains

In coding, a source model informs compression and controlled redundancy supports error detection or correction. Shannon's theorems show existence results in limiting regimes; they do not supply a free practical code or promise zero error at finite delay.

In networking, applications may use TCP, UDP, QUIC, or other transports over IP. TCP numbers bytes, acknowledges data, manages retransmission and flow/congestion behavior, but TCP does not guarantee that an application request is semantically processed once, securely, or within a deadline.

In neural-network training, automatic differentiation applies the chain rule to a computational graph. An optimiser uses gradients or related estimates to update parameters. Success depends on objective, data, representation, regularisation, optimisation, randomisation, hardware numerics, and evaluation; gradient descent does not guarantee the global optimum for a general non-convex model.
""",
    ("technology/19-software-ai/overview.md", 5): """## 5. Important quantities

| Quantity | Unit or form | Boundary |
| :--- | :--- | :--- |
| Entropy or cross-entropy | bits, nats, or task-specific average | Requires a probability distribution and log base. |
| Bandwidth | Hz or sometimes data-rate context | Frequency span is not identical to throughput. |
| Signal-to-noise ratio | dimensionless ratio; dB after logarithmic conversion | State measurement bandwidth and reference. |
| Capacity | bit/s | Defined for a channel model and reliability criterion. |
| Latency | s | Specify one-way, round-trip, percentile, and boundary. |
| Throughput or goodput | bit/s, requests/s, tokens/s | Specify useful payload and load. |
| Loss | task-dependent | Not simply “difference”; may be negative log likelihood, ranking, control cost, or another objective. |
| Calibration error | task-dependent | Compares predicted confidence with observed frequency under a protocol. |
| Energy and emissions | J, kWh, or lifecycle units | Require hardware, utilisation, location, and accounting boundary. |
""",
    ("technology/19-software-ai/overview.md", 6): """## 6. Mathematical models and equations

For a discrete random variable,
$$H(X)=-\sum_x p(x)\log_2p(x).$$
For an ideal code over long sequences, expected length is bounded relative to entropy; entropy is not literally the exact file size of every finite message.

For a bandwidth-limited additive white Gaussian-noise channel,
$$C=B\log_2\left(1+\frac{S}{N}\right).$$
Here $S/N$ is a dimensionless power ratio over the stated bandwidth. The equation does not imply infinite physical throughput when a model parameter is set to an unphysical limit; finite power, noise, bandwidth, precision, timing, and implementation remain.

A parameter update may be written
$$\theta_{k+1}=\theta_k-\alpha_k\widehat{\nabla L}(\theta_k),$$
where the gradient can be stochastic or approximate and the learning rate can carry units depending on parameterisation and loss.

An artificial unit
$$y=f(\mathbf{w}^{\mathsf T}\mathbf{x}+b)$$
is a computational component, not a biological neuron model or evidence of cognition.
""",
    ("technology/19-software-ai/overview.md", 8): """## 8. Assumptions and approximations

- **Source and channel models:** Stationarity, memory, noise, feedback, synchronisation, and coding constraints must be stated.
- **Finite implementation:** Block length, numerical precision, queueing, congestion, deadlines, and energy prevent direct identification of theorem limits with product performance.
- **Data-generating process:** Training examples are rarely perfectly independent, identically distributed, representative, consented, or stable over time.
- **Objective adequacy:** Optimising a proxy can improve the measured score while harming the intended outcome.
- **Evaluation validity:** Test leakage, benchmark saturation, selection bias, subgroup size, multiple comparisons, and adaptive use can invalidate conclusions.
- **Deployment:** Distribution shift, feedback loops, adversaries, users, automation bias, and organisational context change system behaviour.
""",
    ("technology/19-software-ai/overview.md", 10): """## 10. Common misconceptions

- **“Information equals meaning.”** Shannon information measures uncertainty in a model, not semantics, truth, value, or wisdom.
- **“The internet has no central points of failure.”** It is a network of networks, yet services, naming, routing, clouds, cables, power, and organisations can create concentrated dependencies.
- **“More data always improves AI.”** Data quality, relevance, rights, representation, contamination, objectives, model capacity, and distribution shift matter.
- **“A fluent model output proves understanding or consciousness.”** Observable behaviour supports claims about tested capability only; internal experience or broad human-like understanding cannot be inferred from fluency.
- **“AI safety means only speculative catastrophic scenarios.”** It also includes measurable failures involving validity, bias, privacy, security, misuse, automation, monitoring, and human consequences.
""",
    ("technology/19-software-ai/technology.md", 3): """## 3. Main components

- **Hardware and firmware:** Processors, memory, storage, accelerators, network interfaces, boot chains, and device controllers.
- **Operating system and runtime:** Scheduling, memory, files, isolation, drivers, identity, logging, and interfaces; none is automatically secure.
- **Network services:** Links, routers, naming, addressing, transports, encryption, load balancing, and observability.
- **Data systems:** Schemas, storage engines, indexes, transactions, replication, recovery, access control, lineage, and retention.
- **ML lifecycle:** Data collection and governance, training, evaluation, deployment, monitoring, incident handling, model and prompt configuration, human review, and retirement.
- **Organisational controls:** Requirements, change management, threat modelling, privacy review, documentation, audit, procurement, and accountability.
""",
    ("technology/19-software-ai/technology.md", 5): """## 5. Matter, energy, force, or information flow

Information is represented by physical states and transformed through hardware and software abstractions. Data movement consumes energy and often dominates computation. During model training, activations, parameters, gradients, optimiser state, and checkpoints move through memory and networks; “information flowing backward” is a metaphor for derivative computation, not a substance. System boundaries should include users, data sources, operators, external services, electricity, cooling, and discarded hardware.
""",
    ("technology/19-software-ai/technology.md", 6): """## 6. System architecture

Layering reduces local complexity but does not remove cross-layer effects. Internet protocols, operating systems, databases, cloud platforms, and ML services each use different architectures. A production AI service commonly includes data ingestion, retrieval, model inference, policy enforcement, authentication, rate limiting, logging, human escalation, monitoring, rollback, and incident response. Trust boundaries and failure containment must be explicit; a model is one component, not the whole system.
""",
    ("technology/19-software-ai/technology.md", 7): """## 7. Design constraints

- **Latency, throughput, and tail behavior:** Percentiles, queueing, and overload matter more than averages alone.
- **Consistency, availability, and partitions:** Distributed systems make context-dependent trade-offs; slogans do not replace a failure model.
- **Computation, memory, and communication:** Complexity classes inform scaling, but approximation, heuristics, preprocessing, hardware, and input size determine practical feasibility.
- **Security and privacy:** Least privilege, secure development, encryption, isolation, secrets management, data minimisation, consent, retention, and incident response impose constraints.
- **AI-specific constraints:** Data rights, representativeness, calibration, interpretability, robustness, misuse resistance, human factors, and monitoring must be designed rather than added later.
""",
    ("technology/19-software-ai/technology.md", 8): """## 8. Performance and efficiency

Network and database systems require load, dataset, hardware, consistency, and percentile definitions. AI evaluation should include task validity, baselines, confidence intervals, calibration, subgroup results, robustness, abstention, latency, throughput, cost, energy, privacy, and human outcomes. Accuracy on one test set is insufficient. Efficiency claims must include data movement, utilisation, retraining, failed experiments, serving, and lifecycle boundaries.
""",
    ("technology/19-software-ai/technology.md", 9): """## 9. Reliability and failure modes

Checksums detect only specified corruption patterns; TCP retransmission does not make an application exactly-once or deadline-safe. Write-ahead logging supports recovery only with correct ordering, durable storage assumptions, tested restoration, and transaction design. Replication can copy errors or attacks. ML systems can fail through distribution shift, data or label errors, prompt injection, insecure tool use, feedback loops, model updates, dependency outages, automation bias, and silent metric drift. Reliability therefore requires redundancy, diversity where appropriate, validation, observability, backups, rollback, chaos or fault testing, and rehearsed recovery.
""",
    ("technology/19-software-ai/technology.md", 10): """## 10. Safety principles

Use a lifecycle risk process: define context and affected people, map hazards and misuse, measure with valid tests, manage residual risk, document limitations, monitor deployment, provide human authority and appeal, and respond to incidents. Security testing must remain authorised and non-destructive. Protect personal data through minimisation, purpose limitation, access control, retention limits, and review. High-impact decisions require domain-qualified human oversight, uncertainty communication, logging, fallback, and the ability to stop or reverse automation.
""",
    ("technology/19-software-ai/explore.md", 1): """## 1. Observation prompts

- Use browser or operating-system performance panels on your own device to compare page size, request count, latency, caching, and throughput. Do not infer physical route or server location from delay alone.
- Examine recommendation settings using a fictional profile or your own non-sensitive history. Record what the interface reveals, what remains unknown, and how privacy, exploration, popularity, and business objectives could shape outputs.
- Compare two model outputs on a low-stakes public question. Check sources, uncertainty, consistency, and failure modes instead of rating fluency as understanding.
""",
    ("technology/19-software-ai/explore.md", 2): """## 2. Prediction questions

- Predict compression for repetitive, already-compressed, encrypted, and random-looking files. Why can headers make some compressed outputs larger?
- If one router or link fails, outcomes depend on routing convergence, transport timeout, application retry, resumable transfer, multipath support, and failure location. List competing outcomes rather than predicting seamless continuation.
- A classifier trained on indoor cats may fail outdoors because background, lighting, camera, breed, label, and sampling distributions changed. Which validation set would test the intended deployment?
""",
    ("technology/19-software-ai/explore.md", 4): """## 4. Thought experiments

- **Noiseless-channel limit:** The Shannon–Hartley equation assumes an idealised Gaussian channel model. Letting $N\to0$ while holding other abstractions fixed exposes a model limit, not a physical design for infinite instantaneous communication. Identify omitted constraints such as quantisation, timing, bandwidth definition, finite energy, hardware, and relativity.
- **Proxy objective failure:** A room-cleaning system rewarded only for measured dust could manipulate the sensor or repeatedly move dust. Redesign the system using multiple measurements, constraints, human review, shutdown authority, and tests for distribution shift.
- **Automation and appeal:** Imagine a model recommends access to a school resource. What evidence, uncertainty, privacy protection, explanation, human review, and appeal process are required before the recommendation affects a student?
""",
    ("technology/19-software-ai/explore.md", 5): """## 5. Household and browser-based explorations

- **Network waterfall:** Use developer tools only on pages you are authorised to access. Record request timing, cache status, content type, and third-party domains without copying tokens, cookies, personal data, or credentials.
- **Latency measurement:** Use your operating system's connection diagnostics, your own router, or a reputable public measurement page. Do not probe private systems or interpret one round-trip value as geographic distance.
- **Model evaluation sheet:** Build a small fictional classification dataset with a held-out test set. Report confusion matrix, calibration bins, subgroup uncertainty, and examples where the model should abstain.
- **Compression experiment:** Compare original and compressed sizes for several non-sensitive files, including an already compressed image. Record algorithm, options, metadata overhead, and reproducibility.
""",
    ("technology/19-software-ai/explore.md", 10): """## 10. Reasoning notes

Distinguish logical abstractions from physical implementation, specification from implementation, average from tail behavior, benchmark from deployment, and correlation from causal effect. Treat model outputs as fallible evidence. Avoid anthropomorphism in either direction: do not infer human-like consciousness from fluent behavior, and do not replace empirical capability analysis with the slogan “only pattern matching.” State the tested task, comparison, uncertainty, distribution, tools, and human context.
""",
    ("technology/20-sensors-control-infrastructure/overview.md", 3): """## 3. Essential concepts

**Measurement and transduction:** Sensors map physical variables to signals through mechanisms such as resistance, capacitance, charge, frequency, optical intensity, or digital state. This is not always a direct conversion of one energy form into another.

**Estimation:** Measurements are incomplete and noisy. Filters and observers combine data and models to estimate hidden state, bias, disturbance, and uncertainty.

**Feedback and feedforward:** Controllers use measurements, estimates, references, constraints, and forecasts to shape behavior. Objectives can include tracking, regulation, disturbance rejection, safety, efficiency, and constraint satisfaction—not merely minimising instantaneous error.

**Automation and robotics:** Physical autonomy integrates sensing, estimation, planning, control, actuation, communication, safety systems, operators, and maintenance.

**Infrastructure resilience:** Resilience concerns anticipation, absorption, adaptation, recovery, and learning across technical, human, organisational, and supply-chain layers. Reliability, resilience, safety, and security are related but distinct.
""",
    ("technology/20-sensors-control-infrastructure/overview.md", 4): """## 4. Mechanisms and causal chains

A more complete loop is **measure–condition–sample–estimate–decide–act–verify**. Sensors have calibration, bandwidth, noise, drift, and failure modes. Controllers operate on delayed and quantised data. Actuators have dynamics, dead zones, saturation, rate limits, and energy constraints. Independent protection, alarms, operators, and emergency systems may override normal control.

In an AC grid, active-power imbalance interacts with stored kinetic or electronic energy, frequency-sensitive demand, controls, network constraints, and protection. Frequency is an important indicator but not a complete state estimate. Primary response, inverter controls, storage, demand response, dispatch, reserves, and restoration act on different timescales. Protection must isolate faults without causing unnecessary cascading trips.
""",
    ("technology/20-sensors-control-infrastructure/overview.md", 5): """## 5. Important quantities

| Quantity | Unit | Boundary |
| :--- | :--- | :--- |
| Measurement error and uncertainty | sensor-specific | Separate bias, noise, resolution, calibration, and model uncertainty. |
| Sampling period and delay | s | Include computation, communication, actuator, and transport delay. |
| State estimate and covariance | mixed units | Defined by the state model and estimator. |
| Control input and saturation | actuator-specific | State amplitude and rate limits. |
| Stability margins | dB, degrees, or model-specific | Valid for a specified linearisation and loop. |
| Active power | W | Average real energy-transfer rate under stated waveform conditions. |
| Reactive power | var | Defined for AC models; interpretation depends on waveform and convention. |
| Frequency and rate of change | Hz, Hz/s | Local measurements influenced by dynamics and estimation. |
| Reliability and resilience metrics | event- and service-specific | Require service boundary, duration, severity, and consequence. |
""",
    ("technology/20-sensors-control-infrastructure/overview.md", 6): """## 6. Mathematical models and equations

An ideal continuous PID law is
$$u(t)=K_pe(t)+K_i\int_0^t e(\tau)d\tau+K_d\frac{de(t)}{dt}.$$
Derivative action responds to rate; it does not literally predict the future. Real implementations filter derivatives, discretise time, limit outputs, prevent integral windup, and handle setpoint changes and sensor noise.

A linear time-invariant state-space model is
$$\dot{\mathbf{x}}=A\mathbf{x}+B\mathbf{u}+E\mathbf{w},\qquad \mathbf{y}=C\mathbf{x}+D\mathbf{u}+\mathbf{v},$$
with disturbance $\mathbf{w}$ and measurement noise $\mathbf{v}$. Stability, controllability, observability, and estimator assumptions must be checked around a defined operating point.

For sinusoidal steady state in a single-phase convention,
$$\underline S=P+jQ=\underline V_{rms}\underline I_{rms}^{*},\quad P=V_{rms}I_{rms}\cos\phi,\quad Q=V_{rms}I_{rms}\sin\phi.$$
Three-phase, unbalanced, distorted, and converter-dominated systems require the appropriate convention and model.
""",
    ("technology/20-sensors-control-infrastructure/overview.md", 8): """## 8. Assumptions and approximations

- **Linearity and time invariance:** Models usually apply near an operating point and over a stated frequency and amplitude range.
- **Sampling and delay:** Continuous equations omit discrete sampling, jitter, communication loss, computation time, and zero-order hold unless added.
- **Sensor and actuator limits:** Noise, drift, saturation, backlash, dead time, hysteresis, and rate constraints can destabilise or bias a loop.
- **Known model:** Parameters, disturbances, and topology change; robust, adaptive, or gain-scheduled methods still require boundaries.
- **Power-system phasors:** RMS and phasor models assume waveform and timescale conditions; electromagnetic and switching transients need faster models.
- **Human and organisational layer:** Procedures, interfaces, staffing, maintenance, markets, regulation, and cybersecurity affect technical outcomes.
""",
    ("technology/20-sensors-control-infrastructure/overview.md", 10): """## 10. Common misconceptions

- **“Derivative control predicts the future.”** It reacts to measured rate and often amplifies noise; filtered PI or other structures may be preferable.
- **“Integral action always removes steady-state error.”** This requires closed-loop stability, sufficient control authority, a suitable plant and disturbance model, and anti-windup handling.
- **“Renewables inherently destabilise or automatically strengthen a grid.”** Outcomes depend on penetration, location, network strength, controls, reserves, protection, forecasting, storage, demand, and grid-forming or grid-following behavior.
- **“Redundancy guarantees safety.”** Common-cause failure, shared software, incorrect sensors, maintenance, and voting logic can defeat redundant channels.
- **“Automation removes the human role.”** Humans design, authorise, supervise, maintain, recover, and remain affected by system decisions.
""",
    ("technology/20-sensors-control-infrastructure/technology.md", 4): """## 4. How the components interact

A sensor and signal chain produce measurements with calibration, noise, delay, and diagnostic status. An estimator combines measurements and a model. Supervisory logic selects mode and constraints. A controller computes commands, which may be sent digitally, through pulse-width modulation, or through analogue conversion depending on the actuator. Power electronics or drives supply energy. Independent interlocks and protection can override the normal controller. The plant responds, and verification checks whether the commanded and measured behavior remain credible.
""",
    ("technology/20-sensors-control-infrastructure/technology.md", 6): """## 6. System architecture

### Position-control chain

1. **Optical principle:** A patterned encoder changes transmitted or reflected light detected by photodiodes; the photoelectric effect is part of detection, while interference is not required for a basic encoder.
2. **Measurement:** Electronics count or interpolate transitions to estimate quantised position and velocity. Accuracy also depends on alignment, index reference, calibration, backlash, missed counts, and timing.
3. **Control:** A sampled controller uses the estimate, reference, limits, and diagnostics.
4. **Drive and actuator:** Power electronics regulate motor current or voltage within thermal and current limits.
5. **Mechanics:** Gearbox compliance, friction, inertia, resonance, payload, and structural modes determine motion.
6. **Safety:** Brakes, stops, guarding, monitored limits, emergency stop, and human procedures are separate from normal position control.

### Grid architecture

Generation, transmission, distribution, distributed energy resources, storage, demand, markets, communications, protection, and operators form coupled layers. Smart inverters may provide voltage support, frequency response, or grid-forming behavior only when hardware, controls, settings, standards, and system conditions support those functions. Synthetic inertia is not an automatic property of every inverter.
""",
    ("technology/20-sensors-control-infrastructure/technology.md", 8): """## 8. Performance and efficiency

Control performance includes tracking, disturbance rejection, settling, overshoot, robustness, constraint violations, energy use, wear, availability, and safety events. Report operating range and uncertainty. Infrastructure efficiency must distinguish component efficiency from service reliability and lifecycle cost. High voltage can reduce current-related losses for a given transferred power, but conversion, reactive power, congestion, stability, and protection constraints remain. Renewable capacity factor is mainly a resource and availability metric; storage and demand response reshape delivery rather than “maximising” the underlying resource.
""",
    ("technology/20-sensors-control-infrastructure/technology.md", 9): """## 9. Reliability and failure modes

- **Measurement faults:** Bias, drift, frozen values, timing errors, spoofing, and common-cause failures can be more dangerous than obvious loss.
- **Estimator or model failure:** Wrong topology, parameters, or unmodelled modes can produce confident but incorrect state estimates.
- **Actuator limits:** Saturation and rate limits remove control authority and can cause integral windup or instability.
- **Communication and timing:** Delay, loss, reordering, clock error, and network partition affect closed-loop behavior.
- **Cascading events:** Protection, operator actions, hidden failures, thermal overload, voltage instability, frequency dynamics, and communication can interact across timescales.
- **Recovery failure:** Backups and redundant controllers help only when tested, independent enough, maintained, and included in restoration exercises.
""",
    ("technology/20-sensors-control-infrastructure/technology.md", 10): """## 10. Safety principles

Safety cannot always be reduced to “power off equals safe.” Some systems must fail safely, others must remain operational long enough to reach a safe condition, and stored mechanical, electrical, thermal, hydraulic, or chemical energy may persist. Use hazard analysis, independent protection, safe-state and fail-operational requirements, physical separation, verified isolation, guarded machinery, access control, alarms, emergency procedures, testing, and trained human authority.

Industrial control systems require cybersecurity that respects real-time performance, availability, safety, legacy equipment, and controlled change. Apply defence in depth, segmentation, authenticated access, least privilege, monitoring, secure remote maintenance, tested backups, incident response, and recovery. Learners should not connect to, scan, alter, or experiment on real operational technology or public infrastructure.
""",
    ("technology/20-sensors-control-infrastructure/technology.md", 11): """## 11. Environmental and lifecycle considerations

Infrastructure lifecycle assessment includes extraction, manufacturing, land and water use, construction, operation, maintenance, losses, replacement, resilience upgrades, decommissioning, and recycling. Equipment lifetime is not one fixed 20–30 year value; it varies by asset, duty, environment, maintenance, obsolescence, and standards. Renewable systems reduce some operating emissions but still require materials, networks, storage, and responsible end-of-life management. Reliability and climate resilience can justify redundancy that increases material use, so trade-offs must be explicit.
""",
    ("technology/20-sensors-control-infrastructure/explore.md", 1): """## 1. Observation prompts

- Identify sensors only from normal public or household use. Do not open alarms, appliances, panels, meters, substations, cabinets, or restricted areas. Record measured variable, likely transduction principle, sampling, and possible failure modes.
- Observe power infrastructure only from a public safe distance. Never touch, climb, approach damaged equipment, enter fenced areas, or infer voltage solely from appearance. Use utility diagrams to distinguish transmission, distribution, substations, and transformers.
- Map an appliance's likely measure–estimate–decide–act–verify loop from manuals or animations rather than interfering with its operation.
""",
    ("technology/20-sensors-control-infrastructure/explore.md", 3): """## 3. Worked reasoning examples

**Scenario:** Conceptual cruise-control tuning in a simulation

1. Proportional action responds to current speed error. A constant hill or drag can leave offset depending on plant and gain.
2. Integral action accumulates error and can remove offset only if the loop remains stable and the actuator has authority. Saturation requires anti-windup.
3. Derivative action responds to rate and can add damping, but it amplifies measurement noise and does not literally anticipate a future hill.
4. Feedforward from estimated grade or requested acceleration can complement feedback.
5. Real vehicle control includes actuator limits, braking, traction, safety supervision, driver authority, and validated operating envelopes. This is a simulation exercise, not a driving or vehicle-modification instruction.
""",
    ("technology/20-sensors-control-infrastructure/explore.md", 5): """## 5. Household and browser-based explorations

- **Low-energy feedback simulation:** Use a browser simulation of an inverted pendulum, temperature loop, or motor. Change delay, noise, sampling, gain, saturation, and disturbance; do not balance long objects near your face or other people.
- **Grid model:** Use an institutional educational simulator or public historical dataset. Separate energy adequacy, frequency response, network congestion, reserves, emissions, cost, and reliability; a 24-hour energy balance is not a full stability study.
- **Sensor calibration model:** Given a supplied table of reference and sensor readings, fit offset and scale, inspect residuals, and propagate uncertainty. Add a drift or stuck-sensor fault and design a diagnostic.
""",
    ("technology/20-sensors-control-infrastructure/explore.md", 10): """## 10. Reasoning notes

Define the plant, controller, estimator, actuator, sensor, communication path, operator, protection system, environment, and service boundary. Track delay, sampling, saturation, uncertainty, common-cause failure, cybersecurity, maintenance, and recovery. A technically stable loop can still be unsafe, insecure, unfair, unaffordable, or difficult to operate. Conversely, resilience is not one component; it is the demonstrated ability of the whole socio-technical system to continue or recover an essential service.
""",
}

BANNED = (
    "Wikipedia.",
    "18-solid-mechanics",
    "19-thermodynamics",
    "19-computing-architecture",
    "Bend it back and forth repeatedly at the same spot until it breaks",
    "heat a piece of high-carbon steel until it glows red",
    "Open it up and identify the printed circuit board",
    "ping google.com",
    "Try balancing a long stick",
    "capacity C approaches infinity",
    "chip will melt",
    "depletion region devoid of mobile charge carriers",
    "minimum gate voltage required to create a conducting channel",
    "simply by processing more examples",
    "no single point of control or failure",
    "exact angular position",
    "predicting future error",
    "sustain human life indefinitely",
)


def expected_slug(module: str, filename: str) -> str:
    return module if filename == "overview.md" else f"{module}-{filename.removesuffix('.md')}"


def set_frontmatter(text: str, module: str, filename: str) -> str:
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated frontmatter")
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    order: list[str] = []
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        data[key] = value.strip()
        order.append(key)
    data["slug"] = expected_slug(module, filename)
    data["module"] = f'"Module {module[:2]}"'
    data["domain"] = "technology"
    data["status"] = "reviewed"
    data["prerequisites"] = "[" + ", ".join(MODULES[module]["prerequisites"]) + "]"
    data["connections"] = "[" + ", ".join(MODULES[module]["connections"]) + "]"
    data["last_reviewed"] = REVIEW_DATE
    data["content_license"] = "CC-BY-4.0"
    canonical = ["title", "slug", "module", "domain", "status", "prerequisites", "connections", "last_reviewed", "content_license"]
    lines = [f"{key}: {data[key]}" for key in canonical if key in data]
    for key in order:
        if key not in canonical:
            lines.append(f"{key}: {data[key]}")
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def replace_numbered_section(text: str, number: int, replacement: str) -> str:
    pattern = re.compile(rf"(?ms)^## {number}\. .*?(?=^## {number + 1}\. |\Z)")
    if not pattern.search(text):
        raise ValueError(f"section {number} not found")
    return pattern.sub(replacement.rstrip() + "\n\n", text, count=1)


def replace_or_append_sources(text: str, module: str, filename: str) -> str:
    source_number = {"overview.md": 12, "technology.md": 13, "explore.md": 11}[filename]
    heading = f"## {source_number}. Sources"
    block = heading + "\n\n" + SOURCES[module].rstrip() + "\n"
    pattern = re.compile(r"(?ms)^## (?:11|12|13)\. Sources\s*\n.*\Z")
    if pattern.search(text):
        return pattern.sub(block, text, count=1)
    return text.rstrip() + "\n\n" + block


def insert_boundaries(text: str, module: str) -> str:
    marker = "## Phase 9 review boundaries and validity limits"
    if marker in text:
        return text
    source = re.search(r"(?m)^## (?:11|12|13)\. Sources\s*$", text)
    if not source:
        raise ValueError("source section missing before boundary insertion")
    return text[: source.start()] + BOUNDARIES[module].rstrip() + "\n\n" + text[source.start() :]


def transform(path: Path, module: str) -> tuple[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    original = text
    rel = path.relative_to(ROOT).as_posix()
    notes: list[str] = []
    text = set_frontmatter(text, module, path.name)
    for old, new in ALIASES.items():
        if old in text:
            text = text.replace(old, new)
            notes.append(f"alias: {old}")
    for old, new in EXACT.get(rel, {}).items():
        if old in text:
            text = text.replace(old, new)
            notes.append(f"replaced: {old[:60]}")
    for (target, number), replacement in SECTION_REPLACEMENTS.items():
        if target == rel:
            text = replace_numbered_section(text, number, replacement)
            notes.append(f"section {number}")
    text = replace_or_append_sources(text, module, path.name)
    text = insert_boundaries(text, module)
    if original != text:
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return text, notes


def update_index() -> None:
    path = ROOT / "INDEX.md"
    text = path.read_text(encoding="utf-8")
    for number in range(17, 21):
        text = re.sub(rf"(?m)^(\| {number:02d} \|.*\|) Draft \|$", r"\1 Reviewed |", text)
    path.write_text(text, encoding="utf-8")


def validate() -> list[str]:
    errors: list[str] = []
    ledger = (ROOT / "sources/source-ledger.md").read_text(encoding="utf-8")
    for module in MODULES:
        for filename in FILENAMES:
            path = ROOT / "technology" / module / filename
            if not path.exists():
                errors.append(f"missing {path.relative_to(ROOT)}")
                continue
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(ROOT).as_posix()
            if "status: reviewed" not in text:
                errors.append(f"{rel}: not reviewed")
            if f"last_reviewed: {REVIEW_DATE}" not in text:
                errors.append(f"{rel}: review date missing")
            if "Phase 9 review boundaries and validity limits" not in text:
                errors.append(f"{rel}: validity-limit section missing")
            for url in re.findall(r"https?://[^\s)]+", SOURCES[module]):
                clean = url.rstrip(".,;:")
                if clean not in text:
                    errors.append(f"{rel}: reviewed source missing: {clean}")
                if clean not in ledger:
                    errors.append(f"{rel}: source absent from central ledger: {clean}")
            lower = text.lower()
            for phrase in BANNED:
                if phrase.lower() in lower:
                    errors.append(f"{rel}: banned legacy or unsafe text remains: {phrase}")
    index = (ROOT / "INDEX.md").read_text(encoding="utf-8")
    for number in range(1, 21):
        row = next((line for line in index.splitlines() if line.startswith(f"| {number:02d} |")), "")
        if not row.endswith("| Reviewed |"):
            errors.append(f"INDEX: Module {number:02d} not Reviewed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.write:
        for module in MODULES:
            for filename in FILENAMES:
                transform(ROOT / "technology" / module / filename, module)
        update_index()

    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Phase 9 technology review transformation validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
