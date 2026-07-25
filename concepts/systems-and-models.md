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

A **system** is a chosen set of entities, states, interactions, and boundaries used to answer a question or deliver a service; its boundary is an analytical and engineering decision, where the interactions produce behaviour that the components alone do not exhibit. A **model** is a simplified representation of a system — mathematical, computational, or conceptual — that captures the relationships relevant to a specific question while deliberately omitting irrelevant detail. Scientific and engineering reasoning uses multiple representations, measurements, theories, experiments, and models; none should be confused with the full physical or social reality.

## Why scientists and engineers use it

No real system can be understood in its full complexity simultaneously. Models allow scientists to isolate mechanisms, make quantitative predictions, and test hypotheses against observation. Engineers use models to simulate performance before building, to identify failure modes, and to optimise designs within constraints. The discipline of defining system boundaries, inputs, outputs, and internal states is the foundation of both scientific analysis and engineering design.

## Demonstrations across modules

### Thermodynamic systems and state functions (Module 08)

Thermodynamics defines three system types: isolated (no exchange of energy or matter), closed (energy exchange only), and open (both). The choice of system boundary determines which conservation laws apply and which quantities are state functions. The ideal gas model $PV = nRT$ captures the essential behaviour of dilute gases by modelling molecules as non-interacting point particles — a deliberate simplification that fails at high pressure (van der Waals corrections) but is useful over a stated dilute-gas regime and fails when interactions, phase change, chemistry, or high density matter.

### Computational simulation as model execution (Module 05)

A numerical simulation is a model made executable. Finite-element analysis discretises a continuous system (a bridge, an airflow, a heat exchanger) into elements small enough that simple equations approximate local behaviour. The model's validity depends on mesh resolution, boundary conditions, and constitutive equations — all choices that define what the model includes and excludes.

### Ecosystem models and trophic networks (Module 15)

An ecosystem can be modelled as a network of energy and nutrient flows between trophic levels. The Lotka–Volterra model captures predator–prey oscillations with two coupled differential equations — a drastic simplification of real food webs, but one that reveals consequences of one idealised interaction structure; real food webs can add density dependence, delay, seasonality, spatial structure, stochasticity, and adaptation. More complex models (food-web matrices, agent-based simulations) add realism at the cost of analytical tractability.

### Control system block diagrams (Module 20)

Engineers represent control systems as block diagrams: each block is a transfer function (a model of a subsystem), and arrows represent signal flow. The entire system's behaviour emerges from the interconnection of these blocks. This abstraction allows analysis of stability, bandwidth, and robustness without knowing the physical details inside each block — input–output models can support analysis, but hidden state, nonlinearities, saturation, uncertainty, safety, and implementation may also matter.

### Software architecture as system design (Module 19)

A software system is decomposed into modules with defined interfaces (APIs). Each module is a model of a responsibility: the database module models data persistence, the network module models communication. The system's emergent behaviour (user-facing functionality) arises from the interaction of these modules, and failures often occur at interfaces — exactly where system boundaries are drawn.

## Common misunderstandings

- **The map is not the territory.** A model is always a simplification. Treating model predictions as exact truths — rather than as approximations valid within stated assumptions — leads to overconfidence and engineering failures.
- **System boundaries are choices, not discoveries.** Where you draw the boundary determines what counts as internal dynamics and what counts as external forcing. Different questions about the same physical reality may require different system definitions.
- **More complex models are not always better.** A model should be as simple as possible for the question being asked (parsimony). Overfitting — adding parameters until the model matches noise — reduces predictive power. Model choice balances purpose, adequacy, identifiability, uncertainty, interpretability, cost, and consequence; simplicity is valuable but not an automatic optimum.
- **Emergent properties are not magic.** When a system exhibits behaviour that its components individually do not, this is emergence. It arises from interactions, not from mysterious holistic forces. A good model of the interactions predicts the emergent behaviour.

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
