---
title: "Design a Passive Cooler"
slug: "design-challenge-passive-cooler"
domain: "experience"
status: draft
prerequisites: [03-mathematical-models, 08-energy-thermodynamics, 12-fluids-materials]
connections: [17-materials-manufacturing, system-dossier-refrigerator, investigation-room-cooling]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# Design a Passive Cooler

## 1. Need and context

Design a portable container that keeps an already-cool payload below a chosen temperature for as long as practical without powered refrigeration.

The challenge is about slowing heat transfer and managing stored thermal energy. It is not about producing indefinite cooling from nothing.

## 2. Stakeholders

Possible stakeholders include:

- a person carrying food or temperature-sensitive non-medical items;
- someone who must lift, clean, repair, or store the container;
- people near the container who may be exposed to leaks or condensation;
- waste handlers and recyclers;
- communities where replacement materials are difficult to obtain.

## 3. Requirements and success measures

Choose and justify values for:

- payload volume;
- maximum total mass;
- initial payload temperature;
- maximum acceptable internal temperature;
- target duration;
- expected surrounding temperature;
- number and duration of openings;
- water resistance;
- cleaning requirements;
- reusable lifetime;
- acceptable material cost.

A valid design must specify a measurable success condition such as:

> The central payload temperature remains below the selected limit for the selected duration under the stated environmental conditions.

## 4. Hard constraints

- No powered compressor, fan, or thermoelectric module.
- No fire, reactive chemicals, pressurised vessels, dry ice, liquid nitrogen, or hazardous substances.
- No claim of maintaining a temperature indefinitely.
- Materials in direct contact with food must be appropriate for that use.
- Condensation and meltwater must be contained.
- The design must be liftable and openable by its intended user.

## 5. Assumptions

State assumptions explicitly. Examples:

- the payload begins uniformly cool;
- the surrounding temperature is approximately constant;
- the cooler remains shaded;
- the lid is opened twice;
- thermal properties are treated as constant;
- air inside is represented as one mixed region.

Then identify which assumptions are most likely to fail.

## 6. System boundary

The boundary may include:

- outer shell;
- insulation;
- reflective layer;
- inner liner;
- lid and seal;
- payload;
- reusable cold packs or ice;
- drainage or condensation control.

The environment includes surrounding air, ground contact, sunlight, rain, and user interactions.

## 7. Concept alternatives

Develop at least three distinct concepts.

### Concept A: thick insulation, low thermal mass

A lightweight container uses a thick insulating layer and tight seal. It is easy to carry but may warm quickly after repeated openings.

### Concept B: thinner insulation with high thermal mass

A stronger container carries more cold mass, such as sealed reusable water-based packs. It may maintain temperature longer but becomes heavier.

### Concept C: modular repairable cooler

Insulation panels, seals, hinges, and liner are replaceable. Initial construction may be more complex, but damaged parts do not require replacing the whole system.

An optional fourth concept may use evaporative cooling only where climate, water availability, hygiene, and containment make it appropriate. Evaporation should not be assumed effective in humid conditions.

## 8. Minimum quantitative model

Approximate steady heat leakage through the enclosure as

$$\dot Q=UA(T_{out}-T_{in})$$

where:

- $\dot Q$ is heat-transfer rate in watts;
- $U$ is the overall heat-transfer coefficient in watts per square metre-kelvin;
- $A$ is effective surface area in square metres;
- $T_{out}-T_{in}$ is the temperature difference in kelvin.

For a single flat insulation layer,

$$U\approx\frac{k}{L}$$

where $k$ is thermal conductivity and $L$ is insulation thickness. This approximation ignores thermal bridges, seals, corners, convection films, and air exchange.

A first estimate of warming time without phase change is

$$t\approx\frac{C\Delta T}{\dot Q}$$

where $C$ is total effective heat capacity and $\Delta T$ is the allowed temperature rise.

With melting ice or a phase-change pack, include latent heat:

$$Q_{stored}=mc\Delta T+mL_f$$

when the material warms to its melting point, melts, and then continues warming. Use only safe, sealed, appropriate materials.

## 9. Opening losses

Opening the lid replaces some cool internal air with warmer air, but the air itself may store less energy than the payload and container walls. The larger effect may come from:

- warm humid air entering and condensing;
- direct exposure of payload surfaces;
- disruption of internal temperature stratification;
- long open duration;
- repeated access.

A useful redesign may therefore change access behaviour: small compartments, removable trays, or a secondary flap can reduce disturbance without changing insulation.

## 10. Trade-off matrix

Score concepts qualitatively or with measured estimates, but explain every score.

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

Do not combine all criteria into one number unless the weighting values are stated and justified.

## 11. Failure modes and safeguards

| Failure mode | Mechanism | Possible safeguard |
| --- | --- | --- |
| Lid leakage | Warm air and moisture enter through gaps | Compressible replaceable seal and latch |
| Thermal bridge | Highly conductive fastener bypasses insulation | Break conduction path or isolate fastener |
| Wet insulation | Water raises heat transfer and causes hygiene problems | Sealed liner, drainage, closed-cell material |
| Crushed insulation | Thickness decreases under load | Load-spreading shell or protected panels |
| Internal contamination | Difficult corners retain residue | Removable smooth liner |
| Meltwater leak | Seal or container fails | Secondary containment and stable pack geometry |
| Excess mass | Thermal storage overwhelms portability | Set mass budget before choosing cold mass |
| Solar heating | Dark exterior absorbs radiation | Shade strategy and reflective exterior where durable |

## 12. Test plan

A safe test can use sealed water bottles as payload simulators and a household thermometer or temperature logger.

Record:

- ambient temperature;
- initial payload temperature;
- temperatures at fixed positions and intervals;
- opening events;
- mass of cold packs;
- visible condensation or leakage;
- final payload temperature.

Compare the observed warming curve with the minimum model. Do not tune the model only to match one test; use a second condition to see whether it predicts anything new.

## 13. Selected concept and rationale

Select a concept only after the model, trade-off matrix, and failure analysis are complete.

A strong rationale has this form:

```text
Because the main requirement is ______,
and the dominant heat path appears to be ______,
we selected ______.
This sacrifices ______ in exchange for ______.
The most important remaining risk is ______,
which we will test by ______.
```

## 14. Evidence that could change the decision

Examples include:

- tests show lid leakage dominates wall conduction;
- the insulation absorbs water;
- the selected cold mass exceeds the lifting limit;
- the container cannot be cleaned adequately;
- a locally available material performs similarly and is easier to replace;
- field conditions are more humid or hotter than assumed.

## 15. Module links

- [Mathematical Models](../foundations/03-mathematical-models/overview.md)
- [Energy and Thermodynamics](../science/08-energy-thermodynamics/overview.md)
- [Fluids and Materials](../science/12-fluids-materials/overview.md)
- [Materials and Manufacturing](../technology/17-materials-manufacturing/overview.md)
- [The Domestic Refrigerator](../system-dossiers/refrigerator.md)
- [How Does a Room Cool?](../investigations/room-cooling.md)
