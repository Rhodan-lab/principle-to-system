# Principia & Atlas Offline Integration

This directory contains the Principia-side exact-revision bridge and bounded offline integration evidence for the future **Principia & Atlas** product.

It does not merge repositories, modify Atlas, or create a live cross-repository dependency.

## Contents

- `manifests/` — revision-specific Principia dependency manifests;
- `exports/` — deterministic importer candidates with legacy IDs and `depends_on_exact` records;
- `pilot/` — pinned Atlas importer evidence, receipts, lifecycle-impact matrices, receipt chains, event records, acknowledgements, and recovery scenarios;
- `fixtures/invalid/` — mutable-revision, status-inheritance, and live-dependency paths that must fail validation.

## Exact bridge boundary

All active manifests remain:

```yaml
mode: bridge-candidate
live: false
```

The delayed-feedback dependency set is:

```text
claim:en:model-oscillation-does-not-prove-real-system@1
concept:en:feedback@1
concept:en:oscillation@1
model:en:delayed-correction-recurrence@2
```

Only the feedback-instability failure pattern depends on the recurrence model. The refrigerator dossier and room-cooling investigation use the feedback, oscillation, and model-to-world claim boundaries without claiming dependence on that specific recurrence.

## Phase 15 — single-artifact pilot

Phase 15 pins the Atlas PR #20 importer implementation:

```text
Atlas tested head: 379d88d620469a749cebb88b0b41d9960e667558
Atlas merge commit: 1cc4aec6908a8703a7f505478329c633a23b4ef9
Atlas adapter: atlas-principia-bridge-adapter/0.1
Atlas operational record: atlas-external-dependent/0.1
```

Its state remains:

```yaml
state: offline-pilot-validated
mode: offline-pilot
live: false
```

Phase 15 artifacts:

- `pilot/atlas-phase2-importer.snapshot.json`;
- `pilot/feedback-instability.import-receipt.json`;
- `pilot/feedback-instability.lifecycle-matrix.json`.

## Phase 16 — offline multi-artifact pilot

Atlas PR #21 finalized the importer baseline record without changing importer behavior:

```text
Atlas PR #21 head:  c30bebf6a63263da8a4356f6c4dbc85f11a67bc4
Atlas PR #21 merge: 9370cc746e9756e433ac3772d56d079c9803b144
Atlas mode: importer-candidate
Atlas live: false
```

Phase 16 adds an atomic batch of three Principia artifacts:

```text
principia:failure-pattern:feedback-instability@1
principia:investigation:room-cooling@1
principia:system-dossier:refrigerator@1
```

Validated state:

```yaml
state: offline-multi-artifact-validated
mode: offline-multi-artifact-pilot
live: false
```

Phase 16 artifacts:

- `pilot/atlas-phase2-importer.snapshot.v02.json` — PR #20 implementation plus PR #21 governance finalization;
- `pilot/thermal-control.multi-artifact.batch.v02.json` — deterministic atomic input batch;
- `pilot/thermal-control.multi-artifact.receipt.v02.json` — three accepted operational records;
- `pilot/thermal-control.receipt-chain.v02.json` — sequence and predecessor-digest boundary;
- `pilot/thermal-control.lifecycle-matrix.v02.json` — mixed lifecycle fan-out;
- `pilot/thermal-control.recovery-matrix.v02.json` — replay, ordering, digest, atomicity, authority, and live-activation recovery cases.

The batch receipt uses `principia-atlas-offline-batch-receipt/0.2`. Duplicate replay is idempotent. A later receipt must use the next sequence and exact predecessor digest. Partial batches, corrupted digests, status inheritance, and `live: true` are rejected.

## Phase 17 — offline event-protocol candidate

Phase 17 binds a lifecycle event to the finalized Phase 16 checkpoint:

```text
Phase 16 PR #20 merge: c493bf879a7945f9991e13592d42424138a0879b
Phase 16 record PR #21 merge: 44410d47d318c5aaedb7716e4ef3bdefae09b442
Receipt-chain sequence: 1
Receipt-chain head: af529bc6c866be889e6a0b552dffedd81a5e46466cdae08e234472031617b562
```

Target state:

```yaml
state: offline-event-protocol-validated
mode: offline-event-protocol
live: false
```

The first event models `concept:en:feedback@1` as deprecated and reports `revalidate` for the exact three thermal-control artifacts. It does not alter their Principia-owned status.

Phase 17 contracts:

```text
principia-atlas-offline-lifecycle-event/0.3
principia-atlas-offline-event-ack/0.3
principia-atlas-offline-event-log/0.3
principia-atlas-offline-event-recovery/0.3
```

Phase 17 artifacts:

- `pilot/thermal-control.lifecycle-event.v03.json` — digest-bound Atlas lifecycle event snapshot;
- `pilot/thermal-control.lifecycle-event-ack.v03.json` — Principia acknowledgement of the exact event digest;
- `pilot/thermal-control.event-log.v03.json` — append-only sequence and predecessor boundary;
- `pilot/thermal-control.event-recovery-matrix.v03.json` — replay, equivocation, ordering, predecessor, authority, acknowledgement, and live-activation cases.

Exact duplicate replay is an idempotent no-op. A different event at the same sequence is rejected as equivocation. Stale, skipped, incorrectly linked, status-inheriting, mutating, or live events are rejected.

## Model boundary

The revision-2 recurrence produces a bounded exact period-6 orbit for its declared initial state. This establishes oscillation in the model, not instability and not real-system behaviour. Principia materials distinguish:

- designed or bounded cycling;
- decaying oscillation;
- sustained bounded oscillation;
- growing oscillation;
- mathematical instability;
- operational limit violation.

## Commands

Validate deterministic exports and earlier pilots:

```bash
python3 scripts/export_principia_atlas_dependents.py --check
python3 scripts/generate_phase15_offline_pilot.py --check
python3 scripts/validate_phase15_offline_pilot.py
python3 scripts/generate_phase16_offline_multi_artifact.py --check
python3 scripts/validate_phase16_offline_multi_artifact.py
python3 scripts/validate_phase16_postmerge_record.py
```

Validate Phase 17:

```bash
python3 scripts/finalize_phase17_state.py --check
python3 scripts/generate_phase17_offline_event_protocol.py --check
python3 scripts/validate_phase17_offline_event_protocol.py
python3 -m unittest software.tests.test_phase17_offline_event_protocol -v
```

Regenerate Phase 17 protocol outputs only during an explicit contract update:

```bash
python3 scripts/generate_phase17_offline_event_protocol.py --write
```

Run the complete Principia gate:

```bash
python3 scripts/validate_principia_atlas_bridge.py
python3 scripts/validate_principia_atlas_audit.py
python3 scripts/validate_repo.py --strict
python3 scripts/validate_phase12_release_candidate.py
python3 -m unittest discover -s software/tests -v
python3 scripts/validate_phase13_software.py
```

Permanent CI is read-only. It never writes, pushes, merges, imports Atlas dynamically, or changes status.

## Authority boundary

- Atlas owns knowledge identity, exact revisions, evidence, provenance, review level, lifecycle, and staleness.
- Principia owns pedagogy, artifact identity, artifact revision, and publication readiness.
- `status`, `release_status`, and Atlas knowledge status remain separate.
- Exports, receipts, events, and acknowledgements contain no inherited Principia status fields.
- Impact reports and lifecycle events do not automatically change status or release state.
- A later live bridge requires a different validated state; Phase 17 remains `live: false`.
