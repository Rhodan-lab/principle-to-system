# Project State

> Last updated: 2026-07-26

## Current phase

**Phase 10 Synthesis Reconciliation implemented on `agent/phase-10-synthesis-reconciliation`; coordinated validation and pull-request integration remain pending.**

The repository remains a material-first educational foundation. Software is intentionally deferred until synthesis, release validation, and governance are mature.

## Phase progress

| Phase | Scope | Status |
| --- | --- | --- |
| 0 | Vision and educational philosophy | Complete |
| 1 | Core knowledge inventory | First-draft inventory complete |
| 2 | Repository audit and hardening | Complete |
| 3 | Applied-material foundation | Implemented and validated |
| 4 | Core metadata normalization | Merged and validated |
| 5 | Legacy source-ledger repair | Merged and validated |
| 6 | Foundations scientific review | Merged and validated through PR #8 |
| 7 | Physical-science review | Merged and validated through PR #8 |
| 8 | Life and Earth systems review | Merged and validated through PR #9 |
| 9 | Technology review | Merged and validated through PR #10 |
| 10 | Synthesis reconciliation | Implemented on Phase 10 branch; coordinated validation pending |
| 11 | Controlled material expansion | Seed exemplars exist; expansion pending reviewed synthesis |
| 12 | Release candidate | Not started |
| 13 | Optional software layer | Deferred |

## Integration topology

`main` contains the reviewed Modules 01–20 after PR #10. The Phase 10 branch was created directly from that merged state and changes only synthesis, audit, state, and validation artifacts. No workflow automatically merges pull requests.

## Repository status on the Phase 10 branch

### Phase 8 — Life and Earth Systems Modules 13–16

- Modules 13–16: **Reviewed**;

### Phase 9 Technology review implemented and merged through PR #10

- Modules 17–20: **Reviewed**;
- Modules 01–20: **Reviewed**;

### Reconciled synthesis layer

- 6 pathways: **Reviewed**;
- 7 crosscutting concepts: **Reviewed**;
- 3 knowledge maps: **Reviewed**;
- source ledger: **143 records**;
- no core or synthesis artifact is Complete.

Reviewed means focused reconciliation has checked metadata, canonical identifiers, links, prerequisite direction, terminology, equations, claims, limitations, and status consistency. It does not mean independently certified or release-ready.

## Phase 10 result — Synthesis Reconciliation

Phase 10 establishes `synthesis/phase-10-canonical-graph.json` as the machine-readable synthesis contract. It reconciles:

1. the exact 20-module prerequisite graph;
2. arrow direction and relationship vocabulary;
3. six science-to-technology pathways;
4. seven crosscutting concepts;
5. three Mermaid maps;
6. status policy, terminology, equations, quantities, and links;
7. superseded claims identified during Modules 01–20 review;
8. the unchanged 143-record source baseline.

Major repairs include removing hard transistor thresholds, universal material stereotypes, unconstrained genome-editing claims, fixed AI deployment promises, instantaneous-grid simplifications, frequency-capacity shortcuts, energy-in-bonds language, universal scale-free-network claims, and deterministic structure–function reasoning.

## Validation

```bash
python3 scripts/apply_phase10_synthesis.py --check
python3 scripts/validate_phase10_synthesis.py
python3 scripts/validate_repo.py
python3 scripts/validate_experiences.py --strict
```

The Phase 10 gate requires all 16 synthesis files to be Reviewed, the canonical graph to match repository module prerequisites, all links to resolve, every prerequisite arrow to use `prerequisite for`, the source ledger to remain at 143 records, no synthesis completion claims, and no regression in Phase 4–9 validation.

## Next phase

Phase 11 may expand system dossiers, failure-atlas entries, investigations, and design challenges only from stable reviewed patterns. Phase 12 remains the strict repository-wide release candidate and the earliest point at which Reviewed artifacts may be considered for Complete status.

## Continuation instructions

Read `README.md`, `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, `AUDIT.md`, this file, and the phase reports. Keep synthesis, expansion, release validation, and software implementation in separate focused pull requests. Never promote material solely because a file exists or a structural check passes.
