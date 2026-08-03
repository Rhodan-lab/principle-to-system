---
title: "Principia current product state"
slug: principia-current-product-state
domain: product
status: reviewed
artifact_revision: 6
release_status: alpha
prerequisites: []
connections: [product-alpha-refrigerator, product-alpha-internal-multi-perspective-review]
last_reviewed: 2026-08-03
content_license: CC-BY-4.0
---

# Principia current product state

**Last updated:** 2026-08-03  
**Active milestone:** Product Alpha 0.2 — second-route planning and reusable route architecture  
**Active repository:** `Rhodan-lab/principle-to-system`  
**Supporting repository:** `Rhodan-lab/Atlas`  
**Decision authority:** deterministic internal multi-perspective review plus an explicit repository decision

## Current decision

Principia remains the learner-facing product. Atlas remains a read-only trust and provenance substrate.

The refrigerator route is now the stable Product Alpha baseline. It has passed the required internal review across:

1. product strategy;
2. pedagogy;
3. scientific integrity;
4. UX and accessibility;
5. privacy and security;
6. operational reliability;
7. evidence and provenance;
8. maintainability and governance.

The primary decision is:

> Advance to next-product planning, select a second system route, and use that route to prove reusable architecture without destabilizing the refrigerator baseline.

External participant observation is optional research. It is not a roadmap gate, release prerequisite, or authority requirement.

GitHub issues are not part of the current execution workflow.

## Internal review authority

The canonical review artifacts are:

- `reports/product-alpha-0-1-multi-perspective-review.json`;
- `reports/product-alpha-0-1-multi-perspective-review.md`.

Validate them without writing:

```bash
python3 software/product_alpha/evaluation/validate_internal_review.py check
```

The validator requires exactly eight perspectives, concrete repository evidence, residual risks, next actions, claim boundaries, and the decision:

```text
advance-to-next-product-planning-review
```

## Multi-perspective result

| Perspective | Status | Current judgment |
|---|---|---|
| Product strategy | Pass | One complete route and a clear next test: generalization to a second route |
| Pedagogy | Pass | Prediction, mechanism, model interpretation, diagnosis, evidence boundary, and redesign are structurally required |
| Scientific integrity | Pass | The thermal model is bounded, limitation-aware, and separated from universal physical claims |
| UX and accessibility | Pass | Keyboard, focus, semantic grouping, live recovery, table, dialog, and dynamic-chart contracts are covered |
| Privacy and security | Pass | Local-first, no accounts or analytics, no persistence, loopback-only, restrictive headers, and fail-closed loading |
| Operational reliability | Pass | Deterministic packaging, build identity, smoke verification, drift rejection, and focused CI |
| Evidence and provenance | Pass | Canonical Principia sources and pinned Atlas revisions remain separate, advisory, deterministic, and offline |
| Maintainability and governance | Pass | Current authority is separated from historical phases and protected by regression tests |

## Completed Product Alpha baseline

Product Alpha 0.1 includes:

- a five-step refrigerator journey: Observe → Map → Model → Diagnose → Redesign;
- canonical content extraction from existing Principia artifacts;
- a dependency-free thermal model and diagnosis challenge;
- pinned exact-revision Atlas references with separate status authority;
- in-tab learner reasoning state without browser persistence;
- accessible learner navigation, tables, dialogs, choice validation, and dynamic chart descriptions;
- a local anonymous facilitator recorder with semantic scoring groups and precise validation recovery;
- fail-closed learner and facilitator loading states;
- a browser-local Pilot Lab with additive batches, deliberate replacement, duplicate rejection, accessible tables, and protected destructive actions;
- deterministic packaging and a 64-character build identity;
- loopback-only serving with exact Host validation and restrictive response headers;
- optional repository-external observation, aggregation, review, decision, and handoff tools;
- focused Product Alpha JavaScript, Python, runtime, smoke, and clean-repository CI.

The stable browser and runtime baseline was completed through PR #151.

## What the project may claim

The project may claim:

- internally validated product coherence;
- a complete refrigerator learning journey;
- deterministic local packaging and operation;
- bounded scientific and model design;
- exact-revision evidence and provenance separation;
- tested keyboard accessibility and failure recovery;
- local-first privacy and loopback security contracts;
- operational readiness to begin a second-route implementation;
- authorization to perform next-product planning.

## What the project may not claim

The project may not claim from internal review alone:

- empirical learning effectiveness;
- validated comprehension, retention, transfer, or engagement outcomes;
- product-market fit;
- public production readiness;
- universal scientific accuracy beyond the model's stated boundaries;
- that internal inspection substitutes for measured human outcomes.

These are claim boundaries, not roadmap blockers.

## Authorized next work

The next product cycle may:

1. choose a second system route from the canonical corpus;
2. define route-selection criteria;
3. separate reusable product architecture from refrigerator-specific content;
4. implement the candidate route using the same Observe → Map → Model → Diagnose → Redesign grammar when appropriate;
5. preserve prediction-before-model and choice-before-feedback contracts;
6. preserve accessibility, privacy, security, deterministic build, and provenance boundaries;
7. add Atlas entities only when the selected route creates a concrete exact-revision evidence need;
8. update this state file after the second-route planning decision.

## Work that remains premature

Do not begin these merely because the internal review passed:

- public production deployment;
- account systems;
- behavioral analytics;
- cloud storage of learner data;
- live Atlas runtime calls;
- broad SaaS infrastructure;
- automatic publication or repository mutation.

A second route should first prove that the architecture generalizes.

## Optional field-evaluation capability

The existing workspace, recorder, Pilot Lab, cohort aggregation, review, decision, receipt, and handoff tools remain available for optional external observation or future research.

They are not required for:

- second-route planning;
- route implementation;
- repository progress;
- internal product decisions.

Any optional records remain local, private, repository-external, and non-authoritative unless a future decision explicitly adopts them.

## Product boundaries

The current alpha has:

- no accounts;
- no analytics;
- no cloud database;
- no external runtime dependency;
- no live Atlas call;
- no browser persistence for learner, recorder, or Pilot Lab state;
- no automatic repository mutation;
- no automated publication;
- no production deployment contract.

## Atlas operating state

The bounded Atlas evidence chain remains complete for the accepted refrigerator baseline.

Do not expand Atlas from abstract readiness. Expand it only when the selected second route requires a new evidence entity, revision, relation, or provenance record.

## Historical governance status

Phases 0–50 remain preserved in `PROJECT_STATE.md`, `release/`, `reports/`, validators, and tests as research and compatibility history.

They are not the active product roadmap. No recursive readiness or assurance phase should be added without a concrete product requirement.

## Current next action

The selected action is:

```text
advance-to-next-product-planning-review
```

The next repository work should identify and score candidate second routes, choose one, and define the reusable architecture changes required to implement it.
