# Phase 13 — Software Foundation

> Branch: `agent/phase-13-software-foundation`  
> Baseline: Phase 12 RC1 merged through PR #14 at `824fa2d4774647203222ab9198fc25ad4b11cda5`  
> Authority mode: **machine-only**  
> Atlas integration: **non-live**

## Purpose

Phase 13 creates the first executable Principia layer without moving the material foundation into a proprietary database or duplicating it into application-specific content files.

Repository Markdown and JSON remain authoritative. The software discovers them, validates them, and produces disposable static output.

## Owner directive

The project owner explicitly removed human review as a blocking project gate. Phase 13 therefore uses deterministic machine gates for progression.

This does not mean the software claims perfect scientific correctness. It means progression is decided by declared automated contracts rather than an undefined future reviewer.

Automatic merge and automatic public publication remain disabled. A failing machine gate blocks progression.

## Architecture

```text
repository Markdown and JSON
→ frontmatter and document ingestion
→ canonical content catalog
→ module grouping and dependency graph
→ safe Markdown-to-HTML rendering
→ navigation, search, and applied-experience views
→ deterministic static build manifest
```

## Implementation

`software/principia_site.py` provides:

- repository content discovery;
- minimal frontmatter parsing for the existing contract;
- safe HTML escaping;
- external-link scheme restrictions;
- Markdown headings, paragraphs, lists, tables, blockquotes, code, and display-math preservation;
- internal content-link resolution;
- module grouping from `overview.md`, `technology.md`, and `explore.md`;
- synthesis and applied-experience indexes;
- local search-index generation;
- module dependency-graph generation;
- deterministic content and output digests;
- protected output-directory cleanup;
- local static preview serving.

The implementation uses the Python standard library only and performs no build-time network fetch.

## Generated surfaces

A build generates:

```text
index.html
modules/index.html
modules/<module-id>.html
documents/<slug>.html
pathways/index.html
experiences/index.html
graph/index.html
search/index.html
api/catalog.json
api/search-index.json
api/graph.json
api/build-manifest.json
assets/site.css
assets/site.js
```

## Scope invariants

The Phase 13 catalog must contain exactly:

- 20 modules;
- 60 core learner files;
- 16 synthesis files;
- 16 applied-experience files;
- 92 rendered content documents.

Every module must retain all three canonical views. Core pedagogical status remains `reviewed`; experience release status remains `draft`.

## Machine-only governance

`release/phase-13-machine-governance.json` changes the active project transition from:

```text
candidate-hold
```

into:

```text
machine-gated-development
```

It does not promote material, copy Atlas status, enable live integration, merge pull requests, or publish a public release.

## Validation

The permanent workflow runs:

```bash
python3 scripts/finalize_phase12_validation_record.py --check
python3 scripts/validate_phase12_release_candidate.py
python3 scripts/validate_repo.py --strict
python3 -m unittest discover -s software/tests -v
python3 scripts/validate_phase13_software.py
python3 software/principia_site.py build --output phase13-site
```

The Phase 13 validator checks:

- machine-only governance;
- Phase 12 lifecycle continuity;
- standard-library-only Python imports;
- catalog counts and unique identities;
- three-view module completeness;
- search-index completeness;
- graph endpoint integrity;
- Reviewed/Draft status preservation;
- local browser assets only;
- unsafe DOM execution patterns;
- generated-link validity and path containment;
- two byte-identical builds;
- read-only workflow permissions.

## Content operations

Ordinary material expansion requires only a valid repository content file. After rebuild, the new or changed content is reflected automatically in the generated document pages, catalog, search index, and any applicable module or collection views.

No software-code edit is required for routine content additions.

## Deliberate boundaries

Phase 13 does not add:

- accounts or identity;
- remote databases;
- browser-based authoring;
- analytics or tracking;
- live Atlas calls;
- automatic merge;
- automatic publication;
- status inheritance between repositories.

These remain future capabilities governed by explicit machine contracts.
