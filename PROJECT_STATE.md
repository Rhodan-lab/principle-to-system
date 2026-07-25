# Project State

> Last updated: 2026-07-26

## Current phase

**Phase 7 Physical Science review is implemented and validated on PR #7. Phase 6 requires integration through PR #8 before Phase 7 can enter `main`.**

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
| 6 | Foundations scientific review | Implemented and validated; integration PR #8 open |
| 7 | Physical-science review | Implemented and validated on PR #7 |
| 8 | Life and Earth systems review | Next after Phase 7 integration |
| 9 | Technology review | Not started systematically |
| 10 | Synthesis reconciliation | Initial materials exist; final reconciliation pending |
| 11 | Controlled material expansion | Seed exemplars complete |
| 12 | Release candidate | Not started |
| 13 | Optional software layer | Deferred |

## Branch and merge topology

The original Phase 6 PR was based on `agent/phase-5-source-repair` and was merged into that feature branch after Phase 5 had already entered `main`. Therefore, the Phase 6 content did not reach `main`, despite the original PR showing as merged.

The correction is explicit:

1. **PR #8** — integrate `agent/phase-6-foundations-review` into `main`;
2. **PR #7** — review Phase 7 against `agent/phase-6-foundations-review`;
3. after PR #8 merges, retarget PR #7 to `main`;
4. rerun the read-only Phase 7 gate;
5. obtain independent review before any merge.

No phase workflow automatically merges pull requests.

## Content inventory and review status

### Core layer

- 20 modules and 60 learner-facing files;
- 7 crosscutting concepts;
- 6 end-to-end pathways;
- 3 Mermaid knowledge maps;
- normalized central source ledger;
- reusable metadata, source, and scientific-review validators.

On the integrated Phase 7 branch:

- Modules 01–05: **Reviewed**;
- Modules 06–12: **Reviewed**;
- Modules 13–20: **Draft**;
- no core module is Complete.

A module is Reviewed only when its `overview.md`, `technology.md`, and `explore.md` files all complete the same focused scientific and editorial review.

### Applied-material layer

- shared learning contract in `experiences/`;
- 4 family standards;
- 4 reusable templates;
- 4 reviewed exemplars;
- normalized experience-source ledger;
- dedicated strict validator and GitHub Actions workflow.

## Phase 4 result — metadata foundation

Phase 4 normalized all 60 original learner files:

- unique canonical slugs by file role;
- consistent module identifiers and subject domains;
- canonical prerequisites and connections;
- removal of self-references and unknown legacy identifiers;
- deterministic normalizer and generated audit;
- focused idempotence validation.

Phase 4 was merged through PR #4.

## Phase 5 result — source foundation

Phase 5:

- recovered 109 historical logical records from malformed rows;
- normalized one eight-column row per source;
- removed 22 weak or invalid records only when inspected replacements were provided;
- added 23 replacement records;
- produced a 110-record baseline with no malformed locators, dates, module fields, or weak records under the Phase 5 classifier;
- established at least four sources and two policy-tier sources for every core module;
- added deterministic source-repair tools and a read-only CI gate.

Phase 5 is merged into `main`.

## Phase 6 result — Foundations Modules 01–05

Phase 6 scientifically and editorially reviewed all 15 Foundations files.

Main corrections include:

- causal identification, p-values, confidence intervals, reproducibility, and replicability;
- VIM/GUM measurement terminology, covariance propagation, traceability, and dynamic measurement;
- model purpose, calibration, validation, identifiability, linearisation, scaling, and extrapolation limits;
- probability, finite-sample inference, calibration, sampling bias, and decision thresholds;
- conditioning, stability, consistency, convergence, floating-point error, verification, and validation;
- safe and age-appropriate exploration activities.

Phase 6 added six exact reviewed source records. The Phase 6 ledger contains **116 records**.

Artifacts:

- `reports/phase-6-foundations-review.md`;
- `reports/phase-6-foundations-sources.json`;
- `sources/foundations-review-sources.json`;
- `scripts/apply_foundations_review_sources.py`;
- `scripts/validate_foundations_review.py`.

Phase 6 integration into `main` is represented by PR #8.

## Phase 7 result — Physical Science Modules 06–12

Phase 7 scientifically and editorially reviewed all 21 files across:

1. Matter and Quantum Foundations;
2. Chemical Bonding and Reactions;
3. Energy and Thermodynamics;
4. Motion and Forces;
5. Electricity and Magnetism;
6. Waves and Signals;
7. Fluids and Materials.

### Major corrections

- quantum states, wavefunctions, uncertainty, vacuum language, nuclear interactions, MRI, STM, and tunnelling limits;
- bonding continua, dimensionless activities, standard states, catalytic cycles, electrochemistry, and reaction-rate limits;
- temperature, entropy, heat, work, free-energy constraints, net radiation, Carnot scope, and exergy;
- momentum form of Newton's second law, invariant mass, rotational inertia, specific impulse, factors of safety, and worked-example arithmetic;
- revised-SI electromagnetic constants, Ohmic limits, impedance-based current division, induction, and circuit-model boundaries;
- Fourier series and transforms, sampling, interference-energy accounting, guided fibre modes, bandwidth, and data rate;
- Bernoulli assumptions, aerodynamic lift, non-Newtonian flow, tensor stress and strain, fracture mechanics, anisotropy, fatigue, and damage tolerance.

### Safety corrections

Unsafe or unsuitable activities were removed or replaced, including:

- directly shorting batteries with loose wire;
- heating sealed containers;
- snapping stretched bands near the face or skin;
- using fragile glass for resonance;
- observing traffic at close range;
- breaking metal objects by repeated bending;
- cutting pressurised containers or restricting hoses;
- weapon-based orbital framing.

The replacement activities use simulations, recorded observations, low-energy apparatus, reference data, or teacher-approved equipment.

### Source result

Phase 7 added five direct reviewed records:

- NIBIB MRI;
- NIST scanning probe microscopy;
- EPA automobile emissions;
- BIPM SI Brochure;
- NASA Bernoulli and Newton.

The integrated Phase 7 ledger contains **121 records**:

- 110 Phase 5 baseline records;
- 6 Phase 6 review records;
- 5 Phase 7 review records.

Artifacts:

- `reports/phase-7-physical-science-review.md`;
- `reports/phase-7-physical-science-sources.json`;
- `sources/phase-7-reviewed-sources.json`;
- `scripts/apply_phase7_review_sources.py`;
- `scripts/apply_phase7_physical_science_review.py`;
- `scripts/run_phase7_review.py`;
- `scripts/finalize_phase7_review.py`.

## Status meanings

- **Draft** — content exists but has not completed focused scientific review.
- **Reviewed** — claims, sources, structure, safety, metadata, equations, links, assumptions, and limitations received focused review.
- **Complete** — reviewed content passes the applicable release gate and has no unresolved findings.
- **Blocked** — progress depends on a recorded unresolved issue.

Reviewed does not mean independently certified or release-ready.

## Validation

### Phase 4 metadata

```bash
python3 scripts/normalize_module_metadata.py
```

### Phase 5 sources

```bash
python3 scripts/normalize_source_ledger.py --check --strict
python3 scripts/apply_verified_source_baseline.py --check
```

### Phase 6 review

```bash
python3 scripts/apply_foundations_review_sources.py --check
python3 scripts/validate_foundations_review.py
```

In a downstream Phase 7 branch:

```bash
python3 scripts/validate_foundations_review.py --allow-downstream-reviewed
```

### Phase 7 review

```bash
python3 scripts/apply_phase7_review_sources.py --check
python3 scripts/finalize_phase7_review.py --check
python3 scripts/validate_repo.py
```

The Phase 7 gate checks:

- all 21 expected Physical Science files and Reviewed metadata;
- canonical slugs, prerequisites, domains, connections, and INDEX status;
- direct source-to-ledger matching;
- equations, constants, arithmetic, assumptions, and model boundaries;
- removal of known stale identifiers and superseded claims;
- removal of unsafe learner activities;
- Phase 6 source and content continuity;
- deterministic idempotence of the review transformation.

## Next phase — Life and Earth Systems

Phase 8 should review Modules 13–16 in dependency order:

1. Cells and Bioenergetics;
2. DNA and Evolution;
3. Ecosystems and Complex Systems;
4. Earth and Planetary Systems.

The review must check molecular and cellular mechanisms, energy and matter flows, gene-expression accuracy, evolutionary mechanisms, ecological feedback, climate and planetary boundaries, equations, sources, safety, and scale transitions.

## Remaining core work

1. Review and merge PR #8 into `main`.
2. Retarget PR #7 to `main` and rerun its read-only gate.
3. Obtain independent review before merging PR #7.
4. Complete scientific review of Modules 13–20.
5. Reconcile pathways, concepts, maps, terminology, and links.
6. Pass repository-wide strict release validation.
7. Consider software only after the material system is mature.

## Continuation instructions

Read `README.md`, `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, `AUDIT.md`, this file, and the relevant phase reports. Keep metadata repair, source repair, scientific review, synthesis, and software implementation in separate focused pull requests. Never promote content solely because a file exists or a structural check passes.
