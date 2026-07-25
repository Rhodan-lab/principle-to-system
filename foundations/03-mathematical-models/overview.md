---
title: "Mathematical models, quantities, vectors, and scale"
slug: 03-mathematical-models
module: "Module 03"
domain: foundations
status: reviewed
prerequisites: [01-scientific-reasoning]
connections: [04-probability-statistics, 05-computation-algorithms, 06-matter-quantum, 08-energy-thermodynamics, 09-motion-forces, 10-electricity-magnetism, 11-waves-signals, 12-fluids-materials]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# Mathematical models, quantities, vectors, and scale

## 1. The central questions

How can a real system be represented with variables, relationships, and rules that are simple enough to analyze yet adequate for a purpose? Which details belong inside the model boundary? What data determine parameters, and what observations test the model? A mathematical model is not reality translated without loss. It is a purposeful representation whose usefulness depends on its question, assumptions, scale, data, uncertainty, and range of validity.

## 2. Observable phenomena

Many systems show recurring mathematical patterns: nearly periodic oscillation, approximately exponential growth or decay, diffusion, saturation, thresholds, conservation, and feedback. Similar curve shapes do not prove identical mechanisms. Exponential-looking change can arise from several processes, and a straight line over a narrow range can hide a non-linear relationship.

Modelling begins by defining the system, selecting quantities, and identifying candidate mechanisms or empirical relationships. It continues through calibration, solution, comparison with observations, and revision.

## 3. Essential concepts

**Quantity:** A property that can be expressed by a number and a reference such as a unit. Variables should be defined operationally and dimensionally.

**State variable:** A quantity included to summarize the current state sufficiently for the model to determine future evolution when inputs are specified.

**Parameter:** A quantity treated as fixed during one model run, such as mass, stiffness, rate constant, or carrying capacity. Parameters may still be uncertain or vary across systems.

**Scalar:** A quantity represented by one component that is invariant under a change of coordinate orientation, such as mass or thermodynamic temperature.

**Vector:** A geometric quantity with components that transform according to vector rules, such as displacement, velocity, or force. A vector is not merely “a number with a direction”; its coordinate representation depends on the basis.

**Tensor:** A multilinear geometric object whose components obey tensor transformation rules. Stress and moment of inertia require second-rank tensors because their effects depend on direction.

**Function and equation:** A function maps admissible inputs to outputs. Equations can encode definitions, constraints, conservation laws, constitutive relations, empirical fits, or dynamical rules.

**Calibration:** Estimation of model parameters or discrepancy terms using data.

**Verification and validation:** Verification checks whether equations and calculations are implemented correctly. Validation evaluates whether model outputs agree adequately with observations for the intended use.

**Sensitivity and identifiability:** Sensitivity measures how outputs change with inputs. Identifiability asks whether available observations can distinguish parameter values or model structures.

## 4. Mechanisms and causal chains

A model may encode a mechanism, but mathematics alone does not make it causal. For a mass–spring system,

```text
displacement
→ restoring force
→ acceleration
→ velocity change
→ displacement change
```

is represented by

$$m\frac{d^2x}{dt^2}+c\frac{dx}{dt}+kx=F(t).$$

Here $m$ is mass, $c$ damping, $k$ stiffness, and $F(t)$ external force. The equation is useful only under conditions where these lumped parameters and linear relationships are adequate. A fitted sinusoid might predict the same motion without explaining the force mechanism.

## 5. Important quantities

| Quantity | Symbol | Typical unit | Role |
| --- | --- | --- | --- |
| Independent variable | $t$ or $x$ | context-dependent | Indexes time, position, or another input. |
| State vector | $\mathbf{x}$ | mixed units | Collects variables needed to represent system state. |
| Input | $\mathbf{u}$ | context-dependent | External forcing or control. |
| Parameter vector | $\boldsymbol{\theta}$ | mixed units | Defines material, rate, geometry, or model properties. |
| Output | $\mathbf{y}$ | context-dependent | Quantity compared with observations or used for decisions. |
| Residual | $r_i=y_i-\hat y_i$ | same as output | Difference between observation and model prediction. |
| Sensitivity | $\partial y/\partial\theta_j$ | output per parameter unit | Local response to a parameter change. |
| Characteristic scale | $L_c,T_c,Q_c$ | corresponding units | Reference size used for comparison and non-dimensionalization. |

## 6. Mathematical models and equations

A general continuous-time state-space model is

$$\frac{d\mathbf{x}}{dt}=\mathbf{f}(\mathbf{x},\mathbf{u},\boldsymbol{\theta},t),$$

$$\mathbf{y}=\mathbf{g}(\mathbf{x},\mathbf{u},\boldsymbol{\theta},t).$$

The functions $\mathbf{f}$ and $\mathbf{g}$ may come from physical laws, empirical relationships, or a combination.

### Linearization

Near a reference state $\mathbf{x}_0$, a differentiable non-linear model can be approximated by a first-order Taylor expansion:

$$\mathbf{f}(\mathbf{x})\approx\mathbf{f}(\mathbf{x}_0)+J_f(\mathbf{x}_0)(\mathbf{x}-\mathbf{x}_0),$$

where $J_f$ is the Jacobian matrix. This is a local approximation; accuracy should be checked over the actual operating region.

For a pendulum,

$$\frac{d^2\theta}{dt^2}+\frac{g}{L}\sin\theta=0.$$

When $|\theta|$ is sufficiently small and expressed in radians,

$$\sin\theta\approx\theta,$$

so

$$\frac{d^2\theta}{dt^2}+\frac{g}{L}\theta=0.$$

The approximation error increases with amplitude, and damping or moving supports require additional terms.

### Non-dimensionalization

Let $x=L_cx^*$ and $t=T_ct^*$. Rewriting equations in dimensionless variables can reveal governing groups, compare systems of different size, and identify negligible terms. Dimensional consistency is necessary but not sufficient for physical correctness.

### Calibration and residuals

Parameters can be estimated by minimizing a loss such as

$$J(\boldsymbol{\theta})=\sum_{i=1}^{n}w_i\left[y_i-\hat y_i(\boldsymbol{\theta})\right]^2.$$

A small fitted loss does not prove the model structure is correct. Residual patterns, out-of-sample prediction, parameter plausibility, uncertainty, and comparison with alternatives are also needed.

## 7. Definitions of symbols and units

- $\mathbf{x}$: State vector.
- $\mathbf{u}$: Input or forcing vector.
- $\boldsymbol{\theta}$: Parameter vector.
- $\mathbf{y}$: Model output.
- $\mathbf{f},\mathbf{g}$: State-evolution and observation functions.
- $J_f$: Jacobian matrix of partial derivatives.
- $\theta$: Pendulum angle; radian, dimensionless in SI.
- $g$: Local gravitational acceleration, $\mathrm{m\,s^{-2}}$.
- $L$: Pendulum length, $\mathrm{m}$.
- $r_i$: Residual, same unit as $y_i$.
- $w_i$: Weight, chosen according to the fitting model.

## 8. Assumptions and approximations

A model should state:

- system boundary and omitted interactions;
- spatial and temporal resolution;
- conservation laws and constitutive relations used;
- parameter constancy or variability;
- initial and boundary conditions;
- deterministic or stochastic treatment of variation;
- approximation order and operating range;
- calibration data and independence of validation data;
- model-form discrepancy and measurement uncertainty;
- quantities or regimes for which the model should not be used.

An assumption is not automatically a flaw. It becomes a flaw when it is hidden, unjustified for the intended use, or applied outside its range.

## 9. Spatial and temporal scales

Different mechanisms dominate at different scales. A continuum model may be adequate when microscopic details average out, while molecular or agent-based models may be needed when discreteness matters. Multi-scale modelling connects representations rather than assuming one equation is valid everywhere.

Scaling laws such as area $\propto L^2$ and volume $\propto L^3$ explain important tendencies, but real organisms and engineered systems can change shape, material, posture, metabolism, internal transport, and control as size changes. The square–cube law is therefore a starting constraint, not a complete explanation of biological form.

## 10. Common misconceptions

- **A model is a miniature reality:** A model is a purpose-dependent representation.
- **A good fit proves the mechanism:** Different models can fit the same data, especially inside the calibration range.
- **More parameters always improve the model:** Added flexibility can reduce interpretability, identifiability, and out-of-sample performance.
- **Dimensionally correct means physically correct:** Dimensional consistency cannot determine signs, dimensionless constants, mechanisms, or boundary conditions.
- **Validation proves a model universally true:** Validation evidence is conditional on quantities, regimes, data quality, and intended use.
- **Higher fidelity always means higher trust:** A complex model can contain more unresolved assumptions, numerical error, and uncertain parameters.

## 11. Connections to other modules

- **01-scientific-reasoning:** Models formalize hypotheses and competing explanations.
- **02-measurement-uncertainty:** Observations, calibration, and uncertainty determine what a model can learn and test.
- **04-probability-statistics:** Statistical models represent variability, parameter uncertainty, and residual structure.
- **05-computation-algorithms:** Numerical methods solve models and introduce discretization and floating-point effects.
- **08-energy-thermodynamics, 09-motion-forces, 10-electricity-magnetism, 11-waves-signals, 12-fluids-materials:** These modules supply domain-specific governing laws, constitutive relations, and characteristic scales.

## 12. Sources

1. Meerschaert, M. M. (2013). *Mathematical Modeling* (4th ed.). Academic Press. https://www.sciencedirect.com/book/monograph/9780123869128/mathematical-modeling
2. Mahajan, S. (2010). *Street-Fighting Mathematics*. MIT Press. https://mitpress.mit.edu/9780262514293/street-fighting-mathematics/
3. Barenblatt, G. I. (1996). *Scaling, Self-similarity, and Intermediate Asymptotics*. Cambridge University Press. https://www.cambridge.org/core/books/scaling-selfsimilarity-and-intermediate-asymptotics/3B56096C3B7E822794C81B51F7370B82
4. Giordano, F. R., Fox, W. P., & Horton, S. B. (2013). *A First Course in Mathematical Modeling* (5th ed.). Cengage. https://www.cengage.com/c/a-first-course-in-mathematical-modeling-5e-giordano/9781285050904/
5. MIT OpenCourseWare. *Introduction to Modeling and Simulation*. https://ocw.mit.edu/courses/3-021j-introduction-to-modeling-and-simulation-spring-2012/
