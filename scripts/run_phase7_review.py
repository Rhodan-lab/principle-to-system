#!/usr/bin/env python3
"""Run the Phase 7 review while preserving or creating source headings."""
from __future__ import annotations

import re

import apply_phase7_physical_science_review as phase7

for module, block in tuple(phase7.SOURCES.items()):
    lines = block.splitlines()
    if lines and re.match(r"^## (?:12|13)\. Sources$", lines[0]):
        phase7.SOURCES[module] = "\n".join(lines[1:]).lstrip()

# Corrective explanations may name a misconception. Ban the exact legacy claims
# or unsafe instructions rather than banning the educational phrase everywhere.
phase7.BANNED = tuple(
    phrase
    for phrase in phase7.BANNED
    if phrase not in {
        "virtual particles popping in and out",
        "path of least resistance",
        "upper lip",
    }
) + (
    "vacuum is teeming with fluctuating quantum fields and virtual particles",
    "Current takes the path of least resistance",
    "Hold it loosely against your upper lip",
    "inevitable progression of systems toward disorder",
    "Measure of average microscopic kinetic energy",
    "Total heat content of a system",
    "Cold is not a substance; it is the absence of thermal energy",
    "-300,000 \\, \\text{N}",
    "Coanda effect",
    "must experience a drop in pressure",
    "Vigorously pump up a bicycle tire",
    "sealed, rigid container half-filled with liquid water",
    "without the catalyst being consumed",
)

ALIASES = {
    "08-thermodynamics": "08-energy-thermodynamics",
    "09-materials-science": "17-materials-manufacturing",
    "09-fluid-dynamics": "12-fluids-materials",
    "10-thermodynamics": "08-energy-thermodynamics",
    "11-electromagnetism": "10-electricity-magnetism",
    "11-thermodynamics": "08-energy-thermodynamics",
    "12-quantum-mechanics": "06-matter-quantum",
    "12-semiconductors": "18-semiconductors-electronics",
    "12-optics": "11-waves-signals",
    "12-chemical-kinetics": "07-chemical-bonding",
    "13-energy-systems": "20-sensors-control-infrastructure",
    "14-electronics": "18-semiconductors-electronics",
    "14-quantum-mechanics": "06-matter-quantum",
    "15-control-systems": "20-sensors-control-infrastructure",
    "16-communication-systems": "20-sensors-control-infrastructure",
    "16-manufacturing-processes": "17-materials-manufacturing",
    "17-structural-engineering": "17-materials-manufacturing",
    "18-aerospace-systems": "20-sensors-control-infrastructure",
}

FINAL_EXACT = {
    "science/06-matter-quantum/overview.md": {
        "Instead, the universe at its most fundamental level operates according to quantum principles, where energy, momentum, and angular momentum are often restricted to discrete values, and particles exhibit both wave-like and particle-like properties.":
            "Instead, quantum states determine probability amplitudes for measurement outcomes; some observables have discrete spectra in bound systems, and quantum entities do not obey a purely classical particle-or-wave description.",
        "The electromagnetic force, mediated by photons, binds negatively charged electrons to the positively charged nucleus.":
            "The electromagnetic interaction binds negatively charged electrons to the positively charged nucleus.",
        "As electrons are added to an atom, they fill available orbitals in order of increasing energy (Aufbau principle).":
            "As electrons are added to an atom, approximate orbital-filling rules organise many ground-state configurations, with known exceptions caused by electron correlation and near-degenerate energies.",
        "$h$: Planck constant ($6.626 \\times 10^{-34} \\text{ J}\\cdot\\text{s}$)":
            "$h$: Planck constant (exactly $6.62607015 \\times 10^{-34} \\text{ J}\\cdot\\text{s}$)",
        "$\\hbar$: Reduced Planck constant, $h / (2\\pi)$ ($1.055 \\times 10^{-34} \\text{ J}\\cdot\\text{s}$)":
            "$\\hbar$: Reduced Planck constant, $h/(2\\pi)$ (approximately $1.054571817 \\times 10^{-34} \\text{ J}\\cdot\\text{s}$)",
        "$c$: Speed of light in a vacuum ($3.00 \\times 10^8 \\text{ m/s}$)":
            "$c$: Speed of light in vacuum (exactly $299\\,792\\,458 \\text{ m/s}$)",
        "$\\Delta x$: Uncertainty in position ($\\text{m}$)":
            "$\\Delta x$: Standard deviation of position outcomes for the prepared state ($\\text{m}$)",
        "$\\Delta p$: Uncertainty in momentum ($\\text{kg}\\cdot\\text{m/s}$)":
            "$\\Delta p$: Standard deviation of momentum outcomes for the prepared state ($\\text{kg}\\cdot\\text{m/s}$)",
        "\"Observation\" in quantum mechanics simply means interaction with a macroscopic measuring device, which causes wavefunction collapse or decoherence; consciousness is not required.":
            "Measurement is a physical interaction that correlates a system with an apparatus and environment; decoherence explains loss of observable interference, while collapse language depends on the interpretive or operational framework. Consciousness is not required.",
    },
    "science/06-matter-quantum/technology.md": {
        "Atomic nuclei with non-zero spin possess a magnetic moment. In a strong external magnetic field, these nuclei align and can absorb and re-emit electromagnetic radiation at specific resonant frequencies.":
            "Atomic nuclei with non-zero spin possess magnetic moments. A static field creates a small population imbalance and net magnetisation; radiofrequency fields drive resonance, and the precessing magnetisation induces signals in receiver coils.",
        "If this photon strikes another excited atom, it triggers stimulated emission, producing a second identical photon.":
            "Interaction with the optical field can stimulate emission into the same resonator mode, coherently increasing that mode's field amplitude.",
        "A flow of electrons (matter/charge) tunnels across a vacuum barrier driven by an applied voltage (force).":
            "A small applied potential difference produces a tunnelling current across the vacuum barrier; voltage is energy per unit charge, not a mechanical force.",
        "If a second metal is brought close enough before the wavefunction decays completely, the electron has a finite probability of appearing in the second metal.":
            "When the tip and sample are sufficiently close, their electronic states overlap across the barrier and a bias can produce a measurable tunnelling current.",
        "- **Laser:** Efficiency varies wildly. Semiconductor diode lasers can be highly efficient (over 50% electrical-to-optical efficiency), while gas lasers (like Argon-ion) are notoriously inefficient (often less than 0.1%), dissipating massive amounts of heat.":
            "- **Laser:** Wall-plug efficiency depends strongly on laser architecture, wavelength, operating point, optical losses, and cooling requirements; performance must be reported for the specific device.",
        "- **MRI:** Performance is measured in spatial resolution and signal-to-noise ratio (SNR). Higher magnetic field strengths (e.g., 3 Tesla vs 1.5 Tesla) provide better SNR and resolution but are exponentially more expensive and difficult to engineer.":
            "- **MRI:** Performance depends on signal-to-noise ratio, spatial and temporal resolution, sequence design, coil geometry, field homogeneity, scan time, and patient constraints. Higher field can improve available signal but also increases engineering and safety challenges.",
        "- **STM:** Performance is defined by spatial resolution. A well-tuned STM can resolve individual atoms laterally (approx. 0.1 nm) and fractions of an atom vertically (approx. 0.01 nm).":
            "- **STM:** Under suitable vibration, thermal, electronic, tip, and sample conditions, STM can resolve atomic-scale electronic and topographic contrast; the result is not a simple geometric height map.",
        "A \"quench\" is a catastrophic failure mode where the superconducting magnet suddenly loses its superconductivity, causing rapid loss of superconductivity and helium venting; engineered quench protection and ventilation are essential.":
            "A quench is a serious abnormal event in which part of the superconducting magnet becomes resistive, rapidly depositing stored magnetic energy and potentially venting helium; engineered protection and ventilation are essential.",
        "can become lethal projectiles": "can become dangerous projectiles",
    },
    "science/07-chemical-bonding/overview.md": {
        "A dimensionless ratio of product concentrations to reactant concentrations at equilibrium, each raised to the power of their stoichiometric coefficients.":
            "A dimensionless ratio constructed from equilibrium activities relative to standard states, each raised to its stoichiometric coefficient.",
        "under standard conditions": "with reactants and products in their defined standard states",
        "$A$ is the pre-exponential factor (frequency of collisions)":
            "$A$ is the pre-exponential factor, which combines collision, orientation, and dynamical contributions within the model",
        "For a general reversible reaction $a\\text{A} + b\\text{B} \\rightleftharpoons c\\text{C} + d\\text{D}$, the equilibrium constant $K_c$ is given by:\n$$ K_c = \\frac{[\\text{C}]^c [\\text{D}]^d}{[\\text{A}]^a [\\text{B}]^b} $$\nWhere brackets denote the equilibrium concentrations in $\\text{mol} \\cdot \\text{L}^{-1}$.":
            "For a general reaction $a\\text{A} + b\\text{B} \\rightleftharpoons c\\text{C} + d\\text{D}$, the thermodynamic equilibrium constant is\n$$ K = \\frac{a_{\\mathrm{C}}^c a_{\\mathrm{D}}^d}{a_{\\mathrm{A}}^a a_{\\mathrm{B}}^b}, $$\nwhere each $a_i$ is a dimensionless activity. Concentration or partial-pressure forms are ideal approximations with stated standard states.",
        "$n$ is the number of moles of electrons transferred":
            "$n$ is the stoichiometric number of electrons transferred per reaction as written",
    },
    "science/07-chemical-bonding/technology.md": {
        "catalysis provides mechanisms to lower the activation energy of specific reactions, thereby accelerating them without the catalyst being consumed.":
            "catalysis provides alternative reaction mechanisms with different activation barriers; the catalyst participates in elementary steps and is regenerated overall.",
        "convert toxic byproducts of combustion (such as carbon monoxide, nitrogen oxides, and unburned hydrocarbons) into harmless gases":
            "convert regulated combustion pollutants such as carbon monoxide, nitrogen oxides, and unburned hydrocarbons into less harmful products; carbon dioxide remains a greenhouse gas",
        "reduction of nitrogen oxides ($\\text{NO}_x$) to nitrogen ($\\text{N}_2$) and oxygen ($\\text{O}_2$)":
            "reduction of nitrogen oxides ($\\text{NO}_x$), primarily toward nitrogen ($\\text{N}_2$) under controlled exhaust composition",
        "Efficiency is typically high (over 90%) but is reduced by internal resistance (joule heating).":
            "Round-trip and coulombic efficiencies depend on cell chemistry, temperature, current, state of charge, ageing, and the measurement boundary; internal resistance converts some energy to heat.",
    },
    "science/07-chemical-bonding/explore.md": {
        "replace the hydrogen atoms in water ($\\text{H}_2\\text{O}$) with a heavier element from the same group, like sulfur to make hydrogen sulfide":
            "replace oxygen in water ($\\text{H}_2\\text{O}$) with the heavier group-16 element sulfur to form hydrogen sulfide",
        "If you grind the solid metal into a fine powder, how will the rate of the reaction change?":
            "If otherwise identical samples have smaller particle size and therefore greater exposed area, how will the reaction rate change?",
    },
    "science/08-energy-thermodynamics/overview.md": {
        "the inevitable progression of systems toward disorder":
            "the constraints imposed by energy conservation, entropy production, and equilibrium",
        "**Energy** is the capacity of a physical system to perform work. It exists in many forms, including kinetic (motion), potential (position or configuration), thermal (microscopic kinetic energy), and chemical (energy stored in molecular bonds).":
            "**Energy** is a conserved state quantity used to account for changes and transfers in physical systems. Kinetic, potential, internal, electromagnetic, and chemical contributions are bookkeeping categories; chemical energy is not simply energy stored in individual bonds.",
        "**Free Energy** (such as Gibbs or Helmholtz free energy) is the portion of a system's internal energy that is available to perform thermodynamic work at a constant temperature. It determines whether a process will occur spontaneously.":
            "**Thermodynamic potentials** such as Helmholtz and Gibbs free energy combine state variables for specified environmental constraints. Their changes provide equilibrium and direction criteria only when those constraints and allowed work modes are stated.",
        "| Temperature | $T$ | Kelvin ($\\text{K}$) | Measure of average microscopic kinetic energy. |":
            "| Temperature | $T$ | Kelvin ($\\text{K}$) | Thermodynamic state variable that determines thermal equilibrium and heat-transfer direction. |",
        "| Entropy | $S$ | Joule per Kelvin ($\\text{J/K}$) | Measure of the number of accessible microstates. |":
            "| Entropy | $S$ | Joule per Kelvin ($\\text{J/K}$) | State function defined thermodynamically and statistically. |",
        "| Enthalpy | $H$ | Joule ($\\text{J}$) | Total heat content of a system ($H = U + pV$). |":
            "| Enthalpy | $H$ | Joule ($\\text{J}$) | State function $H=U+pV$, useful in constant-pressure energy balances. |",
        "Where $\\dot{Q}_{\\text{rad}}$ is the radiated power":
            "Where $\\dot{Q}_{\\text{net}}$ is the approximate net radiative heat-transfer rate",
        "A process is spontaneous if the change in Gibbs free energy is negative ($\\Delta G < 0$).":
            "At constant temperature and pressure, with composition and allowed non-expansion work specified, a negative $\\Delta G$ gives the thermodynamic direction away from equilibrium but not the rate.",
        "This demonstrates that no heat engine can be $100\\%$ efficient unless the cold reservoir is at absolute zero, which is practically impossible.":
            "This bound applies to a reversible engine between ideal reservoirs. Reaching absolute zero is unattainable, and every real engine also generates entropy.",
        "Cold is not a substance; it is the absence of thermal energy. Heat flows *out* of the warm room into the cold exterior.":
            "Cold is not a substance. Energy is transferred from the warmer region to the cooler region according to the relevant conduction, convection, and radiation processes.",
        "entropy is strictly a measure of the number of accessible microstates":
            "entropy is a state function whose statistical expression depends on the probability distribution over microstates",
        "it is simply converted into less useful forms, typically low-temperature thermal energy, increasing the entropy of the universe":
            "its ability to deliver useful work can decrease as entropy is generated; this loss of work potential is described by exergy destruction",
    },
    "science/08-energy-thermodynamics/explore.md": {
        "*   **The Bicycle Pump:** Vigorously pump up a bicycle tire. Feel the base of the pump cylinder. Why does it feel warm? Which thermodynamic mechanism is responsible for this temperature increase?":
            "*   **Compression observation:** Use a teacher-approved hand pump normally and within its rated pressure, or use a gas-properties simulation. Compare slow and rapid compression without blocking outlets or touching parts that become hot.",
        "*   Consider a sealed, rigid container half-filled with liquid water and half with water vapor, sitting at room temperature. If you heat the container, what will happen to the pressure inside, and why?":
            "*   In a simulation of a rigid closed vessel containing liquid and vapour, predict how equilibrium pressure changes with temperature. Why would heating a sealed real container be unsafe?",
        "Finally, remember that while energy is always conserved, the *quality* of that energy (its ability to do work) is constantly degrading due to the generation of entropy.":
            "Finally, energy is conserved, but irreversible entropy generation destroys exergy—the maximum useful work available relative to a specified environment.",
    },
    "science/09-motion-forces/overview.md": {
        "mass and energy curve spacetime, and objects follow the straightest possible paths through this curved geometry":
            "stress-energy curves spacetime, and freely falling objects follow geodesics in that geometry",
    },
    "science/09-motion-forces/explore.md": {
        "First, we calculate the initial momentum of the car:":
            "First, we calculate the initial momentum of the cart:",
        "The final momentum is zero because the car stops.":
            "The final momentum is zero because the cart stops.",
        "$$ F_{\\text{avg}} = \\frac{\\Delta p}{t} = \\frac{-3.0 \\, \\text{kg}\\cdot\\text{m/s}}{0.1 \\, \\text{s}} = -300,000 \\, \\text{N} $$":
            "$$ F_{\\text{avg}} = \\frac{\\Delta p}{t} = \\frac{-3.0 \\, \\text{kg}\\cdot\\text{m/s}}{0.20 \\, \\text{s}} = -15 \\, \\text{N} $$",
        "Many people intuitively guess they will weigh the same because they balanced. However, the shorter piece with the bristles is much heavier. It balances the longer, lighter handle because torque":
            "Balance does not imply equal masses. The heavier bristle region can balance the longer, lighter handle because torque",
        "Engineers use gyroscopes to stabilize spacecraft. How does a person riding a bicycle utilize similar principles of rotational dynamics to stay upright?":
            "A moving bicycle is stabilised mainly through steering geometry, tyre contact forces, and rider control, with wheel angular momentum contributing. How does this differ from an actively controlled spacecraft gyroscope?",
    },
    "science/11-waves-signals/overview.md": {
        "**Phase ($\\phi$)**: The position of a point in time (instant) on a waveform cycle.":
            "**Phase ($\\phi$)**: The angular coordinate locating a sinusoidal oscillation within its cycle relative to a reference.",
        "For underdamped systems, the solution is an exponentially decaying oscillation:\n$$ x(t) = A_0 e^{-\\frac{b}{2m}t} \\cos(\\omega_d t + \\phi) $$":
            "For underdamped systems, the solution is an exponentially decaying oscillation:\n$$ x(t) = A_0 e^{-\\frac{b}{2m}t} \\cos(\\omega_d t + \\phi), \\qquad \\omega_d=\\sqrt{\\frac{k}{m}-\\left(\\frac{b}{2m}\\right)^2}. $$",
        "When waves interfere destructively in one region, they interfere constructively in another, redistributing the energy in space.":
            "Local cancellation of displacement or field amplitude does not destroy energy; the energy balance depends on flux, reflection, storage, and the complete boundary conditions.",
    },
    "science/11-waves-signals/technology.md": {
        "When the weak signal photons pass by, they stimulate the ions to emit identical photons, amplifying the wave optically.":
            "The signal stimulates emission into the guided optical modes, coherently amplifying the field while adding unavoidable amplifier noise.",
        "**bandwidth** (data rate, e.g., Terabits per second)":
            "available channel bandwidth and achievable data rate (distinct quantities linked by modulation, coding, and signal-to-noise ratio)",
    },
    "science/11-waves-signals/explore.md": {
        "If you shine a red laser pointer and a blue laser pointer through the same glass prism, which beam will bend (refract) more?":
            "In a ray-optics simulation using the same prism material, which wavelength—red or blue—has the larger refractive index and bends more?",
    },
    "science/12-fluids-materials/overview.md": {
        "In a steady, incompressible, frictionless flow along a streamline, the total mechanical energy of the fluid is conserved. This is expressed by Bernoulli's principle. As a fluid moves through a constriction, its velocity must increase to conserve mass (continuity equation). Because kinetic energy increases, the pressure energy must decrease to conserve total energy. For a specified streamline":
            "For a specified steady-flow model, conservation of mass and the mechanical-energy equation relate area, density, velocity, pressure, elevation, shaft work, and losses. For a specified streamline",
        "A complete explanation requires Newton's laws, the Coanda effect, and the downward deflection of the airflow (downwash).":
            "A complete analysis uses the velocity field and boundary conditions to obtain surface pressure and shear, whose integrated force corresponds to the momentum change of the airflow.",
        "This is valid when the physical dimensions of the system are much larger than the mean free path of the molecules.":
            "This is valid when characteristic lengths are large compared with the molecular, granular, or microstructural scales relevant to the constitutive model.",
    },
    "science/12-fluids-materials/technology.md": {
        "- **Fatigue Limit:** Structures subjected to cyclic loading (like an aircraft pressurising and depressurising) must be designed so that operating stresses do not cause microscopic cracks to grow over time.":
            "- **Fatigue and damage tolerance:** Cyclic loading can grow cracks below yield stress. Some materials show an endurance limit over a specified test regime, while others require finite-life and crack-growth assessment.",
        "Smooth pipe interiors and laminar flow regimes reduce the energy required for pumping.":
            "Pumping power depends on required flow rate, geometry, roughness, viscosity, fittings, and flow regime; engineers minimise irreversible head loss subject to performance constraints.",
    },
    "science/12-fluids-materials/explore.md": {
        "blow air strongly between them": "direct a gentle airflow between them",
        "why a fluid accelerating through a narrow pipe must experience a drop in pressure":
            "under which assumptions a speed increase through a narrowing is accompanied by lower static pressure, and when pumps, elevation, losses, or compressibility change that conclusion",
        "how does this structure prevent your legs from shattering when you jump?":
            "how does this hierarchical structure combine stiffness, toughness, and damage resistance under ordinary loading?",
        "Elasticity is about atomic bonds stretching; plasticity is about atomic planes sliding past one another.":
            "Elasticity is reversible deformation described by a constitutive response; plasticity is irreversible deformation produced by mechanisms such as dislocation motion in crystals, molecular rearrangement in polymers, or damage in composites.",
    },
}


def source_match(text: str):
    return re.search(r"(?m)^#{1,2} \d+\. Sources\s*$", text)


def insert_boundaries(text: str, module: str) -> str:
    if "## Phase 7 review boundaries and validity limits" in text:
        return text
    marker = source_match(text)
    if marker:
        return text[: marker.start()] + phase7.BOUNDARIES[module].rstrip() + "\n\n" + text[marker.start():]
    return text.rstrip() + "\n\n" + phase7.BOUNDARIES[module].rstrip() + "\n\n## 11. Sources\n"


def replace_sources(text: str, module: str) -> str:
    pattern = re.compile(r"(?ms)^(#{1,2} \d+\. Sources\s*\n).*\Z")
    match = pattern.search(text)
    if not match:
        text = text.rstrip() + "\n\n## 11. Sources\n"
        match = pattern.search(text)
    assert match is not None
    return pattern.sub(match.group(1) + "\n" + phase7.SOURCES[module].rstrip() + "\n", text)


_original_transform = phase7.transform


def transform(path, module):
    text, notes = _original_transform(path, module)
    rel = path.relative_to(phase7.ROOT).as_posix()

    for old, new in ALIASES.items():
        text = text.replace(old, new)

    for old, new in FINAL_EXACT.get(rel, {}).items():
        text = text.replace(old, new)

    if rel == "science/08-energy-thermodynamics/explore.md":
        safe_activity = (
            "*   **Elastocaloric model:** Use published temperature–extension data "
            "or a classroom simulation for a rubber elastomer. Plot the qualitative "
            "temperature response during rapid extension, thermal equilibration, and "
            "release. Do not snap stretched bands near the face or skin."
        )
        text = re.sub(
            r"(?ms)^\*   \*\*The Rubber Band Refrigerator:\*\*.*?(?=\n\*   \*\*Online Simulation:)",
            safe_activity,
            text,
        )

    text = re.sub(r"(?m)^(#{1,2} \d+\. Sources\s*)\n{3,}", r"\1\n\n", text)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return text, notes


phase7.insert_boundaries = insert_boundaries
phase7.replace_sources = replace_sources
phase7.transform = transform

if __name__ == "__main__":
    raise SystemExit(phase7.main())
