#!/usr/bin/env python3
"""Apply the Phase 10 synthesis reconciliation deterministically."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "synthesis" / "phase-10-canonical-graph.json"
DATE = "2026-07-26"

PATHWAYS = (
    "pathways/atoms-to-computers.md",
    "pathways/biology-to-biotechnology.md",
    "pathways/chemistry-to-materials-and-batteries.md",
    "pathways/data-to-ai-and-automation.md",
    "pathways/fields-to-electric-power.md",
    "pathways/waves-to-global-communication.md",
)
CONCEPTS = (
    "concepts/cause-and-effect.md",
    "concepts/energy-and-matter.md",
    "concepts/patterns.md",
    "concepts/scale-proportion-and-quantity.md",
    "concepts/stability-and-change.md",
    "concepts/structure-and-function.md",
    "concepts/systems-and-models.md",
)
MAPS = (
    "maps/foundations-map.md",
    "maps/science-to-technology-map.md",
    "maps/complete-dependency-map.md",
)
SYNTHESIS_FILES = PATHWAYS + CONCEPTS + MAPS

BOUNDARY = """## Phase 10 synthesis boundaries

- This document is a reviewed route or crosscutting synthesis, not proof that one mechanism, architecture, or historical sequence is inevitable.
- Every equation, quantity, and causal claim inherits the assumptions and validity limits stated in the linked reviewed modules.
- Technology performance depends on architecture, implementation, operating conditions, measurement boundary, lifecycle, safety, security, and human organisation.
- `Reviewed` records focused reconciliation; it does not mean independently certified or release-ready.
"""

REPLACEMENTS: dict[str, tuple[tuple[str, str], ...]] = {
    "pathways/atoms-to-computers.md": (
        ("This pathway traces the complete dependency chain from atomic physics to a functioning digital computer.", "This pathway traces one defensible dependency route from atomic physics to programmable computing; other material, device, circuit, and architectural routes are possible."),
        ("their discrete energy levels broaden into continuous *bands*. The gap between the valence band (filled) and conduction band (empty) determines whether the material is a conductor, semiconductor, or insulator.", "their allowed electronic states form bands separated by gaps. Occupancy, Fermi level, temperature, disorder, dimensionality, contacts, and scattering jointly determine transport; a band-gap value alone does not universally classify every material."),
        ("The *band gap* $E_g$ — a single energy value that characterises the material's electrical behaviour. For silicon, $E_g \\approx 1.1$ eV at room temperature.", "The *band gap* $E_g$ — a useful material parameter whose value depends on temperature, composition, strain, structure, and measurement convention. It informs transport but does not by itself determine device behaviour."),
        ("The *diode* — a two-terminal device that conducts current in one direction (forward bias) and blocks it in the other (reverse bias). Its behaviour is captured by the Shockley equation: $I = I_0(e^{V/nV_T} - 1)$.", "The *diode* — a nonlinear two-terminal device whose forward injection, reverse leakage, capacitance, recombination, resistance, and breakdown depend on structure and operating regime. The Shockley equation is an ideal model under restricted assumptions, not a universal device law."),
        ("Forward voltage drop ($\\sim 0.6$ V for silicon) wastes energy.", "Forward voltage depends on current, area, temperature, material, structure, and series resistance, so conduction loss must be evaluated at a specified operating point."),
        ("Above the threshold voltage $V_{th}$, an inversion layer forms and current flows; below it, the channel is off.", "Gate bias changes surface potential and channel charge continuously. Threshold voltage is an extraction and compact-model parameter; subthreshold current, leakage, contacts, capacitance, and short-channel effects prevent a perfectly hard on/off boundary."),
        ("The *binary switch* — the transistor is treated as either fully on (logic 1) or fully off (logic 0), ignoring the analogue transition region.", "The *binary abstraction* — circuits assign voltage ranges and timing windows to logical states while device current remains analogue and continuous. Noise margins, delay, leakage, and metastability bound the abstraction."),
        ("a single hardware design that can execute any algorithm expressed in its instruction set", "A programmable architecture that executes instruction sequences within its ISA, memory, timing, numerical, and computability limits"),
        ("each running program behaves as if it has exclusive access to a complete computer", "process, virtual-memory, container, or virtual-machine abstractions provide selected resource and isolation views whose guarantees depend on hardware, kernel, configuration, and implementation"),
    ),
    "pathways/biology-to-biotechnology.md": (
        ("enables faithful replication by template-directed polymerisation", "supports high-fidelity template-directed replication together with proofreading, repair, and residual error"),
        ("Biological regulatory circuits are robust (evolved redundancy) but difficult to rewire.", "Biological regulation can be robust in some contexts and fragile in others; redundancy, feedback, burden, stochasticity, history, and host physiology all affect rewiring."),
        ("the ability to modify any gene in any organism by simply designing a 20-nucleotide guide sequence", "programmable nucleic-acid targeting whose feasible targets depend on recognition constraints, chromatin or accessibility, delivery, repair pathway, cell state, off-target activity, and validation"),
        ("make a double-strand break at a precise genomic location", "create a targeted DNA lesion or recruit an editing activity at a selected locus with nonzero uncertainty and context-dependent outcomes"),
        ("Flux balance analysis (FBA) models cellular metabolism as a linear programming problem, predicting which genetic changes will redirect carbon and energy flow toward the target product.", "Flux balance analysis represents steady-state stoichiometric constraints and an assumed objective as a linear programme. It identifies feasible or optimal model fluxes; it does not by itself predict regulation, kinetics, toxicity, or actual genetic outcomes."),
        ("Scaling from laboratory flasks (mL) to industrial bioreactors (10,000–200,000 L)", "Scaling from laboratory cultures to pilot and production bioreactors"),
        ("Larger bioreactors have worse mass transfer (oxygen, nutrients) due to lower surface-area-to-volume ratio.", "Scale-up changes mixing time, gas transfer, heat removal, gradients, shear, sensor placement, contamination risk, and control authority; no single geometric ratio determines performance."),
    ),
    "pathways/chemistry-to-materials-and-batteries.md": (
        ("The type and strength of bonding determine melting point, hardness, electrical conductivity, and solubility.", "Bonding, composition, structure, defects, phase, microstructure, temperature, environment, and measurement jointly influence melting, mechanics, transport, and solubility."),
        ("Metals for conductivity, ceramics for hardness, polymers for flexibility — each choice follows from bonding character.", "Material classes contain broad internal variation; selection requires measured properties, processing history, geometry, environment, reliability, and lifecycle constraints rather than class labels alone."),
        ("Equilibrium phase diagrams assume infinite time for diffusion.", "Equilibrium phase diagrams describe stable or constrained-equilibrium states under stated variables; finite-rate paths require kinetic, nucleation, transport, and metastability models."),
        ("Direct conversion of chemical energy to electrical energy without the intermediate step of heat (bypassing Carnot limitations). Fuel cells and batteries exploit this to achieve higher theoretical efficiency than heat engines.", "Electrochemical devices are not heat engines, so the Carnot expression is not their direct efficiency limit. Their reversible work is constrained by Gibbs free energy, while kinetics, transport, resistance, auxiliary systems, and operating strategy reduce realised efficiency."),
        ("give it the highest theoretical specific energy among practical anode materials", "make lithium-based systems attractive for high specific energy, while usable performance depends on the complete cell chemistry, inactive materials, voltage window, safety, and cycling constraints"),
        ("Individual electrochemical cells ($\\sim 3.6$ V, limited capacity)", "Individual cells with chemistry- and state-dependent voltage and capacity"),
        ("Scaling from a single cell to a 100 kWh automotive battery pack or a GWh grid storage installation", "Scaling from a single cell to modules, packs, and stationary storage systems"),
        ("Achieving >500 Wh/kg at the cell level while maintaining >1000 cycles and acceptable safety — the threshold for electric aviation and affordable grid storage.", "Improving usable energy, power, lifetime, safety, manufacturability, cost, temperature range, and recyclability together; application thresholds differ and must be stated explicitly."),
        ("The path from laboratory breakthrough to manufacturable product typically takes 10–20 years.", "The path from laboratory result to qualified production is uncertain and depends on reproducibility, scale-up, supply chain, standards, safety, economics, and application requirements."),
    ),
    "pathways/data-to-ai-and-automation.md": (
        ("Analogue-to-digital converters (ADCs) sample these signals at discrete intervals (Nyquist criterion: $f_s \\geq 2f_{max}$)", "Analogue-to-digital converters sample and quantise conditioned signals. The familiar $f_s>2f_{max}$ result assumes a band-limited signal and suitable anti-alias filtering; sampling, aperture, jitter, noise, range, and calibration remain"),
        ("stored in standardised formats, decoupled from the specific sensors and conditions that produced it", "stored with schema, provenance, consent or rights, calibration, sampling, missingness, transformation history, and deployment context; it must not be detached from how it was produced"),
        ("The trained model generalises (makes useful predictions on unseen data) if it has learned the underlying structure rather than memorising noise.", "Generalisation is performance under a stated target distribution and evaluation protocol. It can fail through shift, leakage, confounding, unstable labels, feedback, or strategic behaviour even when training error is low."),
        ("More data generally reduces variance but increases computational cost.", "Additional data helps only when its quality, relevance, rights, coverage, dependence structure, and labels support the intended task; it can also amplify bias or shift."),
        ("Achieving human-level or superhuman performance on perceptual tasks", "Improving performance on specified benchmarks and operational tasks"),
        ("Deep networks require massive datasets and compute (training GPT-scale models costs millions of dollars in energy and hardware).", "Resource requirements vary by task, architecture, data, hardware, precision, optimisation, reuse, and accounting boundary; fixed cost claims age quickly and omit deployment and failed experiments."),
        ("available at scale, in real time, to billions of users and devices simultaneously, with acceptable latency (<100 ms for interactive applications)", "available to a defined service population under stated latency, throughput, reliability, privacy, energy, and cost objectives"),
        ("The *control policy* $\\pi(s) \\to a$ — a mapping from observed state $s$ to action $a$", "The *control policy* $\\pi(o,\\hat{x},r,c)\\to a$ — a mapping from observations, estimated state, reference, and constraints to an action"),
        ("sense → perceive → plan → act → monitor", "measure → condition → estimate → decide → act → verify, with protection, human authority, and fallback outside the normal loop"),
        ("Safety certification requires demonstrating reliability orders of magnitude beyond human performance.", "Assurance requires scenario coverage, hazard analysis, uncertainty, independent protection, human factors, cybersecurity, monitoring, incident response, and evidence appropriate to the regulated application."),
    ),
    "pathways/fields-to-electric-power.md": (
        ("The Lorentz force on charge carriers in the conductor is the microscopic mechanism.", "Induction is described by the Maxwell–Faraday relation and, for moving conductors, the magnetic part of the Lorentz force; the appropriate description depends on geometry and reference frame."),
        ("Any mismatch causes destructive currents.", "Loss of synchronism, excessive angle or frequency deviation, faults, and protection interactions can produce damaging currents or instability; acceptable operating regions depend on machine and grid models."),
        ("Providing the mechanical torque to spin generators at thousands of MW scale. Combined-cycle gas turbines achieve ~60% thermal efficiency", "Providing mechanical work over application-dependent power scales. Combined cycles can improve efficiency by using exhaust heat, but performance depends on ambient conditions, load, equipment, fuel, cooling, and accounting boundary"),
        ("Transmitting gigawatts of power over hundreds of kilometres with losses below 5%.", "Transmitting large power flows over distance while managing resistive, dielectric, corona, reactive, conversion, stability, congestion, protection, and right-of-way constraints."),
        ("supply must instantaneously equal demand (plus losses) at all times, because electrical energy cannot be stored in the grid itself", "active-power imbalance changes energy stored in rotating masses, fields, converters, storage, and responsive demand while frequency, voltage, flows, and controls evolve across timescales; operation requires balance within dynamic and protection limits"),
        ("Frequency is the real-time indicator of balance", "Frequency is an important indicator of active-power dynamics but not a complete description of network state"),
        ("spinning reserves (generators running below capacity, ready to ramp), which wastes fuel", "reserves and headroom that carry opportunity, efficiency, wear, emissions, and cost trade-offs"),
    ),
    "pathways/waves-to-global-communication.md": (
        ("Lower frequencies propagate farther (less atmospheric absorption, better diffraction around obstacles) but carry less information (bandwidth is proportional to frequency). Higher frequencies offer more bandwidth but require line-of-sight paths", "Propagation and available bandwidth depend on allocation, antenna size, environment, absorption, diffraction, scattering, regulation, coding, power, and geometry. Frequency alone does not set information capacity or guarantee line of sight"),
        ("The *channel* — a defined frequency band carrying a defined data rate, independent of the physical medium.", "The *channel model* — a stated probabilistic or deterministic relation between transmitted and received signals, including bandwidth, noise, interference, fading, memory, feedback, and decoding assumptions."),
        ("Total internal reflection confines light within a glass fibre", "Refractive-index structure supports guided electromagnetic modes within a glass fibre; ray total-internal-reflection language is a useful geometric approximation in some regimes"),
        ("Transmitting terabits per second over thousands of kilometres (submarine cables spanning oceans) with regeneration only every 50–80 km", "Transmitting high aggregate rates over long terrestrial or submarine routes using wavelength multiplexing, amplification, coherent detection, coding, dispersion management, repeaters, and route-specific engineering"),
        ("Analogue signals are sampled (Nyquist theorem: sample at $\\geq 2f_{max}$)", "Band-limited signals can be sampled without aliasing above the relevant Nyquist rate only with the stated spectral assumptions and practical anti-alias filtering"),
        ("approach the Shannon limit — transmitting near the theoretical maximum rate with arbitrarily low error probability", "can approach information-theoretic bounds for stated channel models as block length and complexity grow, while finite systems trade error probability, latency, energy, rate, and implementation cost"),
        ("Routers forward packets independently along available paths, and the destination reassembles them in order.", "Routers forward IP datagrams using routing and forwarding state. Ordering, retransmission, congestion control, security, and application semantics are handled by other layers or protocols when required."),
        ("Any device with an IP address can communicate with any other", "IP supplies a common network-layer addressing and forwarding model, while reachability still depends on routing, policy, translation, firewalls, naming, identity, and application protocols"),
        ("allows each layer to evolve independently", "reduces coupling but does not eliminate cross-layer dependencies, ossification, shared failure modes, or coordinated change"),
        ("5G NR achieves multi-gigabit peak rates using millimetre-wave spectrum and massive MIMO.", "Modern cellular systems combine licensed spectrum, coding, scheduling, antenna arrays, handover, power control, backhaul, and deployment density; realised rate and coverage are environment- and load-dependent."),
    ),
    "concepts/cause-and-effect.md": (
        ("is the relationship in which one event (the cause) produces another event (the effect) through a specific mechanism", "describes how changing one factor would change an outcome under a stated causal model, intervention, population, timescale, and set of background conditions"),
        ("establishing causality requires demonstrating that the cause precedes the effect, that a plausible mechanism connects them, and that the relationship holds under controlled variation", "causal identification requires assumptions and evidence that distinguish intervention effects from confounding, selection, reverse direction, measurement error, and chance; temporal order and mechanism alone are not sufficient"),
        ("All scientific explanation is ultimately causal", "Many scientific explanations are causal, while others classify, describe, unify, constrain, or derive patterns without identifying a manipulable cause"),
        ("force is the cause, acceleration is the effect", "the equation relates net force and acceleration within a Newtonian model and inertial frame; causal interpretation depends on the chosen intervention, system boundary, and constraints"),
        ("This circular causality produces oscillations (Lotka–Volterra cycles).", "The classical Lotka–Volterra model has idealised neutrally stable closed orbits; real predator–prey dynamics can damp, grow, shift, or behave differently when additional mechanisms are included."),
        ("adjusts the cause (actuator output) to minimise that error", "computes an actuator command from error and other signals subject to dynamics, delay, saturation, safety, and objective definitions"),
    ),
    "concepts/energy-and-matter.md": (
        ("**Matter** is anything that has mass and occupies space", "**Matter** refers to physical constituents such as atoms, molecules, condensed phases, plasmas, and particles whose properties are described by the applicable physical theory"),
        ("**Energy** is the capacity to do work or transfer heat", "**Energy** is a conserved state quantity associated with time-translation symmetry in closed physical descriptions; work and heat are transfer modes, not substances stored in a container"),
        ("if you know the energy input and the system boundary, you know the energy output regardless of the internal pathway", "balances constrain totals, but prediction also requires storage, accumulation, transfer modes, losses, sign conventions, state, and measurement uncertainty"),
        ("both move toward the iron-56 peak", "many energy-releasing nuclear reactions move nuclei toward the high-binding-energy region near iron and nickel, subject to reaction pathways and conservation laws"),
        ("The matter (ATP molecule) carries energy in its phosphoanhydride bonds", "ATP hydrolysis can drive coupled processes because the complete reaction has a favourable Gibbs free-energy change under cellular conditions; no isolated bond contains a packet of usable energy"),
        ("Earth receives $\\sim 1361$ W/m² of solar radiation and re-emits an equal amount as infrared radiation at steady state. Greenhouse gases absorb and re-emit some of this outgoing radiation, reducing the effective emissivity", "Earth's top-of-atmosphere energy budget depends on solar input, albedo, spectral absorption and emission, clouds, circulation, storage, and effective emission temperature. Greenhouse gases alter wavelength-dependent optical depth and emission levels rather than acting as a simple reduced-emissivity blanket"),
        ("Smelting aluminium from bauxite requires $\\sim 13$ kWh/kg", "Primary aluminium production is electricity- and process-intensive, with values depending on technology, feedstock, electricity, boundaries, yield, and allocation"),
    ),
    "concepts/patterns.md": (
        ("that signals an underlying mechanism or constraint", "that may suggest an underlying mechanism, constraint, data-generating process, or artefact and therefore requires testing"),
        ("Without pattern recognition there is no generalisation, and without generalisation there is no science.", "Pattern recognition supports generalisation, but valid science also requires measurement, uncertainty, comparison, mechanism, and tests against alternatives."),
        ("This pattern is not arbitrary; it minimises the phenotypic effect of point mutations and reflects the evolutionary optimisation of translation fidelity.", "Codon redundancy has structured consequences for translation, mutation, expression, and error tolerance, but its present form should not be reduced to one universal optimisation objective."),
        ("Ecosystems, metabolic networks, and the internet all exhibit degree distributions that follow approximate power laws", "Some biological, ecological, technological, and social networks show heavy-tailed or approximately power-law features over limited ranges, while others do not; model choice and sampling strongly affect the conclusion"),
        ("scale-free networks tolerate random failures but are vulnerable to targeted attacks on hubs", "robustness depends on topology, weights, direction, dynamics, dependency, repair, common-cause failure, and the attack or failure model; degree distribution alone is insufficient"),
    ),
    "concepts/scale-proportion-and-quantity.md": (
        ("Physical laws do not change with scale, but their *relative importance* does.", "Fundamental descriptions and effective models apply over stated regimes; as scale changes, new degrees of freedom, approximations, fluctuations, interfaces, and dominant dimensionless ratios can become relevant."),
        ("For macroscopic objects, $\\lambda \\sim 10^{-35}$ m", "For ordinary macroscopic centre-of-mass motion the de Broglie wavelength is generally far below experimental resolution, whereas microscopic systems can require quantum descriptions"),
        ("at scales below ~5 nm, quantum tunnelling through the gate oxide becomes significant, and classical MOSFET models break down", "as dimensions, fields, barriers, and carrier numbers change, tunnelling, confinement, variability, contacts, electrostatics, and heat can require quantum-aware and nanoscale compact models; no one node label defines the transition"),
        ("Propagating uncertainties through calculations requires understanding how proportional errors combine — linearly for sums, quadratically for products", "Uncertainty propagation depends on the measurement model, derivatives or simulation, covariance, distributions, nonlinearity, and reporting convention; simple independent-error formulas are special cases"),
    ),
    "concepts/stability-and-change.md": (
        ("is the tendency of a system to remain in or return to a particular state when subjected to small perturbations", "is a property of a specified state, trajectory, distribution, or operating set under defined perturbations, dynamics, norms, timescales, and boundaries"),
        ("Small perturbations increase $G$, and the system spontaneously returns to the minimum", "A local Gibbs-energy minimum is a thermodynamic stability criterion under fixed temperature and pressure, but kinetics, constraints, nucleation, transport, and finite-system fluctuations determine the observed path and timescale"),
        ("Below this threshold, small lateral deflections are restored by elastic forces. Above it, the column buckles", "Euler buckling is an ideal bifurcation model for a slender elastic column with stated supports, loading, geometry, imperfections, and material assumptions; real failure can occur earlier or by other modes"),
        ("Punctuated equilibrium — long periods of stasis interrupted by rapid change — reflects", "Observed evolutionary tempo can involve stasis and comparatively rapid change, but explanations require fossil resolution, population processes, environment, selection, drift, migration, and development rather than one universal stability mechanism"),
        ("Loss of resilience (shrinking basin of attraction) often precedes catastrophic change.", "Alternative states and basins are model-dependent; proposed early-warning signals can fail and require system-specific evidence, uncertainty, and competing explanations."),
        ("Removing the control system causes immediate instability.", "Loss of control can leave some systems stable, degraded, unsafe, or unstable depending on passive dynamics, protection, redundancy, stored energy, operating point, and failure mode."),
    ),
    "concepts/structure-and-function.md": (
        ("The principle that *structure determines function*", "The relationship between structure and function"),
        ("if you understand how something is built, you can predict what it will do", "structure constrains possible behaviour, but function also depends on material state, environment, history, dynamics, interfaces, control, and definition of the task"),
        ("can predict its catalytic activity", "can generate hypotheses about catalytic activity that still require thermodynamic, kinetic, environmental, and experimental validation"),
        ("The spatial distribution of electrons around a nucleus (orbitals, shells, subshells) determines", "Electronic states, occupancy, interactions, molecular environment, and symmetry help explain"),
        ("The function (oxygen transport) depends entirely on the structure", "Oxygen transport depends on molecular structure together with concentration, binding equilibria, allostery, cellular environment, flow, and physiology"),
        ("Face-centred cubic (FCC) metals like copper are ductile because their close-packed planes allow dislocation glide. Body-centred cubic (BCC) metals like iron are harder but more brittle at low temperatures.", "Crystal structure affects available deformation mechanisms, but ductility, strength, and fracture also depend on composition, temperature, rate, texture, grain structure, defects, processing, and environment."),
        ("The gate length determines switching speed and leakage current.", "Geometry contributes to electrostatics, capacitance, delay, leakage, variability, and contacts, while circuit and system performance also depend on interconnect, memory, architecture, packaging, workload, and thermal limits."),
    ),
    "concepts/systems-and-models.md": (
        ("A **system** is a set of interacting components bounded from its environment", "A **system** is a chosen set of entities, states, interactions, and boundaries used to answer a question or deliver a service; its boundary is an analytical and engineering decision"),
        ("All scientific understanding is mediated through models; all engineered artefacts are systems.", "Scientific and engineering reasoning uses multiple representations, measurements, theories, experiments, and models; none should be confused with the full physical or social reality."),
        ("succeeds for most engineering calculations", "is useful over a stated dilute-gas regime and fails when interactions, phase change, chemistry, or high density matter"),
        ("reveals the essential mechanism (delayed negative feedback)", "reveals consequences of one idealised interaction structure; real food webs can add density dependence, delay, seasonality, spatial structure, stochasticity, and adaptation"),
        ("only its input–output relationship matters", "input–output models can support analysis, but hidden state, nonlinearities, saturation, uncertainty, safety, and implementation may also matter"),
        ("The best model is the simplest one that captures the mechanism of interest.", "Model choice balances purpose, adequacy, identifiability, uncertainty, interpretability, cost, and consequence; simplicity is valuable but not an automatic optimum."),
    ),
}

FOUNDATIONS_MAP = """---
title: "Foundations Map"
slug: map-foundations
domain: map
status: reviewed
prerequisites: []
connections: []
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Foundations Map

This map shows the canonical prerequisite direction among Modules 01–05. Every prerequisite arrow points from the knowledge assumed first to the module that depends on it.

```mermaid
graph TD
    M01["01 Scientific Reasoning"]
    M02["02 Measurement & Uncertainty"]
    M03["03 Mathematical Models"]
    M04["04 Probability & Statistics"]
    M05["05 Computation & Algorithms"]

    M01 -->|prerequisite for| M02
    M01 -->|prerequisite for| M03
    M01 -->|prerequisite for| M04
    M03 -->|prerequisite for| M04
    M03 -->|prerequisite for| M05
    M04 -->|prerequisite for| M05
```

## Canonical direct prerequisites

| Module | Direct prerequisites |
| --- | --- |
| 01 Scientific Reasoning | None |
| 02 Measurement & Uncertainty | 01 |
| 03 Mathematical Models | 01 |
| 04 Probability & Statistics | 01, 03 |
| 05 Computation & Algorithms | 03, 04 |

## Reading rule

`A -->|prerequisite for| B` means learners should normally understand A before B. Measurement data can inform models and algorithms can implement models, but those are non-prerequisite relations and are intentionally omitted from this prerequisite-only map.

""" + BOUNDARY

SCIENCE_TECH_MAP = """---
title: "Science to Technology Map"
slug: map-science-to-technology
domain: map
status: reviewed
prerequisites: []
connections: []
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Science to Technology Map

This map shows selected enabling and constraining relationships between reviewed science and technology modules. These are not a substitute for the canonical prerequisite graph.

```mermaid
graph LR
    M06["06 Matter & Quantum"]
    M07["07 Chemical Bonding"]
    M08["08 Energy & Thermodynamics"]
    M09["09 Motion & Forces"]
    M10["10 Electricity & Magnetism"]
    M11["11 Waves & Signals"]
    M12["12 Fluids & Materials"]
    M13["13 Cells & Bioenergetics"]
    M14["14 DNA & Evolution"]
    M15["15 Ecosystems & Complex Systems"]
    M16["16 Earth & Planetary Systems"]
    M17["17 Materials & Manufacturing"]
    M18["18 Semiconductors & Electronics"]
    M19["19 Software & AI"]
    M20["20 Sensors, Control & Infrastructure"]

    M06 -->|enables| M17
    M06 -->|enables| M18
    M07 -->|enables| M17
    M08 -->|constrains| M17
    M08 -->|constrains| M20
    M09 -->|constrains| M17
    M10 -->|enables| M18
    M10 -->|enables| M20
    M11 -->|enables| M18
    M11 -->|enables| M20
    M12 -->|enables| M17
    M12 -->|constrains| M20
    M13 -->|enables| M17
    M14 -->|enables| M17
    M15 -->|models| M19
    M16 -->|measures| M20
    M17 -->|enables| M18
    M18 -->|enables| M19
    M18 -->|enables| M20
    M19 -->|controls| M20
```

## Relationship vocabulary

| Label | Meaning |
| --- | --- |
| enables | Supplies a mechanism, material, or capability used by the target. |
| constrains | Supplies limits, conservation laws, or operating boundaries. |
| measures | Supplies measurement or inference methods. |
| models | Supplies representations or computational methods. |
| controls | Supplies decision, feedback, or coordination logic. |

A relation is selective rather than exhaustive. Technology also depends on manufacturing, institutions, standards, maintenance, operators, safety, security, economics, and lifecycle governance.

""" + BOUNDARY


def complete_map(manifest: dict[str, object]) -> str:
    modules = manifest["modules"]
    assert isinstance(modules, dict)
    labels = {
        "01-scientific-reasoning": "01 Scientific Reasoning",
        "02-measurement-uncertainty": "02 Measurement & Uncertainty",
        "03-mathematical-models": "03 Mathematical Models",
        "04-probability-statistics": "04 Probability & Statistics",
        "05-computation-algorithms": "05 Computation & Algorithms",
        "06-matter-quantum": "06 Matter & Quantum",
        "07-chemical-bonding": "07 Chemical Bonding",
        "08-energy-thermodynamics": "08 Energy & Thermodynamics",
        "09-motion-forces": "09 Motion & Forces",
        "10-electricity-magnetism": "10 Electricity & Magnetism",
        "11-waves-signals": "11 Waves & Signals",
        "12-fluids-materials": "12 Fluids & Materials",
        "13-cells-bioenergetics": "13 Cells & Bioenergetics",
        "14-dna-evolution": "14 DNA & Evolution",
        "15-ecosystems-complex-systems": "15 Ecosystems & Complex Systems",
        "16-earth-planetary": "16 Earth & Planetary Systems",
        "17-materials-manufacturing": "17 Materials & Manufacturing",
        "18-semiconductors-electronics": "18 Semiconductors & Electronics",
        "19-software-ai": "19 Software & AI",
        "20-sensors-control-infrastructure": "20 Sensors, Control & Infrastructure",
    }
    ids = {module: f"M{module[:2]}" for module in modules}
    lines = [
        "---", 'title: "Complete Dependency Map"', "slug: map-complete-dependency", "domain: map",
        "status: reviewed", "prerequisites: []", "connections: []", f"last_reviewed: {DATE}",
        "content_license: CC-BY-4.0", "---", "", "# Complete Dependency Map", "",
        "This map is generated from the Phase 10 canonical graph. Every arrow points from a direct prerequisite to the dependent module.", "",
        "```mermaid", "graph TD",
    ]
    for module, label in labels.items():
        lines.append(f'    {ids[module]}["{label}"]')
    lines.append("")
    for target, prereqs in modules.items():
        assert isinstance(prereqs, list)
        for source in prereqs:
            lines.append(f"    {ids[source]} -->|prerequisite for| {ids[target]}")
    lines.extend(["```", "", "## Canonical direct prerequisites", "", "| Module | Direct prerequisites |", "| --- | --- |"])
    for module, prereqs in modules.items():
        assert isinstance(prereqs, list)
        display = ", ".join(p[:2] for p in prereqs) if prereqs else "None"
        lines.append(f"| {labels[module]} | {display} |")
    lines.extend([
        "", "## Reading rule", "",
        "`A -->|prerequisite for| B` means A is assumed before B. Enabling, constraining, measuring, modelling, and controlling relations belong in the science-to-technology map and must not be confused with prerequisites.",
        "", BOUNDARY.rstrip(), "",
    ])
    return "\n".join(lines)


def update_frontmatter(text: str) -> str:
    text = re.sub(r"(?m)^status:\s*complete\s*$", "status: reviewed", text)
    text = re.sub(r"(?m)^last_reviewed:\s*.*$", f"last_reviewed: {DATE}", text, count=1)
    return text


def replace_known(text: str, pairs: tuple[tuple[str, str], ...], rel: str, errors: list[str]) -> str:
    for old, new in pairs:
        if new in text:
            continue
        if old not in text:
            errors.append(f"{rel}: expected legacy text missing: {old[:90]}")
            continue
        text = text.replace(old, new, 1)
    return text


def ensure_boundary(text: str) -> str:
    if "## Phase 10 synthesis boundaries" in text:
        return text
    source_match = list(re.finditer(r"(?m)^##\s+(?:\d+\.\s*)?Sources\s*$", text, re.I))
    if source_match:
        pos = source_match[-1].start()
        return text[:pos].rstrip() + "\n\n" + BOUNDARY + "\n" + text[pos:]
    return text.rstrip() + "\n\n" + BOUNDARY


def project_state() -> str:
    return """# Project State

> Last updated: 2026-07-26

## Current phase

**Phase 10 Synthesis Reconciliation implemented on `agent/phase-10-synthesis-reconciliation`; coordinated validation and pull-request integration remain pending.**

The repository remains a material-first educational foundation. Software is intentionally deferred until synthesis, release validation, and governance are mature.

## Phase progress

| Phase | Scope | Status |
| --- | --- | --- |
| 0 | Vision and educational philosophy | Complete |
| 1 | Core knowledge inventory | First-draft inventory complete |
| 2 | Repository audit and hardening | Complete |
| 3 | Applied-material foundation | Implemented and validated |
| 4 | Core metadata normalization | Merged and validated |
| 5 | Legacy source-ledger repair | Merged and validated |
| 6 | Foundations scientific review | Merged and validated through PR #8 |
| 7 | Physical-science review | Merged and validated through PR #8 |
| 8 | Life and Earth systems review | Merged and validated through PR #9 |
| 9 | Technology review | Merged and validated through PR #10 |
| 10 | Synthesis reconciliation | Implemented on Phase 10 branch; coordinated validation pending |
| 11 | Controlled material expansion | Seed exemplars exist; expansion pending reviewed synthesis |
| 12 | Release candidate | Not started |
| 13 | Optional software layer | Deferred |

## Integration topology

`main` contains the reviewed Modules 01–20 after PR #10. The Phase 10 branch was created directly from that merged state and changes only synthesis, audit, state, and validation artifacts. No workflow automatically merges pull requests.

## Repository status on the Phase 10 branch

### Foundations Modules 01–05

- Modules 01–05: **Reviewed**;

### Physical Science Modules 06–12

- Modules 06–12: **Reviewed**;

### Phase 8 — Life and Earth Systems Modules 13–16

- Modules 13–16: **Reviewed**;

### Phase 9 Technology review implemented and merged through PR #10

- Modules 17–20: **Reviewed**;
- Modules 01–20: **Reviewed**;

### Reconciled synthesis layer

- 6 pathways: **Reviewed**;
- 7 crosscutting concepts: **Reviewed**;
- 3 knowledge maps: **Reviewed**;
- source ledger: **143 records**;
- no core or synthesis artifact is Complete.

## Historical continuity record

- Phase 9 Technology review implemented and validated on draft PR #10 before that pull request was merged.
- Historical pre-merge marker: `Technology review | Implemented and validated on PR #10; awaiting merge`.
- The Phase 9 central-ledger transition was 131 → 143 records.
- Phase 10 Synthesis reconciliation is the current branch-stage audit label.
- Permanent CI is read-only.
- no core module is Complete; synthesis artifacts also remain Reviewed pending Phase 12.

Reviewed means focused reconciliation has checked metadata, canonical identifiers, links, prerequisite direction, terminology, equations, claims, limitations, and status consistency. It does not mean independently certified or release-ready.

## Phase 10 result — Synthesis Reconciliation

Phase 10 establishes `synthesis/phase-10-canonical-graph.json` as the machine-readable synthesis contract. It reconciles:

1. the exact 20-module prerequisite graph;
2. arrow direction and relationship vocabulary;
3. six science-to-technology pathways;
4. seven crosscutting concepts;
5. three Mermaid maps;
6. status policy, terminology, equations, quantities, and links;
7. superseded claims identified during Modules 01–20 review;
8. the unchanged 143-record source baseline.

Major repairs include removing hard transistor thresholds, universal material stereotypes, unconstrained genome-editing claims, fixed AI deployment promises, instantaneous-grid simplifications, frequency-capacity shortcuts, energy-in-bonds language, universal scale-free-network claims, and deterministic structure–function reasoning.

## Validation

```bash
python3 scripts/apply_phase10_synthesis.py --check
python3 scripts/validate_phase10_synthesis.py
python3 scripts/validate_repo.py
python3 scripts/validate_experiences.py --strict
```

The Phase 10 gate requires all 16 synthesis files to be Reviewed, the canonical graph to match repository module prerequisites, all links to resolve, every prerequisite arrow to use `prerequisite for`, the source ledger to remain at 143 records, no synthesis completion claims, and no regression in Phase 4–9 validation.

## Next phase

Phase 11 may expand system dossiers, failure-atlas entries, investigations, and design challenges only from stable reviewed patterns. Phase 12 remains the strict repository-wide release candidate and the earliest point at which Reviewed artifacts may be considered for Complete status.

## Continuation instructions

Read `README.md`, `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, `AUDIT.md`, this file, and the phase reports. Keep synthesis, expansion, release validation, and software implementation in separate focused pull requests. Never promote material solely because a file exists or a structural check passes.
"""


def update_audit(text: str) -> str:
    text = text.replace("**Current action:** `INDEX.md` now reports all modules as Draft pending review.", "**Resolution:** Modules 01–20 are Reviewed after focused Phase 6–9 review; no module is Complete before the release gate.")
    text = text.replace("### Phase 5 — Synthesis reconciliation\n\nReconcile pathways, crosscutting concepts, maps, index entries, and source-ledger references against the reviewed modules.", "### Phase 5 — Synthesis reconciliation\n\n**Implemented in repository Phase 10.** Pathways, crosscutting concepts, maps, status, terminology, links, and prerequisite direction are reconciled against reviewed Modules 01–20 and a machine-readable canonical graph.")
    old = "> A structurally complete, connected first draft undergoing scientific and editorial review."
    new = "> A scientifically reviewed 20-module foundation with a reconciled synthesis layer, awaiting applied-material expansion, independent review, and strict release validation."
    text = text.replace(old, new)
    if "## Phase 10 synthesis disposition" not in text:
        text = text.rstrip() + "\n\n## Phase 10 synthesis disposition\n\n- A-001 through A-010 have repository-level resolutions or focused review artifacts.\n- A-011 and A-012 are addressed for the synthesis layer through canonical titles, identifiers, navigable links, and edge vocabulary.\n- A-013 is addressed through phase-specific reports, deterministic scripts, and read-only CI.\n- No synthesis document is Complete; final completion remains governed by Phase 12.\n"
    return text + ("" if text.endswith("\n") else "\n")


def update_readme(text: str) -> str:
    text = text.replace("Module sources remain in [`sources/source-ledger.md`](sources/source-ledger.md), which is undergoing normalization.", "Reviewed module sources are recorded in the normalized [`sources/source-ledger.md`](sources/source-ledger.md).")
    if "Phase 10 canonical synthesis graph" not in text:
        marker = "| `maps/` | Dependency and enabling-relationship maps |"
        text = text.replace(marker, marker + "\n| `synthesis/` | Phase-level canonical graphs and reconciliation contracts |")
        text = text.replace("GitHub Actions runs strict applied-material validation when relevant files change.", "GitHub Actions runs focused metadata, source, scientific-review, synthesis, and applied-material validation. The Phase 10 canonical synthesis graph is validated against Modules 01–20.")
    return text


def apply(write: bool) -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    changed: list[str] = []

    for rel in PATHWAYS + CONCEPTS:
        path = ROOT / rel
        original = path.read_text(encoding="utf-8")
        text = update_frontmatter(original)
        text = replace_known(text, REPLACEMENTS.get(rel, ()), rel, errors)
        text = ensure_boundary(text)
        text = text.rstrip() + "\n"
        if text != original:
            changed.append(rel)
            if write:
                path.write_text(text, encoding="utf-8")

    generated_maps = {
        "maps/foundations-map.md": FOUNDATIONS_MAP.rstrip() + "\n",
        "maps/science-to-technology-map.md": SCIENCE_TECH_MAP.rstrip() + "\n",
        "maps/complete-dependency-map.md": complete_map(manifest),
    }
    for rel, text in generated_maps.items():
        path = ROOT / rel
        original = path.read_text(encoding="utf-8")
        text = text.rstrip() + "\n"
        if text != original:
            changed.append(rel)
            if write:
                path.write_text(text, encoding="utf-8")

    top_updates = {
        "PROJECT_STATE.md": project_state(),
        "AUDIT.md": update_audit((ROOT / "AUDIT.md").read_text(encoding="utf-8")),
        "README.md": update_readme((ROOT / "README.md").read_text(encoding="utf-8")),
    }
    for rel, text in top_updates.items():
        path = ROOT / rel
        original = path.read_text(encoding="utf-8")
        text = text.rstrip() + "\n"
        if text != original:
            changed.append(rel)
            if write:
                path.write_text(text, encoding="utf-8")

    if errors:
        print("Phase 10 synthesis errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if not write and changed:
        print("Phase 10 synthesis is not applied:", file=sys.stderr)
        for rel in changed:
            print(f"- {rel}", file=sys.stderr)
        return 1
    print(f"Phase 10 synthesis {'updated' if write else 'is idempotent'}: {len(changed)} changed files.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return apply(args.write)


if __name__ == "__main__":
    raise SystemExit(main())
