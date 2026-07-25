# Principle to System

**Learn how foundational science becomes technology—and how to reason with the systems that result.**

Principle to System is an open-source knowledge repository for curious independent learners. It explains how scientific understanding is built, how that understanding becomes engineered technology, and how real systems can be investigated, redesigned, and understood through their failures.

Every learning module follows the same explanatory arc:

```text
observation
→ scientific concept
→ mechanism
→ mathematical model
→ engineered component
→ technological system
→ limitation and trade-off
```

The experience layer continues the arc:

```text
notice a system
→ choose a boundary
→ identify flows and state variables
→ propose a mechanism
→ build the smallest useful model
→ test it against evidence
→ redesign under constraints
→ explain remaining uncertainty
```

This is not a textbook, exam course, or encyclopaedia of disconnected facts. It is a connected map of causal explanations and reasoning practices: why phenomena happen, how they are modelled, how engineers exploit them, why systems fail, and how evidence should change a design.

## Who this is for

Independent learners who want to understand *why* technology works, not merely *that* it works. No formal enrolment, grades, or assessment framework is assumed. The material uses clear international English and meaningful mathematics, with symbols, units, assumptions, and model limits made explicit.

## How the content is organised

The repository contains 20 core learning modules, synthesis layers that connect them, and experience layers that turn understanding into investigation and design.

| Folder | Contents |
| --- | --- |
| `foundations/` | Modules 01–05: reasoning, measurement, mathematics, probability, and computation |
| `science/` | Modules 06–16: natural science from quantum matter to planetary systems |
| `technology/` | Modules 17–20: materials, electronics, software, control, and infrastructure |
| `concepts/` | Seven crosscutting ideas used across disciplines |
| `pathways/` | Six end-to-end science-to-technology dependency chains |
| `maps/` | Mermaid maps showing prerequisite and enabling relationships |
| `experiences/` | The shared rules and navigation for applied learning experiences |
| `system-dossiers/` | Reverse engineering of familiar technologies across multiple scales |
| `failure-atlas/` | Reusable system-failure patterns, causal maps, and redesign strategies |
| `investigations/` | Safe evidence-building inquiries with competing models and uncertainty |
| `design-challenges/` | Open-ended engineering problems with measurable requirements and trade-offs |
| `sources/` | Central source ledger for references used in the repository |
| `scripts/` | Repository and release-readiness validation |

Every core module directory contains three learner-facing files:

| File | Purpose |
| --- | --- |
| `overview.md` | Phenomena, concepts, mechanisms, quantities, models, assumptions, scales, misconceptions, connections, and sources |
| `technology.md` | Components, flows, system architecture, constraints, performance, failure modes, safety, and lifecycle |
| `explore.md` | Observation, prediction, worked reasoning, thought experiments, model building, transfer, and learning routes |

## Four ways to use the repository

### 1. Learn from foundations upward

Open [`INDEX.md`](INDEX.md), begin with scientific reasoning, and follow the prerequisite structure toward a technology module.

### 2. Follow a goal-directed pathway

Choose a route in [`pathways/`](pathways/), such as [`atoms-to-computers.md`](pathways/atoms-to-computers.md), and move through the abstractions that connect scientific principles to a complete system.

### 3. Reverse-engineer a familiar system

Start with [`system-dossiers/refrigerator.md`](system-dossiers/refrigerator.md). Trace energy, matter, and information flows; remove a component mentally; predict the consequences; then compare alternative architectures.

### 4. Investigate and design

Use the linked experience sequence:

1. [`system-dossiers/refrigerator.md`](system-dossiers/refrigerator.md) — explain the system;
2. [`failure-atlas/feedback-instability.md`](failure-atlas/feedback-instability.md) — understand a recurring failure pattern;
3. [`investigations/room-cooling.md`](investigations/room-cooling.md) — compare models with evidence;
4. [`design-challenges/passive-cooler.md`](design-challenges/passive-cooler.md) — design under explicit constraints.

The same scientific ideas are viewed through explanation, failure, evidence, and design.

## How to navigate dependencies

Each module's YAML frontmatter lists its `prerequisites` and `connections`. [`INDEX.md`](INDEX.md) summarises the canonical prerequisite graph, while [`maps/complete-dependency-map.md`](maps/complete-dependency-map.md) visualises it. Prerequisites are recommendations for smooth understanding rather than access gates.

## Content status and validation

A file existing does not mean it is scientifically reviewed. Status definitions and the current repair sequence are recorded in [`PROJECT_STATE.md`](PROJECT_STATE.md), while [`AUDIT.md`](AUDIT.md) records known structural, metadata, source, and editorial problems.

Run:

```bash
python3 scripts/validate_repo.py
```

for structural validation, or:

```bash
python3 scripts/validate_repo.py --strict
```

for release-readiness validation where warnings also fail.

## How to contribute

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Follow [`CONTENT_GUIDE.md`](CONTENT_GUIDE.md), cite sources according to [`SOURCE_POLICY.md`](SOURCE_POLICY.md), keep each pull request focused, and preserve the project's emphasis on causal explanation, quantitative models, explicit assumptions, system boundaries, and honest uncertainty.

Contributions can include:

- scientific corrections;
- stronger sources;
- clearer causal mechanisms;
- worked numerical examples;
- improved cross-links;
- new system dossiers;
- reusable failure patterns;
- safe investigations;
- design challenges with explicit requirements and trade-offs.

## Licensing

This repository uses two licences:

- **Code and scripts** in `scripts/` and `.github/`: [Apache License 2.0](LICENSE)
- **Original educational content**: [Creative Commons Attribution 4.0 International](LICENSE-CONTENT)

When reusing content, attribute "Principle to System contributors" and link to this repository. See [`CITATION.cff`](CITATION.cff) for citation metadata.

## Project status

The repository contains a complete first-draft inventory, but scientific and editorial review is ongoing. The live state, blockers, and continuation order are maintained in [`PROJECT_STATE.md`](PROJECT_STATE.md).
