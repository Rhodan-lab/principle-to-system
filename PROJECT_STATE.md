# Project State

> Last updated: 2026-07-25

## Current phase

**Phase 5 legacy source repair implemented; Phase 6 foundations scientific review is next.**

The repository contains two coordinated layers:

1. a structurally complete first draft of 20 core modules and synthesis materials;
2. a reviewed applied-material foundation for system explanation, failure analysis, investigation, and design.

The project remains material-first Markdown. Software is intentionally deferred until the educational architecture, metadata, sources, and review workflow are stable.

## Phase progress

| Phase | Scope | Status |
| --- | --- | --- |
| 0 | Vision and educational philosophy | Complete |
| 1 | Core knowledge inventory | First-draft inventory complete |
| 2 | Repository audit and hardening | Complete |
| 3 | Applied-material foundation | Implemented and validated |
| 4 | Core metadata normalization | Merged and validated |
| 5 | Legacy source-ledger repair | Implemented on PR #5; awaiting merge |
| 6 | Foundations scientific review | Next |
| 7 | Physical-science review | Not started systematically |
| 8 | Life and Earth systems review | Not started systematically |
| 9 | Technology review | Not started systematically |
| 10 | Synthesis reconciliation | Initial materials exist; final reconciliation pending |
| 11 | Controlled material expansion | Seed exemplars complete |
| 12 | Release candidate | Not started |
| 13 | Optional software layer | Deferred |

## Content inventory

### Core layer

- 20 modules and 60 learner-facing files
- 7 crosscutting concepts
- 6 end-to-end pathways
- 3 Mermaid knowledge maps
- normalized core source ledger
- repository validator

All 20 modules remain **Draft** pending scientific and editorial review. Metadata and source normalization do not change scientific review status.

### Applied-material layer

- shared learning contract in `experiences/`
- 4 family standards
- 4 reusable templates
- 4 reviewed exemplars
- normalized experience-source ledger
- dedicated strict validator
- GitHub Actions validation workflow

## Phase 4 result

Phase 4 normalized the frontmatter of all 60 original learner files:

- unique canonical slugs by file role;
- consistent module identifiers and subject domains;
- canonical prerequisite lists;
- self-references and unknown connection identifiers removed;
- recoverable legacy references remapped;
- direct downstream modules added as canonical connections;
- deterministic normalizer and generated audit report;
- focused idempotence gate in GitHub Actions.

Phase 4 was merged through PR #4.

## Phase 5 result

Phase 5 repairs the original source infrastructure without changing educational prose.

### Ledger normalization

- recovered 109 historical logical source records from concatenated Markdown rows;
- rewrote the ledger to exactly one eight-column row per source;
- normalized DOI locators and canonical module identifiers;
- preserved source-to-module provenance;
- removed no records merely because they were weak without providing an inspected replacement;
- made normalization deterministic and idempotent.

### Verified replacement baseline

The inspected replacement registry:

- removed 22 weak or invalid legacy records;
- added 23 institutional, publisher, standards, textbook, or primary-literature records;
- matched all 22 declared replacement locators;
- repaired all five previously invalid book or publisher locators;
- strengthened the former coverage gaps in mathematical models, quantum foundations, cells and bioenergetics, and semiconductors.

### Final source audit

The normalized ledger now contains 110 records:

- 36 tier-1 primary-literature or review records;
- 57 tier-2 standards, agencies, institutions, universities, or textbooks;
- 17 other traceable publications;
- 0 weak or incomplete records under the Phase 5 classifier;
- 0 malformed rows;
- 0 invalid access dates;
- 0 invalid locators;
- 0 unmapped module fields.

Every one of the 20 core modules now has:

- at least 4 recorded sources;
- at least 2 policy-tier sources.

Audit files:

- `reports/phase-5-source-audit.json`
- `reports/phase-5-source-replacements.json`

Reusable tools:

- `scripts/normalize_source_ledger.py`
- `scripts/apply_verified_source_baseline.py`

## Status meanings

- **Draft** — content exists but has not completed focused scientific review.
- **Reviewed** — claims, sources, structure, safety, metadata, equations, and links received focused review.
- **Complete** — reviewed content passes the applicable strict release gate with no unresolved findings.
- **Blocked** — progress depends on a recorded unresolved issue.

## Validation

### Phase 4 metadata gate

```bash
python3 scripts/normalize_module_metadata.py
```

### Phase 5 source gate

```bash
python3 scripts/normalize_source_ledger.py --check --strict
python3 scripts/apply_verified_source_baseline.py --check
```

The Phase 5 GitHub Actions workflow is read-only. It checks the exact committed ledger and fails when:

- the table is not normalized;
- a locator, access date, or module field is malformed;
- any module has fewer than four total sources;
- any module has fewer than two policy-tier sources;
- an inspected replacement has not been applied.

### Core repository audit

```bash
python3 scripts/validate_repo.py
python3 scripts/validate_repo.py --strict
```

A clean metadata and source foundation does not certify scientific claims. Repository-wide strict release readiness still depends on Phases 6–10.

### Applied materials

```bash
python3 scripts/validate_experiences.py
python3 scripts/validate_experiences.py --strict
```

## Next phase: foundations scientific review

Phase 6 reviews Modules 01–05 in dependency order:

1. Scientific Reasoning
2. Measurement and Uncertainty
3. Mathematical Models
4. Probability and Statistics
5. Computation and Algorithms

Each module review must check:

- factual and conceptual accuracy;
- definitions and scope conditions;
- equations, symbols, units, and sign conventions;
- assumptions, approximations, and model limits;
- misconceptions and counterexamples;
- alignment between local citations and the central ledger;
- safety and age-appropriateness of explorations;
- consistency across `overview.md`, `technology.md`, and `explore.md`.

No module may move from Draft to Reviewed until all three learner-facing files complete that focused review.

## Remaining core work

1. Merge and independently review Phase 5 source repair.
2. Complete Phase 6 review of Modules 01–05.
3. Continue through Modules 06–20 in dependency order.
4. Reconcile pathways, concepts, maps, links, and terminology.
5. Pass repository-wide strict validation.
6. Consider software only after the material and review system is mature.

## Continuation instructions

Read `README.md`, `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, `AUDIT.md`, and this file. Keep metadata repair, source repair, scientific review, and applied-material expansion in separate focused pull requests. Never change scientific review status solely because metadata or source validation passes.
