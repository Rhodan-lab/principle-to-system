---
title: "Exploring Fluids and Materials"
slug: 12-fluids-materials-explore
module: "Module 12"
domain: science
status: reviewed
prerequisites: [03-mathematical-models, 08-energy-thermodynamics, 09-motion-forces]
connections: [16-earth-planetary, 17-materials-manufacturing]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Explore: Fluids, Material Properties, and Structural Behaviour

## 1. Observation prompts

- **The Tap Stream:** Turn on a tap to a smooth, steady flow. Observe the shape of the water stream as it falls. Why does it get narrower further down?
- **The Honey Spoon:** Dip a spoon into honey and pull it out. Watch how the honey flows off the spoon. Compare this to water. What does this tell you about internal friction?
- **Stress–strain evidence:** Compare manufacturer curves or a classroom simulation for elastic, yielding, and fracture behaviour. Do not fatigue or break metal objects by hand; fractured ends can be sharp.

## 2. Prediction questions

- If you hold two sheets of paper vertically, parallel to each other and a few centimetres apart, and direct a gentle airflow between them, will the sheets move apart, move together, or stay still?
- If you have a thick rubber band and a thin rubber band of the same length, and you hang the same weight from both, which will stretch more? Why, in terms of stress and strain?
- In a fracture simulation, place an identical surface flaw on the tensile side and compressive side of a bent specimen. Which orientation produces the larger opening stress at the crack tip?

## 3. Worked reasoning examples

**Scenario:** A water tower supplies a town. The water level in the tower is 50 metres above a tap in a house. Assuming no viscous losses in the pipes, what is the velocity of the water when it exits the tap?

**Reasoning:**
1. **Identify the system and principles:** We are dealing with fluid flow driven by gravity. We can use Bernoulli's equation, assuming incompressible, inviscid flow.
2. **Set up the equation:** $P_1 + \frac{1}{2}\rho v_1^2 + \rho g z_1 = P_2 + \frac{1}{2}\rho v_2^2 + \rho g z_2$
3. **Define state 1 (top of the water tower):** The pressure $P_1$ is atmospheric pressure. The velocity $v_1$ is essentially zero (the tank is large, so the surface drops very slowly). The height $z_1$ is 50 m.
4. **Define state 2 (the tap):** The pressure $P_2$ is also atmospheric pressure (once the water exits the tap). The height $z_2$ is 0 m (our reference level). We want to find $v_2$.
5. **Simplify:** Since $P_1 = P_2$, they cancel out. Since $v_1 \approx 0$, that term disappears. The equation becomes: $\rho g z_1 = \frac{1}{2}\rho v_2^2$.
6. **Solve:** The density $\rho$ cancels out. $g z_1 = \frac{1}{2} v_2^2 \rightarrow v_2 = \sqrt{2 g z_1}$.
7. **Calculate:** $v_2 = \sqrt{2 \cdot 9.81 \cdot 50} = \sqrt{981} \approx 31.3 \text{ m/s}$.

## 4. Thought experiments

- **The Infinite Pipe:** Imagine a perfectly smooth, infinitely long horizontal pipe with water flowing through it. If the fluid has zero viscosity, do you need a pump to keep it moving? What if the fluid is real water with viscosity?
- **The Unbreakable Thread:** Imagine a material with an infinitely high yield strength but a very low Young's modulus. What would a bridge made of this material look like when a heavy truck drives over it?

## 5. Household and browser-based explorations

- **Continuity and losses simulation:** Use a virtual pipe model to vary cross-section, elevation, flow rate, viscosity, and pump head. Compare ideal continuity/Bernoulli predictions with a model that includes head loss; do not cut pressurised containers or restrict hoses.
- **Viscosity Race:** Place a drop of water, a drop of cooking oil, and a drop of honey at the top of a tilted baking tray. Time how long it takes each to reach the bottom. The difference in speed is a direct macroscopic observation of dynamic viscosity.
- **Composite load-sharing model:** Use a diagram or simulation of fibres embedded in a matrix. Remove one fibre and observe how interfacial shear transfers load to neighbours; distinguish this from claiming that taped food is an engineering composite.

## 6. Model-building prompts

- Construct a causal loop diagram showing the relationship between fluid velocity, pressure, and pipe cross-sectional area based on Bernoulli's principle and the continuity equation.
- Draw a stress-strain curve for a ductile metal (like steel) and a brittle material (like glass). Label the elastic region, the yield point, the plastic region, and the fracture point.

## 7. Self-explanation questions

- Explain in your own words under which assumptions a speed increase through a narrowing is accompanied by lower static pressure, and when pumps, elevation, losses, or compressibility change that conclusion, assuming no energy is added by a pump.
- Why does a crack in a material cause it to fail at a much lower overall stress than the material's theoretical strength?
- What is the physical difference between a material that is "stiff" (high Young's modulus) and a material that is "strong" (high yield strength)?

## 8. Transfer questions

- How do the principles of fluid viscosity apply to the design of motor oil for car engines operating at different temperatures?
- If bone is a composite material made of flexible collagen fibres and brittle calcium phosphate crystals, how does this hierarchical structure combine stiffness, toughness, and damage resistance under ordinary loading?
- How does the concept of stress concentration at a crack tip explain why it is easier to tear a piece of paper if you make a small cut in the edge first?

## 9. Suggested learning paths

- **To understand the mathematics of flow:** Study vector calculus and the derivation of the Navier-Stokes equations.
- **To understand material failure:** Investigate the microscopic mechanisms of dislocations in crystal lattices and how alloying elements impede their movement.
- **To explore advanced materials:** Research the manufacturing and failure modes of carbon fibre reinforced polymers (CFRP) used in modern aerospace.

## 10. Reasoning notes

- When applying Bernoulli's equation, always verify the assumptions: is the flow steady? Is it incompressible? Are viscous losses negligible? If the answer to any of these is no, the simple form of the equation will yield incorrect results.
- Remember that stress is not a force, but a force *distribution*. A small force applied to a microscopic area (like a pinprick) can create a massive stress, exceeding the material's yield strength.
- The distinction between elastic and plastic deformation is fundamental. Elasticity is reversible deformation described by a constitutive response; plasticity is irreversible deformation produced by mechanisms such as dislocation motion in crystals, molecular rearrangement in polymers, or damage in composites.

## Phase 7 review boundaries and validity limits

- Bernoulli's equation is an energy relation for specified steady-flow assumptions; a constriction does not universally cause a pressure drop without considering elevation, losses, pumps, compressibility, and boundary conditions.
- Aerodynamic lift comes from the complete pressure and shear distribution associated with circulation and momentum deflection. Bernoulli and Newton descriptions are consistent views of the same flow, not competing one-line causes.
- Viscosity relates stress to rate of deformation for a constitutive model. Newtonian behavior is not universal; many polymers, suspensions, and biological fluids are non-Newtonian.
- Stress and strain are tensor quantities in three dimensions. Scalar Hooke-law forms apply to simple uniaxial or shear cases in a linear elastic regime.
- Griffith's ideal brittle-fracture equation is geometry- and assumption-dependent. Engineering fracture assessment normally uses stress-intensity factors, energy-release rates, toughness data, and flaw geometry.
- Polycrystalline metals can be approximately isotropic only when texture and processing support that approximation; single crystals, wood, laminates, and many composites are anisotropic.

## 11. Sources


1. Leishman, J. G. *Introduction to Aerospace Flight Vehicles: Energy and Bernoulli Equations*. https://eaglepubs.erau.edu/introductiontoaerospaceflightvehicles/chapter/energy-equation/
2. University of Central Florida. *University Physics Volume 1: Bernoulli's Equation*. https://pressbooks.online.ucf.edu/osuniversityphysics/chapter/14-6-bernoullis-equation/
3. Massachusetts Institute of Technology. *Mechanical Behavior of Materials: Linear Elastic Behavior*. https://mitxonline.mit.edu/courses/course-v1:MITxT+3.032.1x/
4. Nairn, J. A. (2000). Fracture mechanics of composites with residual stresses. https://www.cof.orst.edu/cof/wse/faculty/Nairn/papers/Damage.pdf
5. NASA Glenn Research Center. *Bernoulli and Newton*. https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/bernoulli-and-newton/
