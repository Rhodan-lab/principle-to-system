# Project State

> Last updated: 2026-07-26

## Current phase

**Phase 11A — Principia & Atlas Compatibility Foundation implemented on draft PR #12; coordinated validation and independent review remain pending.**

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
| 11A | Principia & Atlas compatibility foundation | Implemented on draft PR #12; coordinated validation pending |
| 11B | Controlled material expansion | Pending compatibility foundation |
| 12 | Release candidate | Not started |
| 13 | Optional software layer | Deferred |

## Integration topology

PR #11 was merged into `main` at commit `058f164f6e181311a34d68def22e252e7e20f646`. Main now contains reviewed Modules 01–20, six pathways, seven crosscutting concepts, and three knowledge maps.

The Phase 11A branch was created directly from that merged state. It modifies only the Principia repository. Atlas was inspected read-only to match its accepted `atlas-content/0.1` identities and `atlas-review-coverage/0.1` external-dependent boundary.

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
- Permanent CI is read-only.

### Reconciled synthesis layer

- 6 pathways: **Reviewed**;
- 7 crosscutting concepts: **Reviewed**;
- 3 knowledge maps: **Reviewed**.

Reviewed means focused reconciliation has checked metadata, canonical identifiers, links, prerequisite direction, terminology, equations, claims, limitations, and status consistency. It does not mean independently certified or release-ready.

## Phase 11A result — Principia & Atlas Compatibility Foundation

Phase 11A introduces the Principia-side `principia-atlas-bridge/0.1` contract without changing Atlas.

### Artifact identity and status separation

The four seed experiences and their templates now include:

```yaml
artifact_revision: 1
release_status: draft
```

- `status` remains Principia pedagogical maturity;
- `release_status` is Principia publication readiness;
- `artifact_revision` is the exact Principia revision exposed to dependency reporting;
- Atlas knowledge status remains authoritative only in Atlas.

### Non-live compatibility fixture

`integration/principia-atlas/manifests/feedback-instability.fixture.json` describes exact revision-1 Atlas dependencies for the Principia feedback-instability artifact.

The fixture is explicitly:

```yaml
mode: compatibility-fixture
live: false
```

It proves contract compatibility only. It does not assert Atlas review completion and does not activate cross-repository behavior.

### Deterministic external-dependent export

`scripts/export_principia_atlas_dependents.py` generates the opaque shape documented by Atlas:

```text
Principia artifact ID + repository + artifact revision + local role + exact Atlas IDs
```

The export contains no pedagogical, release, or knowledge status fields.

### Dishonest paths that must fail

- copying Atlas lifecycle status into Principia authority;
- using mutable `latest` Atlas revisions;
- activating a live bridge while Atlas Phase 1 freezes direct integration.

## Validation

```bash
python3 scripts/export_principia_atlas_dependents.py --check
python3 scripts/validate_principia_atlas_bridge.py
python3 scripts/validate_principia_atlas_audit.py
python3 scripts/validate_experiences.py --strict
python3 scripts/validate_phase10_synthesis.py
python3 scripts/validate_phase10_audit.py
python3 scripts/validate_repo.py
```

The permanent compatibility workflow uses `contents: read`. It may validate Principia files and stored fixtures, but it may not clone Atlas, write files, push commits, merge pull requests, or change lifecycle status.

## Next phase

Phase 11B may expand system dossiers, failure-atlas entries, investigations, and design challenges using revisioned Principia artifacts. A live Principia–Atlas pilot requires explicit approval and compatible phase gates in both repositories. Phase 12 remains the strict release candidate and earliest completion gate.

## Continuation instructions

Read `README.md`, `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, `AUDIT.md`, this file, the Phase 10 report, the Phase 11A report, and `contracts/principia-atlas/0.1/README.md`. Keep Atlas changes in the Atlas development track. Never infer status across repositories and never promote material solely because structural validation passes.
