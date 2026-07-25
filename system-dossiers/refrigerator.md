---
title: "The Domestic Refrigerator"
slug: "system-dossier-refrigerator"
domain: "experience"
status: draft
prerequisites: [08-energy-thermodynamics, 12-fluids-materials, 20-sensors-control-infrastructure]
connections: [17-materials-manufacturing, concept-energy-and-matter, concept-systems-and-models]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# The Domestic Refrigerator

A refrigerator does not manufacture cold. It uses work to move thermal energy from a cooler enclosed space to a warmer room.

## 1. The observable system

Food placed inside becomes cooler than the surrounding room. The cabinet releases heat near its rear or underside. The compressor runs intermittently rather than continuously. Frost may form where humid air meets a sufficiently cold surface.

These observations already imply three things:

- energy leaves the cabinet;
- additional energy enters through the electrical supply;
- a control system switches the cooling process according to temperature.

## 2. System boundary and environment

A useful boundary includes the insulated cabinet, refrigerant loop, compressor, heat exchangers, expansion device, temperature sensor, and controller.

The environment includes the room air, electrical grid, food and air introduced when the door opens, and the user who changes the temperature setting.

Changing the boundary changes the accounting. If the entire room and refrigerator are treated as one closed system, the room gains heat overall because the electrical work eventually becomes thermal energy.

## 3. Inputs, outputs, stores, and flows

| Category | Examples |
| --- | --- |
| Inputs | Electrical work, warm food, room heat leaking through insulation, humid room air entering through the door |
| Outputs | Heat rejected to the room, condensed water, sound and vibration |
| Stores | Thermal energy in food and cabinet materials, refrigerant internal energy, pressure differences |
| Flows | Refrigerant mass flow, heat flow, electrical current, control information |

## 4. Scientific principles used

### First law of thermodynamics

For a repeating refrigeration cycle, the heat rejected to the room is approximately

$$Q_H = Q_C + W$$

where $Q_C$ is heat removed from the cabinet, $W$ is compressor work, and $Q_H$ is heat released to the room.

### Phase change

The refrigerant absorbs substantial energy while evaporating at low pressure and releases energy while condensing at higher pressure. Phase change allows large heat transfer without requiring an equally large temperature change of the refrigerant.

### Pressure-temperature relationship

Changing refrigerant pressure changes the temperature at which evaporation or condensation occurs. The compressor and expansion device therefore create two pressure regions that make heat flow possible in the desired locations.

### Heat transfer

Heat crosses surfaces by conduction, convection, and radiation. The evaporator must accept heat from cabinet air, while the condenser must reject heat to room air. Insulation slows unwanted heat leakage through the cabinet walls.

## 5. Components and functions

| Component | Function | Consequence if removed or degraded |
| --- | --- | --- |
| Compressor | Raises refrigerant pressure and drives circulation | Pressure difference collapses; sustained cooling stops |
| Condenser | Rejects heat to the room and condenses refrigerant | High-side temperature and pressure rise; efficiency and reliability fall |
| Expansion device | Drops pressure and meters refrigerant flow | Evaporator receives the wrong pressure or mass flow |
| Evaporator | Absorbs heat inside the cabinet | Cabinet cannot transfer heat effectively into the cycle |
| Refrigerant | Transports energy through compression and phase change | Cycle cannot operate as designed |
| Insulation and door seal | Reduce parasitic heat and moisture entry | Compressor runs longer; condensation and frost increase |
| Temperature sensor | Measures controlled condition | Controller acts on incorrect or missing information |
| Controller | Starts and stops cooling | Temperature may drift, oscillate, or overcool |

## 6. Interaction architecture

```text
cabinet heat
→ evaporator
→ low-pressure refrigerant vapour
→ compressor
→ high-pressure hot vapour
→ condenser
→ high-pressure liquid
→ expansion device
→ low-pressure cold mixture
→ evaporator
```

A separate information loop operates alongside the energy loop:

```text
cabinet temperature
→ sensor
→ controller
→ compressor command
→ cooling rate
→ cabinet temperature
```

## 7. A minimum mathematical model

The cabinet can be approximated as one thermal store:

$$C\frac{dT}{dt}=\dot Q_{leak}+\dot Q_{load}-\dot Q_{cool}$$

where:

- $C$ is the effective heat capacity of cabinet contents in joules per kelvin;
- $T$ is cabinet temperature in kelvin or degrees Celsius for temperature differences;
- $\dot Q_{leak}$ is heat entering through walls and seals in watts;
- $\dot Q_{load}$ is heat introduced by food, air exchange, lights, or fans;
- $\dot Q_{cool}$ is heat removed by the evaporator in watts.

A simple leakage model is

$$\dot Q_{leak}=UA(T_{room}-T)$$

where $U$ is an overall heat-transfer coefficient and $A$ is cabinet surface area.

The coefficient of performance is

$$COP_R=\frac{Q_C}{W}$$

A larger value means more cabinet heat is removed per unit of compressor work.

## 8. Control and feedback

Many refrigerators use on-off control with hysteresis. The compressor starts above an upper temperature threshold and stops below a lower threshold. Two thresholds prevent rapid switching around one exact setpoint.

This creates a temperature cycle rather than a perfectly constant temperature. Narrower hysteresis reduces temperature variation but may increase switching frequency. Wider hysteresis protects equipment from frequent starts but permits larger temperature swings.

## 9. Failure modes

### Dirty or obstructed condenser

Reduced heat rejection raises operating temperatures and pressures. The compressor must work harder, while cooling capacity may fall.

### Damaged door seal

Warm humid air leaks inward. The added sensible and latent heat increases compressor runtime, and water may freeze on cold surfaces.

### Incorrect refrigerant charge or restricted flow

The evaporator may be underfed or flooded. Both conditions reduce useful heat transfer and can damage the compressor.

### Sensor or controller fault

The physical refrigeration loop may remain functional while the information loop fails. The result can be excessive cycling, continuous operation, or unsafe temperature drift.

### Frost accumulation

Ice adds thermal resistance and restricts airflow. A surface can remain cold while heat transfer into the refrigerant becomes worse.

## 10. Efficiency and performance

Efficiency depends on more than compressor quality. Important variables include:

- temperature difference between cabinet and room;
- condenser airflow;
- evaporator airflow;
- insulation thickness and thermal bridges;
- door-opening frequency;
- amount, temperature, and arrangement of stored material;
- control settings;
- refrigerant properties and pressure losses.

Lowering the cabinet setpoint increases the required temperature lift and usually reduces efficiency. Improving one subsystem can expose another bottleneck—for example, better insulation makes door openings a larger fraction of the remaining heat load.

## 11. Lifecycle and environmental consequences

The system has impacts during material production, refrigerant manufacture, appliance assembly, electricity use, maintenance, and disposal. A longer-lived appliance may avoid repeated manufacturing impacts, but an inefficient old appliance can consume more electricity. Refrigerant leakage and recovery matter independently of electricity use.

The correct comparison therefore depends on system boundary, electricity source, expected remaining life, repairability, and refrigerant management.

## 12. Alternative designs

- Vapour-compression systems dominate because they combine compactness, controllability, and useful efficiency.
- Absorption refrigeration replaces much compressor work with a heat-driven chemical cycle, useful where heat is available but usually less compact.
- Thermoelectric cooling has no circulating refrigerant and few moving parts, but is generally less efficient for large temperature-controlled volumes.
- Passive coolers use insulation, thermal mass, evaporation, or radiative heat transfer without active refrigeration, but cannot maintain arbitrary temperatures under all conditions.

## 13. Principle-to-system chain

```text
energy conservation
→ phase equilibrium and latent heat
→ pressure-dependent boiling temperature
→ compressor and expansion device
→ evaporator and condenser
→ closed refrigerant loop
→ temperature sensing and feedback control
→ insulated food-preservation system
```

## 14. Questions not yet answered

- How should performance be compared across different climates and usage patterns?
- Which losses dominate in a particular appliance?
- How do refrigerant choice, compressor design, and heat-exchanger geometry interact?
- When does repair have a lower lifecycle impact than replacement?
- How should temperature uniformity be measured inside a loaded cabinet?

## 15. Sources and module links

This dossier synthesises the repository's existing material. Its factual claims should be reviewed alongside the sources already recorded for:

- [Module 08 — Energy and Thermodynamics](../science/08-energy-thermodynamics/overview.md)
- [Module 12 — Fluids and Materials](../science/12-fluids-materials/overview.md)
- [Module 17 — Materials and Manufacturing](../technology/17-materials-manufacturing/overview.md)
- [Module 20 — Sensors, Control, and Infrastructure](../technology/20-sensors-control-infrastructure/overview.md)
- [Systems and Models](../concepts/systems-and-models.md)
- [Energy and Matter](../concepts/energy-and-matter.md)
