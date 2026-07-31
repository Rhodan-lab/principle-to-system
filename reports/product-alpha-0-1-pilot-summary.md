---
title: "Product Alpha 0.1 pilot evidence integrity report"
slug: product-alpha-0-1-pilot-evidence-integrity
domain: product
status: draft
artifact_revision: 1
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
**Primary decision:** repeat and complete the real learner pilot before adding another route

## Executive decision

The repository does not currently contain the de-identified aggregate cohort report required to support a learning-effectiveness decision. It also does not contain reportable cohort metrics or a documented evidence-based product decision derived from those metrics.

No learner result is invented in this report. Missing values are recorded as **not reportable**, not estimated, simulated, or reconstructed.

The product decision is therefore:

> Keep the existing refrigerator route stable, run or repeat the documented 5–8 learner pilot with verifiable anonymous records, produce an aggregate report, and only then decide whether to revise the route or add a second route.

## Evidence reviewed

The following product infrastructure is present and machine-testable:

- the five-step refrigerator learner route;
- deterministic static packaging;
- an anonymous local facilitator recorder;
- a committed evaluation rubric and session template;
- a deterministic JSONL cohort summarizer;
- a loopback-only local pilot launcher;
- focused Product Alpha CI.

The following evidence required for a completed pilot decision is not present in the repository:

- a de-identified aggregate cohort report;
- reportable completion and duration statistics;
- aggregate rubric scores;
- aggregate confusion-tag counts;
- voluntary-continuation results;
- a documented product decision tied to measured cohort evidence.

Private raw session records should not be committed. Their absence from the repository is expected. However, an aggregate report derived from those records is required before the pilot can be treated as an evidence-complete milestone.

## Cohort metrics

| Measure | Result | Evidence status |
|---|---:|---|
| Learners recruited | Not reportable | No aggregate cohort report is available |
| Sessions started | Not reportable | No aggregate cohort report is available |
| Sessions completed | Not reportable | No aggregate cohort report is available |
| Reached redesign | Not reportable | No aggregate cohort report is available |
| Mean or median duration | Not reportable | No aggregate cohort report is available |
| Mechanism explanation score | Not reportable | No aggregate cohort report is available |
| Model reasoning score | Not reportable | No aggregate cohort report is available |
| Failure diagnosis score | Not reportable | No aggregate cohort report is available |
| Evidence-boundary score | Not reportable | No aggregate cohort report is available |
| Redesign trade-off score | Not reportable | No aggregate cohort report is available |
| Repeated confusion tags | Not reportable | No aggregate cohort report is available |
| Voluntary continuation | Not reportable | No aggregate cohort report is available |

## What may be claimed

The project may claim that Product Alpha 0.1 is technically pilot-ready:

- the route can be built deterministically;
- the local learner and facilitator interfaces are available;
- the anonymous record contract is machine-validated;
- the cohort summarizer exists;
- the pilot can be launched locally without accounts, analytics, cloud storage, or a public network binding.

## What may not be claimed

The project may not yet claim:

- that 5–8 verified learner sessions produced a specific result;
- demonstrated learning effectiveness;
- validated comprehension, transfer, retention, or engagement;
- evidence that the refrigerator route meets its progression thresholds;
- evidence that a second route should be built;
- product-market fit, SaaS readiness, or production readiness.

## Integrity finding

Issue #101 was closed while its aggregate-report, cohort-metrics, and product-decision checklist items remained incomplete. Closure status alone is not learner evidence.

This mismatch is a process defect, not evidence of product failure. It is corrected by reopening the evidence gate and requiring an aggregate report before completion.

## Required repeatable pilot

Run the same Product Alpha build with 5–8 learners who did not author or review the route.

For each session:

1. use an anonymous label such as `anonymous-001`;
2. follow `software/product_alpha/PILOT.md` without teaching answers in advance;
3. export one validated JSONL record;
4. review free-text notes for accidental identifying information;
5. keep raw records private and local;
6. do not commit names, school details, contact information, or raw session records.

After the cohort, combine the local records and run:

```bash
python3 software/product_alpha/evaluation/summarize.py \
  --input path/to/anonymous-sessions.jsonl \
  --format markdown
```

Replace the **not reportable** entries in this report with aggregate values generated from real records. Do not manually manufacture a complete-looking dataset.

## Decision rule after real evidence

Choose one primary action:

1. **Revise the refrigerator route** when repeated confusion or weak rubric performance crosses a documented threshold.
2. **Repeat the pilot after a targeted revision** when the evidence identifies a bounded route problem.
3. **Add a second route** only when completion, comprehension, evidence-boundary reasoning, and voluntary continuation meet the documented thresholds.
4. **Narrow or stop the product hypothesis** when learners neither understand nor choose to continue.

## Current product decision

**Decision:** repeat and complete the learner pilot before feature expansion.

**Rationale:** the software and evaluation infrastructure are ready, but the repository does not contain the aggregate learner evidence required to justify route revision, route expansion, Atlas expansion, SaaS infrastructure, or production deployment.

## Completion criteria

This evidence gate is complete only when:

- 5–8 real learner sessions have been conducted;
- raw records remain private, local, and de-identified;
- this report contains aggregate cohort metrics rather than placeholders;
- recurring confusion and threshold results are documented;
- `PRODUCT_STATE.md` records exactly one evidence-based product decision;
- Issue #101 is closed only after the report and decision are merged.
