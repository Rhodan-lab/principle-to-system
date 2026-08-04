# Principia & Atlas product bundle

This directory turns the cross-repository compatibility work into one navigable local product without merging authority or adding a live runtime dependency.

## Product shape

The bundle contains three layers:

- a root **Principia & Atlas** launcher;
- one exact verified Principia Product Alpha package under `principia/`;
- one exact verified Atlas research workspace shell under `atlas/`.

The loopback runtime adds deterministic navigation chrome to HTML responses so every surface can return to the suite or move between Learn and Research. Stored source snapshots are not rewritten.

## One-command product workflow

Keep the Principia and Atlas repositories as sibling checkouts, or pass the Atlas path explicitly. Product output must remain outside both source repositories. From the Principia repository, build, verify, smoke-test, and launch the complete product with:

```bash
python3 software/principia_atlas/orchestrate.py run \
  --atlas-repo ../Atlas \
  --route distributed-information \
  --output /tmp/principia-atlas \
  --open
```

The orchestrator performs all of the following before the server starts:

1. verifies both checkout roots and records their exact Git commits;
2. rejects tracked changes and untracked files unless `--allow-dirty` is explicitly supplied;
3. records a SHA-256 digest of each checkout's Git status in the source receipt;
4. runs the official Atlas product-input deterministic check;
5. runs the Principia Product Alpha deterministic check;
6. builds and verifies the official Atlas eight-file package;
7. builds the selected Principia route;
8. assembles, verifies, and loopback-smoke-tests the combined bundle;
9. publishes the bundle and sealed receipt as one rollback-capable transaction.

A failed source build, smoke, receipt write, or receipt verification leaves the last complete product-and-receipt pair untouched. An output-specific lock rejects overlapping builds. An incomplete pre-existing pair is rejected rather than overwritten ambiguously.

## Product commands

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

Receipt contract `principia-atlas-orchestration-receipt/0.2` binds the combined bundle ID to the Principia commit, Atlas commit, clean/dirty status digest, Principia build ID, Atlas shell/report digests, exact Atlas workspace revision, and preserved authority boundaries. Verification remains compatible with receipt contract `0.1` for already built products.

For release or CI use, exact source revisions can be enforced:

```bash
python3 software/principia_atlas/orchestrate.py build \
  --atlas-repo ../Atlas \
  --expected-principia-commit <full-principia-commit> \
  --expected-atlas-commit <full-atlas-commit> \
  --route distributed-information \
  --output /tmp/principia-atlas
```

`--allow-dirty` is development-only. A dirty build records `clean: false` and the status digest in its receipt; it is not equivalent to a clean release build.

## Versioned release archive

`release.py` converts the verified local product into one versioned ZIP archive with a SHA-256 sidecar. The default release version is `0.1.0-alpha.1`; every supplied version must be valid SemVer.

Build the product and release in one command:

```bash
python3 software/principia_atlas/release.py build \
  --atlas-repo ../Atlas \
  --route distributed-information \
  --version 0.1.0-alpha.1 \
  --output /tmp/principia-atlas-0.1.0-alpha.1.zip
```

A release build performs the complete product build and verification first, then produces:

```text
/tmp/principia-atlas-0.1.0-alpha.1.zip
/tmp/principia-atlas-0.1.0-alpha.1.zip.sha256
```

The archive is byte-deterministic for the same verified product and version. It uses sorted canonical paths, fixed ZIP timestamps, stored entries, stable file modes, no directory entries, and one version-bound root directory.

Release manifest contract `principia-atlas-release/0.1` binds:

- the SemVer release version and release ID;
- the unified bundle ID and orchestration receipt ID;
- the selected Principia route;
- every payload path, byte size, and SHA-256 digest;
- local-only runtime and preserved authority boundaries;
- Linux/macOS, macOS double-click, and Windows launch entrypoints.

The archive and checksum are published as one rollback-capable pair under an output lock. A failed checksum write, archive verification, product verification, or replacement restores the previous complete pair.

Package an already verified product:

```bash
python3 software/principia_atlas/release.py pack \
  --product /tmp/principia-atlas \
  --version 0.1.0-alpha.1 \
  --output /tmp/principia-atlas-0.1.0-alpha.1.zip
```

Check that packaging the same product twice produces identical archive bytes:

```bash
python3 software/principia_atlas/release.py check \
  --product /tmp/principia-atlas \
  --version 0.1.0-alpha.1
```

Verify the checksum, strict archive structure, release manifest seal, payload hashes, bundled product manifest, and source receipt:

```bash
python3 software/principia_atlas/release.py verify \
  --output /tmp/principia-atlas-0.1.0-alpha.1.zip
```

After extraction, the release no longer requires either repository. Its standalone verifier and loopback launcher require Python 3.10 or newer:

```bash
cd principia-atlas-0.1.0-alpha.1
python3 launcher.py verify
./launch.sh
```

Other packaged entrypoints are:

```text
launch.command   macOS double-click launcher
launch.cmd       Windows launcher
launcher.py run  direct cross-platform loopback launcher
```

The standalone runtime verifies all extracted payload files before binding to `127.0.0.1`. It does not use accounts, cloud persistence, or an external network.

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
release_runtime: extracted-loopback-suite
authorities_separate: true
status_inheritance: prohibited
principia_snapshot: exact-manifest-verified
atlas_snapshot: exact-build-report-verified
source_commits: sealed-in-build-receipt
source_status: tracked-and-untracked-bound
product_publication: bundle-and-receipt-rollback-transaction
release_publication: archive-and-checksum-rollback-transaction
release_manifest: sealed-path-size-digest-inventory
live_cross_repository_dependency: false
external_network_required: false
canonical_mutation: false
repository_mutation: false
```

The bundle and release are product integration layers. They do not grant Atlas authority over pedagogy, grant Principia authority over knowledge status, or create a release decision.
