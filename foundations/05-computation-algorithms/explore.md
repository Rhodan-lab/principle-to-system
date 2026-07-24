---
title: "Explore: Computation and Simulation"
slug: "05-computation-algorithms-explore"
module: "Module 05: Computation, algorithms, numerical methods, and simulation"
domain: "foundations"
status: draft
prerequisites: ["05-computation-algorithms", "05-computation-algorithms-technology"]
connections: ["06-systems-control", "07-data-information"]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Explore: Computation and Simulation

## 1. Observation prompts

- Open a weather forecasting application that shows a radar or wind map. Zoom in as far as possible. Can you identify the discrete grid cells (pixels or blocks) where the simulation calculates the data? How large is the spatial step ($\Delta x$) in your local area?
- Look at a digital photograph of a smooth gradient, like a clear blue sky. Zoom in until you see individual pixels. This is spatial discretisation. How does the illusion of a continuous sky break down at the discrete level?
- Watch a video game or a 3D animated film. Observe how curved surfaces (like a character's face or a car tire) are actually composed of flat polygons. This is geometric discretisation.

## 2. Prediction questions

- If you double the resolution of a 3D simulation grid (halving $\Delta x$, $\Delta y$, and $\Delta z$), by what factor does the number of spatial grid points increase? 
- If the Courant-Friedrichs-Lewy (CFL) condition requires that $\Delta t \le \Delta x / v$, what must happen to the time step if you halve the spatial step $\Delta x$?
- Based on the previous two answers, if you halve the spatial step in a 3D simulation, by what factor does the total computational time increase (assuming the physical time simulated remains the same)?

## 3. Worked reasoning examples

**Estimating Pi using a Monte Carlo Method**

Imagine a square with side length $2r$, and a circle inscribed within it with radius $r$. 
The area of the square is $A_s = (2r)^2 = 4r^2$.
The area of the circle is $A_c = \pi r^2$.
The ratio of their areas is $A_c / A_s = \pi r^2 / 4r^2 = \pi / 4$.

If we randomly throw darts at the square, the probability that a dart lands inside the circle is equal to the ratio of their areas ($\pi / 4$).

1. Generate $N$ random points $(x, y)$ where $x$ and $y$ are between $-r$ and $r$.
2. For each point, calculate its distance from the centre: $d = \sqrt{x^2 + y^2}$.
3. If $d \le r$, the point is inside the circle. Count this as $N_{inside}$.
4. The ratio $N_{inside} / N$ approximates $\pi / 4$.
5. Therefore, $\pi \approx 4 \times (N_{inside} / N)$.

As $N$ increases, the approximation of $\pi$ becomes more accurate, demonstrating how random sampling can solve a deterministic geometric problem.

## 4. Thought experiments

- **The Infinite Precision Machine**: Imagine a computer with infinite memory that can represent real numbers with zero round-off error. Would numerical simulations on this machine be perfectly accurate? (Consider truncation error and modelling error).
- **The Butterfly Effect in Simulation**: In a weather simulation, you change the initial temperature of a single grid cell in Brazil by $0.000001^\circ\text{C}$. Due to the non-linear equations of fluid dynamics, how might this affect the simulated weather in Texas a month later? How does this limit the predictive power of simulations, regardless of computational power?

## 5. Household and browser-based explorations

- **Spreadsheet Integration**: Open a spreadsheet program. Create a column of $x$ values from $0$ to $1$ in steps of $0.1$ ($\Delta x = 0.1$). In the next column, calculate $y = x^2$. In a third column, calculate the area of the trapezoid for each step: $(y_i + y_{i-1}) / 2 \times \Delta x$. Sum the third column. Compare your result to the analytical integral of $x^2$ from $0$ to $1$ (which is $1/3 \approx 0.333$). Decrease $\Delta x$ to $0.01$ and see how the error changes.
- **Browser Physics Engines**: Search for a browser-based 2D physics sandbox (like Matter.js or Box2D demonstrations). Build a tall tower of blocks. Find the setting to change the "time step" or "iterations per step." Lower the iterations significantly and watch the tower collapse or blocks pass through each other. This demonstrates numerical instability when the solver cannot resolve the collision forces accurately within the given discrete steps.

## 6. Model-building prompts

- **Population Dynamics**: Build a simple discrete model of a rabbit population. Let $P_n$ be the population in year $n$. Assume the population grows by $10\%$ each year, but $50$ rabbits are eaten by foxes. The discrete equation is $P_{n+1} = P_n + 0.10 P_n - 50$. Start with $P_0 = 1000$ and calculate the population for the next 10 years. What happens if you change the initial population to $400$?
- **Cooling Coffee**: Newton's Law of Cooling states that the rate of heat loss is proportional to the temperature difference between the object and its surroundings. Write a finite difference equation to model the temperature of a cup of coffee over time. Choose a time step $\Delta t$ and a cooling constant $k$. Calculate the temperature minute by minute.

## 7. Self-explanation questions

- Explain the difference between truncation error and round-off error in your own words.
- Why is it impossible to simulate the exact trajectory of every molecule in a glass of water, and how do numerical methods bypass this problem?
- If a simulation perfectly matches the results of a physical experiment, does that mean the mathematical model is a perfect representation of reality? Why or why not?

## 8. Transfer questions

- How do the principles of discretisation apply to digital audio recording? What are the equivalents of $\Delta t$ and round-off error in an MP3 file?
- In financial risk management, banks use Monte Carlo simulations to predict the probability of massive portfolio losses. How is this similar to, and different from, using Monte Carlo methods to calculate the area of a circle?

## 9. Suggested learning paths

- To understand the mathematics of discretisation: Study Taylor series expansions and basic numerical calculus (Euler's method for differential equations).
- To understand algorithmic implementation: Learn a programming language like Python and write a script to solve the 1D heat equation using finite differences.
- To understand computational complexity: Study Big O notation and the difference between polynomial ($O(n^2)$) and exponential ($O(2^n)$) time algorithms.

## 10. Reasoning notes

When evaluating any computational claim (e.g., "Our AI model predicts a 20% increase in traffic"), always ask:
1. What are the underlying mathematical equations?
2. What is the spatial and temporal resolution of the data?
3. What assumptions were made to simplify the model?
4. Has this specific simulation framework been validated against historical, real-world data? 
Never accept a simulation output as ground truth; it is always an approximation bounded by its discretisation and assumptions.
