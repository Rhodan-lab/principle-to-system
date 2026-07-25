---
title: "How Does a Room Cool?"
slug: "investigation-room-cooling"
domain: "experience"
status: draft
prerequisites: [02-measurement-uncertainty, 03-mathematical-models, 08-energy-thermodynamics]
connections: [04-probability-statistics, system-dossier-refrigerator]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# How Does a Room Cool?

## 1. Question

After a cooling source is switched off, how does room temperature approach the surrounding temperature?

## 2. Why the answer is not obvious

A room is not one uniform object. Air mixes imperfectly, walls store energy, sunlight changes, doors open, people and electronics release heat, and the outdoor temperature may change during the observation.

A smooth cooling curve may therefore be only an approximation of several interacting processes.

## 3. Competing models

### Model A: constant cooling rate

$$T(t)=T_0-rt$$

This model assumes temperature falls by the same amount during every equal time interval. It is simple but predicts continued cooling even after the room reaches its environment.

### Model B: exponential approach

$$T(t)=T_{env}+(T_0-T_{env})e^{-t/\tau}$$

Here $T_{env}$ is the effective environmental temperature and $\tau$ is a time constant. Cooling is fastest when the temperature difference is largest and slows near equilibrium.

### Model C: disturbed exponential model

The exponential model is used only between disturbances. Door openings, sunlight, occupants, or equipment create step changes or alter $T_{env}$ and $\tau$.

## 4. Variables and units

| Quantity | Symbol | Unit |
| --- | --- | --- |
| Room temperature | $T$ | degrees Celsius or kelvin |
| Initial room temperature | $T_0$ | degrees Celsius or kelvin |
| Effective environmental temperature | $T_{env}$ | degrees Celsius or kelvin |
| Time | $t$ | seconds or minutes |
| Linear cooling rate | $r$ | kelvin per minute |
| Thermal time constant | $\tau$ | minutes |

Temperature differences have the same numerical magnitude in kelvin and degrees Celsius.

## 5. Safe observation method

This investigation does not require heating devices, exposed electrical equipment, or modification of an air conditioner.

Choose one method:

1. Record an already-occurring room-temperature change with a household thermometer.
2. Use temperature logs from a safe consumer sensor.
3. Work entirely from a hypothetical dataset.

Record temperature at equal intervals. Also note door openings, direct sunlight, occupants, fans, cooling operation, and sensor position.

Do not place sensors inside electrical equipment or block ventilation openings.

## 6. Data-recording structure

| Time | Temperature | Door state | Occupants | Sunlight | Cooling device | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 0 min |  |  |  |  |  |  |
| 5 min |  |  |  |  |  |  |
| 10 min |  |  |  |  |  |  |

## 7. Uncertainty and confounders

Possible measurement issues include:

- thermometer resolution and calibration;
- sensor response delay;
- vertical temperature gradients;
- warm walls or furniture continuing to release heat;
- changing outdoor conditions;
- local airflow from fans or vents;
- heat from people, computers, or lighting.

A sensor near a wall or window may describe a local microenvironment rather than the room average.

## 8. Analysis method

### Visual comparison

Plot temperature against time. Ask:

- Does the curve remain approximately straight?
- Does it flatten as it approaches an apparent equilibrium?
- Are there abrupt changes aligned with recorded disturbances?

### Test the exponential model

Estimate $T_{env}$. For data above that temperature, calculate

$$\ln(T-T_{env})$$

If the one-time-constant model is reasonable, a plot of $\ln(T-T_{env})$ against $t$ should be approximately linear between disturbances.

### Estimate the time constant

Under the exponential model, after one time constant the remaining temperature difference is about $e^{-1}$ of its initial value:

$$T(\tau)-T_{env}\approx0.37(T_0-T_{env})$$

Use this as an estimate rather than an exact rule for a real room.

## 9. Interpretation limits

A good curve fit does not prove that the room is physically uniform. Different combinations of wall heat capacity, airflow, leakage, and internal heat generation can produce similar temperature curves.

The fitted $T_{env}$ may represent a mixture of outdoor air, neighbouring rooms, walls, and ongoing heat sources rather than one directly measured temperature.

## 10. Model revision

Revise the model when residuals show structure:

- repeated oscillation may suggest control cycling;
- two distinct slopes may suggest changing airflow or a second thermal store;
- abrupt jumps may indicate door opening or sensor movement;
- a plateau above outdoor temperature may indicate internal heat generation.

A more detailed two-store model could separate room air and building materials, but added complexity is justified only if it improves explanation or prediction.

## 11. Transfer questions

- Why does a small empty room respond differently from a furnished room?
- How would high humidity influence comfort even at the same measured temperature?
- Why can a refrigerator cabinet be modelled similarly to a room, despite its much smaller scale?
- What measurements would distinguish air leakage from weak insulation?
- How could sensor placement create false conclusions about cooling performance?

## 12. Module links

- [Measurement and Uncertainty](../foundations/02-measurement-uncertainty/overview.md)
- [Mathematical Models](../foundations/03-mathematical-models/overview.md)
- [Energy and Thermodynamics](../science/08-energy-thermodynamics/overview.md)
- [The Domestic Refrigerator](../system-dossiers/refrigerator.md)
