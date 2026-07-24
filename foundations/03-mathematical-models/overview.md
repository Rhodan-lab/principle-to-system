---
title: "Mathematical Models, Quantities, Vectors, and Scale"
slug: "03-mathematical-models"
module: "Module 03: Mathematical models, quantities, vectors, and scale"
domain: "foundations"
status: draft
prerequisites: ["01-scientific-reasoning"]
connections: ["04-classical-mechanics", "05-thermodynamics", "06-electromagnetism"]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Mathematical Models, Quantities, Vectors, and Scale

## 1. The central questions

How do we translate the physical world into the language of mathematics? When we observe a falling apple, a cooling cup of coffee, or a fluctuating stock market, how can we predict their future states? The central questions of mathematical modelling revolve around abstraction and quantification: What are the essential features of a system? How do these features relate to one another? How do changes in one quantity affect others? By constructing mathematical models, we bridge the gap between qualitative observation and quantitative prediction, allowing us to simulate reality, test hypotheses, and engineer solutions.

## 2. Observable phenomena

The physical world is replete with phenomena that demand mathematical description. A pendulum swings with a regular period, its motion tracing a sinusoidal curve. A population of bacteria grows exponentially until constrained by resources, at which point the growth rate slows, following a logistic curve. A heated metal rod cools down, its temperature approaching that of the surrounding air at a rate proportional to the temperature difference. These observable phenomena—periodic motion, exponential growth, and exponential decay—are not isolated events but manifestations of underlying mathematical structures that govern the universe.

## 3. Essential concepts

To build mathematical models, we must first define the language of quantities. 

**Scalars** are quantities fully described by a magnitude (a number) and a unit. Examples include mass ($m$), temperature ($T$), and time ($t$). 

**Vectors** are quantities that require both a magnitude and a direction for complete description. Examples include velocity ($\vec{v}$), force ($\vec{F}$), and acceleration ($\vec{a}$). Vectors are essential for modelling phenomena in multi-dimensional space.

**Tensors** are a generalization of scalars and vectors. A scalar is a tensor of rank 0, and a vector is a tensor of rank 1. Higher-rank tensors, such as the stress tensor or the moment of inertia tensor, describe complex relationships between vectors and are crucial in fields like fluid dynamics and general relativity.

**Functions** describe the relationship between variables. A function $f(x)$ assigns a unique output value to each input value $x$. Functions are the building blocks of mathematical models, representing how one quantity depends on another.

**Rates of change** describe how a quantity changes with respect to another, typically time or space. The derivative, a fundamental concept in calculus, formalizes the notion of an instantaneous rate of change.

## 4. Mechanisms and causal chains

Mathematical models capture the mechanisms and causal chains of physical systems. Consider a simple harmonic oscillator, such as a mass on a spring. The causal chain begins with a displacement from equilibrium, which generates a restoring force (Hooke's Law). This force causes an acceleration (Newton's Second Law), which changes the velocity, which in turn changes the displacement. This continuous feedback loop is elegantly captured by a differential equation, which relates the displacement, velocity, and acceleration of the mass.

## 5. Important quantities

Several quantities are fundamental to mathematical modelling across various domains:

| Quantity | Symbol | SI Unit | Description |
| :--- | :---: | :---: | :--- |
| Time | $t$ | $\text{s}$ | The continuous progression of existence and events. |
| Position | $\vec{r}$ | $\text{m}$ | The location of an object in space relative to a reference point. |
| Velocity | $\vec{v}$ | $\text{m/s}$ | The rate of change of position with respect to time. |
| Acceleration | $\vec{a}$ | $\text{m/s}^2$ | The rate of change of velocity with respect to time. |
| Mass | $m$ | $\text{kg}$ | A measure of an object's resistance to acceleration. |
| Force | $\vec{F}$ | $\text{N}$ ($\text{kg}\cdot\text{m/s}^2$) | An interaction that, when unopposed, changes the motion of an object. |

## 6. Mathematical models and equations

Mathematical models often take the form of differential equations, which relate a function to its derivatives. 

**Linearisation** is a powerful technique used to simplify complex, non-linear models. By approximating a non-linear function with a linear one near a specific point (often an equilibrium point), we can analyze the system's behavior using the tools of linear algebra and linear differential equations. For example, the equation for a simple pendulum is non-linear:
$$ \frac{d^2\theta}{dt^2} + \frac{g}{L}\sin(\theta) = 0 $$
For small angles ($\theta \approx 0$), we can linearise the equation using the approximation $\sin(\theta) \approx \theta$:
$$ \frac{d^2\theta}{dt^2} + \frac{g}{L}\theta = 0 $$
This linearised equation is much easier to solve and provides a highly accurate model for small oscillations.

**Dimensional analysis** is a method for checking the consistency of mathematical models and deriving relationships between physical quantities. By ensuring that the dimensions (e.g., length, mass, time) on both sides of an equation match, we can verify the model's validity and even deduce the form of unknown equations.

## 7. Definitions of symbols and units

- $\theta$: Angular displacement (radians, $\text{rad}$)
- $t$: Time (seconds, $\text{s}$)
- $g$: Acceleration due to gravity ($\approx 9.81 \text{ m/s}^2$)
- $L$: Length of the pendulum (meters, $\text{m}$)

## 8. Assumptions and approximations

Every mathematical model is an abstraction of reality and relies on assumptions and approximations. The linearised pendulum model assumes that the angle of swing is small, the string is massless and inextensible, and there is no air resistance or friction at the pivot. When these assumptions are violated (e.g., for large swings or in a viscous fluid), the model's predictions will diverge from reality, necessitating a more complex model.

## 9. Spatial and temporal scales

Mathematical models operate across a vast range of spatial and temporal scales. **Orders of magnitude** provide a way to compare quantities that differ vastly in size. For example, the mass of an electron is on the order of $10^{-30} \text{ kg}$, while the mass of the Sun is on the order of $10^{30} \text{ kg}$. 

**Scaling laws** describe how the properties of a system change as its size changes. For instance, the surface area of an object scales with the square of its characteristic length ($L^2$), while its volume scales with the cube ($L^3$). This square-cube law explains why large animals have proportionally thicker legs than small animals (to support their weight, which scales with volume) and why cells cannot grow indefinitely large (as their surface area, which controls nutrient exchange, would not keep pace with their volume).

## 10. Common misconceptions

A common misconception is that a mathematical model is a perfect representation of reality. In truth, as statistician George Box famously noted, "All models are wrong, but some are useful." Models are simplifications designed to capture the essential features of a system while ignoring irrelevant details. Another misconception is that more complex models are always better. Often, a simple, linearised model provides more insight and is easier to analyze than a highly complex, non-linear model, provided the assumptions of the simple model hold.

## 11. Connections to other modules

- **01-scientific-reasoning**: Mathematical models are the formal expression of scientific hypotheses and theories.
- **04-classical-mechanics**: Classical mechanics relies heavily on vectors, differential equations, and calculus to model the motion of objects.
- **05-thermodynamics**: Thermodynamics uses mathematical models to describe the transfer of heat and work, often employing statistical mechanics to bridge microscopic and macroscopic scales.

## 12. Sources

1. Meerschaert, M. M. (2013). *Mathematical Modeling* (4th ed.). Academic Press. [1]
2. Mahajan, S. (2010). *Street-Fighting Mathematics: The Art of Educated Guessing and Opportunistic Problem Solving*. MIT Press. [2]
3. Barenblatt, G. I. (1996). *Scaling, Self-similarity, and Intermediate Asymptotics: Dimensional Analysis and Intermediate Asymptotics*. Cambridge University Press. [3]
4. Giordano, F. R., Fox, W. P., & Horton, S. B. (2013). *A First Course in Mathematical Modeling* (5th ed.). Brooks/Cole. [4]
