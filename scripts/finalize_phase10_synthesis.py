#!/usr/bin/env python3
"""Apply the final editorial-scientific quality pass to Phase 10 synthesis files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REPLACEMENTS: dict[str, tuple[tuple[str, str], ...]] = {
    "pathways/atoms-to-computers.md": (
        (
            "**Engineering problem solved:** Identifying which elements have the right electronic properties (four valence electrons, moderate band gap) to serve as controllable conductors. Silicon and germanium emerge as candidates.",
            "**Engineering problem solved:** Identifying material systems whose electronic states, defects, interfaces, thermal behaviour, manufacturability, and supply constraints can support controllable devices. Silicon became dominant through a combination of suitable oxide chemistry, process maturity, abundance, and device performance rather than one valence-electron rule.",
        ),
        (
            "**Trade-off:** Quantum mechanics is exact but computationally intractable for many-electron atoms. Approximations (Hartree–Fock, density functional theory) trade accuracy for tractability.",
            "**Trade-off:** Many-electron calculations require approximations and numerical choices. Hartree–Fock, density-functional methods, empirical models, and experiments offer different balances of accuracy, interpretation, computational cost, and domain of validity.",
        ),
        (
            "**Trade-off:** Narrower band gaps increase intrinsic carrier concentration (more leakage current at high temperature). Wider band gaps require higher voltages to switch. Silicon's moderate gap is a compromise between switching voltage and thermal stability.",
            "**Trade-off:** Band gap, carrier statistics, mobility, breakdown field, contacts, defects, thermal conductivity, dielectric interfaces, and fabrication jointly shape leakage, voltage, speed, temperature range, and reliability. No single band-gap ordering determines the best device material.",
        ),
        (
            "**Engineering problem solved:** Amplification and switching with no moving parts, at speeds determined by carrier transit time across the channel (picoseconds for nanometre gates).",
            "**Engineering problem solved:** Amplification and switching in compact solid-state devices. Device and circuit delay depend on capacitance, resistance, carrier transport, contacts, interconnect, load, supply, geometry, and the chosen timing definition.",
        ),
        (
            "**Trade-off:** Smaller transistors switch faster and use less energy per switch, but suffer increased leakage current (quantum tunnelling through thin gate oxides) and greater variability in threshold voltage. This is the fundamental tension driving Moore's law and its eventual slowdown.",
            "**Trade-off:** Scaling can reduce some capacitances and increase density, but leakage, variability, electrostatics, interconnect, memory movement, heat, reliability, lithography, packaging, and cost can offset or reverse expected gains. Moore's observation is an economic and historical trend, not a device law.",
        ),
        (
            "**Trade-off:** CMOS draws significant power only during switching (dynamic power $P = \\alpha C V^2 f$), but static leakage grows as transistors shrink. Power density, not transistor count, is now the primary design constraint.",
            "**Trade-off:** The approximation $P_{dyn}=\\alpha C V^2 f$ describes selected switching losses at a stated boundary. Leakage, short-circuit current, clocks, memory, interconnect, I/O, data movement, workload, packaging, and cooling also matter; the dominant constraint depends on the system and operating point.",
        ),
        (
            "**Abstraction introduced:** The *stored-program computer* (von Neumann architecture) — instructions and data share the same memory, and the processor fetches, decodes, and executes instructions sequentially (with pipelining and parallelism for performance).",
            "**Abstraction introduced:** The *stored-program architecture* — instructions are represented as data and executed through an instruction-set interface. Implementations may use caches, pipelines, speculation, parallel units, accelerators, separate memory paths, or other organisations while preserving selected architectural behaviour.",
        ),
        (
            "**Trade-off:** The von Neumann bottleneck — memory bandwidth limits throughput because instructions and data compete for the same bus. Caches, out-of-order execution, and multi-core designs mitigate but do not eliminate this fundamental constraint.",
            "**Trade-off:** Computation, memory capacity, latency, bandwidth, coherence, communication, control flow, energy, and software locality interact. A shared instruction/data path is one possible bottleneck, not the only universal limit.",
        ),
        (
            "**Engineering problem solved:** Programmability and portability — software written once runs on any hardware that supports the same OS interface, and multiple programs coexist without interference.",
            "**Engineering problem solved:** Programmability, resource sharing, and conditional portability through specified language, ABI, runtime, operating-system, and hardware interfaces. Isolation and coexistence are engineered properties that can fail through defects, configuration, shared resources, or hostile inputs.",
        ),
    ),
    "pathways/data-to-ai-and-automation.md": (
        (
            "**Mechanism used:** Sensors convert physical quantities (temperature, pressure, light, acceleration, chemical concentration) into electrical signals. Analogue-to-digital converters sample and quantise conditioned signals. The familiar $f_s>2f_{max}$ result assumes a band-limited signal and suitable anti-alias filtering; sampling, aperture, jitter, noise, range, and calibration remain and quantise them into binary numbers. The result is a digital data stream — a sequence of numbers representing the state of the physical world.",
            "**Mechanism used:** Sensors and signal-conditioning chains map physical variables to measurable signals with finite bandwidth, noise, drift, calibration, and failure modes. Analogue-to-digital converters sample and quantise those signals. The familiar $f_s>2f_{max}$ condition assumes a band-limited signal and suitable anti-alias filtering; aperture, jitter, range, resolution, timing, and calibration still limit the resulting digital record.",
        ),
        (
            "**Engineering problem solved:** Making the physical world computationally accessible. Once phenomena are represented as numbers, all the tools of mathematics, statistics, and computation can be applied.",
            "**Engineering problem solved:** Creating traceable digital observations that mathematical, statistical, and computational methods can analyse while retaining units, provenance, uncertainty, timing, and collection context.",
        ),
        (
            "**Mechanism used:** Machine learning algorithms discover patterns (functions, boundaries, clusters) in data by optimising an objective function. Supervised learning minimises prediction error on labelled examples; unsupervised learning finds structure without labels; reinforcement learning maximises cumulative reward through trial and error.",
            "**Mechanism used:** Learning algorithms fit functions, representations, policies, or probability models using data, feedback, objectives, and inductive assumptions. Supervised, self-supervised, unsupervised, and reinforcement-learning settings differ in what feedback is available and how success is evaluated.",
        ),
        (
            "**Trade-off:** The bias–variance trade-off — simple models (high bias) underfit, complex models (high variance) overfit. Regularisation, cross-validation, and architectural choices (depth, width, dropout) navigate this trade-off. Additional data helps only when its quality, relevance, rights, coverage, dependence structure, and labels support the intended task; it can also amplify bias or shift.",
            "**Trade-off:** Approximation error, estimation uncertainty, optimisation, data quality, leakage, distribution shift, robustness, interpretability, and computation interact. Model size alone does not determine underfitting or overfitting. Additional data helps only when its relevance, rights, coverage, dependence structure, and labels support the intended task.",
        ),
        (
            "**Mechanism used:** Neural networks with many layers (deep networks) learn hierarchical representations: early layers detect simple features (edges, phonemes), later layers compose them into complex concepts (objects, words, syntax). Backpropagation computes gradients of the loss with respect to all parameters, and gradient descent updates them. GPUs and TPUs provide the parallel arithmetic needed for training on large datasets.",
            "**Mechanism used:** Deep networks compose parameterised transformations. Automatic differentiation applies the chain rule to a computational graph, and an optimiser uses gradients or related estimates to update parameters. Learned features, internal organisation, and hardware requirements depend on architecture, data, objective, numerics, and task; they do not follow one universal layer hierarchy.",
        ),
        (
            "**Trade-off:** Resource requirements vary by task, architecture, data, hardware, precision, optimisation, reuse, and accounting boundary; fixed cost claims age quickly and omit deployment and failed experiments. They are opaque — understanding *why* a network makes a specific prediction is an open research problem (interpretability). They can encode biases present in training data and fail unpredictably on out-of-distribution inputs.",
            "**Trade-off:** Resource use, interpretability, calibration, robustness, privacy, security, bias, and evaluation validity depend on the complete lifecycle. Explanations can describe different things—local sensitivity, causal mechanism, example influence, or system rationale—and must be validated for their intended users and decisions.",
        ),
        (
            "**Engineering problem solved:** Making AI capabilities available to a defined service population under stated latency, throughput, reliability, privacy, energy, and cost objectives and cost.",
            "**Engineering problem solved:** Delivering a specified model-assisted service to a defined population under stated latency, throughput, reliability, privacy, security, energy, cost, and human-oversight objectives.",
        ),
        (
            "**Trade-off:** Larger models are more capable but more expensive to run. Latency, throughput, accuracy, and cost form a four-way trade-off. Edge deployment reduces latency and bandwidth but limits model size. Cloud deployment enables large models but introduces network dependency and privacy concerns.",
            "**Trade-off:** Capability is task- and evaluation-specific rather than monotonic in model size. Edge, local, and remote deployment trade hardware limits, data movement, latency, availability, privacy, update control, observability, energy, and cost in context-dependent ways.",
        ),
        (
            "**Mechanism used:** A control system measures the current state (via sensors), compares it to a desired state (setpoint), computes a corrective action (via a controller — PID, model-predictive, or learned policy), and applies it through actuators. The feedback loop continuously drives the system toward the desired state despite disturbances.",
            "**Mechanism used:** A control architecture conditions measurements, estimates relevant state, compares behaviour with references and constraints, computes commands, acts through limited actuators, and verifies response. Feedback can reject some disturbances, but delay, uncertainty, saturation, unmodelled dynamics, and faults bound performance.",
        ),
        (
            "**Trade-off:** Stability vs responsiveness — aggressive control (high gain) responds quickly but risks oscillation or instability. Conservative control (low gain) is stable but slow to correct errors. Robustness vs optimality — controllers designed for worst-case disturbances sacrifice average-case performance.",
            "**Trade-off:** Tracking, disturbance rejection, stability margins, delay tolerance, noise sensitivity, control effort, constraint violations, wear, energy, robustness, and average performance must be balanced for a stated plant and operating region. Gain alone does not determine whether a controller is safe or stable.",
        ),
        (
            "**Engineering problem solved:** Machines that operate in unstructured, dynamic environments without human teleoperation — warehouse robots, surgical robots, autonomous vehicles, drone swarms.",
            "**Engineering problem solved:** Conditional autonomy within a defined operational design domain, authority structure, supervision model, and fallback plan—from constrained industrial handling to assisted mobility and other regulated cyber-physical services.",
        ),
        (
            "**Trade-off:** Full autonomy in open environments (Level 5 self-driving) requires handling an unbounded set of situations, including rare edge cases. The long tail of unusual scenarios makes validation extremely difficult. Current systems achieve high reliability in constrained environments (factories, highways) but struggle with unconstrained ones (urban intersections, construction zones). Assurance requires scenario coverage, hazard analysis, uncertainty, independent protection, human factors, cybersecurity, monitoring, incident response, and evidence appropriate to the regulated application.",
            "**Trade-off:** As the operational domain, authority, speed, interaction, and consequence expand, assurance becomes harder. Scenario coverage alone cannot prove safety; evidence must combine hazard analysis, uncertainty, simulation and physical testing, independent protection, human factors, cybersecurity, monitoring, incident response, and controlled change appropriate to the application.",
        ),
    ),
    "pathways/fields-to-electric-power.md": (
        (
            "**Mechanism used:** Charged particles create electric fields; moving charges (currents) create magnetic fields. These fields exert forces on other charges and currents, described by Coulomb's law and the Biot–Savart law. Maxwell's equations unify these phenomena and predict electromagnetic waves.",
            "**Mechanism used:** Charge and current distributions, together with changing fields and material response, are related by Maxwell's equations. Coulomb and Biot–Savart expressions are useful under restricted electrostatic or magnetostatic assumptions; forces on charges are described by the Lorentz law.",
        ),
        (
            "**Abstraction introduced:** The *field* — a quantity defined at every point in space that encodes the force a test charge would experience, without requiring action at a distance.",
            "**Abstraction introduced:** The *field* — a spatial and temporal quantity used to represent electromagnetic state and interactions locally. Electric and magnetic fields have operational definitions, units, source relations, and measurement limits; neither is merely a hidden force table.",
        ),
        (
            "**Engineering problem solved:** Predicting forces between conductors, the behaviour of capacitors and inductors, and the propagation of signals — all from the field description alone.",
            "**Engineering problem solved:** Analysing forces, energy storage, induction, circuits, waves, insulation, compatibility, and signal propagation using field models combined with material, geometry, boundary, and circuit descriptions.",
        ),
        (
            "**Abstraction introduced:** The *generator principle* — mechanical rotation of a coil in a magnetic field (or rotation of a magnet past a coil) converts kinetic energy to electrical energy continuously.",
            "**Abstraction introduced:** The *electromechanical generator* — relative motion, magnetic flux, conductors, and a connected circuit form a system that transfers mechanical work to electrical output, with losses and transient behaviour determined by the machine and load.",
        ),
        (
            "**Engineering problem solved:** Converting any source of mechanical motion (steam turbine, water turbine, wind turbine) into electrical current.",
            "**Engineering problem solved:** Converting controlled shaft work from selected prime movers into electrical power with specified voltage, frequency, quality, efficiency, and protection requirements.",
        ),
        (
            "**Trade-off:** The induced voltage is proportional to the rate of flux change, so higher voltages require faster rotation or stronger magnets. But faster rotation increases mechanical stress, and stronger magnets require expensive rare-earth materials or superconducting coils.",
            "**Trade-off:** Voltage and power depend on turns, geometry, flux, speed, excitation, saturation, cooling, insulation, frequency, and load. Increasing one design variable can raise mechanical, thermal, dielectric, material, control, or cost burdens; permanent magnets are only one excitation option.",
        ),
        (
            "**Mechanism used:** Thermodynamic cycles (Rankine for steam, Brayton for gas turbines) convert thermal energy from fuel combustion or nuclear fission into mechanical work. The second law limits efficiency to the Carnot bound $\\eta \\leq 1 - T_C/T_H$.",
            "**Mechanism used:** Heat-engine cycles transfer energy from a high-temperature source, produce work, and reject heat. The Carnot expression bounds ideal reversible operation between two reservoirs; real Rankine, Brayton, combined, nuclear, geothermal, and other plants require cycle-specific state, component, and boundary models.",
        ),
        (
            "**Abstraction introduced:** The *heat rate* — the amount of thermal energy input required per unit of electrical energy output (kJ/kWh), a single metric for power plant efficiency.",
            "**Abstraction introduced:** *Heat rate* — thermal input per electrical output over a stated fuel, load, time, and accounting boundary. It supports comparison but does not capture start-up, part-load operation, auxiliaries, emissions, water, reliability, or lifecycle performance by itself.",
        ),
        (
            "**Engineering problem solved:** Providing mechanical work over application-dependent power scales. Combined cycles can improve efficiency by using exhaust heat, but performance depends on ambient conditions, load, equipment, fuel, cooling, and accounting boundary by cascading a gas turbine (high $T_H$) with a steam turbine (recovering exhaust heat).",
            "**Engineering problem solved:** Supplying controlled shaft work over application-dependent power scales. Combined cycles can recover part of a gas turbine's exhaust energy in a steam cycle, while realised performance depends on ambient conditions, load, equipment, fuel, cooling, degradation, and the accounting boundary.",
        ),
        (
            "**Trade-off:** Higher efficiency requires higher turbine inlet temperatures, which demand expensive superalloys and thermal barrier coatings. Material limits set the practical ceiling on $T_H$.",
            "**Trade-off:** Higher source temperature can improve an ideal cycle, but real optimisation also involves pressure ratio, cooling flow, blade aerodynamics, materials, coatings, emissions, lifetime, maintenance, cost, and off-design operation.",
        ),
        (
            "**Mechanism used:** A transformer uses mutual induction between two coils sharing a magnetic core to step voltage up or down while conserving power ($V_1 I_1 \\approx V_2 I_2$). Stepping voltage up reduces current, which reduces resistive losses ($P_{loss} = I^2 R$) in long transmission lines.",
            "**Mechanism used:** A transformer couples windings through time-varying magnetic flux. In an ideal sinusoidal model, voltage ratio follows turns ratio and input and output apparent power are related; real units include magnetising current, winding and core loss, leakage impedance, harmonics, insulation, temperature, and regulation. For a specified real-power transfer, higher voltage can reduce current-related conductor loss.",
        ),
        (
            "**Trade-off:** Higher voltages require larger clearances (taller towers, wider rights-of-way) and more expensive insulation. Corona discharge at very high voltages causes energy loss and radio interference. HVDC transmission eliminates reactive power losses over very long distances but requires expensive converter stations.",
            "**Trade-off:** Voltage choice changes clearance, insulation, corona, conductor, tower, converter, protection, land, reliability, and environmental requirements. HVDC lines do not carry AC reactive power, but converter stations, controls, harmonics, losses, fault handling, and economics remain.",
        ),
        (
            "**Abstraction introduced:** *Automatic generation control (AGC)* — a hierarchical control system that dispatches generators to maintain frequency at the nominal value (50 or 60 Hz ± tight tolerance).",
            "**Abstraction introduced:** *Automatic generation control* — one supervisory layer that adjusts participating resources using frequency and interchange objectives over defined timescales. Primary response, local controls, dispatch, protection, markets, operators, and restoration remain distinct layers.",
        ),
        (
            "**Trade-off:** Faster response requires reserves and headroom that carry opportunity, efficiency, wear, emissions, and cost trade-offs. Battery storage and demand response offer alternatives but add capital cost. Renewable intermittency (solar, wind) increases the need for flexibility, challenging grid stability.",
            "**Trade-off:** Flexibility can come from generation, storage, demand, networks, forecasting, controls, reserves, and operating rules. Needs depend on resource mix, location, correlation, network strength, contingencies, protection, and service criteria; variable renewable generation is neither automatically destabilising nor automatically sufficient.",
        ),
    ),
    "pathways/waves-to-global-communication.md": (
        (
            "**Mechanism used:** Maxwell's equations predict that time-varying electric and magnetic fields propagate through space as transverse waves at speed $c = 1/\\sqrt{\\mu_0 \\epsilon_0} \\approx 3 \\times 10^8$ m/s. These waves carry energy and can be generated by accelerating charges (oscillating currents in an antenna).",
            "**Mechanism used:** Maxwell's equations admit electromagnetic-wave solutions. In vacuum their speed is the defined constant $c$; in materials, propagation depends on constitutive response, dispersion, loss, geometry, and mode. Antennas and other sources radiate when charge-current distributions vary appropriately in time.",
        ),
        (
            "**Trade-off:** Propagation and available bandwidth depend on allocation, antenna size, environment, absorption, diffraction, scattering, regulation, coding, power, and geometry. Frequency alone does not set information capacity or guarantee line of sight and are attenuated by rain, foliage, and buildings.",
            "**Trade-off:** Propagation and usable bandwidth depend on allocation, antenna aperture, environment, absorption, diffraction, scattering, weather, blockage, regulation, coding, power, interference, and geometry. Frequency alone does not determine capacity, coverage, or whether a route is line of sight.",
        ),
        (
            "**Mechanism used:** A carrier wave at frequency $f_c$ is modified (modulated) so that its amplitude, frequency, or phase varies in proportion to the information signal. The modulated wave occupies a bandwidth around $f_c$ determined by the information rate (Shannon–Hartley theorem: $C = B \\log_2(1 + \\text{SNR})$).",
            "**Mechanism used:** A transmitter maps symbols to waveform amplitude, phase, frequency, timing, code, or spatial mode. Occupied spectrum depends on pulse shape, symbol rate, filtering, coding, nonlinearity, regulation, and measurement convention. The Shannon–Hartley expression applies to an ideal bandwidth-limited additive white Gaussian-noise channel, not every radio link.",
        ),
        (
            "**Trade-off:** Higher-order modulation (e.g., 256-QAM) packs more bits per symbol but requires higher signal-to-noise ratio — the signal must be cleaner, limiting range or requiring more transmit power.",
            "**Trade-off:** A higher-order constellation can carry more coded bits per symbol under suitable conditions, but error performance also depends on coding, channel estimation, interference, fading, nonlinearity, phase noise, receiver design, latency, and power constraints.",
        ),
        (
            "**Mechanism used:** Refractive-index structure supports guided electromagnetic modes within a glass fibre; ray total-internal-reflection language is a useful geometric approximation in some regimes whose core has a higher refractive index than its cladding. Signals propagate as guided modes with extremely low attenuation ($\\sim 0.2$ dB/km at 1550 nm wavelength in silica).",
            "**Mechanism used:** A fibre's refractive-index profile and geometry support guided electromagnetic modes. Ray total-internal-reflection language is a useful approximation in suitable regimes. Attenuation, dispersion, mode coupling, bends, splices, connectors, wavelength, and fibre type determine link performance; no single loss value describes every route.",
        ),
        (
            "**Engineering problem solved:** Transmitting high aggregate rates over long terrestrial or submarine routes using wavelength multiplexing, amplification, coherent detection, coding, dispersion management, repeaters, and route-specific engineering (erbium-doped fibre amplifiers).",
            "**Engineering problem solved:** Carrying high aggregate data rates over long terrestrial or submarine routes through wavelength multiplexing, amplification, coherent detection, coding, dispersion management, repeaters, power feeding, monitoring, and route-specific engineering.",
        ),
        (
            "**Mechanism used:** Band-limited signals can be sampled without aliasing above the relevant Nyquist rate only with the stated spectral assumptions and practical anti-alias filtering, quantised, and represented as binary data. Forward error correction (FEC) codes add redundancy so that the receiver can detect and correct bit errors without retransmission.",
            "**Mechanism used:** Under stated band-limit and filtering assumptions, samples can preserve the information needed to reconstruct a signal model. Quantisation maps samples to finite representations. Forward-error-correction codes add structured redundancy so a decoder can estimate transmitted data under a specified channel and error criterion.",
        ),
        (
            "**Abstraction introduced:** The *bit stream* — information reduced to a sequence of 0s and 1s, independent of the physical representation (voltage, light intensity, phase). This enables universal processing by digital logic.",
            "**Abstraction introduced:** The *bit stream* — a logical sequence represented by physical states under encoding, timing, framing, and error conventions. It separates many processing tasks from a specific medium without making implementation or semantics irrelevant.",
        ),
        (
            "**Engineering problem solved:** Scalable, resilient, heterogeneous interconnection of billions of devices. The internet's layered architecture (physical → link → network → transport → application) reduces coupling but does not eliminate cross-layer dependencies, ossification, shared failure modes, or coordinated change.",
            "**Engineering problem solved:** Scalable, heterogeneous internetworking across independently operated links and networks. Layering reduces selected coupling, while naming, routing, policy, security, power, cloud concentration, cables, dependencies, and organisations still create shared risks.",
        ),
        (
            "**Trade-off:** Packet switching introduces variable latency (jitter) and potential packet loss during congestion. Real-time applications require quality-of-service mechanisms or over-provisioning. The end-to-end principle places intelligence at endpoints, making the network simple but pushing complexity to applications.",
            "**Trade-off:** Packet networks trade statistical sharing against queueing, loss, reordering, overhead, congestion, and tail latency. Service quality can use admission, scheduling, reservation, adaptation, redundancy, or capacity planning. End-to-end arguments guide function placement but do not make the network intrinsically simple.",
        ),
        (
            "**Mechanism used:** Cellular networks divide geography into cells, each served by a base station. Frequency reuse (the same frequencies in non-adjacent cells) multiplies capacity. MIMO (multiple-input multiple-output) antennas exploit multipath propagation to increase throughput without additional spectrum.",
            "**Mechanism used:** Cellular systems coordinate coverage areas, base stations, users, spectrum, scheduling, handover, coding, and power. Spatial reuse and multi-antenna processing can improve capacity or reliability when channel rank, interference, geometry, hardware, and channel knowledge support them.",
        ),
        (
            "**Trade-off:** Spectrum is finite and regulated. More users in a cell require either more spectrum (expensive, scarce), smaller cells (more infrastructure), or more sophisticated interference management (more computation). Coverage vs capacity is the permanent tension in wireless network design.",
            "**Trade-off:** Spectrum access, coverage, capacity, latency, energy, mobility, interference, infrastructure density, backhaul, cost, and equity interact. More traffic can be managed through many architectural choices, each with deployment and governance constraints.",
        ),
    ),
    "pathways/biology-to-biotechnology.md": (
        (
            "**Abstraction introduced:** The *gene* — a functional unit of heredity, defined as a DNA sequence that encodes a protein (or functional RNA) along with its regulatory elements. This abstraction allows genetics to operate without tracking every nucleotide.",
            "**Abstraction introduced:** The *gene* — a context-dependent hereditary and functional unit associated with a transcribed product and its regulation. Gene boundaries, isoforms, overlapping features, non-coding products, and distant regulatory elements prevent one universal sequence-only definition.",
        ),
        (
            "**Engineering problem solved:** Understanding how organisms store, copy, and transmit biological information — the prerequisite for any deliberate modification of living systems.",
            "**Engineering problem solved:** Relating molecular sequence, replication, expression, inheritance, variation, and phenotype well enough to formulate and test interventions while respecting uncertainty, biosafety, ethics, and regulation.",
        ),
        (
            "**Engineering problem solved:** Predicting and controlling which proteins a cell produces, when, and in what quantity — the basis for producing recombinant proteins (insulin, antibodies) in engineered host cells.",
            "**Engineering problem solved:** Influencing expression of selected products within a host while accounting for promoter context, RNA processing, translation, folding, modification, localisation, toxicity, burden, and cell-state variation.",
        ),
        (
            "**Mechanism used:** Restriction enzymes cut DNA at specific sequences; DNA ligase joins fragments. Plasmid vectors carry foreign DNA into host cells (bacteria, yeast, mammalian cells). Polymerase chain reaction (PCR) amplifies specific DNA sequences exponentially using thermostable DNA polymerase and thermal cycling.",
            "**Mechanism used:** Restriction enzymes, ligases, synthesis, assembly methods, vectors, transformation or transfection, and selection support construction and propagation of DNA. PCR can amplify a target over repeated cycles, but efficiency, inhibition, primer design, contamination, and stochastic sampling prevent guaranteed exact doubling.",
        ),
        (
            "**Engineering problem solved:** Moving genes between organisms — expressing human insulin in *E. coli*, producing viral antigens in yeast for vaccines, or inserting pest-resistance genes into crop plants.",
            "**Engineering problem solved:** Constructing and expressing selected genetic sequences in suitable hosts for research or regulated production. Successful transfer does not guarantee correct expression, folding, modification, phenotype, containment, or safety.",
        ),
        (
            "**Mechanism used:** The CRISPR-Cas9 system uses a guide RNA (gRNA) complementary to a target DNA sequence to direct the Cas9 nuclease to create a targeted DNA lesion or recruit an editing activity at a selected locus with nonzero uncertainty and context-dependent outcomes. The cell's repair machinery then introduces insertions, deletions, or researcher-supplied sequences at the break site.",
            "**Mechanism used:** A guide RNA and compatible CRISPR-associated effector can recognise a target subject to sequence and motif constraints. Nuclease, base-editing, prime-editing, or regulatory systems then rely on delivery, accessibility, repair, cell state, and validation; outcomes can be heterogeneous and include unintended changes.",
        ),
        (
            "**Abstraction introduced:** *Programmable genome editing* — programmable nucleic-acid targeting whose feasible targets depend on recognition constraints, chromatin or accessibility, delivery, repair pathway, cell state, off-target activity, and validation, without needing organism-specific tools. This generalises genetic engineering from a craft to a platform technology.",
            "**Abstraction introduced:** *Programmable genome targeting* — a reusable design pattern in which sequence recognition is configured separately from some effector functions. Organism-, tissue-, cell-, delivery-, repair-, and regulation-specific engineering remains necessary.",
        ),
        (
            "**Engineering problem solved:** Precise, efficient modification of endogenous genes — correcting disease-causing mutations, knocking out genes to study function, or inserting new metabolic pathways at defined genomic locations.",
            "**Engineering problem solved:** Creating, suppressing, replacing, or regulating selected genomic functions for research and carefully governed applications, with measured efficiency, specificity, mosaicism, phenotype, reversibility, and consequence.",
        ),
        (
            "**Abstraction introduced:** The *chassis organism* — a well-characterised host (e.g., *E. coli*, *S. cerevisiae*) with known metabolism, genetic tools, and fermentation behaviour, serving as a standardised platform for diverse products.",
            "**Abstraction introduced:** The *chassis organism* — a selected host with documented genetics, metabolism, cultivation, containment, and tooling. It is a conditional platform, not a perfectly standard or context-independent biological component.",
        ),
        (
            "**Engineering problem solved:** Producing complex molecules (artemisinin, 1,3-propanediol, spider silk proteins) by fermentation rather than chemical synthesis or extraction from scarce natural sources — enabling scalable, sustainable manufacturing.",
            "**Engineering problem solved:** Producing selected molecules or materials through biological conversion when it offers a favourable route. Scalability and sustainability require lifecycle, feedstock, land, water, energy, yield, purification, waste, safety, and economic assessment.",
        ),
        (
            "**Trade-off:** Cells optimise for growth, not for product yield. Engineering high-flux pathways often creates metabolic burden (diverting resources from growth), triggers toxicity, or activates stress responses. Balancing productivity and cell viability requires iterative design–build–test–learn cycles.",
            "**Trade-off:** Evolution and regulation do not generally maximise an engineered product objective. Added pathways can alter growth, redox balance, energy, precursors, toxicity, burden, stability, and selection. Iterative design–build–test–learn cycles require controls, uncertainty, containment, and long-term stability checks.",
        ),
        (
            "**Abstraction introduced:** *Volumetric productivity* (g/L/h) — a single metric that integrates cell growth rate, specific production rate, and achievable cell density, determining economic viability.",
            "**Abstraction introduced:** *Volumetric productivity* — product amount per reactor volume per time under a stated basis. It is one metric among titre, yield, quality, recovery, batch time, uptime, contamination risk, raw materials, energy, waste, capital, and regulatory requirements.",
        ),
    ),
    "pathways/chemistry-to-materials-and-batteries.md": (
        (
            "**Mechanism used:** Atoms lower their total energy by sharing (covalent), transferring (ionic), or delocalising (metallic) valence electrons. Bonding, composition, structure, defects, phase, microstructure, temperature, environment, and measurement jointly influence melting, mechanics, transport, and solubility. Weaker intermolecular forces (van der Waals, hydrogen bonds) govern the behaviour of molecular solids, liquids, and polymers.",
            "**Mechanism used:** Electronic structure and interactions produce bonding continua that are described with covalent, ionic, metallic, coordination, and intermolecular models. Composition, phase, defects, microstructure, temperature, environment, and measurement jointly determine material behaviour; class labels do not impose fixed properties.",
        ),
        (
            "**Abstraction introduced:** *Bond energy* — the energy required to break a specific bond, allowing prediction of reaction energetics and material stability from tabulated values rather than full quantum calculations.",
            "**Abstraction introduced:** *Bond-dissociation or bond-enthalpy data* — process- and state-specific quantities that can support approximate thermochemical accounting. They do not alone predict condensed-phase stability, kinetics, structure, or reaction pathways.",
        ),
        (
            "**Trade-off:** Strong bonds (covalent, ionic) give high melting points and hardness but make processing difficult (high-temperature sintering, brittle fracture). Weak bonds (van der Waals) enable easy processing but limit thermal and mechanical performance.",
            "**Trade-off:** Bonding tendencies influence stiffness, phase stability, transport, and processing, but hardness, toughness, melting, formability, and durability also depend on structure, defects, microstructure, geometry, rate, and environment. Stronger bonding does not imply universally better performance.",
        ),
        (
            "**Mechanism used:** Atoms in solids arrange into periodic lattices that minimise free energy. The equilibrium structure depends on temperature, pressure, and composition — captured by phase diagrams. Phase transformations (solidification, precipitation, martensitic transformation) alter microstructure and properties.",
            "**Mechanism used:** Solids can be crystalline, amorphous, semicrystalline, multiphase, or defective. Equilibrium and constrained-equilibrium states depend on variables such as temperature, pressure, and composition; finite transformations also depend on nucleation, diffusion, interfaces, stress, and thermal history.",
        ),
        (
            "**Engineering problem solved:** Designing heat treatments (annealing, quenching, tempering) to produce desired microstructures. Steel's versatility — from soft and ductile to hard and wear-resistant — comes from controlling the iron–carbon phase diagram.",
            "**Engineering problem solved:** Designing processing paths that create measured microstructures and properties. For steels, composition, prior state, heating, cooling, transformation kinetics, tempering, geometry, atmosphere, and residual stress all matter in addition to equilibrium diagrams.",
        ),
        (
            "**Mechanism used:** In an electrochemical cell, a spontaneous redox reaction is separated into two half-reactions at different electrodes, forcing electron transfer through an external circuit (producing current) while ions migrate through an electrolyte to maintain charge neutrality. The cell voltage is determined by the Nernst equation: $E = E^0 - (RT/nF)\\ln Q$.",
            "**Mechanism used:** Electrochemical cells couple electrode reactions, electron transport, ion transport, interfaces, and an external circuit. The Nernst equation relates equilibrium potential to activities under stated temperature and reaction conventions; operating voltage also reflects kinetics, resistance, concentration gradients, and history.",
        ),
        (
            "**Abstraction introduced:** *Standard electrode potential* $E^0$ — a single number for each half-reaction that predicts cell voltage, reaction spontaneity, and the direction of electron flow when half-cells are combined.",
            "**Abstraction introduced:** *Standard electrode potential* — an equilibrium potential relative to a reference under specified standard-state conventions. Combining half-cell data can estimate standard cell potential, but spontaneity and operating direction require a balanced reaction, activities, temperature, and non-equilibrium conditions.",
        ),
        (
            "**Mechanism used:** Lithium ions reversibly intercalate (insert) into layered crystal structures at both electrodes. During discharge, Li⁺ deintercalates from the graphite anode, migrates through a non-aqueous electrolyte, and intercalates into the cathode (e.g., LiCoO₂, LiFePO₄, NMC). Electrons flow through the external circuit, doing work.",
            "**Mechanism used:** Many lithium-ion cells shuttle lithium between host materials through an electrolyte while electrons travel through the external circuit. Electrode mechanisms, structures, phase changes, interfaces, and degradation vary by chemistry; not every lithium-based electrode is a simple layered intercalation host.",
        ),
        (
            "**Abstraction introduced:** *Specific energy* (Wh/kg) and *energy density* (Wh/L) — figures of merit that allow comparison across chemistries without detailed knowledge of the intercalation mechanism. These determine whether a battery is suitable for a phone, a car, or a grid.",
            "**Abstraction introduced:** *Specific energy* and *volumetric energy density* — energy delivered per stated mass or volume at specified rate, temperature, voltage limits, age, and cell or pack boundary. Suitability also depends on power, lifetime, safety, cost, reliability, controls, and service requirements.",
        ),
        (
            "**Trade-off:** High energy density means high stored energy in a small volume — a safety risk if thermal runaway occurs (exothermic decomposition of electrolyte). Cathode capacity, cycle life, charging speed, cost, and safety form a multi-dimensional trade-off space. No single chemistry optimises all simultaneously.",
            "**Trade-off:** Greater stored energy can increase consequence when faults propagate, but safety depends on chemistry, state, defects, abuse, heat transfer, venting, spacing, sensing, control, protection, enclosure, and emergency response. Energy, power, life, fast charge, cost, temperature range, and safety form a multi-objective design space.",
        ),
        (
            "**Mechanism used:** Individual cells with chemistry- and state-dependent voltage and capacity are connected in series (for voltage) and parallel (for capacity) to form modules and packs. A battery management system (BMS) monitors voltage, temperature, and state of charge of each cell, balancing charge distribution and preventing operation outside safe limits.",
            "**Mechanism used:** Cells can be arranged in series and parallel and integrated with sensing, estimation, balancing, contactors, fuses, thermal management, mechanical containment, communication, and supervisory control. A BMS can reduce risk but cannot guarantee safe operation or directly observe every internal state.",
        ),
        (
            "**Trade-off:** Series connection means the weakest cell limits the pack. Cell-to-cell variation (manufacturing tolerance) reduces usable capacity unless active balancing is employed, adding cost and complexity. Thermal management (liquid cooling, phase-change materials) is essential but adds mass and volume.",
            "**Trade-off:** Cell variation, ageing, topology, estimation error, thermal gradients, balancing, isolation, fault propagation, serviceability, mass, volume, and cost interact. The limiting element can change with state and duty, and passive or active balancing cannot remove every mismatch or failure mode.",
        ),
        (
            "**Mechanism used:** Research targets higher energy density through solid-state electrolytes (eliminating flammable liquid), silicon or lithium-metal anodes (higher capacity than graphite), and high-nickel cathodes (more energy per formula unit). Each requires solving materials-science challenges: ionic conductivity in solids, volume expansion in silicon, dendrite growth on lithium metal.",
            "**Mechanism used:** Research explores solid and hybrid electrolytes, silicon-rich or lithium-metal negative electrodes, diverse positive electrodes, sodium and other carriers, structural designs, manufacturing methods, and control strategies. Each route changes transport, interfaces, mechanics, safety, supply, cost, and degradation rather than providing one monotonic energy upgrade.",
        ),
        (
            "**Trade-off:** Every gain in energy density tends to reduce cycle life or increase manufacturing complexity. Solid-state batteries eliminate liquid electrolyte fires but introduce brittle ceramic interfaces that crack under cycling strain. The path from laboratory result to qualified production is uncertain and depends on reproducibility, scale-up, supply chain, standards, safety, economics, and application requirements.",
            "**Trade-off:** Energy-density gains do not impose one universal penalty, but they often create new interface, transport, safety, manufacturing, qualification, or cost constraints. Solid electrolytes may reduce some flammable-liquid hazards while introducing contact, fracture, processing, pressure, and short-circuit challenges. Translation to production requires reproducibility and application-specific evidence.",
        ),
    ),
    "concepts/cause-and-effect.md": (
        (
            "Many scientific explanations are causal, while others classify, describe, unify, constrain, or derive patterns without identifying a manipulable cause: we explain *why* something happens by identifying the chain of mechanisms that produces it. Engineers invert this reasoning — they select causes (inputs, forces, signals) that will produce desired effects (motion, computation, structural integrity) within acceptable tolerances. Without causal reasoning, science reduces to description and engineering reduces to trial and error.",
            "Many scientific explanations are causal, while others classify, describe, unify, constrain, or derive patterns without identifying a manipulable cause. Causal explanations connect interventions, mechanisms, counterfactual contrasts, and outcomes under explicit assumptions. Engineers use causal models to select inputs and safeguards, but they also rely on descriptive, predictive, and empirical evidence when mechanisms are incomplete.",
        ),
        (
            "A net force $\\vec{F}$ applied to a mass $m$ causes an acceleration $\\vec{a} = \\vec{F}/m$. The causal chain is explicit: the equation relates net force and acceleration within a Newtonian model and inertial frame; causal interpretation depends on the chosen intervention, system boundary, and constraints, and mass is the mediating property. Removing the force removes the acceleration (in an inertial frame). This directness makes Newtonian mechanics the archetype of causal physical explanation.",
            "Within a Newtonian point-particle model in an inertial frame, net force and acceleration satisfy $\\sum\\vec F=m\\vec a$. Interpreting a force change as an intervention requires the system boundary, constraints, mass model, and other forces to remain specified. The equation is a powerful dynamical relation, not by itself a complete causal identification argument.",
        ),
        (
            "A changing magnetic flux $\\Phi_B$ through a conducting loop causes an electromotive force $\\mathcal{E} = -d\\Phi_B/dt$ (Faraday's law). The mechanism is the Lorentz force on charge carriers in the conductor. This causal relationship is the operating principle of generators, transformers, and induction sensors — the cause (mechanical rotation or varying current) reliably produces the effect (electrical energy or signal).",
            "Faraday's law relates circulation of electric field to changing magnetic flux, while moving-conductor problems can also involve the magnetic Lorentz force. Generator, transformer, and sensor behaviour depends on geometry, material response, circuit loading, motion, losses, and reference frame; one scalar flux derivative is not the whole mechanism.",
        ),
        (
            "Increasing temperature causes faster molecular collisions with sufficient activation energy, which causes higher reaction rates (Arrhenius equation). A catalyst provides an alternative pathway with lower activation energy, causing the same products to form faster without being consumed. The causal chain — temperature → collision energy → reaction probability — is quantitatively predictable.",
            "Temperature can change rate constants, populations, transport, phases, and mechanisms. The Arrhenius form is an empirical or model relation over a stated range. A catalyst participates in a reaction network and is regenerated in the net cycle; it changes kinetics without changing the equilibrium constant for the overall reaction under fixed conditions.",
        ),
        (
            "- **Temporal sequence does not prove causation.** Event A preceding event B is necessary but not sufficient for A causing B. Confounders, coincidences, and reverse causation are alternatives that must be ruled out by mechanism and controlled experiment.",
            "- **Temporal sequence does not prove causation.** A cause cannot occur after its effect under the chosen causal ordering, but measurement timing may be coarse or delayed. Confounding, selection, reverse direction, measurement error, and chance require design assumptions and evidence; a controlled experiment is powerful but not always possible or sufficient by itself.",
        ),
    ),
    "concepts/energy-and-matter.md": (
        (
            "**Matter** refers to physical constituents such as atoms, molecules, condensed phases, plasmas, and particles whose properties are described by the applicable physical theory — atoms, molecules, and their assemblies. **Energy** is a conserved state quantity associated with time-translation symmetry in closed physical descriptions; work and heat are transfer modes, not substances stored in a container — a conserved quantity that can change form (kinetic, potential, thermal, chemical, electromagnetic, nuclear) but cannot be created or destroyed within a closed system. The interplay between energy and matter — how energy is stored in matter, transferred between material systems, and transformed from one form to another — underlies all physical, chemical, and biological processes.",
            "**Matter** refers to physical constituents and states—such as particles, atoms, molecules, condensed phases, and plasmas—described by the applicable theory. **Energy** is a quantitative property used in physical state and balance descriptions. In closed time-invariant models it is conserved; work, heat, radiation, and matter flow are transfer pathways rather than material substances. Energy accounting and material accounting jointly constrain physical, chemical, biological, and engineered systems.",
        ),
        (
            "Conservation of energy and conservation of mass (or mass-energy in relativistic contexts) are the most powerful constraints in science. They allow prediction without knowing every microscopic detail: balances constrain totals, but prediction also requires storage, accumulation, transfer modes, losses, sign conventions, state, and measurement uncertainty. Engineers use energy and mass balances to design power plants, chemical reactors, biological processes, and electronic systems. Violations of these balances indicate measurement error, missing pathways, or new physics.",
            "Energy, momentum, charge, atomic-species, and mass balances are powerful constraints when their system boundaries and approximations are stated. A residual can indicate measurement error, unmeasured storage or flow, model mismatch, reaction, leakage, or an incorrect boundary; extraordinary new-physics interpretations require much stronger evidence.",
        ),
        (
            "Electrons in atoms occupy quantised energy levels. The binding energy of an electron — the energy required to remove it from the atom — determines chemical reactivity. Nuclear binding energy (the mass defect, $\\Delta E = \\Delta m \\cdot c^2$) explains why fusion of light nuclei and fission of heavy nuclei both release energy: many energy-releasing nuclear reactions move nuclei toward the high-binding-energy region near iron and nickel, subject to reaction pathways and conservation laws of binding energy per nucleon.",
            "Atomic electronic states and ionisation energies contribute to chemical behaviour together with molecular environment, bonding, kinetics, and accessible pathways. Nuclear mass differences correspond to reaction-energy changes through $\\Delta E=\\Delta m c^2$. Many exothermic fusion or fission pathways move products toward higher binding energy per nucleon, subject to conservation laws, reaction barriers, and decay channels.",
        ),
        (
            "Chemical reactions rearrange atoms by breaking and forming bonds. The net energy change equals the difference between the energy required to break reactant bonds and the energy released when product bonds form. Exothermic reactions (negative $\\Delta H$) release energy to the surroundings; endothermic reactions absorb it. This energy accounting governs combustion, battery chemistry, and metabolism.",
            "Chemical reactions change electronic, vibrational, rotational, translational, solvation, and phase contributions. Average gas-phase bond enthalpies can provide an approximation, while accurate reaction enthalpy uses defined initial and final states. The sign of $\\Delta H$ describes heat transfer at constant pressure under stated conventions, not reaction rate or spontaneity by itself.",
        ),
        (
            "The first law of thermodynamics ($\\Delta U = Q - W$) states that the internal energy change of a system equals heat added minus work done by the system. The second law constrains *how much* of that energy can be converted to useful work: the Carnot efficiency $\\eta = 1 - T_C/T_H$ sets an upper bound determined by temperature ratios. Every real engine, power plant, and refrigerator operates within these constraints.",
            "With the convention that $Q$ enters the system and $W$ is work done by it, $\\Delta U=Q-W$ for a closed system. The second law constrains entropy production and available work. The Carnot expression bounds a reversible heat engine operating between two reservoirs; refrigerators, open systems, chemical devices, and real cycles require their own models and boundaries.",
        ),
        (
            "Living cells couple exergonic reactions (ATP hydrolysis, $\\Delta G \\approx -30.5$ kJ/mol) to endergonic processes (protein synthesis, ion pumping, muscle contraction). ATP hydrolysis can drive coupled processes because the complete reaction has a favourable Gibbs free-energy change under cellular conditions; no isolated bond contains a packet of usable energy, and enzymes ensure that the energy is transferred to the correct acceptor rather than dissipated as heat. Photosynthesis captures electromagnetic energy and stores it in the chemical bonds of glucose — a matter-based energy reservoir.",
            "Cells couple reactions and transport processes through shared intermediates, conformational changes, electrochemical gradients, and reaction networks. ATP-hydrolysis free energy depends on activities, pH, ionic conditions, and coupling mechanism; the standard biochemical value is not a universal cellular constant. Enzymes alter pathways and rates rather than guaranteeing useful transfer. Photosynthesis uses absorbed radiation to drive redox and carbon-fixation chemistry whose products can later support metabolism.",
        ),
        (
            "Earth's top-of-atmosphere energy budget depends on solar input, albedo, spectral absorption and emission, clouds, circulation, storage, and effective emission temperature. Greenhouse gases alter wavelength-dependent optical depth and emission levels rather than acting as a simple reduced-emissivity blanket and raising surface temperature until a new balance is reached. The entire climate system is an energy-flow problem: solar input → absorption → redistribution by atmosphere and ocean → re-emission to space.",
            "Earth's top-of-atmosphere energy budget depends on solar input, albedo, spectral absorption and emission, clouds, circulation, storage, and effective emission temperature. Greenhouse gases alter wavelength-dependent optical depth and emission levels rather than acting as a simple reduced-emissivity blanket. Surface and atmospheric response depend on feedbacks, transport, internal variability, forcing history, and the timescale of adjustment.",
        ),
        (
            "Manufacturing transforms raw matter into useful forms, and every transformation requires energy. Primary aluminium production is electricity- and process-intensive, with values depending on technology, feedstock, electricity, boundaries, yield, and allocation because the Al–O bond is strong. The embodied energy of a material — the total energy consumed from extraction through fabrication — is a critical engineering quantity for lifecycle assessment and sustainable design.",
            "Manufacturing changes material form and state through energy and matter flows. Primary aluminium production is electricity- and process-intensive because ore preparation, electrolysis, heat, anode reactions, yield, and auxiliary systems all contribute. Embodied-energy or cumulative-energy metrics require geography, electricity mix, allocation, recycled content, transport, process yield, and lifecycle boundaries.",
        ),
        (
            "- **Energy is not a substance.** Energy is a property of systems, not a fluid that flows. Phrases like \"energy flows\" are metaphorical shorthand for \"the capacity to do work is transferred between systems.\"",
            "- **Energy is not a material substance.** Energy flux and transfer are quantitatively defined, but they do not describe a conserved fluid made of energy particles. State variables, work, heat, radiation, and matter transport must be distinguished.",
        ),
        (
            "- **Matter is not always conserved separately.** In nuclear reactions and particle physics, matter can be converted to energy and vice versa ($E = mc^2$). In chemistry and biology, however, mass is conserved to excellent approximation because binding energies are negligible fractions of rest mass.",
            "- **Rest mass and particle number are not universally conserved.** Relativistic reactions conserve total energy-momentum and relevant charges, while particle species and invariant mass of a composite system can change. In ordinary chemical and biological accounting, mass conservation is an excellent approximation at usual precision.",
        ),
    ),
    "concepts/patterns.md": (
        (
            "Some biological, ecological, technological, and social networks show heavy-tailed or approximately power-law features over limited ranges, while others do not; model choice and sampling strongly affect the conclusion — a pattern indicating preferential attachment or optimisation under resource constraints. Recognising this pattern allows prediction of network robustness: robustness depends on topology, weights, direction, dynamics, dependency, repair, common-cause failure, and the attack or failure model; degree distribution alone is insufficient.",
            "Some biological, ecological, technological, and social networks show heavy-tailed or approximately power-law features over limited ranges, while others do not. Sampling, thresholding, dependence, finite size, and model comparison strongly affect the conclusion. Preferential attachment is one possible mechanism among many; robustness requires topology, weights, direction, dynamics, dependency, repair, and a specified failure model.",
        ),
        (
            "- **Correlation is not pattern.** A pattern implies reproducibility under stated conditions; a single correlation in noisy data may be coincidence. Genuine patterns survive replication and have mechanistic explanations.",
            "- **A correlation can be a pattern without being causal.** Reproducibility, effect size, uncertainty, measurement quality, and out-of-sample performance determine whether a regularity is credible. A mechanistic explanation strengthens understanding but is not part of the definition of every empirical pattern.",
        ),
    ),
    "concepts/scale-proportion-and-quantity.md": (
        (
            "Fundamental descriptions and effective models apply over stated regimes; as scale changes, new degrees of freedom, approximations, fluctuations, interfaces, and dominant dimensionless ratios can become relevant. Surface tension dominates at millimetre scales; gravity dominates at kilometre scales. Engineers must identify the relevant scale of a problem to select the correct model, the right materials, and the appropriate tolerances. Proportional reasoning — understanding that doubling a dimension cubes the volume — prevents catastrophic design errors and enables dimensional analysis as a powerful checking tool.",
            "Fundamental descriptions and effective models apply over stated regimes. As scale changes, degrees of freedom, averaging, interfaces, fluctuations, transport lengths, and dimensionless ratios can change importance. Surface and body forces must be compared for a specified geometry and material. Under geometric similarity, doubling every length multiplies volume by eight; other scaling paths give different results.",
        ),
        (
            "Any physically meaningful equation must be dimensionally consistent. The Buckingham Pi theorem shows that a system described by $n$ variables involving $k$ fundamental dimensions can be characterised by $n - k$ dimensionless groups. These groups (Reynolds number, Mach number, etc.) encode the proportional relationships that determine which regime a system occupies — laminar vs turbulent, subsonic vs supersonic.",
            "A valid physical equation must be dimensionally consistent, though consistency alone does not make it correct. Under the rank and completeness assumptions of dimensional analysis, $n$ dimensional variables with a dimension matrix of rank $k$ can be expressed through $n-k$ independent dimensionless groups. Regime boundaries still require equations or data; one dimensionless number rarely determines all behaviour.",
        ),
        (
            "Quantum effects become significant when the de Broglie wavelength $\\lambda = h/p$ is comparable to the system's characteristic length. For ordinary macroscopic centre-of-mass motion the de Broglie wavelength is generally far below experimental resolution, whereas microscopic systems can require quantum descriptions — negligible. For electrons in atoms, $\\lambda \\sim 10^{-10}$ m — comparable to atomic radii. The *scale* of the system determines whether quantum mechanics or classical mechanics is the appropriate model.",
            "The de Broglie wavelength $\\lambda=h/p$ is one scale relevant to wave behaviour, but coherence, action, temperature, coupling, measurement resolution, and environment also matter. Macroscopic centre-of-mass interference is usually unobservable under ordinary conditions, while microscopic systems can require quantum descriptions. Classical models can emerge as controlled approximations rather than replacing quantum theory at one sharp size.",
        ),
        (
            "Reducing transistor gate length from micrometres to nanometres changes the dominant physics: as dimensions, fields, barriers, and carrier numbers change, tunnelling, confinement, variability, contacts, electrostatics, and heat can require quantum-aware and nanoscale compact models; no one node label defines the transition. The proportional reduction in switching energy ($\\propto CV^2$, where $C$ scales with area) enabled decades of exponential performance growth, but the approach to atomic scales imposes fundamental limits.",
            "As device dimensions, fields, barriers, and carrier populations change, tunnelling, confinement, discrete variability, contacts, electrostatics, interconnect, and self-heating require revised models. The switching approximation $E\\sim CV^2$ is boundary- and activity-dependent, and capacitance does not simply scale with area across changing architectures. Historical performance gains combined device, circuit, architecture, memory, packaging, software, and manufacturing changes.",
        ),
        (
            "Earth's climate is governed by the proportion between incoming solar radiation ($\\sim 1361$ W/m² at the top of the atmosphere) and outgoing longwave radiation. A change of a few watts per square metre in radiative forcing — a tiny proportion of the total flux — shifts global mean temperature by degrees, because the system operates near a sensitive equilibrium. Scale awareness prevents dismissing small forcings as insignificant.",
            "Climate response depends on top-of-atmosphere imbalance, effective radiative forcing, feedbacks, heat uptake, internal variability, spatial pattern, and timescale. A forcing can be small relative to gross incoming and outgoing fluxes yet persistent enough to alter stored energy. Its temperature consequence must be estimated with a stated model and uncertainty rather than a fixed degrees-per-flux rule.",
        ),
        (
            "Every measured quantity has a scale of uncertainty. Reporting a length as $1.5000 \\pm 0.0001$ m claims a relative uncertainty of $7 \\times 10^{-5}$. Uncertainty propagation depends on the measurement model, derivatives or simulation, covariance, distributions, nonlinearity, and reporting convention; simple independent-error formulas are special cases — ensuring that final results honestly reflect the scale of what is actually known.",
            "Every reported measurement result requires a quantity value, unit, uncertainty or resolution context, and a measurement model. For $1.5000\\pm0.0001$ m, the relative standard uncertainty would be about $6.7\\times10^{-5}$ only if the stated interval is a standard uncertainty. Propagation depends on covariance, distributions, nonlinearity, and reporting convention.",
        ),
        (
            "- **Neglecting dimensionless ratios.** Two systems can have the same dimensionless numbers (and therefore the same physics) despite vastly different absolute sizes. This is the basis of wind-tunnel testing and scale models, but it requires matching *all* relevant dimensionless groups, not just geometric similarity.",
            "- **Neglecting dimensionless ratios.** Matching a sufficient set of relevant dimensionless groups can produce dynamic similarity for the modelled mechanisms. Exact similarity may be impossible when several groups, roughness, chemistry, elasticity, or scale-dependent effects cannot all be matched.",
        ),
    ),
    "concepts/stability-and-change.md": (
        (
            "**Stability** is a property of a specified state, trajectory, distribution, or operating set under defined perturbations, dynamics, norms, timescales, and boundaries. **Change** is the transition from one state to another, driven by forces, flows, or fluctuations that exceed the system's restoring capacity. Understanding when and why systems are stable — and what causes them to change — is central to both scientific prediction and engineering reliability.",
            "**Stability** is a property of a specified equilibrium, trajectory, distribution, or operating set under defined dynamics, perturbations, metrics, timescales, and boundaries. **Change** includes continuous evolution, drift, transition, bifurcation, failure, adaptation, or stochastic fluctuation; it need not result from exceeding one restoring capacity.",
        ),
        (
            "A system at constant temperature and pressure is stable when its Gibbs free energy $G$ is at a minimum. A local Gibbs-energy minimum is a thermodynamic stability criterion under fixed temperature and pressure, but kinetics, constraints, nucleation, transport, and finite-system fluctuations determine the observed path and timescale — this is thermodynamic stability. Change occurs when conditions shift the free-energy landscape: heating can make a solid unstable relative to its liquid phase, triggering melting. Metastable states (diamond at room temperature) are locally stable but globally unstable — they persist only because the kinetic barrier to change is high.",
            "At fixed temperature, pressure, composition constraints, and relevant variables, a Gibbs-free-energy minimum supplies a thermodynamic stability criterion. Local and global minima, phase coexistence, finite size, constraints, nucleation, and kinetics must be distinguished. A metastable state can persist because transitions are kinetically suppressed, not because every perturbation restores the same state.",
        ),
        (
            "A column under compressive load is stable below the Euler critical load $P_{cr} = \\pi^2 EI / L^2$. Euler buckling is an ideal bifurcation model for a slender elastic column with stated supports, loading, geometry, imperfections, and material assumptions; real failure can occur earlier or by other modes — a sudden transition from stable straight configuration to a bent one. This is a classic bifurcation: the system's qualitative behaviour changes discontinuously at a critical parameter value.",
            "For an ideal slender, straight, linearly elastic pin-ended column under centred load, Euler theory gives $P_{cr}=\\pi^2EI/L^2$. Effective length changes with support conditions. Imperfections, yielding, residual stress, eccentricity, local buckling, and dynamics alter real response, which may grow continuously rather than jump discontinuously.",
        ),
        (
            "A population is evolutionarily stable when no rare mutant strategy can invade (the Evolutionarily Stable Strategy, ESS). Change occurs when environmental shifts alter fitness landscapes, making previously stable genotypes less fit. Observed evolutionary tempo can involve stasis and comparatively rapid change, but explanations require fossil resolution, population processes, environment, selection, drift, migration, and development rather than one universal stability mechanism the interplay between stabilising selection (maintaining the current state) and directional selection (driving change when conditions shift).",
            "An evolutionarily stable strategy is a game-theoretic concept defined relative to payoffs, population structure, and invasion conditions; it is not the same as a stable genotype or ecosystem. Evolutionary change can involve mutation, recombination, drift, selection, gene flow, development, and environmental change. Fossil tempo and apparent stasis also depend on sampling and temporal resolution.",
        ),
        (
            "Ecosystems can exist in alternative stable states (e.g., clear-water lake vs turbid-water lake). Gradual nutrient loading may not cause visible change until a tipping point is crossed, after which the system rapidly shifts to the alternative state. Resilience — the size of the perturbation a system can absorb without shifting states — is a measure of stability. Alternative states and basins are model-dependent; proposed early-warning signals can fail and require system-specific evidence, uncertainty, and competing explanations.",
            "Some ecological models and well-studied systems support alternative-state or hysteresis hypotheses. Establishing them requires evidence that distinguishes nonlinear state dependence from external forcing, slow recovery, observation error, and transient dynamics. Resilience has multiple definitions—recovery rate, persistence, service continuity, or disturbance tolerance—and must be operationalised.",
        ),
        (
            "Earth's climate is stabilised by negative feedbacks (e.g., increased temperature → increased radiation to space via Stefan–Boltzmann law). But positive feedbacks (ice-albedo feedback, water-vapour feedback) can amplify perturbations. The balance between stabilising and destabilising feedbacks determines climate sensitivity — how much warming results from a given forcing. Past climate shifts (snowball Earth, PETM) demonstrate that the climate system can undergo rapid state transitions when stabilising feedbacks are overwhelmed.",
            "Climate response combines radiative, cloud, water-vapour, lapse-rate, surface-albedo, carbon-cycle, circulation, and ice feedbacks across timescales. Effective climate sensitivity is conditional on forcing, state, spatial pattern, and model. Palaeoclimate evidence constrains possible transitions but does not reduce them to one feedback being overwhelmed.",
        ),
        (
            "A metal component under cyclic loading may appear stable for millions of cycles, then suddenly fracture. Fatigue cracks nucleate and grow incrementally (change accumulating below the threshold of detection) until the remaining cross-section cannot support the load — catastrophic failure. The S–N curve quantifies how many cycles a material can endure at a given stress amplitude before stability is lost.",
            "Cyclic loading can initiate or grow damage through mechanisms that depend on stress history, mean stress, geometry, surface, defects, environment, temperature, and material state. S–N data are statistical and test-specific; some designs instead use strain-life, crack-growth, damage-tolerance, or inspection models. Apparent sudden fracture can follow long undetected growth.",
        ),
        (
            "- **Stability does not mean immobility.** A spinning gyroscope, a flowing river, and a metabolising cell are all stable systems — they maintain their state (rotation, flow pattern, homeostasis) despite perturbations. Dynamic stability is as real as static stability.",
            "- **Stability does not mean immobility.** A trajectory, oscillation, flow, regulated state, or probability distribution can be stable under a specified definition. A river or cell is not simply stable without naming the variable, disturbance, timescale, and recovery criterion.",
        ),
    ),
    "concepts/structure-and-function.md": (
        (
            "**Structure** is the arrangement of components — spatial, temporal, or logical — within a system. **Function** is what the system does: the behaviour or capability that emerges from that arrangement. The relationship between structure and function is one of the most powerful generalisations in science and engineering: structure constrains possible behaviour, but function also depends on material state, environment, history, dynamics, interfaces, control, and definition of the task, and if you need it to do something specific, you must build it accordingly.",
            "**Structure** is an arrangement of components, states, or relations across spatial, temporal, logical, or organisational scales. **Function** is a behaviour, role, or service defined relative to a context and observer. Structure constrains possible behaviour, but function also depends on material state, environment, history, dynamics, interfaces, control, and the task definition.",
        ),
        (
            "Identifying the structure–function relationship allows prediction without exhaustive testing. A biologist who knows the three-dimensional fold of a protein can generate hypotheses about catalytic activity that still require thermodynamic, kinetic, environmental, and experimental validation. An engineer who knows the crystal structure of a metal can predict its mechanical properties. Conversely, when a desired function is specified, the structure–function principle guides the design of structures that will achieve it. This bidirectional reasoning — from structure to function and from function to required structure — is the core of both scientific explanation and engineering design.",
            "Structure can narrow hypotheses and guide measurement without uniquely determining outcome. A protein fold or crystal structure supports mechanistic hypotheses, but catalytic or mechanical performance still requires composition, defects, state, environment, loading, kinetics, and test evidence. Inverse design is generally many-to-many: several structures may realise a function, and one structure may support several functions.",
        ),
        (
            "Electronic states, occupancy, interactions, molecular environment, and symmetry help explain how an atom bonds, what ions it forms, and what spectra it emits. Carbon's four valence electrons in $sp^3$ hybridised orbitals create a tetrahedral bonding geometry that enables the structural diversity of organic chemistry. Silicon's similar but larger orbitals enable semiconductor behaviour. Structure (electron arrangement) determines function (chemical and electronic properties).",
            "Electronic states, occupancy, interactions, molecular environment, and symmetry help explain bonding, ions, spectra, and transport. Carbon supports many hybridisation and bonding environments; silicon's solid-state behaviour depends on periodic structure, defects, dopants, interfaces, and temperature. Electronic structure constrains chemistry and transport without uniquely fixing them.",
        ),
        (
            "Enzyme active sites have precise three-dimensional shapes that complement their substrates (the lock-and-key or induced-fit model). A single amino acid substitution can alter the shape enough to destroy catalytic function — as in sickle-cell haemoglobin, where a valine-for-glutamate swap changes the protein's surface, causing aggregation. Oxygen transport depends on molecular structure together with concentration, binding equilibria, allostery, cellular environment, flow, and physiology (quaternary fold and surface chemistry).",
            "Enzyme function depends on dynamic conformational ensembles, electrostatics, solvent, cofactors, substrate access, and reaction pathways; lock-and-key and induced-fit are limited models. A substitution can change stability, dynamics, binding, assembly, expression, or have little measurable effect. Haemoglobin oxygen transport combines molecular structure with binding equilibria, allostery, concentration, cells, flow, and physiology.",
        ),
        (
            "The double-helical structure of DNA — antiparallel sugar-phosphate backbones with hydrogen-bonded base pairs (A–T, G–C) — enables three functions simultaneously: information storage (base sequence), faithful replication (complementary base pairing), and regulated expression (accessibility of promoter regions). The structure is not merely correlated with these functions; it mechanistically enables them.",
            "DNA's base sequence and complementary duplex structure support storage and template-directed copying, while fidelity also depends on polymerases, proofreading, repair, chromatin, cell state, and damage. Regulated expression involves promoters, enhancers, RNA processing, accessibility, transcription machinery, and many other structures; the double helix alone does not provide all three functions.",
        ),
        (
            "The arrangement of atoms in a crystal lattice determines hardness, conductivity, optical properties, and failure modes. Crystal structure affects available deformation mechanisms, but ductility, strength, and fracture also depend on composition, temperature, rate, texture, grain structure, defects, processing, and environment. Diamond and graphite are both pure carbon, but their radically different structures (3D tetrahedral vs 2D layered) produce radically different functions (hardest natural material vs lubricant).",
            "Atomic arrangement and electronic structure influence mechanics, transport, optics, and failure, while composition, defects, phases, texture, grain structure, environment, processing, geometry, and test method also matter. Diamond and graphite illustrate strong structural effects, but labels such as 'hardest' or 'lubricant' remain property- and condition-specific.",
        ),
    ),
    "concepts/systems-and-models.md": (
        (
            "A **system** is a chosen set of entities, states, interactions, and boundaries used to answer a question or deliver a service; its boundary is an analytical and engineering decision, where the interactions produce behaviour that the components alone do not exhibit. A **model** is a simplified representation of a system — mathematical, computational, or conceptual — that captures the relationships relevant to a specific question while deliberately omitting irrelevant detail. Scientific and engineering reasoning uses multiple representations, measurements, theories, experiments, and models; none should be confused with the full physical or social reality.",
            "A **system** is a chosen set of entities, states, interactions, environments, and boundaries used for a question or service. Its boundary is an analytical and engineering choice. A **model** is a mathematical, computational, physical, statistical, or conceptual representation designed for a purpose; omitted detail is not necessarily irrelevant for another purpose. Measurements, theories, experiments, simulations, and models provide different evidence and should not be confused with the full physical or social reality.",
        ),
        (
            "No real system can be understood in its full complexity simultaneously. Models allow scientists to isolate mechanisms, make quantitative predictions, and test hypotheses against observation. Engineers use models to simulate performance before building, to identify failure modes, and to optimise designs within constraints. The discipline of defining system boundaries, inputs, outputs, and internal states is the foundation of both scientific analysis and engineering design.",
            "Models help isolate mechanisms, organise data, estimate unobserved quantities, compare alternatives, predict conditionally, and test assumptions. Engineers use them before and during operation, but high-consequence decisions also require measurements, verification, validation, margins, monitoring, and human judgement. Boundaries, inputs, outputs, states, disturbances, and stakeholders must match the question.",
        ),
        (
            "Thermodynamics defines three system types: isolated (no exchange of energy or matter), closed (energy exchange only), and open (both). The choice of system boundary determines which conservation laws apply and which quantities are state functions. The ideal gas model $PV = nRT$ captures the essential behaviour of dilute gases by modelling molecules as non-interacting point particles — a deliberate simplification that fails at high pressure (van der Waals corrections) but is useful over a stated dilute-gas regime and fails when interactions, phase change, chemistry, or high density matter.",
            "Thermodynamic analyses commonly distinguish isolated, closed, and open control masses or volumes according to allowed transfers. Conservation laws remain fundamental, but their balance terms depend on the boundary. The ideal-gas equation is useful for suitable dilute gas states; real-gas interactions, phase change, chemistry, high density, and non-equilibrium conditions require other models.",
        ),
        (
            "Engineers represent control systems as block diagrams: each block is a transfer function (a model of a subsystem), and arrows represent signal flow. The entire system's behaviour emerges from the interconnection of these blocks. This abstraction allows analysis of stability, bandwidth, and robustness without knowing the physical details inside each block — input–output models can support analysis, but hidden state, nonlinearities, saturation, uncertainty, safety, and implementation may also matter.",
            "Block diagrams represent selected signal and subsystem relations; a block may be a transfer function, nonlinear operator, state-space model, estimator, controller, delay, or logic element. Interconnection supports analysis, but hidden state, sampling, saturation, uncertainty, physical energy flow, safety, cybersecurity, and implementation remain relevant.",
        ),
        (
            "A software system is decomposed into modules with defined interfaces (APIs). Each module is a model of a responsibility: the database module models data persistence, the network module models communication. The system's emergent behaviour (user-facing functionality) arises from the interaction of these modules, and failures often occur at interfaces — exactly where system boundaries are drawn.",
            "Software can be decomposed into components and interfaces, but architecture varies across processes, services, libraries, data stores, queues, devices, users, and organisations. Interfaces encode contracts and failure semantics; failures can occur within components, across dependencies, through shared infrastructure, or from incorrect system boundaries.",
        ),
        (
            "- **Emergent properties are not magic.** When a system exhibits behaviour that its components individually do not, this is emergence. It arises from interactions, not from mysterious holistic forces. A good model of the interactions predicts the emergent behaviour.",
            "- **Emergence does not guarantee predictability.** Collective behaviour can arise from interactions, constraints, heterogeneity, adaptation, and environment. Even known local rules may be computationally difficult, sensitive, stochastic, or insufficient for reliable macro-level prediction.",
        ),
    ),
}


def apply(write: bool) -> int:
    errors: list[str] = []
    changed: list[str] = []
    for rel, pairs in REPLACEMENTS.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        fixed = text
        for old, new in pairs:
            if new in fixed:
                continue
            if old not in fixed:
                errors.append(f"{rel}: expected pre-final text missing: {old[:100]}")
                continue
            fixed = fixed.replace(old, new, 1)
        fixed = fixed.rstrip() + "\n"
        if fixed != text:
            changed.append(rel)
            if write:
                path.write_text(fixed, encoding="utf-8")

    if errors:
        print("Phase 10 finalizer errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if not write and changed:
        print("Phase 10 editorial-scientific finalizer is not applied:", file=sys.stderr)
        for rel in changed:
            print(f"- {rel}", file=sys.stderr)
        return 1
    print(f"Phase 10 editorial-scientific finalizer {'updated' if write else 'is idempotent'}: {len(changed)} changed files.")
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
