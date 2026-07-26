# Principia & Atlas Offline Integration

This directory contains the Principia-side exact-revision bridge and the first validated offline end-to-end pilot for the future **Principia & Atlas** product.

It does not merge repositories, modify Atlas, or create a live cross-repository dependency.

## Contents

- `manifests/` — revision-specific Principia dependency manifests;
- `exports/` — deterministic importer candidates with legacy IDs and `depends_on_exact` records;
- `pilot/` — pinned Atlas importer evidence, deterministic receipt, and lifecycle-impact matrix;
- `fixtures/invalid/` — mutable-revision, status-inheritance, and live-dependency paths that must fail validation.

## Current bridge candidate

The candidate maps:

```text
principia:failure-pattern:feedback-instability@1
```

to:

```text
claim:en:model-oscillation-does-not-prove-real-system@1
concept:en:feedback@1
concept:en:oscillation@1
model:en:delayed-correction-recurrence@2
```

Only the delayed-correction model moved from revision 1 to revision 2. The other dependencies remain at revision 1.

```yaml
mode: bridge-candidate
live: false
```

## Phase 15 offline pilot

Atlas PR #20 merged a deterministic read-only adapter for `principia-atlas-external-dependent/0.2`.

Principia pins that importer evidence without calling or cloning Atlas:

```text
Atlas PR: 20
Atlas tested head: 379d88d620469a749cebb88b0b41d9960e667558
Atlas merge commit: 1cc4aec6908a8703a7f505478329c633a23b4ef9
Atlas adapter: atlas-principia-bridge-adapter/0.1
Atlas operational record: atlas-external-dependent/0.1
```

The offline pilot state is:

```yaml
state: offline-pilot-validated
mode: offline-pilot
live: false
```

Generated artifacts:

- `pilot/atlas-phase2-importer.snapshot.json` — immutable Atlas importer evidence and capability boundary;
- `pilot/feedback-instability.import-receipt.json` — accepted exact-revision receipt;
- `pilot/feedback-instability.lifecycle-matrix.json` — current, deprecated, stale, and retracted impact scenarios.

The Atlas `PROJECT_STATE.md` wording still labels PR #20 a candidate even though the PR is merged. The pilot records this as a non-blocking governance observation. It relies on the pinned merged PR, exact fixture, implementation, tests, and CI evidence—not on live access or mutable branch state.

## Model boundary

The revision-2 recurrence produces a bounded exact period-6 orbit for its declared initial state. This establishes oscillation in the model, not instability and not real-system behaviour. Principia materials distinguish:

- designed or bounded cycling;
- decaying oscillation;
- sustained bounded oscillation;
- growing oscillation;
- mathematical instability;
- operational limit violation.

## Commands

Validate the bridge candidate:

```bash
python3 scripts/export_principia_atlas_dependents.py --check
python3 scripts/validate_principia_atlas_bridge.py
python3 scripts/validate_principia_atlas_audit.py
```

Validate the offline pilot:

```bash
python3 scripts/generate_phase15_offline_pilot.py --check
python3 scripts/validate_phase15_offline_pilot.py
```

Regenerate pilot outputs only during an explicit contract change:

```bash
python3 scripts/generate_phase15_offline_pilot.py --write
```

Run the complete Principia gate:

```bash
python3 scripts/validate_repo.py --strict
python3 scripts/validate_phase12_release_candidate.py
python3 -m unittest discover -s software/tests -v
python3 scripts/validate_phase13_software.py
```

Permanent CI is read-only. It never writes, pushes, merges, imports Atlas, or changes status.

## Authority boundary

- Atlas owns knowledge identity, exact revisions, evidence, provenance, review level, lifecycle, and staleness.
- Principia owns pedagogy, artifact identity, artifact revision, and publication readiness.
- `status`, `release_status`, and Atlas knowledge status remain separate.
- The export and receipt contain no inherited status fields.
- Impact reports do not automatically change status or release state.
- A later live bridge requires a different validated state; Phase 15 remains `live: false`.
