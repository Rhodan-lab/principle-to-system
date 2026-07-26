---
title: "Complete Dependency Map"
slug: map-complete-dependency
domain: map
status: reviewed
prerequisites: []
connections: []
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Complete Dependency Map

This map is generated from the Phase 10 canonical graph. Every arrow points from a direct prerequisite to the dependent module.

```mermaid
graph TD
    M01["01 Scientific Reasoning"]
    M02["02 Measurement & Uncertainty"]
    M03["03 Mathematical Models"]
    M04["04 Probability & Statistics"]
    M05["05 Computation & Algorithms"]
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

    M01 -->|prerequisite for| M02
    M01 -->|prerequisite for| M03
    M01 -->|prerequisite for| M04
    M03 -->|prerequisite for| M04
    M03 -->|prerequisite for| M05
    M04 -->|prerequisite for| M05
    M01 -->|prerequisite for| M06
    M02 -->|prerequisite for| M06
    M03 -->|prerequisite for| M06
    M06 -->|prerequisite for| M07
    M03 -->|prerequisite for| M08
    M06 -->|prerequisite for| M08
    M03 -->|prerequisite for| M09
    M03 -->|prerequisite for| M10
    M06 -->|prerequisite for| M10
    M03 -->|prerequisite for| M11
    M09 -->|prerequisite for| M11
    M03 -->|prerequisite for| M12
    M08 -->|prerequisite for| M12
    M09 -->|prerequisite for| M12
    M07 -->|prerequisite for| M13
    M08 -->|prerequisite for| M13
    M07 -->|prerequisite for| M14
    M13 -->|prerequisite for| M14
    M04 -->|prerequisite for| M15
    M13 -->|prerequisite for| M15
    M14 -->|prerequisite for| M15
    M08 -->|prerequisite for| M16
    M09 -->|prerequisite for| M16
    M12 -->|prerequisite for| M16
    M15 -->|prerequisite for| M16
    M06 -->|prerequisite for| M17
    M07 -->|prerequisite for| M17
    M12 -->|prerequisite for| M17
    M06 -->|prerequisite for| M18
    M10 -->|prerequisite for| M18
    M17 -->|prerequisite for| M18
    M04 -->|prerequisite for| M19
    M05 -->|prerequisite for| M19
    M18 -->|prerequisite for| M19
    M10 -->|prerequisite for| M20
    M11 -->|prerequisite for| M20
    M18 -->|prerequisite for| M20
    M19 -->|prerequisite for| M20
```

## Canonical direct prerequisites

| Module | Direct prerequisites |
| --- | --- |
| 01 Scientific Reasoning | None |
| 02 Measurement & Uncertainty | 01 |
| 03 Mathematical Models | 01 |
| 04 Probability & Statistics | 01, 03 |
| 05 Computation & Algorithms | 03, 04 |
| 06 Matter & Quantum | 01, 02, 03 |
| 07 Chemical Bonding | 06 |
| 08 Energy & Thermodynamics | 03, 06 |
| 09 Motion & Forces | 03 |
| 10 Electricity & Magnetism | 03, 06 |
| 11 Waves & Signals | 03, 09 |
| 12 Fluids & Materials | 03, 08, 09 |
| 13 Cells & Bioenergetics | 07, 08 |
| 14 DNA & Evolution | 07, 13 |
| 15 Ecosystems & Complex Systems | 04, 13, 14 |
| 16 Earth & Planetary Systems | 08, 09, 12, 15 |
| 17 Materials & Manufacturing | 06, 07, 12 |
| 18 Semiconductors & Electronics | 06, 10, 17 |
| 19 Software & AI | 04, 05, 18 |
| 20 Sensors, Control & Infrastructure | 10, 11, 18, 19 |

## Reading rule

`A -->|prerequisite for| B` means A is assumed before B. Enabling, constraining, measuring, modelling, and controlling relations belong in the science-to-technology map and must not be confused with prerequisites.

## Phase 10 synthesis boundaries

- This document is a reviewed route or crosscutting synthesis, not proof that one mechanism, architecture, or historical sequence is inevitable.
- Every equation, quantity, and causal claim inherits the assumptions and validity limits stated in the linked reviewed modules.
- Technology performance depends on architecture, implementation, operating conditions, measurement boundary, lifecycle, safety, security, and human organisation.
- `Reviewed` records focused reconciliation; it does not mean independently certified or release-ready.
