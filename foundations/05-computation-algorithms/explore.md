---
title: "Exploring computation and simulation"
slug: 05-computation-algorithms-explore
module: "Module 05"
domain: foundations
status: reviewed
prerequisites: [03-mathematical-models, 04-probability-statistics]
connections: [19-software-ai]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# Exploring computation and simulation

## 1. Observation prompts

- Zoom into a digital photograph or map. Distinguish display pixels from the resolution of the data or model that produced the image; they are not necessarily the same grid.
- Watch a recorded simulation at different frame rates. Which changes reflect the numerical time step, which reflect saved output intervals, and which are only animation choices?
- Examine a spreadsheet containing many decimal digits. Which digits came from measurement, which from formulas, and which are merely display formatting?
- Find two applications that solve similar problems. What evidence would show that they implement the same mathematical model and not merely produce similar-looking graphics?

## 2. Prediction questions

- Halving $\Delta x$, $\Delta y$, and $\Delta z$ in a fixed 3D domain increases the number of spatial cells by approximately what factor?
- If a time-integration stability condition also requires halving $\Delta t$, how many more cell-updates are required to simulate the same physical duration under an idealized constant-cost assumption?
- Does a smaller residual always imply a more accurate physical prediction?
- If two mathematically equivalent expressions are evaluated in floating-point arithmetic, must they return identical values?
- When can more Monte Carlo samples fail to fix a biased result?

## 3. Worked reasoning examples

### Resolution and computational work

Suppose a 3D grid has $N_xN_yN_z$ cells. Halving spacing in every direction approximately doubles each dimension count:

$$N_{\text{cells,new}}\approx(2N_x)(2N_y)(2N_z)=8N_{\text{cells,old}}.$$

If the time step is also halved, twice as many time steps are needed for the same simulated duration. An idealized explicit calculation therefore requires about

$$8\times2=16$$

as many cell-updates. Real runtime can scale worse or better depending on solver complexity, memory, communication, parallel efficiency, and cache behavior.

### Estimating $\pi$ with Monte Carlo sampling

Sample $N$ independent points uniformly from the square $[-1,1]^2$. Let $I_i=1$ when $x_i^2+y_i^2\le1$ and $0$ otherwise. Since $E[I_i]=\pi/4$,

$$\hat\pi=4\bar I=\frac{4}{N}\sum_{i=1}^{N}I_i.$$

An estimated standard error is

$$\widehat{\operatorname{SE}}(\hat\pi)=4\sqrt{\frac{\bar I(1-\bar I)}{N}}.$$

Increasing $N$ reduces sampling variation at roughly $N^{-1/2}$, but a non-uniform or dependent point generator can introduce bias or invalidate the simple standard-error calculation.

### Cancellation in floating-point arithmetic

For small $x$, directly evaluating

$$\sqrt{1+x}-1$$

can lose significant digits because two nearly equal numbers are subtracted. Algebraically rationalizing gives

$$\sqrt{1+x}-1=\frac{x}{\sqrt{1+x}+1},$$

which can be numerically more stable. Mathematical equivalence over real numbers does not guarantee equal floating-point behavior.

## 4. Thought experiments

- **Infinite precision, imperfect model:** If a computer represented real numbers exactly, which errors would remain in a simulation?
- **Chaotic sensitivity:** Two weather simulations begin with slightly different initial states. How can their detailed trajectories diverge while ensemble or statistical forecasts remain useful?
- **Small residual, wrong answer:** Imagine solving an ill-conditioned linear system. Why can the equations be nearly satisfied while the recovered parameters are inaccurate?
- **Reproducible but invalid:** A perfectly documented simulation is rerun exactly and gives the same output. What further evidence is required before using it for a real system?

## 5. Household and browser-based explorations

- **Trapezoidal rule:** In a spreadsheet, integrate $f(x)=x^2$ from 0 to 1 using step sizes 0.1, 0.05, and 0.01. Compare errors with the exact value $1/3$ and plot error against step size.
- **Floating-point representation:** In a programming language or spreadsheet, evaluate repeated addition of 0.1, compare with exact decimal expectations, and test whether a tolerance is more appropriate than direct equality.
- **Iterative convergence:** Implement or simulate bisection for a simple root. Record interval width and function value at each step, and distinguish stopping criteria.
- **Physics sandbox:** Use a reputable browser simulation without changing device security settings. Compare outputs under different solver step or iteration settings, treating visual behavior as a prompt for verification rather than proof.
- **Random-seed reproducibility:** Run one Monte Carlo calculation with a recorded seed and then with new seeds. Separate reproducibility of one run from sampling variability across runs.

## 6. Model-building prompts

- **Discrete cooling:** Starting from

  $$\frac{dT}{dt}=-k(T-T_a),$$

  derive forward Euler:

  $$T_{n+1}=T_n-k\Delta t(T_n-T_a).$$

  Explore how behavior changes with $k\Delta t$ and identify unstable or non-physical results.
- **Population update:** Analyze

  $$P_{n+1}=P_n+0.10P_n-50.$$

  Determine the equilibrium and explain why the model becomes physically inappropriate if it predicts a negative population.
- **Verification case:** Choose an equation with a known analytical solution and design a grid-refinement study for a numerical approximation.
- **Validation plan:** Define which physical observations, uncertainty ranges, and acceptance criteria would be needed to validate a cooling simulation.
- **Complexity comparison:** Compare linear search and binary search, stating the precondition required for binary search.

## 7. Self-explanation questions

- How do modelling, discretization, iterative, floating-point, sampling, and implementation errors differ?
- What is the difference between a problem being ill-conditioned and an algorithm being unstable?
- Why can a small residual fail to imply a small solution error?
- How do code verification, solution verification, and validation differ?
- What information is needed to reproduce a stochastic simulation?
- Why is Big-O notation insufficient for predicting actual runtime?

## 8. Transfer questions

- What are the equivalents of time sampling, amplitude quantization, and compression error in digital audio?
- How can a numerical weather forecast be useful even when one detailed trajectory becomes unpredictable?
- Why can a machine-learning surrogate fail when the original physical solver would remain valid?
- How should an engineering team decide between one high-resolution run and many lower-resolution uncertainty scenarios?
- Which parts of a simulation workflow should be independently checked before a safety-relevant decision?

## 9. Suggested learning paths

- **Algorithms and complexity:** Data structures, correctness, invariants, Big-O analysis, and computability.
- **Numerical analysis:** Floating-point arithmetic, conditioning, root finding, linear algebra, quadrature, and differential equations.
- **Scientific software:** Testing, version control, dependency management, documentation, and reproducible environments.
- **Simulation evidence:** Verification, validation, uncertainty quantification, sensitivity, and benchmark design.
- **High-performance computing:** Parallel decomposition, memory hierarchy, communication, scaling, and energy-to-solution.

## 10. Reasoning notes

Before trusting a computational result, ask:

1. What question and quantity of interest were defined?
2. Which mathematical model and boundary conditions were used?
3. How was the problem discretized?
4. What are the conditioning and stability properties?
5. Were code tests and reference solutions used?
6. Were mesh, time-step, and solver-tolerance studies performed?
7. How were floating-point, stochastic, and parameter uncertainties handled?
8. Which data were used for calibration and which for validation?
9. Can the run be reproduced from code, inputs, environment, and configuration?
10. Is the intended decision inside the validated domain?

A simulation output is evidence generated by a chain of models and computations. Trust comes from testing that chain, not from numerical detail or visual realism alone.
