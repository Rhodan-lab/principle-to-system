# Principia–Atlas Bridge Contract 0.1

## Purpose

`principia-atlas-bridge/0.1` lets Principia declare exact-revision Atlas dependencies while preserving repository independence and separate authority.

The bridge is one-way and offline:

- Principia authors a revision-specific dependency manifest.
- A deterministic exporter produces an importer candidate with legacy dependency IDs and exact dependency objects.
- Atlas Phase 2 importer work may later ingest and validate that committed export through Atlas's own process.
- Principia never imports Atlas source files, review records, lifecycle status, or runtime state during validation.
- Atlas remains independently buildable and is not modified by this contract update.

The active manifest uses:

```yaml
mode: bridge-candidate
live: false
```

`bridge-candidate` means the record is revision-pinned and importer-ready on the Principia side. It does not activate a network call, synchronization process, status transfer, or live dependency. **No live cross-repository call is permitted by this state.**

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

- Atlas review status does not make a Principia artifact pedagogically reviewed or released.
- Principia `reviewed` does not change any Atlas entity's knowledge lifecycle.
- Principia software or bridge validation does not promote pedagogical or publication state.
- Atlas importer acceptance, when implemented, will remain an Atlas decision.

## Principia artifact identity

A bridgeable Principia artifact requires independent fields:

```yaml
slug: failure-pattern-feedback-instability
status: reviewed
artifact_revision: 1
release_status: draft
```

`status` is pedagogical maturity. `release_status` is publication readiness. `artifact_revision` changes only when dependency-relevant Principia meaning changes. Clarifying an already-declared model boundary without changing the principal conclusion does not require an artifact revision increment.

The exported external ID is stable:

```text
principia:failure-pattern:feedback-instability
```

## Exact Atlas dependency references

Every Atlas dependency uses one exact positive integer revision. The current model reference is:

```json
{
  "id": "model:en:delayed-correction-recurrence",
  "revision": 2,
  "entity_type": "model",
  "role": "supporting",
  "use": "model-boundary",
  "change_policy": "inspect"
}
```

The other delayed-feedback dependencies remain pinned to revision 1.

Forbidden forms include:

- `revision: "latest"`;
- unversioned entity references;
- copied Atlas lifecycle status used as a Principia gate;
- automatic pedagogical or release promotion;
- direct repository imports;
- live calls while `live: false`.

## Dependency roles and uses

- `load-bearing` — changing or invalidating the Atlas entity could change the artifact's principal explanation or conclusion.
- `supporting` — materially useful but replaceable without changing the principal conclusion.
- `context` — navigation or interpretation rather than authority.

Allowed `use` values are `definition`, `evidence`, `claim-boundary`, `model`, `model-boundary`, `source-context`, and `synthesis-context`.

## Change policies

- `inspect` — inspect a changed exact revision and record whether the Principia artifact can adopt it unchanged.
- `revalidate` — rerun the bounded Principia material checks.
- `block-release` — prevent release-status promotion until a load-bearing incompatibility is resolved.

These policies affect Principia workflow only. They do not change Atlas lifecycle state.

## Candidate export

The exporter emits `principia-atlas-external-dependent/0.2`:

```json
{
  "contract": "principia-atlas-external-dependent/0.2",
  "id": "principia:failure-pattern:feedback-instability",
  "revision": 1,
  "bridge_mode": "bridge-candidate",
  "live": false,
  "depends_on": [
    "claim:en:model-oscillation-does-not-prove-real-system",
    "model:en:delayed-correction-recurrence"
  ],
  "depends_on_exact": [
    {
      "id": "model:en:delayed-correction-recurrence",
      "revision": 2,
      "role": "supporting",
      "use": "model-boundary",
      "change_policy": "inspect"
    }
  ]
}
```

`depends_on` preserves the existing opaque ID coverage shape. `depends_on_exact` is the Phase 2 importer candidate surface for exact-revision lookup and dependency-impact queries.

The export contains no Atlas knowledge status and no Principia pedagogical or release status.

## Oscillation and instability boundary

The revision-2 recurrence proves a bounded exact period-6 orbit for its declared initial state. It demonstrates oscillation. It does not prove instability, does not show that delay always causes instability, and does not establish real-system behaviour. Principia retains the load-bearing claim boundary that model oscillation does not prove a real system.

## Promotion boundary

The candidate is ready for an Atlas Phase 2 importer test, but remains non-live:

1. Atlas may import the committed candidate through a read-only, exact-revision process.
2. Atlas may reject it without changing Principia status.
3. Neither repository imports the other's status.
4. Revision, staleness, deprecation, retraction, and recovery behaviour remain testable.
5. Live calls require a later contract and `live: true` transition that is not part of this candidate.
