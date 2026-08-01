---
title: "Principia current product state"
slug: principia-current-product-state
domain: product
status: draft
artifact_revision: 3
release_status: alpha
prerequisites: []
connections: [product-alpha-refrigerator, product-alpha-learner-pilot]
last_reviewed: 2026-08-01
content_license: CC-BY-4.0
---

# Principia current product state

**Last updated:** 2026-08-01  
**Active milestone:** Product Alpha 0.1 — real cohort execution and human review  
**Active repository:** `Rhodan-lab/principle-to-system`  
**Supporting repository:** `Rhodan-lab/Atlas`  
**Decision authority:** verifiable real learner evidence, not phase counts, issue state, or tool-generated status

## Current decision

Principia remains the learner-facing product. Atlas remains a read-only trust and provenance substrate.

The current primary decision is:

> Keep the refrigerator route stable and run the documented 5–8 learner pilot before authorizing another route, public release, or production infrastructure.

The active work is direct repository development and evidence review. GitHub issues are not part of the current execution workflow.

## Completed product foundation

Product Alpha 0.1 now includes:

- a five-step refrigerator journey: Observe → Map → Model → Diagnose → Redesign;
- canonical content extraction from existing Principia artifacts;
- a dependency-free thermal model and diagnosis challenge;
- pinned exact-revision Atlas references with separate status authority;
- a local anonymous facilitator recorder;
- a deterministic Pilot Lab with duplicate and mixed-build rejection;
- a loopback-only launcher with deterministic build identity;
- a pilot-day HTTP smoke gate;
- expected-build cohort verification;
- a private, hash-bound, de-identified human-review packet;
- executable learner-runtime coverage for the thermal model;
- focused Product Alpha CI.

Relevant merged work now extends through:

| Change | Result |
|---|---|
| PR #103 | Local Product Alpha Pilot Lab |
| PR #104 | Additive duplicate-counter repair |
| PR #105 | Deterministic Pilot build identity |
| PR #106 | Build-bound cohort records and mixed-build rejection |
| PR #107 | Expected-build verification CLI |
| PR #108 | Pilot-day loopback smoke gate |
| PR #109 | Hash-bound human-review packet |
| PR #110 | Learner thermal-model runtime repair |

## Evidence integrity finding

The software and pilot instrumentation are validated. The repository still does not contain a de-identified aggregate report derived from 5–8 real learner sessions.

That absence is recorded honestly in:

- `reports/product-alpha-0-1-pilot-summary.md`

The report keeps cohort values **not reportable** rather than inventing, estimating, or simulating learner outcomes.

## What the project may claim

The project may claim:

- deterministic Product Alpha packaging;
- a working local learner interface and facilitator recorder;
- build-bound anonymous session records;
- duplicate and mixed-build rejection;
- a loopback-only smoke-tested launcher;
- deterministic cohort verification and review-packet generation;
- technical readiness for a small formative pilot.

## What the project may not claim

The project may not yet claim:

- verified completion of a 5–8 learner cohort;
- demonstrated learning effectiveness;
- validated retention or transfer;
- evidence that the refrigerator route meets progression thresholds;
- authorization for a second route;
- public-release readiness;
- product-market fit;
- SaaS or production readiness.

## Active evidence workflow

Before participant sessions:

```bash
python3 software/product_alpha/run_pilot.py smoke
python3 software/product_alpha/run_pilot.py --open
```

Use one printed 64-character Pilot build ID for the entire cohort. Every session record must carry that same ID.

After collecting 5–8 valid anonymous sessions, verify the cohort:

```bash
python3 software/product_alpha/evaluation/verify_cohort.py \
  --input path/to/anonymous-sessions.jsonl \
  --expect-build-id <64-character-pilot-build-id> \
  --format markdown
```

Then create the private human-review packet outside the repository:

```bash
python3 software/product_alpha/evaluation/prepare_review.py \
  --input path/to/anonymous-sessions.jsonl \
  --expect-build-id <64-character-pilot-build-id> \
  --output-prefix /private/cohort-folder/refrigerator-review
```

Keep raw records and private review files outside the repository. Commit only a separately reviewed, de-identified product change.

## Revision triggers

Revise Product Alpha before another route when any of these conditions appear:

- the same confusion tag occurs in at least two sessions;
- fewer than half of started sessions reach redesign;
- average mechanism, diagnosis, or evidence-boundary score is below 1.25;
- learners manipulate the model without first predicting direction;
- learners treat Atlas status as proof of a physical conclusion;
- learners finish but do not voluntarily continue.

## Product boundaries

The current alpha has:

- no accounts;
- no analytics;
- no cloud database;
- no external runtime dependency;
- no live Atlas call;
- no browser storage for pilot records;
- no automatic repository mutation;
- no automated publication;
- no production deployment contract.

Pilot records remain local, anonymous, private, and facilitator-controlled.

## Atlas operating state

The bounded Atlas evidence chain is complete for the accepted refrigerator baseline: bridge, drift audit, registry, promotion gate, impact index, hypothetical simulation, and automatic runtime preflight.

Do not add more Atlas abstraction until a real Principia candidate snapshot or canonical evidence change requires it.

## Historical governance status

Phases 0–50 remain preserved in `PROJECT_STATE.md`, `release/`, `reports/`, validators, and tests as research and compatibility history.

They are not the active product roadmap. No recursive readiness or assurance phase should be added without a concrete product requirement.

## Decision after verifiable evidence

After reviewing the real packet, choose exactly one primary action:

1. revise the current refrigerator route;
2. repeat the current-route pilot;
3. hold the current route;
4. advance to a separate next-product planning review.

The fourth action starts planning only. It does not authorize a second route, public release, or an effectiveness claim.

Until real cohort evidence exists, the selected action remains **run and complete the learner pilot**.