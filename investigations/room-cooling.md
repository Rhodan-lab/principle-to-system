---
title: "How Does a Room Cool?"
slug: investigation-room-cooling
domain: experience
experience_type: investigation
status: reviewed
prerequisites: [02-measurement-uncertainty, 03-mathematical-models, 08-energy-thermodynamics]
connections: [04-probability-statistics, system-dossier-refrigerator, design-challenge-passive-cooler]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# How Does a Room Cool?

## 1. Question

After active cooling stops, how does room temperature approach its surroundings?

## 2. Why the answer is not obvious

Air mixes imperfectly. Walls and furniture store energy. Sunlight, doors, occupants, electronics, outdoor conditions, and sensor position can change during observation. One smooth curve can hide several interacting processes.

## 3. Competing models

### Model A: constant-rate change

$$T(t)=T_0-rt$$

This is easy to use over a short interval but predicts continued cooling even after equilibrium.

### Model B: exponential approach

$$T(t)=T_{env}+(T_0-T_{env})e^{-t/\tau}$$

Here $T_{env}$ is an effective surrounding temperature and $\tau$ is a time constant.

### Model C: disturbed exponential model

Use Model B only between disturbances. Door openings, sunlight, people, and equipment can change the effective environment or add step-like heat inputs.

## 4. Variables and units

| Quantity | Symbol | Unit |
| --- | --- | --- |
| Room temperature | $T$ | °C or K |
| Initial temperature | $T_0$ | °C or K |
| Effective environment | $T_{env}$ | °C or K |
| Time | $t$ | min or s |
| Linear rate | $r$ | K/min or K/s |
| Time constant | $\tau$ | min or s |

Temperature differences have the same numerical magnitude in kelvin and degrees Celsius.

## 5. Safe observation or simulation method

Use one of these options:

1. record an already-occurring temperature change with a household thermometer;
2. use logs from a safe consumer sensor;
3. analyse a hypothetical dataset.

Do not modify cooling equipment, place sensors inside electrical devices, block ventilation, or create extreme temperatures.

## 6. Data-recording structure

| Time | Temperature | Door | Occupants | Sunlight | Cooling state | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 0 min |  |  |  |  |  |  |
| 5 min |  |  |  |  |  |  |
| 10 min |  |  |  |  |  |  |

## 7. Uncertainty and confounders

Consider sensor resolution, calibration, response delay, vertical gradients, wall temperature, changing outdoor conditions, airflow, and internal heat sources. A sensor near a wall or window may represent a local microenvironment rather than a room average.

## 8. Analysis method

Plot temperature against time and compare residual patterns.

For the exponential model, estimate $T_{env}$ and examine

$$\ln(T-T_{env})$$

against time. Approximate linearity between disturbances supports—but does not prove—the one-time-constant model.

After one time constant,

$$T(\tau)-T_{env}\approx0.37(T_0-T_{env})$$

Use this as an estimate, not an exact law for a real room.

## 9. Interpretation limits

A good fit does not prove the room is uniform. Different combinations of leakage, thermal mass, airflow, and internal heating can produce similar curves. The fitted $T_{env}$ may represent several surroundings rather than one measured temperature.

## 10. Model revision

- repeated oscillation may indicate control cycling;
- two slopes may indicate a changing airflow path or second thermal store;
- abrupt changes may align with door openings or sensor movement;
- a plateau above outdoor temperature may indicate internal heat generation.

Add complexity only when it improves explanation or prediction.

## 11. Transfer questions

- Why does a furnished room respond differently from an empty room?
- What measurements distinguish leakage from weak insulation?
- How can sensor placement create a false conclusion?
- Why can a refrigerator cabinet use a similar minimum model?

## 12. Sources and module links

- OpenStax, *Calculus Volume 2 — Separable Equations and Newton's Law of Cooling*: https://openstax.org/books/calculus-volume-2/pages/4-3-separable-equations
- OpenStax, *Algebra and Trigonometry — Exponential and Logarithmic Models*: https://openstax.org/books/algebra-and-trigonometry/pages/6-7-exponential-and-logarithmic-models
- [Measurement and Uncertainty](../foundations/02-measurement-uncertainty/overview.md)
- [Mathematical Models](../foundations/03-mathematical-models/overview.md)
- [Energy and Thermodynamics](../science/08-energy-thermodynamics/overview.md)
