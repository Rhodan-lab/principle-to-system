# Principia & Atlas unified product bundle

## Decision

Principia and Atlas remain separate repositories and separate authorities, but they no longer need to remain separate user experiences.

The new integration layer assembles an exact Principia Product Alpha package and an exact Atlas research workspace package into one local bundle with:

- one **Principia & Atlas** launcher;
- a Learn space backed by Principia;
- a Research space backed by Atlas;
- direct access to the facilitator recorder and Pilot Lab;
- deterministic suite navigation on every HTML surface;
- one combined manifest binding both source identities.

## Why the repositories are not merged

A repository merge would blur ownership and lifecycle rules. Principia owns causal explanation, pedagogy, pathways, investigations, and design experiences. Atlas owns exact research entities, provenance, lifecycle, staleness, and review state.

The product bundle joins navigation and runtime while preserving those responsibilities.

## Identity chain

The bundle records:

1. the SHA-256 identity of the verified Principia build manifest;
2. the Atlas workspace shell build digest and report digest;
3. the exact Atlas workspace ID and revision;
4. every copied file's byte length and SHA-256;
5. a deterministic bundle ID over the combined manifest.

## Runtime boundary

The server loads the complete verified bundle into memory before opening a loopback socket. It serves only manifest-declared paths, rejects untrusted Host headers, blocks framing, disables caching, and makes no external request.

Navigation chrome is injected only into served HTML responses. The stored Principia and Atlas snapshots remain byte-identical to their verified inputs.

## Product progression

This establishes the first actual combined product layer. A later online or SaaS version can replace the local package inputs with authenticated services, but it must preserve exact revision references, authority separation, and explicit revalidation instead of silently inheriting status.
