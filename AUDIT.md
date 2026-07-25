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

This was a repository-level audit, not yet a line-by-line scientific certification of all 60 learner-facing files.

## Central finding

The repository has a strong educational architecture and a complete first-draft inventory. Its principal weakness is that structural completion was previously treated as scientific and editorial completion.

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

The pathways and crosscutting concepts reinforce this architecture well. The next phase is therefore not a redesign. It is a systematic verification and repair pass that makes the implementation satisfy its own standard.

## Severity levels

- **Blocking** — prevents trustworthy validation or makes repository status materially misleading.
- **Major** — can mislead learners, break navigation, or violate the documented content/source policy.
- **Minor** — reduces consistency, clarity, or maintainability without making the content unusable.

## Blocking findings

### A-001 — Status claims do not match learner-file status

`INDEX.md` and the former project state labelled every module Complete while sampled learner files retained `status: draft`.

**Required resolution:** module status must be computed from the three learner-facing files and may advance only under the definitions in `PROJECT_STATE.md`.

**Current action:** `INDEX.md` now reports all modules as Draft pending review.

### A-002 — Malformed slug values

A previous duplicate-slug repair produced values such as:

```yaml
slug: "11-waves-signals"-technology
```

This is not a valid quoted scalar under the intended frontmatter contract, even though the former ad-hoc parser accepted it.

**Required resolution:** normalize each learner-file slug to a valid unique lowercase kebab-case identifier, for example:

```yaml
slug: 11-waves-signals-technology
```

### A-003 — Source-ledger rows are not consistently machine-readable

Some lines contain several sources concatenated into one Markdown table row. A row-count check therefore cannot establish that the claimed number of sources is valid.

**Required resolution:** use exactly one source per row and exactly eight columns per row.

### A-004 — Former validator could report false success

The former validator used a permissive frontmatter parser, searched for section keywords anywhere in a file rather than validating headings, did not validate canonical dependency identifiers, and counted ledger lines rather than valid source rows.

**Current action:** the validator has been replaced with a stricter standard-library implementation and a `--strict` release mode.

## Major findings

### A-005 — Non-canonical connection identifiers

Several files use identifiers that do not correspond to repository modules, including names that appear to come from an earlier outline.

**Required resolution:** define one canonical module-ID vocabulary and use it in all `prerequisites` and `connections` lists.

### A-006 — Inconsistent `domain` semantics

Some files use `domain: technology` or `domain: explore` to describe the file role, while the content guide defines domain as the module’s subject grouping.

**Required resolution:** all three files in a module should share the module domain: `foundations`, `science`, or `technology`.

### A-007 — Source quality does not consistently meet policy

The policy prioritizes primary literature, reviews, consensus reports, standards, agencies, institutions, societies, and peer-reviewed open textbooks. Some modules instead rely substantially on Wikipedia or weaker summaries; sampled semiconductor material cited only Wikipedia in its local source section.

**Required resolution:** replace weak sources with higher-tier sources and verify every cited source directly before changing factual claims.

### A-008 — Scientific explanations require expert tightening

Representative examples include definitions that are valid only under restricted conditions but are written as general definitions, such as temperature described only through average translational kinetic energy, or entropy framed through “disorder.”

**Required resolution:** review each claim for scope, assumptions, sign convention, units, counterexamples, and model limits.

### A-009 — Repository maps may disagree with file metadata

The dependency map and index provide a coherent canonical graph, but sampled frontmatter lists diverge from it.

**Required resolution:** treat `INDEX.md` and the complete dependency map as the initial canonical graph, then revise both together when scientific review justifies a dependency change.

### A-010 — Pathways are stronger than some source modules

The pathways often explain abstraction and trade-offs more clearly than the modules they depend on.

**Required resolution:** use pathway quality as a benchmark while reviewing module `technology.md` files, avoiding copy-paste duplication.

## Minor findings

### A-011 — Terminology and capitalization vary

Module titles, headings, identifier names, and domain labels are not fully normalized.

### A-012 — Some cross-links are descriptive rather than navigable

A connection may be named without a relative Markdown link, reducing the repository’s usefulness as a connected map.

### A-013 — Completion history obscures review history

Large batches were committed as “complete” without a documented scientific-review trail.

**Required resolution:** future review pull requests should identify claims corrected, sources opened, equations checked, and remaining caveats.

## Repair sequence

### Phase 1 — Contract and metadata

1. Harden validation.
2. Make status claims honest.
3. Repair frontmatter syntax and unique slugs.
4. Normalize domains, prerequisites, and connections.
5. Normalize the source ledger.
6. Resolve all structural validator errors.

### Phase 2 — Foundations review

Review Modules 01–05 in order. These modules define the reasoning, measurement, modeling, probability, and computational language used by every later module.

### Phase 3 — Science review

Review Modules 06–16 in dependency order. Check equations, units, causal mechanisms, scale transitions, conservation principles, and limits of validity.

### Phase 4 — Technology review

Review Modules 17–20 against the scientific modules. Ensure that each component and architecture is causally connected to the underlying principle and that constraints, safety, reliability, and lifecycle are substantive.

### Phase 5 — Synthesis reconciliation

Reconcile pathways, crosscutting concepts, maps, index entries, and source-ledger references against the reviewed modules.

### Phase 6 — Release gate

A release candidate must pass:

```bash
python3 scripts/validate_repo.py --strict
```

It must also have no unresolved scientific-review findings.

## Review record template

Use this template in module-focused pull requests:

```text
Module:
Files reviewed:
Scientific claims corrected:
Equations and units checked:
Assumptions and limits added:
Sources opened and verified:
Weak sources replaced:
Links and identifiers repaired:
Safe explorations checked:
Remaining caveats:
Status transition:
```

## Current disposition

The repository is valuable and worth continuing. Its architecture should be preserved. The correct description today is:

> A structurally complete, connected first draft undergoing scientific and editorial review.
