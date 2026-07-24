---
title: "Measurement, Units, Error, and Uncertainty"
slug: "02-measurement-uncertainty"
module: "Module 02: Measurement, units, error, and uncertainty"
domain: "foundations"
status: draft
prerequisites: ["01-scientific-reasoning"]
connections: ["03-kinematics-dynamics", "04-thermodynamics"]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Measurement, Units, Error, and Uncertainty

## 1. The central questions

How do we quantify the physical world in a way that is universally understood and reproducible? When we measure a physical quantity, how do we know the true value, and how do we quantify our doubt about that measurement? Measurement is the bridge between abstract mathematical models and physical reality. Without a rigorous framework for units, error, and uncertainty, scientific observations would be subjective and technological systems would fail to interoperate. The central questions of this module explore how we establish standard units, how we use dimensional analysis to verify physical relationships, and how we account for the inevitable imperfections in every measurement we make.

## 2. Observable phenomena

Every day, we interact with measurement systems. A digital scale reads the mass of ingredients, a speedometer indicates the velocity of a vehicle, and a thermometer displays the ambient temperature. However, these readings are never absolute truths. If you step on a bathroom scale three times in succession, you might get slightly different readings. If you measure the length of a table with a wooden ruler versus a laser measure, the results will differ in precision and accuracy. These phenomena highlight that every measurement is an approximation of a true value, bounded by the resolution of the instrument, the method of measurement, and environmental factors. The variations we observe are manifestations of random and systematic errors.

## 3. Essential concepts

**The International System of Units (SI):** The globally accepted system of measurement, based on seven defining constants of nature (such as the speed of light in vacuum and the Planck constant). From these constants, seven base units are derived: the metre (length), kilogram (mass), second (time), ampere (electric current), kelvin (thermodynamic temperature), mole (amount of substance), and candela (luminous intensity) [1].

**Dimensional Analysis:** A mathematical tool used to check the consistency of equations and to deduce the relationships between physical quantities. It relies on the principle that only quantities with the same dimensions can be added, subtracted, or equated. The dimensions of any physical quantity can be expressed as a product of the dimensions of the base quantities (e.g., Length $L$, Mass $M$, Time $T$).

**True Value vs. Measured Value:** The true value of a quantity is an idealized concept—the value that would be obtained by a perfect measurement. The measured value is the result of a physical measurement process, which always includes some error.

**Error:** The difference between the measured value and the true value. Error is traditionally categorized into two types:
*   **Systematic Error:** A consistent, repeatable error associated with faulty equipment or a flawed experimental design. It affects the accuracy of a measurement, shifting all measurements in the same direction (e.g., a scale that is not zeroed properly).
*   **Random Error:** Unpredictable fluctuations in the readings of a measurement apparatus, or in the experimenter's interpretation of the instrumental reading. It affects the precision of a measurement, causing data points to scatter around a mean value.

**Uncertainty:** A non-negative parameter characterizing the dispersion of the quantity values being attributed to a measurand, based on the information used [2]. While error is a single (usually unknown) value, uncertainty is a range or an interval. It quantifies the doubt about the measurement result.

**Accuracy and Precision:** Accuracy refers to the closeness of agreement between a measured quantity value and a true quantity value of a measurand. Precision refers to the closeness of agreement between indications or measured quantity values obtained by replicate measurements on the same or similar objects under specified conditions [3].

**Significant Figures:** The digits in a measurement that carry meaning contributing to its precision. This includes all certain digits plus one estimated digit.

## 4. Mechanisms and causal chains

The process of measurement involves a causal chain from the physical phenomenon to the final recorded value. Consider measuring the temperature of a liquid with a mercury thermometer. The thermal energy of the liquid transfers to the glass bulb (heat transfer), causing the mercury to expand (thermal expansion). The volume change of the mercury forces it up the capillary tube. The height of the mercury column is then visually compared against a printed scale by an observer. 

Errors and uncertainties enter at every step of this chain:
1.  **The Measurand:** The liquid's temperature might not be uniform (spatial variation).
2.  **The Sensor:** The glass bulb takes time to reach thermal equilibrium (dynamic error), and the thermometer itself absorbs some heat, slightly altering the liquid's temperature (loading effect).
3.  **The Transduction:** The expansion of mercury might not be perfectly linear over the entire range.
4.  **The Scale:** The printed markings might be slightly misplaced during manufacturing (systematic error).
5.  **The Observer:** The observer might read the scale from an angle, causing parallax error (random or systematic error).

Understanding this causal chain is essential for identifying sources of error and evaluating the overall measurement uncertainty.

## 5. Important quantities

| Quantity | Symbol | SI Unit | Dimension | Description |
| :--- | :---: | :--- | :---: | :--- |
| Length | $l, x, r$ | metre ($\text{m}$) | $L$ | The one-dimensional extent of an object. |
| Mass | $m$ | kilogram ($\text{kg}$) | $M$ | A measure of an object's resistance to acceleration. |
| Time | $t$ | second ($\text{s}$) | $T$ | The continuous progress of existence and events. |
| Temperature | $T$ | kelvin ($\text{K}$) | $\Theta$ | A measure of the average kinetic energy of particles. |
| Electric Current | $I, i$ | ampere ($\text{A}$) | $I$ | The rate of flow of electric charge. |
| Amount of Substance | $n$ | mole ($\text{mol}$) | $N$ | The number of elementary entities (atoms, molecules). |
| Luminous Intensity | $I_v$ | candela ($\text{cd}$) | $J$ | The wavelength-weighted power emitted by a light source. |

## 6. Mathematical models and equations

### Dimensional Analysis and the Buckingham $\pi$ Theorem

Any physical equation must be dimensionally homogeneous. If an equation is given by $A = B + C$, then the dimensions of $A$, $B$, and $C$ must be identical: $[A] = [B] = [C]$.

The Buckingham $\pi$ theorem states that if there is a physically meaningful equation involving $n$ physical variables, and these variables are expressible in terms of $k$ independent fundamental physical dimensions, then the original equation can be rewritten in terms of a set of $p = n - k$ dimensionless parameters $\pi_1, \pi_2, \dots, \pi_p$.

### Statistical Evaluation of Random Error (Type A Evaluation)

When a measurement is repeated $N$ times under the same conditions, the best estimate of the true value is the arithmetic mean, $\bar{x}$:

$$ \bar{x} = \frac{1}{N} \sum_{i=1}^{N} x_i $$

The dispersion of the values is characterized by the experimental standard deviation, $s(x)$:

$$ s(x) = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (x_i - \bar{x})^2} $$

The standard uncertainty of the mean, $u(\bar{x})$, which represents how well the mean estimates the true value, is given by the standard deviation of the mean:

$$ u(\bar{x}) = \frac{s(x)}{\sqrt{N}} $$

### Propagation of Uncertainty

When a quantity $Y$ is not measured directly but is determined from $N$ other measured quantities $X_1, X_2, \dots, X_N$ through a functional relationship $Y = f(X_1, X_2, \dots, X_N)$, the combined standard uncertainty $u_c(y)$ is calculated using the law of propagation of uncertainty (assuming the input quantities are uncorrelated) [2]:

$$ u_c^2(y) = \sum_{i=1}^{N} \left( \frac{\partial f}{\partial x_i} \right)^2 u^2(x_i) $$

Where:
*   $y$ is the estimate of the measurand $Y$.
*   $x_i$ are the estimates of the input quantities $X_i$.
*   $u(x_i)$ is the standard uncertainty associated with $x_i$.
*   $\frac{\partial f}{\partial x_i}$ are the sensitivity coefficients, evaluated at $X_i = x_i$.

For simple operations, this reduces to:
*   **Addition/Subtraction ($Y = A \pm B$):** $u_c(y) = \sqrt{u^2(a) + u^2(b)}$
*   **Multiplication/Division ($Y = A \cdot B$ or $Y = A / B$):** $\frac{u_c(y)}{|y|} = \sqrt{\left(\frac{u(a)}{a}\right)^2 + \left(\frac{u(b)}{b}\right)^2}$

## 7. Definitions of symbols and units

*   $x_i$: The $i$-th measured value of a quantity (unit depends on the quantity).
*   $\bar{x}$: The arithmetic mean of a set of measured values (unit depends on the quantity).
*   $N$: The number of repeated measurements (dimensionless).
*   $s(x)$: The experimental standard deviation (unit depends on the quantity).
*   $u(x_i)$: The standard uncertainty of an input estimate $x_i$ (unit depends on the quantity).
*   $u_c(y)$: The combined standard uncertainty of an output estimate $y$ (unit depends on the quantity).
*   $\frac{\partial f}{\partial x_i}$: The partial derivative of the function $f$ with respect to $x_i$, representing the sensitivity coefficient (unit is the unit of $y$ divided by the unit of $x_i$).

## 8. Assumptions and approximations

*   **Normal Distribution:** The statistical methods for evaluating random error (Type A evaluation) and calculating coverage intervals generally assume that the repeated measurements follow a Gaussian (normal) distribution.
*   **Linearization:** The standard law of propagation of uncertainty is based on a first-order Taylor series expansion of the measurement function. It assumes that the function is approximately linear in the region defined by the uncertainties of the input quantities. If the function is highly non-linear, higher-order terms or Monte Carlo methods must be used.
*   **Uncorrelated Inputs:** The simplified uncertainty propagation formula assumes that the input quantities $X_i$ are independent (uncorrelated). If they are correlated, covariance terms must be included in the calculation.

## 9. Spatial and temporal scales

Measurement spans an extraordinary range of scales. At the quantum scale, spatial measurements are on the order of femtometres ($10^{-15}\text{ m}$) for atomic nuclei, and time is measured in attoseconds ($10^{-18}\text{ s}$) for electron dynamics. At the cosmological scale, distances are measured in parsecs or light-years (order of $10^{16}\text{ m}$ to $10^{26}\text{ m}$), and time spans billions of years ($10^{17}\text{ s}$). The SI system accommodates these extremes through the use of standard prefixes (e.g., nano-, kilo-, giga-), but the physical instruments and the dominant sources of uncertainty change drastically across these scales. For instance, quantum uncertainty (Heisenberg's uncertainty principle) sets a fundamental limit at the microscopic scale, which is entirely negligible at the macroscopic scale where instrumental and environmental errors dominate.

## 10. Common misconceptions

*   **Misconception:** "Error" means a mistake made by the experimenter.
    *   **Correction:** In metrology, error is the inevitable difference between a measured value and the true value, arising from the limitations of instruments and the physical environment, not necessarily human blunders.
*   **Misconception:** A digital display with many decimal places is highly accurate.
    *   **Correction:** A high number of decimal places indicates high resolution, but not necessarily high accuracy. A highly precise instrument can still have a large systematic error (e.g., a digital scale that is improperly calibrated).
*   **Misconception:** The "true value" of a physical quantity can be known exactly if we have good enough instruments.
    *   **Correction:** The true value is an idealized concept. Every measurement has some uncertainty. We can only estimate the true value and quantify our confidence in that estimate.

## 11. Connections to other modules

*   **01-scientific-reasoning:** Measurement is the empirical foundation of scientific reasoning. Hypotheses are tested by comparing theoretical predictions with measured values, taking uncertainty into account.
*   **03-kinematics-dynamics:** The measurement of length, time, and mass is essential for defining velocity, acceleration, and force.
*   **04-thermodynamics:** Temperature measurement and the definition of the kelvin are central to thermodynamic models.

## 12. Sources

[1] Bureau International des Poids et Mesures. (2019). *The International System of Units (SI)* (9th ed.). https://www.bipm.org/en/publications/si-brochure
[2] Joint Committee for Guides in Metrology. (2008). *Evaluation of measurement data — Guide to the expression of uncertainty in measurement (GUM)* (JCGM 100:2008). https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf
[3] Joint Committee for Guides in Metrology. (2012). *International vocabulary of metrology — Basic and general concepts and associated terms (VIM)* (JCGM 200:2012). https://www.bipm.org/documents/20126/2071204/JCGM_200_2012.pdf
