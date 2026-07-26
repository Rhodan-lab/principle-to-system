# Phase 15 — Offline Integration Pilot

> Date: 2026-07-26  
> Principia repository: `Rhodan-lab/principle-to-system`  
> Atlas repository: `Rhodan-lab/Atlas`  
> Pilot state: `offline-pilot-validated`  
> Live integration: disabled

## Purpose

Phase 15 proves one bounded end-to-end Principia–Atlas dependency path without merging repositories, cloning Atlas in Principia CI, calling either repository at runtime, or inheriting lifecycle status.

The pilot covers:

```text
Principia deterministic export
→ pinned Atlas Phase 2 importer snapshot
→ deterministic offline import receipt
→ Principia receipt verification
→ lifecycle-impact scenario matrix
→ machine-only end-to-end validation
```

## Pinned inputs

### Principia

- artifact: `principia:failure-pattern:feedback-instability@1`;
- export contract: `principia-atlas-external-dependent/0.2`;
- export SHA-256: `6d9d232007b5ecc18c6470f5c2e457decfcae1a5be99764be9796b4b24db7047`;
- bridge state: `bridge-candidate`;
- live: `false`.

Exact Atlas dependencies:

```text
claim:en:model-oscillation-does-not-prove-real-system@1
concept:en:feedback@1
concept:en:oscillation@1
model:en:delayed-correction-recurrence@2
```

### Atlas

- importer PR: `Rhodan-lab/Atlas#20`;
- tested head: `379d88d620469a749cebb88b0b41d9960e667558`;
- merge commit: `1cc4aec6908a8703a7f505478329c633a23b4ef9`;
- accepted wire contract: `principia-atlas-external-dependent/0.2`;
- adapter contract: `atlas-principia-bridge-adapter/0.1`;
- operational record: `atlas-external-dependent/0.1`;
- lifecycle report: `atlas-lifecycle-impact-report/0.1`;
- live: `false`.

Atlas PR #20 passed Phase 2 Knowledge Kernel, Phase 1 AI Review, Foundation Contract, and Atlas CI. Principia does not rerun Atlas code. It pins the accepted importer evidence and verifies its own receipt deterministically.

## Receipt

`integration/principia-atlas/pilot/feedback-instability.import-receipt.json` uses:

```text
principia-atlas-offline-import-receipt/0.1
```

It records:

- exact Principia input identity and digest;
- exact Atlas importer PR, head, and merge commit;
- all four exact dependency resolutions;
- Atlas operational and adapter contracts;
- verified legacy-ID/exact-dependency alignment;
- `status_inheritance: prohibited`;
- no repository mutation;
- no automatic status change;
- no automatic release action;
- `live: false`.

## Lifecycle scenarios

The model dependency is exercised through five offline scenarios:

| Atlas state | Staleness | Declared | Effective |
| --- | --- | --- | --- |
| current | current | inspect | inspect |
| deprecated | current | inspect | revalidate |
| draft | review-required | inspect | revalidate |
| draft | confirmed-stale | inspect | revalidate |
| retracted | current | inspect | block-release |

These are impact decisions, not automatic actions. Atlas knowledge status remains Atlas-owned. Principia pedagogical status and release status remain Principia-owned.

## Negative paths

Tests reject:

- `live: true`;
- imported pedagogical or release status;
- model revision rollback from 2 to 1;
- an unpinned Atlas merge reference;
- automatic status mutation;
- stale generated receipt or lifecycle matrix.

## Atlas governance observation

Atlas implementation, pinned fixture, tests, PR #20 merge, and exact-head CI are consistent. Atlas `PROJECT_STATE.md` still calls PR #20 a candidate and lists its merge as a next action. This wording is stale but does not alter the merged importer contract or test evidence. The observation is recorded as non-blocking and must not be presented as evidence of live activation.

## Safety and authority boundary

No live cross-repository call occurs in Phase 15.

- Principia CI does not clone Atlas.
- Principia CI does not download Atlas content.
- Atlas is not modified by this phase.
- The repositories remain independently buildable.
- Knowledge, pedagogical, and release statuses remain separate.
- No workflow writes, pushes, merges, publishes, or changes lifecycle state.

## Validation

```bash
python3 scripts/generate_phase15_offline_pilot.py --check
python3 scripts/validate_phase15_offline_pilot.py
python3 scripts/export_principia_atlas_dependents.py --check
python3 scripts/validate_principia_atlas_bridge.py
python3 scripts/validate_principia_atlas_audit.py
python3 scripts/validate_repo.py --strict
python3 scripts/validate_phase12_release_candidate.py
python3 -m unittest discover -s software/tests -v
python3 scripts/validate_phase13_software.py
```

## Result

Phase 15 establishes a validated offline integration path for one exact-revision artifact. It does not establish synchronization, scale, multiple external dependents, recovery from remote outages, authentication, or live operation.

The next legitimate step is a broader offline multi-artifact pilot and receipt-versioning contract. Live integration remains a separate future transition and stays disabled.
