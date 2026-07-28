# Project State

> Last updated: 2026-07-28

## Current phase

**Phase 22 — Offline Resolution-Consequence Planning Candidate implemented on `agent/phase-22-offline-resolution-consequence-planning`; exact-head validation pending.**

Material baseline: `principia-material-foundation-rc1`  
Active transition: **machine-gated-development**  
Software state: **foundation-validated**.  
Bridge state: **candidate-ready** (`mode: bridge-candidate`, `live: false`).  
Phase 15 state: **offline-pilot-validated** (`mode: offline-pilot`, `live: false`).  
Phase 16 state: **offline-multi-artifact-validated** (`mode: offline-multi-artifact-pilot`, `live: false`).  
Phase 17 state: **offline-event-protocol-validated** (`mode: offline-event-protocol`, `live: false`).  
Phase 18 state: **offline-reconciliation-simulation-validated** (`mode: offline-reconciliation-simulation`, `live: false`).  
Phase 19 state: **offline-reconciliation-policy-validated** (`mode: offline-reconciliation-policy`, `live: false`).  
Phase 20 state: **offline-manual-policy-resolution-validated** (`mode: offline-manual-policy-resolution`, `live: false`).  
Phase 21 state: **offline-policy-resolution-reconciliation-validated** (`mode: offline-policy-resolution-reconciliation`, `live: false`).  
Phase 22 target state: **offline-resolution-consequence-planning-candidate** (`mode: offline-resolution-consequence-planning`, `live: false`).

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
| 11B | Controlled Material Expansion | Merged and validated through PR #13 |
| 12 | Release candidate | Merged and validated through PR #14 |
| 13 | Software foundation | Merged and validated through PR #15 |
| 14 | Principia–Atlas bridge candidate | Merged and validated through PR #16 |
| 15 | Offline integration pilot | Merged and validated through PR #18 |
| 16 | Offline multi-artifact integration pilot | Merged and validated through PR #20 |
| 17 | Offline event-protocol candidate | Merged and validated through PR #22 |
| 18 | Offline reconciliation simulation | Merged and validated through PR #25 |
| 19 | Offline reconciliation policy | Merged and validated through PR #28 |
| 20 | Offline manual policy resolution | Merged and validated through PR #30 |
| 21 | Offline policy-resolution reconciliation | Merged and validated through PR #32 |
| 22 | Offline resolution-consequence planning | Implemented; exact-head validation pending |

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
- PR #20 was merged into `main` at commit `c493bf879a7945f9991e13592d42424138a0879b`.
- PR #21 finalized the Phase 16 record at `44410d47d318c5aaedb7716e4ef3bdefae09b442`.
- PR #22 was merged into `main` at commit `c9fba79f821d59b36030924e5c388f71a56f7787`.
- PR #24 finalized the Phase 17 record at `806b03335a1d0b43e5a32ffecce8439350564152`.
- PR #25 was merged into `main` at commit `4ecb41ad4f9f524e83cc0db43f672bd9dcf3b67a`.
- PR #27 finalized the Phase 18 record at `582117eb9ea9ecf489be5ef24464977195464d93`.
- Phase 19 exact candidate validation passed at `da77e4b1a5f6f17e98a38f0438c5531d0fba5aac`.
- PR #28 was merged into `main` at commit `699689c7a60da645d59cf2bdfe169b89f137a899`.
- PR #29 finalized the Phase 19 record at `2ceb502ed8bd4155324b76aed6642229dba18bb7`.
- Phase 20 exact candidate validation passed at `d128d2c469b43fc07fe1db2f62ce9538841e4463`.
- PR #30 was merged into `main` at commit `724611a7d7ec0b3723ea217928cba4616ce2bebd`.
- Phase 21 exact candidate validation passed at `ff97a73d8fcba37eaf31220a9480d882c345c7c4`.
- PR #32 was merged into `main` at commit `7e14b700883018ca11c38d07f82418f165f542f5`.
- Atlas PR #20 merged the importer implementation at `1cc4aec6908a8703a7f505478329c633a23b4ef9`.
- Atlas PR #21 finalized the accepted importer baseline at `9370cc746e9756e433ac3772d56d079c9803b144`.
- Phase 16 candidate validation passed at `67d6ec98c51188dabcffd48dad968a83653ea584`.
- Phase 16 final validated-record head was `d37674490f054241ef08ccf7a644247b444fa874`.
- Phase 17 exact candidate validation passed at `e260417ef7631ebf4f87c89faff7da45d571b63c`.
- Phase 18 exact candidate validation passed at `740ab7752bb03fc7dafe6bb9c076f5cb44a5f44f`.

Main contains the reviewed material foundation, synthesis layer, four applied-learning routes, static software foundation, non-live exact-revision bridge candidate, pinned Atlas importer baseline, deterministic Phase 15 receipt, the integrated Phase 16 atomic three-artifact batch, the integrated Phase 17 event protocol, the finalized Phase 18 reconciliation evidence, the integrated Phase 19 policy proposals, the integrated Phase 20 bounded-synthetic resolution evidence, the integrated Phase 21 proposal/resolution reconciliation evidence, and the Phase 22 planning-only consequence-plan stream, digest ledger, checkpoint, and recovery candidate.

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
- Historical Phase 12 table marker: `| 12 | Release candidate | RC1 implemented and validated on draft PR #14; awaiting merge |`.
- Historical Phase 12 transition marker: `After PR #14 receives independent review and is merged, the project enters human release review while the release decision remains Hold.`
- Historical validation marker: release decision remains **Hold**.
- Historical Phase 14 marker: `Phase 14 — Principia–Atlas bridge candidate merged and validated through PR #16`.
- Historical importer marker: `Atlas Phase 2 may now consume`.
- Historical Phase 15 marker: `Phase 15 — Offline Integration Pilot merged and validated through PR #18`.
- Historical Phase 16 marker: `Phase 16 — Offline Multi-Artifact Integration Pilot implemented and validated on draft PR #20`.
- Historical Phase 17 candidate marker: `exact-head validation pending`.
- Historical Phase 18 candidate marker: `exact-head validation pending`.
- Historical Phase 19 candidate marker: `exact-head validation pending`.
- Historical Phase 20 candidate marker: `exact-head validation pending`.
- Historical Phase 20 target marker: `offline-manual-policy-resolution-candidate`.
- Historical Phase 21 candidate marker: `exact-head validation pending`.
- Historical Phase 21 target marker: `offline-policy-resolution-reconciliation-candidate`.
- Historical Phase 22 candidate marker: `exact-head validation pending`.
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
- Atlas remains unchanged by Principia Phase 22.
- status remains separate across repositories.
- automatic status inheritance is prohibited.

## Phase 11B result — Controlled Material Expansion

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

The content-native software foundation is merged and `foundation-validated`. It deterministically renders repository material without promoting content status or activating integration.

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

`release/phase-15-offline-pilot.json` defines `offline-pilot-validated`. Current, deprecated, stale, and retracted scenarios remain non-mutating and `live: false`.

## Phase 16 result — Offline Multi-Artifact Integration Pilot

`release/phase-16-offline-multi-artifact-pilot.json` defines `offline-multi-artifact-validated` for the three thermal-control artifacts. Atomicity, receipt-chain, replay, corruption, status-inheritance, and live-activation cases remain machine-gated.

## Phase 17 result — Offline Event-Protocol Candidate

`release/phase-17-offline-event-protocol.json` preserves the immutable candidate, and `release/phase-17-postmerge.json` pins its exact validated provenance. Two bounded-synthetic events map to `revalidate` and `block-release` acknowledgements without changing status or release state.

## Phase 18 result — Offline Reconciliation Simulation

`release/phase-18-postmerge.json` pins exact candidate head `740ab7752bb03fc7dafe6bb9c076f5cb44a5f44f`, PR #25, merge `4ecb41ad4f9f524e83cc0db43f672bd9dcf3b67a`, and finalization merge `582117eb9ea9ecf489be5ef24464977195464d93`. Decision: `reconciled-no-mutation`.

## Phase 19 result — Offline Reconciliation Policy

Phase 19 records one manual review item and one non-effective release-hold proposal. Decision: `proposals-recorded-no-mutation`.

```yaml
manual_review_items: 1
release_hold_proposals: 1
effective_holds: 0
automatic_executions: 0
live: false
```

`release/phase-19-postmerge.json` pins exact tested head `da77e4b1a5f6f17e98a38f0438c5531d0fba5aac`, PR #28, merge `699689c7a60da645d59cf2bdfe169b89f137a899`, all 15 applicable workflows, and final state `offline-reconciliation-policy-validated`.

## Phase 20 result — Offline Manual Policy Resolution

The bounded-synthetic fixture records `accept` as `accepted-for-manual-review` and `defer` as `deferred-no-hold-activation`.

```yaml
fixture_kind: bounded-synthetic
resolution_count: 2
accepted_count: 1
deferred_count: 1
effective_holds: 0
operational_effects: 0
status_changes: 0
decision: resolutions-recorded-no-mutation
live: false
```

`release/phase-20-postmerge.json` pins exact tested head `d128d2c469b43fc07fe1db2f62ce9538841e4463`, PR #30, merge `724611a7d7ec0b3723ea217928cba4616ce2bebd`, all 16 applicable workflows, `real_authorization_claimed: false`, and final state `offline-manual-policy-resolution-validated`.

## Phase 21 result — Offline Policy-Resolution Reconciliation

Phase 21 reconciles the two exact proposals with the two synthetic resolutions.

```yaml
proposal_count: 2
resolution_count: 2
matched_resolutions: 2
missing_resolutions: 0
orphan_resolutions: 0
proposal_digest_mismatches: 0
resolution_digest_mismatches: 0
ledger_mismatches: 0
checkpoint_mismatches: 0
effective_holds: 0
operational_effects: 0
status_changes: 0
real_authorization_claimed: false
decision: reconciled-resolutions-no-mutation
live: false
```

`release/phase-21-postmerge.json` pins candidate SHA-256 `d3485c7941588232121c74fc2d063d51c73aa121c5bd9a8e4fcbc5be2d5ba4af`, exact tested head `ff97a73d8fcba37eaf31220a9480d882c345c7c4`, PR #32, merge `7e14b700883018ca11c38d07f82418f165f542f5`, all 17 applicable workflows, `real_authorization_claimed: false`, and final state `offline-policy-resolution-reconciliation-validated`.

## Phase 22 result — Offline Resolution-Consequence Planning Candidate

`release/phase-22-offline-resolution-consequence-planning.json` defines the immutable candidate `offline-resolution-consequence-planning-candidate` with `mode: offline-resolution-consequence-planning`, `fixture_kind: bounded-synthetic`, and `live: false`.

The candidate records one manual-review work plan and one release-governance follow-up plan. All six steps remain `planned-not-started` with `execution_permitted: false`.

```yaml
plan_count: 2
manual_review_plan_count: 1
release_governance_plan_count: 1
planned_step_count: 6
started_plan_count: 0
completed_plan_count: 0
effective_hold_count: 0
operational_effect_count: 0
status_change_count: 0
real_authorization_claimed: false
decision: consequence-plans-recorded-no-execution
live: false
```

The plans cover the same three exact thermal-control artifacts at revision 1. No review is completed, no release decision is selected, no content change is proposed, and no hold becomes effective.

The recovery matrix contains 28 deterministic scenarios and rejects source drift, missing or orphan plans, duplicate identities, unknown resolutions, sequence or digest corruption, ledger or checkpoint drift, changed step counts, started or completed work, completed review, content-change proposals, status recommendations, effects, authorization claims, status inheritance, automatic authority changes, repository mutation, and live activation.

## Validation

```bash
python3 scripts/generate_phase22_offline_resolution_consequence_planning.py --check
python3 scripts/validate_phase22_offline_resolution_consequence_planning.py
python3 -m unittest software.tests.test_phase22_offline_resolution_consequence_planning -v
python3 scripts/generate_phase21_offline_policy_resolution_reconciliation.py --check
python3 scripts/validate_phase21_offline_policy_resolution_reconciliation.py
python3 scripts/validate_phase21_postmerge_record.py
python3 -m unittest software.tests.test_phase21_offline_policy_resolution_reconciliation -v
python3 scripts/generate_phase20_offline_manual_policy_resolution.py --check
python3 scripts/validate_phase20_offline_manual_policy_resolution.py
python3 scripts/validate_phase20_postmerge_record.py
python3 -m unittest software.tests.test_phase20_offline_manual_policy_resolution -v
python3 scripts/generate_phase19_offline_reconciliation_policy.py --check
python3 scripts/validate_phase19_offline_reconciliation_policy.py
python3 scripts/validate_phase19_postmerge_record.py
python3 -m unittest software.tests.test_phase19_offline_reconciliation_policy -v
python3 scripts/validate_phase18_postmerge_record.py
python3 scripts/generate_phase18_offline_reconciliation.py --check
python3 scripts/generate_phase18_release_record.py --check
python3 scripts/validate_phase18_offline_reconciliation.py
python3 -m unittest software.tests.test_phase18_offline_reconciliation -v
python3 scripts/validate_phase17_postmerge_record.py
python3 scripts/validate_phase16_postmerge_record.py
python3 scripts/validate_phase15_postmerge_record.py
python3 scripts/validate_principia_atlas_bridge.py
python3 scripts/validate_principia_atlas_audit.py
python3 scripts/validate_experiences.py --strict
python3 scripts/validate_repo.py --strict
python3 scripts/validate_phase12_release_candidate.py
python3 -m unittest discover -s software/tests -v
python3 scripts/validate_phase13_software.py
```

## Next phase

Next gate: **offline-consequence-plan-assurance-candidate**.

The next bounded gate is an **offline consequence-plan assurance candidate**. It may independently verify plan completeness, source binding, digest continuity, and non-execution invariants, but it must not start work, complete review, activate a hold, claim authorization, call Atlas, or mutate either repository.
