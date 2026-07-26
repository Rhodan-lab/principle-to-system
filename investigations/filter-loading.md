---
title: "How Does Filter Loading Change Flow Resistance?"
slug: investigation-filter-loading
domain: experience
experience_type: investigation
status: reviewed
artifact_revision: 1
release_status: draft
prerequisites: [02-measurement-uncertainty, 03-mathematical-models, 12-fluids-materials]
connections: [concept-patterns, concept-cause-and-effect, system-dossier-drinking-water-network, failure-pattern-sensor-drift-hidden-degradation, design-challenge-nonpotable-rainwater-buffer]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# How Does Filter Loading Change Flow Resistance?

## 1. Question

As a filter accumulates retained material, how do pressure loss and flow change, and which model best identifies the point at which the original operating assumption no longer works?

## 2. Why the answer is not obvious

A filter is not a passive screen with one fixed resistance. Material can deposit on the surface, enter pores, rearrange, compress, detach, or create preferential channels. Pump behavior and control can keep either flow or pressure approximately constant, so the visible trend depends on what the system regulates.

This investigation uses synthetic or public data. It does not evaluate whether water is safe to drink and does not instruct learners to treat contaminated water.

## 3. Competing models

### Model A: constant resistance

$$\Delta p=R_0Q$$

where $Q$ is flow and $R_0$ is fixed resistance. This is a baseline that cannot represent loading.

### Model B: linear loading resistance

$$\Delta p=\left(R_0+\alpha M\right)Q$$

where $M$ is cumulative retained mass or a normalized loading index and $\alpha$ is an empirical coefficient.

### Model C: accelerating resistance

$$\Delta p=R_0Q\,e^{\beta M}$$

This can represent an accelerating rise but may overpredict outside the fitted range.

### Model D: regime model

Use one relation before a change point and another after it. A regime model may be more interpretable when cake formation, compression, channeling, or control saturation changes the mechanism.

## 4. Variables and units

| Quantity | Symbol | Unit |
| --- | --- | --- |
| Pressure difference | $\Delta p$ | Pa or kPa |
| Flow rate | $Q$ | m³/s, L/s, or normalized flow |
| Cumulative loading index | $M$ | kg, g, or dimensionless |
| Operating time | $t$ | min or h |
| Hydraulic resistance | $R$ | Pa·s/m³ or consistent normalized unit |
| Turbidity proxy or particle input | $C_{in}$ | stated unit |
| Model residual | $e$ | same unit as observed response |

Use one unit system throughout. A normalized dataset is acceptable when no operational dataset is available.

## 5. Safe observation or simulation method

Choose one safe method:

1. analyse a hypothetical dataset generated from the table below;
2. use a spreadsheet simulation in constant-flow and constant-pressure modes;
3. analyse public educational data that contain only operational variables;
4. observe pressure-drop information from a sealed consumer filter only when the manufacturer already provides it and no disassembly or water-quality claim is made.

Do not collect contaminated water, culture microorganisms, add treatment chemicals, open pressurized equipment, taste test water, or use the result to declare water potable. Do not modify a public or household drinking-water system.

## 6. Data-recording structure

| Interval | Loading index $M$ | Flow $Q$ | Pressure difference $\Delta p$ | Apparent resistance $\Delta p/Q$ | Operating mode | Notes |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0.0 | 1.00 | 10 | 10.0 | constant flow | clean baseline |
| 1 | 0.2 | 1.00 | 12 | 12.0 | constant flow | gradual rise |
| 2 | 0.4 | 1.00 | 15 | 15.0 | constant flow | gradual rise |
| 3 | 0.6 | 1.00 | 21 | 21.0 | constant flow | accelerating |
| 4 | 0.8 | 0.92 | 29 | 31.5 | actuator limit | flow begins falling |
| 5 | 1.0 | 0.78 | 35 | 44.9 | actuator limit | regime changed |

The values are illustrative and contain no water-safety information.

## 7. Uncertainty and confounders

Consider:

- pressure-sensor zero drift;
- flow-meter calibration;
- temperature-dependent viscosity;
- changing inlet particle concentration;
- pump or valve control behavior;
- air pockets or leaks;
- media compaction;
- channeling or detachment;
- data sampled before the system reaches a stable condition;
- using elapsed time as a poor proxy for cumulative loading.

A rising pressure difference can reflect more than retained material. A falling flow can reflect a pump limit or valve position rather than filter resistance alone.

## 8. Analysis method

Calculate apparent resistance:

$$R_{app,k}=\frac{\Delta p_k}{Q_k}$$

Fit the linear and accelerating models to an early subset, then test predictions on later points. Plot residuals against loading and time. A systematic residual pattern indicates that the model is missing a regime or variable.

Estimate a change point by comparing the prediction error of one model with a two-regime model. Avoid treating the best-fitting change point as a physical threshold without independent evidence.

For constant-pressure operation, compare measured flow with

$$Q_k=\frac{\Delta p}{R(M_k)}$$

For constant-flow operation, compare the pressure required to maintain $Q$. State which control mode the dataset represents.

## 9. Interpretation limits

The investigation can compare resistance models but cannot determine microbial safety, chemical removal, disinfection performance, or whether a real filter should remain in service. Operational decisions require validated procedures, qualified operators, manufacturer information, and regulatory requirements.

A model fitted to one medium, particle type, temperature, or loading rate may not transfer to another system. Apparent resistance also combines filter, housing, fittings, and measurement effects unless the boundary is isolated.

## 10. Model revision

Revise the model when:

- residuals accelerate with loading;
- flow changes despite an assumed constant-flow mode;
- pressure plateaus because an actuator or sensor saturates;
- apparent resistance falls, suggesting detachment or channeling;
- temperature explains part of the trend;
- repeated runs have different trajectories;
- a calibration check reveals sensor drift.

A useful revision may include temperature, inlet loading, or operating mode rather than only adding a higher-order curve.

## 11. Transfer questions

- How does constant-flow control hide increasing resistance?
- Why can a clean-looking pressure trend be misleading if the sensor drifts?
- Which residual pattern would suggest a sudden regime change?
- How would a parallel filter arrangement change the system response?
- What measurements distinguish media loading from pump degradation?
- Why is a hydraulic model not a water-quality guarantee?

## 12. Sources and module links

- U.S. Environmental Protection Agency, *Surface Water Treatment Rules*: https://www.epa.gov/dwreginfo/surface-water-treatment-rules
- U.S. Environmental Protection Agency, *Summary of Cyanotoxins Treatment in Drinking Water*: https://www.epa.gov/ground-water-and-drinking-water/summary-cyanotoxins-treatment-drinking-water
- U.S. Environmental Protection Agency, *Drinking Water Distribution System Tools and Resources*: https://www.epa.gov/dwreginfo/drinking-water-distribution-system-tools-and-resources
- [Measurement and Uncertainty](../foundations/02-measurement-uncertainty/overview.md)
- [Mathematical Models](../foundations/03-mathematical-models/overview.md)
- [Fluids and Materials](../science/12-fluids-materials/overview.md)
- [A Drinking-Water Treatment and Distribution Network](../system-dossiers/drinking-water-network.md)
