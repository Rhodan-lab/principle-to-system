# Project State

> Last updated: 2026-07-26

## Current phase

**Phase 11B — Controlled Material Expansion implemented and validated on draft PR #13; independent review and merge remain pending.**

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
| 11B | Controlled material expansion | Implemented and validated on draft PR #13; awaiting independent review and merge |
| 12 | Release candidate | Not started |
| 13 | Optional software layer | Deferred |

## Integration topology

PR #11 was merged into `main` at commit `058f164f6e181311a34d68def22e252e7e20f646`. PR #12 was merged into `main` at commit `565c119e63218b4376f501f99bc96c1e09a3acca`.

Main therefore contains:

- reviewed Modules 01–20;
- six reviewed pathways;
- seven reviewed crosscutting concepts;
- three reviewed knowledge maps;
- the non-live `principia-atlas-bridge/0.1` compatibility foundation.

The Phase 11B branch was created directly from that merged state. It modifies only Principia educational materials, navigation, source coverage, project records, validators, and read-only CI.

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

The existing compatibility fixture remains:

```yaml
mode: compatibility-fixture
live: false
```

No status crosses the repository boundary automatically. A live pilot still requires explicit approval and compatible phase gates in both repositories.

## Phase 11B result — Controlled Material Expansion

Phase 11B expands the applied learning layer from one route and four artifacts to four complete routes and sixteen artifacts.

### Canonical inventory

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

### Routes

1. `thermal-control`
   - domestic refrigerator;
   - feedback instability;
   - room-cooling investigation;
   - passive-cooler design challenge.

2. `resilient-energy`
   - solar–battery microgrid;
   - protection coordination failure;
   - partial-shading investigation;
   - resilient charging-hub design challenge.

3. `water-infrastructure`
   - drinking-water treatment and distribution network;
   - sensor drift and hidden degradation;
   - filter-loading investigation;
   - non-potable rainwater-buffer design challenge.

4. `distributed-information`
   - distributed web-service request;
   - retry storm and queue collapse;
   - queue-delay investigation;
   - resilient school-information-service design challenge.

### Safety boundaries

- Energy work is diagram-, public-data-, and simulation-only; no construction, wiring, battery modification, islanding, backfeed, or grid testing.
- Water work does not provide a procedure for producing safe drinking water; no contaminated-water handling, treatment chemicals, tasting, plumbing modification, or potable claim is allowed.
- Information-system work uses synthetic traffic and fictional data only; no live-service access, scanning, flooding, credential use, or private student data is allowed.

### Source result

`sources/experience-source-ledger.md` expands from 9 to **28 records**. Every one of the sixteen experience slugs has source coverage. The central 143-record core-module ledger is unchanged.

### Principia & Atlas boundary

Phase 11B uses revisioned Principia artifacts but creates no new Atlas manifest and no live dependency. Atlas remains unchanged.

## Validation result

The exact draft PR #13 head passes:

```bash
python3 scripts/validate_experiences.py --strict
python3 scripts/validate_phase11b_expansion.py
python3 scripts/export_principia_atlas_dependents.py --check
python3 scripts/validate_principia_atlas_bridge.py
python3 scripts/validate_principia_atlas_audit.py
python3 scripts/validate_phase10_synthesis.py
python3 scripts/validate_phase10_audit.py
python3 scripts/validate_repo.py
```

All applicable GitHub Actions workflows pass together:

- Phase 5 Sources;
- Phase 6 Foundations;
- Phase 7 Physical Science;
- Phase 8 Life and Earth Systems;
- Phase 9 Technology;
- Phase 10 Synthesis;
- Applied Materials;
- Principia–Atlas Compatibility;
- Phase 11B Expansion.

The permanent `.github/workflows/validate-phase-11b-expansion.yml` workflow uses `contents: read`. It validates the original experience foundation, all sixteen expanded artifacts, route completeness, revision and release state, source coverage, safety boundaries, navigation, Phase 10 continuity, Phase 11A compatibility, repository structure, workflow immutability, and preserved diagnostic output. It cannot write, commit, push, merge, or activate Atlas integration.

## Next phase

Phase 12 is the repository-wide release candidate. It must perform independent scientific and editorial review, cross-artifact terminology and equation reconciliation, source integrity, accessibility and usability review, revision and deprecation tests, release-status governance, and a bounded readiness assessment for the first live Principia–Atlas pilot.

## Continuation instructions

Read `README.md`, `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, `AUDIT.md`, this file, the Phase 10 report, the Phase 11A report, the Phase 11B report, `experiences/phase-11b-inventory.json`, and `contracts/principia-atlas/0.1/README.md`. Keep Atlas changes in the Atlas development track. Never infer status across repositories and never promote material solely because structural validation passes.
