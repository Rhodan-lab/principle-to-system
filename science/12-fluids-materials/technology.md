---
title: "Engineering with Fluids and Materials"
slug: "12-fluids-materials-tech"
module: "Module 12: Fluids, material properties, and structural behaviour"
domain: "technology"
status: draft
prerequisites: ["12-fluids-materials"]
connections: ["16-manufacturing-processes", "17-structural-engineering", "18-aerospace-systems"]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Technology: Engineering with Fluids and Materials

## 1. Scientific principles used

Engineering systems rely on the predictable behaviour of continuous media under stress. The primary scientific principles applied are:
- **Conservation of Mass and Energy in Fluids:** Utilised to control flow rates, pressures, and velocities in piping systems, nozzles, and aerodynamic surfaces (Bernoulli's principle and the continuity equation).
- **Viscous Dissipation:** Managed in lubrication systems to reduce friction, or exploited in dampers to absorb kinetic energy.
- **Linear Elasticity (Hooke's Law):** Used to design structures that must bear loads without permanent deformation, ensuring stresses remain below the material's yield strength.
- **Fracture Mechanics:** Applied to predict and prevent catastrophic failure by understanding how cracks propagate under stress, particularly in fatigue scenarios.
- **Composite Material Theory:** Combining materials with different properties (e.g., high tensile strength fibres in a tough matrix) to create structures that outperform homogeneous materials.

## 2. The engineering problem

Engineers must design systems that transport fluids efficiently, withstand external and internal forces without failing, and minimise weight while maximising strength. The core problem is managing stress. Whether it is the shear stress of a viscous fluid resisting flow in a pipeline, the tensile stress in a suspension bridge cable, or the complex stress states in an aircraft fuselage, the goal is to direct forces through materials that can safely bear them, while accounting for the inevitable presence of microscopic flaws and the limits of energy dissipation.

## 3. Main components

A typical fluid-structural system, such as a high-pressure hydraulic actuator or an aircraft wing, consists of:
- **Pressure Vessels/Pipes:** Contain fluids and resist hoop and longitudinal stresses.
- **Pumps/Compressors:** Add mechanical energy to fluids to overcome viscous friction and elevation changes.
- **Valves/Constrictions:** Control fluid flow by intentionally introducing pressure drops (utilising Bernoulli's principle and viscous losses).
- **Load-Bearing Members (Beams, Struts, Ties):** Solid components designed to resist bending, compression, and tension.
- **Composite Panels:** Lightweight, high-strength surfaces (e.g., carbon fibre reinforced polymers) used in aerospace and automotive applications.

## 4. How the components interact

In a hydraulic system, a pump increases the pressure energy of a fluid. This fluid travels through pipes, where viscous friction causes a gradual pressure drop. When the fluid reaches an actuator (a cylinder with a piston), the fluid pressure exerts a normal force on the piston area, converting fluid energy back into mechanical work. The cylinder walls must be made of a material with sufficient yield strength to withstand the internal pressure without plastic deformation. If the system experiences a sudden pressure spike, the material must possess enough fracture toughness to prevent any microscopic manufacturing flaws from propagating into a catastrophic crack [1] [3].

## 5. Matter, energy, force, or information flow

- **Matter Flow:** Fluids (liquids or gases) move through defined boundaries (pipes, channels) or around aerodynamic surfaces.
- **Energy Flow:** Mechanical energy from a pump is converted into fluid pressure and kinetic energy. Viscosity continuously dissipates some of this energy into heat.
- **Force Flow:** External loads applied to a structure are distributed internally as stress. The geometry of the structure and the stiffness (Young's modulus) of the materials dictate how these forces are routed to the supports or foundations.

## 6. System architecture

### Principle-to-System Chain: The Aircraft Wing
1. **Scientific Principle:** Bernoulli's principle and Newton's third law dictate that a fluid moving over a curved surface creates a pressure differential.
2. **Component Design:** The wing is shaped as an aerofoil to manipulate the airflow, creating lower pressure above and higher pressure below, generating lift.
3. **Material Selection:** The lift force creates massive bending moments at the wing root. The upper surface is in compression, the lower in tension.
4. **Structural Architecture:** The wing is built with a central spar (to resist bending) and ribs (to maintain the aerofoil shape). 
5. **Composite Integration:** To save weight, modern wings use carbon fibre composites. The carbon fibres provide immense tensile strength along their length, while the epoxy matrix holds them in place and transfers shear stresses between them [4].

## 7. Design constraints

- **Weight vs. Strength:** Especially in aerospace and automotive engineering, materials must have a high specific strength (strength-to-weight ratio).
- **Cost and Manufacturability:** Titanium is strong and light but expensive and difficult to machine. Steel is cheap and isotropic but heavy.
- **Corrosion and Environment:** Materials must resist chemical degradation. Fluids must not corrode their containers.
- **Fatigue Limit:** Structures subjected to cyclic loading (like an aircraft pressurising and depressurising) must be designed so that operating stresses do not cause microscopic cracks to grow over time.

## 8. Performance and efficiency

Efficiency in fluid systems is often dictated by minimising viscous losses. Smooth pipe interiors and laminar flow regimes reduce the energy required for pumping. In structural systems, performance is measured by the ability to carry loads with minimal material. This is achieved by placing material only where stresses are highest (e.g., the flanges of an I-beam) and using composite materials tailored to the specific directional loads of the application.

## 9. Reliability and failure modes

- **Yielding:** The material undergoes plastic deformation, permanently altering the shape of the component.
- **Buckling:** A sudden macroscopic failure of a structural member subjected to high compressive stress, dependent on geometry rather than material strength.
- **Fatigue Failure:** The progressive growth of cracks under cyclic loading, even when the maximum stress is well below the yield strength.
- **Brittle Fracture:** Sudden, catastrophic crack propagation with little plastic deformation, often occurring at low temperatures or in materials with low fracture toughness [4].
- **Cavitation:** In fluid systems, if the local pressure drops below the fluid's vapour pressure (often due to high velocity, per Bernoulli), bubbles form and violently collapse, eroding metal surfaces [1].

## 10. Safety principles

- **Factors of Safety:** Components are designed to withstand loads significantly higher than their expected maximum operating loads (e.g., a factor of safety of 1.5 means the structure can hold 150% of its rated load before yielding).
- **Fail-Safe Design:** If one component fails, the load is redistributed to other components, preventing total system collapse.
- **Leak-Before-Break:** Pressure vessels are designed so that a growing crack will penetrate the wall and cause a detectable leak before it reaches the critical length required for catastrophic brittle fracture.

## 11. Environmental and lifecycle considerations

The extraction and processing of metals and the manufacturing of carbon fibre composites are highly energy-intensive. While composites offer significant fuel savings during the operational life of a vehicle due to weight reduction, they are notoriously difficult to recycle compared to steel or aluminium. Fluid systems must also account for the environmental impact of leaks, particularly with hydraulic oils or chemical transport.

## 12. Connections to other technologies

- **16-manufacturing-processes:** Determines how materials can be shaped and how manufacturing flaws (which initiate fractures) are introduced.
- **17-structural-engineering:** Applies these material and fluid principles to the design of buildings, bridges, and dams.
- **18-aerospace-systems:** Heavily relies on advanced composites and fluid dynamics for vehicle design.

## 13. Sources

[1] J. G. Leishman, *Introduction to Aerospace Flight Vehicles*, Embry-Riddle Aeronautical University, 2023. [Online]. Available: https://eaglepubs.erau.edu/introductiontoaerospaceflightvehicles/chapter/energy-equation/
[3] Massachusetts Institute of Technology, *Mechanical Behavior of Materials, Part 1: Linear Elastic Behavior*, MITx. [Online]. Available: https://mitxonline.mit.edu/courses/course-v1:MITxT+3.032.1x/
[4] J. A. Nairn, "Fracture mechanics of composites with residual stresses," in *Comprehensive Composite Materials*, 2000. [Online]. Available: https://www.cof.orst.edu/cof/wse/faculty/Nairn/papers/Damage.pdf
