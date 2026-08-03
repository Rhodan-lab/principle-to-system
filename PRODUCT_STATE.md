---
title: "Principia current product state"
slug: principia-current-product-state
domain: product
status: reviewed
artifact_revision: 8
release_status: alpha
prerequisites: []
connections: [product-alpha-refrigerator, product-alpha-internal-multi-perspective-review, product-alpha-0-2-route-selection, product-alpha-distributed-information]
last_reviewed: 2026-08-03
content_license: CC-BY-4.0
---

# Principia current product state

**Last updated:** 2026-08-03
**Active milestone:** Product Alpha 0.2 — two-route local alpha and route-aware evidence records
**Active repository:** `Rhodan-lab/principle-to-system`
**Supporting repository:** `Rhodan-lab/Atlas`
**Decision authority:** internal multi-perspective review, validated route selection, implemented route contract, and focused Product Alpha CI

## Current decision

Principia remains the learner-facing product. Atlas remains a read-only trust and provenance substrate.

The internal multi-perspective review authorized roadmap progress through:

```text
advance-to-next-product-planning-review
```

The selected implementation action was:

```text
implement-distributed-information-model-adapter-and-route
```

That implementation is now complete as a local alpha. The current product state is:

```text
status: implemented-local-alpha
baseline route: refrigerator
second route: distributed-information
learner architecture: two-route local alpha
```

External participant observation remains optional research. It is not a roadmap gate, release prerequisite, or authority requirement. GitHub issues are not part of the current execution workflow.

## Runnable learner routes

### Refrigerator

```bash
python3 software/product_alpha/run_pilot.py --route refrigerator --open
```

The refrigerator route remains the default and uses:

```text
thermal-cabinet-v1
```

Its deterministic thermal direction, visible precision, prediction gate, diagnosis behavior, accessibility semantics, and local privacy boundaries remain protected by regression tests.

### Distributed information

```bash
python3 software/product_alpha/run_pilot.py --route distributed-information --open
```

The second route uses:

```text
queue-delay-fluid-v1
```

It presents the same five-step learner grammar:

```text
Observe → Map → Model → Diagnose → Redesign
```

The route is built from reviewed canonical sources for web-service requests, retry-storm queue collapse, queue delay near capacity, and resilient school information service design. Its model is synthetic, local, deterministic, and dependency-free.

## Architecture result

The learner shell is no longer thermal-specific.

The shell now obtains these items from route configuration or a model adapter:

- activity title;
- input controls and labels;
- parameter ranges and units;
- prediction choices and feedback;
- model execution;
- result summary;
- chart title and description;
- model limitations.

The adapter boundary provides:

```text
validate(parameters)
run(parameters)
summarize(result)
describe-chart(result)
```

The shared shell continues to own navigation, learner notes, validation recovery, accessibility, canonical content rendering, evidence boundaries, and in-tab state.

## Deterministic package identity

Each packaged learner build contains a route-bound marker and exactly one matching route payload.

The browser loads:

```text
data/${routeId}.json
```

and fails closed when the packaged route identity does not match the payload. The package includes the local `model-adapters.js` asset and makes no external runtime request.

Both routes are validated independently:

```bash
python3 software/product_alpha/build.py check --route refrigerator
python3 software/product_alpha/build.py check --route distributed-information
python3 software/product_alpha/run_pilot.py check --route refrigerator
python3 software/product_alpha/run_pilot.py check --route distributed-information
```

## Product authorities

Validate the Product Alpha 0.1 internal review:

```bash
python3 software/product_alpha/evaluation/validate_internal_review.py check
```

Validate the Product Alpha 0.2 selection and implementation contract:

```bash
python3 software/product_alpha/evaluation/validate_route_selection.py check
```

The route-selection score remains:

| Candidate | Weighted score | State |
|---|---:|---|
| Resilient energy | 3.90 | Deferred |
| Water infrastructure | 3.95 | Deferred |
| Distributed information | **4.95** | Implemented local alpha |

## What the project may claim

The project may claim:

- internally validated Product Alpha coherence;
- a stable default refrigerator route;
- a buildable and loopback-runnable distributed-information route;
- a reusable learner shell demonstrated across physical thermal and distributed queue domains;
- deterministic route-bound packaging for both routes;
- prediction-before-model and diagnosis-before-feedback contracts for both routes;
- local-first operation without accounts, analytics, browser persistence, cloud storage, or live Atlas calls;
- preservation of accessibility, privacy, security, and provenance boundaries during route generalization.

## What the project may not claim

The current evidence does not establish:

- performance of a real distributed service;
- security of a real school system;
- empirical learning effectiveness;
- validated comprehension, retention, transfer, or engagement outcomes;
- product-market fit;
- public production readiness;
- that internal inspection substitutes for measured human outcomes.

These are claim boundaries, not roadmap blockers.

## Concrete remaining defect

The learner and launcher layers are route-aware, but the facilitator and evidence-record layer is not yet fully route-aware.

The current session template still contains:

```text
route_id: refrigerator-v1
```

This creates a real integrity risk: a distributed-information session could be exported or aggregated under refrigerator identity.

## Current next action

The next repository change must:

1. bind the packaged route identity into the facilitator recorder;
2. generate the correct route ID in exported session records;
3. update the session template from one hard-coded route to an explicit supported-route contract;
4. reject unknown or mismatched route identities in validation, Pilot Lab, aggregation, review, and handoff paths;
5. preserve existing refrigerator evidence compatibility;
6. add dual-route evidence tests before any third route is considered.

The next milestone is therefore:

```text
make-facilitator-and-evidence-records-route-aware
```

## Optional field-evaluation capability

Recorder, Pilot Lab, repository-external workspace, aggregation, review, decision, receipt, and handoff tools remain optional research capability. They are not required for roadmap progress.

Their route-identity integrity must still be corrected because optional evidence must not be mislabeled when used.

## Atlas operating state

No Atlas repository change is required by the implemented route.

The route uses reviewed canonical Principia material and direct source boundaries. Atlas expansion remains deferred until a concrete exact-revision evidence gap appears. Live Atlas access and status inheritance remain prohibited.

## Work that remains premature

Do not begin these merely because two routes are runnable:

- a third route before evidence records become route-aware;
- public production deployment;
- account systems;
- behavioral analytics;
- cloud learner-data storage;
- live Atlas runtime calls;
- broad SaaS infrastructure;
- automatic publication or repository mutation.

## Historical governance status

Phases 0–50 remain preserved in `PROJECT_STATE.md`, `release/`, `reports/`, validators, and tests as compatibility and research history.

They are not the active roadmap. No recursive readiness or assurance phase should be added without a concrete product requirement.
