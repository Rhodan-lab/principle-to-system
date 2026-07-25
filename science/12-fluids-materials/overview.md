---
title: "Fluids, Material Properties, and Structural Behaviour"
slug: 12-fluids-materials
module: "Module 12"
domain: science
status: reviewed
prerequisites: [03-mathematical-models, 08-energy-thermodynamics, 09-motion-forces]
connections: [16-earth-planetary, 17-materials-manufacturing]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Overview: Fluids, Material Properties, and Structural Behaviour

## 1. The central questions

How do continuous media—whether liquid, gas, or solid—respond to applied forces? Why do some materials flow endlessly under shear while others deform slightly and spring back, or permanently bend, or suddenly shatter? Understanding the physical world requires moving beyond point masses and rigid bodies to examine how matter behaves when its internal structure is subjected to stress. This module explores the continuum mechanics of fluids and solids, asking how energy is conserved in a moving fluid, how internal friction resists flow, and how the atomic bonds within solid materials dictate their macroscopic strength, elasticity, and failure.

## 2. Observable phenomena

The principles of fluid and solid mechanics manifest in everyday observations. Water flowing from a tap narrows as it accelerates downward, a consequence of mass conservation. An aeroplane wing generates lift because of the pressure distribution in the moving air around it. Honey pours much slower than water due to its high internal friction. In solids, a rubber band stretches and returns to its original shape, while a paperclip bent too far remains permanently deformed. A glass drops and shatters instantly, whereas a dented car bumper absorbs the impact. These phenomena reveal the underlying rules governing how matter distributes and dissipates applied energy.

## 3. Essential concepts

### Fluid Mechanics
A **fluid** is a substance that continuously deforms (flows) under an applied shear stress, no matter how small. Fluids include liquids, which are largely incompressible, and gases, which are highly compressible. 
- **Fluid Statics:** The study of fluids at rest, where pressure increases with depth due to gravity.
- **Fluid Dynamics:** The study of fluids in motion, governed by the conservation of mass, momentum, and energy.
- **Viscosity:** A constitutive measure relating stress to deformation rate; for a Newtonian fluid, shear stress is proportional to the velocity gradient.
- **Laminar vs. Turbulent Flow:** Laminar flow occurs in smooth, parallel layers, while turbulent flow is characterised by chaotic changes in pressure and flow velocity.

### Solid Mechanics and Material Properties
A **solid** resists shear stress by deforming up to a point and then holding its shape.
- **Stress and Strain:** Stress is the internal force per unit area within a material, while strain is the resulting relative deformation.
- **Elasticity:** The ability of a material to return to its original shape after the stress is removed.
- **Plasticity:** Permanent, non-reversible deformation that occurs when a material is stressed beyond its elastic limit (yield point).
- **Fracture Mechanics:** The study of the propagation of cracks in materials.
- **Composite Materials:** Materials made from two or more constituent materials with significantly different physical or chemical properties, which remain separate and distinct at the macroscopic or microscopic scale within the finished structure.

## 4. Mechanisms and causal chains

### Energy Conservation in Fluid Flow
In a steady, incompressible, frictionless flow along a streamline, the total mechanical energy of the fluid is conserved. This is expressed by Bernoulli's principle. As a fluid moves through a constriction, its velocity must increase to conserve mass (continuity equation). Because kinetic energy increases, the pressure energy must decrease to conserve total energy. For a specified streamline with negligible losses and no added shaft work, continuity and the energy equation relate area, velocity, pressure, and elevation. A constriction often raises speed, but the pressure response depends on the complete boundary conditions. Aerodynamic lift requires the full pressure and shear distribution and momentum deflection, not Bernoulli's equation alone [1].

### Viscous Dissipation
Real fluids possess viscosity. When fluid layers move at different velocities, intermolecular forces create friction between the layers. This shear stress transfers momentum from faster layers to slower ones, dissipating mechanical energy into thermal energy. In pipes, this causes a pressure drop along the length of the flow, requiring a pump to maintain movement [2].

### Elastic and Plastic Deformation
When a solid is subjected to an external load, the atomic bonds stretch. In the elastic regime, this stretching is reversible; removing the load allows the atoms to return to their equilibrium positions. If the stress exceeds the yield strength, dislocations (defects in the crystal lattice) begin to move and multiply. This slip mechanism causes permanent plastic deformation. The material absorbs energy as it deforms, a property known as toughness [3].

### Fracture and Crack Propagation
All materials contain microscopic flaws. When stress is applied, it concentrates at the tips of these flaws. If the local stress exceeds the cohesive strength of the atomic bonds, the crack propagates. In brittle materials (like glass), this happens rapidly with little energy absorption. In ductile materials (like steel), plastic deformation at the crack tip blunts the flaw, absorbing energy and resisting further crack growth [4].

## 5. Important quantities

| Quantity | Symbol | SI Unit | Description |
| :--- | :---: | :--- | :--- |
| Pressure | $P$ | Pascal ($\text{Pa}$ or $\text{N/m}^2$) | Force applied perpendicular to the surface of an object per unit area. |
| Density | $\rho$ | $\text{kg/m}^3$ | Mass per unit volume. |
| Dynamic Viscosity | $\mu$ | $\text{Pa}\cdot\text{s}$ | Resistance of a fluid to shear flow. |
| Kinematic Viscosity | $\nu$ | $\text{m}^2/\text{s}$ | Ratio of dynamic viscosity to density ($\mu/\rho$). |
| Stress | $\sigma$ (normal), $\tau$ (shear) | Pascal ($\text{Pa}$) | Internal resisting force per unit area. |
| Strain | $\varepsilon$ (normal), $\gamma$ (shear) | Dimensionless | Ratio of deformation to original dimension. |
| Young's Modulus | $E$ | Pascal ($\text{Pa}$) | Measure of stiffness in the linear elastic region. |
| Yield Strength | $\sigma_y$ | Pascal ($\text{Pa}$) | Stress at which plastic deformation begins. |

## 6. Mathematical models and equations

### Fluid Statics
The pressure $P$ at a depth $h$ in an incompressible fluid at rest is given by the hydrostatic equation:
$$ P = P_0 + \rho g h $$
where $P_0$ is the pressure at the surface, $\rho$ is the fluid density, and $g$ is the acceleration due to gravity.

### Continuity Equation
For an incompressible fluid flowing through a pipe, the mass flow rate is constant. Thus, the product of the cross-sectional area $A$ and the flow velocity $v$ is constant:
$$ A_1 v_1 = A_2 v_2 $$

### Bernoulli's Equation
For steady, incompressible, frictionless flow along a streamline, the sum of pressure energy, kinetic energy, and potential energy per unit volume is constant:
$$ P + \frac{1}{2}\rho v^2 + \rho g z = \text{constant} $$
where $P$ is the static pressure, $v$ is the fluid velocity, and $z$ is the elevation [1].

### Hooke's Law (Linear Elasticity)
In the linear elastic regime, normal stress $\sigma$ is directly proportional to normal strain $\varepsilon$:
$$ \sigma = E \varepsilon $$
where $E$ is Young's modulus. Similarly, for shear stress $\tau$ and shear strain $\gamma$:
$$ \tau = G \gamma $$
where $G$ is the shear modulus [3].

### Fracture Mechanics (Griffith Criterion)
For a brittle material containing a crack of length $2a$, the critical stress $\sigma_c$ required for crack propagation is:
$$ \sigma_c = \sqrt{\frac{2 E \gamma_s}{\pi a}} $$
where $E$ is Young's modulus and $\gamma_s$ is the surface energy per unit area [4].

## 7. Definitions of symbols and units

- $P$: Pressure ($\text{Pa}$)
- $P_0$: Reference or surface pressure ($\text{Pa}$)
- $\rho$: Density ($\text{kg/m}^3$)
- $g$: Acceleration due to gravity ($\approx 9.81 \text{ m/s}^2$)
- $h$: Depth below the surface ($\text{m}$)
- $A$: Cross-sectional area ($\text{m}^2$)
- $v$: Fluid velocity ($\text{m/s}$)
- $z$: Elevation above a reference datum ($\text{m}$)
- $\sigma$: Normal stress ($\text{Pa}$)
- $\varepsilon$: Normal strain (dimensionless)
- $E$: Young's modulus ($\text{Pa}$)
- $\tau$: Shear stress ($\text{Pa}$)
- $\gamma$: Shear strain (dimensionless)
- $G$: Shear modulus ($\text{Pa}$)
- $\sigma_c$: Critical fracture stress ($\text{Pa}$)
- $a$: Half crack length ($\text{m}$)
- $\gamma_s$: Surface energy ($\text{J/m}^2$)

## 8. Assumptions and approximations

- **Continuum Assumption:** Both fluids and solids are treated as continuous media, ignoring their discrete atomic structure. This is valid when the physical dimensions of the system are much larger than the mean free path of the molecules.
- **Incompressibility:** In Bernoulli's equation and the continuity equation, liquids (and gases at low Mach numbers, typically $< 0.3$) are assumed to have constant density.
- **Inviscid Flow:** Bernoulli's equation assumes zero viscosity, meaning no energy is lost to friction. This is a significant approximation and is only valid outside the boundary layer where viscous effects are negligible.
- **Linear Elasticity:** Hooke's law assumes that deformations are small and that the material returns exactly to its original shape. It fails once the yield point is reached.
- **Isotropy:** Many basic models assume materials have the same properties in all directions. This may approximate some randomly oriented polycrystalline metals, but processing texture, single crystals, wood, and composite laminates can be strongly anisotropic.

## 9. Spatial and temporal scales

- **Microscopic Scale ($10^{-9}$ to $10^{-6}$ m):** Atomic bonds, crystal lattice defects (dislocations), and micro-cracks dictate the macroscopic properties of solids.
- **Mesoscopic Scale ($10^{-6}$ to $10^{-3}$ m):** Grain boundaries in metals and fiber-matrix interfaces in composites influence strength and fracture toughness.
- **Macroscopic Scale ($10^{-3}$ to $10^2$ m):** The scale of engineering structures (beams, pipes, aircraft wings) where continuum mechanics equations are applied.
- **Temporal Scales:** Fluid flow can change in milliseconds (turbulence), while solid deformation can occur instantly (elastic snap) or over years (creep under constant stress at high temperatures).

## 10. Common misconceptions

- **Misconception:** Bernoulli's principle alone explains aerodynamic lift.
  **Correction:** While Bernoulli's equation relates pressure and velocity, it does not explain *why* the air moves faster over the top of a wing. A complete explanation requires Newton's laws, the Coanda effect, and the downward deflection of the airflow (downwash).
- **Misconception:** Strong materials are always tough.
  **Correction:** Strength is the ability to withstand stress without yielding or breaking, while toughness is the ability to absorb energy before fracturing. Glass is very strong in compression but extremely brittle (low toughness).
- **Misconception:** Fluids only exert pressure downwards.
  **Correction:** In a static fluid, pressure is isotropic; it acts equally in all directions at a given point.

## 11. Connections to other modules

- **03-mathematical-models:** Provides the calculus and differential equations necessary to derive and solve the Navier-Stokes equations and elasticity tensors.
- **08-energy-thermodynamics:** Connects viscous dissipation in fluids to the generation of thermal energy and entropy.
- **09-motion-forces:** The foundation of continuum mechanics; stress is simply force distributed over an area, and fluid dynamics is Newton's second law applied to a continuous medium.

## Phase 7 review boundaries and validity limits

- Bernoulli's equation is an energy relation for specified steady-flow assumptions; a constriction does not universally cause a pressure drop without considering elevation, losses, pumps, compressibility, and boundary conditions.
- Aerodynamic lift comes from the complete pressure and shear distribution associated with circulation and momentum deflection. Bernoulli and Newton descriptions are consistent views of the same flow, not competing one-line causes.
- Viscosity relates stress to rate of deformation for a constitutive model. Newtonian behavior is not universal; many polymers, suspensions, and biological fluids are non-Newtonian.
- Stress and strain are tensor quantities in three dimensions. Scalar Hooke-law forms apply to simple uniaxial or shear cases in a linear elastic regime.
- Griffith's ideal brittle-fracture equation is geometry- and assumption-dependent. Engineering fracture assessment normally uses stress-intensity factors, energy-release rates, toughness data, and flaw geometry.
- Polycrystalline metals can be approximately isotropic only when texture and processing support that approximation; single crystals, wood, laminates, and many composites are anisotropic.

## 12. Sources



1. Leishman, J. G. *Introduction to Aerospace Flight Vehicles: Energy and Bernoulli Equations*. https://eaglepubs.erau.edu/introductiontoaerospaceflightvehicles/chapter/energy-equation/
2. University of Central Florida. *University Physics Volume 1: Bernoulli's Equation*. https://pressbooks.online.ucf.edu/osuniversityphysics/chapter/14-6-bernoullis-equation/
3. Massachusetts Institute of Technology. *Mechanical Behavior of Materials: Linear Elastic Behavior*. https://mitxonline.mit.edu/courses/course-v1:MITxT+3.032.1x/
4. Nairn, J. A. (2000). Fracture mechanics of composites with residual stresses. https://www.cof.orst.edu/cof/wse/faculty/Nairn/papers/Damage.pdf
