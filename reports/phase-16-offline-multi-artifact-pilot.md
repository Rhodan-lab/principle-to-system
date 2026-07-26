# Phase 16 — Offline Multi-Artifact Integration Pilot

> Date: 2026-07-26  
> Repository: `Rhodan-lab/principle-to-system`  
> Atlas repository modified: no  
> State: `offline-multi-artifact-validated`  
> Mode: `offline-multi-artifact-pilot`  
> Live: `false`  
> Pull request: #20  
> Candidate head: `67d6ec98c51188dabcffd48dad968a83653ea584`  
> Final tested head: `d37674490f054241ef08ccf7a644247b444fa874`  
> Merge commit: `c493bf879a7945f9991e13592d42424138a0879b`

## Purpose

Phase 15 proved one exact Principia external dependent could be processed against a pinned Atlas importer and represented by a deterministic receipt. Phase 16 tests the next bounded problem: several Principia artifacts in one atomic offline batch, a versioned receipt chain, lifecycle impact across several dependents, and deterministic recovery after replay, ordering, digest, or authority failures.

No live cross-repository call is made. Principia CI does not clone Atlas, invoke an Atlas service, synchronize repositories, or mutate either repository.

## Exact artifacts

The pilot covers three reviewed, unreleased Principia artifacts from the thermal-control route:

| Artifact | Revision | Role | Atlas dependencies |
| --- | ---: | --- | ---: |
| `principia:failure-pattern:feedback-instability` | 1 | load-bearing | 4 |
| `principia:investigation:room-cooling` | 1 | supporting | 3 |
| `principia:system-dossier:refrigerator` | 1 | load-bearing | 3 |

All three retain:

```yaml
status: reviewed
artifact_revision: 1
release_status: draft
```

Those fields remain Principia authority and are intentionally absent from the exports and Atlas operational records.

## Atlas baseline

The offline snapshot pins two separate Atlas facts:

1. importer implementation merged through Atlas PR #20;
2. importer governance baseline finalized through Atlas PR #21.

Exact pins:

```text
Atlas PR #20 tested head: 379d88d620469a749cebb88b0b41d9960e667558
Atlas PR #20 merge:       1cc4aec6908a8703a7f505478329c633a23b4ef9
Atlas PR #21 head:        c30bebf6a63263da8a4356f6c4dbc85f11a67bc4
Atlas PR #21 merge:       9370cc746e9756e433ac3772d56d079c9803b144
```

The active pinned Atlas state is `importer-candidate`, `live: false`.

## Contracts

```text
principia-atlas-external-dependent/0.2
principia-atlas-offline-import-batch/0.2
principia-atlas-offline-batch-receipt/0.2
principia-atlas-offline-receipt-chain/0.2
principia-atlas-offline-multi-impact-matrix/0.2
principia-atlas-offline-recovery-matrix/0.2
```

The batch is atomic. Either all three exact exports are represented in the receipt or the batch is rejected.

## Receipt versioning

The first receipt uses:

```yaml
sequence: 1
previous_receipt_sha256: null
```

The committed receipt digest becomes the head of `principia-atlas-offline-receipt-chain/0.2`. A later receipt must use sequence 2 and name the exact predecessor digest. Duplicate replay of the same sequence and batch is an idempotent no-op; stale, skipped, or incorrectly linked receipts are rejected.

## Lifecycle impact

Phase 16 distinguishes dependency fan-out instead of assuming every Atlas entity affects every Principia artifact.

- The recurrence model revision 2 is used only by the feedback-instability failure pattern.
- The feedback and oscillation concepts are used by all three artifacts.
- The model-to-world claim boundary is load-bearing for all three artifacts.

The mixed matrix proves:

```text
current claim                 → block-release remains declared for 3 artifacts
deprecated feedback concept   → revalidate 3 artifacts
confirmed-stale oscillation   → revalidate 3 artifacts
current recurrence model      → inspect 1 artifact
retracted recurrence model    → block-release 1 artifact
retracted claim boundary      → block-release 3 artifacts
```

Atlas may escalate a declared response but may not weaken it. Reports do not execute the response automatically.

## Recovery scenarios

The deterministic recovery matrix includes:

- duplicate replay;
- stale sequence;
- skipped sequence;
- wrong predecessor digest;
- valid next checkpoint;
- partial atomic batch;
- export or batch digest corruption;
- status-inheritance injection;
- attempted live activation.

Only duplicate replay and a correctly linked next checkpoint are accepted. All other scenarios fail with stable error codes.

## Authority boundary

- Atlas owns knowledge identity, exact revisions, evidence, review level, lifecycle, and staleness.
- Principia owns pedagogical status, artifact revision, and release status.
- `status_inheritance` remains `prohibited`.
- `automatic_status_change` remains `false`.
- `automatic_release_action` remains `false`.
- `repository_mutation` remains `false`.
- `live` remains `false`.

## Deterministic validation

```bash
python3 scripts/export_principia_atlas_dependents.py --check
python3 scripts/export_principia_atlas_dependents.py \
  --manifest integration/principia-atlas/manifests/refrigerator.fixture.json \
  --output integration/principia-atlas/exports/refrigerator.external-dependent.fixture.json \
  --check
python3 scripts/export_principia_atlas_dependents.py \
  --manifest integration/principia-atlas/manifests/room-cooling.fixture.json \
  --output integration/principia-atlas/exports/room-cooling.external-dependent.fixture.json \
  --check
python3 scripts/generate_phase16_offline_multi_artifact.py --check
python3 scripts/validate_phase16_offline_multi_artifact.py
python3 scripts/validate_phase16_postmerge_record.py
python3 -m unittest software.tests.test_phase16_offline_multi_artifact -v
```

The permanent workflow also runs Phase 15 post-merge validation, bridge and audit checks, strict repository validation, release-candidate validation, all software tests, and the Phase 13 software validator.

## Validation result

The final tested head `d37674490f054241ef08ccf7a644247b444fa874` passed every applicable workflow together:

- Phase 5 Sources;
- Phase 6 Foundations;
- Phase 7 Physical Science;
- Phase 8 Life and Earth Systems;
- Phase 9 Technology;
- Phase 10 Synthesis;
- Phase 11B Expansion;
- Principia–Atlas Compatibility;
- Phase 12 Release Candidate;
- Phase 13 Software Foundation;
- Phase 15 Offline Pilot;
- Phase 16 Offline Multi-Artifact.

PR #20 was merged into `main` at `c493bf879a7945f9991e13592d42424138a0879b`. Phase 16 is therefore integrated and remains `offline-multi-artifact-validated`.

Live activation is not part of Phase 16. The next bounded gate is the offline event-protocol candidate, which must remain digest-bound, repository-separate, and `live: false`.
