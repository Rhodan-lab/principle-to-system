# Principia & Atlas Offline Integration

This directory contains the Principia-side exact-revision bridge and bounded offline integration evidence for the future **Principia & Atlas** product.

It does not merge repositories, modify Atlas, or create a live cross-repository dependency.

## Contents

- `manifests/` — revision-specific Principia dependency manifests;
- `exports/` — deterministic importer candidates with legacy IDs and `depends_on_exact` records;
- `pilot/` — pinned Atlas importer evidence, receipts, lifecycle-impact matrices, receipt chains, and recovery scenarios;
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
tested_head: 67d6ec98c51188dabcffd48dad968a83653ea584
```

Phase 16 artifacts:

- `pilot/atlas-phase2-importer.snapshot.v02.json` — PR #20 implementation plus PR #21 governance finalization;
- `pilot/thermal-control.multi-artifact.batch.v02.json` — deterministic atomic input batch;
- `pilot/thermal-control.multi-artifact.receipt.v02.json` — three accepted operational records;
- `pilot/thermal-control.receipt-chain.v02.json` — sequence and predecessor-digest boundary;
- `pilot/thermal-control.lifecycle-matrix.v02.json` — mixed lifecycle fan-out;
- `pilot/thermal-control.recovery-matrix.v02.json` — replay, ordering, digest, atomicity, authority, and live-activation recovery cases.

The batch receipt uses `principia-atlas-offline-batch-receipt/0.2`. Duplicate replay is idempotent. A later receipt must use the next sequence and exact predecessor digest. Partial batches, corrupted digests, status inheritance, and `live: true` are rejected.

## Model boundary

The revision-2 recurrence produces a bounded exact period-6 orbit for its declared initial state. This establishes oscillation in the model, not instability and not real-system behaviour. Principia materials distinguish:

- designed or bounded cycling;
- decaying oscillation;
- sustained bounded oscillation;
- growing oscillation;
- mathematical instability;
- operational limit violation.

## Commands

Validate all deterministic exports:

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
```

Validate Phase 15 and Phase 16:

```bash
python3 scripts/generate_phase15_offline_pilot.py --check
python3 scripts/validate_phase15_offline_pilot.py
python3 scripts/generate_phase16_offline_multi_artifact.py --check
python3 scripts/validate_phase16_offline_multi_artifact.py
```

Regenerate Phase 16 outputs only during an explicit contract update:

```bash
python3 scripts/generate_phase16_offline_multi_artifact.py --write
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
- Exports and receipts contain no inherited status fields.
- Impact reports do not automatically change status or release state.
- A later live bridge requires a different validated state; Phase 16 remains `live: false`.
