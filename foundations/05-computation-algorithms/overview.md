---
title: "Computation, Algorithms, Numerical Methods, and Simulation"
slug: 05-computation-algorithms
module: "Module 05"
domain: foundations
status: draft
prerequisites: [03-mathematical-models, 04-probability-statistics]
connections: [19-software-ai]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Computation, Algorithms, Numerical Methods, and Simulation

## 1. The central questions

How can continuous physical reality be translated into discrete mathematical operations that a machine can execute? When analytical solutions to mathematical models are impossible to find, how can we approximate them with known precision? What are the fundamental limits of computation in terms of time, memory, and accuracy? How do we know if a computer simulation faithfully represents the physical world it is meant to model?

## 2. Observable phenomena

The modern world is saturated with the outputs of computation and simulation. Weather forecasts predict the path of a hurricane days in advance by solving fluid dynamics equations over a grid covering the Earth. Financial markets execute millions of trades per second based on algorithmic pricing models. Engineers design aircraft wings without building physical wind tunnel models for every iteration, relying instead on computational fluid dynamics. When a smartphone renders a 3D video game, it is rapidly solving geometric and lighting equations using numerical approximations. Even the structural integrity of bridges is verified through finite element analysis before concrete is poured. All these phenomena rely on the translation of continuous physics into discrete, computable steps.

## 3. Essential concepts

**Computation** is the systematic execution of mathematical operations to process information or solve a problem. An **algorithm** is a finite, unambiguous sequence of instructions designed to perform a specific task or solve a class of problems. 

**Numerical methods** are algorithms used for solving mathematical problems continuously (as opposed to discrete mathematics) by using numerical approximation rather than analytical manipulation. They are essential because most real-world mathematical models—such as non-linear differential equations—cannot be solved exactly.

**Discretisation** is the process of transforming continuous models and equations into discrete counterparts. For example, replacing a continuous domain (like space or time) with a grid of finite points.

**Simulation** is the execution of a mathematical model over time to study the behaviour of a complex system. It uses numerical methods to step through time and space, calculating the state of the system at each discrete interval.

**Computational complexity** characterises the resources (usually time or memory) required by an algorithm to solve a problem as a function of the size of the input. It defines the theoretical limits of what can be computed practically.

**Verification and Validation (V&V)** are the processes used to check that a simulation is correct. Verification asks, "Are we solving the equations correctly?" (checking for bugs and numerical errors). Validation asks, "Are we solving the correct equations?" (comparing simulation results to physical experiments).

## 4. Mechanisms and causal chains

The process of moving from a physical phenomenon to a computational simulation follows a specific causal chain:

1. **Physical Reality to Mathematical Model**: A physical system is observed, and its governing laws (e.g., conservation of mass, momentum, energy) are expressed as continuous mathematical equations, typically differential equations.
2. **Mathematical Model to Numerical Model (Discretisation)**: The continuous equations are approximated using discretisation techniques. Derivatives are replaced by finite differences; integrals are replaced by finite sums. The continuous space is divided into a discrete grid or mesh.
3. **Numerical Model to Algorithm**: The discrete equations are arranged into an algorithm—a step-by-step procedure to solve the algebraic equations at each grid point and time step.
4. **Algorithm to Code**: The algorithm is translated into a programming language that a computer can execute.
5. **Execution to Simulation**: The computer executes the code, performing billions of arithmetic operations to generate numerical data representing the system's state over time.
6. **Data to Insight**: The numerical output is visualised and analysed to understand the physical system, make predictions, or guide engineering decisions.

Errors can be introduced at every step of this chain: modelling errors in step 1, truncation errors in step 2, round-off errors in step 5, and interpretation errors in step 6.

## 5. Important quantities

| Quantity | Symbol | SI Unit | Description |
| :--- | :--- | :--- | :--- |
| Time step | $\Delta t$ | $\text{s}$ | The discrete interval of time used in a simulation. |
| Spatial step | $\Delta x$ | $\text{m}$ | The distance between adjacent points in a discrete spatial grid. |
| Truncation error | $\epsilon_t$ | Varies | The error introduced by approximating a continuous mathematical operation (like a derivative) with a discrete one. |
| Round-off error | $\epsilon_r$ | Varies | The error introduced by the computer's inability to represent real numbers with infinite precision (floating-point arithmetic). |
| Computational time | $T_c$ | $\text{s}$ | The physical time required for a computer to execute an algorithm. |
| Problem size | $N$ | Dimensionless | A measure of the input size, such as the number of grid points or equations. |

## 6. Mathematical models and equations

### Finite Differences

The foundation of many numerical methods is the approximation of derivatives. The continuous definition of a derivative is:

$$ \frac{df}{dx} = \lim_{\Delta x \to 0} \frac{f(x + \Delta x) - f(x)}{\Delta x} $$

In numerical methods, we cannot take the limit to zero. Instead, we use a finite $\Delta x$. The **forward difference** approximation is:

$$ \frac{df}{dx} \approx \frac{f(x + \Delta x) - f(x)}{\Delta x} $$

Using Taylor series expansion, we can determine the error of this approximation. The **central difference** approximation is often preferred because it is more accurate (the error scales with $\Delta x^2$ rather than $\Delta x$):

$$ \frac{df}{dx} \approx \frac{f(x + \Delta x) - f(x - \Delta x)}{2\Delta x} $$

### Numerical Integration

When an integral cannot be evaluated analytically, numerical integration (quadrature) is used. The simplest method is the **Trapezoidal Rule**, which approximates the area under a curve as a series of trapezoids:

$$ \int_{a}^{b} f(x) dx \approx \sum_{i=1}^{N} \frac{f(x_{i-1}) + f(x_i)}{2} \Delta x $$

where the domain $[a, b]$ is divided into $N$ intervals of width $\Delta x = (b - a) / N$.

### Monte Carlo Methods

Monte Carlo methods use random sampling to obtain numerical results, particularly useful for high-dimensional integrals or complex probabilistic systems. To estimate an integral over a volume $V$:

$$ \int_V f(\mathbf{x}) dV \approx V \langle f \rangle = V \frac{1}{N} \sum_{i=1}^{N} f(\mathbf{x}_i) $$

where $\mathbf{x}_i$ are $N$ uniformly distributed random points within the volume $V$. The error of Monte Carlo integration decreases proportionally to $1/\sqrt{N}$, regardless of the number of dimensions, making it superior to grid-based methods for high-dimensional problems.

## 7. Definitions of symbols and units

- $f(x)$: A continuous mathematical function (units depend on the physical quantity).
- $x$: An independent variable, often representing space ($\text{m}$).
- $\Delta x$: The discrete step size in the independent variable ($\text{m}$).
- $a, b$: The lower and upper limits of integration.
- $N$: The number of discrete intervals or random samples (dimensionless).
- $V$: The volume of the integration domain (e.g., $\text{m}^3$ for 3D space).
- $\mathbf{x}_i$: A randomly sampled point in a multi-dimensional space.

## 8. Assumptions and approximations

Numerical methods are built entirely on approximations. The fundamental assumption is that a continuous function can be adequately represented by its values at a finite set of discrete points. 

It is assumed that the **truncation error** (from using finite steps instead of infinitesimal limits) and the **round-off error** (from finite computer memory) remain bounded and do not grow uncontrollably as the simulation progresses. If errors amplify over time, the numerical method is considered **unstable**.

In Monte Carlo methods, it is assumed that the pseudo-random number generator used by the computer produces a sequence of numbers that is statistically indistinguishable from true randomness.

## 9. Spatial and temporal scales

Computation spans an extraordinary range of scales. At the hardware level, a single arithmetic operation occurs in less than a nanosecond ($10^{-9}\text{ s}$). A complex climate simulation might run for weeks on a supercomputer, calculating interactions across a global grid with a spatial resolution of $10\text{ km}$ ($\Delta x = 10^4\text{ m}$) and a time step of $10\text{ minutes}$ ($\Delta t = 600\text{ s}$), simulating decades of physical time.

The choice of $\Delta x$ and $\Delta t$ is strictly constrained by the physics being modelled. For example, the Courant-Friedrichs-Lewy (CFL) condition dictates that in fluid simulations, the time step must be small enough that information does not travel across more than one spatial grid cell per time step: $\Delta t \le \Delta x / v$, where $v$ is the maximum velocity in the system.

## 10. Common misconceptions

- **"Computers give exact answers."** Computers using floating-point arithmetic cannot even represent simple fractions like $1/10$ exactly in binary. Every numerical simulation contains some degree of error.
- **"A finer grid always gives a better answer."** While decreasing $\Delta x$ reduces truncation error, it increases the number of calculations, which increases round-off error. There is an optimal step size where the total error is minimised.
- **"If a simulation looks realistic, it is correct."** High-fidelity graphics can mask fundamentally flawed physics. A simulation is only valid if it has been rigorously compared against physical experiments (Validation).

## 11. Connections to other modules

- **03-mathematical-models**: Provides the continuous differential equations that numerical methods attempt to solve.
- **04-probability-statistics**: Provides the foundation for Monte Carlo methods and the analysis of simulation uncertainty.
- **06-systems-control**: Relies heavily on real-time algorithms to process sensor data and compute control outputs.

## 12. Sources

[1] Press, W. H., Teukolsky, S. A., Vetterling, W. T., & Flannery, B. P. (2007). *Numerical Recipes: The Art of Scientific Computing* (3rd ed.). Cambridge University Press.
[2] Shiflet, A. B., & Shiflet, G. W. (2014). *Introduction to Computational Science: Modeling and Simulation for the Sciences* (2nd ed.). Princeton University Press.
[3] Oberkampf, W. L., & Roy, C. J. (2010). *Verification and Validation in Scientific Computing*. Cambridge University Press.
[4] Metropolis, N., & Ulam, S. (1949). The Monte Carlo Method. *Journal of the American Statistical Association*, 44(247), 335-341.
