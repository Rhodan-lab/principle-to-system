---
title: "Product Alpha 0.2 optional field observation"
slug: product-alpha-0-2-optional-field-observation
domain: experience
experience_type: optional-observation-protocol
status: optional
artifact_revision: 10
release_status: draft
prerequisites: [product-alpha-refrigerator, product-alpha-distributed-information]
connections: [product-alpha-internal-multi-perspective-review, product-alpha-0-2-route-selection]
last_reviewed: 2026-08-03
content_license: CC-BY-4.0
---

# Product Alpha 0.2 optional field observation

This protocol is retained as an optional research capability. It is not a roadmap gate, release prerequisite, or decision authority.

The active authorities are the internal multi-perspective review and the implemented Product Alpha 0.2 route contract:

```bash
python3 software/product_alpha/evaluation/validate_internal_review.py check
python3 software/product_alpha/evaluation/validate_route_selection.py check
```

## When to use this protocol

Use it only when the project deliberately wants external observation of interaction problems, misconceptions, or workflow friction. There is no participant-count requirement and no requirement to run it before repository development continues.

Observations may inform a later decision, but they do not automatically authorize, block, or mutate repository work.

## Safety and privacy boundaries

- Do not collect names, contact details, school details, account identifiers, birth dates, or other identifying information.
- Use anonymous session labels.
- Keep all records outside the repository.
- Keep the workspace local and facilitator-controlled.
- Do not modify appliances or perform physical repair work for the refrigerator route.
- Keep distributed-information examples synthetic and disconnected from live services, accounts, networks, or real records.
- Review free text before export.
- Treat the recorder as a convenience boundary rather than a guarantee of anonymity.

## Route identity

Each optional observation workspace contains exactly one route and one deterministic build.

| Software route | Evidence route |
|---|---|
| `refrigerator` | `refrigerator-v1` |
| `distributed-information` | `distributed-information-v1` |

The packaged session template, evaluation rubric, facilitator recorder, and Pilot Lab all use the same evidence route. Intake rejects unknown routes, route drift, and mixed-route cohorts.

## Prepare refrigerator observation

```bash
python3 software/product_alpha/prepare_pilot.py \
  --workspace /private/path/refrigerator-observation \
  --route refrigerator
```

## Prepare distributed-information observation

```bash
python3 software/product_alpha/prepare_pilot.py \
  --workspace /private/path/distributed-information-observation \
  --route distributed-information
```

Preparation runs the selected deterministic build and loopback smoke gate before creating the empty workspace.

Launch the exact prepared build:

```bash
python3 software/product_alpha/launch_workspace.py \
  --workspace /private/path/<route>-observation \
  --open
```

The launcher reads the workspace evidence route, maps it back to the matching software route, rebuilds that route, fails closed on build drift, and stores no session data.

## Observation prompts

Focus on product behavior rather than scoring people:

1. Can the person identify the system boundary and important flows?
2. Do they predict a model direction before running it?
3. Can they connect the model result to a mechanism rather than only describing the chart?
4. Can they distinguish the route’s ordinary behavior from the diagnosed failure pattern?
5. Do they state what the model and source material support and do not prove?
6. Can they propose a redesign with a benefit, trade-off, and remaining risk?
7. Which interface step creates avoidable friction or ambiguity?

For refrigerator, watch for confusion about energy transfer, cycling, and short-cycling. For distributed information, watch for confusion about requests versus operations, queues versus service, timeout versus cancellation, and retry versus recovery.

Do not teach the answer before the first attempt. Record product problems without blaming the participant.

## Optional local evidence chain

Check the current stage without writing:

```bash
python3 software/product_alpha/evaluation/workspace_status.py \
  --workspace /private/path/<route>-observation
```

Validate current exports without sealing the cohort:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py check \
  --workspace /private/path/<route>-observation
```

If the project deliberately closes an observation set, it may use the existing assembly, review, decision, receipt, and handoff commands documented in the generated workspace README. Those tools retain privacy, non-overwrite, hash-binding, route-binding, and repository-external guarantees.

They do not authorize another route, public release, SaaS infrastructure, empirical learning claims, or repository mutation.

## Verification boundary

Lower-level tests cover both route packages, route-specific rubrics, facilitator record identity, Pilot Lab identity, session validation, mixed-route rejection, summary identity, route-specific workspace paths, and route-bound workspace launch.

A deterministic synthetic distributed-information fixture now verifies preparation, assembly, review, decision, receipt, handoff, verification, route-specific filenames, privacy redaction, and route-drift rejection. That fixture is test data only and must not be represented as real learner evidence.

## Claim boundary

Optional observation may reveal interaction failures or recurring confusion. It does not by itself establish:

- empirical learning effectiveness;
- retention;
- transfer;
- engagement outcomes;
- product-market fit;
- performance or security of a real distributed service;
- public production readiness.

The roadmap may proceed from internal product evidence whether or not this optional protocol is used.
