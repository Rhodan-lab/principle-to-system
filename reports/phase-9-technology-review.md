# Phase 9 Review — Technology Modules 17–20

> Review date: 2026-07-26  
> Scope: 4 modules, 12 learner-facing files  
> Transition: Draft → Reviewed after coordinated validation  
> Release status: not Complete

## Review standard

Phase 9 applies one coordinated scientific, engineering, editorial, safety, privacy, security, and source review to each module's `overview.md`, `technology.md`, and `explore.md` files. A module is promoted only when all three files pass together.

The review checks:

- scientific and engineering accuracy;
- equations, symbols, dimensions, signs, and operating regimes;
- model assumptions, approximation limits, and scale transitions;
- measurement, calibration, uncertainty, metrology, and qualification;
- system architecture, interfaces, trust boundaries, and failure containment;
- safety, cybersecurity, privacy, human oversight, and authorised use;
- lifecycle, energy, water, material, maintenance, and end-of-life boundaries;
- direct source-to-ledger matching;
- canonical metadata, prerequisites, connections, slugs, and status;
- safe and age-appropriate exploration activities.

Reviewed means the focused gate passed. It does not mean independently certified, production-qualified, or release-ready.

## Module 17 — Materials Science and Manufacturing

### Scientific corrections

- Replaced broad material-class stereotypes with conditional structure–processing–property–performance relationships.
- Distinguished crystalline, amorphous, semicrystalline, multiphase, textured, porous, and composite structures.
- Expanded defects beyond dislocations and tied their effects to arrangement, scale, environment, and loading.
- Clarified equilibrium phase diagrams versus finite-rate transformation, solidification, and metastability models.
- Limited Hall–Petch to an empirical fitted regime rather than a universal nanoscale law.
- Corrected the claim that an ideal defect-free pure crystal is soft.
- Defined yield, hardness, ultimate strength, ductility, fatigue, creep, and toughness as test- and condition-dependent quantities.
- Restricted plane-strain mode-I fracture toughness to the specimen and linear-elastic validity requirements under which `K_Ic` is a material property.
- Corrected the lever rule and added consistent composition-basis requirements.
- Generalised diffusion from constant scalar diffusivity to gradient and divergence forms with chemical-potential and multicomponent limits.

### Manufacturing-system corrections

- Reframed casting, forming, subtractive, additive, joining, inspection, and disposition as coupled process systems.
- Removed the claim that forged parts are automatically superior to cast or machined parts.
- Replaced automatic additive-manufacturing material-efficiency claims with explicit support, failed-build, powder, post-processing, inspection, and recycling boundaries.
- Added process capability, traceable metrology, uncertainty, representative qualification, acceptance criteria, and change control.
- Added digital-thread configuration, provenance, and data-integrity requirements.
- Replaced fixed lifecycle claims with geography-, electricity-, yield-, use-, maintenance-, and end-of-life-dependent accounting.

### Safety corrections

- Removed repeated bending until fracture.
- Removed learner heating and quenching of glowing steel.
- Prohibited learner operation of furnaces, presses, cutting machinery, lasers, powders, chemical baths, and industrial systems.
- Added machine guarding, enclosure, ventilation, hazardous-energy isolation, compatible equipment, emergency planning, and professional risk assessment.
- Added NIOSH metal-powder inhalation, dermal, fire, and explosion boundaries.

## Module 18 — Semiconductors and Electronics

### Scientific corrections

- Replaced fixed band-gap thresholds with band structure, Fermi level, carrier statistics, contacts, disorder, temperature, and dimensional context.
- Clarified holes as quasiparticle descriptions rather than literal empty particles or imaginary conveniences.
- Distinguished dopant concentration, activation, compensation, and free-carrier concentration.
- Corrected the depletion approximation: mobile carrier density is reduced, not literally absent.
- Replaced the ideal one-way-valve diode description with injection, leakage, capacitance, resistance, recombination, and breakdown regimes.
- Reframed BJT action through injection, transport, recombination, and collector fields.
- Reframed MOSFET action through surface potential and continuous carrier-density change; threshold is not a hard on/off boundary.
- Added equilibrium, non-degenerate-statistics, abrupt-junction, low-field, and long-channel assumptions to device equations.
- Clarified that built-in potential is not directly read by placing a voltmeter across equilibrium contacts.
- Replaced literal feature-size interpretation of technology-node names.

### Hardware-system corrections

- Distinguished logical information from charge, current, fields, and energy.
- Added dynamic switching power, leakage, short-circuit, memory, clock, I/O, data-movement, and packaging boundaries.
- Replaced “chip will melt” with realistic throttling, leakage, timing, ageing, packaging, and shutdown failure progression.
- Reframed Moore's observation as economical component-density history rather than a physical law or guaranteed performance trend.
- Added workload, precision, compiler, memory, batch, latency, throughput, energy, temperature, and comparison-baseline requirements.
- Expanded lithography constraints to optics, masks, resist, process window, pattern transfer, overlay, etch, and metrology.
- Added yield, variability, testing, redundancy, packaging, power delivery, signal integrity, and thermal design.

### Safety corrections

- Replaced physical teardown with diagrams, repair documentation, and virtual board inspection.
- Prohibited chemical processing, opening mains-powered electronics, and bypassing thermal or electrical protection.
- Added professional cleanroom containment, monitoring, interlocks, ventilation, compatible materials, and emergency systems.

## Module 19 — Software and AI Foundations

### Scientific and computational corrections

- Replaced universal compression claims with finite-file and metadata-overhead boundaries.
- Reframed Shannon source and channel theorems as asymptotic existence results under stated models.
- Corrected signal-to-noise ratio as a dimensionless ratio before logarithmic conversion to decibels.
- Prevented the noiseless Shannon–Hartley limit from being interpreted as a physical infinite-throughput design.
- Distinguished IP best-effort delivery, TCP byte-stream reliability, application semantics, security, retry, and deadline guarantees.
- Added alternatives such as UDP and QUIC instead of presenting all internet communication as TCP.
- Clarified automatic differentiation and optimisation limits; gradient methods do not guarantee a global optimum for general non-convex systems.
- Replaced categorical “more examples means better AI” and vague emergent-capability claims with reproducible evaluation, contamination, prompting, distribution-shift, and failure-case requirements.
- Replaced “only pattern matching” as a universal conclusion with task-, evidence-, and uncertainty-based capability assessment.

### Software and AI-system corrections

- Expanded architecture to hardware, firmware, operating systems, networks, data systems, ML lifecycle, and organisational controls.
- Added trust boundaries, authentication, rate limiting, policy enforcement, logging, human escalation, rollback, and incident response.
- Reframed database and TCP reliability so WAL, retransmission, replication, and checksums are not treated as unconditional guarantees.
- Added tail latency, overload, consistency, partitions, secure development, least privilege, secrets, data minimisation, consent, and retention.
- Expanded AI evaluation beyond accuracy to task validity, baselines, uncertainty, calibration, subgroup performance, robustness, abstention, privacy, security, misuse, human outcomes, and lifecycle cost.
- Added NIST-style governance, mapping, measurement, management, monitoring, documentation, appeal, shutdown authority, and incident response.

### Safety and privacy corrections

- Restricted browser inspection to authorised pages and prohibited copying credentials, cookies, tokens, or personal data.
- Replaced network probing of third-party servers with own-device, own-router, or reputable public diagnostics.
- Replaced sensitive recommendation observation with fictional or non-sensitive profiles.
- Added high-impact decision requirements for domain-qualified human oversight, uncertainty communication, fallback, logging, appeal, and reversibility.

## Module 20 — Sensors, Control, and Infrastructure

### Scientific and control corrections

- Replaced anthropomorphic “sense–think–act” with measure–condition–sample–estimate–decide–act–verify.
- Distinguished transduction from a universal conversion of one energy form into another.
- Added estimation, observer uncertainty, calibration, bandwidth, sampling, quantisation, delay, and diagnostic status.
- Expanded feedback objectives beyond instantaneous error minimisation.
- Corrected derivative action: it responds to rate and does not literally predict the future.
- Limited integral offset removal to stable loops with adequate control authority and anti-windup handling.
- Added disturbance and measurement-noise terms to state-space models.
- Added linearisation, controllability, observability, sampling, timing, saturation, hysteresis, and model-mismatch boundaries.
- Corrected complex-power notation and limited sinusoidal single-phase equations to the appropriate convention.

### Infrastructure-system corrections

- Added estimator, supervisory logic, drive, independent interlocks, protection, operators, and emergency systems.
- Corrected basic optical encoders: interference is not required, and position is quantised and calibration-dependent rather than exact.
- Reframed smart-inverter support and synthetic inertia as configured capabilities, not automatic properties.
- Distinguished energy adequacy, frequency response, voltage, network congestion, reserves, protection, restoration, reliability, markets, and regulation.
- Added common-cause failure, topology error, spoofing, timing faults, partitions, hidden protection failures, and recovery-test requirements.
- Distinguished fail-safe from fail-operational requirements and persistent stored energy.

### Safety and cybersecurity corrections

- Replaced close observation of power infrastructure with public safe-distance and utility-diagram activities.
- Removed balancing a long object near the learner's face or other people.
- Prohibited connection to, scanning, alteration of, or experimentation on real operational technology or public infrastructure.
- Added defence in depth, segmentation, authenticated access, least privilege, secure remote maintenance, monitoring, tested backup, incident response, and recovery.
- Added independent protection, guarded machinery, verified isolation, emergency procedures, and trained human authority.

## Sources added

Phase 9 declares twelve inspected authoritative records.

### Module 17

- NIST additive manufacturing of metals;
- NIOSH metal-powder additive-manufacturing safety;
- OSHA machine-guarding requirements.

### Module 18

- NIST CHIPS for America Metrology Program;
- NIST review of next-generation semiconductor-device metrology;
- NIST critical-dimension and overlay metrology.

### Module 19

- NIST AI Risk Management Framework 1.0;
- NIST Generative AI Profile;
- IETF RFC 9293 for TCP.

### Module 20

- NIST Cyber-Physical Systems Framework;
- NIST industrial-control-system cybersecurity guidance;
- U.S. Department of Energy Grid Modernization Initiative.

The intended central ledger transition is 131 → 143 records.

## Validation artifacts

- `sources/phase-9-reviewed-sources.json`
- `scripts/apply_phase9_review_sources.py`
- `scripts/apply_phase9_technology_review.py`
- `scripts/validate_phase8_continuity_phase9.py`
- `scripts/validate_phase9_technology_review.py`
- `reports/phase-9-technology-sources.json`
- `.github/workflows/validate-phase-9-technology.yml`

## Status after Phase 9

- Modules 01–05: Reviewed
- Modules 06–12: Reviewed
- Modules 13–16: Reviewed
- Modules 17–20: Reviewed
- Modules 01–20: Reviewed
- no core module is Complete

## Next stage

Phase 10 reconciles the synthesis layer:

1. pathways;
2. crosscutting concepts;
3. knowledge maps;
4. terminology and equations;
5. source and status references;
6. cross-module prerequisite and transfer logic.
