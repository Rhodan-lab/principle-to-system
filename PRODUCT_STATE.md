---
title: "Principia current product state"
slug: principia-current-product-state
domain: product
status: draft
artifact_revision: 1
release_status: alpha
prerequisites: []
connections: [product-alpha-refrigerator, product-alpha-learner-pilot]
last_reviewed: 2026-07-31
content_license: CC-BY-4.0
---

# Principia current product state

**Last updated:** 2026-07-31  
**Active milestone:** Product Alpha 0.1 — pilot-ready  
**Active repository:** `Rhodan-lab/principle-to-system`  
**Supporting repository:** `Rhodan-lab/Atlas`  
**Decision authority:** real learner evidence, not phase-count growth

## Current decision

Principia is the learner-facing product. Atlas remains a read-only trust and provenance substrate.

The next milestone is **not Phase 51**. The next milestone is execution of the documented refrigerator learner pilot and evidence-based revision of Product Alpha 0.1.

## Completed product foundation

Product Alpha 0.1 now includes:

- a five-step refrigerator journey: Observe → Map → Model → Diagnose → Redesign;
- canonical content extraction from existing Principia artifacts;
- a dependency-free thermal model and diagnosis challenge;
- pinned exact-revision Atlas references with separate status authority;
- a local anonymous facilitator recorder;
- a deterministic JSONL pilot summarizer;
- focused CI that runs Product Alpha checks without launching the full historical phase chain.

Relevant merged work:

| Change | Result |
|---|---|
| PR #93 | First learner-facing Product Alpha route |
| PR #95 | Anonymous pilot protocol, rubric, records, and summarizer |
| PR #96 | Product Alpha CI ownership and legacy fan-out reduction |
| PR #98 | Local facilitator recorder and deterministic packaging |

## Evidence state

The software and pilot instrumentation are validated. **No real learner cohort result is recorded in this repository yet.**

Therefore the project may claim:

- the route builds deterministically;
- the local interface and recorder are testable;
- the pilot record contract is machine-validated;
- Product Alpha is ready for a small formative pilot.

The project may not yet claim:

- demonstrated learning effectiveness;
- validated retention or transfer at population scale;
- public-release readiness;
- product-market fit;
- SaaS readiness;
- production security, availability, or compliance.

## Next evidence gate

Run the protocol in `software/product_alpha/PILOT.md` with 5–8 learners who did not author the route.

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

Then summarize the cohort with:

```bash
python3 software/product_alpha/evaluation/summarize.py \
  --input path/to/anonymous-sessions.jsonl \
  --format markdown
```

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

They are not the active product roadmap. No new recursive readiness or assurance phase should be added without a product requirement that cannot be served by the current generic validation architecture.

## Decision after the pilot

After reviewing the learner evidence, choose exactly one primary action:

1. revise the refrigerator route;
2. repeat the pilot after a targeted revision;
3. add a second route only when the first route meets the documented evidence threshold;
4. stop or narrow the product hypothesis when learners do not gain or continue.

Production infrastructure, accounts, deployment, and monetization remain later decisions.
