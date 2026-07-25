# Project State

> Last updated: 2026-07-25

## Current phase

**Phase 6 Foundations scientific review implemented on stacked PR #6; Phase 5 PR #5 must merge first.**

The repository remains a material-first educational foundation. Software is intentionally deferred until the core material, sources, review workflow, and synthesis are mature.

## Phase progress

| Phase | Scope | Status |
| --- | --- | --- |
| 0 | Vision and educational philosophy | Complete |
| 1 | Core knowledge inventory | First-draft inventory complete |
| 2 | Repository audit and hardening | Complete |
| 3 | Applied-material foundation | Implemented and validated |
| 4 | Core metadata normalization | Merged and validated |
| 5 | Legacy source-ledger repair | Implemented and validated on PR #5; awaiting merge |
| 6 | Foundations scientific review | Implemented and validated on stacked PR #6 |
| 7 | Physical-science review | Next after stack integration |
| 8 | Life and Earth systems review | Not started systematically |
| 9 | Technology review | Not started systematically |
| 10 | Synthesis reconciliation | Initial materials exist; final reconciliation pending |
| 11 | Controlled material expansion | Seed exemplars complete |
| 12 | Release candidate | Not started |
| 13 | Optional software layer | Deferred |

## Content inventory and status

### Core layer

- 20 modules and 60 learner-facing files
- 7 crosscutting concepts
- 6 end-to-end pathways
- 3 Mermaid knowledge maps
- normalized central source ledger
- repository and phase-specific validators

Focused review status:

- Modules 01–05: **Reviewed**
- Modules 06–20: **Draft**
- No core module is Complete

A module is Reviewed only when its `overview.md`, `technology.md`, and `explore.md` files all complete the focused scientific and editorial review.

### Applied-material layer

- shared learning contract in `experiences/`
- 4 family standards
- 4 reusable templates
- 4 reviewed exemplars
- normalized experience-source ledger
- dedicated strict validator and GitHub Actions workflow

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

Phase 5 is implemented on PR #5 and remains unmerged at the time of this update.

## Phase 6 result — Foundations Modules 01–05

Phase 6 scientifically and editorially reviewed all 15 Foundations files.

### Module 01 — Scientific Reasoning

- corrected p-value and confidence-interval interpretations;
- separated association, prediction, causal effect, and mechanism;
- added potential outcomes and identification assumptions;
- distinguished reproducibility from replicability;
- clarified limits of automated causal discovery;
- replaced unsafe or age-inappropriate exploration examples.

### Module 02 — Measurement and Uncertainty

- aligned terminology with VIM and GUM;
- separated error, uncertainty, accuracy, trueness, precision, and resolution;
- corrected thermodynamic-temperature wording;
- added covariance to uncertainty propagation;
- clarified traceability, loading, dynamic response, sampling, and calibration lifecycle;
- revised activities for safety and interpretive accuracy.

### Module 03 — Mathematical Models

- defined model purpose, boundary, calibration, validation, sensitivity, and identifiability;
- corrected vector and tensor scope;
- made linearization explicitly local;
- separated fit from mechanism and fidelity from trustworthiness;
- added extrapolation, model discrepancy, coupling, and governance limits.

### Module 04 — Probability and Statistics

- corrected probability, sampling, CLT, p-value, confidence-interval, and regression interpretations;
- distinguished discrimination, calibration, and decision quality;
- separated sampling variance from bias;
- corrected the quantum probability-density statement;
- replaced an ambiguous medical example with a neutral rare-defect example.

### Module 05 — Computation and Algorithms

- separated conditioning, stability, consistency, convergence, and numerical error classes;
- distinguished code verification, solution verification, and validation;
- corrected finite differences, quadrature, Monte Carlo, conditioning, and CFL scope;
- corrected the Landauer-limit wording;
- removed unstable hardware-performance claims;
- strengthened safe verification and reproducibility exercises.

The full review record is in `reports/phase-6-foundations-review.md`.

## Phase 6 sources

The focused review added six exact inspected locators:

- GUM official DOI;
- GUM Supplement 1 for Monte Carlo propagation;
- VIM official DOI;
- MIT OpenCourseWare dynamic-systems modelling;
- NIST/SEMATECH Engineering Statistics Handbook;
- NIST simulation verification and validation report.

The central ledger now contains **116 records**. The additions are declared in `sources/foundations-review-sources.json`, applied by `scripts/apply_foundations_review_sources.py`, and recorded in `reports/phase-6-foundations-sources.json`.

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

### Phase 6 Foundations review

```bash
python3 scripts/apply_foundations_review_sources.py --check
python3 scripts/validate_foundations_review.py
python3 scripts/validate_repo.py
```

The Phase 6 gate checks:

- all 15 expected files and their Reviewed metadata;
- canonical prerequisites, slugs, domains, and connections;
- required overview, technology, and exploration sections;
- at least four direct URLs in each theory source section;
- exact source-to-ledger matching;
- removal of known stale identifiers, misconceptions, and unsafe examples;
- INDEX agreement: Modules 01–05 Reviewed and Modules 06–20 Draft;
- review and source audit artifacts.

## Stack and merge order

1. Review and merge PR #5 into `main`.
2. Retarget PR #6 from `agent/phase-5-source-repair` to `main`.
3. Re-run the Phase 6 validation against the retargeted branch.
4. Obtain independent review before merging PR #6.

No pull request is automatically merged by this phase workflow.

## Next phase — Physical Science

Phase 7 should review Modules 06–12 in dependency order:

1. Matter and Quantum Foundations
2. Chemical Bonding and Reactions
3. Energy and Thermodynamics
4. Motion and Forces
5. Electricity and Magnetism
6. Waves and Signals
7. Fluids and Materials

The review must check equations, units, conservation laws, constitutive assumptions, scale transitions, causal mechanisms, model limits, technology links, sources, and safe explorations.

## Remaining core work

1. Integrate PR #5 and PR #6 in stack order.
2. Independently review Modules 01–05.
3. Complete scientific review of Modules 06–20.
4. Reconcile pathways, concepts, maps, terminology, and links.
5. Pass repository-wide strict release validation.
6. Consider software only after the material system is mature.

## Continuation instructions

Read `README.md`, `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, `AUDIT.md`, this file, and the relevant phase report. Keep metadata repair, source repair, scientific review, synthesis, and software implementation in separate focused pull requests. Never promote content solely because a file exists or a structural check passes.
