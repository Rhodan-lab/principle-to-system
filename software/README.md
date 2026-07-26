# Principia software foundation

This directory contains the Phase 13 reference implementation for turning the repository's material foundation into a browsable static site.

The software does **not** duplicate module content into a database or application-specific format. Markdown and JSON in the repository remain the source of truth.

## What the build produces

- a home page and catalog summary;
- module index and one page per module;
- one rendered page for every core, synthesis, and applied document;
- a local full-text search index;
- a module dependency graph;
- a machine-readable content catalog;
- a deterministic build manifest.

The current frozen scope is:

```text
60 core learner files
16 synthesis files
16 applied experience files
92 rendered content documents
20 module group pages
```

## Requirements

- Python 3.12 or newer;
- no third-party Python packages;
- no Node.js dependency;
- no build-time network access.

## Build

Run from the repository root:

```bash
python3 software/principia_site.py build --output software/dist
```

The generator refuses to clean a non-empty output directory unless that directory contains its own `.principia-build` marker.

## Inspect the catalog

```bash
python3 software/principia_site.py inspect --pretty
```

## Preview locally

```bash
python3 software/principia_site.py serve --output software/dist --port 8000
```

Then open `http://127.0.0.1:8000`.

## Tests

```bash
python3 -m unittest discover -s software/tests -v
python3 scripts/validate_phase13_software.py
```

The test and validation layers check catalog counts, three-view module completeness, HTML escaping, unsafe-link rejection, protected output cleanup, deterministic builds, graph integrity, search completeness, machine-only governance, Phase 12 continuity, and read-only CI.

## Editing content

To add or modify material:

1. edit the relevant Markdown file in `foundations/`, `science/`, `technology/`, `pathways/`, `concepts/`, `maps/`, or one of the applied-experience directories;
2. keep its frontmatter and repository links valid;
3. rebuild the site;
4. run the validators.

Navigation, search data, catalog records, document pages, and dependency relationships are regenerated automatically. No application code needs to be changed for ordinary content edits.

## Deliberate limits

Phase 13 is a reference foundation, not the final product experience. It deliberately avoids accounts, analytics, remote databases, live Atlas calls, content editing in the browser, external search services, and automated publication. Those capabilities can be layered later without changing the repository's content authority model.
