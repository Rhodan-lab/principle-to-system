# Project State

> Last updated: 2026-07-26

## Current phase

**Phase 16 — Offline Multi-Artifact Integration Pilot implemented and validated on draft PR #20; the PR remains unmerged.**

Material baseline: `principia-material-foundation-rc1`  
Active transition: **machine-gated-development**  
Software state: **foundation-validated**.  
Bridge state: **candidate-ready** (`mode: bridge-candidate`, `live: false`).  
Phase 15 state: **offline-pilot-validated** (`mode: offline-pilot`, `live: false`).  
Phase 16 state: **offline-multi-artifact-validated** (`mode: offline-multi-artifact-pilot`, `live: false`).

Principia and Atlas remain separate repositories with separate lifecycle authority.

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
| 13 | Software foundation | Merged and validated through PR #15 |
| 14 | Principia–Atlas bridge candidate | Merged and validated through PR #16 |
| 15 | Offline integration pilot | Merged and validated through PR #18 |
| 16 | Offline multi-artifact integration pilot | Implemented and validated on draft PR #20; unmerged |

## Integration topology

- PR #11 merged at `058f164f6e181311a34d68def22e252e7e20f646`.
- PR #12 merged at `565c119e63218b4376f501f99bc96c1e09a3acca`.
- PR #13 merged at `223327901b6c1c259350622a00b822511293d516`.
- PR #14 merged at `824fa2d4774647203222ab9198fc25ad4b11cda5`.
- PR #15 merged at `fa9807fcdb649692d9670701211e155ecff21258`.
- PR #16 was merged into `main` at commit `eb3a00dfbfdfaa5470cb40505fa213e5349a917f`.
- PR #17 finalized the bridge record at `02ce0bf99b6a27852a6ec610d875a9c88e465cec`.
- PR #18 was merged into `main` at commit `beeb4d6d4e71d1d08698a000e720fc88fc730ebc`.
- PR #19 finalized the Phase 15 record at `c9b14e385333e2640a76902297f0c8b3282668e4`.
- Atlas PR #20 merged the importer implementation at `1cc4aec6908a8703a7f505478329c633a23b4ef9`.
- Atlas PR #21 finalized the accepted importer baseline at `9370cc746e9756e433ac3772d56d079c9803b144`.
- Phase 16 candidate validation passed on exact head `67d6ec98c51188dabcffd48dad968a83653ea584`.

Main contains the reviewed material foundation, synthesis layer, four applied-learning routes, static software foundation, non-live exact-revision bridge candidate, pinned Atlas PR #20 importer snapshot, deterministic Phase 15 receipt, and lifecycle-impact matrix.

The validated Phase 16 branch adds two additional exact Principia exports, an atomic three-artifact batch, receipt contract v0.2, receipt chain, mixed lifecycle-impact matrix, and deterministic recovery scenarios.

No live Atlas dependency is declared. No workflow clones Atlas, writes to Atlas, imports Atlas status, or changes either repository automatically.

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
- no core module is Complete;
- no core or synthesis artifact is Complete;
- source ledger: **143 records**;
- Phase 9 central-ledger transition: 131 → 143 records.

### Historical validator markers

- Phase 9 Technology review implemented and validated on draft PR #10 before merge.
- Historical pre-merge marker: `Technology review | Implemented and validated on PR #10; awaiting merge`.
- Historical Phase 10 marker: `Phase 10 Synthesis Reconciliation implemented and validated on draft PR #11`.
- Phase 10 Synthesis reconciliation was subsequently merged through PR #11.
- Phase 11A — Principia & Atlas Compatibility Foundation was implemented and validated on draft PR #12 before merge.
- Phase 11B — Controlled Material Expansion was implemented and validated on draft PR #13 before merge.
- Historical Phase 12 marker: **Phase 12 — Release Candidate implemented and validated on draft PR #14; independent review, merge, and release authority remain pending.**
- Historical Phase 12 table marker: `| 12 | Release candidate | RC1 implemented and validated on draft PR #14; awaiting independent review and merge |`.
- Historical Phase 12 transition marker: `After PR #14 receives independent review and is merged, the project enters human release review while the release decision remains Hold.`
- Historical validation marker: release decision remains **Hold**.
- Historical Phase 14 marker: `Phase 14 — Principia–Atlas bridge candidate merged and validated through PR #16`.
- Historical importer marker: `Atlas Phase 2 may now consume`.
- Historical Phase 15 marker: `Phase 15 — Offline Integration Pilot merged and validated through PR #18`.
- Permanent CI is read-only.

### Reconciled synthesis layer

- 6 pathways: **Reviewed**;
- 7 crosscutting concepts: **Reviewed**;
- 3 knowledge maps: **Reviewed**.

Reviewed records focused machine validation; it does not merge Atlas status into Principia status.

## Status and authority separation

```yaml
status: reviewed
artifact_revision: 1
release_status: draft
```

- Atlas owns knowledge identity, evidence, provenance, exact revision, review level, lifecycle, and staleness.
- Principia owns pedagogical `status`, artifact revision, and publication `release_status`.
- Atlas remains unchanged by Principia Phase 16.
- status remains separate across repositories.
- automatic status inheritance is prohibited.

## Phase 11B result — Controlled Material Expansion

The applied-material layer contains:

- 4 complete routes;
- 16 Reviewed artifacts;
- 4 system dossiers;
- 4 failure patterns;
- 4 investigations;
- 4 design challenges;
- 28 records in the experience-source ledger.

All experience artifacts remain `artifact_revision: 1` and `release_status: draft`.

## Phase 12 result — Release Candidate RC1

`release/phase-12-release-candidate.json` defines `principia-material-foundation-rc1`.

RC1 preserves reviewed core, synthesis, and experience status; experience `release_status` remains draft; repository release decision remains **Hold**. The material foundation is machine-validated but not automatically published.

## Phase 13 result — Software foundation

The content-native software foundation is merged and `foundation-validated`. It deterministically renders the repository material without promoting content status or activating integration.

## Phase 14 result — Principia–Atlas bridge candidate

```yaml
mode: bridge-candidate
live: false
decision: candidate-ready
```

Exact Atlas dependencies:

```text
claim:en:model-oscillation-does-not-prove-real-system@1
concept:en:feedback@1
concept:en:oscillation@1
model:en:delayed-correction-recurrence@2
```

Atlas PR #20 subsequently accepted the exact export through a pinned read-only adapter. No live cross-repository call is enabled.

## Phase 15 result — Offline Integration Pilot

`release/phase-15-offline-pilot.json` defines `offline-pilot-validated`.

The pilot pins:

- Principia export SHA-256 `6d9d232007b5ecc18c6470f5c2e457decfcae1a5be99764be9796b4b24db7047`;
- Atlas PR #20 tested head `379d88d620469a749cebb88b0b41d9960e667558`;
- Atlas PR #20 merge commit `1cc4aec6908a8703a7f505478329c633a23b4ef9`;
- adapter `atlas-principia-bridge-adapter/0.1`;
- operational record `atlas-external-dependent/0.1`;
- lifecycle report `atlas-lifecycle-impact-report/0.1`.

The deterministic receipt accepts all four exact dependencies. Lifecycle scenarios produce:

- current → inspect;
- deprecated → revalidate;
- review-required stale → revalidate;
- confirmed stale → revalidate;
- retracted → block-release.

No automatic status change, release action, repository mutation, or network call is permitted. `live: false` remains mandatory.

## Phase 16 result — Offline Multi-Artifact Integration Pilot

`release/phase-16-offline-multi-artifact-pilot.json` defines `offline-multi-artifact-validated`.

The atomic batch contains:

```text
principia:failure-pattern:feedback-instability@1
principia:investigation:room-cooling@1
principia:system-dossier:refrigerator@1
```

The pilot pins Atlas PR #20 implementation and the accepted Atlas PR #21 governance baseline. It introduces:

- `principia-atlas-offline-import-batch/0.2`;
- `principia-atlas-offline-batch-receipt/0.2`;
- `principia-atlas-offline-receipt-chain/0.2`;
- `principia-atlas-offline-multi-impact-matrix/0.2`;
- `principia-atlas-offline-recovery-matrix/0.2`.

The lifecycle matrix tests fan-out across one or three Principia artifacts depending on the Atlas entity. The recovery matrix tests duplicate replay, stale or skipped sequence, wrong predecessor, valid next checkpoint, partial batch, digest corruption, status inheritance, and attempted live activation.

The exact candidate head `67d6ec98c51188dabcffd48dad968a83653ea584` passed all applicable Phase 5–16, compatibility, release-candidate, and software workflows. Repository integration remains a separate explicit action.

## Validation

```bash
python3 scripts/finalize_phase15_state.py --check
python3 scripts/validate_phase15_postmerge_record.py
python3 scripts/generate_phase15_offline_pilot.py --check
python3 scripts/validate_phase15_offline_pilot.py
python3 scripts/export_principia_atlas_dependents.py --check
python3 scripts/export_principia_atlas_dependents.py --manifest integration/principia-atlas/manifests/refrigerator.fixture.json --output integration/principia-atlas/exports/refrigerator.external-dependent.fixture.json --check
python3 scripts/export_principia_atlas_dependents.py --manifest integration/principia-atlas/manifests/room-cooling.fixture.json --output integration/principia-atlas/exports/room-cooling.external-dependent.fixture.json --check
python3 scripts/generate_phase16_offline_multi_artifact.py --check
python3 scripts/validate_phase16_offline_multi_artifact.py
python3 scripts/finalize_bridge_candidate_records.py --check
python3 scripts/validate_principia_atlas_bridge.py
python3 scripts/validate_principia_atlas_audit.py
python3 scripts/validate_experiences.py --strict
python3 scripts/validate_phase11b_expansion.py
python3 scripts/validate_phase10_synthesis.py
python3 scripts/validate_phase10_audit.py
python3 scripts/validate_repo.py --strict
python3 scripts/validate_phase12_release_candidate.py
python3 -m unittest discover -s software/tests -v
python3 scripts/validate_phase13_software.py
```

All applicable workflows passed on the exact candidate head before the validated record was written. The validated-record head must also remain green before integration.

## Next phase

After Phase 16 is integrated, the next bounded gate is an **offline event-protocol candidate** that models digest-bound lifecycle events and acknowledgements without activating network synchronization. Live integration remains disabled and requires a distinct future contract transition.
