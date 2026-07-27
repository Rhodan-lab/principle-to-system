# Phase 18 — Offline Reconciliation Simulation

> Date: 2026-07-27  
> Repository: `Rhodan-lab/principle-to-system`  
> Atlas repository modified: no  
> Candidate state: `offline-reconciliation-simulation-candidate`  
> Mode: `offline-reconciliation-simulation`  
> Live: `false`

## Purpose

Phase 17 established a bounded synthetic lifecycle-event stream, an acknowledgement stream, and exact digest chains. Phase 18 asks a different question: can Principia deterministically prove that every accepted event has the correct acknowledgement, action, artifact set, and still-current Principia artifact revision?

The reconciliation process is fully offline. It reads committed files in the Principia repository and does not clone, call, or modify Atlas.

## Official Phase 17 baseline

```text
Phase 17 exact candidate head: e260417ef7631ebf4f87c89faff7da45d571b63c
Phase 17 integration merge:    c9fba79f821d59b36030924e5c388f71a56f7787
Phase 17 finalization merge:   806b03335a1d0b43e5a32ffecce8439350564152
```

Pinned source files:

- `thermal-control.lifecycle-events.v01.json`;
- `thermal-control.lifecycle-acknowledgements.v01.json`;
- `thermal-control.event-protocol-chain.v01.json`;
- `release/phase-17-postmerge.json`;
- Phase 16 lifecycle-impact matrix for independent expected-action derivation.

## Reconciliation result

The official baseline produces:

```yaml
event_count: 2
acknowledgement_count: 2
reconciled_count: 2
unacknowledged_count: 0
orphan_acknowledgement_count: 0
stale_artifact_reference_count: 0
action_mismatch_count: 0
decision: reconciled-no-mutation
```

Event 1 reconciles the deprecated feedback concept with the exact `revalidate` acknowledgement. Event 2 reconciles the retracted model-to-world claim boundary with the exact `block-release` acknowledgement.

## Current Principia inventory

The acknowledgement references are compared with the live content state committed in the same Principia revision:

| Artifact | Acknowledged revision | Current revision | Pedagogical status | Release status |
| --- | ---: | ---: | --- | --- |
| `principia:failure-pattern:feedback-instability` | 1 | 1 | reviewed | draft |
| `principia:investigation:room-cooling` | 1 | 1 | reviewed | draft |
| `principia:system-dossier:refrigerator` | 1 | 1 | reviewed | draft |

The reconciliation report may observe these Principia-owned fields but may not inherit or change them from Atlas lifecycle data.

## Contracts

```text
principia-atlas-offline-reconciliation-report/0.1
principia-atlas-offline-reconciliation-checkpoint/0.1
principia-atlas-offline-reconciliation-recovery/0.1
principia-offline-reconciliation-simulation/0.1
```

## Checkpoint

The checkpoint pins:

- exact event and acknowledgement chain heads at sequence 2;
- exact reconciliation report digest;
- exact current-artifact inventory digest;
- next expected event sequence 3;
- next expected acknowledgement sequence 3;
- decision `reconciled-no-mutation`.

## Divergence simulation

The deterministic recovery matrix detects:

- missing acknowledgement;
- orphan acknowledgement;
- acknowledgement-to-event digest mismatch;
- weakened lifecycle action;
- incorrect affected-artifact set;
- stale Principia artifact revision;
- missing current Principia artifact;
- reordered event stream;
- reordered acknowledgement stream;
- event-chain head mismatch;
- acknowledgement-chain head mismatch;
- status-inheritance injection;
- automatic release mutation;
- attempted live activation.

The exact unmodified baseline is the only `reconciled` scenario. Every divergence produces a stable Phase 18 error code.

## Authority boundary

- Atlas owns knowledge identity, exact revision, lifecycle, review level, and staleness.
- Principia owns pedagogical status, artifact revision, and release status.
- Reconciliation reports actions but does not execute them.
- `status_inheritance` remains prohibited.
- `automatic_status_change` remains false.
- `automatic_release_action` remains false.
- `repository_mutation` remains false.
- `live` remains false.

## Validation

```bash
python3 scripts/generate_phase18_offline_reconciliation.py --check
python3 scripts/generate_phase18_release_record.py --check
python3 scripts/validate_phase18_offline_reconciliation.py
python3 -m unittest software.tests.test_phase18_offline_reconciliation -v
```

Permanent Phase 18 CI also runs Phase 17 post-merge validation, Phase 16 and Phase 15 validation, bridge and audit checks, strict repository and experience validation, release-candidate validation, all software tests, and Phase 13 software validation.

## Next bounded gate

After Phase 18 integration, the next bounded gate is an **offline reconciliation-policy candidate**. It may model how reconciliation findings become explicit Principia review queues or release holds, but it must not mutate content status or activate live synchronization automatically.
