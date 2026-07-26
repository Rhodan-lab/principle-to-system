# Principia & Atlas Compatibility Fixtures

This directory contains Principia-side compatibility preparation for the future **Principia & Atlas** product.

It does not create a live cross-repository dependency.

## Contents

- `manifests/` — revision-specific Principia artifact dependency manifests;
- `exports/` — deterministic opaque external-dependent records compatible with Atlas coverage reporting;
- `fixtures/invalid/` — dishonest or unsafe integration paths that must fail validation.

## Current pilot

The first fixture maps:

```text
Principia failure-pattern: Feedback Instability, revision 1
```

to exact-revision Atlas delayed-feedback entities. The referenced Atlas entities remain governed entirely by Atlas. Their lifecycle state is not copied into Principia.

The fixture is explicitly:

```json
{
  "mode": "compatibility-fixture",
  "live": false
}
```

## Commands

Validate the complete compatibility foundation:

```bash
python3 scripts/validate_principia_atlas_bridge.py
```

Check the deterministic external-dependent export:

```bash
python3 scripts/export_principia_atlas_dependents.py --check
```

Regenerate the export during an explicitly reviewed contract update:

```bash
python3 scripts/export_principia_atlas_dependents.py --write
```

The permanent CI workflow is read-only and uses `--check`; it never writes, pushes, imports Atlas, or changes status.

## Boundary

- Principia owns the artifact, pedagogical maturity, and release readiness.
- Atlas owns knowledge entities, evidence, provenance, review, lifecycle, and staleness.
- Exports contain no Principia status fields.
- A future live bridge requires approval and validation in both repositories.
