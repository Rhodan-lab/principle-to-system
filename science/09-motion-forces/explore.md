---
title: "Exploring Motion and Forces"
slug: 09-motion-forces-explore
module: "Module 09"
domain: science
status: draft
prerequisites: [03-mathematical-models]
connections: [03-mathematical-models, 11-waves-signals, 12-fluids-materials, 16-earth-planetary]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# 1. Observation prompts

Look around your environment and identify instances of motion and the forces causing them. Observe a door swinging on its hinges; where is the force applied, and how does the distance from the hinge affect the ease of opening it? Watch a vehicle accelerate from a stoplight; how does the vehicle's mass seem to relate to its acceleration compared to a bicycle? Notice the trajectory of a tossed object, such as a set of keys; does it follow a straight line or a curve, and what forces are acting on it while it is in the air?

# 2. Prediction questions

If you drop a heavy book and a single sheet of paper simultaneously from the same height, which will hit the ground first, and why? If you crumple the paper into a tight ball and repeat the experiment, how will the outcome change? Imagine you are standing on a frictionless surface (like perfectly smooth ice) and you throw a heavy backpack forward; what will happen to your own motion? If a spinning figure skater pulls their arms in tight to their body, how will their rotational speed change?

# 3. Worked reasoning examples

**Example: The Physics of a Car Crash**

Consider a car of mass $m = 1500 \, \text{kg}$ traveling at a velocity $v = 20 \, \text{m/s}$ (about $45 \, \text{mph}$) that collides with a rigid wall and comes to a complete stop in $t = 0.1 \, \text{s}$. We want to find the average force exerted on the car during the impact.

First, we calculate the initial momentum of the car:
$$ p_{\text{initial}} = m \cdot v = 1500 \, \text{kg} \cdot 20 \, \text{m/s} = 30,000 \, \text{kg}\cdot\text{m/s} $$

The final momentum is zero because the car stops. The change in momentum ($\Delta p$) is therefore $-30,000 \, \text{kg}\cdot\text{m/s}$.

Using the impulse-momentum theorem, the impulse $J$ equals the change in momentum, and impulse is also the average force $F_{\text{avg}}$ multiplied by the time duration $t$:
$$ J = F_{\text{avg}} \cdot t = \Delta p $$
$$ F_{\text{avg}} = \frac{\Delta p}{t} = \frac{-30,000 \, \text{kg}\cdot\text{m/s}}{0.1 \, \text{s}} = -300,000 \, \text{N} $$

The negative sign indicates the force is directed opposite to the car's initial motion. This force is equivalent to the weight of approximately 30 small cars, illustrating why high-speed collisions are so destructive and why crumple zones (which increase the collision time $t$, thereby decreasing $F_{\text{avg}}$) are critical for safety.

# 4. Thought experiments

**Newton's Cannonball**

Imagine a very tall mountain on Earth, reaching above the atmosphere so there is no air resistance. Place a powerful cannon at the peak, aimed perfectly horizontally. If you fire a cannonball at a low speed, it will follow a parabolic path and hit the ground. If you fire it faster, it will travel further before hitting the ground, because the Earth curves away beneath it. 

Now, imagine firing the cannonball at a specific, very high speed. The ball falls toward the Earth due to gravity, but the Earth's surface curves away at the exact same rate that the ball falls. The cannonball is now in continuous free-fall, never hitting the ground. It has achieved orbit. This thought experiment, originally proposed by Isaac Newton, elegantly unifies the physics of falling apples with the orbits of planets.

# 5. Household and browser-based explorations

**Household Exploration: Center of Mass and Stability**

Take a standard broom. Try to balance it horizontally on one finger. You will find that the balance point (the center of mass) is not in the middle of the handle, but much closer to the heavy bristle end. Now, cut the broom exactly at that balance point (conceptually, or use a prop you don't mind breaking). If you weigh the two pieces, will they weigh the same? 

Many people intuitively guess they will weigh the same because they balanced. However, the shorter piece with the bristles is much heavier. It balances the longer, lighter handle because torque ($\tau = r \times F$) depends on both the force (weight) and the distance from the pivot ($r$). The lighter handle has its center of mass further from the pivot, compensating for its lower weight.

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

Engineers use gyroscopes to stabilize spacecraft. How does a person riding a bicycle utilize similar principles of rotational dynamics to stay upright?

# 9. Suggested learning paths

To deepen your understanding of classical mechanics, consider the following progression. First, ensure a solid grasp of vector algebra and basic calculus, as these are the languages of physics. Next, study kinematics in one and two dimensions to master the description of motion. Then, delve into Newton's Laws of Motion and practice applying them to various systems using free-body diagrams. 

Once comfortable with forces, study the conservation laws: work and energy, followed by impulse and momentum. Finally, extend these concepts to rotational motion, studying torque, moment of inertia, and angular momentum. For a comprehensive and rigorous treatment, the *Feynman Lectures on Physics* (Volume 1) or MIT's OpenCourseWare 8.01 (Classical Mechanics) are excellent resources.

# 10. Reasoning notes

When analyzing mechanical systems, always begin by defining your system boundaries and identifying all external forces acting on the system. Drawing a clear, accurate free-body diagram is the most crucial step in solving dynamics problems. 

Remember that Newton's Third Law pairs (action-reaction forces) always act on *different* objects; they never cancel each other out on the same free-body diagram. When dealing with rotational motion, carefully define your axis of rotation, as the moment of inertia and torque depend entirely on this choice. Finally, always check the units of your final answer to ensure they are consistent with the physical quantity you are calculating.

# 11. Sources

- [1] OpenStax. (2016). *University Physics Volume 1*. OpenStax. https://openstax.org/details/books/university-physics-volume-1
- [2] MIT OpenCourseWare. (2016). *8.01SC Classical Mechanics*. Massachusetts Institute of Technology. https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/
- [3] NASA. (2025). *Basics of Space Flight: Chapter 3: Gravity & Mechanics*. https://science.nasa.gov/learn/basics-of-space-flight/chapter3-4/
- [4] Feynman, R. P., Leighton, R. B., & Sands, M. (1963). *The Feynman Lectures on Physics, Vol. I: Mainly Mechanics, Radiation, and Heat*. Addison-Wesley. https://www.feynmanlectures.caltech.edu/
