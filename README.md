# Principle to System — Principia

**Principia** is an open, evidence-aware learning system for understanding how scientific principles become mechanisms, models, technologies, failures, investigations, and redesigns.

> **Current program:** **Product Alpha 0.1 — evidence integrity recovery.** The active milestone is completion of a verifiable real learner pilot of the refrigerator route, not another numbered governance phase. See [`PRODUCT_STATE.md`](PRODUCT_STATE.md) for the current decision state. The detailed Phase 0–50 ledger remains in [`PROJECT_STATE.md`](PROJECT_STATE.md) as validated project history.

## What Principia does

Principia teaches through complete system journeys rather than isolated facts:

```text
observation
→ system boundary and flows
→ causal mechanism
→ quantitative model
→ failure diagnosis
→ evidence boundary
→ redesign under constraints
```

The canonical learning corpus remains Markdown and JSON in this repository. The product layer reads that material; it does not replace it with a second content database.

## Product Alpha 0.1

The first learner-facing route uses a domestic refrigerator and five steps:

1. **Observe** surprising cycling behavior.
2. **Map** the boundary, stores, inputs, outputs, and flows.
3. **Model** the cabinet’s thermal response.
4. **Diagnose** normal cycling versus abnormal short-cycling.
5. **Redesign** under explicit constraints and trade-offs.

The alpha includes:

- a responsive learner interface;
- a dependency-free thermal model;
- a diagnosis challenge;
- exact-revision Atlas evidence presentation;
- a local anonymous facilitator recorder;
- a deterministic evaluation summarizer;
- a loopback-only one-command pilot launcher;
- focused Product Alpha CI.

### Run locally

```bash
python3 software/product_alpha/run_pilot.py --open
```

The launcher builds Product Alpha, binds only to `127.0.0.1`, and opens:

- learner route: `http://127.0.0.1:8000/`
- facilitator recorder: `http://127.0.0.1:8000/facilitator.html`

The recorder exports one anonymous JSONL record per learner. It creates no account, writes no browser storage, submits no network request, makes no live Atlas call, and performs no repository mutation.

### Validate

```bash
python3 software/product_alpha/build.py check
python3 software/product_alpha/run_pilot.py check
python3 -m unittest discover -s software/tests -p 'test_product_alpha*.py' -v
```

### Next evidence gate

Run or verify the documented 5–8 learner pilot before adding another route or production infrastructure. Evaluate route completion, mechanism explanation, model reasoning, failure diagnosis, evidence-boundary understanding, redesign trade-offs, recurring confusion, and voluntary continuation.

The pilot protocol is [`software/product_alpha/PILOT.md`](software/product_alpha/PILOT.md). The current evidence review is [`reports/product-alpha-0-1-pilot-summary.md`](reports/product-alpha-0-1-pilot-summary.md); unavailable cohort values remain **not reportable** until derived from real anonymous records.

## Principia and Atlas

Principia owns explanation, pedagogy, pathways, systems, investigations, failure analysis, and design.

Atlas owns structured identity, exact revisions, evidence, provenance, review state, lifecycle, staleness, translation lineage, and governance.

The product relationship is:

```text
Principia = learner-facing product
Atlas      = read-only trust substrate
```

Atlas references are pinned and advisory. Principia does not inherit Atlas status, and Product Alpha makes no live Atlas calls.

## Validated foundation

The following historical foundation remains machine-validated. These statements are retained as compatibility evidence, not as the active product roadmap.

### Four complete routes

- 4 route files in `experiences/`
- 16 applied artifacts
- 28 applied-material source records

All route and applied-artifact records remain canonical inputs to Product Alpha and future system journeys.

### Current release state

The retained Phase 12 release-candidate record is [`release/phase-12-release-candidate.json`](release/phase-12-release-candidate.json). All learner-facing material remains in a draft release state under `candidate-hold`.

Historical compatibility record: The Phase 12 validator passes on draft PR #14; the release decision remains Hold; the retained candidate identifier is `principia-material-foundation-rc1`. These phrases describe the archived Phase 12 record and do not supersede the current Product Alpha evidence gate.

Live Atlas integration remains disabled. Product Alpha is pilot-ready as software, not a public learning-effectiveness claim and not a production SaaS release.

### Principia & Atlas compatibility

The historical `bridge-candidate` compatibility surface remains explicit: the delayed-correction evidence reference `delayed-correction-recurrence@2` uses the exact-dependency relation `depends_on_exact`. The finalized offline bridge profile is `principia-atlas-external-dependent/0.2`. No live cross-repository call is enabled. These markers preserve validator compatibility only; they do not activate live Atlas integration or grant learner-facing status.

### Principia–Atlas bridge candidate

The retained bridge candidate is `claim-delayed-correction-r2`, pinned to `model-delayed-correction@2`.

The candidate does not inherit Atlas status. The candidate imports no glossary term. Live integration remains disabled. The candidate does not change the Phase 12 hold.

### Phase 13 software foundation

The historical Phase 13 static foundation remains `machine-only` and operationally inert outside explicit local build commands.

Historical compatibility record: The Phase 13 machine gate passes on draft PR #15; the archived software state is `foundation-validated`; and the generated site is reproducible. These markers describe the preserved Phase 13 foundation rather than the current learner-evidence milestone.

The generated foundation contains 92 learner-facing documents and 20 module pages. It is not a production application.

### Canonical material inventory

- 20 reviewed modules across foundations, physical science, life and Earth systems, and technology;
- 16 reviewed files in `synthesis/`;
- four complete applied routes;
- system dossiers, failure patterns, investigations, and design challenges;
- deterministic source and compatibility validation.

## Repository map

| Path | Purpose |
|---|---|
| `foundations/` | Scientific reasoning, measurement, models, probability, and computation |
| `science/` | Physical, chemical, biological, Earth, and systems science |
| `technology/` | Materials, electronics, software, AI, sensors, control, and infrastructure |
| `pathways/` | Cross-domain learning sequences |
| `concepts/` | Shared concepts used across modules |
| `maps/` | Dependency and systems maps |
| `synthesis/` | Cross-domain synthesis documents |
| `experiences/` | Route definitions |
| `system-dossiers/` | End-to-end system explanations |
| `failure-atlas/` | Recurring failure patterns |
| `investigations/` | Evidence-gathering activities |
| `design-challenges/` | Redesign tasks under constraints |
| `software/product_alpha/` | Current learner route, pilot recorder, and evaluation tools |
| `integration/principia-atlas/` | Offline exact-revision compatibility fixtures |
| `contracts/` | Machine-readable authority boundaries |
| `sources/` | Source ledgers and review records |
| `reports/` | Audits and historical validation evidence |
| `release/` | Historical release and governance records |

## Core principles

### Mechanism before memorization

Learners should explain how parts interact and why behavior emerges.

### Models with boundaries

Every model should expose assumptions, useful scope, and failure conditions.

### Failure as evidence

Breakdowns and surprises reveal hidden architecture and causal dependencies.

### Evidence without status inheritance

Review or acceptance in Atlas never automatically promotes a Principia learning claim.

### Progressive disclosure

A learner should be able to move from intuition to mechanism, model, deep evidence, and challenge without facing the full corpus at once.

## Status files

- [`PRODUCT_STATE.md`](PRODUCT_STATE.md): canonical current product decision state.
- [`PROJECT_STATE.md`](PROJECT_STATE.md): detailed historical phase and governance ledger.
- [`AUDIT.md`](AUDIT.md): editorial, scientific, and structural audit history.
- [`INDEX.md`](INDEX.md): canonical module index.

## Licensing

- Code and repository tooling: [`LICENSE`](LICENSE)
- Educational content: [`LICENSE-CONTENT`](LICENSE-CONTENT)
- Citation metadata: [`CITATION.cff`](CITATION.cff)

## Contributing

Contributions should preserve canonical content authority, exact source attribution, deterministic validation, product privacy boundaries, and the separation between Principia learning status and Atlas evidence status. See [`CONTRIBUTING.md`](CONTRIBUTING.md).
