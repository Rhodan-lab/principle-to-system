# Phase 11B — Controlled Material Expansion

> Date: 2026-07-26  
> Repository: `Rhodan-lab/principle-to-system`  
> Product identity: Principia  
> Atlas status: separate repository; unchanged  
> Expansion: 12 new artifacts, 16 total experiences, 4 complete routes  
> Validation status: implemented and validated on draft PR #13

## Purpose

Phase 11B expands the applied learning layer from one thermodynamic seed route into four coherent routes. The goal is not maximum file count. The goal is enough domain diversity to test whether the Principia experience model transfers across physical infrastructure, public systems, and distributed information systems while preserving scientific boundaries, safety, source traceability, revision identity, and release governance.

## Canonical inventory

`experiences/phase-11b-inventory.json` defines `principia-experience-expansion/0.1` with:

- four complete routes;
- sixteen reviewed experience artifacts;
- four system dossiers;
- four failure patterns;
- four investigations;
- four design challenges;
- `artifact_revision: 1` for every artifact;
- `release_status: draft` for every artifact;
- no `Complete` or released artifact;
- Phase 12 as the release gate;
- no live Atlas dependency or Atlas status inheritance.

## Routes

### 1. thermal-control

Existing reviewed seed route:

1. `system-dossier-refrigerator`
2. `failure-pattern-feedback-instability`
3. `investigation-room-cooling`
4. `design-challenge-passive-cooler`

### 2. resilient-energy

New route:

1. `system-dossier-solar-battery-microgrid`
2. `failure-pattern-protection-coordination`
3. `investigation-solar-shading`
4. `design-challenge-resilient-charging-hub`

Scientific and engineering scope includes photovoltaic conversion, storage, power electronics, energy balance, grid-connected and islanded modes, protection selectivity, shading and mismatch, critical-load definition, reserve, lifecycle, and common-cause failure.

Safety boundary:

- no construction, wiring, live measurement, battery modification, islanding test, backfeed, or grid connection;
- investigations use public, teacher-provided, hypothetical, or simulated data;
- the design challenge produces requirements, models, diagrams, and scenario evidence only.

### 3. water-infrastructure

New route:

1. `system-dossier-drinking-water-network`
2. `failure-pattern-sensor-drift-hidden-degradation`
3. `investigation-filter-loading`
4. `design-challenge-nonpotable-rainwater-buffer`

Scientific and engineering scope includes source-to-service boundaries, particle removal, disinfection and by-product trade-offs, fluid storage and distribution, sensor drift, filter resistance, rainfall storage balance, maintenance, and public-system governance.

Safety boundary:

- no procedure for producing safe drinking water;
- no contaminated-water collection, chemical treatment, culturing, tasting, plumbing modification, or cross-connection;
- the rainwater challenge is explicitly non-potable;
- investigations use synthetic or public operational data.

### 4. distributed-information

New route:

1. `system-dossier-web-service-request`
2. `failure-pattern-retry-storm-queue-collapse`
3. `investigation-queue-delay-near-capacity`
4. `design-challenge-resilient-school-information-service`

Scientific and engineering scope includes packet and protocol boundaries, queues, utilization, latency distributions, caching, retries, idempotency, overload control, cyber resilience, accessibility, privacy, deployment, rollback, and verified recovery.

Safety boundary:

- no access to real accounts, school systems, APIs, networks, or devices;
- no automated live traffic, scanning, flooding, password guessing, or rate-limit bypass;
- no real student or personal data;
- all tests use synthetic traffic and offline simulation.

## Artifact lifecycle

Each experience carries:

```yaml
status: reviewed
artifact_revision: 1
release_status: draft
```

These fields remain independent:

- `status` records focused Principia pedagogical review;
- `artifact_revision` identifies dependency-relevant meaning;
- `release_status` records publication readiness;
- Atlas knowledge lifecycle remains Atlas-only authority.

Reviewed does not mean independently certified or released. Phase 11B creates no `Complete` content.

## Source result

`sources/experience-source-ledger.md` expands from 9 to 28 records.

New source coverage uses official or standards-based material from:

- U.S. Department of Energy;
- U.S. Environmental Protection Agency;
- U.S. Geological Survey;
- National Institute of Standards and Technology;
- Internet Engineering Task Force / RFC Editor.

Every one of the sixteen experience slugs has at least one ledger row. The central 143-record core-module ledger remains unchanged.

## Validation architecture

`scripts/validate_phase11b_expansion.py` extends the inherited strict experience validator to all sixteen artifacts. It checks:

- inventory schema and exact counts;
- one artifact from every family in each route;
- unique paths and slugs;
- required headings, models, sources, and internal links;
- `status: reviewed`, `artifact_revision: 1`, and `release_status: draft`;
- source-ledger coverage and exact 28-record transition;
- route-specific electrical, public-health, privacy, and live-system boundaries;
- navigation coverage in every family index;
- non-live Principia–Atlas compatibility;
- Phase 12 as the earliest release gate;
- read-only CI.

The workflow preserves full validation diagnostics as a GitHub Actions artifact while still failing the job whenever the validator reports an error.

## Principia & Atlas boundary

Phase 11A was merged through PR #12. Phase 11B uses the revisioned artifact model introduced there but adds no new Atlas manifest and no live dependency.

The existing fixture remains:

```yaml
mode: compatibility-fixture
live: false
```

No status crosses the repository boundary automatically. Atlas remains unchanged.

## Validation result

The exact draft PR #13 head passes:

```bash
python3 scripts/validate_experiences.py --strict
python3 scripts/validate_phase11b_expansion.py
python3 scripts/export_principia_atlas_dependents.py --check
python3 scripts/validate_principia_atlas_bridge.py
python3 scripts/validate_principia_atlas_audit.py
python3 scripts/validate_phase10_synthesis.py
python3 scripts/validate_phase10_audit.py
python3 scripts/validate_repo.py
```

The coordinated GitHub Actions result is green for:

- Phase 5 Sources;
- Phase 6 Foundations;
- Phase 7 Physical Science;
- Phase 8 Life and Earth Systems;
- Phase 9 Technology;
- Phase 10 Synthesis;
- Applied Materials;
- Principia–Atlas Compatibility;
- Phase 11B Expansion.

The permanent workflow uses `contents: read`, does not clone Atlas, and cannot write, commit, push, merge, or change lifecycle state.

## Exit condition achieved

Phase 11B satisfies its automated exit conditions:

- all sixteen artifacts pass the expanded strict validator;
- all four routes are navigable and complete;
- all twenty-eight experience-source records validate;
- prior Phase 5–11A continuity is green;
- CI is permanently read-only;
- all artifacts remain unreleased;
- Atlas remains separate and non-live.

Independent review and merge remain pending. Automated validation is not a release claim.

## Next stage

Phase 12 is the repository-wide release candidate. It should perform independent scientific and editorial review, cross-artifact terminology and equation reconciliation, accessibility and usability review, source integrity, revision and deprecation tests, release-status governance, and a bounded readiness assessment for the first live Principia–Atlas pilot.
