# Project State

> Last updated: 2026-07-26

## Current phase

**Phase 13 — Software Foundation active on `agent/phase-13-software-foundation`; progression is governed by machine gates.**

Material baseline: `principia-material-foundation-rc1`  
Active transition: **machine-gated-development**  
Software state: **implementation pending validation**.

The repository remains a material-first educational foundation. Its future product identity is Principia. Atlas remains a separate repository and knowledge-governance authority.

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
| 10 | Synthesis reconciliation | Merged and validated through PR #11 |
| 11A | Principia & Atlas compatibility foundation | Merged and validated through PR #12 |
| 11B | Controlled material expansion | Merged and validated through PR #13 |
| 12 | Release candidate | Merged and validated through PR #14 |
| 13 | Software foundation | Active; machine validation pending |

## Integration topology

PR #11 was merged into `main` at commit `058f164f6e181311a34d68def22e252e7e20f646`. PR #12 was merged into `main` at commit `565c119e63218b4376f501f99bc96c1e09a3acca`. PR #13 was merged into `main` at commit `223327901b6c1c259350622a00b822511293d516`. PR #14 was merged into `main` at commit `824fa2d4774647203222ab9198fc25ad4b11cda5`.

Main therefore contains:

- reviewed Modules 01–20;
- six reviewed pathways;
- seven reviewed crosscutting concepts;
- three reviewed knowledge maps;
- four complete applied-learning routes with sixteen Reviewed artifacts;
- the non-live `principia-atlas-bridge/0.1` compatibility foundation.

Phase 12 was merged through PR #14 and remains the validated material baseline. Phase 13 was created directly from that merge and adds a content-native static software layer, deterministic build artifacts, machine-only governance, tests, project documentation, and read-only CI.

No live Atlas dependency is declared. No workflow clones Atlas, imports Atlas status, or changes either repository automatically.

## Reviewed foundation and historical continuity

### Foundations Modules 01–05

- Modules 01–05: **Reviewed**;

### Physical Science Modules 06–12

- Modules 06–12: **Reviewed**;

### Phase 8 — Life and Earth Systems Modules 13–16

- Modules 13–16: **Reviewed**;

### Phase 9 Technology review

- Modules 17–20: **Reviewed**;
- Modules 01–20: **Reviewed**;
- source ledger: **143 records**;
- no core module is Complete;
- no core or synthesis artifact is Complete.

### Phase 12 transition markers retained for validator continuity

The following strings describe the former Phase 12 gate and are retained only as historical audit inputs. They are superseded by `release/phase-13-machine-governance.json`.

- Historical validation marker: release decision remains **Hold**.

- **Phase 12 — Release Candidate implemented and validated on draft PR #14; independent review, merge, and release authority remain pending.**
- `| 12 | Release candidate | RC1 implemented and validated on draft PR #14; awaiting independent review and merge |`
- `After PR #14 receives independent review and is merged, the project enters human release review while the release decision remains Hold.`

### Historical phase markers retained for deterministic continuity

- Phase 9 Technology review implemented and validated on draft PR #10 before that pull request was merged.
- Historical pre-merge marker: `Technology review | Implemented and validated on PR #10; awaiting merge`.
- The Phase 9 central-ledger transition was 131 → 143 records.
- Historical Phase 10 marker: `Phase 10 Synthesis Reconciliation implemented and validated on draft PR #11`.
- Phase 10 Synthesis reconciliation was subsequently merged through PR #11.
- Phase 11A — Principia & Atlas Compatibility Foundation was implemented and validated on draft PR #12 before merge.
- Phase 11B — Controlled Material Expansion was implemented and validated on draft PR #13 before merge.
- Permanent CI is read-only.

### Reconciled synthesis layer

- 6 pathways: **Reviewed**;
- 7 crosscutting concepts: **Reviewed**;
- 3 knowledge maps: **Reviewed**.

Reviewed means focused reconciliation has checked metadata, canonical identifiers, links, prerequisite direction, terminology, equations, claims, limitations, and status consistency. It does not mean independently certified or release-ready.

## Phase 11A result — Principia & Atlas Compatibility Foundation

Phase 11A introduced the Principia-side `principia-atlas-bridge/0.1` contract without changing Atlas.

The experience identity model separates:

```yaml
status: reviewed
artifact_revision: 1
release_status: draft
```

- `status` remains Principia pedagogical maturity;
- `artifact_revision` is the exact dependency-relevant Principia revision;
- `release_status` is Principia publication readiness;
- Atlas knowledge status remains Atlas-only authority.

The compatibility fixture remains:

```yaml
mode: compatibility-fixture
live: false
```

No status crosses the repository boundary automatically.

## Phase 11B result — Controlled Material Expansion

`experiences/phase-11b-inventory.json` defines:

- **4 complete routes**;
- **16 Reviewed artifacts**;
- **4 system dossiers**;
- **4 failure patterns**;
- **4 investigations**;
- **4 design challenges**;
- `artifact_revision: 1` for every artifact;
- `release_status: draft` for every artifact;
- no Complete or released experience.

`sources/experience-source-ledger.md` contains **28 records**. The central core-module ledger remains at **143 records**.

## Phase 12 result — Release Candidate RC1

`release/phase-12-release-candidate.json` defines `principia-material-foundation-rc1`.

### Frozen scope

- 20 core modules;
- 60 learner-facing core files;
- 16 synthesis files;
- 4 complete routes;
- 16 Reviewed experience artifacts;
- 143 core source records;
- 28 experience-source records;
- one non-live Principia–Atlas compatibility fixture.

### Lifecycle policy

RC1 preserves:

```yaml
core_status: reviewed
synthesis_status: reviewed
experience_status: reviewed
artifact_revision: 1
release_status: draft
repository_release_state: candidate-hold
```

Phase 12 originally kept RC1 on Hold. The Phase 13 owner directive supersedes the human-review dependency and authorizes machine-gated software development while preserving all pedagogical and publication statuses.

### RC contracts

- `release/phase-12-terminology.json` defines cross-artifact terminology and prohibited semantic shortcuts.
- `release/phase-12-equation-contracts.json` defines ten representative equation and model-boundary contracts.
- `release/phase-12-revision-impact.json` defines revision, deprecation, retraction, and Principia meaning-change behavior.
- `release/phase-12-pilot-readiness.json` records conditional readiness for the delayed-feedback pilot.
- `scripts/validate_phase12_release_candidate.py` validates the repository-wide candidate without writing files.

### Principia & Atlas boundary

Principia has exact artifact identity, status separation, deterministic export, and revision-impact scenarios. The pilot remains:

```yaml
mode: compatibility-fixture
live: false
decision: hold
```

Atlas remains unchanged. Atlas has not recorded that its direct-integration freeze has ended, accepted the external dependent, or approved a live pilot.

## Validation

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

The exact draft PR #14 head passes metadata, source, scientific-review, synthesis, applied-material, compatibility, strict-repository, accessibility, terminology, equation, revision-impact, and workflow-immutability gates. The permanent Phase 12 workflow uses `contents: read`, preserves diagnostics, and cannot clone Atlas, write, commit, push, merge, promote lifecycle state, or activate integration.

## Phase 13 machine-only authority

The project owner removed human review as a blocking gate. Active progression now follows `release/phase-13-machine-governance.json`.

Machine authority means:

1. declared validators and tests decide whether the phase passes;
2. any failed gate blocks progression;
3. material status is not promoted merely because software builds;
4. automatic merge and automatic public publication remain disabled;
5. Atlas status is never inherited and live integration remains disabled until cross-repository machine contracts pass.

The former Phase 12 human-authority language is retained only in historical records for deterministic audit continuity. It is not an active project dependency.

## Next phase

Phase 13 validates the reference software foundation. After that gate passes, the next software phase expands product navigation, content operations, deployment packaging, and optional Atlas interoperability without changing content authority.

## Continuation instructions

Read `README.md`, `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, `AUDIT.md`, this file, `release/README.md`, the Phase 10–12 reports, `experiences/phase-11b-inventory.json`, and `contracts/principia-atlas/0.1/README.md`. Keep Atlas changes in the Atlas development track. Never infer status across repositories and never promote material solely because software or structural validation passes. Phase progression uses declared machine gates rather than a human-review dependency.
