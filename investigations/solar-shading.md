---
title: "How Does Partial Shading Change Solar Output?"
slug: investigation-solar-shading
domain: experience
experience_type: investigation
status: reviewed
artifact_revision: 1
release_status: draft
prerequisites: [02-measurement-uncertainty, 04-probability-statistics, 10-electricity-magnetism, 18-semiconductors-electronics]
connections: [concept-patterns, concept-cause-and-effect, system-dossier-solar-battery-microgrid, failure-pattern-protection-coordination, design-challenge-resilient-charging-hub]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# How Does Partial Shading Change Solar Output?

## 1. Question

How does the pattern and timing of partial shade change the power and energy yield of a photovoltaic array?

## 2. Why the answer is not obvious

A shaded fraction of area does not always produce the same fractional loss of array power. Cells may be connected in series and parallel; bypass devices can change the active circuit; an inverter may search among several operating points; temperature and irradiance change at the same time; and a shadow moves across modules rather than remaining uniform.

The investigation therefore distinguishes a simple area model from electrical mismatch and time-dependent system behavior.

## 3. Competing models

### Model A: proportional-area model

$$P=P_{clear}(1-f_s)$$

where $f_s$ is shaded area fraction. This model assumes uniform independent conversion and no series mismatch.

### Model B: string-limited model

$$I_{string}\approx \min(I_1,I_2,\ldots,I_n)$$

for a simplified series string before bypass behavior. One strongly limited section can constrain the current of the connected string.

### Model C: empirical system model

$$P(t)=P_{clear}(t)\,r\bigl(s(t),T(t),m(t)\bigr)$$

where $s(t)$ describes the shadow pattern, $T(t)$ temperature, $m(t)$ operating mode, and $r$ is estimated from data. This model admits nonlinear and history-dependent behavior without claiming one universal circuit response.

## 4. Variables and units

| Quantity | Symbol | Unit |
| --- | --- | --- |
| Clear-reference power | $P_{clear}$ | W or normalized units |
| Observed power | $P$ | W or normalized units |
| Shaded-area fraction | $f_s$ | dimensionless |
| Irradiance | $G$ | W/m² |
| Module or air temperature | $T$ | °C or K |
| Time | $t$ | s, min, or h |
| Energy over interval | $E$ | Wh or normalized power-time units |
| Relative power | $P/P_{clear}$ | dimensionless |

A normalized dataset is acceptable when no real PV data are available.

## 5. Safe observation or simulation method

Use one of these safe options:

1. analyse a public or teacher-provided PV power dataset containing naturally occurring shade;
2. use a spreadsheet or code simulation with synthetic shadow patterns;
3. compare photographs or sun-path diagrams with existing inverter logs supplied by an adult or institution;
4. analyse the hypothetical dataset included in the recording structure.

Do not cover, touch, disconnect, open, rewire, climb onto, or electrically test an installed solar array. Do not create shadows by approaching roofs, live equipment, roadways, or restricted facilities. The investigation is about data and models, not field intervention.

## 6. Data-recording structure

| Time | Clear-reference power | Observed power | Relative power | Estimated shade fraction | Shadow location | Temperature | Notes |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| 09:00 | 0.62 | 0.60 | 0.97 | 0.00 | none | 27 | baseline |
| 10:00 | 0.78 | 0.55 | 0.71 | 0.12 | lower edge | 31 | moving shadow |
| 11:00 | 0.91 | 0.48 | 0.53 | 0.18 | one module section | 35 | possible bypass change |
| 12:00 | 1.00 | 0.84 | 0.84 | 0.20 | distributed | 39 | different pattern |
| 13:00 | 0.95 | 0.89 | 0.94 | 0.05 | edge | 41 | shadow leaving |

The values above are illustrative, not a claim about a particular array.

## 7. Uncertainty and confounders

Consider:

- irradiance changes caused by cloud and atmosphere;
- temperature effects on voltage and efficiency;
- uncertain shaded fraction from photographs;
- different module, string, optimizer, and inverter architectures;
- clipping, curtailment, battery charging limits, or load-following modes;
- sensor calibration and logging interval;
- soiling, degradation, or temporary obstruction;
- time mismatch between image and electrical data.

A clear-reference model must be justified. A nearby unshaded array can differ in orientation, temperature, or equipment.

## 8. Analysis method

Calculate relative output:

$$R_P(t)=\frac{P(t)}{P_{clear}(t)}$$

and compare it with the proportional prediction $1-f_s$. Plot residuals:

$$e(t)=R_P(t)-(1-f_s(t))$$

A large negative residual suggests that the proportional-area model underestimates mismatch or mode effects. Group observations by shadow pattern rather than only by shaded fraction.

Estimate energy loss over the observation window:

$$\Delta E=\sum_k\left[P_{clear,k}-P_k\right]\Delta t$$

Use consistent intervals and report missing data. Compare models using residual patterns and out-of-sample intervals rather than selecting the equation with the smallest in-sample error alone.

## 9. Interpretation limits

The investigation cannot infer internal cell temperature, diode operation, exact string topology, or inverter algorithm from power logs alone. Similar output curves can arise from cloud, clipping, curtailment, sensor error, or shading. A correlation between a visible shadow and a power change supports a hypothesis but does not establish the full electrical mechanism.

Results from one array, season, or shadow shape do not transfer automatically to another installation.

## 10. Model revision

Revise the model when:

- equal shaded fractions produce different power loss;
- the same shadow pattern produces different loss at different irradiance;
- abrupt steps suggest a bypass or control-mode transition;
- lag suggests logging or control delay;
- the clear-reference model systematically misses temperature or cloud effects;
- residuals cluster by module string, orientation, or time of day.

A useful revised model may classify operating regimes instead of forcing one smooth equation across all conditions.

## 11. Transfer questions

- Why can a narrow shadow across several series-connected cells matter more than a larger shadow on an electrically independent section?
- How would module-level power electronics change the expected pattern?
- What information would distinguish shading from curtailment?
- Why is annual energy loss not determined by peak power loss alone?
- Which design decisions reduce sensitivity without assuming shade can be eliminated?
- How would uncertainty in the clear reference affect the conclusion?

## 12. Sources and module links

- U.S. Department of Energy, *Photovoltaic System Design and Energy Yield*: https://www.energy.gov/cmei/systems/photovoltaic-system-design-and-energy-yield
- U.S. Department of Energy, *Solar Photovoltaic System Design Basics*: https://www.energy.gov/cmei/systems/solar-photovoltaic-system-design-basics
- U.S. Department of Energy, *Solar Integration: Solar Energy and Storage Basics*: https://www.energy.gov/cmei/systems/solar-integration-solar-energy-and-storage-basics
- [Measurement and Uncertainty](../foundations/02-measurement-uncertainty/overview.md)
- [Probability and Statistics](../foundations/04-probability-statistics/overview.md)
- [Electricity and Magnetism](../science/10-electricity-magnetism/overview.md)
- [Semiconductors and Electronics](../technology/18-semiconductors-electronics/overview.md)
- [A Solar–Battery Microgrid](../system-dossiers/solar-battery-microgrid.md)
