---
title: "Exploring mathematical models and scale"
slug: 03-mathematical-models-explore
module: "Module 03"
domain: foundations
status: reviewed
prerequisites: [01-scientific-reasoning]
connections: [04-probability-statistics, 05-computation-algorithms, 06-matter-quantum, 08-energy-thermodynamics, 09-motion-forces, 10-electricity-magnetism, 11-waves-signals, 12-fluids-materials]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# Exploring mathematical models and scale

## 1. Observation prompts

- Observe a cooling drink, a bouncing ball, or a queue. Which quantities change, which appear nearly constant, and where would you place the system boundary?
- Compare a real tree branch with a smaller branch. Which features are approximately repeated and which are not? Treat self-similarity as an approximation rather than an exact law.
- Watch a safe pendulum demonstration or simulation. Does period depend visibly on length, mass, release angle, or friction? Which effects are difficult to separate by observation alone?
- Find a graph that looks linear over one interval. What could happen outside the displayed range?

## 2. Prediction questions

- If pendulum length is doubled under the small-angle model, by what factor does the period change?
- If every linear dimension of a similar object is doubled, how do area, volume, and mass change when density is constant?
- If an exponential-growth model is fitted early in a process, what observations would indicate that saturation or resource limits need to be added?
- If two parameter sets produce nearly identical output curves, what does that suggest about identifiability?

## 3. Worked reasoning examples

### Dimensional analysis of a pendulum

Assume a small-angle pendulum period $T$ depends on bob mass $m$, length $L$, and gravitational acceleration $g$:

$$T=Cm^aL^bg^c,$$

where $C$ is dimensionless. Using dimensions,

$$[T]=[M]^a[L]^b[LT^{-2}]^c.$$

Equating exponents gives

$$a=0,\qquad b+c=0,\qquad -2c=1,$$

so

$$T=C\sqrt{\frac{L}{g}}.$$

Dimensional analysis shows that mass cannot appear under these assumptions and determines the dimensional form, but it cannot determine $C=2\pi$, damping, amplitude dependence, or whether omitted variables matter.

### Linearization error

For a pendulum, the approximation $\sin\theta\approx\theta$ is based on the Taylor series

$$\sin\theta=\theta-\frac{\theta^3}{6}+\frac{\theta^5}{120}-\cdots.$$

The leading neglected term is approximately $-\theta^3/6$. This makes the limitation visible: “small” should be judged against an acceptable prediction error, not used as an undefined label.

## 4. Thought experiments

- **Same fit, different mechanism:** Construct two models that match the same short dataset but predict different long-term behavior. What future observation would discriminate between them?
- **Scaled giant:** If a body is enlarged geometrically, mass grows approximately as $L^3$ while cross-sectional area grows as $L^2$. What changes in shape, material, posture, or internal transport could compensate?
- **Frictionless baseline:** Start with an ideal oscillator without friction, then add damping. Which new parameter appears, and what observation could estimate it?
- **Model outside its domain:** Imagine applying a room-temperature material law during a fire. Which assumptions fail before the numerical solver does?

## 5. Household and browser-based explorations

- **Pendulum data:** Use a simulation, or a lightweight object tied securely to string in a clear area away from people and breakable objects. Measure several lengths and time multiple periods. Plot $T$ against $L$ and against $\sqrt{L}$.
- **Cooling curve:** Record a drink or safe container approaching room temperature. Compare a linear fit with an exponential model and examine residuals.
- **Recipe scaling:** Scale a rectangular cake pan in width and length while holding height fixed, then scale all three dimensions. Identify which ingredients, heating times, and structural effects may not follow geometry alone.
- **Model comparison:** Use a spreadsheet to fit exponential and logistic population models to synthetic data. Reserve later points for validation rather than fitting every point.

## 6. Model-building prompts

- **Newton cooling:** Write

  $$\frac{dT}{dt}=-k(T-T_a),$$

  define every quantity, and list conditions under which $k$ could be treated as constant.
- **Queue model:** Define arrivals, service times, capacity, and queue discipline. Which outputs matter: mean wait, maximum wait, or probability of exceeding a threshold?
- **State-space model:** For a mass–spring–damper system, choose state variables and convert the second-order equation into two first-order equations.
- **Non-dimensionalization:** Choose characteristic length and time scales for a falling object and identify dimensionless groups that compare drag, inertia, and gravity.

## 7. Self-explanation questions

- What is the difference between a state variable, parameter, input, and output?
- Why can a model fit data well yet have the wrong mechanism?
- What does dimensional analysis prove, and what can it not prove?
- Why is linearization local?
- How do calibration, verification, and validation answer different questions?
- What does it mean for a parameter to be non-identifiable?

## 8. Transfer questions

- How can a model validated for one bridge design fail for another geometry or material?
- Why can a machine-learning surrogate be fast yet unsafe outside its training domain?
- How do scaling laws affect cooling, structural support, communication delay, or metabolic transport?
- How should a digital twin respond when sensor data move outside the model’s validation domain?

## 9. Suggested learning paths

- **Calculus and differential equations:** Derivatives, integrals, ordinary differential equations, and stability.
- **Linear algebra:** Vectors, matrices, eigenvalues, coordinate transformations, and state-space models.
- **Dimensional analysis and similarity:** Buckingham $\pi$, scaling, and experimental similitude.
- **Statistical modelling:** Calibration, residuals, identifiability, uncertainty, and model comparison.
- **Computational modelling:** Numerical solvers, discretization, verification, and convergence.

## 10. Reasoning notes

For every model, record:

1. Intended question and decision.
2. System boundary and resolution.
3. Variables, parameters, units, and reference frames.
4. Governing laws, empirical relationships, and data sources.
5. Initial and boundary conditions.
6. Assumptions and prohibited extrapolations.
7. Calibration method and validation evidence.
8. Sensitivity, uncertainty, and model discrepancy.
9. Competing models and observations that could distinguish them.
10. Version, implementation, and reviewer.

Start with the simplest model that can answer the question, but do not confuse simplicity with adequacy or complexity with truth.
