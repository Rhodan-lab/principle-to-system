---
title: "Complete Dependency Map"
slug: map-complete-dependency
domain: map
status: complete
prerequisites: []
connections: []
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Complete Dependency Map

This map shows all prerequisite and enabling relationships among the 20 modules. Arrows point from prerequisite to dependent module, with labelled relationship types.

```mermaid
graph TD
    %% Foundations
    M01["01 Scientific Reasoning"]
    M02["02 Measurement"]
    M03["03 Mathematical Models"]
    M04["04 Probability & Statistics"]
    M05["05 Computation"]

    %% Science
    M06["06 Matter & Quantum"]
    M07["07 Chemical Bonding"]
    M08["08 Energy & Thermo"]
    M09["09 Motion & Forces"]
    M10["10 Electricity & Magnetism"]
    M11["11 Waves & Signals"]
    M12["12 Fluids & Materials"]
    M13["13 Cells & Bioenergetics"]
    M14["14 DNA & Evolution"]
    M15["15 Ecosystems"]
    M16["16 Earth & Planetary"]

    %% Technology
    M17["17 Materials & Mfg"]
    M18["18 Semiconductors"]
    M19["19 Software & AI"]
    M20["20 Sensors & Control"]

    %% Foundations dependencies
    M01 -->|requires| M02
    M01 -->|requires| M03
    M01 & M03 -->|requires| M04
    M03 & M04 -->|requires| M05

    %% Foundations → Science
    M01 & M02 & M03 -->|requires| M06
    M03 -->|requires| M08
    M03 -->|requires| M09
    M03 & M06 -->|requires| M10
    M03 & M09 -->|requires| M11
    M03 & M08 & M09 -->|requires| M12
    M04 & M13 & M14 -->|requires| M15
    M08 & M09 & M12 & M15 -->|requires| M16

    %% Science internal
    M06 -->|requires| M07
    M06 -->|requires| M08
    M07 & M08 -->|requires| M13
    M07 & M13 -->|requires| M14

    %% Science → Technology
    M06 & M07 & M12 -->|enables| M17
    M06 & M10 & M17 -->|enables| M18
    M04 & M05 & M18 -->|enables| M19
    M10 & M11 & M18 & M19 -->|enables| M20
```

## Dependency summary table

| Module | Direct prerequisites |
| --- | --- |
| 01 Scientific Reasoning | None |
| 02 Measurement | 01 |
| 03 Mathematical Models | 01 |
| 04 Probability & Statistics | 01, 03 |
| 05 Computation | 03, 04 |
| 06 Matter & Quantum | 01, 02, 03 |
| 07 Chemical Bonding | 06 |
| 08 Energy & Thermo | 03, 06 |
| 09 Motion & Forces | 03 |
| 10 Electricity & Magnetism | 03, 06 |
| 11 Waves & Signals | 03, 09 |
| 12 Fluids & Materials | 03, 08, 09 |
| 13 Cells & Bioenergetics | 07, 08 |
| 14 DNA & Evolution | 07, 13 |
| 15 Ecosystems | 04, 13, 14 |
| 16 Earth & Planetary | 08, 09, 12, 15 |
| 17 Materials & Manufacturing | 06, 07, 12 |
| 18 Semiconductors & Electronics | 06, 10, 17 |
| 19 Software & AI | 04, 05, 18 |
| 20 Sensors, Control & Infrastructure | 10, 11, 18, 19 |

## Allowed relationship labels used

| Label | Meaning |
| --- | --- |
| requires | The target module assumes knowledge from the source |
| enables | The source module's science makes the target technology possible |
| constrains | The source module's laws set limits on the target |
| controls | The source module provides the control logic for the target |
| measures | The source module provides measurement methods for the target |
| transforms | The source module's mechanisms transform inputs in the target |
| is modelled by | The source phenomenon is represented by models in the target |

## Reading this map

Start at Module 01 (the only module with no prerequisites). Follow arrows downward and rightward to trace learning paths. Any path from 01 to 20 passes through a valid sequence of prerequisite knowledge. The six pathways in [`pathways/`](../pathways/) each trace one such route in detail.
