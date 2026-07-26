# Principle to System

**Learn how foundational science becomes technology—and how to reason with the systems that result.**

Principle to System is the current repository identity and the future product identity **Principia**. It is an open-source knowledge repository for curious independent learners. It explains how scientific understanding is built, how it becomes engineered technology, and how real systems can be investigated, redesigned, and understood through their failures.

Principia is being prepared to work beside the separate [`Rhodan-lab/Atlas`](https://github.com/Rhodan-lab/Atlas) repository as a future **Principia & Atlas** product:

- Principia owns causal explanation, pedagogy, pathways, systems, investigations, failure analysis, and design experiences.
- Atlas owns structured knowledge identity, evidence, provenance, exact revision, review, lifecycle, staleness, translation lineage, and promotion governance.
- Neither repository inherits the other's status automatically.
- The repositories remain independently buildable and independently validatable.

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
| `experiences/` | Shared rules, four-route navigation, and the Phase 11B inventory |
| `system-dossiers/` | Reverse-engineering complete technologies |
| `failure-atlas/` | Recurring causal failure patterns and redesign strategies |
| `investigations/` | Safe model-comparison inquiries with uncertainty |
| `design-challenges/` | Engineering decisions under measurable constraints |
| `templates/` | Reusable authoring structures for the four experience families |
| `contracts/principia-atlas/` | Versioned Principia-side compatibility contracts |
| `integration/principia-atlas/` | Non-live bridge manifests, deterministic exports, and invalid fixtures |
| `sources/` | Normalized module and experience source ledgers |
| `scripts/` | Module, experience, synthesis, expansion, and compatibility validators |

Every core module contains `overview.md`, `technology.md`, and `explore.md`. Applied materials use family-specific standards and templates.

## Four ways to learn

### 1. Foundations upward

Open [`INDEX.md`](INDEX.md), begin with scientific reasoning, and follow prerequisites toward a technology module.

### 2. Goal-directed pathways

Choose a route in [`pathways/`](pathways/), such as [`atoms-to-computers.md`](pathways/atoms-to-computers.md).

### 3. Reverse-engineer a system

Choose one reviewed dossier:

- [`system-dossiers/refrigerator.md`](system-dossiers/refrigerator.md)
- [`system-dossiers/solar-battery-microgrid.md`](system-dossiers/solar-battery-microgrid.md)
- [`system-dossiers/drinking-water-network.md`](system-dossiers/drinking-water-network.md)
- [`system-dossiers/web-service-request.md`](system-dossiers/web-service-request.md)

Trace energy, matter, information, control, and failure boundaries; remove a component mentally; predict the result; compare alternative architectures.

### 4. Explain, diagnose, investigate, design

[`experiences/phase-11b-inventory.json`](experiences/phase-11b-inventory.json) defines four complete routes:

| Route | System | Failure | Investigation | Design |
| --- | --- | --- | --- | --- |
| thermal-control | Refrigerator | Feedback instability | Room cooling | Passive cooler |
| resilient-energy | Solar–battery microgrid | Protection coordination | Solar shading | Resilient charging hub |
| water-infrastructure | Drinking-water network | Sensor drift | Filter loading | Non-potable rainwater buffer |
| distributed-information | Web-service request | Retry storm | Queue delay | Resilient school information service |

Each route examines one system through explanation, failure, evidence, and design.

## Content and artifact status

File presence does not imply review completion. Module status is tracked in [`INDEX.md`](INDEX.md); repository blockers and review order are tracked in [`PROJECT_STATE.md`](PROJECT_STATE.md) and [`AUDIT.md`](AUDIT.md).

The sixteen applied-material artifacts have completed focused source, safety, structure, and metadata review. Their pedagogical `status` is `reviewed`, not `complete`.

Applied experiences also carry:

- `artifact_revision` — the exact Principia revision exposed to dependency reporting;
- `release_status` — publication readiness, currently `draft` for all Phase 11B artifacts.

Pedagogical review, release readiness, and Atlas knowledge status are separate decisions. Phase 12 is the earliest release gate.

## Safety boundaries

- Energy experiences use diagrams, public data, and simulation; they do not authorize wiring, battery modification, islanding, backfeed, or grid testing.
- Water experiences explain regulated systems without providing a procedure for producing safe drinking water; the rainwater design is explicitly non-potable.
- Distributed-information experiences use synthetic traffic and fictional data; they do not authorize scanning, flooding, credential use, private-data access, or testing live services.

## Principia & Atlas compatibility

[`contracts/principia-atlas/0.1/`](contracts/principia-atlas/0.1/) defines `principia-atlas-bridge/0.1`. It allows Principia to declare exact-revision Atlas dependencies and generate the opaque external-dependent shape already supported by Atlas coverage reporting.

The current integration remains a non-live fixture:

```yaml
mode: compatibility-fixture
live: false
```

Principia does not clone Atlas during validation, and the export contains no Principia pedagogical or release status. A future live bridge requires explicit approval and compatible phase gates in both repositories. Phase 11B does not activate that bridge.

## Validation

Core repository audit:

```bash
python3 scripts/validate_repo.py
python3 scripts/validate_repo.py --strict
```

Applied-material foundation and controlled expansion:

```bash
python3 scripts/validate_experiences.py --strict
python3 scripts/validate_phase11b_expansion.py
```

Principia & Atlas compatibility:

```bash
python3 scripts/export_principia_atlas_dependents.py --check
python3 scripts/validate_principia_atlas_bridge.py
python3 scripts/validate_principia_atlas_audit.py
```

GitHub Actions runs focused metadata, source, scientific-review, synthesis, applied-material, expansion, and compatibility validation. Compatibility and Phase 11B CI are read-only and do not import Atlas.

## Sources

Reviewed module sources are recorded in [`sources/source-ledger.md`](sources/source-ledger.md). Applied materials use [`sources/experience-source-ledger.md`](sources/experience-source-ledger.md), which contains 28 one-source-per-row records after Phase 11B.

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md), [`CONTENT_GUIDE.md`](CONTENT_GUIDE.md), and [`SOURCE_POLICY.md`](SOURCE_POLICY.md). New applied materials must begin from the appropriate file in [`templates/`](templates/), enter the machine-readable experience inventory, and pass strict expansion validation. Bridgeable artifacts must use positive exact `artifact_revision` values and explicit `release_status`.

## Licensing

- Code and scripts: [Apache License 2.0](LICENSE)
- Original educational content: [CC BY 4.0](LICENSE-CONTENT)

When reusing content, attribute “Principle to System contributors” and link to this repository. See [`CITATION.cff`](CITATION.cff).
