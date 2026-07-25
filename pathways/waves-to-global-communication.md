---
title: "Waves to Global Communication"
slug: pathway-waves-to-global-communication
domain: pathway
status: reviewed
prerequisites: [10-electricity-magnetism, 11-waves-signals, 18-semiconductors-electronics, 19-software-ai]
connections: [05-computation-algorithms, 17-materials-manufacturing]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Waves to Global Communication

This pathway traces how the physics of electromagnetic waves becomes the global communication infrastructure — from Maxwell's equations to the internet.

---

## Stage 1: Electromagnetic wave propagation

**Mechanism used:** Maxwell's equations admit electromagnetic-wave solutions. In vacuum their speed is the defined constant $c$; in materials, propagation depends on constitutive response, dispersion, loss, geometry, and mode. Antennas and other sources radiate when charge-current distributions vary appropriately in time.

**Abstraction introduced:** The *electromagnetic spectrum* — a continuum of frequencies from radio waves (kHz–GHz) through microwaves, infrared, visible light, ultraviolet, X-rays, to gamma rays, all governed by the same wave equation but interacting differently with matter.

**Engineering problem solved:** Transmitting information without physical wires, at the speed of light, through free space or guided media.

**Trade-off:** Propagation and usable bandwidth depend on allocation, antenna aperture, environment, absorption, diffraction, scattering, weather, blockage, regulation, coding, power, interference, and geometry. Frequency alone does not determine capacity, coverage, or whether a route is line of sight.

**Prerequisite knowledge:** [Module 10 — Electricity and Magnetism](../science/10-electricity-magnetism/overview.md), [Module 11 — Waves and Signals](../science/11-waves-signals/overview.md)

---

## Stage 2: Modulation — encoding information onto waves

**Mechanism used:** A transmitter maps symbols to waveform amplitude, phase, frequency, timing, code, or spatial mode. Occupied spectrum depends on pulse shape, symbol rate, filtering, coding, nonlinearity, regulation, and measurement convention. The Shannon–Hartley expression applies to an ideal bandwidth-limited additive white Gaussian-noise channel, not every radio link.

**Abstraction introduced:** The *channel model* — a stated probabilistic or deterministic relation between transmitted and received signals, including bandwidth, noise, interference, fading, memory, feedback, and decoding assumptions. Multiple channels can coexist via frequency-division, time-division, or code-division multiplexing.

**Engineering problem solved:** Sharing the electromagnetic spectrum among many simultaneous users without mutual interference, and maximising the information carried per hertz of bandwidth.

**Trade-off:** A higher-order constellation can carry more coded bits per symbol under suitable conditions, but error performance also depends on coding, channel estimation, interference, fading, nonlinearity, phase noise, receiver design, latency, and power constraints.

**Prerequisite knowledge:** [Module 11](../science/11-waves-signals/overview.md), [Module 04 — Probability and Statistics](../foundations/04-probability-statistics/overview.md)

---

## Stage 3: Optical fibre — guiding light

**Mechanism used:** A fibre's refractive-index profile and geometry support guided electromagnetic modes. Ray total-internal-reflection language is a useful approximation in suitable regimes. Attenuation, dispersion, mode coupling, bends, splices, connectors, wavelength, and fibre type determine link performance; no single loss value describes every route.

**Abstraction introduced:** The *optical link* — a point-to-point connection characterised by bandwidth, distance, and bit-error rate, abstracting away the wave optics of mode propagation and dispersion.

**Engineering problem solved:** Carrying high aggregate data rates over long terrestrial or submarine routes through wavelength multiplexing, amplification, coherent detection, coding, dispersion management, repeaters, power feeding, monitoring, and route-specific engineering.

**Trade-off:** Fibre offers enormous bandwidth but requires physical installation (trenching, submarine laying) — high capital cost and long deployment time. Chromatic and polarisation-mode dispersion limit reach without compensation, requiring digital signal processing at each end.

**Prerequisite knowledge:** [Module 11](../science/11-waves-signals/overview.md), [Module 17 — Materials Science](../technology/17-materials-manufacturing/overview.md)

---

## Stage 4: Digital signal processing and error correction

**Mechanism used:** Under stated band-limit and filtering assumptions, samples can preserve the information needed to reconstruct a signal model. Quantisation maps samples to finite representations. Forward-error-correction codes add structured redundancy so a decoder can estimate transmitted data under a specified channel and error criterion.

**Abstraction introduced:** The *bit stream* — a logical sequence represented by physical states under encoding, timing, framing, and error conventions. It separates many processing tasks from a specific medium without making implementation or semantics irrelevant.

**Engineering problem solved:** Reliable communication over noisy channels. Turbo codes and LDPC codes can approach information-theoretic bounds for stated channel models as block length and complexity grow, while finite systems trade error probability, latency, energy, rate, and implementation cost.

**Trade-off:** Stronger error correction requires more redundancy (lower effective data rate) and more computational power for decoding. Latency-sensitive applications (voice, gaming) must balance error resilience against processing delay.

**Prerequisite knowledge:** [Module 05 — Computation and Algorithms](../foundations/05-computation-algorithms/overview.md), [Module 18 — Semiconductors](../technology/18-semiconductors-electronics/overview.md)

---

## Stage 5: Packet switching and the Internet Protocol

**Mechanism used:** Data is divided into packets, each labelled with source and destination addresses. Routers forward IP datagrams using routing and forwarding state. Ordering, retransmission, congestion control, security, and application semantics are handled by other layers or protocols when required. This statistical multiplexing shares link capacity efficiently among bursty users.

**Abstraction introduced:** The *network layer* (IP) — a uniform addressing and routing scheme that makes the physical medium (fibre, copper, radio) invisible to applications. IP supplies a common network-layer addressing and forwarding model, while reachability still depends on routing, policy, translation, firewalls, naming, identity, and application protocols, regardless of the underlying link technology.

**Engineering problem solved:** Scalable, heterogeneous internetworking across independently operated links and networks. Layering reduces selected coupling, while naming, routing, policy, security, power, cloud concentration, cables, dependencies, and organisations still create shared risks.

**Trade-off:** Packet networks trade statistical sharing against queueing, loss, reordering, overhead, congestion, and tail latency. Service quality can use admission, scheduling, reservation, adaptation, redundancy, or capacity planning. End-to-end arguments guide function placement but do not make the network intrinsically simple.

**Prerequisite knowledge:** [Module 19 — Software and AI Foundations](../technology/19-software-ai/overview.md)

---

## Stage 6: Wireless access — the last mile

**Mechanism used:** Cellular systems coordinate coverage areas, base stations, users, spectrum, scheduling, handover, coding, and power. Spatial reuse and multi-antenna processing can improve capacity or reliability when channel rank, interference, geometry, hardware, and channel knowledge support them.

**Abstraction introduced:** The *wireless channel model* — a statistical description of signal fading, interference, and capacity that allows network planning without deterministic ray-tracing of every environment.

**Engineering problem solved:** Connecting mobile users to the fibre backbone at broadband speeds, anywhere within coverage. Modern cellular systems combine licensed spectrum, coding, scheduling, antenna arrays, handover, power control, backhaul, and deployment density; realised rate and coverage are environment- and load-dependent.

**Trade-off:** Spectrum access, coverage, capacity, latency, energy, mobility, interference, infrastructure density, backhaul, cost, and equity interact. More traffic can be managed through many architectural choices, each with deployment and governance constraints.

**Prerequisite knowledge:** [Module 11](../science/11-waves-signals/overview.md), [Module 18](../technology/18-semiconductors-electronics/overview.md)

---

## Summary chain

```text
Maxwell's equations (electromagnetic wave propagation)
→ modulation (encoding information onto carrier waves)
→ optical fibre (guiding light over long distances)
→ digital signal processing (reliable bit streams over noisy channels)
→ packet switching / IP (scalable, heterogeneous internetworking)
→ cellular wireless (mobile access to the network)
→ global communication
```

Each stage converts a physical phenomenon into an engineering abstraction, solves a specific connectivity problem, and introduces a constraint (bandwidth, noise, latency, spectrum scarcity) that the next stage must manage.

## Phase 10 synthesis boundaries

- This document is a reviewed route or crosscutting synthesis, not proof that one mechanism, architecture, or historical sequence is inevitable.
- Every equation, quantity, and causal claim inherits the assumptions and validity limits stated in the linked reviewed modules.
- Technology performance depends on architecture, implementation, operating conditions, measurement boundary, lifecycle, safety, security, and human organisation.
- `Reviewed` records focused reconciliation; it does not mean independently certified or release-ready.
