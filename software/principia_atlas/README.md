# Principia & Atlas product bundle

This directory turns the cross-repository compatibility work into one navigable local product without merging authority or adding a live runtime dependency.

## Product shape

The bundle contains three layers:

- a root **Principia & Atlas** launcher;
- one exact verified Principia Product Alpha package under `principia/`;
- one exact verified Atlas research workspace shell under `atlas/`.

The loopback runtime adds deterministic navigation chrome to HTML responses so every surface can return to the suite or move between Learn and Research. Stored source snapshots are not rewritten.

## One-command workflow

Keep the Principia and Atlas repositories as sibling checkouts, or pass the Atlas path explicitly. From the Principia repository, build, verify, smoke-test, and launch the complete product with:

```bash
python3 software/principia_atlas/orchestrate.py run \
  --atlas-repo ../Atlas \
  --route distributed-information \
  --output /tmp/principia-atlas \
  --open
```

The orchestrator performs all of the following before the server starts:

1. verifies both checkout roots and records their exact Git commits;
2. rejects tracked source changes unless `--allow-dirty` is explicitly supplied;
3. runs the official Atlas product-input deterministic check;
4. runs the Principia Product Alpha deterministic check;
5. builds and verifies the official Atlas eight-file package;
6. builds the selected Principia route;
7. assembles, verifies, and loopback-smoke-tests the combined bundle;
8. publishes the new bundle atomically only after every check passes;
9. writes a sealed build receipt beside the output.

A failed replacement leaves the last successfully published product untouched. An output-specific lock rejects overlapping builds.

## Commands

Build without starting the server:

```bash
python3 software/principia_atlas/orchestrate.py build \
  --atlas-repo ../Atlas \
  --route distributed-information \
  --output /tmp/principia-atlas
```

Run the complete deterministic assembly twice without publishing:

```bash
python3 software/principia_atlas/orchestrate.py check \
  --atlas-repo ../Atlas \
  --route distributed-information
```

Verify an already published product and its source receipt:

```bash
python3 software/principia_atlas/orchestrate.py verify \
  --output /tmp/principia-atlas
```

The build receipt is written to:

```text
/tmp/principia-atlas.build-receipt.json
```

It binds the combined bundle ID to the Principia commit, Atlas commit, Principia build ID, Atlas shell/report digests, exact Atlas workspace revision, and preserved authority boundaries.

For release or CI use, exact source revisions can be enforced:

```bash
python3 software/principia_atlas/orchestrate.py build \
  --atlas-repo ../Atlas \
  --expected-principia-commit <full-principia-commit> \
  --expected-atlas-commit <full-atlas-commit> \
  --route distributed-information \
  --output /tmp/principia-atlas
```

## Lower-level package API

`orchestrate.py` is the product entry point. `suite.py` remains available for inspecting or assembling already-built source packages:

```bash
python3 software/principia_atlas/suite.py build \
  --principia /tmp/principia-package \
  --atlas /tmp/atlas-product-input \
  --atlas-report /tmp/atlas-product-input/workspace-shell-build-report.json \
  --output /tmp/principia-atlas
```

## Preserved boundaries

```yaml
product_runtime: unified-local-suite
authorities_separate: true
status_inheritance: prohibited
principia_snapshot: exact-manifest-verified
atlas_snapshot: exact-build-report-verified
source_commits: sealed-in-build-receipt
live_cross_repository_dependency: false
external_network_required: false
canonical_mutation: false
repository_mutation: false
```

The bundle is a product integration layer. It does not grant Atlas authority over pedagogy, grant Principia authority over knowledge status, or create a release decision.
