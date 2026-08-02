---
title: "Principia current product state"
slug: principia-current-product-state
domain: product
status: draft
artifact_revision: 5
release_status: alpha
prerequisites: []
connections: [product-alpha-refrigerator, product-alpha-learner-pilot]
last_reviewed: 2026-08-02
content_license: CC-BY-4.0
---

# Principia current product state

**Last updated:** 2026-08-02  
**Active milestone:** Product Alpha 0.1 — real cohort execution and human review  
**Active repository:** `Rhodan-lab/principle-to-system`  
**Supporting repository:** `Rhodan-lab/Atlas`  
**Decision authority:** verified real learner evidence plus an explicit human decision, not phase counts, issue state, or tool-generated readiness

## Current decision

Principia remains the learner-facing product. Atlas remains a read-only trust and provenance substrate.

The current primary decision is:

> Keep the refrigerator route stable and run the documented 5–8 learner pilot before authorizing another route, public release, SaaS infrastructure, or production deployment.

The active work is direct repository development and private evidence review. GitHub issues are not part of the current execution workflow.

## Completed Product Alpha foundation

Product Alpha 0.1 now includes:

- a five-step refrigerator journey: Observe → Map → Model → Diagnose → Redesign;
- canonical content extraction from existing Principia artifacts;
- a dependency-free thermal model and diagnosis challenge;
- pinned exact-revision Atlas references with separate status authority;
- in-tab learner reasoning state without browser persistence;
- a local anonymous facilitator recorder that locks after capture;
- a browser-local Pilot Lab with additive batches and duplicate or mixed-build rejection;
- deterministic packaging and a 64-character Pilot build identity;
- a loopback-only preparation smoke gate and build-bound long-running launcher;
- a private repository-external cohort workspace;
- repeatable non-writing intake preflight;
- fail-closed immutable cohort assembly with explicit incomplete-cohort authorization;
- post-intake raw-source, manifest, and combined-evidence verification;
- an immutable de-identified review packet;
- a separate immutable human-decision record and decision receipt;
- no-write final decision verification;
- a read-only workspace stage and next-action reporter;
- a repository-external, allowlisted, de-identified handoff candidate;
- handoff verification against the unchanged private decision and evidence chain;
- focused Product Alpha Python, browser-runtime, Node.js, and workflow-scope CI.

The current operational chain was completed through these merged changes:

| Change | Result |
|---|---|
| PR #118 | Bind workspace creation to deterministic smoke validation |
| PR #119 | Deterministic private workspace intake |
| PR #120 | Bind long-running launch to the prepared workspace |
| PR #121 | Bind review to unchanged intake and raw sources |
| PR #122 | Record an immutable human product decision |
| PR #123 | Preserve learner reasoning state in the current tab |
| PR #124 | Make Pilot Lab multi-file loading explicit and additive |
| PR #125 | Lock facilitator records after successful capture |
| PR #126 | Add non-writing intake preflight and safe cohort closure |
| PR #127 | Seal and verify decision artifacts with a receipt |
| PR #128 | Report the verified workspace stage and next valid action |
| PR #129 | Synchronize canonical product-state and pilot evidence authority |
| PR #130 | Prepare and verify a de-identified repository handoff candidate |

## Evidence integrity finding

The software and pilot instrumentation are validated. The repository still does not contain a reviewed product change derived from 5–8 real learner sessions.

That absence is recorded honestly in:

- `reports/product-alpha-0-1-pilot-summary.md`

Private raw records, intake files, review packets, decision records, receipts, and handoff candidates must not be committed. Missing cohort values remain **not reportable** rather than invented, estimated, simulated, or reconstructed.

## What the project may claim

The project may claim:

- deterministic Product Alpha packaging;
- a working local learner route, recorder, and Pilot Lab;
- exact workspace/build binding before real sessions;
- build-bound anonymous session records;
- duplicate, mixed-build, personal-data, malformed-record, and repeated-file rejection;
- repeatable no-write intake validation;
- immutable, hash-bound intake, review, and human-decision artifacts;
- final no-write decision verification;
- a de-identified repository-external handoff candidate bound to the verified decision;
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

## Supported private evidence workflow

Create a new repository-external workspace only after deterministic smoke verification succeeds:

```bash
python3 software/product_alpha/prepare_pilot.py \
  --workspace /private/path/refrigerator-cohort
```

Run every participant session through the exact prepared build:

```bash
python3 software/product_alpha/launch_workspace.py \
  --workspace /private/path/refrigerator-cohort \
  --open
```

At any time, inspect the strongest verified stage and next valid action without writing:

```bash
python3 software/product_alpha/evaluation/workspace_status.py \
  --workspace /private/path/refrigerator-cohort
```

During collection, validate all current exports without sealing the cohort:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py check \
  --workspace /private/path/refrigerator-cohort
```

After collection is deliberately closed and at least five valid sessions are present, create the immutable intake:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py \
  --workspace /private/path/refrigerator-cohort
```

An intentionally stopped incomplete cohort requires the explicit `--allow-incomplete` flag. It records early closure but does not make the evidence complete or planning-review eligible.

Verify and create the private review packet:

```bash
python3 software/product_alpha/evaluation/review_workspace.py check \
  --workspace /private/path/refrigerator-cohort

python3 software/product_alpha/evaluation/review_workspace.py \
  --workspace /private/path/refrigerator-cohort
```

Verify decision readiness, then record exactly one human action:

```bash
python3 software/product_alpha/evaluation/record_decision.py check \
  --workspace /private/path/refrigerator-cohort

python3 software/product_alpha/evaluation/record_decision.py \
  --workspace /private/path/refrigerator-cohort \
  --action <allowed-primary-action> \
  --reviewer "<role-or-initials>" \
  --review-date YYYY-MM-DD \
  --rationale "<de-identified rationale>" \
  --next-checkpoint "<next checkpoint>"
```

Verify the completed decision JSON, Markdown, receipt, review packet, intake, combined cohort, and raw-source bindings without writing:

```bash
python3 software/product_alpha/evaluation/record_decision.py verify \
  --workspace /private/path/refrigerator-cohort
```

Prepare a private, de-identified input for a later human-reviewed repository change:

```bash
python3 software/product_alpha/evaluation/prepare_handoff.py check \
  --workspace /private/path/refrigerator-cohort \
  --output-prefix /private/path/refrigerator-cohort/handoff/refrigerator-product-change

python3 software/product_alpha/evaluation/prepare_handoff.py \
  --workspace /private/path/refrigerator-cohort \
  --output-prefix /private/path/refrigerator-cohort/handoff/refrigerator-product-change

python3 software/product_alpha/evaluation/prepare_handoff.py verify \
  --workspace /private/path/refrigerator-cohort \
  --output-prefix /private/path/refrigerator-cohort/handoff/refrigerator-product-change
```

The handoff contains only an allowlisted de-identified aggregate, revision signals, verified human action, and evidence hashes. It excludes raw sessions, session identifiers, facilitator notes, custom confusion text, reviewer identity, review date, private rationale, checkpoint text, and local workspace paths.

Keep the entire workspace and handoff private and outside the repository. A repository change remains a separate human-reviewed pull request. None of these commands automatically mutates the repository.

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
- no browser persistence for learner, recorder, or Pilot Lab state;
- no automatic repository mutation;
- no automated publication;
- no production deployment contract.

Pilot records and all derived private artifacts remain local, anonymous where applicable, private, and facilitator-controlled.

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

The fourth action starts planning only. It does not authorize a second route, public release, or an effectiveness claim. A verified handoff candidate does not change that authority boundary.

Until real cohort evidence exists, the selected action remains **run and complete the learner pilot**.
