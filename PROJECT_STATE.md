# Project State

> Last updated: 2026-07-26

## Current phase

**Phase 8 Life and Earth Systems review implemented and validated on draft PR #9; independent review and merge remain pending.**

The repository remains a material-first educational foundation. Software is intentionally deferred until the core material, sources, review workflow, and synthesis are mature.

## Phase progress

| Phase | Scope | Status |
| --- | --- | --- |
| 0 | Vision and educational philosophy | Complete |
| 1 | Core knowledge inventory | First-draft inventory complete |
| 2 | Repository audit and hardening | Complete |
| 3 | Applied-material foundation | Implemented and validated |
| 4 | Core metadata normalization | Merged and validated |
| 5 | Legacy source-ledger repair | Merged and validated |
| 6 | Foundations scientific review | Merged and validated through PR #8 |
| 7 | Physical-science review | Merged and validated through PR #8 |
| 8 | Life and Earth systems review | Implemented and validated on PR #9; awaiting merge |
| 9 | Technology review | Next after Phase 8 integration |
| 10 | Synthesis reconciliation | Initial materials exist; final reconciliation pending |
| 11 | Controlled material expansion | Seed exemplars complete |
| 12 | Release candidate | Not started |
| 13 | Optional software layer | Deferred |

## Integration history

The original Phase 6 work was merged into the Phase 5 feature branch after Phase 5 had already entered `main`. Phase 7 was later merged into that Phase 6 branch. PR #8 corrected the topology by integrating the reviewed Phase 6 and Phase 7 layers into `main`.

Current branch order is now clean:

1. `main` contains reviewed Modules 01–12;
2. `agent/phase-8-life-earth-review` was created directly from the merged `main` state;
3. PR #9 carries only the focused Phase 8 review into `main`;
4. no phase workflow automatically merges pull requests.

## Content inventory and status

### Core layer

- 20 modules and 60 learner-facing files;
- 7 crosscutting concepts;
- 6 end-to-end pathways;
- 3 Mermaid knowledge maps;
- normalized central source ledger;
- reusable metadata, source, and scientific-review validators.

On PR #9:

- Modules 01–05: **Reviewed**;
- Modules 06–12: **Reviewed**;
- Modules 13–16: **Reviewed**;
- Modules 17–20: **Draft**;
- no core module is Complete.

A module is Reviewed only when its `overview.md`, `technology.md`, and `explore.md` files all complete the same focused scientific and editorial review.

### Applied-material layer

- shared learning contract in `experiences/`;
- 4 family standards;
- 4 reusable templates;
- 4 reviewed exemplars;
- normalized experience-source ledger;
- dedicated strict validator and GitHub Actions workflow.

## Phase 4 result — Metadata foundation

Phase 4 normalized all 60 original learner files:

- unique canonical slugs by file role;
- consistent module identifiers and subject domains;
- canonical prerequisites and connections;
- removal of self-references and unknown legacy identifiers;
- deterministic normalizer and generated audit;
- focused idempotence validation.

Phase 4 was merged through PR #4.

## Phase 5 result — Source foundation

Phase 5:

- recovered 109 historical logical records from malformed rows;
- normalized one eight-column row per source;
- removed 22 weak or invalid records only when inspected replacements were supplied;
- added 23 replacement records;
- produced a 110-record baseline without malformed locators, dates, module fields, or weak records under the Phase 5 classifier;
- established at least four sources and two policy-tier sources for every core module;
- added deterministic source-repair tools and a read-only CI gate.

Phase 5 is merged into `main`.

## Phase 6 result — Foundations Modules 01–05

Phase 6 scientifically and editorially reviewed all 15 Foundations files. Major corrections covered:

- causal identification, p-values, confidence intervals, reproducibility, and replicability;
- VIM/GUM measurement terminology, covariance propagation, traceability, and dynamic measurement;
- model purpose, calibration, validation, identifiability, linearisation, scaling, and extrapolation limits;
- probability, finite-sample inference, calibration, sampling bias, and decision thresholds;
- conditioning, stability, consistency, convergence, floating-point error, verification, and validation;
- safe and age-appropriate exploration activities.

Phase 6 added six reviewed source records, producing a 116-record ledger.

## Phase 7 result — Physical Science Modules 06–12

Phase 7 scientifically and editorially reviewed all 21 Physical Science files. Major corrections covered:

- quantum states, uncertainty, measurement, vacuum language, MRI, STM, and tunnelling limits;
- bonding continua, activities, standard states, catalytic cycles, electrochemistry, and rate-model limits;
- temperature, entropy, heat, work, free-energy constraints, radiation, Carnot scope, and exergy;
- momentum, invariant mass, rotational inertia, specific impulse, safety factors, and worked arithmetic;
- revised-SI electromagnetic constants, Ohmic limits, impedance, induction, and circuit boundaries;
- Fourier scope, sampling, interference-energy accounting, guided modes, bandwidth, and data rate;
- Bernoulli assumptions, lift, non-Newtonian flow, tensor stress and strain, fracture, fatigue, and anisotropy;
- removal of unsafe batteries, sealed heating, fragile resonance, traffic, cutting, fracture, and weapon-based activities.

Phase 7 added five reviewed source records, producing a **121-record** ledger. Phases 6 and 7 were integrated into `main` through PR #8.

## Phase 8 result — Life and Earth Systems Modules 13–16

Phase 8 scientifically and editorially reviewed all 12 learner-facing files.

### Module 13 — Cells and Bioenergetics

- corrected ATP, Gibbs-free-energy coupling, enzyme, membrane-transport, respiration, photosynthesis, and ATP-yield explanations;
- added activity, sign, direction, and model limits to electrochemical transport;
- removed unsafe pressure, hot-water, tasting, and real-poison activities.

### Module 14 — DNA and Evolution

- corrected replication fidelity, gene-expression scope, bacterial-versus-eukaryotic replication machinery, mutation, selection, Hardy–Weinberg notation, fitness, and PCR limits;
- replaced sensitive family-trait analysis, household alcohol extraction, and real antibiotic-exposure prompts;
- clarified that synonymous substitutions can still have functional consequences;
- replaced stale biotechnology identifiers with canonical computational and systems connections.

### Module 15 — Ecosystems and Complex Systems

- removed fixed trophic-transfer, carrying-capacity, modularity, wetland-performance, and reliability claims;
- distinguished keystone effect, network degree, biomass, and functional uniqueness;
- corrected Lotka–Volterra, logistic-map, and signed causal-loop interpretation;
- reframed closed ecological systems around leakage, accumulation, ageing, and backup requirements;
- replaced direct standing-water contact and sealed-organism activities.

### Module 16 — Earth and Planetary Systems

- corrected plate-driving mechanisms, overturning circulation, effective radiative forcing, greenhouse physics, energy-balance models, and climate-projection uncertainty;
- removed unstable Argo-count, dataset-volume, and computing-power claims;
- replaced stove heating, permanent-marker, and operational terraforming activities.

Phase 8 added ten inspected institutional records:

- NCBI bioenergetics and cell membranes;
- NHGRI DNA replication, gene expression, and evolution;
- EPA constructed-treatment-wetland guidance;
- ESA MELiSSA research;
- IPCC AR6 Chapter 7;
- NOAA Argo;
- USGS *This Dynamic Earth*.

The integrated ledger contains **131 records**.

Artifacts:

- `reports/phase-8-life-earth-review.md`;
- `reports/phase-8-life-earth-sources.json`;
- `sources/phase-8-reviewed-sources.json`;
- `scripts/apply_phase8_review_sources.py`;
- `scripts/apply_phase8_life_earth_review.py`;
- `scripts/finalize_phase8_review.py`;
- `scripts/validate_phase8_life_earth_review.py`;
- `.github/workflows/validate-phase-8-life-earth.yml`.

## Status meanings

- **Draft** — content exists but has not completed focused scientific review.
- **Reviewed** — claims, sources, structure, safety, metadata, equations, links, assumptions, and limitations received focused review.
- **Complete** — reviewed content passes the applicable release gate and has no unresolved findings.
- **Blocked** — progress depends on a recorded unresolved issue.

Reviewed does not mean independently certified or release-ready.

## Validation

### Metadata and source foundation

```bash
python3 scripts/normalize_module_metadata.py
python3 scripts/normalize_source_ledger.py --check --strict
python3 scripts/apply_verified_source_baseline.py --check
```

### Phase 6 and Phase 7 continuity

```bash
python3 scripts/apply_foundations_review_sources.py --check
python3 scripts/validate_foundations_continuity_phase8.py --allow-downstream-reviewed
python3 scripts/apply_phase7_review_sources.py --check
python3 scripts/finalize_phase7_review.py --check
```

### Phase 8 review

```bash
python3 scripts/apply_phase8_review_sources.py --check
python3 scripts/finalize_phase8_review.py --check
python3 scripts/validate_phase8_life_earth_review.py
python3 scripts/validate_repo.py
```

The Phase 8 gate checks:

- all 12 expected files and Reviewed metadata;
- canonical slugs, prerequisites, domains, connections, and INDEX status;
- exact source-to-ledger matching;
- biological, ecological, climate, and Earth-system model boundaries;
- removal of known stale identifiers and superseded claims;
- safe and age-appropriate explorations;
- continuity of Modules 01–12;
- Modules 17–20 remaining Draft;
- deterministic idempotence and review-record consistency.

## Next phase — Technology Modules 17–20

Phase 9 should review:

1. Materials and Manufacturing;
2. Semiconductors and Electronics;
3. Software and AI;
4. Sensors, Control, and Infrastructure.

The review must check materials models, manufacturing process boundaries, semiconductor-device physics, computing and AI claims, software and networking abstractions, sensing and control equations, infrastructure dependencies, current-but-unstable technology claims, sources, safety, and lifecycle impacts.

## Remaining core work

1. Review and merge PR #9 into `main`.
2. Obtain independent review of Modules 01–16.
3. Complete scientific review of Modules 17–20.
4. Reconcile pathways, concepts, maps, terminology, and links.
5. Pass repository-wide strict release validation.
6. Consider software only after the material system is mature.

## Continuation instructions

Read `README.md`, `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, `AUDIT.md`, this file, and the relevant phase reports. Keep metadata repair, source repair, scientific review, synthesis, and software implementation in separate focused pull requests. Never promote content solely because a file exists or a structural check passes.
