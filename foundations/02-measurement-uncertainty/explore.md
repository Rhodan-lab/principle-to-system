---
title: "Exploring measurement and uncertainty"
slug: 02-measurement-uncertainty-explore
module: "Module 02"
domain: foundations
status: reviewed
prerequisites: [01-scientific-reasoning]
connections: [06-matter-quantum]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# Exploring measurement and uncertainty

## 1. Observation prompts

- Find three safe measuring devices such as a tape measure, kitchen scale, clock, or room thermometer. Record the displayed resolution. What additional information would be needed to estimate uncertainty?
- As a passenger, or using a recorded dashboard video, observe whether a vehicle speed display changes smoothly or in discrete steps. Which changes might reflect real motion, sampling, filtering, or display quantization?
- Compare the dimensions printed on two packages with nominally identical products. How might manufacturing variation, sampling, and legal tolerances affect the stated quantity?
- Observe a room thermometer after moving it between locations. How long does it take to approach a stable indication, and what does that reveal about response time?

## 2. Prediction questions

- A room is measured using a short ruler and then a long tape. Which method is more likely to accumulate alignment and repositioning effects? Which might be affected by tension or sag?
- Density is calculated from mass divided by three measured dimensions. If each dimension has a relative standard uncertainty of 1% and mass has 5%, which contribution dominates under an uncorrelated first-order model?
- A scale reads 5 g when empty. What happens to the mean and standard deviation of repeated measurements if the offset remains constant?
- Two sensors agree to every displayed digit. Does this establish that either is traceable or accurate?

## 3. Worked reasoning examples

### Area from correlated or uncorrelated measurements

A rectangle has

$$L=50.0\ \mathrm{m},\qquad u(L)=0.5\ \mathrm{m},$$

$$W=20.0\ \mathrm{m},\qquad u(W)=0.2\ \mathrm{m}.$$

The model is $A=LW$, giving $A=1000\ \mathrm{m^2}$. If $L$ and $W$ are uncorrelated,

$$\frac{u_c(A)}{A}=\sqrt{\left(\frac{u(L)}{L}\right)^2+\left(\frac{u(W)}{W}\right)^2}
=\sqrt{0.01^2+0.01^2}=0.0141.$$

Therefore,

$$u_c(A)\approx14\ \mathrm{m^2},$$

and a suitable standard-uncertainty statement is

$$A=(1000\pm14)\ \mathrm{m^2}.$$

This result depends on the measurement model and the assumption of negligible covariance. If both dimensions were calibrated using the same biased scale, a covariance term could matter.

### Repetition does not remove every contribution

Suppose a stable offset $b$ and independent random terms $\epsilon_i$ produce

$$x_i=x_{\mathrm{ref}}+b+\epsilon_i.$$

Averaging many observations reduces the random contribution to the mean under suitable conditions, but the offset $b$ remains. Repetition estimates repeatability; calibration and other information are needed to evaluate systematic effects.

## 4. Thought experiments

- **Perfectly stable ruler:** A ruler has negligible thermal expansion, but a steel beam changes length with temperature. Is the measurand “beam length” sufficiently defined?
- **Infinite repetition:** Under what assumptions would a sample mean converge? What if observations drift, are correlated, or share one calibration bias?
- **More digits:** Imagine a display changing from 0.1-unit resolution to 0.0001-unit resolution without improving the sensor. What information has actually improved?
- **Two laboratories:** Two laboratories report different values with overlapping uncertainty intervals. What evidence would you need before calling the results incompatible?

## 5. Household and browser-based explorations

- **Reaction-time repeatability:** Use a privacy-respecting offline or browser timer, record at least ten trials, and calculate the mean and sample standard deviation. Treat the result as repeatability data, not a complete uncertainty budget.
- **Volume and mass comparison:** At room temperature, use a clean measuring cup and a kitchen scale to compare a nominal water volume with measured mass. Do not interpret one difference as the calibration error of one device; list alternative contributions such as temperature, meniscus reading, container residue, scale resolution, and cup tolerances.
- **Ruler comparison:** Measure one object with two rulers. Repeat after changing orientation and observer. Separate within-method variation from differences between instruments.
- **Response-time curve:** Safely move a room thermometer between two indoor locations and record indications at fixed intervals. Plot the approach to the new stable value.

## 6. Model-building prompts

- Build an uncertainty budget for measuring a tabletop length. Include resolution, repeatability, alignment, temperature, and calibration information. Mark which contributions are estimated from data and which come from other information.
- Model a first-order temperature sensor using

  $$\frac{dT_s}{dt}=\frac{T-T_s}{\tau},$$

  where $T_s$ is the sensor indication, $T$ is the surrounding temperature, and $\tau$ is a time constant. What sampling interval is needed to observe the response?
- Derive the dimensions of wave speed from tension $F$ and linear mass density $\mu$ using $v=kF^a\mu^b$.
- Compare first-order uncertainty propagation with a simple Monte Carlo calculation for $A=LW$.

## 7. Self-explanation questions

- Why are error and uncertainty not interchangeable?
- How do accuracy, trueness, precision, repeatability, and resolution differ?
- Why is a measurement result incomplete without a measurand and relevant uncertainty?
- What is the difference between Type A and Type B evaluation?
- Why can two individually traceable inputs still be correlated?

## 8. Transfer questions

- How do sampling interval and timing uncertainty affect measurements from a computer server, weather station, or sensor network?
- How can measurement uncertainty influence a pass/fail manufacturing decision near a tolerance boundary?
- Why can a model trained on sensor data inherit calibration drift or changes in the measurement procedure?
- How should long-term environmental records document sensor replacement and algorithm changes?

## 9. Suggested learning paths

- **Next module:** Continue to **03-mathematical-models** to express measurement processes as functions and sensitivity coefficients.
- **Metrology:** Study the SI Brochure, VIM, GUM, and GUM supplements.
- **Instrumentation:** Learn transfer functions, calibration curves, sampling, filtering, and dynamic response.
- **Conformity assessment:** Explore how measurement uncertainty affects decisions against specifications.

## 10. Reasoning notes

Before calculating uncertainty:

1. Define the measurand and intended use.
2. Draw the measurement chain and write the measurement model.
3. Apply known corrections rather than hiding them inside a large uncertainty.
4. Include repeatability, calibration, resolution, environment, sampling, drift, and model effects where relevant.
5. Represent correlations and shared references.
6. Use first-order propagation only when it is adequate.
7. Report units, coverage convention, significant digits, and limitations consistently.

Uncertainty describes the quality of knowledge produced by a measurement process. It is neither a confession of failure nor a physical property attached to the object alone.
