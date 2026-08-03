# Principia Product Alpha 0.2

Product Alpha is a local-first learner application built from canonical Principia Markdown and JSON. It now supports two independently buildable routes through one route-driven learner shell:

- `refrigerator` using `thermal-cabinet-v1`;
- `distributed-information` using `queue-delay-fluid-v1`.

The package requires no account, analytics, cloud storage, browser persistence, live Atlas call, or external runtime dependency.

## Learner grammar

Both routes use the same progression:

```text
Observe → Map → Model → Diagnose → Redesign
```

The shared shell owns:

- navigation and step state;
- learner notes that remain in the active tab;
- prediction-before-model validation;
- diagnosis-before-feedback validation;
- canonical content rendering;
- keyboard access, visible focus, and live error recovery;
- evidence and claim boundaries;
- fail-closed route loading.

Route configuration or a model adapter owns:

- activity title;
- parameter controls, labels, ranges, and units;
- prediction choices;
- model equations and execution;
- summaries and output names;
- chart title and description;
- model limitations.

## Model-adapter boundary

The local `model-adapters.js` registry implements:

```text
validate(model, parameters)
run(model, parameters)
summarize(model, result)
describeChart(model, result)
draw(model, result, chart, description)
```

The current adapters are:

```text
thermal-cabinet-v1
queue-delay-fluid-v1
```

Route-specific calculations are not embedded in the generic learner shell.

## Run refrigerator

Refrigerator remains the default route.

```bash
python3 software/product_alpha/run_pilot.py --route refrigerator --open
```

Equivalent default command:

```bash
python3 software/product_alpha/run_pilot.py --open
```

The route uses reviewed canonical sources for the refrigerator system, feedback instability, room-cooling investigation, and passive-cooler redesign challenge.

## Run distributed information

```bash
python3 software/product_alpha/run_pilot.py --route distributed-information --open
```

The route uses reviewed canonical sources for web-service requests, retry-storm queue collapse, queue delay near capacity, and resilient school information-service design.

Its model is synthetic and local. It reasons about arrival rate, service capacity, retry fraction, utilization, stable mean delay under stated assumptions, backlog growth, finite queue capacity, and estimated rejected work. It does not measure or predict a real service.

## Route-bound packaging

Every build writes one route payload and injects the same route identity into the packaged learner HTML.

The learner loads:

```text
data/${routeId}.json
```

and fails closed if the payload route ID does not match the packaged marker.

The deterministic package includes:

```text
index.html
model-adapters.js
facilitator.html
pilot-lab.html
evaluation/rubric.json
evaluation/session-template.json
data/<route-id>.json
build-manifest.json
```

The manifest and Pilot build identity bind the exact packaged bytes.

## Validate both routes

```bash
python3 software/product_alpha/build.py check --route refrigerator
python3 software/product_alpha/build.py check --route distributed-information
python3 software/product_alpha/run_pilot.py check --route refrigerator
python3 software/product_alpha/run_pilot.py check --route distributed-information
node --test software/tests/test_product_alpha*.mjs
python3 -m unittest discover -s software/tests -p 'test_product_alpha*.py' -v
```

The loopback launcher binds only to `127.0.0.1`, rejects untrusted Host headers, uses no-store and restrictive response headers, verifies the route payload and manifest, and requires the local adapter asset.

## Product authorities

Validate the internal eight-perspective Product Alpha review:

```bash
python3 software/product_alpha/evaluation/validate_internal_review.py check
```

Validate the second-route selection and implemented contract:

```bash
python3 software/product_alpha/evaluation/validate_route_selection.py check
```

The implemented contract is:

```text
software/product_alpha/route-contracts/distributed-information.json
status: implemented-local-alpha
```

## Current evidence-record limitation

Learner packaging and launch are route-aware. The optional facilitator and evidence-record chain still contains a refrigerator-specific session-template route ID.

Until that is corrected, do not treat distributed-information recorder exports as route-integrity-complete evidence. The next product milestone is:

```text
make-facilitator-and-evidence-records-route-aware
```

This limitation does not block local learner-route development or inspection. It prevents optional evidence from being mislabeled.

## Optional field observation

Field observation is optional research, not a roadmap gate or release prerequisite.

[`PILOT.md`](PILOT.md) documents the repository-external workspace, recorder, Pilot Lab, aggregation, review, decision, and handoff tools. Those tools retain privacy, non-overwrite, hash-binding, and no-repository-mutation boundaries.

They must not collect identifying information, and they must not be used for distributed-information evidence until route identity is bound through the full record chain.

## Safety and privacy boundaries

- Keep the distributed-information route synthetic and offline.
- Do not connect model execution to a real service, account, school system, network, or device.
- Use fictional content and no personal information.
- Keep learner notes and recorder state local.
- Do not add accounts, analytics, browser persistence, automatic upload, or live Atlas calls.
- Do not treat a simplified model as proof about a real system.

## Claim boundary

The current package may support claims about:

- two buildable and loopback-runnable learner routes;
- reusable model-adapter architecture;
- deterministic route-bound packaging;
- local-first privacy and security contracts;
- tested prediction, diagnosis, accessibility, and failure-recovery behavior.

It does not establish:

- empirical learning effectiveness;
- comprehension, retention, transfer, or engagement outcomes;
- performance or security of a real distributed service;
- product-market fit;
- public production readiness.

These are claim boundaries, not a requirement to run a real learner cohort before continuing repository development.
