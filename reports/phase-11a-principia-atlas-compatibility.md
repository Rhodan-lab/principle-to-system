# Phase 11A — Principia & Atlas Compatibility Foundation

> Date: 2026-07-26  
> Principia repository: `Rhodan-lab/principle-to-system`  
> Atlas repository inspected read-only: `Rhodan-lab/Atlas`  
> Integration mode: compatibility preparation only  
> Live dependency: prohibited during this phase

## Purpose

Phase 11A prepares the Principia repository for a future combined **Principia & Atlas** product without merging repositories, importing Atlas content, or conflating authority.

Atlas already supports optional opaque `external_dependents` in `atlas-review-coverage/0.1`. Principia previously lacked:

- stable artifact revisions for external dependency reporting;
- a separate publication-readiness status;
- a machine-readable Atlas dependency manifest;
- a deterministic exporter to Atlas's opaque reference shape;
- invalid fixtures proving that status inheritance and mutable revisions fail;
- a read-only compatibility gate.

## Repository boundary preserved

Atlas remains unchanged.

- Atlas owns source, evidence, claim, concept, model, synthesis, provenance, exact revision, review, lifecycle, staleness, translation lineage, and promotion governance.
- Principia owns causal explanation, pedagogy, pathways, systems, failure analysis, investigations, and design experiences.
- Atlas does not validate Principia pedagogical or release status.
- Principia does not inherit Atlas knowledge status.
- No validator pass creates scientific or release authority.

## Principia artifact metadata

The four seed experience artifacts and all four templates now include:

```yaml
artifact_revision: 1
release_status: draft
```

The existing `status` field remains the Principia pedagogical status. `release_status` is independent publication readiness. `artifact_revision` is the exact revision exposed to a future Atlas external-dependent record.

## Bridge contract

`contracts/principia-atlas/0.1/` defines `principia-atlas-bridge/0.1`.

It requires:

- exact Principia artifact ID and revision;
- exact Atlas entity IDs and revisions;
- dependency role, use, and change policy;
- explicit prohibition of status inheritance;
- Principia-only and Atlas-only authority declarations;
- non-live fixture mode during Atlas Phase 1;
- an export that omits pedagogical, release, and knowledge status.

## Pilot fixture

The first non-live fixture connects the Principia artifact:

```text
principia:failure-pattern:feedback-instability@1
```

to exact revision-1 Atlas delayed-feedback entities:

- `claim:en:model-oscillation-does-not-prove-real-system`;
- `model:en:delayed-correction-recurrence`;
- `concept:en:feedback`;
- `concept:en:oscillation`.

The fixture does not assert that those Atlas entities are reviewed. It records dependency shape only.

## Deterministic Atlas export

The generated export matches the opaque external-dependent structure documented by Atlas:

```json
{
  "id": "principia:failure-pattern:feedback-instability",
  "kind": "principia-artifact",
  "repository": "Rhodan-lab/principle-to-system",
  "revision": 1,
  "role": "load-bearing",
  "depends_on": ["..."]
}
```

It contains no Principia status fields.

## Negative fixtures

Validation requires known dishonest or premature paths to fail:

1. copying Atlas knowledge status into Principia authority;
2. using mutable `revision: "latest"` references;
3. activating a live dependency while Atlas Phase 1 freezes direct integration.

## Validation

```bash
python3 scripts/validate_experiences.py --strict
python3 scripts/export_principia_atlas_dependents.py --check
python3 scripts/validate_principia_atlas_bridge.py
python3 scripts/validate_repo.py
python3 scripts/validate_phase10_synthesis.py
```

The permanent workflow must use `contents: read`, must not clone Atlas, and must not write, push, merge, or modify lifecycle status.

## Exit result

Phase 11A is ready when:

- all four experience artifacts and templates have revision and release metadata;
- the valid fixture and deterministic export match;
- all negative fixtures fail for the expected reasons;
- Phase 10 and experience validation remain green;
- CI is read-only;
- Atlas remains independent and unchanged;
- no live dependency exists.

## Next work

Phase 11B may continue controlled material expansion using revisioned Principia artifacts. A future live Principia–Atlas pilot must wait for explicit approval and compatible phase gates in both repositories.
