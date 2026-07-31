---
title: "Principia current product state"
slug: principia-current-product-state
domain: product
status: draft
artifact_revision: 2
release_status: alpha
prerequisites: []
connections: [product-alpha-refrigerator, product-alpha-learner-pilot]
last_reviewed: 2026-08-01
content_license: CC-BY-4.0
---

# Principia current product state

**Last updated:** 2026-08-01  
**Active milestone:** Product Alpha 0.1 — evidence integrity recovery  
**Active repository:** `Rhodan-lab/principle-to-system`  
**Supporting repository:** `Rhodan-lab/Atlas`  
**Decision authority:** verifiable real learner evidence, not phase-count growth or issue-closure status

## Current decision

Principia remains the learner-facing product. Atlas remains a read-only trust and provenance substrate.

The current primary decision is:

> Keep the refrigerator route stable and repeat or complete the documented 5–8 learner pilot before adding another route, expanding Atlas, or building SaaS and production infrastructure.

The next milestone is **not Phase 51**. It is completion of the Product Alpha evidence chain with real anonymous learner records and a de-identified aggregate report.

## Completed product foundation

Product Alpha 0.1 includes:

- a five-step refrigerator journey: Observe → Map → Model → Diagnose → Redesign;
- canonical content extraction from existing Principia artifacts;
- a dependency-free thermal model and diagnosis challenge;
- pinned exact-revision Atlas references with separate status authority;
- a local anonymous facilitator recorder;
- a deterministic JSONL pilot summarizer;
- a loopback-only one-command pilot launcher;
- focused CI that runs Product Alpha checks without launching the full historical phase chain.

Relevant merged work:

| Change | Result |
|---|---|
| PR #93 | First learner-facing Product Alpha route |
| PR #95 | Anonymous pilot protocol, rubric, records, and summarizer |
| PR #96 | Product Alpha CI ownership and legacy fan-out reduction |
| PR #98 | Local facilitator recorder and deterministic packaging |
| PR #99 | Product Alpha established as the current program state |
| PR #100 | Loopback-only one-command pilot launcher |

## Evidence integrity finding

The software and pilot instrumentation are validated. The repository still does not contain a de-identified aggregate cohort report with reportable completion, duration, rubric, confusion, and continuation metrics.

Issue #101 was closed while its aggregate-report, cohort-metrics, and product-decision checklist items remained incomplete. Closure status is not learner evidence. The evidence gate must therefore remain open.

The current evidence review is recorded in:

- `reports/product-alpha-0-1-pilot-summary.md`

That report intentionally marks cohort values as **not reportable** rather than inventing, estimating, or simulating learner outcomes.

## What the project may claim

The project may claim:

- the route builds deterministically;
- the local learner interface and facilitator recorder are testable;
- the pilot record contract is machine-validated;
- the cohort summarizer is available;
- the pilot launcher binds only to `127.0.0.1`;
- Product Alpha is technically ready for a small formative pilot.

## What the project may not claim

The project may not yet claim:

- verified completion of a 5–8 learner cohort;
- demonstrated learning effectiveness;
- validated retention or transfer;
- evidence that the refrigerator route meets progression thresholds;
- justification for a second route;
- public-release readiness;
- product-market fit;
- SaaS readiness;
- production security, availability, or compliance.

## Active evidence gate

Run `software/product_alpha/PILOT.md` with 5–8 learners who did not author or review the route.

Start the local pilot with:

```bash
python3 software/product_alpha/run_pilot.py --open
```

For each anonymous session, record:

- ordered route completion;
- duration;
- mechanism explanation score;
- model reasoning score;
- failure diagnosis score;
- evidence-boundary score;
- redesign trade-off score;
- recurring confusion tags;
- voluntary continuation;
- anonymous product-focused facilitator notes.

Keep raw records private and local. Do not commit names, contact information, school details, raw JSONL records, or identifiable free-text notes.

Then summarize the cohort with:

```bash
python3 software/product_alpha/evaluation/summarize.py \
  --input path/to/anonymous-sessions.jsonl \
  --format markdown
```

Use the output to replace the **not reportable** entries in `reports/product-alpha-0-1-pilot-summary.md`.

## Revision triggers

Revise Product Alpha before adding another route when any of these conditions appear:

- the same confusion tag occurs in at least two sessions;
- fewer than half of started sessions reach redesign;
- average mechanism, diagnosis, or evidence-boundary score is below 1.25;
- learners manipulate the model without predicting direction;
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

Pilot records remain local, anonymous, and facilitator-controlled.

## Atlas operating state

Atlas remains frozen except for bounded defects required by Principia’s exact-revision evidence interface.

Do not expand Atlas retrieval, embeddings, generalized search, or production synchronization unless learner evidence creates a concrete Principia requirement.

## Historical governance status

Phases 0–50 remain preserved in `PROJECT_STATE.md`, `release/`, `reports/`, validators, and tests as research and compatibility history.

They are not the active product roadmap. No recursive readiness or assurance phase should be added without a product requirement that cannot be served by the current generic validation architecture.

## Decision after verifiable evidence

After reviewing the real aggregate learner evidence, choose exactly one primary action:

1. revise the refrigerator route;
2. repeat the pilot after a targeted revision;
3. add a second route only when the first route meets the documented evidence threshold;
4. stop or narrow the product hypothesis when learners do not gain or continue.

Until that evidence exists, the selected action is **repeat and complete the learner pilot**. Production infrastructure, accounts, deployment, monetization, and additional routes remain deferred.
