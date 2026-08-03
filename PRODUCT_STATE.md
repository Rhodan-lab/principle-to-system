---
title: "Principia current product state"
slug: principia-current-product-state
domain: product
status: reviewed
artifact_revision: 7
release_status: alpha
prerequisites: []
connections: [product-alpha-refrigerator, product-alpha-internal-multi-perspective-review, product-alpha-0-2-route-selection]
last_reviewed: 2026-08-03
content_license: CC-BY-4.0
---

# Principia current product state

**Last updated:** 2026-08-03
**Active milestone:** Product Alpha 0.2 — distributed-information model adapter and reusable learner shell
**Active repository:** `Rhodan-lab/principle-to-system`
**Supporting repository:** `Rhodan-lab/Atlas`
**Decision authority:** deterministic internal multi-perspective review plus the validated second-route scorecard and contract

## Current decision

Principia remains the learner-facing product. Atlas remains a read-only trust and provenance substrate.

The refrigerator route is the stable Product Alpha baseline. The internal multi-perspective review authorized next-product planning through:

```text
advance-to-next-product-planning-review
```

The second-route decision is now complete:

```text
selected route: distributed-information
action: implement-distributed-information-model-adapter-and-route
```

The next repository work is implementation, not another planning or readiness layer.

External participant observation remains optional research. It is not a roadmap gate, release prerequisite, or authority requirement. GitHub issues are not part of the current execution workflow.

## Internal review authority

The Product Alpha 0.1 baseline review remains authoritative for product quality and claim boundaries:

- `reports/product-alpha-0-1-multi-perspective-review.json`;
- `reports/product-alpha-0-1-multi-perspective-review.md`.

Validate it without writing:

```bash
python3 software/product_alpha/evaluation/validate_internal_review.py check
```

The eight perspectives remain:

1. product strategy;
2. pedagogy;
3. scientific integrity;
4. UX and accessibility;
5. privacy and security;
6. operational reliability;
7. evidence and provenance;
8. maintainability and governance.

## Second-route selection authority

The Product Alpha 0.2 selection artifacts are:

- `reports/product-alpha-0-2-route-selection.json`;
- `reports/product-alpha-0-2-route-selection.md`;
- `software/product_alpha/route-contracts/distributed-information.json`.

Validate them without writing:

```bash
python3 software/product_alpha/evaluation/validate_route_selection.py check
```

The scorecard compared all three reviewed alternatives outside the refrigerator baseline:

| Candidate | Weighted score | Decision |
|---|---:|---|
| Resilient energy | 3.90 | Defer until the reusable shell is proven with lower physical-safety complexity |
| Water infrastructure | 3.95 | Defer until the reusable shell is proven without public-health interpretation risk |
| Distributed information | **4.95** | Selected for implementation |

## Why distributed information is selected

Distributed information is the strongest first generalization test because it:

- is maximally different from the physical thermal-control baseline;
- can be explored entirely through synthetic, offline data;
- has a deterministic queueing model with explicit assumptions and failure conditions;
- supports prediction before model execution;
- provides a clear retry-feedback diagnosis challenge;
- requires redesign across performance, reliability, accessibility, low-bandwidth delivery, privacy, freshness, recovery, and operational complexity;
- does not require speculative Atlas expansion before implementation begins.

The canonical source chain is:

| Role | Source |
|---|---|
| System dossier | `system-dossiers/web-service-request.md` |
| Failure pattern | `failure-atlas/retry-storm-queue-collapse.md` |
| Investigation | `investigations/queue-delay-near-capacity.md` |
| Design challenge | `design-challenges/resilient-school-information-service.md` |

## Architecture finding

`software/product_alpha/build.py` already loads route configuration and canonical source roles generically.

The current learner shell is the real blocker because its model activity still embeds refrigerator-specific:

- labels;
- input controls;
- prediction choices;
- thermal calculations;
- result text;
- chart title and description;
- limitations.

A buildable `software/product_alpha/routes/distributed-information.json` must not be added until the shell can invoke a route-specific model adapter. A configuration that builds while the browser still runs thermal logic would create false support.

## Required model-adapter boundary

The next implementation must introduce a route-driven adapter with at least these operations:

```text
validate(parameters)
run(parameters)
summarize(result)
describe-chart(result)
```

The distributed-information contract defines the first adapter:

```text
queue-delay-fluid-v1
```

Its model relates external arrival rate, retry fraction, service capacity, utilization, mean delay under stated stable assumptions, backlog growth, queue capacity, observation duration, and rejected work.

All model labels, controls, prediction choices, output names, chart semantics, and limitations must come from the route payload or adapter rather than thermal literals in the generic shell.

## Generic shell responsibilities

The route-independent shell must continue to own:

- Observe → Map → Model → Diagnose → Redesign navigation;
- learner notes that remain in the active tab only;
- prediction-before-model validation;
- diagnosis-before-feedback validation;
- visible focus and accessible error recovery;
- canonical Markdown rendering;
- evidence and claim boundaries;
- no account, analytics, persistence, external runtime, or repository mutation behavior.

## Refrigerator preservation rule

The refrigerator route remains the default until distributed information is independently runnable.

The adapter refactor must preserve:

- deterministic refrigerator build output;
- thermal model direction and visible precision;
- learner-state behavior;
- diagnosis behavior;
- accessibility semantics;
- loopback security;
- facilitator and Pilot Lab contracts.

The second route is not complete merely because its contract exists.

## What the project may claim

The project may claim:

- internally validated Product Alpha 0.1 coherence;
- a complete stable refrigerator route;
- a deterministic three-candidate route-selection process;
- selection of `distributed-information`;
- a machine-readable second-route implementation contract;
- authorization to refactor the learner shell around model adapters;
- continued local-first privacy, deterministic build, and provenance boundaries.

## What the project may not claim

The current decision does not establish:

- a runnable second route;
- performance or security of a real distributed service;
- empirical learning effectiveness;
- validated comprehension, retention, transfer, or engagement outcomes;
- product-market fit;
- public production readiness;
- that internal inspection substitutes for measured human outcomes.

These are claim boundaries, not roadmap blockers.

## Authorized next implementation

The next product change should:

1. extract refrigerator model controls and calculations from the generic learner shell;
2. define a stable adapter interface for validation, execution, summary, and chart description;
3. reimplement the thermal model as the first adapter without changing its behavior;
4. implement `queue-delay-fluid-v1` as the second adapter;
5. add `software/product_alpha/routes/distributed-information.json` only when the second adapter is usable;
6. render both routes from canonical source files;
7. add focused JavaScript and Python regression coverage for both adapters;
8. keep refrigerator as the default route until both deterministic checks pass.

## Work that remains premature

Do not begin these from route selection alone:

- public production deployment;
- account systems;
- behavioral analytics;
- cloud storage of learner data;
- live Atlas runtime calls;
- broad SaaS infrastructure;
- automatic publication or repository mutation.

## Optional field-evaluation capability

The recorder, Pilot Lab, repository-external workspace, aggregation, review, decision, receipt, and handoff tools remain available for optional observation or future research.

They are not required for adapter implementation, route implementation, repository progress, or internal product decisions.

## Atlas operating state

No Atlas repository change is authorized by this selection.

The distributed-information route can begin from canonical Principia artifacts and direct standards sources. Atlas expansion remains deferred until implementation reveals a concrete exact-revision entity, relation, or provenance gap. Live Atlas access and status inheritance remain prohibited.

## Historical governance status

Phases 0–50 remain preserved in `PROJECT_STATE.md`, `release/`, `reports/`, validators, and tests as research and compatibility history.

They are not the active product roadmap. No recursive readiness or assurance phase should be added without a concrete product requirement.

## Current next action

The selected action is:

```text
implement-distributed-information-model-adapter-and-route
```

The next PR should implement the reusable model-adapter boundary and keep the refrigerator route behaviorally stable while making the distributed-information route genuinely runnable.
