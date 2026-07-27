# Phase 17 — Offline Event-Protocol Candidate

> Date: 2026-07-27  
> Repository: `Rhodan-lab/principle-to-system`  
> Atlas repository modified: no  
> State: `offline-event-protocol-validated`  
> Mode: `offline-event-protocol`  
> Live: `false`  
> Pull request: #22  
> Exact tested head: `e260417ef7631ebf4f87c89faff7da45d571b63c`  
> Merge commit: `c9fba79f821d59b36030924e5c388f71a56f7787`

## Purpose

Phase 16 proved that three exact Principia artifacts can be admitted as one deterministic offline batch with a receipt chain and lifecycle-impact policy. Phase 17 tests the next bounded problem: how Atlas lifecycle changes can be represented as digest-bound events and how Principia can acknowledge them without activating synchronization or transferring status authority.

No network synchronization, Atlas checkout, service call, webhook, repository mutation, status inheritance, automatic release action, or live dependency is introduced.

## Pinned foundation

Phase 17 starts from the merged and finalized Phase 16 state:

```text
Principia Phase 16 finalization merge:
44410d47d318c5aaedb7716e4ef3bdefae09b442

Phase 16 source receipt:
integration/principia-atlas/pilot/thermal-control.multi-artifact.receipt.v02.json
SHA-256:
af529bc6c866be889e6a0b552dffedd81a5e46466cdae08e234472031617b562
```

The Atlas baseline remains exactly:

```yaml
repository: Rhodan-lab/Atlas
implementation_merge_commit: 1cc4aec6908a8703a7f505478329c633a23b4ef9
governance_merge_commit: 9370cc746e9756e433ac3772d56d079c9803b144
mode: importer-candidate
live: false
```

## Contracts

```text
principia-atlas-offline-lifecycle-event/0.1
principia-atlas-offline-lifecycle-event-stream/0.1
principia-atlas-offline-lifecycle-acknowledgement/0.1
principia-atlas-offline-lifecycle-acknowledgement-stream/0.1
principia-atlas-offline-event-protocol-chain/0.1
principia-atlas-offline-event-protocol-recovery/0.1
principia-offline-event-protocol-finalization/0.1
```

Every event is explicitly `bounded-synthetic`. The fixtures model protocol behavior only; they do not assert that Atlas actually deprecated or retracted a canonical entity.

## Event stream

Two exact, ordered lifecycle fixtures are committed:

1. `concept:en:feedback@1`: `current → deprecated`;
2. `claim:en:model-oscillation-does-not-prove-real-system@1`: `current → retracted`.

The first event has sequence 1 and no predecessor. The second event has sequence 2 and names the exact SHA-256 digest of the first event. Each event pins the accepted Atlas importer baseline and remains:

```yaml
mode: offline-event-protocol
live: false
fixture_kind: bounded-synthetic
```

## Principia acknowledgements

Principia records one deterministic acknowledgement per event.

- Deprecated feedback concept → `revalidate` all three thermal-control artifacts.
- Retracted model-boundary claim → `block-release` all three thermal-control artifacts.

The acknowledgement means only that the required response was recorded. It does not change pedagogical status, release status, Atlas lifecycle, repository contents, or publication state.

```yaml
outcome: recorded-no-mutation
status_inheritance: prohibited
automatic_status_change: false
automatic_release_action: false
repository_mutation: false
```

## Ordered chain

The event and acknowledgement chains independently enforce:

- monotonically increasing sequence;
- exact predecessor digest;
- exact event-to-acknowledgement binding;
- deterministic SHA-256 calculation;
- one acknowledgement for each accepted event;
- separate event and acknowledgement heads.

The protocol does not use clocks, mutable aliases, `latest` references, network delivery, or hidden runtime state.

## Replay and recovery

The recovery matrix covers:

- duplicate event replay → idempotent no-op;
- stale or skipped sequence → reject;
- wrong predecessor digest → reject;
- event digest corruption → reject;
- unknown exact subject revision → reject;
- status-inheritance injection → reject;
- `live: true` → reject;
- correctly linked next event → accept as a recovery checkpoint;
- acknowledgement bound to the wrong event → reject;
- acknowledgement out of order → reject;
- acknowledgement that weakens `block-release` to `inspect` → reject.

The recovery matrix is evidence about deterministic protocol handling, not a live queue or synchronization service.

## Authority boundary

- Atlas remains the authority for canonical knowledge lifecycle.
- Principia remains the authority for pedagogical status, artifact revision, and release status.
- Lifecycle events can request inspection, revalidation, or blocking.
- Acknowledgements can record the required response.
- Neither side automatically mutates the other.
- No event promotes, completes, releases, deprecates, or retracts content by itself.
- `live: false` remains mandatory.

## Deterministic validation

```bash
python3 scripts/validate_phase16_postmerge_record.py
python3 scripts/generate_phase17_offline_event_protocol.py --check
python3 scripts/validate_phase17_offline_event_protocol.py
python3 scripts/validate_phase17_postmerge_record.py
python3 -m unittest software.tests.test_phase17_offline_event_protocol -v
```

The permanent Phase 17 workflow also executes the complete inherited Phase 15–16, bridge, strict repository, release-candidate, and software validation chain. It uses `contents: read` and uploads complete diagnostics.

## Validation result

All 13 applicable workflows passed together on exact candidate head `e260417ef7631ebf4f87c89faff7da45d571b63c`.

PR #22 was merged into `main` at `c9fba79f821d59b36030924e5c388f71a56f7787`. The immutable candidate record remains at `release/phase-17-offline-event-protocol.json`; merged provenance is pinned separately in `release/phase-17-postmerge.json`.

Phase 17 is therefore integrated as `offline-event-protocol-validated`. It still does not activate synchronization or transfer authority between repositories.

The next bounded gate is the offline reconciliation simulation candidate. It must remain deterministic, repository-separate, and `live: false`; any live bridge requires a distinct future contract transition.
