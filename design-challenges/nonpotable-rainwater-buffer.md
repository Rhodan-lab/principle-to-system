---
title: "Design a Non-Potable Rainwater Buffer"
slug: design-challenge-nonpotable-rainwater-buffer
domain: experience
experience_type: design-challenge
status: reviewed
artifact_revision: 1
release_status: draft
prerequisites: [03-mathematical-models, 12-fluids-materials, 16-earth-planetary, 20-sensors-control-infrastructure]
connections: [17-materials-manufacturing, system-dossier-drinking-water-network, failure-pattern-sensor-drift-hidden-degradation, investigation-filter-loading]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Design a Non-Potable Rainwater Buffer

## 1. Need and context

Design a **conceptual** rainwater collection and storage buffer for a clearly non-potable purpose such as irrigation of ornamental plants, cleaning outdoor surfaces where permitted, or supplying a classroom water-cycle demonstrator. The design must manage variable rainfall, finite storage, overflow, sediment, mosquito prevention, labeling, and maintenance.

The system must never be presented as producing drinking water.

## 2. Stakeholders

Consider:

- people who operate, clean, and inspect the system;
- children or visitors who could misunderstand its purpose;
- property owners and drainage managers;
- neighbors affected by overflow or standing water;
- maintenance staff and waste handlers;
- local authorities responsible for plumbing, drainage, and public health;
- ecosystems affected by altered runoff or discharge.

## 3. Requirements and success measures

Define:

- catchment area and assumed runoff coefficient;
- target non-potable demand;
- maximum storage volume and footprint;
- overflow destination;
- minimum drainability and access for cleaning;
- exclusion of insects, animals, debris, and unauthorized connections;
- clear permanent labeling as non-potable;
- maximum acceptable standing-water duration outside sealed storage;
- maintenance and inspection frequency;
- materials, repairability, and end-of-life requirements.

A measurable success statement can be:

> Under the stated rainfall and demand scenarios, the conceptual buffer meets at least the selected fraction of non-potable demand without uncontrolled overflow, cross-connection, or inaccessible stagnant storage.

## 4. Hard safety constraints

- The design is for non-potable use only. Do not drink, taste, cook with, wash food with, or claim safety for collected water.
- Do not connect the concept to household drinking-water plumbing or any public-water system.
- Do not create a cross-connection, pressurized vessel, buried tank, rooftop installation, or structural load.
- Do not collect water from hazardous, contaminated, industrial, or unknown surfaces.
- Do not leave open containers that can become drowning, insect, or hygiene hazards.
- Use drawings, public rainfall data, and simulation. Any tabletop model must use clean tap water, small unpressurized containers, immediate cleanup, and adult-approved materials.
- Real installation requires local rules, structural review, plumbing safeguards, drainage design, and competent supervision.

## 5. Assumptions

State assumptions for:

- rainfall depth and event timing;
- catchment material and runoff coefficient;
- first-loss or initial wetting volume;
- evaporation and leakage;
- demand schedule;
- storage starting level;
- overflow capacity;
- maintenance availability;
- seasonal dry periods;
- whether water quality is outside the design claim.

Do not use annual rainfall alone to claim reliability. Timing and storage capacity matter.

## 6. System boundary

The conceptual boundary may include:

- catchment surface;
- gutters or conveyance paths;
- debris exclusion;
- non-potable storage;
- level indication;
- overflow and safe discharge;
- controlled non-potable outlet;
- labels and physical separation;
- inspection and cleaning access;
- maintenance records.

The environment includes rainfall, wind, leaves, dust, animals, sunlight, temperature, users, nearby foundations, drains, and local regulation.

## 7. Concept alternatives

Develop at least three genuinely different concepts:

1. **Single sealed tank** with gravity-fed non-potable outlet and visible overflow.
2. **Modular linked containers** that can be isolated and cleaned separately.
3. **Detention-first landscape feature** that temporarily slows runoff without storing water for reuse.
4. **Small demonstrator loop** using only clean tap water and simulated rainfall for education.

A concept that merely changes tank size is not a distinct architecture.

## 8. Minimum quantitative model

Potential captured volume for event $k$ is

$$V_{in,k}=C_r A P_k$$

where $C_r$ is a dimensionless runoff coefficient, $A$ is catchment area, and $P_k$ is rainfall depth in consistent units.

Storage balance is

$$S_{k+1}=\min\left[S_{max},\max\left(0,S_k+V_{in,k}-D_k-L_k\right)\right]$$

where $D_k$ is non-potable demand and $L_k$ includes modeled evaporation, leakage, or deliberate draining. Overflow is

$$V_{overflow,k}=\max\left(0,S_k+V_{in,k}-D_k-L_k-S_{max}\right)$$

A demand-reliability estimate is

$$R_D=1-\frac{\sum_k V_{unmet,k}}{\sum_k D_k}$$

for the stated scenario set. This is not a water-quality metric.

## 9. Trade-off matrix

| Criterion | Single sealed tank | Modular containers | Detention landscape | Demonstrator loop |
| --- | --- | --- | --- | --- |
| Non-potable demand coverage |  |  |  |  |
| Overflow control |  |  |  |  |
| Cross-connection risk |  |  |  |  |
| Cleaning access |  |  |  |  |
| Insect exclusion |  |  |  |  |
| Structural complexity |  |  |  |  |
| Repairability |  |  |  |  |
| Space requirement |  |  |  |  |
| Educational value |  |  |  |  |
| Lifecycle burden |  |  |  |  |

State evidence and uncertainty for every score. Safety constraints are pass/fail gates, not tradeable points.

## 10. Failure modes and safeguards

| Failure | Mechanism | Safeguard or response |
| --- | --- | --- |
| Uncontrolled overflow | Storage or outlet undersized | Defined overflow path and event scenarios |
| Cross-connection | Non-potable line reaches potable plumbing | Physical separation, labeling, competent review |
| Insect breeding | Open or poorly screened water | Sealed storage and maintained exclusion barriers |
| Sediment accumulation | Catchment debris enters storage | Debris exclusion and accessible cleaning |
| Structural overload | Water mass exceeds support capacity | Ground-supported concept and structural review |
| Hidden leak | Container or connection degrades | Visible inspection path and secondary drainage |
| Stagnant unused water | Demand lower than assumed | Drain-down policy and bounded retention |
| Misuse as drinking water | Labeling or access fails | Permanent labels, restricted outlet, education |
| Sensor drift | Level reading becomes unreliable | Simple physical verification and conservative overflow |
| Maintenance abandonment | No owner or schedule | Named steward and documented inspection triggers |

## 11. Safe test plan

Run a spreadsheet simulation using at least one dry sequence, one frequent-light-rain sequence, and one intense-event sequence. Test several storage volumes and demand schedules. Report capture, overflow, unmet demand, and maximum retention time.

A safe tabletop demonstrator may use a shallow tray, clean tap water, a small open cup observed continuously, and immediate drying. It must not be stored, consumed, pressurized, or connected to plumbing. Do not reproduce roof access, gutters at height, buried storage, or real drainage work.

## 12. Selected concept and rationale

```text
Because the main non-potable purpose is ____________________,
and the dominant constraint is ____________________,
we selected ____________________.

The design remains separated from potable plumbing by ____________________.
The overflow path is ____________________.
The most important maintenance dependency is ____________________.
```

Explain why rejected concepts fail a requirement rather than merely receiving a lower score.

## 13. Evidence that could change the decision

Change the concept if:

- rainfall timing produces more overflow or unmet demand than expected;
- structural review rejects the assumed location;
- local rules prohibit the intended use or require additional safeguards;
- maintenance cannot reliably prevent blockage or insect access;
- users confuse the outlet with potable water;
- a detention-only solution manages runoff with less lifecycle burden;
- water-quality uncertainty makes the intended non-potable use inappropriate;
- climate, catchment, or demand changes invalidate the model.

## 14. Sources and module links

- U.S. Environmental Protection Agency, *How Does Your Water System Work?*: https://www.epa.gov/ground-water-and-drinking-water/how-does-your-water-system-work-text-only
- U.S. Environmental Protection Agency, *Drinking Water Distribution System Tools and Resources*: https://www.epa.gov/dwreginfo/drinking-water-distribution-system-tools-and-resources
- U.S. Geological Survey, *The Water Cycle*: https://www.usgs.gov/special-topics/water-science-school/science/water-cycle
- [Mathematical Models](../foundations/03-mathematical-models/overview.md)
- [Fluids and Materials](../science/12-fluids-materials/overview.md)
- [Earth and Planetary Systems](../science/16-earth-planetary/overview.md)
- [Sensors, Control, and Infrastructure](../technology/20-sensors-control-infrastructure/overview.md)
- [A Drinking-Water Treatment and Distribution Network](../system-dossiers/drinking-water-network.md)
