# Project State

> Last updated: 2026-07-28

## Current phase

**Phase 20 — Offline Manual Policy Resolution Candidate implemented on `agent/phase-20-offline-manual-policy-resolution`; exact-head validation pending.**

Material baseline: `principia-material-foundation-rc1`  
Active transition: **machine-gated-development**  
Software state: **foundation-validated**.  
Bridge state: **candidate-ready** (`mode: bridge-candidate`, `live: false`).  
Phase 15 state: **offline-pilot-validated** (`mode: offline-pilot`, `live: false`).  
Phase 16 state: **offline-multi-artifact-validated** (`mode: offline-multi-artifact-pilot`, `live: false`).  
Phase 17 state: **offline-event-protocol-validated** (`mode: offline-event-protocol`, `live: false`).  
Phase 18 state: **offline-reconciliation-simulation-validated** (`mode: offline-reconciliation-simulation`, `live: false`).  
Phase 19 state: **offline-reconciliation-policy-validated** (`mode: offline-reconciliation-policy`, `live: false`).  
Phase 20 target state: **offline-manual-policy-resolution-candidate** (`mode: offline-manual-policy-resolution`, `live: false`).

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
| 16 | Offline multi-artifact integration pilot | Merged and validated through PR #20 |
| 17 | Offline event-protocol candidate | Merged and validated through PR #22 |
| 18 | Offline reconciliation simulation | Merged and validated through PR #25 |
| 19 | Offline reconciliation policy | Merged and validated through PR #28 |
| 20 | Offline manual policy resolution | Implemented; exact-head validation pending |

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
- Atlas PR #20 merged the importer implementation at `1cc4aec6908a8703a7f505478329c633a23b4ef9`.
- Atlas PR #21 finalized the accepted importer baseline at `9370cc746e9756e433ac3772d56d079c9803b144`.
- Phase 16 candidate validation passed at `67d6ec98c51188dabcffd48dad968a83653ea584`.
- Phase 16 final validated-record head was `d37674490f054241ef08ccf7a644247b444fa874`.
- Phase 17 exact candidate validation passed at `e260417ef7631ebf4f87c89faff7da45d571b63c`.
- Phase 18 exact candidate validation passed at `740ab7752bb03fc7dafe6bb9c076f5cb44a5f44f`.

Main contains the reviewed material foundation, synthesis layer, four applied-learning routes, static software foundation, non-live exact-revision bridge candidate, pinned Atlas importer baseline, deterministic Phase 15 receipt, the integrated Phase 16 atomic three-artifact batch, the integrated Phase 17 event protocol, the finalized Phase 18 reconciliation evidence, the integrated Phase 19 manual review queue, non-effective release-hold proposal, digest ledger, and recovery evidence, and the Phase 20 bounded-synthetic accept/defer resolution stream, resolution ledger, checkpoint, and recovery candidate.

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
- Historical Phase 16 marker: `Phase 16 — Offline Multi-Artifact Integration Pilot implemented and validated on draft PR #20`.
- Historical Phase 17 candidate marker: `exact-head validation pending`.
- Historical Phase 18 candidate marker: `exact-head validation pending`.
- Historical Phase 19 candidate marker: `exact-head validation pending`.
- Historical Phase 20 candidate marker: `exact-head validation pending`.
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
- Atlas remains unchanged by Principia Phase 20.
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

The pilot pins the exact Principia export, the accepted Atlas PR #20 implementation, and the Atlas PR #21 governance baseline. Current, deprecated, stale, and retracted scenarios remain non-mutating and `live: false`.

## Phase 16 result — Offline Multi-Artifact Integration Pilot

`release/phase-16-offline-multi-artifact-pilot.json` defines `offline-multi-artifact-validated` for the three thermal-control artifacts. Atomic batch, receipt-chain, lifecycle fan-out, replay, corruption, sequence, status-inheritance, and live-activation cases remain machine-gated.

## Phase 17 result — Offline Event-Protocol Candidate

`release/phase-17-offline-event-protocol.json` preserves the immutable event-protocol candidate, and `release/phase-17-postmerge.json` pins its exact validated provenance. Two bounded-synthetic events map to `revalidate` and `block-release` acknowledgements without changing Principia status or release state.

## Phase 18 result — Offline Reconciliation Simulation

`release/phase-18-offline-reconciliation.json` preserves the immutable reconciliation candidate, and `release/phase-18-postmerge.json` pins exact candidate head `740ab7752bb03fc7dafe6bb9c076f5cb44a5f44f`, PR #25, merge `4ecb41ad4f9f524e83cc0db43f672bd9dcf3b67a`, and finalization merge `582117eb9ea9ecf489be5ef24464977195464d93`.

The exact baseline reconciles two events and two acknowledgements with zero missing, orphan, stale-artifact, or action-mismatch findings. Decision: `reconciled-no-mutation`.

## Phase 19 result — Offline Reconciliation Policy

Phase 19 converts the finalized Phase 18 actions into two explicit proposals:

- one manual review queue item for `revalidate`;
- one release-hold proposal for `block-release`.

Both cover the three exact thermal-control artifacts. The review item requires manual resolution. The hold remains proposed and non-effective. The digest ledger decision is `proposals-recorded-no-mutation`.

```yaml
manual_review_items: 1
release_hold_proposals: 1
effective_holds: 0
automatic_executions: 0
live: false
```

The recovery matrix contains 14 scenarios and rejects source drift, weakened action, automatic execution, effective holds, affected-set drift, duplicate identities, ledger drift, status inheritance, automatic mutation, and live activation.

`release/phase-19-postmerge.json` separately pins the immutable candidate digest, exact tested head `da77e4b1a5f6f17e98a38f0438c5531d0fba5aac`, PR #28, merge commit `699689c7a60da645d59cf2bdfe169b89f137a899`, all 15 applicable workflows, authority boundaries, and final state `offline-reconciliation-policy-validated`.

## Phase 20 result — Offline Manual Policy Resolution Candidate

`release/phase-20-offline-manual-policy-resolution.json` defines the immutable candidate `offline-manual-policy-resolution-candidate` with `mode: offline-manual-policy-resolution` and `live: false`.

The bounded-synthetic fixture records two explicit proposal resolutions:

- `accept` the manual-review proposal as `accepted-for-manual-review`;
- `defer` the release-hold proposal as `deferred-no-hold-activation`.

Both resolutions remain non-operational and cover the three exact thermal-control artifacts at revision 1. They do not claim real human authorization.

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

The ordered ledger pins each proposal-document digest, resolution digest, sequence, and predecessor. The checkpoint pins the stream and ledger while recording zero effective holds, operational effects, and status changes.

The recovery matrix contains 17 scenarios and rejects Phase 19 source drift, proposal digest drift, unknown or duplicate identities, sequence and predecessor corruption, automatic execution, effective deferred holds, unsupported decisions, affected-set drift, status inheritance, automatic status or release action, repository mutation, and live activation.

## Validation

```bash
python3 scripts/generate_phase20_offline_manual_policy_resolution.py --check
python3 scripts/validate_phase20_offline_manual_policy_resolution.py
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

After Phase 20 integration, the next bounded gate is an **offline policy-resolution reconciliation candidate**. It may reconcile proposal identities, synthetic resolutions, ledger heads, and checkpoints, but it must not treat synthetic decisions as real authorization or activate status, release, network, or repository mutation.
