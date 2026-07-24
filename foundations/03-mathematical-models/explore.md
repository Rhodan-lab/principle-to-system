---
title: "Exploring Mathematical Models and Scale"
slug: "03-mathematical-models-explore"
module: "Module 03: Mathematical models, quantities, vectors, and scale"
domain: "foundations"
status: draft
prerequisites: ["03-mathematical-models"]
connections: ["04-classical-mechanics"]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Exploring Mathematical Models and Scale

## 1. Observation prompts

- Observe the flow of water from a tap. How does the shape of the water stream change as you increase the flow rate? Can you identify a transition from smooth (laminar) flow to chaotic (turbulent) flow?
- Look at the branches of a tree or the veins in a leaf. Notice how the patterns repeat at different scales. This is an example of self-similarity, a concept closely related to scaling laws.
- Watch a pendulum swing (you can make one with a string and a small weight). Does the time it takes to complete one swing (the period) seem to depend on how high you release it? What happens if you change the length of the string or the mass of the weight?

## 2. Prediction questions

- If you double the length of a pendulum, what do you predict will happen to its period? Will it double, halve, or change by some other factor?
- Imagine a spherical balloon. If you double its radius, by what factor does its surface area increase? By what factor does its volume increase?
- If an animal were scaled up to be twice as tall, twice as wide, and twice as long, how much heavier would it be? Would its legs need to be proportionally thicker or thinner to support the new weight?

## 3. Worked reasoning examples

**Dimensional Analysis of a Pendulum**

Let's use dimensional analysis to deduce the formula for the period ($T$) of a simple pendulum. We assume the period might depend on the mass of the bob ($m$), the length of the string ($L$), and the acceleration due to gravity ($g$).

1.  **Identify dimensions:**
    -   $[T] = \text{Time (T)}$
    -   $[m] = \text{Mass (M)}$
    -   $[L] = \text{Length (L)}$
    -   $[g] = \text{Length/Time}^2 (\text{L/T}^2)$

2.  **Set up the equation:**
    Assume $T \propto m^a L^b g^c$.
    In terms of dimensions: $\text{T} = \text{M}^a \text{L}^b (\text{L/T}^2)^c$

3.  **Equate dimensions:**
    -   Mass (M): $0 = a$ (The period does not depend on mass!)
    -   Length (L): $0 = b + c$
    -   Time (T): $1 = -2c$

4.  **Solve for exponents:**
    -   $c = -1/2$
    -   $b = 1/2$

5.  **Construct the final formula:**
    $T \propto L^{1/2} g^{-1/2} = \sqrt{\frac{L}{g}}$
    The actual formula, derived from differential equations, is $T = 2\pi\sqrt{\frac{L}{g}}$. Dimensional analysis gave us the correct functional form, missing only the dimensionless constant $2\pi$.

## 4. Thought experiments

- **The Isometrically Scaled Giant:** Imagine a human scaled up isometrically (all proportions remain exactly the same) to be 10 times taller. Their volume (and thus mass) would increase by a factor of $10^3 = 1000$. However, the cross-sectional area of their leg bones, which determines their strength, would only increase by a factor of $10^2 = 100$. The giant's bones would experience 10 times more stress than a normal human's, likely causing them to shatter under their own weight. This thought experiment illustrates why large animals have proportionally thicker limbs (allometric scaling).
- **The Frictionless World:** Imagine a world where friction and air resistance do not exist. If you set a pendulum in motion, it would swing forever. If you pushed a block on a flat surface, it would slide indefinitely at a constant velocity. This idealized world is often the starting point for mathematical models in physics, allowing us to isolate the effects of other forces before adding the complexity of friction back in.

## 5. Household and browser-based explorations

- **Pendulum Experiment:** Build a simple pendulum using string and a small, dense object (like a nut or a washer). Measure the time it takes for 10 complete swings for different lengths of string. Plot the period (time for one swing) against the length, and then against the square root of the length. What do you observe?
- **Scaling in Baking:** Find a recipe for a cake. If you want to bake a cake that is twice as wide and twice as long (but the same height), how should you adjust the ingredients? What if you want a cake that is twice as wide, twice as long, and twice as high?
- **Browser Simulation:** Search for "PhET Pendulum Lab" online. Use the interactive simulation to explore how changing the mass, length, gravity, and friction affects the motion of a pendulum. Verify the results of your dimensional analysis and physical experiments.

## 6. Model-building prompts

- **Cooling Coffee:** Formulate a simple mathematical model for the temperature of a cup of coffee over time. Assume the rate of cooling is proportional to the difference between the coffee's temperature and the room temperature (Newton's Law of Cooling). What parameters would you need to measure to calibrate your model?
- **Population Growth:** Create a model for the population of rabbits on an island. Start with a simple exponential growth model (birth rate is proportional to the current population). Then, refine the model by adding a carrying capacity (a maximum population the island can support), leading to a logistic growth model.

## 7. Self-explanation questions

- Why is it useful to linearise a non-linear differential equation? What are the limitations of this approach?
- Explain the difference between a scalar, a vector, and a tensor. Give an example of a physical quantity that requires a tensor for its description.
- How does dimensional analysis help us check the validity of an equation? Can it tell us if an equation is definitely correct?

## 8. Transfer questions

- The square-cube law explains why large animals have proportionally thicker legs. How might this law apply to the design of buildings or bridges?
- Exponential decay describes the cooling of a cup of coffee and the radioactive decay of isotopes. Can you think of a phenomenon in economics or sociology that might also follow an exponential decay model?
- We used dimensional analysis to find the period of a pendulum. Could you use the same technique to find the speed of a wave on a stretched string, given that it depends on the tension force and the mass per unit length of the string?

## 9. Suggested learning paths

- **Calculus and Differential Equations:** To deeply understand mathematical modelling, a solid foundation in calculus (derivatives and integrals) and differential equations is essential.
- **Linear Algebra:** For working with vectors, matrices, and linearised systems, linear algebra provides the necessary mathematical framework.
- **Computational Modelling:** Learn a programming language (like Python or MATLAB) to numerically solve complex models that cannot be solved analytically.

## 10. Reasoning notes

When building mathematical models, always start simple. Identify the most crucial variables and the fundamental laws governing their interaction. Make simplifying assumptions (like ignoring air resistance or assuming small angles) to create a tractable model. Once you understand the behavior of the simple model, gradually add complexity to capture more subtle effects. Always verify your model's predictions against real-world observations or experimental data. Remember that a model is a tool for understanding, not a perfect replica of reality.
