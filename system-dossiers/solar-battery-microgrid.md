---
title: "A Solar–Battery Microgrid"
slug: system-dossier-solar-battery-microgrid
domain: experience
experience_type: system-dossier
status: reviewed
artifact_revision: 1
release_status: draft
prerequisites: [08-energy-thermodynamics, 10-electricity-magnetism, 18-semiconductors-electronics, 20-sensors-control-infrastructure]
connections: [17-materials-manufacturing, 19-software-ai, concept-energy-and-matter, concept-systems-and-models, failure-pattern-protection-coordination, investigation-solar-shading, design-challenge-resilient-charging-hub]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# A Solar–Battery Microgrid

A microgrid is not simply a collection of solar panels and batteries. It is a coordinated electrical system that must measure changing conditions, balance generation and load, enforce limits, isolate faults, and decide when it may connect to or separate from a larger grid.

## 1. Observable system

From outside, a small solar–battery microgrid may appear as rooftop photovoltaic modules, an inverter enclosure, a battery cabinet, a switchboard, meters, and selected loads. Its important behavior is less visible: direct-current generation varies with irradiance and temperature, loads change independently, the battery has finite power and energy limits, and protective devices must respond correctly during abnormal conditions.

## 2. System boundary and environment

The boundary includes the PV array, DC conductors, isolation devices, power converters, battery system, meters, controller, protection, selected loads, and point of connection to the larger grid. The environment includes sunlight, ambient temperature, weather, utility voltage and frequency, users, maintenance, communications, tariffs, regulations, and emergency procedures.

A boundary must state whether it includes upstream utility equipment, building wiring, electric vehicles, backup generators, and thermal loads. Different boundaries produce different efficiency, reliability, and lifecycle conclusions.

## 3. Inputs, outputs, stores, and flows

| Type | Examples |
| --- | --- |
| Inputs | Solar irradiance, utility electricity, control settings, forecasts, maintenance actions |
| Outputs | Electricity to loads or grid, heat, logs, alarms, curtailed energy |
| Stores | Battery chemical state, electromagnetic energy, thermal energy, queued control actions |
| Flows | DC and AC electrical power, information, heat, maintenance resources |

The battery stores energy but does not create it. The controller stores information and state estimates but cannot override physical power, energy, temperature, or protection limits.

## 4. Scientific principles

A simplified PV power relation is

$$P_{pv}=G A \eta_{pv}$$

where $G$ is plane-of-array irradiance in W/m², $A$ is active module area in m², and $\eta_{pv}$ is operating efficiency. Real output also depends on spectrum, cell temperature, angle, mismatch, shading, soiling, wiring, converter operation, and degradation.

Battery energy balance over a short interval can be written

$$E_{b}(t+\Delta t)=E_b(t)+\eta_c P_c\Delta t-\frac{P_d\Delta t}{\eta_d}$$

where $P_c$ and $P_d$ are nonnegative charging and discharging powers, and $\eta_c$ and $\eta_d$ are boundary-specific efficiencies. The model must also enforce state-of-charge, current, voltage, temperature, and lifetime constraints.

For the AC boundary,

$$P_{grid}+P_{inv}=P_{load}+P_{loss}+\frac{dE_{stored}}{dt}$$

with a consistent sign convention. An instantaneous mismatch changes stored electromagnetic or rotational energy and can move voltage or frequency; a controller cannot assume balance without measuring and acting.

## 5. Components and functions

| Component | Function | Important limit |
| --- | --- | --- |
| PV modules | Convert part of incident radiation to DC electricity | Temperature, shading, mismatch, weather, degradation |
| DC isolation and protection | Limit and isolate abnormal current paths | Ratings, coordination, arc behavior, installation quality |
| Maximum-power-point control | Select a PV operating point | Rapid irradiance change, local maxima under partial shade |
| Inverter | Convert and regulate electrical power | Current, voltage, temperature, switching, grid-code limits |
| Battery cells and pack | Store and release electrical energy | State of charge, power, temperature, ageing, fault propagation |
| Battery management system | Estimate state and enforce local limits | Sensor error, model error, communication, hidden cell variation |
| Microgrid controller | Coordinate sources, loads, schedules, and modes | Forecast error, delay, conflicting objectives, cyber dependency |
| Relays and breakers | Detect and isolate selected faults | Measurement, settings, selectivity, interruption capability |
| Critical-load panel | Defines loads intended to remain supplied | Finite capacity and changing user demand |
| Metering and logs | Support control, billing, diagnosis, and review | Calibration, time synchronization, missing data, access control |

## 6. Interaction architecture

```text
sunlight → PV array → DC conversion → inverter → AC bus → loads
                                      ↘ battery converter ↔ battery
utility grid ↔ point of connection ↔ AC bus
meters → state estimation → controller → converter and switch commands
independent protection → breakers/contactors → fault isolation
```

Control and protection are related but not identical. Normal optimization may schedule the battery, while independent protection must still act when software, communications, measurements, or commands are wrong.

## 7. Quantitative model

For an interval-based planning model,

$$P_{grid,k}+P_{pv,k}+P_{d,k}=P_{load,k}+P_{c,k}+P_{loss,k}+P_{curt,k}$$

subject to

$$E_{min}\le E_{b,k}\le E_{max}$$

and power, temperature, ramp, reserve, and connection constraints. $P_{curt}$ represents available generation intentionally not used. The model can compare operating policies but does not prove safe switching, transient stability, protection coordination, or battery lifetime.

Resilience requires a service definition. A useful metric is critical-load energy not served:

$$ENS=\sum_k \max(0,P_{critical,k}-P_{served,k})\Delta t$$

Low $ENS$ for one scenario does not guarantee resilience to different outage duration, weather, equipment failure, or common-cause dependencies.

## 8. Control and feedback

The controller may estimate solar availability, load, state of charge, and grid condition; schedule charging; reserve energy for expected outages; curtail generation; and shed lower-priority loads. Fast inverter control regulates current or voltage, while slower supervisory control manages energy and modes.

Intentional islanding requires a valid grid-forming source, compatible protection, defined grounding and switching behavior, and a safe reconnection process. Solar modules alone do not automatically power a building during an outage.

## 9. Failure modes

- Partial shade creates mismatch and may move the PV operating point.
- A failed or drifting sensor corrupts state-of-charge or power estimates.
- Battery temperature or cell imbalance reaches a protective limit.
- Inverter current limits prevent the commanded response.
- Protection settings isolate too much, too little, or the wrong section.
- A communication failure separates measurement from command.
- The controller depletes reserve energy before a long outage.
- A shared power supply, clock, network, or sensor defeats apparently redundant controls.
- Reconnection occurs with incompatible voltage, frequency, or phase conditions.

## 10. Efficiency and performance

Round-trip battery efficiency, inverter efficiency, PV yield, curtailment, standby consumption, auxiliary cooling, and conductor losses must use consistent boundaries and time periods. Peak power, usable energy, autonomy duration, recovery time, and critical-load service are different metrics.

A design optimized for annual energy cost may preserve too little emergency reserve. A design optimized for long autonomy may cycle the battery less economically or require more capacity. Performance therefore depends on declared priorities rather than one universal score.

## 11. Lifecycle consequences

Lifecycle analysis includes mining and refining, semiconductor and battery manufacturing, structures, electronics, transport, land and roof use, installation, software support, maintenance, replacement, fire and emergency planning, recycling, and disposal. Longer service life can reduce replacement burden, but only if repair, compatibility, documentation, and spare parts remain available.

## 12. Alternative designs

- Grid-connected PV without storage: simpler, but usually unable to sustain local loads during an outage.
- Solar plus battery backup for selected circuits: bounded service with simpler priorities.
- Community microgrid: shared resources and coordination, with more complex ownership and protection.
- DC-coupled or AC-coupled storage: different conversion paths, retrofit options, and control boundaries.
- Dispatchable generator plus storage: longer-duration support with fuel, emissions, maintenance, and supply dependencies.
- Flexible-load microgrid: shifts or sheds demand instead of only adding generation.

## 13. Principle-to-system chain

```text
photon absorption and semiconductor junctions
→ DC electrical generation
→ switching power electronics
→ measurement and state estimation
→ energy storage with finite limits
→ protection and controlled switching
→ supervisory scheduling and load priority
→ grid-connected and islanded operating modes
→ resilient service for defined critical loads
```

## 14. Unresolved questions

- Which loads are genuinely critical, and for how long?
- What common-cause failures remain across controllers and protection?
- Which weather and outage scenarios dominate storage sizing?
- How will firmware, communications, and replacement parts be supported?
- What evidence is required before islanding and reconnection are trusted?
- How should cost, emissions, reliability, equity, and repairability be compared?

## 15. Sources and module links

- U.S. Department of Energy, *Solar Photovoltaic System Design Basics*: https://www.energy.gov/cmei/systems/solar-photovoltaic-system-design-basics
- U.S. Department of Energy, *Solar Integration: Distributed Energy Resources and Microgrids Basics*: https://www.energy.gov/cmei/systems/solar-integration-distributed-energy-resources-and-microgrids-basics
- U.S. Department of Energy, *Solar Integration: Solar Energy and Storage Basics*: https://www.energy.gov/cmei/systems/solar-integration-solar-energy-and-storage-basics
- [Energy and Thermodynamics](../science/08-energy-thermodynamics/overview.md)
- [Electricity and Magnetism](../science/10-electricity-magnetism/overview.md)
- [Semiconductors and Electronics](../technology/18-semiconductors-electronics/overview.md)
- [Sensors, Control, and Infrastructure](../technology/20-sensors-control-infrastructure/overview.md)
