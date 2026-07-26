# Principia & Atlas Bridge Candidate

This directory contains the Principia-side, exact-revision candidate for the future **Principia & Atlas** product.

It does not modify Atlas and does not create a live cross-repository dependency.

## Contents

- `manifests/` — revision-specific Principia dependency manifests;
- `exports/` — deterministic importer candidates with legacy IDs and `depends_on_exact` records;
- `fixtures/invalid/` — mutable-revision, status-inheritance, and live-dependency paths that must fail validation.

## Current candidate

The candidate maps:

```text
Principia failure-pattern: Feedback Instability, artifact revision 1
```

to the following exact Atlas revisions:

```text
claim:en:model-oscillation-does-not-prove-real-system@1
model:en:delayed-correction-recurrence@2
concept:en:feedback@1
concept:en:oscillation@1
```

Only the delayed-correction model moved from revision 1 to revision 2. The other dependencies remain at revision 1.

The active state is:

```yaml
mode: bridge-candidate
live: false
```

The candidate is ready for a future Atlas Phase 2 read-only importer. It does not perform live calls, clone Atlas, synchronize repositories, or copy lifecycle status.

## Model boundary

The revision-2 recurrence produces a bounded exact period-6 orbit for its declared initial state. This establishes oscillation in the model, not instability and not real-system behaviour. Principia materials explicitly distinguish:

- designed or bounded cycling;
- decaying oscillation;
- sustained bounded oscillation;
- growing oscillation;
- mathematical instability;
- operational limit violation.

## Commands

Validate the complete bridge candidate:

```bash
python3 scripts/validate_principia_atlas_bridge.py
python3 scripts/validate_principia_atlas_audit.py
```

Check the deterministic export:

```bash
python3 scripts/export_principia_atlas_dependents.py --check
```

Regenerate the export during an explicit contract update:

```bash
python3 scripts/export_principia_atlas_dependents.py --write
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
- The export contains no status fields.
- A later live bridge requires a different validated state; this candidate remains `live: false`.
