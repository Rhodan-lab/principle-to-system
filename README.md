# Principle to System

**Learn how foundational science becomes technology—and how to reason with the systems that result.**

Principle to System is an open-source knowledge repository for curious independent learners. It explains how scientific understanding is built, how it becomes engineered technology, and how real systems can be investigated, redesigned, and understood through their failures.

Core modules follow this arc:

```text
observation
→ scientific concept
→ mechanism
→ mathematical model
→ engineered component
→ technological system
→ limitation and trade-off
```

Applied materials continue it:

```text
notice a system
→ choose a boundary
→ identify flows and state variables
→ propose competing mechanisms
→ build the smallest useful model
→ test it against evidence
→ redesign under constraints
→ explain remaining uncertainty
```

This is not an exam course or an encyclopaedia of disconnected facts. It is a connected map of causal explanations and reasoning practices.

## Who this is for

Independent learners who want to understand *why* technology works, not merely *that* it works. No grades or formal enrolment are assumed. Mathematics is used where it improves explanation, with symbols, units, assumptions, and model limits made explicit.

## Repository structure

| Folder | Contents |
| --- | --- |
| `foundations/` | Modules 01–05: reasoning, measurement, mathematics, probability, and computation |
| `science/` | Modules 06–16: natural science from quantum matter to planetary systems |
| `technology/` | Modules 17–20: materials, electronics, software, control, and infrastructure |
| `concepts/` | Seven crosscutting ideas used across disciplines |
| `pathways/` | Six end-to-end science-to-technology chains |
| `maps/` | Dependency and enabling-relationship maps |
| `synthesis/` | Phase-level canonical graphs and reconciliation contracts |
| `experiences/` | Shared rules and navigation for applied materials |
| `system-dossiers/` | Reverse-engineering complete technologies |
| `failure-atlas/` | Recurring causal failure patterns and redesign strategies |
| `investigations/` | Safe model-comparison inquiries with uncertainty |
| `design-challenges/` | Engineering decisions under measurable constraints |
| `templates/` | Reusable authoring structures for the four experience families |
| `sources/` | Legacy module ledger and normalized experience-source ledger |
| `scripts/` | Module and experience validators |

Every core module contains `overview.md`, `technology.md`, and `explore.md`. Applied materials use family-specific standards and templates.

## Four ways to learn

### 1. Foundations upward

Open [`INDEX.md`](INDEX.md), begin with scientific reasoning, and follow prerequisites toward a technology module.

### 2. Goal-directed pathways

Choose a route in [`pathways/`](pathways/), such as [`atoms-to-computers.md`](pathways/atoms-to-computers.md).

### 3. Reverse-engineer a system

Start with [`system-dossiers/refrigerator.md`](system-dossiers/refrigerator.md). Trace energy, matter, and information flows; remove a component mentally; predict the result; compare alternative architectures.

### 4. Explain, diagnose, investigate, design

1. [`system-dossiers/refrigerator.md`](system-dossiers/refrigerator.md)
2. [`failure-atlas/feedback-instability.md`](failure-atlas/feedback-instability.md)
3. [`investigations/room-cooling.md`](investigations/room-cooling.md)
4. [`design-challenges/passive-cooler.md`](design-challenges/passive-cooler.md)

The same thermodynamic theme is viewed through explanation, failure, evidence, and design.

## Content status

File presence does not imply review completion. Module status is tracked in [`INDEX.md`](INDEX.md); repository blockers and review order are tracked in [`PROJECT_STATE.md`](PROJECT_STATE.md) and [`AUDIT.md`](AUDIT.md).

The initial applied-material exemplars have completed a focused source, safety, structure, and metadata review. Their status is `reviewed`, not `complete`, because repository-wide strict validation and independent scientific review are still required for a release claim.

## Validation

Core repository audit:

```bash
python3 scripts/validate_repo.py
python3 scripts/validate_repo.py --strict
```

Applied-material layer:

```bash
python3 scripts/validate_experiences.py
python3 scripts/validate_experiences.py --strict
```

GitHub Actions runs focused metadata, source, scientific-review, synthesis, and applied-material validation. The Phase 10 canonical synthesis graph is validated against Modules 01–20.

## Sources

Reviewed module sources are recorded in the normalized [`sources/source-ledger.md`](sources/source-ledger.md). New applied materials use the machine-readable [`sources/experience-source-ledger.md`](sources/experience-source-ledger.md), with one source per eight-column row.

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md), [`CONTENT_GUIDE.md`](CONTENT_GUIDE.md), and [`SOURCE_POLICY.md`](SOURCE_POLICY.md). New applied materials must begin from the appropriate file in [`templates/`](templates/) and pass strict experience validation.

## Licensing

- Code and scripts: [Apache License 2.0](LICENSE)
- Original educational content: [CC BY 4.0](LICENSE-CONTENT)

When reusing content, attribute “Principle to System contributors” and link to this repository. See [`CITATION.cff`](CITATION.cff).
