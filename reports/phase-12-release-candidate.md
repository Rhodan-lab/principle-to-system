# Phase 12 — Principia Material Foundation Release Candidate

> Date: 2026-07-26  
> Candidate: `principia-material-foundation-rc1`  
> Base: Phase 11B merged through PR #13 at `223327901b6c1c259350622a00b822511293d516`  
> Product identity: Principia  
> Atlas status: separate repository; unchanged  
> Release decision: **Hold**  
> Validation status: implemented and validated on draft PR #14

## Purpose

Phase 12 evaluates the complete material-first Principia foundation as one release candidate. It does not add a software product and does not treat automated checks as independent certification.

RC1 covers:

- 20 core modules and 60 learner-facing core files;
- 6 pathways, 7 crosscutting concepts, and 3 knowledge maps;
- 16 applied experiences across 4 complete routes;
- 143 core source records and 28 experience-source records;
- the non-live `principia-atlas-bridge/0.1` fixture;
- release, revision, terminology, equation, accessibility, and dependency-impact governance.

## Status policy

RC1 preserves:

```yaml
core_status: reviewed
synthesis_status: reviewed
experience_status: reviewed
artifact_revision: 1
release_status: draft
repository_release_state: candidate-hold
```

No core, synthesis, or experience artifact becomes Complete. No experience becomes Released. Atlas knowledge status remains Atlas-only authority.

## Machine-readable contracts

- `release/phase-12-release-candidate.json` — exact RC scope, gates, and hold decision;
- `release/phase-12-terminology.json` — cross-artifact semantic vocabulary and prohibited shortcuts;
- `release/phase-12-equation-contracts.json` — ten representative equation and model-boundary contracts;
- `release/phase-12-revision-impact.json` — revision, deprecation, retraction, and Principia meaning-change scenarios;
- `release/phase-12-pilot-readiness.json` — bounded Principia–Atlas pilot readiness record;
- `scripts/validate_phase12_release_candidate.py` — read-only repository-wide validator.

## Terminology reconciliation

RC1 makes the following distinctions explicit:

- Reviewed is not Complete, Released, or Atlas-reviewed.
- Pedagogical status is not publication readiness.
- A model is a purpose-bounded representation, not the system itself.
- Correlation alone is not a causal identification strategy.
- Energy and power are different quantities.
- Efficiency requires a declared boundary and interval.
- Resilience requires a defined service and disturbance.
- Availability requires a defined population, interval, and service condition.
- A compatibility fixture is non-live and creates no lifecycle dependency.

## Equation and model reconciliation

Ten representative contracts test that recurring equations remain attached to variables, dimensions, assumptions, operating regimes, and interpretation limits:

1. Little’s Law;
2. queue backlog balance;
3. photovoltaic power;
4. battery energy balance;
5. water storage balance;
6. rainwater storage balance;
7. affine sensor error;
8. filter hydraulic resistance;
9. first-order room cooling;
10. refrigeration coefficient of performance.

Dimensional consistency is necessary but not sufficient. RC1 rejects equations presented without model-boundary language.

## Accessibility and usability heuristics

The automated gate checks the 92 learner-facing and synthesis documents for:

- one clear level-1 heading;
- non-skipping heading hierarchy;
- balanced code and display-math blocks;
- non-empty image alternative text;
- descriptive Markdown link labels;
- valid local link targets;
- source-and-module-link sections for applied experiences.

These checks do not replace human accessibility testing with assistive technology, varied devices, different reading conditions, or representative learners.

## Revision and deprecation behavior

The delayed-feedback bridge fixture is used to test five scenarios:

- load-bearing Atlas claim revised;
- supporting model revised;
- supporting concept deprecated;
- load-bearing claim retracted;
- Principia artifact meaning changed.

The required behavior is inspection, revalidation, or release blocking according to the declared policy. Forbidden behavior includes following `latest`, copying Atlas status, automatic promotion, ignoring a load-bearing retraction, or reusing a stale export after a Principia revision.

## Principia & Atlas readiness

Principia RC1 has exact revision identity, status separation, deterministic export, and impact scenarios. The integration remains:

```yaml
mode: compatibility-fixture
live: false
decision: hold
```

Atlas has not been modified by Phase 12. Atlas has not recorded that its direct-integration freeze has ended, accepted the external dependent, or approved a live pilot. Therefore RC1 may support a future pilot proposal but cannot activate one.

## Automated gates

The permanent Phase 12 workflow runs:

```bash
python3 scripts/validate_repo.py --strict
python3 scripts/validate_experiences.py --strict
python3 scripts/validate_phase11b_expansion.py
python3 scripts/validate_phase10_synthesis.py
python3 scripts/validate_phase10_audit.py
python3 scripts/export_principia_atlas_dependents.py --check
python3 scripts/validate_principia_atlas_bridge.py
python3 scripts/validate_principia_atlas_audit.py
python3 scripts/validate_phase12_release_candidate.py
```

The workflow uses `contents: read`, preserves diagnostics, and cannot clone Atlas, write files, commit, push, merge, promote status, or activate integration.

## Automated validation result

The exact draft PR #14 head passes all inherited Phase 5–11B workflows and the Phase 12 release-candidate workflow. Strict repository validation reports zero warnings and zero errors. RC1 validates 60 core files, 16 synthesis files, 16 draft-release experiences, 143 core sources, 28 experience sources, the ten equation contracts, terminology boundaries, document accessibility heuristics, five revision-impact scenarios, and the non-live pilot record.

Automated conformance does not change the release decision. It remains **Hold**.

## Human authority still required

A release decision requires recorded approval for:

1. independent scientific review;
2. editorial and pedagogical review;
3. accessibility and usability review;
4. safety and ethical review;
5. source and attribution review;
6. release-owner approval;
7. Atlas-side approval before a live pilot.

Until those records exist, the release decision remains **Hold**.

## Exit interpretation

Passing RC1 means the repository is a coherent, machine-validated material foundation suitable for independent review and bounded pilot planning. It does not mean every statement has been externally certified, every learner can use the materials accessibly, or a live Principia & Atlas product exists.

## Next stage

After RC1 merges, work separates into two tracks:

- **Principia release review:** human scientific, editorial, accessibility, safety, attribution, and release decisions;
- **Atlas maturity:** complete Atlas Phase 1 and independently approve the first exact-revision external-dependent pilot.

The optional software layer remains Phase 13 and begins only after the material foundation and governance decisions are mature enough to support it.
