# Principia–Atlas Bridge Contract 0.1

## Purpose

`principia-atlas-bridge/0.1` prepares Principia artifacts to participate in a future **Principia & Atlas** product while preserving repository independence and separate authority.

The bridge is deliberately one-way and offline:

- Principia authors a revision-specific dependency manifest.
- A deterministic exporter can produce the opaque `external_dependents` shape already accepted by Atlas coverage reporting.
- Atlas may later ingest that export through its own reviewed process.
- Principia never imports Atlas source files, review records, or lifecycle decisions during validation.
- Atlas remains able to validate itself without cloning or reading Principia.

During Atlas Phase 1, every Principia bridge manifest must use `mode: compatibility-fixture` and `live: false`. A fixture proves contract compatibility; it is not a live knowledge dependency.

## Ownership boundary

| Concern | Owner |
| --- | --- |
| Scientific knowledge identity, evidence, provenance, exact revision, review, lifecycle, staleness | Atlas |
| Causal explanation, pedagogy, pathways, system dossiers, failure patterns, investigations, design challenges | Principia |
| Principia pedagogical maturity | Principia `status` field |
| Principia publication readiness | Principia `release_status` field |
| Principia artifact identity | Principia `slug` plus `artifact_revision` |
| Atlas knowledge status | Atlas only |

No status crosses the boundary automatically.

- Atlas `reviewed` does not make a Principia artifact pedagogically reviewed or released.
- Principia `reviewed` does not make any Atlas entity scientifically reviewed.
- A validator pass establishes only structural conformance.
- AI-generated analysis cannot grant scientific, editorial, legal, ethical, methodological, translation, or release authority.

## Principia artifact identity

A bridgeable Principia artifact requires:

```yaml
slug: failure-pattern-feedback-instability
status: reviewed
artifact_revision: 1
release_status: draft
```

`status` is pedagogical maturity under Principia governance. `release_status` is publication readiness. `artifact_revision` is a positive integer that changes whenever dependency-relevant meaning changes.

The exported external ID is namespaced and stable:

```text
principia:failure-pattern:feedback-instability
```

Renaming a file path does not change the ID. Changing the artifact's dependency-relevant meaning requires a new `artifact_revision`.

## Atlas dependency reference

Every Atlas dependency is exact-revision:

```json
{
  "id": "model:en:delayed-correction-recurrence",
  "revision": 1,
  "entity_type": "model",
  "role": "supporting",
  "use": "model-boundary",
  "change_policy": "inspect"
}
```

Forbidden forms include:

- `revision: "latest"`;
- unversioned entity references;
- copied Atlas lifecycle status used as a Principia gate;
- automatic release or pedagogical promotion;
- direct repository imports;
- a live dependency while Atlas Phase 1 keeps direct integration frozen.

## Dependency roles

- `load-bearing` — changing or invalidating the Atlas entity could change the artifact's principal explanation, model, requirement, or conclusion.
- `supporting` — materially useful but replaceable without changing the principal conclusion.
- `context` — navigation or interpretation rather than authority.

Roles are local to the Principia artifact manifest. They do not modify Atlas entities.

## Uses

Allowed `use` values are:

- `definition`;
- `evidence`;
- `claim-boundary`;
- `model`;
- `model-boundary`;
- `source-context`;
- `synthesis-context`.

## Change policies

- `inspect` — flag the artifact for inspection after an Atlas revision, deprecation, or retraction.
- `revalidate` — rerun the bounded Principia review before release.
- `block-release` — a pending or incompatible change blocks release-status promotion until resolved.

These policies affect Principia workflow only. They do not ask Atlas to change lifecycle state.

## Export format

The exporter emits the exact opaque reference shape documented by Atlas:

```json
{
  "id": "principia:failure-pattern:feedback-instability",
  "kind": "principia-artifact",
  "repository": "Rhodan-lab/principle-to-system",
  "revision": 1,
  "role": "load-bearing",
  "depends_on": [
    "claim:en:model-oscillation-does-not-prove-real-system",
    "model:en:delayed-correction-recurrence"
  ]
}
```

The export contains no Principia pedagogical or release status because Atlas must not validate or inherit those states.

## Current fixture

`integration/principia-atlas/manifests/feedback-instability.fixture.json` maps the existing Principia failure-pattern artifact to exact Atlas delayed-feedback entities. It is intentionally non-live. Its generated export is stored beside it for deterministic comparison.

## Promotion boundary

A future live bridge requires separate approval in both repositories:

1. Atlas exits the phase that freezes direct integration.
2. Principia approves a live manifest through its own review.
3. Atlas accepts the external dependent through its own contract and governance.
4. Neither repository imports the other's status.
5. Revision, staleness, deprecation, and retraction behavior are tested end to end.

Until then, bridge work remains compatibility preparation only.
