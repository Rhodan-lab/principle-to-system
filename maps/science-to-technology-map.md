---
title: "Science to Technology Map"
slug: map-science-to-technology
domain: map
status: complete
prerequisites: []
connections: []
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Science to Technology Map

This map shows how the science modules (06–16) enable the technology modules (17–20) through specific mechanisms.

```mermaid
graph LR
    %% Science modules
    M06["06 Matter & Quantum"]
    M07["07 Chemical Bonding"]
    M08["08 Energy & Thermo"]
    M09["09 Motion & Forces"]
    M10["10 Electricity & Magnetism"]
    M11["11 Waves & Signals"]
    M12["12 Fluids & Materials"]
    M13["13 Cells & Bioenergetics"]
    M14["14 DNA & Evolution"]
    M15["15 Ecosystems & Complex Systems"]
    M16["16 Earth & Planetary"]

    %% Technology modules
    M17["17 Materials & Manufacturing"]
    M18["18 Semiconductors & Electronics"]
    M19["19 Software & AI"]
    M20["20 Sensors, Control & Infrastructure"]

    %% Science → Technology links
    M06 -->|enables| M17
    M06 -->|enables| M18
    M07 -->|enables| M17
    M07 -->|transforms| M17
    M08 -->|constrains| M17
    M08 -->|constrains| M20
    M09 -->|constrains| M17
    M10 -->|enables| M18
    M10 -->|enables| M20
    M11 -->|enables| M20
    M11 -->|enables| M18
    M12 -->|enables| M17
    M12 -->|constrains| M20
    M13 -->|enables| M17
    M14 -->|enables| M17
    M15 -->|is modelled by| M19
    M16 -->|measures| M20

    %% Technology inter-dependencies
    M17 -->|enables| M18
    M18 -->|enables| M19
    M18 -->|enables| M20
    M19 -->|controls| M20
```

## Relationship key

| From | To | Label | Meaning |
| --- | --- | --- | --- |
| 06 Matter & Quantum | 17 Materials | enables | Atomic theory explains material properties |
| 06 Matter & Quantum | 18 Semiconductors | enables | Band theory from quantum mechanics |
| 07 Chemical Bonding | 17 Materials | enables, transforms | Bond chemistry determines material synthesis |
| 08 Energy & Thermo | 17 Materials | constrains | Thermodynamic limits on processing |
| 08 Energy & Thermo | 20 Infrastructure | constrains | Carnot efficiency limits power generation |
| 09 Motion & Forces | 17 Materials | constrains | Mechanical loads constrain material choice |
| 10 Electricity & Magnetism | 18 Semiconductors | enables | Electromagnetic theory underlies circuits |
| 10 Electricity & Magnetism | 20 Infrastructure | enables | Induction enables power generation |
| 11 Waves & Signals | 18 Semiconductors | enables | Signal processing in electronic systems |
| 11 Waves & Signals | 20 Infrastructure | enables | Sensing and communication |
| 12 Fluids & Materials | 17 Materials | enables | Mechanical properties and processing |
| 12 Fluids & Materials | 20 Infrastructure | constrains | Fluid dynamics constrains cooling and hydraulics |
| 15 Complex Systems | 19 Software & AI | is modelled by | Network and learning theory |
| 16 Earth & Planetary | 20 Infrastructure | measures | Environmental monitoring drives infrastructure |
| 17 Materials | 18 Semiconductors | enables | Fabrication enables chip manufacturing |
| 18 Semiconductors | 19 Software & AI | enables | Hardware runs software |
| 18 Semiconductors | 20 Infrastructure | enables | Electronics in sensors and controllers |
| 19 Software & AI | 20 Infrastructure | controls | Software controls automated systems |

## Reading this map

Science modules appear on the left; technology modules on the right. The flow is generally left-to-right (science enables technology), with inter-technology dependencies flowing top-to-bottom (materials → electronics → software → control).
