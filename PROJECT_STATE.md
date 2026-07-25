# Project State

> Last updated: 2026-07-25

## Current phase

**Phase 4 core metadata normalization implemented; Phase 5 legacy source repair is next.**

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
| 4 | Core metadata normalization | Implemented on PR #4; awaiting merge |
| 5 | Legacy source-ledger repair | Next |
| 6 | Foundations scientific review | Not started systematically |
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
- legacy source ledger
- repository validator

All 20 modules remain **Draft** pending scientific and editorial review. Metadata normalization does not change scientific review status.

### Applied-material layer

- shared learning contract in `experiences/`
- 4 family standards
- 4 reusable templates
- 4 reviewed exemplars
- normalized experience-source ledger
- dedicated strict validator
- GitHub Actions validation workflow

## Phase 4 result

Phase 4 normalizes the frontmatter of all 60 original learner files.

Implemented changes:

- unique canonical slugs for `overview.md`, `technology.md`, and `explore.md`;
- a consistent `module` identifier for each module;
- subject domains normalized to `foundations`, `science`, or `technology`;
- prerequisite lists replaced with the canonical dependency graph;
- self-references and unknown connection identifiers removed;
- recoverable legacy references remapped to canonical module IDs;
- direct downstream modules added as canonical connections;
- a generated audit record saved at `reports/phase-4-metadata-normalization.json`;
- deterministic normalization implemented in `scripts/normalize_module_metadata.py`;
- a focused GitHub Actions gate added for Phase 4 changes.

The generated audit processed all 60 expected learner files, changed all 60, and reported no processing errors.

Phase 4 CI checks that normalization is idempotent: running the normalizer again must produce no further changes.

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

The command exits successfully only when all 60 learner files already match the canonical metadata contract.

To regenerate metadata and its audit report:

```bash
python3 scripts/normalize_module_metadata.py --write
```

### Core repository audit

```bash
python3 scripts/validate_repo.py
python3 scripts/validate_repo.py --strict
```

The repository-wide validator still reports legacy source-ledger and later-phase review findings. Those do not invalidate the focused Phase 4 metadata result.

### Applied materials

```bash
python3 scripts/validate_experiences.py
python3 scripts/validate_experiences.py --strict
```

## Source state and Phase 5

The legacy [`sources/source-ledger.md`](sources/source-ledger.md) remains the next blocking area. It contains concatenated entries and lower-tier sources that prevent repository-wide release readiness.

Phase 5 must:

1. split every concatenated entry into one source per row;
2. enforce exactly eight columns per row;
3. preserve source-to-module provenance;
4. verify URLs and DOI records;
5. replace weak sources with standards, agencies, institutions, strong textbooks, reviews, or primary literature;
6. rerun the repository-wide validator and record the remaining scientific-review backlog.

New applied materials remain recorded separately in [`sources/experience-source-ledger.md`](sources/experience-source-ledger.md).

## Remaining core work

1. Merge and independently review Phase 4 metadata normalization.
2. Complete Phase 5 legacy source repair.
3. Review Modules 01–05 scientifically and editorially.
4. Continue through Modules 06–20 in dependency order.
5. Reconcile pathways, concepts, maps, links, and terminology.
6. Pass repository-wide strict validation.

## Continuation instructions

Read `README.md`, `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, `AUDIT.md`, and this file. Keep metadata repair, source repair, scientific review, and applied-material expansion in separate focused pull requests. Never change scientific review status solely because metadata or structural validation passes.
