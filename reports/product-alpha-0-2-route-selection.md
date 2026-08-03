---
title: "Product Alpha 0.2 second-route selection"
slug: product-alpha-0-2-route-selection
domain: product
status: reviewed
artifact_revision: 1
release_status: alpha
prerequisites: [product-alpha-internal-multi-perspective-review]
connections: [system-dossier-web-service-request, failure-pattern-retry-storm-queue-collapse, investigation-queue-delay-near-capacity, design-challenge-resilient-school-information-service]
last_reviewed: 2026-08-03
content_license: CC-BY-4.0
---

# Product Alpha 0.2 second-route selection

**Decision date:** 2026-08-03
**Baseline:** refrigerator
**Selected route:** `distributed-information`
**Action:** `implement-distributed-information-model-adapter-and-route`

## Decision

Product Alpha will implement **Distributed Web Service, Queueing, and Recovery** as its second learner route.

The selection is not based on topic popularity. It is the strongest architectural test of whether Principia can move beyond a thermal-control implementation while preserving the same learner grammar:

```text
Observe → Map → Model → Diagnose → Redesign
```

The route is fully synthetic and offline. It uses queueing, capacity, retry feedback, failure amplification, and resilient information-service design without physical intervention, live-system traffic, real accounts, or personal data.

## Candidate comparison

The machine-readable authority is:

- `reports/product-alpha-0-2-route-selection.json`

Scores use a five-point scale and the declared weights in that file.

| Candidate | Weighted score | Main strength | Main reason not selected first |
|---|---:|---|---|
| Resilient energy | 3.90 | Rich energy, control, protection, and resilience trade-offs | Electrical protection, islanding, batteries, and physical safety add avoidable first-expansion risk |
| Water infrastructure | 3.95 | Strong measurement, fluid, treatment, storage, and public-infrastructure reasoning | Public-health boundaries make model interpretation and learner claims more difficult to isolate |
| Distributed information | **4.95** | Maximum architectural contrast, deterministic queue model, strong failure loop, safe offline execution, and rich redesign | Selected |

## Why distributed information wins

### Architectural contrast

Refrigerator is a physical thermal-control route. Distributed information is a software, queueing, protocol, organizational, and control route. Supporting both will reveal whether the current product is genuinely route-driven or merely a refrigerator interface with replaceable text.

### Deterministic model fit

The route supports a bounded analytical model:

$$\lambda_{offered}=\lambda_{external}(1+p_{retry})$$

$$\rho=\frac{\lambda_{offered}}{\mu}$$

and, under the stated M/M/1 assumptions when $\lambda_{offered}<\mu$,

$$W=\frac{1}{\mu-\lambda_{offered}}$$

Backlog growth can be represented by:

$$\frac{dB}{dt}=\lambda_{offered}-\mu$$

This is sufficient for prediction, parameter manipulation, model-boundary discussion, and a visible transition from stable service to sharp delay or accumulating backlog.

### Diagnostic clarity

The retry-storm pattern has an explicit positive-feedback mechanism:

```text
dependency slows
→ clients time out
→ synchronized retries increase offered load
→ queues grow
→ service slows further
→ more clients retry
```

The diagnosis task can distinguish a simple capacity shortage from a recovery action that amplifies the original failure.

### Redesign richness

The school information-service challenge requires decisions about:

- static-first versus dynamic service;
- freshness versus cache resilience;
- finite queues and admission control;
- retry ownership and deadlines;
- degraded and offline modes;
- low-bandwidth and accessible delivery;
- privacy-minimizing logs;
- rollback and correction authority;
- operational complexity and maintenance.

This tests whether Redesign remains a real systems decision rather than a decorative final step.

### Safe offline execution

The route must use fictional content and synthetic requests. It must not interact with a real website, API, school system, account, network, or device, and it must not contain real student records or personal information.

## Canonical route chain

| Role | Canonical source |
|---|---|
| System dossier | `system-dossiers/web-service-request.md` |
| Failure pattern | `failure-atlas/retry-storm-queue-collapse.md` |
| Investigation | `investigations/queue-delay-near-capacity.md` |
| Design challenge | `design-challenges/resilient-school-information-service.md` |

All four artifacts are reviewed canonical inputs. Product Alpha will extract from them rather than creating a second content database.

## Implementation contract

The selected route contract is:

- `software/product_alpha/route-contracts/distributed-information.json`

It defines:

- title and learner-facing purpose;
- five route prompts;
- the queue model adapter and parameters;
- prediction choices;
- required outputs and chart semantics;
- diagnosis challenge;
- safety and claim boundaries;
- Atlas operating decision;
- reusable-shell requirements;
- acceptance criteria for a runnable route.

The contract is deliberately separate from `software/product_alpha/routes/`. A buildable route file must not be added until the generic learner shell can use a queue adapter. This prevents a configuration from appearing supported while the browser still contains thermal-only controls and calculations.

## Required architecture change

The current builder already loads route configurations generically. The learner shell remains the actual constraint because its model activity contains thermal labels, controls, prediction language, calculations, and chart descriptions.

The next implementation must introduce a model-adapter boundary with at least these operations:

```text
validate(parameters)
run(parameters)
summarize(result)
describe-chart(result)
```

All labels, controls, prediction choices, result names, chart semantics, and limitations must come from the route payload or adapter. Route-specific equations must not remain embedded in the generic shell.

The generic shell must continue to own:

- navigation;
- learner notes;
- prediction-before-model validation;
- diagnosis-before-feedback validation;
- accessible focus and live recovery;
- canonical content rendering;
- evidence boundaries;
- in-tab state;
- privacy and no-persistence behavior.

## Refrigerator preservation rule

The refrigerator route remains the default stable baseline until the second route is independently runnable.

The refactor must preserve:

- deterministic refrigerator build output;
- thermal model direction and visible precision;
- learner-state behavior;
- diagnosis behavior;
- accessibility semantics;
- loopback security;
- facilitator and Pilot Lab contracts.

## Atlas decision

No Atlas repository change is authorized by route selection alone.

The distributed-information route can begin from canonical Principia artifacts and their direct standards sources. Atlas expansion is deferred until implementation identifies a concrete exact-revision entity, relation, or provenance gap. Live Atlas calls and status inheritance remain prohibited.

## Claim boundary

This decision establishes:

- a deterministic route-selection process;
- selection of `distributed-information`;
- a machine-readable implementation contract;
- authorization to refactor the learner shell for model adapters.

It does not establish:

- a runnable second route;
- performance or security of a real web service;
- empirical learning effectiveness;
- product-market fit;
- public production readiness.

## Validation

Run the read-only decision validator:

```bash
python3 software/product_alpha/evaluation/validate_route_selection.py check
```

The next repository milestone is complete only after the adapter refactor and buildable distributed-information route pass focused regression coverage while refrigerator remains unchanged.
