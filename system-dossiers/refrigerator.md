---
title: "The Domestic Refrigerator"
slug: system-dossier-refrigerator
domain: experience
experience_type: system-dossier
status: reviewed
prerequisites: [08-energy-thermodynamics, 12-fluids-materials, 20-sensors-control-infrastructure]
connections: [17-materials-manufacturing, concept-energy-and-matter, concept-systems-and-models, failure-pattern-feedback-instability, investigation-room-cooling, design-challenge-passive-cooler]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# The Domestic Refrigerator

A refrigerator does not create cold. It uses work to move thermal energy from a cooler cabinet to a warmer room.

## 1. Observable system

Food cools below room temperature, the rear or underside becomes warm, the compressor cycles, and frost can form when humid air reaches a cold surface.

## 2. System boundary and environment

The boundary includes the cabinet, refrigerant loop, compressor, evaporator, condenser, expansion device, sensor, controller, insulation, and door seal. The environment includes room air, electricity supply, food loads, door openings, and user settings.

## 3. Inputs, outputs, stores, and flows

| Type | Examples |
| --- | --- |
| Inputs | Electrical work, warm food, heat leakage, humid air |
| Outputs | Heat rejected to room, condensate, sound, vibration |
| Stores | Thermal energy in food and cabinet, refrigerant internal energy, pressure difference |
| Flows | Refrigerant mass, heat, electrical current, control information |

## 4. Scientific principles

For a repeating cycle, energy conservation gives

$$Q_H = Q_C + W$$

where $Q_C$ is heat removed from the cabinet, $W$ is compressor work, and $Q_H$ is heat rejected to the room.

Pressure changes alter refrigerant saturation temperature. Evaporation at low pressure absorbs energy; condensation at higher pressure releases energy. Conduction, convection, and radiation govern heat exchange through walls and heat exchangers.

## 5. Components and functions

| Component | Function | If degraded |
| --- | --- | --- |
| Compressor | Raises pressure and drives circulation | Sustained cooling falls or stops |
| Condenser | Rejects heat and condenses vapour | Pressure and temperature rise |
| Expansion device | Reduces pressure and meters flow | Evaporator is incorrectly supplied |
| Evaporator | Absorbs cabinet heat | Cooling capacity falls |
| Refrigerant | Transports energy through phase change | Cycle cannot operate as designed |
| Insulation and seal | Limit heat and moisture entry | Runtime, frost, and energy use increase |
| Sensor and controller | Close the temperature-control loop | Temperature drifts or cycling becomes abnormal |

## 6. Interaction architecture

```text
cabinet heat → evaporator → compressor → condenser → expansion device → evaporator
cabinet temperature → sensor → controller → compressor command → cooling rate
```

## 7. Quantitative model

A minimum cabinet model is

$$C\frac{dT}{dt}=UA(T_{room}-T)+\dot Q_{load}-\dot Q_{cool}$$

where $C$ is effective heat capacity in J/K, $U$ is overall heat-transfer coefficient in W/(m²·K), $A$ is area in m², and heat-flow terms are in W.

Refrigeration coefficient of performance is

$$COP_R=\frac{Q_C}{W}$$

The model treats the cabinet as one temperature and ignores spatial gradients, cycling details, pressure losses, and changing refrigerant properties.

## 8. Control and feedback

On-off control commonly uses hysteresis: cooling starts above an upper threshold and stops below a lower threshold. Narrow hysteresis reduces temperature variation but can increase switching. Wider hysteresis protects equipment but permits larger temperature swings.

## 9. Failure modes

- Dirty condenser: poorer heat rejection and higher operating pressure.
- Damaged seal: warm humid air enters, increasing load and frost.
- Restricted flow or incorrect refrigerant charge: poor heat transfer and possible compressor stress.
- Sensor fault: the physical loop works but the information loop fails.
- Frost accumulation: airflow and heat transfer decline.

## 10. Efficiency and performance

Performance depends on room temperature, setpoint, insulation, thermal bridges, condenser airflow, door openings, load temperature, refrigerant properties, and control settings. Improving one subsystem can expose another bottleneck.

## 11. Lifecycle consequences

Impacts include material production, refrigerant manufacture and leakage, electricity use, maintenance, repairability, and end-of-life recovery. Whether repair or replacement is preferable depends on appliance efficiency, expected remaining life, electricity source, and refrigerant management.

## 12. Alternative designs

- Vapour-compression: compact, controllable, and widely used.
- Absorption refrigeration: driven mainly by heat, but often bulkier and less efficient.
- Thermoelectric cooling: few moving parts, but generally less efficient for large volumes.
- Passive cooling: insulation and thermal storage without indefinite temperature control.

## 13. Principle-to-system chain

```text
energy conservation
→ phase equilibrium and latent heat
→ pressure-dependent saturation temperature
→ compressor and expansion device
→ evaporator and condenser
→ closed refrigerant loop
→ sensing and feedback
→ insulated food-preservation system
```

## 14. Unresolved questions

- Which losses dominate for a particular appliance and climate?
- How should temperature uniformity be measured in a loaded cabinet?
- When does repair have lower lifecycle impact than replacement?

## 15. Sources and module links

- NIST, *Computer Modeling of the Vapor Compression Cycle*: https://www.nist.gov/publications/computer-modeling-vapor-compression-cycle-constant-flow-area-expansion-device-final
- NIST, *Refrigerant Properties for Heat Transfer Analysis*: https://www.nist.gov/publications/refrigerant-properties-heat-transfer-analysis
- U.S. Department of Energy, *Refrigeration Products*: https://www.energy.gov/cmei/buildings/refrigeration-products
- [Energy and Thermodynamics](../science/08-energy-thermodynamics/overview.md)
- [Fluids and Materials](../science/12-fluids-materials/overview.md)
- [Sensors, Control, and Infrastructure](../technology/20-sensors-control-infrastructure/overview.md)
