---
title: "Exploring Motion and Forces"
slug: 09-motion-forces-explore
module: "Module 09"
domain: science
status: reviewed
prerequisites: [03-mathematical-models]
connections: [11-waves-signals, 12-fluids-materials, 16-earth-planetary]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# 1. Observation prompts

Look around your environment and identify instances of motion and the forces causing them. Observe a door swinging on its hinges; where is the force applied, and how does the distance from the hinge affect the ease of opening it? Watch a vehicle accelerate from a stoplight; how does the vehicle's mass seem to relate to its acceleration compared to a bicycle? Use a slow-motion video of a soft foam ball released over a clear area. Does its centre follow a straight line or a curve, and what forces act after release?

# 2. Prediction questions

If you drop a heavy book and a single sheet of paper simultaneously from the same height, which will hit the ground first, and why? If you crumple the paper into a tight ball and repeat the experiment, how will the outcome change? Imagine you are standing on a frictionless surface (like perfectly smooth ice) and you throw a heavy backpack forward; what will happen to your own motion? If a spinning figure skater pulls their arms in tight to their body, how will their rotational speed change?

# 3. Worked reasoning examples

**Example: Stopping a low-speed cart**

Consider a laboratory cart of mass $m = 1.5 \, \text{kg}$ moving at $v = 2.0 \, \text{m/s}$ that is brought to rest by a padded bumper over $t = 0.20 \, \text{s}$. We want the average horizontal force on the cart.

First, we calculate the initial momentum of the cart:
$$ p_{\text{initial}} = m \cdot v = 1.5 \, \text{kg} \cdot 2.0 \, \text{m/s} = 3.0 \, \text{kg}\cdot\text{m/s} $$

The final momentum is zero because the cart stops. The change in momentum ($\Delta p$) is therefore $-3.0 \, \text{kg}\cdot\text{m/s}$.

Using the impulse-momentum theorem, the impulse $J$ equals the change in momentum, and impulse is also the average force $F_{\text{avg}}$ multiplied by the time duration $t$:
$$ J = F_{\text{avg}} \cdot t = \Delta p $$
$$ F_{\text{avg}} = \frac{\Delta p}{t} = \frac{-3.0 \, \text{kg}\cdot\text{m/s}}{0.20 \, \text{s}} = -15 \, \text{N} $$

The negative sign indicates the force is directed opposite to the cart's initial motion. The result illustrates that increasing stopping time reduces the magnitude of average force for the same momentum change. Real forces vary during contact, so a force sensor would reveal a time-dependent profile.

# 4. Thought experiments

**Orbital free-fall simulation**

Imagine a small test object already above the atmosphere in a simulation. Give it a modest horizontal velocity: gravity curves its path downward until it intersects Earth. Increase the horizontal velocity and the intersection occurs farther away. At the appropriate speed, the object continuously falls toward Earth while the surface curves away beneath it, producing an orbit. How do initial altitude, horizontal speed, and Earth's curvature determine whether the trajectory intersects the surface, forms an ellipse, or escapes?

# 5. Household and browser-based explorations

**Household Exploration: Center of Mass and Stability**

Take a standard broom. Try to balance it horizontally on one finger. You will find that the balance point (the center of mass) is not in the middle of the handle, but much closer to the heavy bristle end. Without cutting anything, place removable tape markers at the balance point and at estimated centres of mass for the handle and bristle regions. Why can unequal masses balance when their lever arms differ? 

Balance does not imply equal masses. The heavier bristle region can balance the longer, lighter handle because torque ($\tau = r \times F$) depends on both the force (weight) and the distance from the pivot ($r$). The lighter handle has its center of mass further from the pivot, compensating for its lower weight.

**Browser-based Exploration: PhET Interactive Simulations**

Visit the PhET Interactive Simulations website (provided by the University of Colorado Boulder) and search for "Gravity and Orbits." Use the simulation to explore how changing the mass of the Sun or the Earth, or changing the distance between them, affects the Earth's orbit. Try to create a stable elliptical orbit, and observe how the Earth's velocity changes as it gets closer to or further from the Sun (Kepler's Second Law).

# 6. Model-building prompts

Construct a simple mathematical model of a falling object. Start with Newton's Second Law ($F = ma$). Assume the only force acting on the object is gravity ($F_g = mg$). Show that the acceleration is constant and independent of mass. 

Next, refine your model by adding a simple approximation for air resistance, assuming the drag force is proportional to velocity ($F_d = -kv$, where $k$ is a constant). Set up the differential equation $mg - kv = m \frac{dv}{dt}$. What happens to the acceleration as the velocity increases? Can you determine the "terminal velocity" where acceleration becomes zero?

# 7. Self-explanation questions

Explain in your own words why an astronaut in the International Space Station experiences weightlessness, even though the gravitational force from Earth at that altitude is still about 90% as strong as it is on the surface. 

Describe the difference between mass and weight. If you travel to the Moon, which of these quantities changes, and why?

Why is it easier to loosen a tight bolt with a long wrench rather than a short one? Explain this using the concept of torque.

# 8. Transfer questions

The principles of momentum conservation apply to rocket propulsion in the vacuum of space. How do these same principles apply to a squid propelling itself through water? What is the "propellant" in the squid's case?

A moving bicycle is stabilised mainly through steering geometry, tyre contact forces, and rider control, with wheel angular momentum contributing. How does this differ from an actively controlled spacecraft gyroscope?

# 9. Suggested learning paths

To deepen your understanding of classical mechanics, consider the following progression. First, ensure a solid grasp of vector algebra and basic calculus, as these are the languages of physics. Next, study kinematics in one and two dimensions to master the description of motion. Then, delve into Newton's Laws of Motion and practice applying them to various systems using free-body diagrams. 

Once comfortable with forces, study the conservation laws: work and energy, followed by impulse and momentum. Finally, extend these concepts to rotational motion, studying torque, moment of inertia, and angular momentum. For a comprehensive and rigorous treatment, the *Feynman Lectures on Physics* (Volume 1) or MIT's OpenCourseWare 8.01 (Classical Mechanics) are excellent resources.

# 10. Reasoning notes

When analyzing mechanical systems, always begin by defining your system boundaries and identifying all external forces acting on the system. Drawing a clear, accurate free-body diagram is the most crucial step in solving dynamics problems. 

Remember that Newton's Third Law pairs (action-reaction forces) always act on *different* objects; they never cancel each other out on the same free-body diagram. When dealing with rotational motion, carefully define your axis of rotation, as the moment of inertia and torque depend entirely on this choice. Finally, always check the units of your final answer to ensure they are consistent with the physical quantity you are calculating.

## Phase 7 review boundaries and validity limits

- Newton's second law is fundamentally ΣF_ext = dp/dt. The familiar ma form requires constant mass in an inertial frame.
- Mass is an invariant measure in modern relativity; relativistic momentum and energy, not “relativistic mass,” replace the low-speed formulas as speed approaches c.
- Moment of inertia is generally a tensor. Treating it as a scalar is valid only for rotation about a specified principal or fixed axis.
- Third-law force pairs act on different bodies. Momentum conservation follows from the external-force balance for the chosen system; internal-force cancellation must be justified for the model used.
- Newtonian gravity is an accurate weak-field, low-speed approximation. General relativity is required for strong fields, high precision, or relativistic motion.

# 11. Sources



1. OpenStax. *University Physics Volume 1*. https://openstax.org/details/books/university-physics-volume-1
2. MIT OpenCourseWare. *8.01SC Classical Mechanics*. https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/
3. NASA. *Basics of Space Flight: Gravity and Mechanics*. https://science.nasa.gov/learn/basics-of-space-flight/chapter3-4/
4. Feynman, R. P., Leighton, R. B., and Sands, M. *The Feynman Lectures on Physics, Volume I*. https://www.feynmanlectures.caltech.edu/
