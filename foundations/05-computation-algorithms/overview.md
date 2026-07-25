---
title: "Computation, algorithms, numerical methods, and simulation"
slug: 05-computation-algorithms
module: "Module 05"
domain: foundations
status: reviewed
prerequisites: [03-mathematical-models, 04-probability-statistics]
connections: [19-software-ai]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# Computation, algorithms, numerical methods, and simulation

## 1. The central questions

How can a mathematical procedure be represented so that a machine can execute it reliably? How are continuous models approximated using finite data, finite time, and finite-precision arithmetic? Which errors come from the physical model, discretization, iterative solution, software, hardware, or interpretation? How can a simulation be verified and validated for a stated use?

Computation does not remove modelling assumptions. It adds an implementation layer whose correctness, stability, complexity, and reproducibility must also be examined.

## 2. Observable phenomena

Weather maps, structural analyses, digital images, navigation systems, and numerical experiments all use discretized representations. Refining a grid can change a predicted flow. Reordering floating-point operations can change low-order digits. A simulation can produce a smooth, realistic animation while violating conservation or using the wrong boundary condition.

Computational results therefore depend on a chain from question to model, algorithm, code, hardware, data, and interpretation. Error at one stage can be hidden by apparent precision at another.

## 3. Essential concepts

**Computation:** The execution of formally specified operations on representations of information.

**Algorithm:** A finite description of an effective procedure. An algorithm may terminate with an output, process a stream continuously, or define an iterative sequence; its preconditions, outputs, and stopping rules must be explicit.

**Computational complexity:** How required time, memory, communication, or other resources scale with input size. Big-O notation describes asymptotic growth and does not by itself predict runtime on a specific machine.

**Numerical method:** An algorithm that approximates a mathematical quantity or solution using finite arithmetic. Examples include root finding, quadrature, linear-system solution, optimization, and differential-equation solvers.

**Discretization:** Replacement of a continuous domain or operator with a finite representation such as a mesh, time grid, basis expansion, or sample set.

**Conditioning:** Sensitivity of the mathematical problem’s solution to small changes in input. A well-implemented method cannot recover information that an ill-conditioned problem does not contain.

**Stability:** The behavior of errors introduced during numerical computation. Stability is a property of a method applied to a problem under stated step sizes and conditions.

**Consistency and convergence:** Consistency concerns whether the discrete equations approach the continuous equations as resolution improves. Convergence concerns whether the numerical solution approaches the relevant mathematical solution.

**Floating-point arithmetic:** A finite representation of real numbers with rounding, limited range, signed zero, infinities, and special values. Algebraic identities over real numbers may not hold exactly in floating-point arithmetic.

**Verification and validation:** Code verification examines whether software implements the numerical method correctly. Solution verification estimates numerical error for a particular calculation. Validation evaluates whether the model adequately represents reality for the intended use.

**Reproducibility:** A computational result should be linked to data, code, environment, parameters, random seeds where relevant, and execution instructions.

## 4. Mechanisms and causal chains

```text
physical or abstract question
→ mathematical model
→ discretized problem
→ numerical algorithm
→ software implementation
→ execution on hardware
→ numerical output
→ visualization and decision
```

The chain introduces distinct uncertainties and errors:

- model-form discrepancy and uncertain parameters;
- spatial and temporal discretization error;
- incomplete iterative convergence;
- floating-point rounding and cancellation;
- software defects and configuration mistakes;
- stochastic sampling error;
- hardware faults;
- misleading visualization or interpretation.

These categories should be investigated separately because refining a mesh cannot correct the wrong physical model, and validating one output cannot prove every code path correct.

## 5. Important quantities

| Quantity | Symbol | Typical unit | Meaning |
| --- | --- | --- | --- |
| Spatial step | $\Delta x$ | $\mathrm{m}$ or context-dependent | Distance or scale between spatial degrees of freedom. |
| Time step | $\Delta t$ | $\mathrm{s}$ | Increment used by a time-integration method. |
| Truncation error | $\tau$ | equation-dependent | Error from replacing a mathematical operator by an approximation. |
| Iterative residual | $\mathbf r$ | equation-dependent | Imbalance remaining in the discrete equations. |
| Condition number | $\kappa$ | dimensionless | Sensitivity measure for a mathematical problem or matrix. |
| Machine precision | $\epsilon_{\mathrm{mach}}$ | dimensionless | Scale of relative rounding near 1 for a floating-point format. |
| Sample count | $N$ | dimensionless | Number of stochastic samples. |
| Runtime | $T_c$ | $\mathrm{s}$ | Physical execution time under a specified system and configuration. |
| Memory use | $M_c$ | bytes | Storage required by data and algorithm state. |

## 6. Mathematical models and equations

### Finite differences

For a sufficiently smooth function, Taylor expansion gives

$$f(x+h)=f(x)+hf'(x)+\frac{h^2}{2}f''(\xi),$$

for some $\xi$ between $x$ and $x+h$. Therefore the forward difference

$$f'(x)\approx\frac{f(x+h)-f(x)}{h}$$

has first-order truncation error, written $O(h)$. The central difference

$$f'(x)\approx\frac{f(x+h)-f(x-h)}{2h}$$

has $O(h^2)$ truncation error for a sufficiently smooth function. Smaller $h$ reduces truncation error only until floating-point cancellation and other effects become important.

### Numerical integration

For a uniform partition $x_i=a+ih$ with $h=(b-a)/N$, the composite trapezoidal rule is

$$\int_a^b f(x)\,dx\approx h\left[\frac{f(x_0)}{2}+\sum_{i=1}^{N-1}f(x_i)+\frac{f(x_N)}{2}\right].$$

Its error order depends on smoothness and the integration rule; discontinuities or singular behavior require special treatment.

### Monte Carlo estimation

If $X_i$ are independent samples from a distribution and $E[f(X)^2]$ is finite,

$$\hat\mu_N=\frac{1}{N}\sum_{i=1}^{N}f(X_i)$$

estimates $\mu=E[f(X)]$, with standard error approximately

$$\operatorname{SE}(\hat\mu_N)=\frac{s_f}{\sqrt{N}},$$

where $s_f$ is the sample standard deviation of $f(X_i)$. The $N^{-1/2}$ rate can be attractive in high dimensions, but constants, variance, dependence, sampling method, and problem structure determine practical efficiency.

### Linear systems and conditioning

For

$$A\mathbf x=\mathbf b,$$

small perturbations can be amplified according to the conditioning of $A$. Roughly,

$$\frac{\|\delta\mathbf x\|}{\|\mathbf x\|}\lesssim\kappa(A)\frac{\|\delta\mathbf b\|}{\|\mathbf b\|}$$

for small perturbations under compatible norms and assumptions. A small residual does not guarantee a small solution error when the problem is ill-conditioned.

## 7. Definitions of symbols and units

- $h,\Delta x$: Spatial or independent-variable step.
- $\Delta t$: Time step.
- $N$: Number of intervals or samples.
- $O(h^p)$: Asymptotic truncation-error order.
- $\hat\mu_N$: Monte Carlo estimator.
- $s_f$: Sample standard deviation of evaluated samples.
- $A,\mathbf x,\mathbf b$: Matrix, unknown vector, and right-hand side.
- $\kappa(A)$: Condition number under a specified norm.
- $\mathbf r=\mathbf b-A\hat{\mathbf x}$: Residual of an approximate solution.
- $\epsilon_{\mathrm{mach}}$: Floating-point precision scale.

## 8. Assumptions and approximations

- Smoothness assumptions determine the order of finite-difference and quadrature formulas.
- Boundary and initial conditions must be compatible with the mathematical problem.
- Stability restrictions depend on the equation and numerical scheme; there is no universal CFL formula for every method.
- Convergence studies require a sequence of sufficiently refined calculations and a stable quantity of interest.
- Iterative tolerances should be small relative to discretization and modelling errors, not chosen only from software defaults.
- Pseudorandom generators must be appropriate for the application, seeded and recorded for reproducibility, and checked for dependence relevant to the method.
- Monte Carlo uncertainty estimates require assumptions about sample independence or an analysis of dependence.
- Floating-point results can depend on operation order, parallel reduction, compiler, and hardware.
- Validation evidence is limited to the tested quantities and regimes.

## 9. Spatial and temporal scales

Discretization must resolve the scales that materially influence the quantity of interest. A global climate model, a molecular simulation, and a circuit solver represent different entities and use different equations. Sub-grid or reduced-order models represent effects that cannot be resolved directly.

For explicit wave or transport schemes, a stability condition often relates $\Delta t$, $\Delta x$, characteristic speeds, dimension, and method coefficients. The familiar form $v\Delta t/\Delta x\le C$ is scheme-specific; $C$ is not always 1. Refining space can require smaller time steps and substantially greater memory and runtime.

## 10. Common misconceptions

- **Computers give exact real-number answers:** Most scientific computation uses finite arithmetic and approximations.
- **A small residual proves an accurate solution:** Ill-conditioning can produce a small residual with a large solution error.
- **A finer grid always improves the result:** The scheme may be unstable, the model may be wrong, iterative error may dominate, or round-off may grow.
- **Convergence proves validation:** Convergence addresses the numerical solution of a model, not whether the model represents reality.
- **A realistic visualization proves correctness:** Visual plausibility can hide violated balances, wrong units, or incorrect boundary conditions.
- **Monte Carlo is automatically superior in high dimensions:** Performance depends on variance, structure, sampling strategy, and required accuracy.
- **Re-running the same code is replication:** Re-running with the same data is computational reproducibility; replication uses new data or an independently repeated study.

## 11. Connections to other modules

- **02-measurement-uncertainty:** Validation data and numerical outputs both require uncertainty statements.
- **03-mathematical-models:** Computation implements and approximates mathematical models.
- **04-probability-statistics:** Monte Carlo methods, stochastic simulation, and statistical validation rely on probability.
- **19-software-ai:** Algorithms, data structures, software engineering, and learning systems build on computational foundations.

## 12. Sources

1. Press, W. H., Teukolsky, S. A., Vetterling, W. T., & Flannery, B. P. (2007). *Numerical Recipes* (3rd ed.). Cambridge University Press. https://assets.cambridge.org/97805218/80688/frontmatter/9780521880688_frontmatter.pdf
2. Shiflet, A. B., & Shiflet, G. W. (2014). *Introduction to Computational Science* (2nd ed.). Princeton University Press. https://press.princeton.edu/books/hardcover/9780691160719/introduction-to-computational-science
3. Oberkampf, W. L., & Roy, C. J. (2010). *Verification and Validation in Scientific Computing*. Cambridge University Press. https://www.cambridge.org/core/books/verification-and-validation-in-scientific-computing/05CA1F8F3CCB5AE5445FDF55239A0183
4. Metropolis, N., & Ulam, S. (1949). “The Monte Carlo Method.” *Journal of the American Statistical Association*, 44(247), 335–341. https://doi.org/10.1080/01621459.1949.10483310
5. National Institute of Standards and Technology. (2004). *Verification and Validation of Computer Simulations of High-Consequence Engineering Systems*. https://www.nist.gov/publications/verification-and-validation-computer-simulations-high-consequence-engineering-systems
