# Repository Audit

This document records repository-wide findings that affect scientific credibility, editorial consistency, and release readiness. It is intentionally separate from `PROJECT_STATE.md`: the project-state file says what to do next, while this file explains why the work is necessary and how to judge it.

## Audit scope

The initial audit examined the repository contract and representative content across:

- the README, index, content guide, source policy, contribution guide, and project state;
- the validator implementation;
- foundation, science, and technology module files;
- crosscutting concepts, pathways, and dependency maps;
- source-ledger structure and source quality;
- commit history related to completion claims and slug repair.

This began as a repository-level audit rather than a claim that every statement had independent external certification. Phases 6–12 progressively added focused scientific review, synthesis reconciliation, applied-material review, compatibility governance, and release-candidate validation.

## Central finding

The repository has a strong educational architecture and a complete reviewed material foundation. Its principal historical weakness was that structural completion was treated as scientific and editorial completion.

The architecture is coherent:

```text
observation
→ scientific concept
→ mechanism
→ mathematical model
→ engineered component
→ technological system
→ limitation and trade-off
```

The corrective strategy preserved that architecture while making status, evidence, assumptions, model limits, safety, lifecycle, and release authority explicit.

## Severity levels

- **Blocking** — prevents trustworthy validation or makes repository status materially misleading.
- **Major** — can mislead learners, break navigation, or violate the documented content/source policy.
- **Minor** — reduces consistency, clarity, or maintainability without making the content unusable.

## Blocking findings

### A-001 — Status claims do not match learner-file status

`INDEX.md` and the former project state labelled every module Complete while sampled learner files retained `status: draft`.

**Required resolution:** module status must be computed from the three learner-facing files and may advance only under the definitions in `PROJECT_STATE.md`.

**Resolution:** Modules 01–20 are Reviewed after focused Phase 6–9 review; no module is Complete before explicit release authority.

### A-002 — Malformed slug values

A previous duplicate-slug repair produced values such as:

```yaml
slug: "11-waves-signals"-technology
```

This was not a valid scalar under the intended frontmatter contract.

**Resolution:** learner-file slugs were normalized to valid unique lowercase kebab-case identifiers.

### A-003 — Source-ledger rows were not consistently machine-readable

Some lines contained several sources concatenated into one Markdown table row. A row-count check could not establish source coverage.

**Resolution:** the core ledger uses exactly one source per eight-column row and contains 143 records. The applied-material ledger uses the same shape and contains 28 records.

### A-004 — Former validator could report false success

The former validator used a permissive frontmatter parser, searched for section keywords anywhere in a file rather than validating headings, did not validate canonical dependency identifiers, and counted ledger lines rather than valid source rows.

**Resolution:** focused standard-library validators now check metadata, scientific-review continuity, canonical graphs, applied experiences, compatibility contracts, release state, and read-only workflow governance.

## Major findings

### A-005 — Non-canonical connection identifiers

Several files used identifiers that did not correspond to repository modules or came from an earlier outline.

**Resolution:** canonical module identifiers and the Phase 10 graph govern prerequisites and synthesis dependencies.

### A-006 — Inconsistent `domain` semantics

Some files used `domain` to describe file role rather than the module’s subject grouping.

**Resolution:** module metadata was normalized, while applied materials use `domain: experience` plus `experience_type`.

### A-007 — Source quality did not consistently meet policy

Some modules relied substantially on weak summaries.

**Resolution:** focused reviews added and normalized institutional, standards-based, consensus, textbook, and primary or review sources. Release review must still inspect attribution and source applicability rather than trusting row count alone.

### A-008 — Scientific explanations required expert tightening

Representative definitions were written outside their valid scope, including simplified temperature, entropy, energy, catalysis, genetics, ecology, climate, electronics, control, and AI claims.

**Resolution:** Phases 6–10 added assumptions, sign conventions, units, counterexamples, causal distinctions, and model limits across Modules 01–20 and the synthesis layer.

### A-009 — Repository maps could disagree with file metadata

Dependency maps and file metadata diverged.

**Resolution:** `synthesis/phase-10-canonical-graph.json` defines the direct prerequisite graph and relationship semantics.

### A-010 — Pathways were stronger than some source modules

Pathways sometimes explained abstraction and trade-offs more clearly than their source modules.

**Resolution:** modules were reviewed against pathway quality, then pathways were reconciled back against the reviewed module foundation.

## Minor findings

### A-011 — Terminology and capitalization vary

Module titles, headings, identifiers, and lifecycle language historically varied.

**Current resolution:** metadata and synthesis terminology are normalized; `release/phase-12-terminology.json` adds an RC-level semantic contract. Human editorial review remains required.

### A-012 — Some cross-links are descriptive rather than navigable

Connections were sometimes named without navigable links.

**Current resolution:** synthesis and applied routes have navigable indexes and release validation checks local Markdown links. Human usability review remains required.

### A-013 — Completion history obscures review history

Large batches were once committed as complete without a documented scientific-review trail.

**Resolution:** phase-specific reports, exact status policies, deterministic validators, source transitions, compatibility fixtures, and read-only CI preserve review history.

## Repair sequence

### Phase 1 — Contract and metadata

Completed through Phases 2–5:

1. hardened validation;
2. made status claims honest;
3. repaired frontmatter and unique slugs;
4. normalized domains, prerequisites, and connections;
5. normalized the source ledger;
6. resolved structural validator errors.

### Phase 2 — Foundations review

Completed in repository Phase 6 for Modules 01–05.

### Phase 3 — Science review

Completed in repository Phases 7–8 for Modules 06–16.

### Phase 4 — Technology review

Completed in repository Phase 9 for Modules 17–20.

### Phase 5 — Synthesis reconciliation

Completed in repository Phase 10. Pathways, crosscutting concepts, maps, status, terminology, links, and prerequisite direction are reconciled against reviewed Modules 01–20 and a machine-readable canonical graph.

### Phase 6 — Applied material and compatibility

Completed through repository Phases 11A–11B:

- exact-revision Principia artifact identity;
- non-live Principia–Atlas compatibility contract;
- four complete applied-learning routes;
- sixteen reviewed, revisioned, draft-release experiences;
- route-specific source and safety review.

### Phase 7 — Release candidate

Repository Phase 12 defines `principia-material-foundation-rc1` and adds:

- exact candidate scope;
- lifecycle and release-hold policy;
- terminology and equation contracts;
- document accessibility heuristics;
- revision, deprecation, and retraction scenarios;
- bounded Principia–Atlas pilot readiness;
- strict read-only RC validation.

A validator pass does not remove the human authority gates.

## Review record template

Use this template in focused review pull requests:

```text
Module or artifact:
Files reviewed:
Scientific claims corrected:
Equations and units checked:
Assumptions and limits added:
Sources opened and verified:
Weak sources replaced:
Links and identifiers repaired:
Safe explorations checked:
Accessibility and usability observations:
Remaining caveats:
Status transition:
Authority granting that transition:
```

## Current disposition

The correct description today is:

> A reviewed 20-module Principia foundation with reconciled synthesis, four complete applied-learning routes, exact-revision compatibility preparation, and an unreleased Phase 12 material release candidate awaiting coordinated automated validation and independent human authority.

## Phase 10 synthesis disposition

- A-001 through A-010 have repository-level resolutions or focused review artifacts.
- A-011 and A-012 are addressed for the synthesis layer through canonical titles, identifiers, navigable links, and edge vocabulary.
- A-013 is addressed through phase-specific reports, deterministic scripts, and read-only CI.
- No synthesis document is Complete; completion remains governed by explicit release authority.

## Phase 11 applied-material and compatibility disposition

- Four complete routes now test the experience model across thermal, energy, water, and distributed-information systems.
- Every experience is Reviewed with `artifact_revision: 1` and `release_status: draft`.
- Electrical, public-health, privacy, and live-system boundaries are explicit.
- The Principia–Atlas fixture remains `live: false` and no status crosses repositories automatically.

## Phase 12 release-candidate disposition

- RC1 scope is frozen in `release/phase-12-release-candidate.json`.
- The release decision is **Hold**.
- Automated promotion to Complete or Released is prohibited.
- The first bounded integration pilot remains conditional and non-live.
- Independent scientific, editorial, accessibility, safety, attribution, release-owner, and Atlas-side decisions remain required.
