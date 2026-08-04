# Principia & Atlas product bundle

This directory turns the existing cross-repository compatibility work into one navigable local product without merging authority or adding a live dependency.

## Product shape

The bundle contains three layers:

- a root **Principia & Atlas** launcher;
- one exact verified Principia Product Alpha package under `principia/`;
- one exact verified Atlas research workspace shell under `atlas/`.

The loopback runtime adds deterministic navigation chrome to HTML responses so every surface can return to the suite or move between Learn and Research. The stored source snapshots are not rewritten.

## Build inputs

Build the two source packages first.

Principia:

```bash
python3 software/product_alpha/build.py build \
  --route distributed-information \
  --output /tmp/principia-package
```

Atlas, from the Atlas repository:

```bash
rm -rf /tmp/atlas-workspace
mkdir -p /tmp/atlas-workspace
cp apps/workspace-shell/index.html /tmp/atlas-workspace/index.html
cp apps/workspace-shell/styles.css /tmp/atlas-workspace/styles.css
cp apps/workspace-shell/app.js /tmp/atlas-workspace/app.js
cp apps/workspace-shell/README.md /tmp/atlas-workspace/README.md
python -m tools.phase4_workspace.build_shell \
  --output-dir /tmp/atlas-workspace \
  --report-output /tmp/atlas-workspace-report.json
```

Assemble the suite from the Principia repository:

```bash
python3 software/principia_atlas/suite.py build \
  --principia /tmp/principia-package \
  --atlas /tmp/atlas-workspace \
  --atlas-report /tmp/atlas-workspace-report.json \
  --output /tmp/principia-atlas
```

Verify and serve it:

```bash
python3 software/principia_atlas/suite.py verify \
  --bundle /tmp/principia-atlas
python3 software/principia_atlas/suite.py check \
  --bundle /tmp/principia-atlas
python3 software/principia_atlas/suite.py serve \
  --bundle /tmp/principia-atlas \
  --open
```

## Preserved boundaries

```yaml
product_runtime: unified-local-suite
authorities_separate: true
status_inheritance: prohibited
principia_snapshot: exact-manifest-verified
atlas_snapshot: exact-build-report-verified
live_cross_repository_dependency: false
external_network_required: false
canonical_mutation: false
repository_mutation: false
```

The bundle is a product integration layer. It does not grant Atlas authority over pedagogy, grant Principia authority over knowledge status, or create a release decision.
