---
title: "Design a Passive Cooler"
slug: design-challenge-passive-cooler
domain: experience
experience_type: design-challenge
status: reviewed
prerequisites: [03-mathematical-models, 08-energy-thermodynamics, 12-fluids-materials]
connections: [17-materials-manufacturing, system-dossier-refrigerator, investigation-room-cooling]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# Design a Passive Cooler

## 1. Need and context

Design a portable container that keeps an already-cool, non-medical payload below a chosen temperature for a stated duration without powered refrigeration.

## 2. Stakeholders

Consider the person carrying, opening, cleaning, repairing, and storing the container; nearby people exposed to leaks or condensation; and waste handlers or recyclers.

## 3. Requirements and success measures

Choose and justify:

- payload volume and total-mass limit;
- initial and maximum acceptable temperature;
- target duration and surrounding temperature;
- expected openings;
- cleaning, water resistance, lifetime, repairability, and cost requirements.

A measurable success statement should have the form:

> The central payload temperature remains below the selected limit for the selected duration under the stated conditions.

## 4. Hard safety constraints

- No powered compressor, fan, or thermoelectric module.
- No fire, pressurised container, dry ice, cryogenic liquid, reactive chemical, or hazardous substance.
- Use only sealed, ordinary water-based cold packs or ice where thermal storage is needed.
- Contain condensation and meltwater.
- Keep the design liftable, cleanable, and appropriate for its intended payload.

## 5. Assumptions

State assumptions such as constant ambient temperature, shade, fixed opening schedule, uniform starting temperature, and constant material properties. Identify which assumption is most likely to fail.

## 6. System boundary

The boundary may include shell, insulation, liner, lid, seal, payload, cold packs, compartments, drainage, and reflective surfaces. The environment includes air, ground contact, sunlight, rain, and user interaction.

## 7. Concept alternatives

Develop at least three genuinely different concepts:

- thick insulation with low thermal mass;
- thinner insulation with greater safe thermal storage;
- modular, repairable panels, seals, and liner;
- optional evaporative assistance only where humidity, water, hygiene, and containment make it appropriate.

## 8. Minimum quantitative model

Approximate enclosure heat leakage as

$$\dot Q=UA(T_{out}-T_{in})$$

where $U$ is overall heat-transfer coefficient in W/(m²·K), $A$ is area in m², and temperature difference is in K.

For one flat layer,

$$U\approx\frac{k}{L}$$

where $k$ is thermal conductivity and $L$ is thickness. This ignores seals, corners, convection films, thermal bridges, and air exchange.

A first warming-time estimate is

$$t\approx\frac{C\Delta T}{\dot Q}$$

With safe phase-change storage, include

$$Q_{stored}=mc\Delta T+mL_f$$

Use these models for comparison, not as a guarantee of field performance.

## 9. Trade-off matrix

| Criterion | Concept A | Concept B | Concept C |
| --- | --- | --- | --- |
| Thermal performance |  |  |  |
| Mass |  |  |  |
| Durability |  |  |  |
| Repairability |  |  |  |
| Water control |  |  |  |
| Cleaning |  |  |  |
| Material availability |  |  |  |
| End-of-life separation |  |  |  |
| Cost |  |  |  |

Explain every score. Do not combine scores without explicit, justified weights.

## 10. Failure modes and safeguards

| Failure | Mechanism | Safeguard |
| --- | --- | --- |
| Lid leakage | Warm humid air enters | Replaceable compressible seal and latch |
| Thermal bridge | Conductive part bypasses insulation | Break or isolate conduction path |
| Wet insulation | Water increases transfer and hygiene risk | Sealed liner and water-resistant insulation |
| Crushed insulation | Thickness decreases under load | Load-spreading shell |
| Meltwater leak | Container or pack fails | Secondary containment |
| Excess mass | Thermal storage harms portability | Set mass budget first |
| Solar heating | Exterior absorbs radiation | Shade and durable reflective surface |

## 11. Safe test plan

Use sealed water bottles as payload simulators and a household thermometer or logger. Record ambient and payload temperature, opening events, cold-pack mass, condensation, leakage, and test duration. Test a second condition to check whether the model predicts beyond one dataset.

## 12. Selected concept and rationale

```text
Because the main requirement is ______,
and the dominant heat path appears to be ______,
we selected ______.
This sacrifices ______ in exchange for ______.
The most important remaining risk is ______,
which we will test by ______.
```

## 13. Evidence that could change the decision

Change the design if tests show that seal leakage dominates, insulation absorbs water, mass exceeds the lifting limit, cleaning is inadequate, or a locally available material provides similar performance with better repairability.

## 14. Sources and module links

- OpenStax, *University Physics Volume 2 — Heat Transfer*: https://openstax.org/books/university-physics-volume-2/pages/1-introduction
- NIST, *Refrigerant Properties for Heat Transfer Analysis*: https://www.nist.gov/publications/refrigerant-properties-heat-transfer-analysis
- [Mathematical Models](../foundations/03-mathematical-models/overview.md)
- [Energy and Thermodynamics](../science/08-energy-thermodynamics/overview.md)
- [Fluids and Materials](../science/12-fluids-materials/overview.md)
- [The Domestic Refrigerator](../system-dossiers/refrigerator.md)
- [How Does a Room Cool?](../investigations/room-cooling.md)
