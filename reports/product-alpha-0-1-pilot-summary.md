---
title: "Product Alpha 0.1 pilot evidence integrity report"
slug: product-alpha-0-1-pilot-evidence-integrity
domain: product
status: draft
artifact_revision: 4
release_status: alpha
prerequisites: [product-alpha-refrigerator]
connections: [product-alpha-learner-pilot]
last_reviewed: 2026-08-02
content_license: CC-BY-4.0
---

# Product Alpha 0.1 pilot evidence integrity report

**Review date:** 2026-08-02  
**Product:** Principia Product Alpha 0.1  
**Route:** Refrigerator — Observe → Map → Model → Diagnose → Redesign  
**Evidence status:** incomplete and not independently verifiable from the repository  
**Primary decision:** run and complete the real learner pilot before another route

## Executive decision

The repository does not currently contain a reviewed product change derived from 5–8 real learner sessions. It therefore cannot support a learning-effectiveness, progression, second-route, public-release, SaaS, or production decision.

No learner result is invented here. Missing values remain **not reportable**, not estimated, simulated, or reconstructed.

The product decision is:

> Keep the refrigerator route bounded, run the prepared build-bound pilot, complete the verified private evidence chain, record one explicit human decision, and prepare a de-identified handoff for a separate human-reviewed repository change.

GitHub issue state is not part of this evidence workflow.

## Evidence reviewed

The following infrastructure is present and machine-testable:

- the five-step refrigerator learner route;
- deterministic static packaging and build identity;
- a loopback-only smoke gate and build-bound workspace launcher;
- in-tab learner reasoning state without browser persistence;
- a build-bound anonymous facilitator recorder that locks after capture;
- a browser-local Pilot Lab with explicit additive file loading;
- a private repository-external cohort workspace;
- repeatable no-write intake preflight;
- immutable cohort assembly with raw-source, source-set, and combined-evidence hashes;
- fail-closed review verification against unchanged incoming exports;
- an immutable de-identified review packet;
- a separate immutable human-decision JSON and Markdown pair;
- a decision receipt that seals both decision files and earlier evidence bindings;
- no-write final decision verification;
- a read-only workspace stage and next-action reporter;
- an allowlisted repository-external handoff candidate;
- handoff verification against the unchanged decision and private evidence chain;
- Product Alpha Python, browser-runtime, Node.js, and workflow-scope CI.

The following evidence required for a completed product decision is not present in the repository:

- verified aggregate results from 5–8 real learners;
- reportable completion and duration statistics;
- aggregate rubric scores;
- aggregate confusion-tag counts;
- voluntary-continuation results;
- a human decision tied to those measured results;
- a verified de-identified handoff derived from that real decision;
- a separately reviewed repository change based on that handoff.

Private raw records, intake files, review packets, decision records, receipts, and handoff candidates should not be committed. Their absence is expected. The missing repository evidence is a separately reviewed product change derived from a verified private cohort and a verified de-identified handoff.

## Cohort metrics

| Measure | Result | Evidence status |
|---|---:|---|
| Learners recruited | Not reportable | No verified real cohort is available |
| Sessions started | Not reportable | No verified real cohort is available |
| Sessions completed | Not reportable | No verified real cohort is available |
| Reached redesign | Not reportable | No verified real cohort is available |
| Mean or median duration | Not reportable | No verified real cohort is available |
| Mechanism explanation score | Not reportable | No verified real cohort is available |
| Model reasoning score | Not reportable | No verified real cohort is available |
| Failure diagnosis score | Not reportable | No verified real cohort is available |
| Evidence-boundary score | Not reportable | No verified real cohort is available |
| Redesign trade-off score | Not reportable | No verified real cohort is available |
| Repeated confusion tags | Not reportable | No verified real cohort is available |
| Voluntary continuation | Not reportable | No verified real cohort is available |

## What may be claimed

The project may claim that Product Alpha 0.1 is technically pilot-ready:

- the route builds deterministically;
- the learner, recorder, and Pilot Lab interfaces are available locally;
- preparation proves the exact loopback build before workspace creation;
- the workspace launcher fails closed on build drift;
- session records are bound to one exact build;
- duplicate, mixed-build, malformed, personal-data-bearing, and repeated records are rejected;
- current exports can be validated repeatedly without sealing the cohort;
- intake, review, decision, and receipt artifacts are hash-bound and non-overwriting;
- final decision verification rechecks the complete private evidence chain;
- a de-identified handoff can be checked, prepared, and verified outside the repository;
- no accounts, analytics, cloud storage, or public network binding are required.

## What may not be claimed

The project may not yet claim:

- that 5–8 verified learner sessions produced a specific result;
- demonstrated learning effectiveness;
- validated comprehension, transfer, retention, or engagement;
- evidence that the refrigerator route meets progression thresholds;
- authorization for another route;
- public-release, SaaS, or production readiness;
- product-market fit.

## Integrity finding

The software evidence and handoff infrastructure are complete, but the human evidence chain has not been executed with a reportable real cohort.

This is an evidence gap, not a software completion signal and not evidence of product failure. The gate remains human review of real anonymous sessions.

## Required repeatable pilot

Prepare one repository-external workspace:

```bash
python3 software/product_alpha/prepare_pilot.py \
  --workspace /private/path/refrigerator-cohort
```

Do not begin participant sessions unless preparation reports `pilot-preparation-passed`.

Run every session through the exact prepared build:

```bash
python3 software/product_alpha/launch_workspace.py \
  --workspace /private/path/refrigerator-cohort \
  --open
```

For each session:

1. follow `software/product_alpha/PILOT.md` without teaching answers in advance;
2. use the build-bound recorder;
3. export exactly one locked anonymous JSONL record;
4. review free text for accidental identifying information;
5. place the reviewed export in `incoming-sessions/`;
6. keep the workspace private and local;
7. do not commit names, school details, contact information, or raw session records.

At any point, inspect the verified stage and next action without writing:

```bash
python3 software/product_alpha/evaluation/workspace_status.py \
  --workspace /private/path/refrigerator-cohort
```

During collection, validate current exports without sealing the cohort:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py check \
  --workspace /private/path/refrigerator-cohort
```

After deliberate collection closure and at least five valid sessions, assemble the immutable intake:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py \
  --workspace /private/path/refrigerator-cohort
```

An intentionally stopped incomplete cohort requires `--allow-incomplete`. That records early closure but keeps the evidence incomplete and planning-review ineligible.

Verify and create the private review packet:

```bash
python3 software/product_alpha/evaluation/review_workspace.py check \
  --workspace /private/path/refrigerator-cohort

python3 software/product_alpha/evaluation/review_workspace.py \
  --workspace /private/path/refrigerator-cohort
```

Verify readiness, review the aggregate with private facilitator notes, and record one human action:

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

Verify the decision artifact trio and every earlier binding without writing:

```bash
python3 software/product_alpha/evaluation/record_decision.py verify \
  --workspace /private/path/refrigerator-cohort
```

Prepare and verify the de-identified repository handoff:

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

The handoff excludes raw sessions, session identifiers, facilitator notes, custom confusion text, reviewer identity, review date, private rationale, checkpoint text, and local workspace paths. It remains private and outside the repository.

Do not manufacture a complete-looking dataset. Do not commit the private workspace or any of its evidence or handoff files.

## Decision rule after real evidence

Choose one primary action:

1. **Revise the current route** when repeated confusion or weak rubric performance crosses a documented threshold.
2. **Repeat the current-route pilot** after a bounded revision or when the cohort is incomplete.
3. **Hold the current route** when the evidence does not justify further product work.
4. **Advance to a separate next-product planning review** only when the evidence supports considering another route.

Planning review is not route authorization. Handoff verification is not repository-change authorization.

## Current product decision

**Decision:** run and complete the learner pilot before feature expansion.

**Rationale:** the software and evaluation infrastructure are ready, but no verified aggregate learner evidence exists to justify route revision, another route, Atlas expansion, SaaS infrastructure, or production deployment.

## Completion criteria

This evidence gate is complete only when:

- 5–8 real learner sessions have been conducted on one exact prepared Pilot build;
- raw records remain private, local, anonymous, and facilitator-controlled;
- intake preflight and immutable assembly succeed;
- the workspace-bound review chain verifies unchanged raw and combined evidence;
- a private de-identified review packet is generated;
- recurring confusion and threshold results are reviewed;
- exactly one human decision is recorded and receipt-verified;
- an allowlisted de-identified handoff is prepared and verified;
- `PRODUCT_STATE.md` records the resulting evidence-based product decision;
- any repository change based on that handoff is separately reviewed and merged.
