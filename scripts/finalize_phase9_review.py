#!/usr/bin/env python3
"""Final editorial-scientific pass for Phase 9 Technology Modules 17–20."""
from __future__ import annotations

import apply_phase9_technology_review as phase9

POST_SECTIONS = {
    ("technology/17-materials-manufacturing/overview.md", 1): r"""## 1. The central questions

How do composition and structure across atomic, microscopic, and component scales influence measured properties and performance? How do thermal, mechanical, chemical, and electromagnetic processes alter those structures? How should engineers select a material, manufacturing route, inspection plan, and lifecycle strategy when variability, defects, safety, cost, repair, and failure consequence all matter?
""",
    ("technology/17-materials-manufacturing/overview.md", 2): r"""## 2. Observable phenomena

Nominally similar alloys can exhibit different hardness, ductility, residual stress, corrosion response, and fatigue life after different thermal or mechanical histories. Diffraction peaks, micrographs, indentation records, tensile curves, and fracture surfaces provide different evidence about structure and behaviour; none alone determines service performance.

Manufacturing leaves measurable signatures. Casting can produce segregation, shrinkage, and texture; forming changes shape, orientation, and residual stress; machining changes geometry and surface integrity; joining creates interfaces and heat-affected regions; additive processes create layerwise thermal histories. Whether a signature is acceptable depends on the component, load, environment, inspection method, and qualification basis.
""",
    ("technology/17-materials-manufacturing/overview.md", 6): r"""## 6. Mathematical models and equations

**Bragg condition:**
$$n\lambda=2d_{hkl}\sin\theta.$$
Here $d_{hkl}$ is the spacing of the selected lattice-plane family. The relation assumes elastic diffraction and a stated geometry; peak position, width, and intensity also depend on structure factor, texture, strain, crystallite size, instrument response, and sample preparation.

**Empirical Hall–Petch relation:**
$$\sigma_y=\sigma_0+k_y d_g^{-1/2}.$$
The coefficients and useful grain-size range must be fitted for a specified material, microstructure, temperature, strain rate, and test method. Extrapolation outside the fitted regime is not justified.

**Lever rule:** For an equilibrium binary two-phase region with tie-line endpoints $C_\alpha$ and $C_\beta$,
$$W_\alpha=\frac{C_\beta-C_0}{C_\beta-C_\alpha},\qquad
W_\beta=\frac{C_0-C_\alpha}{C_\beta-C_\alpha}.$$
All compositions must use one basis. The result gives equilibrium phase fractions, not phase shape, size, connectivity, or transformation rate.

**Diffusion:**
$$\mathbf J=-D\nabla C,\qquad
\frac{\partial C}{\partial t}=\nabla\!\cdot(D\nabla C).$$
The second expression is a concentration-based model. Spatially varying, anisotropic, multicomponent, reactive, or non-ideal systems may require tensor diffusivity and chemical-potential gradients.
""",
    ("technology/17-materials-manufacturing/overview.md", 7): r"""## 7. Definitions of symbols and units

- $n$: diffraction order, dimensionless integer.
- $\lambda$: incident wavelength, m.
- $d_{hkl}$: spacing of the selected lattice-plane family, m.
- $\theta$: Bragg angle under the stated convention, rad or degrees.
- $\sigma_y$: measured yield or proof stress, Pa.
- $\sigma_0$: fitted Hall–Petch intercept, Pa; its physical interpretation is model-dependent.
- $k_y$: fitted Hall–Petch coefficient, Pa$\,\text{m}^{1/2}$.
- $d_g$: specified grain-size measure, m.
- $W_\alpha,W_\beta$: phase fractions on the chosen mass or mole basis, dimensionless.
- $C_0,C_\alpha,C_\beta$: overall and tie-line compositions on one consistent basis.
- $\mathbf J$: diffusion flux, amount per area per time.
- $D$: scalar diffusivity in the simple model, m$^2$/s.
- $C$: concentration on a stated basis.
- $\nabla$: spatial-gradient operator, m$^{-1}$ when acting on a dimensionless field.
- $t$: time, s.
""",
    ("technology/17-materials-manufacturing/technology.md", 1): r"""## 1. Scientific principles used

Manufacturing combines thermodynamics, kinetics, transport, mechanics, chemistry, electromagnetism, and measurement science. Thermodynamics constrains equilibrium and driving forces but does not determine rate. Kinetics describes nucleation, growth, diffusion, reaction, and relaxation. Mechanics relates stress, deformation, contact, fracture, vibration, and machine dynamics. Heat, mass, momentum, charge, and information transfer couple the energy source, tool, feedstock, atmosphere, fixture, sensor, and controller.
""",
    ("technology/17-materials-manufacturing/technology.md", 2): r"""## 2. The engineering problem

The problem is to produce a defined population of components that satisfies geometry, material state, surface condition, function, safety, reliability, traceability, throughput, cost, and lifecycle requirements despite variation in feedstock, equipment, environment, measurement, and operation. There is rarely one universally optimal route. Casting, forming, machining, additive processing, joining, coating, and heat treatment create different defect populations and economic trade-offs; qualification must be tied to the actual design and process window.
""",
    ("technology/17-materials-manufacturing/technology.md", 4): r"""## 4. How the components interact

A manufacturing route links prepared feedstock, tooling or an energy-delivery system, motion and handling, process environment, sensing, control, metrology, and disposition. In machining, tool geometry, speed, feed, workholding, coolant or dry-cutting strategy, machine dynamics, and tool wear influence force, temperature, surface integrity, and dimensional error. In laser powder-bed fusion, powder condition, layer deposition, atmosphere, beam parameters, scan strategy, thermal history, supports, and recoating interact; melt-pool signals alone do not prove final density or mechanical performance. Inspection and destructive validation are needed to connect process observations with accepted product quality.
""",
    ("technology/17-materials-manufacturing/technology.md", 5): r"""## 5. Matter, energy, force, or information flow

- **Matter:** Feedstock becomes product, recyclable return, process consumables, emissions, chips, support material, slag, sludge, off-specification material, or retained contamination.
- **Energy:** Electrical, chemical, optical, thermal, hydraulic, or mechanical inputs are transferred and dissipated across the machine, workpiece, environment, and utilities.
- **Loads:** Forces, moments, pressure, and contact tractions pass through tools, fixtures, frames, bearings, and workpieces; local stress and deformation need not follow a simple one-dimensional path.
- **Information:** Requirements, geometry, material identity, machine state, calibration, process data, inspection, nonconformance, and disposition records form a controlled information chain. G-code is one possible machine representation, not a universal manufacturing language.
""",
    ("technology/17-materials-manufacturing/technology.md", 7): r"""## 7. Design constraints

- **Processability:** A route must match material state, chemistry, rheology, temperature range, atmosphere, joining response, and damage tolerance.
- **Geometry and access:** Internal passages, thin walls, overhangs, tool reach, fixturing, powder removal, support removal, and inspection access constrain feasible shapes.
- **Accuracy and surface integrity:** Capability depends on machine, process, material, feature size, orientation, thermal history, measurement, and post-processing; no process owns one universal tolerance class.
- **Volume and change rate:** Tooling cost, setup, cycle time, material utilisation, automation, qualification, and design stability determine economics. Additive manufacturing can still require fixtures, supports, build plates, and post-processing.
- **Qualification and supply:** Material lots, parameter changes, software versions, maintenance, operators, suppliers, and test methods require configuration control.
""",
    ("technology/17-materials-manufacturing/technology.md", 9): r"""## 9. Reliability and failure modes

Defects and variation arise from coupled mechanisms rather than one parameter alone. Casting failures can involve filling, gas, inclusions, shrinkage, segregation, mould reactions, and residual stress. Forming can produce laps, cracks, texture, springback, nonuniform strain, and tooling damage. Machining can create dimensional error, burrs, altered layers, chatter, tensile residual stress, or thermal damage. Additive failures can involve feedstock variation, recoating, lack of fusion, keyhole instability, contamination, support failure, residual stress, distortion, and anisotropy. A defect's significance depends on location, size, orientation, detectability, load, environment, and acceptance rule.
""",
    ("technology/17-materials-manufacturing/explore.md", 4): r"""## 4. Thought experiments

- **Defect-free-crystal model:** Compare the ideal shear strength of a defect-free lattice with the much lower stress at which dislocations move in an annealed engineering crystal. Why do surfaces, interfaces, thermal fluctuations, and nucleation make a macroscopic perfect crystal an idealisation rather than a realizable test object?
- **Repeated wire drawing:** Model how area reduction, dislocation structure, texture, residual stress, surface damage, intermediate annealing, and die friction change strength and ductility. Why is there no single universal “shatter limit” determined only by dislocation density?
""",
    ("technology/17-materials-manufacturing/explore.md", 7): r"""## 7. Self-explanation questions

- Explain why hot working can reduce required flow stress and enable recovery or recrystallisation, while also introducing oxidation, grain growth, temperature gradients, or dimensional challenges.
- Distinguish elastic strain, recoverable anelasticity, plasticity, damage, and fracture. Which descriptions belong at atomic, defect, microstructural, and continuum scales?
- Ceramics cover glasses, single crystals, polycrystals, porous bodies, composites, and transformation-toughened materials. Explain why limited slip, flaws, interfaces, residual stress, environment, and toughening mechanisms matter more than the slogan “covalent bonds make ceramics brittle.”
""",
    ("technology/17-materials-manufacturing/explore.md", 8): r"""## 8. Transfer questions

- Precipitation hardening controls nanoscale phases in selected alloys. Compare this with hydration, supplementary cementitious reactions, aggregate interfaces, porosity, and reinforcement in concrete. Which ideas transfer, and which mechanisms are fundamentally different?
- For an additively manufactured and a cast metal part of the same nominal alloy and geometry, list the thermal-history, orientation, porosity, surface, residual-stress, heat-treatment, and inspection evidence needed before comparing properties.
""",
    ("technology/18-semiconductors-electronics/overview.md", 1): r"""## 1. The central questions

How do material states, interfaces, fields, and carrier populations create controllable electronic behaviour? How are device characteristics converted into noise-tolerant logic, memory, sensing, communication, and power conversion? How do fabrication, metrology, architecture, packaging, software, workload, and reliability determine system performance beyond the behaviour of one transistor?
""",
    ("technology/18-semiconductors-electronics/overview.md", 7): r"""## 7. Definitions of symbols and units

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
""",
    ("technology/18-semiconductors-electronics/overview.md", 9): r"""## 9. Spatial and temporal scales

Electronic structure begins at atomic and unit-cell scales, while depletion widths, channels, interconnects, vias, packages, boards, and systems span nanometres to metres. Industrial node names do not directly specify one physical dimension. Characteristic times range from carrier scattering and dielectric response through device switching, interconnect propagation, memory access, clock periods, thermal transients, ageing, and product lifetimes. A processor's instruction rate cannot be inferred from transistor transit time or clock frequency alone.
""",
    ("technology/18-semiconductors-electronics/technology.md", 1): r"""## 1. Scientific principles used

Electronics uses quantum and statistical descriptions of solids, electrostatics, carrier transport, electromagnetism, thermodynamics, materials science, and circuit theory. Doping is one method of controlling carrier populations; heterostructures, gates, contacts, geometry, strain, defects, illumination, temperature, and phase also matter. Diodes and transistors implement nonlinear current–voltage and charge–voltage relations; “one-way valve,” “variable resistor,” and “perfect switch” are limited circuit analogies.
""",
    ("technology/18-semiconductors-electronics/technology.md", 2): r"""## 2. The engineering problem

Hardware engineering must realise specified computation, memory, communication, sensing, or power-conversion functions within limits on correctness, delay, energy, temperature, area, manufacturability, yield, reliability, cost, supply, and lifecycle impact. Device scaling is only one strategy. Architecture, memory hierarchy, interconnect, packaging, accelerators, redundancy, software, and workload mapping determine whether device capability becomes useful system performance.
""",
    ("technology/18-semiconductors-electronics/technology.md", 3): r"""## 3. Main components

- **Substrates and active materials:** Silicon is widespread, but compound semiconductors, wide-band-gap materials, thin films, and heterogeneous integration serve different functions.
- **Devices:** MOSFETs, diodes, bipolar devices, memory elements, photonic devices, sensors, and power devices use different structures and operating regimes.
- **Interconnect and dielectrics:** Conductors, barriers, vias, insulators, and interfaces connect and isolate devices while adding resistance, capacitance, inductance, stress, and failure modes.
- **Circuits and architecture:** Standard cells, analog blocks, memories, clocking, power delivery, processors, accelerators, and interfaces organise device behaviour.
- **Package and board:** Mechanical support, cooling, power, signal escape, protection, test access, and external connections extend beyond the die.
- **Manufacturing and test:** Crystal growth, deposition, patterning, doping, etching, cleaning, planarisation, metrology, inspection, packaging, and electrical test create and screen the product.
""",
    ("technology/18-semiconductors-electronics/technology.md", 4): r"""## 4. How the components interact

In a CMOS inverter, complementary devices share an input and drive an output node. Input-voltage ranges, transistor sizing, load capacitance, supply, temperature, leakage, and process variation determine transfer characteristic, delay, energy, and noise margin. “On” and “off” describe useful operating regions, not perfect conduction and insulation. Gates combine into sequential and combinational circuits, but processors also require clocks, memories, interconnect, power delivery, I/O, verification, firmware, and software.
""",
    ("technology/18-semiconductors-electronics/technology.md", 6): r"""## 6. System architecture

One useful hierarchy is material and interface → device → circuit → functional block → microarchitecture → instruction-set interface → software-visible system. The mapping is many-to-many: one physical principle supports several devices, one logic function has several circuit implementations, and one instruction set can have many microarchitectures. Analog, mixed-signal, memory, photonic, power, and sensor systems do not follow one CPU-centred chain. Verification and metrology connect every level back to requirements.
""",
    ("technology/18-semiconductors-electronics/technology.md", 9): r"""## 9. Reliability and failure modes

- **Interconnect degradation:** Current density, temperature, stress, microstructure, interfaces, and geometry influence electromigration and related void or extrusion formation.
- **Dielectric and interface degradation:** Electric field, temperature, defects, charge trapping, and time contribute to breakdown and threshold drift.
- **Bias and hot-carrier ageing:** Operating bias can create or activate defects and change device parameters.
- **Thermomechanical damage:** Temperature gradients and cycling interact with package geometry, solder, underfill, dielectrics, and coefficients of thermal expansion.
- **Radiation and transient faults:** Ionising particles or electrical transients can disturb stored or computed state without permanent damage; sensitivity depends on technology, node, circuit, environment, and protection.
- **Systematic and random defects:** Design errors, process excursions, contamination, variation, and test escape require prevention, screening, redundancy, correction, and field monitoring.
""",
    ("technology/18-semiconductors-electronics/explore.md", 1): r"""## 1. Observation prompts

- Use built-in telemetry during ordinary use only; do not intentionally overheat or stress a device. Compare reported temperature, power, utilisation, brightness, charging, and workload while recognising that sensor placement and software estimates limit interpretation.
- Study a manufacturer diagram or safe photograph of a photovoltaic module. Identify cells, busbars, fingers, encapsulation, bypass elements, and shading trade-offs without touching installed electrical equipment.
- Compare recorded LED and incandescent turn-off transients. Driver capacitance, phosphor persistence, thermal inertia, and camera exposure can affect the observation, so turn-off appearance alone does not identify one emission mechanism.
""",
    ("technology/18-semiconductors-electronics/explore.md", 4): r"""## 4. Thought experiments

- **Relay scaling model:** Given a specified relay volume, switching time, coil energy, contact life, and component count, calculate size, delay, power, and reliability. Which assumptions fail when extrapolated to a processor?
- **Large-gap limit:** Increase band-gap energy in a model while keeping defects, contacts, fields, and dopants specified. Why does “infinite band gap” leave the model's physical domain rather than define a manufacturable perfect insulator?
- **Ultrathin gate stack:** As dimensions approach atomic scales, discuss tunnelling, interface states, variability, quantum confinement, electrostatics, reliability, and the limits of a classical long-channel model.
""",
    ("technology/18-semiconductors-electronics/explore.md", 6): r"""## 6. Model-building prompts

- Build a charge-accounting model of an abrupt p–n junction. Represent ionised dopants, reduced mobile-carrier density, electric field, and potential separately; do not portray holes as empty beads that simply disappear at the boundary.
- Compare schematic band diagrams for a metal, intrinsic semiconductor, doped semiconductor, and insulator under stated temperature and equilibrium conditions. Mark Fermi level and explain why a class label is not determined by band gap alone.
- Construct NAND-based Boolean functions in a simulator, then add propagation delay, fan-out, unknown state, or noise-margin constraints to separate logical universality from a physical implementation.
""",
    ("technology/18-semiconductors-electronics/explore.md", 8): r"""## 8. Transfer questions

- Compare a photovoltaic junction with a chemical or biological field-effect sensor. Which parts of the transduction chain involve carrier generation, surface potential, selective chemistry, amplification, calibration, and interference?
- Instead of one “end of Moore's law,” identify separate limits and opportunities in devices, interconnect, memory, packaging, architecture, algorithms, photonics, quantum systems, and economics.
- Compare an artificial neural-network computation graph with biological neural tissue only at explicitly chosen levels such as connectivity, dynamics, learning signal, energy, and embodiment. Why do matching component counts not establish functional or cognitive equivalence?
""",
    ("technology/18-semiconductors-electronics/explore.md", 10): r"""## 10. Reasoning notes

Separate electronic structure from semiclassical transport, device behaviour from compact models, Boolean function from circuit voltage, and transistor count from system performance. Classical circuit and transport models remain useful within validated regimes; quantum theory does not replace every engineering abstraction. State temperature, bias, geometry, statistics, contacts, measurement, and uncertainty before extending a device explanation to an integrated system.
""",
    ("technology/19-software-ai/overview.md", 1): r"""## 1. The central questions

How can physical states encode and transform abstract information with stated reliability, latency, and resource use? How do independently operated systems communicate across trust and failure boundaries? How can data-driven models support defined tasks, and how should their validity, uncertainty, rights, security, human oversight, and social consequences be governed across deployment?
""",
    ("technology/19-software-ai/overview.md", 7): r"""## 7. Definitions of symbols and units

- $H(X)$: Shannon entropy of random variable $X$, bits when base-2 logarithms are used.
- $p(x)$: probability mass assigned to outcome $x$, dimensionless.
- $C$: capacity of the stated channel model, bit/s.
- $B$: channel bandwidth in the Shannon–Hartley model, Hz.
- $S,N$: average signal and noise powers over the stated bandwidth, W; $S/N$ is dimensionless.
- $\theta_k$: parameter vector at iteration $k$; units depend on parameterisation.
- $\widehat{\nabla L}(\theta_k)$: exact, stochastic, or approximate loss-gradient estimate with units of loss per parameter.
- $\alpha_k$: step size; units must make the update dimensionally consistent.
- $\mathbf x,\mathbf w$: input and weight vectors with model-dependent units.
- $b$: bias or intercept with units compatible with $\mathbf w^{\mathsf T}\mathbf x$.
- $f$: activation or response function.
- $y$: model output with task-dependent units or interpretation.
""",
    ("technology/19-software-ai/overview.md", 9): r"""## 9. Spatial and temporal scales

Computing spans device and package dimensions, boards and data centres, local and wide-area networks, and global organisational dependencies. Time scales span hardware switching and propagation, operating-system scheduling, storage and network delay, user interaction, model training, deployment monitoring, patching, incident response, and archival retention. Values vary by technology and workload; neither transistor dimensions nor parameter count determines one universal latency or training duration.
""",
    ("technology/19-software-ai/overview.md", 11): r"""## 11. Connections to other modules

- **04-probability-statistics:** Supports uncertainty models, estimation, experimental design, calibration, causal questions, and evaluation.
- **05-computation-algorithms:** Provides models of computation, complexity, numerical limits, data structures, optimisation, verification, and algorithm design.
- **18-semiconductors-electronics:** Describes much of the physical substrate of contemporary digital computing, memory, networking, and accelerators while leaving room for photonic, quantum, and other architectures.
- **20-sensors-control-infrastructure:** Connects software and AI to measurement, actuation, timing, safety, operational technology, and human authority in physical systems.
""",
    ("technology/19-software-ai/technology.md", 1): r"""## 1. Scientific principles used

Information theory bounds compression and communication for stated probabilistic models. Probability, statistics, optimisation, numerical analysis, and experimental design support inference and evaluation but do not guarantee deployment validity. Logic, automata, complexity, programming-language semantics, distributed-systems models, cryptography, human factors, and semiconductor physics constrain different layers of a computing system.
""",
    ("technology/19-software-ai/technology.md", 2): r"""## 2. The engineering problem

The problem is to provide a defined service under limits on correctness, availability, latency, throughput, privacy, security, safety, energy, cost, maintainability, and accountability despite hardware faults, software defects, hostile inputs, changing data, dependency failures, and human use. “Reliable,” “scalable,” and “intelligent” require measurable service-level and task definitions rather than being treated as intrinsic system properties.
""",
    ("technology/19-software-ai/technology.md", 4): r"""## 4. How the components interact

Applications use operating-system and runtime interfaces, local libraries, storage, network transports, identity services, databases, queues, and external APIs according to a particular architecture. A request may use TCP, UDP, or QUIC; data may be relational, document, object, stream, graph, or file based. An AI-enabled service may combine retrieval, deterministic rules, one or more models, tools, policy checks, human review, logging, monitoring, and fallback. Interface contracts, authentication, schema, timing, retries, idempotency, provenance, and failure semantics must be explicit.
""",
    ("technology/19-software-ai/technology.md", 11): r"""## 11. Environmental and lifecycle considerations

Computing impacts depend on device manufacture, hardware lifetime, electricity source, utilisation, cooling, water, data movement, software efficiency, retraining, serving, storage, network infrastructure, and end-of-life treatment. Data-centre and model claims require a stated facility, workload, location, time, and accounting boundary. Security updates can extend useful life, while unsupported software, incompatible requirements, or inefficient workloads can drive replacement. Repair, reuse, longer support, efficient algorithms, right-sized hardware, and responsible recycling involve technical and organisational trade-offs.
""",
    ("technology/19-software-ai/technology.md", 12): r"""## 12. Connections to other technologies

- **Cloud and distributed computing:** Combine virtualisation or containers where useful with physical hosts, networks, storage, identity, orchestration, observability, and organisational controls.
- **Cyber-physical systems:** Couple software decisions to sensors, actuators, timing, protection, operators, and physical consequences.
- **Cryptography and security engineering:** Use mathematical constructions together with key management, implementation, protocols, identity, access control, usability, monitoring, and recovery.
- **Data and AI systems:** Depend on governance, provenance, evaluation, deployment controls, human oversight, and incident response as well as models and computation.
""",
    ("technology/19-software-ai/explore.md", 3): r"""## 3. Worked reasoning examples

**Problem:** Compare the entropy of a fair binary source with a source where one outcome has probability $0.9$.

For probabilities $p$ and $1-p$,
$$H=-p\log_2p-(1-p)\log_2(1-p).$$
The fair source has $H=1$ bit per symbol. The $0.9/0.1$ source has approximately $0.469$ bit per symbol. These are ensemble averages under the stated model. One isolated binary outcome still needs a representation agreed by sender and receiver; entropy bounds expected code length across repeated or block-coded symbols rather than assigning a fractional physical bit to one event.
""",
    ("technology/19-software-ai/explore.md", 6): r"""## 6. Model-building prompts

- Build a paper packet-routing model with addressed cards, several nodes, two possible routes, a queue, a dropped packet, and a routing update. Record which behavior belongs to forwarding, routing, transport retry, and application semantics.
- Design a small decision tree for a low-stakes fictional choice. Define inputs, missing values, thresholds, target, cost of each error, validation examples, and an abstain path rather than treating the tree as an objective decision-maker.
""",
    ("technology/19-software-ai/explore.md", 7): r"""## 7. Self-explanation questions

- Explain why an already compressed file often changes little or grows under another compressor. Include algorithm mismatch, headers, finite length, and the difference between measured file structure and source-model entropy.
- Compare IP best-effort delivery with TCP's reliable ordered byte stream and with UDP or QUIC. Which guarantees still belong to the application?
- Improve the “blindfolded hill” analogy for gradient descent by adding local slope, noisy estimates, step size, constraints, flat directions, saddles, and multiple basins. Which aspects of high-dimensional optimisation remain hidden by the analogy?
""",
    ("technology/19-software-ai/explore.md", 9): r"""## 9. Suggested learning paths

- **Information:** Begin with probability and coding examples before reading selected parts of Shannon's paper; distinguish theorem assumptions from implementation.
- **Networks:** Study layering, packet forwarding, routing, transports, naming, congestion, security, and application semantics. Packet switching supports statistical sharing and alternate paths but does not by itself guarantee resilience.
- **Software systems:** Connect operating systems, databases, distributed failure models, testing, security, and recovery.
- **Machine learning and AI:** Start with simple reproducible models and datasets. Add train/validation/test separation, calibration, distribution shift, privacy, threat models, documentation, and human oversight before increasing model complexity.
""",
    ("technology/20-sensors-control-infrastructure/overview.md", 1): r"""## 1. The central questions

How do engineered systems measure variables, estimate hidden state, choose constrained actions, and verify physical response? Under what models and operating regions are stability, performance, safety, and robustness claims valid? How do these ideas scale to infrastructure in which variable resources, stored energy, networks, markets, protection, operators, cybersecurity, maintenance, and recovery interact?
""",
    ("technology/20-sensors-control-infrastructure/overview.md", 2): r"""## 2. Observable phenomena

A thermostat cycles or modulates equipment while room temperature responds slowly. A robot rejects some disturbances but exhibits delay, compliance, saturation, and residual error. A grid maintains service through continuous coordination of generation, storage, demand, networks, controls, protection, and operators; faults can be isolated, but no smart-grid function guarantees blackout prevention. Observations must distinguish commanded state, measured state, estimated state, physical state, and service outcome.
""",
    ("technology/20-sensors-control-infrastructure/overview.md", 7): r"""## 7. Definitions of symbols and units

- $t,\tau$: time and integration variable, s.
- $e(t)$: reference-minus-measurement error under the stated sign convention, units of the controlled variable.
- $u(t)$: controller output, actuator command, or manipulated variable with system-specific units.
- $K_p,K_i,K_d$: gains whose units make proportional, integral, and derivative terms compatible with $u$.
- $\mathbf x,\mathbf u,\mathbf w$: state, input, and disturbance vectors with component-specific units.
- $\mathbf y,\mathbf v$: output and measurement-noise vectors with component-specific units.
- $A,B,C,D,E$: state-space matrices with units determined by the selected states, inputs, outputs, and time unit.
- $\underline S$: complex power under the stated sinusoidal convention, VA.
- $P,Q$: active and reactive power, W and var.
- $\underline V_{rms},\underline I_{rms}$: RMS voltage and current phasors, V and A.
- $\phi$: voltage-current phase difference for the simple sinusoidal scalar form, rad.
- $j$: imaginary unit, $j^2=-1$.
""",
    ("technology/20-sensors-control-infrastructure/overview.md", 9): r"""## 9. Spatial and temporal scales

Sensor physics can occur within microscopic structures while installations span machines, buildings, cities, regions, and interconnected grids. Time scales range from power-electronic switching, sampling, and protection through mechanical motion, thermal processes, dispatch, maintenance, asset ageing, and recovery. Required response time is architecture- and hazard-specific; “grid control” is not one single millisecond-to-second loop.
""",
    ("technology/20-sensors-control-infrastructure/overview.md", 11): r"""## 11. Connections to other modules

- **10-electricity-magnetism:** Supports fields, machines, power conversion, grounding, electromagnetic compatibility, and many transducers.
- **11-waves-signals:** Supports sampling, filtering, communication, spectral analysis, timing, and signal integrity.
- **18-semiconductors-electronics:** Provides sensing elements, embedded processors, memory, interfaces, power devices, and communication hardware.
- **19-software-ai:** Provides algorithms, operating systems, networks, data systems, security, and model evaluation; machine learning is optional and must remain inside validated safety and authority boundaries.
""",
    ("technology/20-sensors-control-infrastructure/technology.md", 1): r"""## 1. Scientific principles used

Automation and infrastructure combine mechanics, electromagnetism, thermodynamics, transport, signal processing, estimation, control, computation, communication, human factors, and reliability engineering. Semiconductor devices support controllers, interfaces, power conversion, and many sensor readouts; photovoltaic cells are energy-conversion devices unless deliberately used as photodetectors. Each principle applies through a model with stated scale and operating limits.
""",
    ("technology/20-sensors-control-infrastructure/technology.md", 2): r"""## 2. The engineering problem

The problem is to deliver a defined physical service within constraints on safety, stability, accuracy, energy, time, availability, security, maintainability, cost, and human authority despite disturbances, uncertainty, failures, and changing conditions. In power systems, electrical energy production, storage, transfer, conversion, and demand must remain dynamically compatible with network and equipment limits; “generation must equal consumption instantaneously” is an incomplete accounting shorthand.
""",
    ("technology/20-sensors-control-infrastructure/technology.md", 3): r"""## 3. Main components

- **Measurement chain:** sensing element, excitation where required, analogue front end, filtering, conversion, timestamp, calibration, diagnostics, and communication.
- **Estimator and controller:** software or hardware that combines measurements, models, references, constraints, and supervisory mode.
- **Actuator and energy path:** drive, valve, motor, converter, breaker, heater, or other mechanism with amplitude, rate, thermal, and energy limits.
- **Plant and environment:** the physical process, load, network, disturbances, and human interaction.
- **Protection and safety:** independent trips, limits, guards, brakes, relief, alarms, emergency systems, and procedures.
- **Communication and operations:** local buses, wide-area links, clocks, identity, cybersecurity controls, operators, maintenance, and recovery resources.
""",
    ("technology/20-sensors-control-infrastructure/technology.md", 5): r"""## 5. Matter, energy, force, or information flow

Measurements and commands carry information with stated timing, integrity, availability, and uncertainty requirements; not every loop needs the lowest possible latency. Energy flows through sources, storage, converters, networks, actuators, loads, losses, and the environment. Forces and moments act through mechanical structures and contacts. Material flows may matter in thermal, fluid, chemical, transport, and industrial plants. A control diagram that omits the energy or material path can hide saturation and hazard.
""",
    ("technology/20-sensors-control-infrastructure/technology.md", 7): r"""## 7. Design constraints

- **Timing:** Sampling, computation, communication, actuation, jitter, and clock synchronisation must fit the plant and hazard timescales.
- **Observability and diagnostics:** Sensor placement, calibration, redundancy, and fault detection determine which states and failures can be inferred.
- **Control authority:** Actuator amplitude, rate, energy, dead zone, backlash, and thermal limits constrain achievable performance.
- **Environment and compatibility:** Temperature, vibration, moisture, corrosion, radiation, electromagnetic interference, and installation affect equipment and signals.
- **Safety and security:** Independent protection, access control, segmentation, safe states, fail-operational needs, and recovery must coexist with availability.
- **Economics and governance:** Precision, redundancy, maintenance, staffing, regulation, interoperability, supply, and lifecycle cost shape the architecture.
""",
    ("technology/20-sensors-control-infrastructure/technology.md", 12): r"""## 12. Connections to other technologies

- **Data and AI systems:** May support forecasting, anomaly detection, maintenance, or decision support, but require validated data, uncertainty, monitoring, cybersecurity, and human authority.
- **Telecommunications and timing:** Fibre, radio, wired fieldbuses, and dedicated operational networks serve different latency, coverage, availability, and security requirements; no single generation of mobile technology is universally required.
- **Power electronics and storage:** Convert and buffer energy while adding controls, limits, harmonics, thermal behaviour, and protection requirements.
- **Manufacturing and metrology:** Build, calibrate, inspect, maintain, and replace the physical components of automation and infrastructure.
""",
    ("technology/20-sensors-control-infrastructure/explore.md", 2): r"""## 2. Prediction questions

- In a simulated temperature loop, increase derivative gain while varying sensor noise, derivative filtering, door-disturbance size, sampling, and actuator saturation. Which outcomes are actually determined by $K_d$ alone?
- As rooftop solar increases, distinguish customer demand from grid net load. Predict midday and evening effects only after weather, orientation, storage, tariffs, feeder constraints, and geographic diversity are specified.
- For a simulated robotic arm carrying a payload, identify inertia, gravity, friction, compliance, resonance, actuator limits, structural loads, trajectory, uncertainty, and safety constraints before predicting overshoot.
""",
    ("technology/20-sensors-control-infrastructure/explore.md", 4): r"""## 4. Thought experiments

- **Ideal rigid massless arm:** Removing inertia and flexibility also removes important energy storage and dynamics, potentially making the model singular or physically meaningless. Which controller questions disappear, and which limits—actuator, sensing, timing, geometry, and contact—remain?
- **Islanded power system:** Given a wind profile, battery power and energy limits, inverter controls, reserve policy, load priorities, and protection settings, trace several possible responses to lost wind. Why can no controller promise “no flicker” without adequate stored energy, power capacity, network support, and validated transitions?
""",
    ("technology/20-sensors-control-infrastructure/explore.md", 6): r"""## 6. Model-building prompts

- Derive a mass–spring–damper state-space model after defining state order, input force, measured output, sign convention, and units. Check matrix dimensions, eigenvalues, controllability, and how parameter uncertainty changes predictions.
- Draw a drone-altitude architecture including reference, estimator, controller, motor drive, vehicle dynamics, altimeter, delay, disturbance, saturation, protection, operator authority, and emergency mode. Distinguish the error signal from the full estimated state.
- Build a grid-service diagram that separates energy adequacy, active-power balance, voltage, frequency, thermal limits, protection, communication, markets, operators, and restoration.
""",
}

REQUIRED_FINAL_MARKERS = {
    "technology/17-materials-manufacturing/overview.md": ("d_{hkl}", "d_g", "amount per area per time"),
    "technology/17-materials-manufacturing/technology.md": ("configuration control", "no process owns one universal tolerance class"),
    "technology/17-materials-manufacturing/explore.md": ("no single universal", "covalent bonds make ceramics brittle"),
    "technology/18-semiconductors-electronics/overview.md": ("N_D,N_A", "instruction rate cannot be inferred"),
    "technology/18-semiconductors-electronics/technology.md": ("many-to-many", "Radiation and transient faults"),
    "technology/18-semiconductors-electronics/explore.md": ("do not intentionally overheat", "matching component counts"),
    "technology/19-software-ai/overview.md": ("\theta_k", "photonic, quantum"),
    "technology/19-software-ai/technology.md": ("idempotency", "right-sized hardware"),
    "technology/19-software-ai/explore.md": ("ensemble averages", "Packet switching supports statistical sharing"),
    "technology/20-sensors-control-infrastructure/overview.md": ("A,B,C,D,E", "not one single"),
    "technology/20-sensors-control-infrastructure/technology.md": ("Photovoltaic cells are energy-conversion devices", "no single generation"),
    "technology/20-sensors-control-infrastructure/explore.md": ("grid net load", "model singular"),
}

_original_transform = phase9.transform
_original_validate = phase9.validate


def transform(path, module):
    text, notes = _original_transform(path, module)
    rel = path.relative_to(phase9.ROOT).as_posix()
    for (target, number), replacement in POST_SECTIONS.items():
        if target == rel:
            text = phase9.replace_numbered_section(text, number, replacement)
            notes.append(f"final section {number}")
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return text, notes


def validate():
    errors = _original_validate()
    for rel, markers in REQUIRED_FINAL_MARKERS.items():
        path = phase9.ROOT / rel
        if not path.exists():
            errors.append(f"{rel}: missing in final Phase 9 pass")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{rel}: final marker missing: {marker}")
    return errors


phase9.transform = transform
phase9.validate = validate

if __name__ == "__main__":
    raise SystemExit(phase9.main())
