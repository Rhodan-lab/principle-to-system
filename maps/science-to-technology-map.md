---
title: "Science to Technology Map"
slug: map-science-to-technology
domain: map
status: reviewed
prerequisites: []
connections: []
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Science to Technology Map

This map shows selected enabling and constraining relationships between reviewed science and technology modules. These are not a substitute for the canonical prerequisite graph.

```mermaid
graph LR
    M06["06 Matter & Quantum"]
    M07["07 Chemical Bonding"]
    M08["08 Energy & Thermodynamics"]
    M09["09 Motion & Forces"]
    M10["10 Electricity & Magnetism"]
    M11["11 Waves & Signals"]
    M12["12 Fluids & Materials"]
    M13["13 Cells & Bioenergetics"]
    M14["14 DNA & Evolution"]
    M15["15 Ecosystems & Complex Systems"]
    M16["16 Earth & Planetary Systems"]
    M17["17 Materials & Manufacturing"]
    M18["18 Semiconductors & Electronics"]
    M19["19 Software & AI"]
    M20["20 Sensors, Control & Infrastructure"]

    M06 -->|enables| M17
    M06 -->|enables| M18
    M07 -->|enables| M17
    M08 -->|constrains| M17
    M08 -->|constrains| M20
    M09 -->|constrains| M17
    M10 -->|enables| M18
    M10 -->|enables| M20
    M11 -->|enables| M18
    M11 -->|enables| M20
    M12 -->|enables| M17
    M12 -->|constrains| M20
    M13 -->|enables| M17
    M14 -->|enables| M17
    M15 -->|models| M19
    M16 -->|measures| M20
    M17 -->|enables| M18
    M18 -->|enables| M19
    M18 -->|enables| M20
    M19 -->|controls| M20
```

## Relationship vocabulary

| Label | Meaning |
| --- | --- |
| enables | Supplies a mechanism, material, or capability used by the target. |
| constrains | Supplies limits, conservation laws, or operating boundaries. |
| measures | Supplies measurement or inference methods. |
| models | Supplies representations or computational methods. |
| controls | Supplies decision, feedback, or coordination logic. |

A relation is selective rather than exhaustive. Technology also depends on manufacturing, institutions, standards, maintenance, operators, safety, security, economics, and lifecycle governance.

## Phase 10 synthesis boundaries

- This document is a reviewed route or crosscutting synthesis, not proof that one mechanism, architecture, or historical sequence is inevitable.
- Every equation, quantity, and causal claim inherits the assumptions and validity limits stated in the linked reviewed modules.
- Technology performance depends on architecture, implementation, operating conditions, measurement boundary, lifecycle, safety, security, and human organisation.
- `Reviewed` records focused reconciliation; it does not mean independently certified or release-ready.
