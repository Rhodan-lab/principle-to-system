# Principia–Atlas Bridge Candidate — Delayed Correction Revision 2

> Date: 2026-07-26  
> Repository changed: `Rhodan-lab/principle-to-system`  
> Atlas was not modified.  
> Candidate state: `mode: bridge-candidate`, `live: false`

## Purpose

Promote the existing delayed-feedback compatibility fixture into a non-live, exact-revision bridge candidate suitable for a future Atlas Phase 2 importer test.

This change does not merge the repositories, call Atlas at runtime, copy Atlas lifecycle status, or change Principia pedagogical or release status.

## Exact dependency transition

The candidate changes only:

```text
model:en:delayed-correction-recurrence@1
→ model:en:delayed-correction-recurrence@2
```

The other delayed-feedback dependencies remain:

```text
claim:en:model-oscillation-does-not-prove-real-system@1
concept:en:feedback@1
concept:en:oscillation@1
```

The active exact model reference is therefore `model:en:delayed-correction-recurrence@2`.

## Scientific correction

The affected Principia materials now state that **oscillation does not prove instability**.

The revision-2 recurrence

```text
x[t+1] = x[t] - x[t-1]
x0 = 1
x1 = 0
```

returns the ordered state pair after six steps. The orbit is bounded and exactly period 6. It demonstrates oscillation in the declared model, not instability, not a theorem that delay always destabilizes systems, and not empirical evidence about a refrigerator or another real system.

`failure-atlas/feedback-instability.md` now distinguishes decaying, bounded sustained, growing, and operationally harmful oscillation. `system-dossiers/refrigerator.md` now distinguishes designed thermostat cycling from abnormal short-cycling, growing excursions, and instability.

These are model-boundary clarifications, so the Principia failure-pattern artifact remains `artifact_revision: 1`.

## Separate status authority

The bridge preserves:

```yaml
Atlas knowledge status authority: Atlas
Principia pedagogical status: reviewed
Principia release status: draft
Principia artifact revision: 1
```

No status is inherited or exported.

## Deterministic export

The export contract is:

```text
principia-atlas-external-dependent/0.2
```

It retains `depends_on` for opaque ID coverage and adds `depends_on_exact` for Atlas Phase 2 exact-revision lookup and dependency-impact queries.

The export contains no pedagogical, release, or Atlas knowledge status.

## Revision-impact decision

The model transition from revision 1 to revision 2 was inspected and accepted because revision 2 corrects the periodicity proof and makes the oscillation-versus-instability boundary explicit. The accepted transition records:

- no automatic pedagogical change;
- no Principia release promotion;
- no Principia artifact revision increment;
- continued exact-revision tracking;
- future revision 3 as a new inspection event.

## Importer readiness

Principia records the candidate as:

```yaml
mode: bridge-candidate
live: false
decision: candidate-ready
```

`candidate-ready` means the committed file is ready for an Atlas Phase 2 importer to inspect through Atlas's own read-only validation. It does not mean Atlas accepted the dependent and does not activate live cross-repository calls.

## Validation commands

```bash
python3 scripts/export_principia_atlas_dependents.py --check
python3 scripts/validate_principia_atlas_bridge.py
python3 scripts/validate_principia_atlas_audit.py
python3 scripts/validate_experiences.py --strict
python3 scripts/validate_phase11b_expansion.py
python3 scripts/validate_repo.py --strict
python3 scripts/validate_phase12_release_candidate.py
python3 -m unittest discover -s software/tests -v
python3 scripts/validate_phase13_software.py
```

The permanent compatibility workflow is read-only and does not clone or modify Atlas.
