---
title: "Exploring Fluids and Materials"
slug: "12-fluids-materials-explore"
module: "Module 12: Fluids, material properties, and structural behaviour"
domain: "science"
status: draft
prerequisites: ["12-fluids-materials"]
connections: []
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Explore: Fluids, Material Properties, and Structural Behaviour

## 1. Observation prompts

- **The Tap Stream:** Turn on a tap to a smooth, steady flow. Observe the shape of the water stream as it falls. Why does it get narrower further down?
- **The Honey Spoon:** Dip a spoon into honey and pull it out. Watch how the honey flows off the spoon. Compare this to water. What does this tell you about internal friction?
- **The Paperclip Bend:** Take a metal paperclip and bend it slightly, then let go. Now bend it severely until it stays bent. Finally, bend it back and forth rapidly in the same spot until it breaks. What three distinct material behaviours have you just observed?

## 2. Prediction questions

- If you hold two sheets of paper vertically, parallel to each other and a few centimetres apart, and blow air strongly between them, will the sheets move apart, move together, or stay still?
- If you have a thick rubber band and a thin rubber band of the same length, and you hang the same weight from both, which will stretch more? Why, in terms of stress and strain?
- If you scratch the surface of a glass rod and then try to bend it, will it break easier if the scratch is on the inside of the bend (under compression) or the outside of the bend (under tension)?

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

- **The Venturi Tube:** Take a plastic bottle and carefully cut a small hole in the side near the bottom. Fill it with water and watch the stream. Now, attach a hose to a tap, pinch the end of the hose to make the opening smaller, and observe the speed of the water. You are manipulating the continuity equation ($A_1 v_1 = A_2 v_2$).
- **Viscosity Race:** Place a drop of water, a drop of cooking oil, and a drop of honey at the top of a tilted baking tray. Time how long it takes each to reach the bottom. The difference in speed is a direct macroscopic observation of dynamic viscosity.
- **Composite Construction:** Try to break a piece of dry spaghetti. It snaps easily (brittle fracture). Now, take several pieces of spaghetti and wrap them tightly in sticky tape. Try to break the bundle. The tape acts as a ductile matrix, preventing the brittle fracture of individual strands from propagating through the whole structure.

## 6. Model-building prompts

- Construct a causal loop diagram showing the relationship between fluid velocity, pressure, and pipe cross-sectional area based on Bernoulli's principle and the continuity equation.
- Draw a stress-strain curve for a ductile metal (like steel) and a brittle material (like glass). Label the elastic region, the yield point, the plastic region, and the fracture point.

## 7. Self-explanation questions

- Explain in your own words why a fluid accelerating through a narrow pipe must experience a drop in pressure, assuming no energy is added by a pump.
- Why does a crack in a material cause it to fail at a much lower overall stress than the material's theoretical strength?
- What is the physical difference between a material that is "stiff" (high Young's modulus) and a material that is "strong" (high yield strength)?

## 8. Transfer questions

- How do the principles of fluid viscosity apply to the design of motor oil for car engines operating at different temperatures?
- If bone is a composite material made of flexible collagen fibres and brittle calcium phosphate crystals, how does this structure prevent your legs from shattering when you jump?
- How does the concept of stress concentration at a crack tip explain why it is easier to tear a piece of paper if you make a small cut in the edge first?

## 9. Suggested learning paths

- **To understand the mathematics of flow:** Study vector calculus and the derivation of the Navier-Stokes equations.
- **To understand material failure:** Investigate the microscopic mechanisms of dislocations in crystal lattices and how alloying elements impede their movement.
- **To explore advanced materials:** Research the manufacturing and failure modes of carbon fibre reinforced polymers (CFRP) used in modern aerospace.

## 10. Reasoning notes

- When applying Bernoulli's equation, always verify the assumptions: is the flow steady? Is it incompressible? Are viscous losses negligible? If the answer to any of these is no, the simple form of the equation will yield incorrect results.
- Remember that stress is not a force, but a force *distribution*. A small force applied to a microscopic area (like a pinprick) can create a massive stress, exceeding the material's yield strength.
- The distinction between elastic and plastic deformation is fundamental. Elasticity is about atomic bonds stretching; plasticity is about atomic planes sliding past one another.
