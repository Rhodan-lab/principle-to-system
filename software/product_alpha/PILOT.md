---
title: "Product Alpha 0.1 optional field observation"
slug: product-alpha-0-1-optional-field-observation
domain: experience
experience_type: optional-observation-protocol
status: optional
artifact_revision: 9
release_status: draft
prerequisites: [system-dossier-refrigerator]
connections: [product-alpha-internal-multi-perspective-review]
last_reviewed: 2026-08-03
content_license: CC-BY-4.0
---

# Product Alpha 0.1 optional field observation

This protocol is retained as an optional research capability. It is not a roadmap gate, release prerequisite, or decision authority.

The active decision authority is the internal multi-perspective review:

```bash
python3 software/product_alpha/evaluation/validate_internal_review.py check
```

## When to use this protocol

Use it only when the project deliberately wants external observation of interaction problems, misconceptions, or workflow friction. There is no minimum participant count and no requirement to run it before planning or implementing another route.

Observations may inform a later decision, but they do not automatically authorize, block, or mutate repository work.

## Safety and privacy boundaries

- Do not collect names, contact details, school details, account identifiers, birth dates, or other identifying information.
- Use anonymous session labels.
- Keep all records outside the repository.
- Keep the workspace local and facilitator-controlled.
- Do not modify appliances or ask anyone to perform physical repair work.
- Review free text before export.
- Treat the recorder as a convenience boundary rather than a guarantee of anonymity.

## Optional preparation

Prepare a repository-external workspace:

```bash
python3 software/product_alpha/prepare_pilot.py   --workspace /private/path/refrigerator-observation
```

Preparation runs the deterministic build and loopback smoke gate before creating the empty workspace.

Launch the exact prepared build:

```bash
python3 software/product_alpha/launch_workspace.py   --workspace /private/path/refrigerator-observation   --open
```

The launcher fails closed on build drift and stores no session data.

## Observation prompts

When external observation is intentionally used, focus on product behavior rather than scoring people:

1. Can the person identify the system boundary and important flows?
2. Do they predict a model direction before running it?
3. Can they distinguish model output from a universal physical claim?
4. Can they distinguish controlled cycling from an abnormal failure condition?
5. Do they understand what the pinned evidence revision supports and does not prove?
6. Can they state a redesign benefit and trade-off?
7. Which interface step creates avoidable friction or ambiguity?

Do not teach the answer before the first attempt. Record product problems without blaming the participant.

## Optional local evidence chain

The existing tools remain available:

```bash
python3 software/product_alpha/evaluation/workspace_status.py   --workspace /private/path/refrigerator-observation

python3 software/product_alpha/evaluation/assemble_workspace.py check   --workspace /private/path/refrigerator-observation
```

If the project deliberately closes an observation set, it may use the existing assembly, review, decision, and handoff commands. Those tools retain their privacy, non-overwrite, hash-binding, and repository-external guarantees.

They do not authorize another route, public release, SaaS infrastructure, empirical learning claims, or repository mutation.

## Claim boundary

Optional observation may reveal interaction failures or recurring confusion. It does not by itself establish:

- empirical learning effectiveness;
- retention;
- transfer;
- engagement outcomes;
- product-market fit;
- public production readiness.

The current roadmap proceeds from the internal review decision, whether or not this optional protocol is used.
