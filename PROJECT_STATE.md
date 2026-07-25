# Project State

> Last updated: 2026-07-25

## Current phase

**Repository-wide scientific and editorial audit in progress.**

The full content architecture exists: 20 modules with 60 learner-facing files, 7 crosscutting concepts, 6 pathways, 3 knowledge maps, a source ledger, and a repository validator. This is a complete first draft, not yet a fully reviewed release.

A module may be marked **Complete** only after its three learner-facing files have passed scientific review, source verification, metadata and link checks, and strict repository validation.

## Content inventory

- 20 modules and 60 core learner files are present.
- 7 crosscutting concepts are present.
- 6 end-to-end pathways are present.
- 3 Mermaid knowledge maps are present.
- A central source ledger is present.
- A standard-library-only validator is present.

Presence does not imply review completion. `INDEX.md` is the source of truth for module review status.

## Review status

All 20 modules are currently **Draft** pending systematic review.

Review order follows the dependency graph:

1. Foundations: Modules 01–05
2. Physical science: Modules 06–12
3. Life and Earth systems: Modules 13–16
4. Technology: Modules 17–20
5. Crosscutting concepts, pathways, and maps
6. Repository-wide terminology, links, and source reconciliation

## Validation status

`scripts/validate_repo.py` has been hardened to check:

- required repository and module files;
- frontmatter syntax and required fields;
- slug syntax and uniqueness;
- canonical module identifiers and prerequisite consistency;
- exact section headings;
- explicit principle-to-system chains;
- relative links and repository-boundary escapes;
- agreement between learner-file status and `INDEX.md`;
- source-ledger row structure and weak-source warnings;
- strict release readiness with `--strict`.

The repository is **not currently release-ready**. Known metadata and source-ledger defects must be repaired before strict validation can pass.

## Known blocking issues

1. Several learner files contain malformed slug values introduced while resolving duplicate slugs, such as a quoted slug followed by `-technology` outside the quotes.
2. Many `connections` values use identifiers that do not correspond to canonical module IDs.
3. Some file `domain` values describe the file role rather than the module’s subject domain.
4. The source ledger contains concatenated entries that must be split into one source per Markdown table row.
5. Several modules rely on encyclopedia or weak secondary sources where the source policy calls for primary literature, standards, consensus reports, or strong textbooks.
6. Module status previously said Complete even though learner-file frontmatter remained Draft.
7. Structural validation does not substitute for scientific review of claims, equations, units, assumptions, safety, and trade-offs.
8. The validation workflow still needs to be added under `.github/workflows/` by an actor with workflow permission.

## Definition of reviewed

A module can move from Draft to Reviewed only when all three files satisfy the following:

- causal explanations are scientifically accurate and appropriately scoped;
- equations, symbols, sign conventions, and SI units are correct;
- assumptions, approximations, system boundaries, scales, and failure conditions are explicit;
- sources have been opened and verified, and ledger entries are valid;
- prerequisites and connections use canonical repository identifiers;
- relative links resolve;
- exploration activities are safe, free, and age-appropriate;
- unnecessary repetition, exam framing, unsupported claims, and padding are removed.

## Definition of complete

A module can move from Reviewed to Complete only when:

- no unresolved scientific or editorial review comments remain;
- all three learner files have `status: complete` and a current `last_reviewed` date;
- its pathways, maps, and crosscutting links remain consistent;
- `python3 scripts/validate_repo.py --strict` passes repository-wide.

## Next highest-priority actions

1. Repair malformed frontmatter and normalize canonical identifiers across all 60 learner files.
2. Normalize the source ledger to exactly one source per row.
3. Run the validator and resolve all structural errors.
4. Review Modules 01–05 scientifically and editorially, then update their statuses only after review.
5. Continue through Modules 06–20 in dependency order.
6. Reconcile pathways, concepts, and maps against the reviewed modules.
7. Add the GitHub Actions validation workflow and require strict validation for release-oriented pull requests.

## Continuation instructions

Read `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, this file, and `AUDIT.md`. Work on a branch, keep each pull request focused, update sources and `last_reviewed` dates with factual changes, and do not change a module’s status until its review criteria are met.
