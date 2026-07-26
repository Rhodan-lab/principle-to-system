# Project State

> Last updated: 2026-07-26

## Current phase

**Phase 12 — Release Candidate implemented on `agent/phase-12-release-candidate`; coordinated validation, independent review, and release authority remain pending.**

Candidate: `principia-material-foundation-rc1`  
Release decision remains **Hold**.

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
| 12 | Release candidate | RC1 implemented; coordinated validation pending |
| 13 | Optional software layer | Deferred |

## Integration topology

PR #11 was merged into `main` at commit `058f164f6e181311a34d68def22e252e7e20f646`. PR #12 was merged into `main` at commit `565c119e63218b4376f501f99bc96c1e09a3acca`. PR #13 was merged into `main` at commit `223327901b6c1c259350622a00b822511293d516`.

Main therefore contains:

- reviewed Modules 01–20;
- six reviewed pathways;
- seven reviewed crosscutting concepts;
- three reviewed knowledge maps;
- four complete applied-learning routes with sixteen Reviewed artifacts;
- the non-live `principia-atlas-bridge/0.1` compatibility foundation.

The Phase 12 branch was created directly from the merged Phase 11B state. It adds release governance, repository-wide validation, terminology and equation contracts, revision-impact scenarios, pilot-readiness records, project documentation, and read-only CI.

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

No automated gate may promote content to Complete or Released. The release decision remains **Hold** until explicit human authority is recorded.

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

The permanent Phase 12 workflow must use `contents: read`, preserve diagnostics, and never clone Atlas, write, commit, push, merge, promote lifecycle state, or activate integration.

## Human authority still required

Automated validation cannot grant:

1. independent scientific approval;
2. editorial and pedagogical approval;
3. accessibility and usability approval;
4. safety and ethical approval;
5. source and attribution approval;
6. release-owner approval;
7. Atlas-side live-pilot approval.

## Next phase

After RC1 automated validation, the project enters independent release review. Phase 13 remains the optional software layer and begins only after the material foundation and governance decisions are mature enough to support it.

## Continuation instructions

Read `README.md`, `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, `AUDIT.md`, this file, `release/README.md`, the Phase 10–12 reports, `experiences/phase-11b-inventory.json`, and `contracts/principia-atlas/0.1/README.md`. Keep Atlas changes in the Atlas development track. Never infer status across repositories and never promote material solely because structural validation passes.
