# Phase 17 — Offline Event-Protocol Candidate

> Date: 2026-07-27  
> Repository: `Rhodan-lab/principle-to-system`  
> Atlas repository modified: no  
> Target state: `offline-event-protocol-validated`  
> Mode: `offline-event-protocol`  
> Live: `false`

## Purpose

Phase 16 proved that three exact Principia artifacts can be processed as one atomic offline batch with a deterministic receipt chain. Phase 17 adds the next bounded layer: a digest-bound lifecycle event, a Principia acknowledgement, an append-only event log, and deterministic replay, ordering, equivocation, and recovery behavior.

The protocol is not a network service. The committed event is generated from pinned Phase 16 and Atlas evidence. It does not claim that Atlas emitted a live message, and Principia CI never clones or calls Atlas.

## Source checkpoint

The first event is anchored to:

```text
Principia Phase 16 PR:          #20
Principia Phase 16 merge:       c493bf879a7945f9991e13592d42424138a0879b
Principia Phase 16 record PR:   #21
Principia Phase 16 record merge:44410d47d318c5aaedb7716e4ef3bdefae09b442
Phase 16 receipt-chain sequence:1
Phase 16 receipt-chain head:    af529bc6c866be889e6a0b552dffedd81a5e46466cdae08e234472031617b562
Atlas importer merge:           1cc4aec6908a8703a7f505478329c633a23b4ef9
Atlas governance merge:         9370cc746e9756e433ac3772d56d079c9803b144
```

The event also pins the exact SHA-256 of `release/phase-16-offline-multi-artifact-pilot.json`.

## Event

The first event models the validated Phase 16 scenario:

```text
concept:en:feedback@1
lifecycle_status: deprecated
staleness: current
```

The event reports three affected Principia artifacts:

- `principia:failure-pattern:feedback-instability@1`;
- `principia:investigation:room-cooling@1`;
- `principia:system-dossier:refrigerator@1`.

Each artifact retains its Principia-owned pedagogical and release status. The event reports `revalidate` as the effective action because Atlas lifecycle policy may escalate the declared `inspect` response for deprecated knowledge. No action is executed automatically.

## Contracts

```text
principia-atlas-offline-lifecycle-event/0.3
principia-atlas-offline-event-ack/0.3
principia-atlas-offline-event-log/0.3
principia-atlas-offline-event-recovery/0.3
```

The first event uses:

```yaml
sequence: 1
previous_event_sha256: null
mode: offline-event-protocol
live: false
```

Its acknowledgement pins the exact event digest, observed Atlas entity state, affected-artifact count, affected-artifact digest, and Phase 16 receipt-chain head.

## Append-only log

The event log stores:

- event sequence;
- predecessor digest;
- event path and SHA-256;
- acknowledgement path and SHA-256;
- acknowledgement decision;
- current event and acknowledgement heads.

A valid second event must use sequence 2 and the exact first-event digest as its predecessor.

## Recovery and rejection behavior

The canonical recovery matrix proves:

| Scenario | Result |
| --- | --- |
| Exact duplicate replay | Idempotent no-op |
| Same sequence, different digest | Reject as equivocation |
| Stale sequence | Reject |
| Skipped sequence | Reject |
| Wrong predecessor | Reject |
| Wrong Phase 16 receipt-chain head | Reject |
| Unknown Atlas entity lifecycle state | Reject |
| Affected-artifact mismatch | Reject |
| Principia status inheritance | Reject |
| Automatic release mutation | Reject |
| `live: true` | Reject |
| Correctly linked next event | Accept |
| Acknowledgement with wrong event digest | Reject |

Error codes are stable and recorded in `thermal-control.event-recovery-matrix.v03.json`.

## Authority boundary

- Atlas remains authority for knowledge identity, exact revision, lifecycle status, and staleness.
- Principia remains authority for pedagogical status, artifact revision, and release status.
- The event may report an effective action but cannot execute it.
- `status_inheritance` remains prohibited.
- `automatic_status_change` remains false.
- `automatic_release_action` remains false.
- `repository_mutation` remains false.
- `live` remains false.

## Validation

```bash
python3 scripts/generate_phase17_offline_event_protocol.py --check
python3 scripts/validate_phase17_offline_event_protocol.py
python3 -m unittest software.tests.test_phase17_offline_event_protocol -v
```

Permanent Phase 17 CI also runs Phase 16 post-merge validation, all earlier bridge and integration gates, strict repository validation, release-candidate validation, complete software tests, and Phase 13 software validation.

## Next bounded gate

After Phase 17 integration, the next candidate is **offline event-stream scaling**: several ordered lifecycle events, checkpoint compaction, bounded retention, and recovery across longer chains. It remains offline. Live integration requires a separate contract and explicit machine gates.
