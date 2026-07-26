# Principia Release Governance

This directory defines machine-readable material and software governance for Principia. Phase 12 records the validated material candidate; Phase 13 authorizes continued software development through declared machine gates without changing material status or activating publication.

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
- the historical non-live Principia–Atlas bridge fixture, now evolved into a non-live bridge candidate.

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

## Phase 13 machine-only authority

`phase-13-machine-governance.json` supersedes the former human-review blocking policy for active development.

```yaml
authority_mode: machine-only
human_review_required: false
automatic_merge: false
automatic_publication: false
failure_behavior: block-progression
```

A Phase 13 pass authorizes continued software development only. It does not mark material Complete, release applied experiences, copy Atlas status, or activate live integration.

The Phase 13 machine gate passes on draft PR #15, so the software foundation state is `foundation-validated`.

The machine gate requires Phase 12 continuity, strict repository validation, safe content ingestion, unit tests, deterministic byte-identical builds, catalog and graph integrity, complete local search indexing, generated-link validation, and read-only CI.

## Principia–Atlas bridge candidate

The delayed-feedback slice is now a Principia-side Atlas Phase 2 importer candidate:

```yaml
mode: bridge-candidate
live: false
decision: candidate-ready
```

The exact dependency set pins `model:en:delayed-correction-recurrence@2` and keeps the related claim and concepts at revision 1. `phase-12-revision-impact.json` records the inspected adoption without changing Principia artifact revision, pedagogical status, or release status.

The deterministic export contract `principia-atlas-external-dependent/0.2` includes `depends_on_exact`. Atlas remains unchanged and decides independently whether its Phase 2 importer accepts the candidate.

A future live bridge still requires a separate validated contract transition. This candidate performs no network call, repository synchronization, status inheritance, automatic merge, or automatic publication.
