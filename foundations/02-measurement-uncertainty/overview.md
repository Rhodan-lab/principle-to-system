---
title: "Measurement, units, error, and uncertainty"
slug: 02-measurement-uncertainty
module: "Module 02"
domain: foundations
status: reviewed
prerequisites: [01-scientific-reasoning]
connections: [06-matter-quantum]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# Measurement, units, error, and uncertainty

## 1. The central questions

How can a physical or chemical quantity be described so that another person can measure the same thing? What information must accompany a measured value? How are calibration, traceability, resolution, repeatability, systematic effects, and uncertainty related? Measurement connects models to observations, but a numerical display is not a complete measurement result unless the measurand, procedure, units, conditions, and relevant uncertainty are understood.

## 2. Observable phenomena

Repeated readings of the same object may vary. Two instruments may agree closely yet both be biased relative to a reference. A thermometer can respond slowly, a ruler can expand with temperature, and a sensor can change the system it measures. A digital display may show many digits even when only a few are supported by calibration and noise.

These effects arise from the full measurement process: the definition of the measurand, sampling in space and time, sensor interaction, calibration, environmental influence, data processing, and reporting. Uncertainty is therefore evaluated from all relevant information, not only from the scatter of repeated readings.

## 3. Essential concepts

**Measurement:** The experimental process of obtaining one or more quantity values that can reasonably be attributed to a quantity. A measurement requires a defined measurand, procedure, calibrated measuring system, and specified conditions.

**Measurand:** The quantity intended to be measured. “Length of the beam” is incomplete if thermal expansion matters; “length of the beam at $20\ ^\circ\mathrm{C}$ under specified support conditions” is better defined.

**Measurement result:** A set of quantity values attributed to a measurand together with relevant information. It is commonly expressed as a measured value plus measurement uncertainty and units.

**Reference quantity value:** A value used as a basis for comparison. It may come from a calibrated standard, a certified reference material, a reference procedure, or a conventional definition.

**Measurement error:** A measured quantity value minus a reference quantity value. Error can sometimes be estimated or corrected, but the exact error relative to an unknown true value is generally unknown.

**Systematic measurement error:** A component of error that remains constant or changes predictably under repeated measurement conditions. A known estimate can be corrected, but uncertainty remains in the correction.

**Random measurement error:** A component of error that varies unpredictably in replicate measurements. Repetition can reduce the uncertainty associated with estimating a mean, but it does not remove systematic effects.

**Measurement uncertainty:** A non-negative parameter characterizing the dispersion of quantity values attributed to the measurand, based on the information used. It is not itself “the error” and is not merely an interval.

**Accuracy, trueness, and precision:** Accuracy is qualitative closeness between a measured value and a true value. Trueness concerns agreement between the average of many replicate values and a reference value. Precision concerns agreement among replicate values under stated conditions. Accuracy is not assigned a numerical value and should not be used as a synonym for precision.

**Resolution:** The smallest change in a quantity that produces a perceptible change in indication. Resolution does not establish accuracy or uncertainty by itself.

**Metrological traceability:** A property of a measurement result whereby it can be related to a reference through a documented, unbroken calibration chain, each link contributing to measurement uncertainty.

## 4. Mechanisms and causal chains

Consider measuring liquid temperature with a contact thermometer:

```text
liquid state
→ heat exchange with sensor
→ temperature-dependent sensor property
→ electrical or visual indication
→ calibration function
→ corrected value and uncertainty
```

Uncertainty can enter because the liquid is not uniform, the sensor has finite response time, the sensor perturbs the liquid, calibration coefficients are uncertain, the response is non-linear, the display is quantized, or the reading time is inconsistent. The first task is not to label every effect “random” or “systematic,” but to construct a measurement model and evaluate each relevant input.

## 5. Important quantities

| Quantity | Symbol | SI unit | Dimension | Careful description |
| --- | --- | --- | --- | --- |
| Length | $l,x,r$ | metre, $\mathrm{m}$ | $L$ | Spatial extent or separation defined by a measurement procedure. |
| Mass | $m$ | kilogram, $\mathrm{kg}$ | $M$ | Physical quantity associated with inertia and gravitation; operational meaning depends on the model and procedure. |
| Time | $t$ | second, $\mathrm{s}$ | $T$ | Duration between specified events, realized using periodic processes. |
| Thermodynamic temperature | $T$ | kelvin, $\mathrm{K}$ | $\Theta$ | Thermodynamic state quantity defined through the kelvin and Boltzmann constant; it is not generally identical to average translational kinetic energy. |
| Electric current | $I$ | ampere, $\mathrm{A}$ | $I$ | Rate of electric-charge flow through a surface. |
| Amount of substance | $n$ | mole, $\mathrm{mol}$ | $N$ | Number of specified elementary entities scaled by the Avogadro constant. |
| Luminous intensity | $I_v$ | candela, $\mathrm{cd}$ | $J$ | Luminous flux per unit solid angle in a specified direction, spectrally weighted for human vision. |

The SI base units are defined by assigning exact numerical values to seven defining constants. Realizing a unit in practice still requires an experimental procedure with uncertainty.

## 6. Mathematical models and equations

### Type A evaluation from repeated observations

For $N$ observations $x_i$ obtained under specified repeatability conditions, the sample mean is

$$\bar{x}=\frac{1}{N}\sum_{i=1}^{N}x_i,$$

and the experimental standard deviation is

$$s(x)=\sqrt{\frac{1}{N-1}\sum_{i=1}^{N}(x_i-\bar{x})^2}.$$

When observations are independent and identically distributed with finite variance, the estimated standard uncertainty of the mean is

$$u(\bar{x})=\frac{s(x)}{\sqrt{N}}.$$

This evaluates only the repeatability contribution. Calibration, resolution, drift, environmental corrections, sampling, and model uncertainty may require Type B evaluation or additional models.

### Propagation through a measurement model

For an output estimate

$$y=f(x_1,x_2,\ldots,x_N),$$

a first-order approximation to combined standard uncertainty is

$$u_c^2(y)=\sum_{i=1}^{N}\left(\frac{\partial f}{\partial x_i}\right)^2u^2(x_i)
+2\sum_{i<j}\frac{\partial f}{\partial x_i}\frac{\partial f}{\partial x_j}u(x_i,x_j),$$

where $u(x_i,x_j)$ denotes covariance. The covariance terms vanish only when the input estimates are uncorrelated.

For strongly non-linear models, asymmetric distributions, discontinuities, or bounded inputs, propagation of distributions using Monte Carlo methods may be more appropriate than first-order linearization.

### Reporting an expanded uncertainty

A result may be reported as

$$Y=y\pm U,\qquad U=k\,u_c(y),$$

where $k$ is a coverage factor chosen for a stated coverage objective under a stated distributional approximation. The report should identify $k$, the intended coverage, and the method used.

## 7. Definitions of symbols and units

- $x_i$: Individual observed value; same unit as the measurand.
- $\bar{x}$: Mean of replicate values.
- $N$: Number of observations; dimensionless integer.
- $s(x)$: Experimental standard deviation.
- $u(x_i)$: Standard uncertainty of input estimate $x_i$.
- $u(x_i,x_j)$: Estimated covariance between input estimates.
- $u_c(y)$: Combined standard uncertainty of output estimate $y$.
- $U$: Expanded uncertainty.
- $k$: Coverage factor; dimensionless.
- $\partial f/\partial x_i$: Sensitivity coefficient, with units of $y$ per unit of $x_i$.

## 8. Assumptions and approximations

- The measurand and measurement conditions are defined adequately for the intended use.
- Replicate observations used in the simple $s/\sqrt{N}$ formula are sufficiently independent and generated under stable conditions.
- A Type A evaluation does not automatically require a normal population; distributional assumptions matter when constructing coverage intervals or using small-sample approximations.
- First-order propagation assumes the model is adequately linear over the relevant input distributions.
- Correlation among inputs must be represented rather than silently ignored.
- Corrections for known systematic effects should be applied when practical, with uncertainty assigned to the corrections.
- More displayed digits do not justify more reported information than the uncertainty supports.

## 9. Spatial and temporal scales

Measurement spans subatomic, laboratory, industrial, geophysical, and astronomical scales. Different scales require different measurands, sampling strategies, reference standards, and uncertainty models. At small scales, quantum theory may constrain which physical quantities can have simultaneously sharp states, but this is conceptually distinct from measurement uncertainty in metrology. At large scales, sampling and model uncertainty can dominate instrument resolution.

Temporal scale also matters. A rapidly changing measurand requires adequate sensor bandwidth and synchronized clocks. A slowly drifting instrument may appear precise over minutes but produce biased comparisons across months.

## 10. Common misconceptions

- **Error means a mistake:** Measurement error is a technical difference from a reference value; mistakes are separate procedural failures.
- **Uncertainty is the same as error:** Error is a difference; uncertainty characterizes dispersion of values attributed to the measurand.
- **Many decimal places mean accuracy:** Display resolution can exceed calibration quality and useful precision.
- **Repeating measurements removes all uncertainty:** Repetition mainly reduces uncertainty in the mean from repeatability effects; common bias remains.
- **A calibration certificate makes an instrument permanently correct:** Calibration applies under stated conditions and at a time; drift, transport, use, and recalibration interval matter.
- **The true value can always be known exactly:** The true-value concept is idealized and generally unknowable in practice; some approaches focus instead on compatible measurement results and reference values.

## 11. Connections to other modules

- **01-scientific-reasoning:** Evidence quality depends on how quantities are defined and measured.
- **03-mathematical-models:** A measurement result depends on a model linking indications and inputs to the measurand.
- **04-probability-statistics:** Probability models support evaluation of sampling variation and uncertainty distributions.
- **05-computation-algorithms:** Numerical methods propagate uncertainty and implement calibration functions.
- **06-matter-quantum:** Atomic and quantum phenomena support modern unit realizations and precision instruments.

## 12. Sources

1. Bureau International des Poids et Mesures. (2019). *The International System of Units (SI)*, 9th ed. https://www.bipm.org/en/publications/si-brochure
2. Joint Committee for Guides in Metrology. (2008). *Evaluation of measurement data — Guide to the expression of uncertainty in measurement* (JCGM 100:2008). https://doi.org/10.59161/JCGM100-2008E
3. Joint Committee for Guides in Metrology. (2008). *Propagation of distributions using a Monte Carlo method* (JCGM 101:2008). https://doi.org/10.59161/JCGM101-2008
4. Joint Committee for Guides in Metrology. (2012). *International vocabulary of metrology* (JCGM 200:2012). https://doi.org/10.59161/JCGM200-2012
5. National Institute of Standards and Technology. *Metrological Traceability*. https://www.nist.gov/metrology/metrological-traceability
