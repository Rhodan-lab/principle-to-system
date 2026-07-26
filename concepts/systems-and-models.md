---
title: "Systems and Models"
slug: concept-systems-and-models
domain: crosscutting
status: reviewed
prerequisites: []
connections: [03-mathematical-models, 05-computation-algorithms, 08-energy-thermodynamics, 15-ecosystems-complex-systems, 19-software-ai, 20-sensors-control-infrastructure]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Systems and Models

## Definition

A **system** is a chosen set of entities, states, interactions, environments, and boundaries used for a question or service. Its boundary is an analytical and engineering choice. A **model** is a mathematical, computational, physical, statistical, or conceptual representation designed for a purpose; omitted detail is not necessarily irrelevant for another purpose. Measurements, theories, experiments, simulations, and models provide different evidence and should not be confused with the full physical or social reality.

## Why scientists and engineers use it

Models help isolate mechanisms, organise data, estimate unobserved quantities, compare alternatives, predict conditionally, and test assumptions. Engineers use them before and during operation, but high-consequence decisions also require measurements, verification, validation, margins, monitoring, and human judgement. Boundaries, inputs, outputs, states, disturbances, and stakeholders must match the question.

## Demonstrations across modules

### Thermodynamic systems and state functions (Module 08)

Thermodynamic analyses commonly distinguish isolated, closed, and open control masses or volumes according to allowed transfers. Conservation laws remain fundamental, but their balance terms depend on the boundary. The ideal-gas equation is useful for suitable dilute gas states; real-gas interactions, phase change, chemistry, high density, and non-equilibrium conditions require other models.

### Computational simulation as model execution (Module 05)

A numerical simulation is a model made executable. Finite-element analysis discretises a continuous system (a bridge, an airflow, a heat exchanger) into elements small enough that simple equations approximate local behaviour. The model's validity depends on mesh resolution, boundary conditions, and constitutive equations — all choices that define what the model includes and excludes.

### Ecosystem models and trophic networks (Module 15)

An ecosystem can be modelled as a network of energy and nutrient flows between trophic levels. The Lotka–Volterra model captures predator–prey oscillations with two coupled differential equations — a drastic simplification of real food webs, but one that reveals consequences of one idealised interaction structure; real food webs can add density dependence, delay, seasonality, spatial structure, stochasticity, and adaptation. More complex models (food-web matrices, agent-based simulations) add realism at the cost of analytical tractability.

### Control system block diagrams (Module 20)

Block diagrams represent selected signal and subsystem relations; a block may be a transfer function, nonlinear operator, state-space model, estimator, controller, delay, or logic element. Interconnection supports analysis, but hidden state, sampling, saturation, uncertainty, physical energy flow, safety, cybersecurity, and implementation remain relevant.

### Software architecture as system design (Module 19)

Software can be decomposed into components and interfaces, but architecture varies across processes, services, libraries, data stores, queues, devices, users, and organisations. Interfaces encode contracts and failure semantics; failures can occur within components, across dependencies, through shared infrastructure, or from incorrect system boundaries.

## Common misunderstandings

- **The map is not the territory.** A model is always a simplification. Treating model predictions as exact truths — rather than as approximations valid within stated assumptions — leads to overconfidence and engineering failures.
- **System boundaries are choices, not discoveries.** Where you draw the boundary determines what counts as internal dynamics and what counts as external forcing. Different questions about the same physical reality may require different system definitions.
- **More complex models are not always better.** A model should be as simple as possible for the question being asked (parsimony). Overfitting — adding parameters until the model matches noise — reduces predictive power. Model choice balances purpose, adequacy, identifiability, uncertainty, interpretability, cost, and consequence; simplicity is valuable but not an automatic optimum.
- **Emergence does not guarantee predictability.** Collective behaviour can arise from interactions, constraints, heterogeneity, adaptation, and environment. Even known local rules may be computationally difficult, sensitive, stochastic, or insufficient for reliable macro-level prediction.

## Connections to repository content

- [Module 03: Mathematical Models](../foundations/03-mathematical-models/overview.md) — the language in which models are expressed.
- [Module 05: Computation and Algorithms](../foundations/05-computation-algorithms/overview.md) — executing models as simulations.
- [Module 08: Energy and Thermodynamics](../science/08-energy-thermodynamics/overview.md) — system boundaries and state functions.
- [Module 15: Ecosystems and Complex Systems](../science/15-ecosystems-complex-systems/overview.md) — modelling emergent behaviour.
- [Module 19: Software and AI Foundations](../technology/19-software-ai/overview.md) — software as system architecture.
- [Module 20: Sensors, Control, and Infrastructure](../technology/20-sensors-control-infrastructure/overview.md) — block diagrams and transfer functions.

## Phase 10 synthesis boundaries

- This document is a reviewed route or crosscutting synthesis, not proof that one mechanism, architecture, or historical sequence is inevitable.
- Every equation, quantity, and causal claim inherits the assumptions and validity limits stated in the linked reviewed modules.
- Technology performance depends on architecture, implementation, operating conditions, measurement boundary, lifecycle, safety, security, and human organisation.
- `Reviewed` records focused reconciliation; it does not mean independently certified or release-ready.
