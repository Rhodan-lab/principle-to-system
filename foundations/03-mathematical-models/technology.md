---
title: "Engineering with Mathematical Models"
slug: "03-mathematical-models-technology"
module: "Module 03: Mathematical models, quantities, vectors, and scale"
domain: "technology"
status: draft
prerequisites: ["03-mathematical-models"]
connections: ["04-classical-mechanics", "07-control-systems"]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Engineering with Mathematical Models

## 1. Scientific principles used

The engineering of complex systems relies fundamentally on the scientific principles of mathematical modelling, dimensional analysis, and scaling laws. By representing physical phenomena through differential equations, vectors, and tensors, engineers can simulate, predict, and optimize system behavior before physical construction begins. The principle of linearisation allows for the simplification of complex dynamics, enabling the design of robust control systems.

## 2. The engineering problem

The core engineering problem is how to design systems that perform reliably and efficiently in the real world, given constraints on time, cost, and materials. Trial-and-error physical prototyping is often prohibitively expensive, dangerous, or impossible (e.g., designing a spacecraft trajectory or a skyscraper's response to earthquakes). The solution is to build mathematical models that accurately capture the system's dynamics, allowing engineers to explore the design space virtually.

## 3. Main components

In the context of engineering with mathematical models, the "components" are the mathematical and computational tools used to represent the physical system:

- **State Variables**: Quantities that define the current condition of the system (e.g., position, velocity, temperature, pressure).
- **Parameters**: Constants that define the system's physical properties (e.g., mass, stiffness, resistance).
- **Governing Equations**: Differential equations derived from physical laws (e.g., Newton's laws, Maxwell's equations) that describe how state variables change over time and space.
- **Boundary and Initial Conditions**: The specific constraints and starting states applied to the governing equations to solve for a particular scenario.
- **Computational Solvers**: Algorithms (e.g., finite element analysis, computational fluid dynamics) used to numerically solve the governing equations when analytical solutions are impossible.

## 4. How the components interact

The engineering process begins by identifying the relevant state variables and parameters. Governing equations are then formulated to describe the interactions between these variables. For example, in structural engineering, the stress tensor (a mathematical component) interacts with the material's stiffness parameters to determine the resulting strain (deformation) under a given load. These equations are subjected to boundary conditions (e.g., the base of a building is fixed to the ground) and solved using computational tools to predict the system's response.

## 5. Matter, energy, force, or information flow

Mathematical models track the flow of matter, energy, force, and information through a system. In a fluid dynamics model of a pipe network, the equations track the flow of matter (water) and energy (pressure and kinetic energy). In a control system model, the equations track the flow of information (sensor readings) and force (actuator commands) to maintain a desired state.

## 6. System architecture

The architecture of a mathematical model often mirrors the physical architecture of the system it represents. A complex system, such as an aircraft, is modelled as a hierarchy of subsystems (aerodynamics, propulsion, structures, control). Each subsystem has its own mathematical model, and these models are coupled together to simulate the entire aircraft's behavior. This modular architecture allows specialized engineering teams to work on different aspects of the design simultaneously.

## 7. Design constraints

Mathematical models are essential for navigating design constraints. Engineers use models to perform optimization, searching for the combination of parameters that maximizes performance while satisfying constraints on weight, cost, strength, and efficiency. Dimensional analysis helps identify the dimensionless groups (e.g., Reynolds number, Mach number) that govern the system's behavior, reducing the number of variables that need to be tested and simplifying the design space.

## 8. Performance and efficiency

The performance and efficiency of an engineered system are directly tied to the accuracy of its mathematical models. A more accurate model allows engineers to design closer to the physical limits of the materials, reducing safety margins and saving weight and cost. However, increasing model fidelity often requires more computational power and time. Engineers must balance the need for accuracy with the cost of computation, often using simplified, linearised models for initial design and high-fidelity, non-linear models for final verification.

## 9. Reliability and failure modes

Mathematical models are crucial for predicting and preventing failure. By simulating extreme conditions and edge cases, engineers can identify potential failure modes (e.g., resonance, fatigue, buckling) before they occur in the real world. Probabilistic models, which incorporate uncertainty in parameters and operating conditions, are used to assess the reliability of the system and ensure it meets safety standards.

## 10. Safety principles

Safety in engineering relies on the principle of conservative modelling. When uncertainties exist, engineers make assumptions that err on the side of safety (e.g., assuming a material is weaker than it likely is, or a load is heavier than expected). Mathematical models are also used to design fail-safe mechanisms and redundancy, ensuring that the failure of one component does not lead to catastrophic system failure.

## 11. Environmental and lifecycle considerations

Mathematical models are increasingly used to assess the environmental impact and lifecycle of engineered systems. Models can predict energy consumption, emissions, and material degradation over the system's lifespan, allowing engineers to design for sustainability and circularity.

## 12. Connections to other technologies

- **Computer-Aided Engineering (CAE)**: Software tools that implement mathematical models for structural, thermal, and fluid analysis.
- **Digital Twins**: Virtual replicas of physical systems that are continuously updated with real-time sensor data, relying on underlying mathematical models to predict future behavior and optimize performance.
- **Control Systems**: Technologies that use mathematical models to regulate the behavior of dynamic systems, from thermostats to autonomous vehicles.

## 13. Sources

1. Meerschaert, M. M. (2013). *Mathematical Modeling* (4th ed.). Academic Press. [1]
2. Mahajan, S. (2010). *Street-Fighting Mathematics: The Art of Educated Guessing and Opportunistic Problem Solving*. MIT Press. [2]
3. Barenblatt, G. I. (1996). *Scaling, Self-similarity, and Intermediate Asymptotics: Dimensional Analysis and Intermediate Asymptotics*. Cambridge University Press. [3]
4. Giordano, F. R., Fox, W. P., & Horton, S. B. (2013). *A First Course in Mathematical Modeling* (5th ed.). Brooks/Cole. [4]
