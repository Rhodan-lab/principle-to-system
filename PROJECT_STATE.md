# Project State

> Last updated: 2026-07-25

## Current phase

**Material foundation expansion complete; repository-wide module audit remains in progress.**

The repository now contains two coordinated layers:

1. a structurally complete first draft of 20 core modules and synthesis materials;
2. a reviewed applied-material foundation for system explanation, failure analysis, investigation, and design.

The applied layer is material-first Markdown, not a software product. Its purpose is to establish reusable educational architecture and high-quality exemplar content before any optional interface is considered.

## Content inventory

### Core layer

- 20 modules and 60 learner-facing files
- 7 crosscutting concepts
- 6 end-to-end pathways
- 3 Mermaid knowledge maps
- legacy source ledger
- repository validator

All 20 modules remain **Draft** pending the systematic scientific and editorial audit recorded in [`AUDIT.md`](AUDIT.md).

### Applied-material layer

- shared learning contract in `experiences/`
- 4 family standards
- 4 reusable templates
- 4 reviewed exemplars:
  - domestic refrigerator system dossier
  - feedback-instability failure pattern
  - room-cooling investigation
  - passive-cooler design challenge
- normalized experience-source ledger
- dedicated strict validator
- GitHub Actions workflow for relevant changes

## Status meanings

- **Draft** — content exists but has not completed focused review.
- **Reviewed** — claims, sources, structure, safety, metadata, equations, and links received a focused review.
- **Complete** — reviewed content also passes the applicable strict release gate and has no unresolved review findings.
- **Blocked** — progress depends on a recorded unresolved issue.

The four applied exemplars are **Reviewed**, not Complete. Independent review and successful CI are still required before a release claim.

## Validation

### Core audit

```bash
python3 scripts/validate_repo.py
python3 scripts/validate_repo.py --strict
```

The core repository is not yet release-ready because known legacy metadata and source-ledger defects remain.

### Applied materials

```bash
python3 scripts/validate_experiences.py
python3 scripts/validate_experiences.py --strict
```

The experience validator checks:

- required family, exemplar, and template files;
- frontmatter fields and experience types;
- valid unique slugs;
- canonical module, concept, and experience identifiers;
- required family-specific headings;
- at least one displayed quantitative model;
- explicit safety language for investigations and challenges;
- direct source URLs;
- internal links;
- normalized source-ledger rows and coverage.

`.github/workflows/validate-experiences.yml` runs the strict gate on relevant pull requests and pushes to `main`.

## Source state

The legacy [`sources/source-ledger.md`](sources/source-ledger.md) still requires normalization. New applied materials are recorded in [`sources/experience-source-ledger.md`](sources/experience-source-ledger.md), which uses one source per row and exactly eight columns.

This separation preserves provenance without pretending the older ledger is repaired.

## Remaining core blockers

1. Repair malformed slug values in original learner files.
2. Normalize original `domain`, `prerequisites`, and `connections` metadata.
3. Split concatenated legacy source rows.
4. Replace weak module sources with policy-compliant references.
5. Review Modules 01–20 in dependency order.
6. Reconcile pathways, concepts, maps, and terminology against reviewed modules.
7. Pass repository-wide strict validation.

## Applied-material expansion rules

New materials must:

1. begin from the correct file in `templates/`;
2. use canonical identifiers;
3. include a meaningful quantitative model;
4. state boundaries, assumptions, uncertainty, failure modes, and trade-offs;
5. keep all activities optional and safe;
6. add inspected sources to the normalized experience ledger;
7. pass `python3 scripts/validate_experiences.py --strict`.

## Next highest-priority actions

1. Run and review the applied-material CI result.
2. Obtain independent scientific review of the four exemplars.
3. Expand each family only after the exemplar pattern proves stable.
4. Continue the original module metadata and source repair in dependency order.
5. Avoid building software until the material architecture and review workflow are mature.

## Continuation instructions

Read `README.md`, `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, `AUDIT.md`, and this file. Keep module-audit work separate from applied-material expansion. Never mark content Complete solely because the file exists or because structural validation passes.
