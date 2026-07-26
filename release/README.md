# Principia Release Governance

This directory defines release-candidate governance for the material-first Principia repository. It does not publish software and does not convert automated validation into scientific, editorial, ethical, accessibility, legal, or release authority.

## Status layers

Principia keeps three decisions separate:

| Layer | Field or record | Meaning |
| --- | --- | --- |
| Pedagogical maturity | `status` | Whether Principia’s focused content review has reached Draft, Reviewed, Complete, or Blocked |
| Artifact identity | `artifact_revision` | Exact dependency-relevant revision of an applied artifact |
| Publication readiness | `release_status` | Whether an applied artifact is Draft, Candidate, Released, Deprecated, or Retracted |

Atlas knowledge lifecycle remains separate. No Atlas status is copied into Principia and no Principia status is copied into Atlas.

## Phase 12 candidate

`phase-12-release-candidate.json` is the machine-readable RC1 contract. It freezes the expected inventory and policy for:

- 20 core modules;
- 6 pathways;
- 7 crosscutting concepts;
- 3 knowledge maps;
- 16 applied experiences in 4 complete routes;
- 143 core source records;
- 28 experience-source records;
- the non-live Principia–Atlas bridge fixture.

The candidate proves repository-wide consistency. It does **not** mark content Complete or Released.

## Automated gate

The Phase 12 validator may verify:

- exact counts and canonical paths;
- metadata and lifecycle separation;
- internal links and source-ledger coverage;
- terminology and equation contracts;
- safety boundaries;
- basic document accessibility heuristics;
- exact-revision dependency behavior;
- deprecation, retraction, and block-release policy;
- read-only CI;
- preservation of the non-live Atlas boundary.

A validator pass means only that the committed repository conforms to these machine-checkable rules.

## Human authority gate

Release still requires explicit recorded decisions for:

1. independent scientific review;
2. editorial and pedagogical review;
3. accessibility and usability review;
4. safety and ethical review where applicable;
5. source and attribution review;
6. release-owner approval;
7. Atlas-side approval before any live cross-repository pilot.

Until those records exist, the repository release decision remains `hold` and experience `release_status` remains `draft`.

## First bounded integration pilot

The delayed-feedback slice remains the preferred pilot because it already has an exact-revision compatibility fixture. The pilot may become live only after:

- Atlas exits its direct-integration freeze;
- Principia approves a live manifest;
- Atlas accepts the external dependent;
- revision, staleness, deprecation, retraction, and recovery behavior pass end to end;
- neither repository imports the other repository’s status.

Phase 12 tests readiness for that pilot but does not activate it.
