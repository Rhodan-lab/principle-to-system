---
title: Principia & Atlas release promotion boundary
status: implemented
scope: product-integration
---

# Principia & Atlas release promotion boundary

The release promotion layer converts a verified versioned archive into an immutable channel decision without merging Principia learning authority and Atlas knowledge-status authority.

## Contracts

- `principia-atlas-promotion/0.1` seals the exact tag, channel, release identity, archive digest, source revisions, compatibility snapshot, predecessor, and upgrade result.
- `principia-atlas-release-index/0.1` seals cumulative immutable version history and the current `alpha`, `beta`, and `stable` pointers.

## Channel policy

- `MAJOR.MINOR.PATCH-alpha.N` maps to `alpha`.
- `MAJOR.MINOR.PATCH-beta.N` maps to `beta`.
- `MAJOR.MINOR.PATCH` maps to `stable`.
- Other prerelease labels and build metadata are rejected.
- The exact Git tag is `principia-atlas-v<VERSION>`.
- Every candidate must advance global SemVer precedence.

## Promotion gates

A candidate is rejected when any of these conditions is true:

- the archive, checksum, release manifest, product bundle, or source receipt fails verification;
- either source checkout was dirty;
- Git tags and historical promotion assets do not match exactly;
- a version or tag is replayed;
- a channel pointer moves backward;
- a non-major upgrade changes the route, release contract, required launch entrypoints, loopback host, authority boundary, or raises the Python minimum;
- a major upgrade weakens authority separation or loopback-only operation.

## Publication

The tag-triggered GitHub Actions workflow rebuilds from the exact Principia tag commit and pinned Atlas commit, reconstructs all promotion history from previous GitHub Release assets, prepares and verifies the new promotion, and only then publishes the release archive, checksum, descriptor, and cumulative index.

Alpha and beta releases are marked prerelease. Stable releases are marked latest. Existing releases for the same tag are never overwritten.
