---
title: "Product Alpha 0.1 pilot evidence integrity report"
slug: product-alpha-0-1-pilot-evidence-integrity
domain: product
status: draft
artifact_revision: 2
release_status: alpha
prerequisites: [product-alpha-refrigerator]
connections: [product-alpha-learner-pilot]
last_reviewed: 2026-08-01
content_license: CC-BY-4.0
---

# Product Alpha 0.1 pilot evidence integrity report

**Review date:** 2026-08-01  
**Product:** Principia Product Alpha 0.1  
**Route:** Refrigerator — Observe → Map → Model → Diagnose → Redesign  
**Evidence status:** incomplete and not independently verifiable from the repository  
**Primary decision:** run and complete the real learner pilot before another route

## Executive decision

The repository does not currently contain a de-identified aggregate cohort report derived from 5–8 real learner sessions. It therefore cannot support a learning-effectiveness, progression, or second-route decision.

No learner result is invented here. Missing values remain **not reportable**, not estimated, simulated, or reconstructed.

The product decision is:

> Keep the current refrigerator route bounded, run the build-bound learner pilot, create the verified private review packet, and make one explicit human decision from real evidence.

GitHub issue state is not part of this evidence workflow.

## Evidence reviewed

The following infrastructure is present and machine-testable:

- the five-step refrigerator learner route;
- deterministic static packaging;
- a loopback-only launcher and HTTP smoke gate;
- a deterministic 64-character Pilot build ID;
- a build-bound anonymous facilitator recorder;
- a Pilot Lab that rejects duplicates and mixed builds;
- expected-build cohort verification;
- deterministic JSON and Markdown summaries;
- a private hash-bound human-review packet;
- Product Alpha CI and executable learner-runtime tests.

The following evidence required for a completed product decision is not present in the repository:

- verified aggregate results from 5–8 real learners;
- reportable completion and duration statistics;
- aggregate rubric scores;
- aggregate confusion-tag counts;
- voluntary-continuation results;
- a human decision tied to those measured results.

Private raw records should not be committed. Their absence is expected. The missing item is a separately reviewed, de-identified product decision derived from a verified private cohort.

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
- session records are bound to one exact build;
- duplicate and mixed-build records are rejected;
- the complete loopback product path passes a smoke check;
- verified private cohort and review-packet tools are available;
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

The software evidence chain is complete, but the human evidence chain has not been executed with a reportable real cohort.

This is an evidence gap, not a software completion signal and not evidence of product failure. The gate remains human review of real anonymous sessions.

## Required repeatable pilot

Before participant sessions:

```bash
python3 software/product_alpha/run_pilot.py smoke
python3 software/product_alpha/run_pilot.py --open
```

Record the printed Pilot build ID and use that exact build for every included session.

For each session:

1. use an anonymous label such as `anonymous-001`;
2. follow `software/product_alpha/PILOT.md` without teaching answers in advance;
3. export one validated build-bound JSONL record;
4. review free text for accidental identifying information;
5. keep raw records private and local;
6. do not commit names, school details, contact information, or raw session records.

After the cohort, verify the private file:

```bash
python3 software/product_alpha/evaluation/verify_cohort.py \
  --input path/to/anonymous-sessions.jsonl \
  --expect-build-id <64-character-pilot-build-id> \
  --format markdown
```

Then create the private review packet outside the repository:

```bash
python3 software/product_alpha/evaluation/prepare_review.py \
  --input path/to/anonymous-sessions.jsonl \
  --expect-build-id <64-character-pilot-build-id> \
  --output-prefix /private/cohort-folder/refrigerator-review
```

Do not manufacture a complete-looking dataset. Do not commit the raw JSONL file or private packet.

## Decision rule after real evidence

Choose one primary action:

1. **Revise the current route** when repeated confusion or weak rubric performance crosses a documented threshold.
2. **Repeat the current-route pilot** after a bounded revision or when the cohort is incomplete.
3. **Hold the current route** when the evidence does not justify further product work.
4. **Advance to a separate next-product planning review** only when the evidence supports considering another route.

Planning review is not route authorization.

## Current product decision

**Decision:** run and complete the learner pilot before feature expansion.

**Rationale:** the software and evaluation infrastructure are ready, but no verified aggregate learner evidence exists to justify route revision, another route, Atlas expansion, SaaS infrastructure, or production deployment.

## Completion criteria

This evidence gate is complete only when:

- 5–8 real learner sessions have been conducted on one exact Pilot build;
- raw records remain private, local, anonymous, and facilitator-controlled;
- expected-build cohort verification succeeds;
- a private de-identified review packet is generated;
- recurring confusion and threshold results are reviewed;
- `PRODUCT_STATE.md` records exactly one human evidence-based product decision;
- any repository change based on that decision is separately reviewed and merged.