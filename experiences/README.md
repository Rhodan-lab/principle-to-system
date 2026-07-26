---
title: "Learning Experiences"
slug: learning-experiences
domain: experience
experience_type: index
status: reviewed
prerequisites: []
connections: [concept-systems-and-models, concept-cause-and-effect]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Learning Experiences

The core modules explain scientific and engineering ideas. This layer asks learners to use those ideas where the answer is not supplied in advance.

```text
notice a system
→ choose a boundary
→ identify flows and state variables
→ propose competing mechanisms
→ build the smallest useful model
→ test it against evidence
→ redesign under constraints
→ explain remaining uncertainty
```

## Four families

| Folder | Purpose | Typical output |
| --- | --- | --- |
| [`system-dossiers/`](../system-dossiers/) | Reverse-engineer a familiar technology | Layered architecture and principle-to-system chain |
| [`failure-atlas/`](../failure-atlas/) | Study recurring causal failure patterns | Failure map, barriers, and redesign strategy |
| [`investigations/`](../investigations/) | Compare models using safe evidence | Evidence notebook and revised explanation |
| [`design-challenges/`](../design-challenges/) | Design under explicit constraints | Requirements, model, trade-off table, and rationale |

## Shared rules

1. Begin with an observable phenomenon or concrete system.
2. State the system boundary and environment.
3. Separate facts, assumptions, estimates, and choices.
4. Include at least one quantitative model.
5. Name uncertainty, failure modes, and trade-offs.
6. Keep physical activities optional, low-energy, and safe.
7. Do not use grades, streaks, or competitive ranking.
8. End with unresolved questions and evidence that could change the conclusion.
9. Do not convert a diagram or validator pass into release authority.
10. Keep Atlas knowledge status separate from Principia pedagogical and release status.

## Identity and status separation

Each authored experience has four independent identity or lifecycle fields:

| Field | Meaning | Authority |
| --- | --- | --- |
| `slug` | Stable Principia artifact identity within its experience family | Principia |
| `artifact_revision` | Positive exact revision for dependency-relevant meaning | Principia |
| `status` | Pedagogical maturity | Principia |
| `release_status` | Publication readiness | Principia |

`status: reviewed` does not imply `release_status: released`. Every Phase 11B artifact uses `artifact_revision: 1` and `release_status: draft`. A dependency-relevant change must increment the artifact revision before a bridge manifest can be updated.

## Canonical four-route inventory

[`phase-11b-inventory.json`](phase-11b-inventory.json) is the machine-readable inventory for four complete routes and sixteen artifacts.

### thermal-control

1. [The Domestic Refrigerator](../system-dossiers/refrigerator.md)
2. [Feedback Instability](../failure-atlas/feedback-instability.md)
3. [How Does a Room Cool?](../investigations/room-cooling.md)
4. [Design a Passive Cooler](../design-challenges/passive-cooler.md)

### resilient-energy

1. [A Solar–Battery Microgrid](../system-dossiers/solar-battery-microgrid.md)
2. [Protection Coordination Failure](../failure-atlas/protection-coordination.md)
3. [How Does Partial Shading Change Solar Output?](../investigations/solar-shading.md)
4. [Design a Resilient Community Charging Hub](../design-challenges/resilient-charging-hub.md)

This route is simulation- and data-first. It does not authorize live electrical work, islanding tests, battery modification, or grid connection.

### water-infrastructure

1. [A Drinking-Water Treatment and Distribution Network](../system-dossiers/drinking-water-network.md)
2. [Sensor Drift and Hidden Degradation](../failure-atlas/sensor-drift-hidden-degradation.md)
3. [How Does Filter Loading Change Flow Resistance?](../investigations/filter-loading.md)
4. [Design a Non-Potable Rainwater Buffer](../design-challenges/nonpotable-rainwater-buffer.md)

This route explains regulated public-water systems and safe models. It does not provide a procedure for producing potable water or modifying plumbing.

### distributed-information

1. [A Web Request Through a Distributed Service](../system-dossiers/web-service-request.md)
2. [Retry Storm and Queue Collapse](../failure-atlas/retry-storm-queue-collapse.md)
3. [How Does Queueing Delay Grow Near Capacity?](../investigations/queue-delay-near-capacity.md)
4. [Design a Resilient School Information Service](../design-challenges/resilient-school-information-service.md)

This route uses synthetic traffic and offline simulation only. It does not authorize testing, scanning, flooding, or accessing live systems.

## Principia & Atlas compatibility

[`contracts/principia-atlas/0.1/`](../contracts/principia-atlas/0.1/) defines a future-safe, one-way compatibility boundary. Principia can describe exact-revision Atlas dependencies and export an opaque external-dependent record without importing Atlas or treating Atlas lifecycle state as Principia status.

During Atlas Phase 1, compatibility manifests remain fixtures only:

```yaml
mode: compatibility-fixture
live: false
```

Phase 11B adds no live Atlas dependency and does not change Atlas.
