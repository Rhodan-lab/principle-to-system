---
title: "Motion, Forces, Momentum, Rotation, and Gravitation"
slug: 09-motion-forces
module: "Module 09"
domain: science
status: reviewed
prerequisites: [03-mathematical-models]
connections: [11-waves-signals, 12-fluids-materials, 16-earth-planetary]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Motion, Forces, Momentum, Rotation, and Gravitation

## 1. The central questions

How do objects move, and what causes their motion to change? Why do some objects remain at rest while others accelerate, rotate, or orbit? How can we predict the future trajectory of a system given its current state and the interactions it experiences? Classical mechanics seeks to answer these questions by establishing a causal framework linking forces to changes in motion, constrained by fundamental conservation laws.

## 2. Observable phenomena

The principles of classical mechanics are evident across vastly different scales:
- **Terrestrial motion:** A thrown ball follows a parabolic path; a sliding block eventually stops due to friction; a pendulum swings with a regular period.
- **Collisions and impacts:** Billiard balls scatter upon impact; vehicles crumple in a crash, transferring momentum and dissipating kinetic energy.
- **Rotational dynamics:** A spinning ice skater rotates faster when pulling their arms inward; a gyroscope resists changes to its axis of rotation; a wrench amplifies the turning effect of a force.
- **Gravitational phenomena:** The Moon orbits the Earth; tides rise and fall; apples fall from trees; planets trace elliptical paths around the Sun.

## 3. Essential concepts

- **Kinematics:** The description of motion (position, velocity, acceleration) without regard to its causes.
- **Dynamics:** The study of the causes of motion, specifically how forces and torques affect the state of a system.
- **Inertia:** The inherent property of matter that resists changes to its state of motion, quantified by mass.
- **Force:** A vector quantity representing an interaction that, when unopposed, changes the motion of an object.
- **Momentum:** The quantity of motion an object possesses, defined as the product of its mass and velocity.
- **Conservation Laws:** Fundamental principles stating that certain isolated system properties (total momentum, angular momentum, total energy) remain constant over time.
- **Reference Frames:** Coordinate systems from which motion is observed and measured. Inertial frames are those in which Newton's first law holds true.

## 4. Mechanisms and causal chains

The causal structure of classical mechanics is deterministic and local (excluding the instantaneous action-at-a-distance model of Newtonian gravity, later refined by general relativity).
- **Force causes acceleration:** A net external force applied to a mass induces an acceleration inversely proportional to that mass (Newton's Second Law). This acceleration changes the object's velocity over time, which in turn changes its position.
- **Interactions are mutual:** When object A exerts a force on object B, object B simultaneously exerts an equal and opposite force on object A (Newton's Third Law). This mechanism ensures the conservation of momentum in isolated systems.
- **Torque causes angular acceleration:** An off-center force produces a torque, which induces an angular acceleration inversely proportional to the object's moment of inertia, changing its rotational state.
- **Gravitational attraction:** Mass curves spacetime (or in the classical view, generates a gravitational field), which exerts an attractive force on other masses, causing them to accelerate toward one another or enter stable orbits.

## 5. Important quantities

| Quantity | Symbol | SI Unit | Vector/Scalar | Description |
| :--- | :---: | :---: | :---: | :--- |
| Position | $\vec{r}$ | $\text{m}$ | Vector | Location relative to an origin. |
| Velocity | $\vec{v}$ | $\text{m/s}$ | Vector | Rate of change of position. |
| Acceleration | $\vec{a}$ | $\text{m/s}^2$ | Vector | Rate of change of velocity. |
| Mass | $m$ | $\text{kg}$ | Scalar | Measure of inertia. |
| Force | $\vec{F}$ | $\text{N}$ ($\text{kg}\cdot\text{m/s}^2$) | Vector | Interaction causing acceleration. |
| Momentum | $\vec{p}$ | $\text{kg}\cdot\text{m/s}$ | Vector | Product of mass and velocity. |
| Impulse | $\vec{J}$ | $\text{N}\cdot\text{s}$ | Vector | Change in momentum. |
| Torque | $\vec{\tau}$ | $\text{N}\cdot\text{m}$ | Vector | Rotational equivalent of force. |
| Angular Momentum | $\vec{L}$ | $\text{kg}\cdot\text{m}^2/\text{s}$ | Vector | Rotational equivalent of momentum. |
| Moment of Inertia | $I$ or $\mathbf{I}$ | $\text{kg}\cdot\text{m}^2$ | Scalar about a fixed axis; tensor generally | Relates angular momentum or torque to rotational motion for a defined geometry and axis. |

## 6. Mathematical models and equations

**Kinematics (Constant Acceleration):**
For an object moving with constant acceleration $\vec{a}$, its velocity $\vec{v}$ and position $\vec{r}$ at time $t$ are:
$$ \vec{v}(t) = \vec{v}_0 + \vec{a}t $$
$$ \vec{r}(t) = \vec{r}_0 + \vec{v}_0 t + \frac{1}{2}\vec{a}t^2 $$

**Newton's Laws of Motion:**
1. **First Law:** $\sum \vec{F} = 0 \implies \frac{d\vec{v}}{dt} = 0$
2. **Second Law:** $\sum \vec{F} = \frac{d\vec{p}}{dt}$. For constant mass, this simplifies to $\sum \vec{F} = m\vec{a}$.
3. **Third Law:** $\vec{F}_{AB} = -\vec{F}_{BA}$

**Momentum and Impulse:**
Momentum is defined as $\vec{p} = m\vec{v}$. The impulse-momentum theorem states that the impulse $\vec{J}$ (the integral of force over time) equals the change in momentum:
$$ \vec{J} = \int_{t_1}^{t_2} \vec{F} dt = \Delta\vec{p} $$
In an isolated system ($\sum \vec{F}_{\text{ext}} = 0$), total momentum is conserved: $\sum \vec{p}_i = \text{constant}$.

**Rotational Dynamics:**
The rotational analog of Newton's second law relates net torque $\vec{\tau}$ to angular momentum $\vec{L}$:
$$ \sum \vec{\tau} = \frac{d\vec{L}}{dt} $$
For a rigid body rotating about a fixed axis of symmetry, $\vec{L} = I\vec{\omega}$ and $\sum \vec{\tau} = I\vec{\alpha}$, where $\vec{\omega}$ is angular velocity and $\vec{\alpha}$ is angular acceleration.

**Newton's Law of Universal Gravitation:**
The attractive force between two point masses $m_1$ and $m_2$ separated by a distance $r$ is:
$$ \vec{F}_g = -G \frac{m_1 m_2}{r^2} \hat{r} $$
where $G$ is the gravitational constant and $\hat{r}$ is the unit vector pointing from one mass to the other.

## 7. Definitions of symbols and units

- $\vec{r}, \vec{r}_0$: Final and initial position vectors ($\text{m}$).
- $\vec{v}, \vec{v}_0$: Final and initial velocity vectors ($\text{m/s}$).
- $\vec{a}$: Acceleration vector ($\text{m/s}^2$).
- $t$: Time ($\text{s}$).
- $m, m_1, m_2$: Mass ($\text{kg}$).
- $\vec{F}, \vec{F}_{AB}, \vec{F}_{BA}, \vec{F}_g$: Force vectors ($\text{N}$).
- $\vec{p}$: Linear momentum vector ($\text{kg}\cdot\text{m/s}$).
- $\vec{J}$: Impulse vector ($\text{N}\cdot\text{s}$).
- $\vec{\tau}$: Torque vector ($\text{N}\cdot\text{m}$).
- $\vec{L}$: Angular momentum vector ($\text{kg}\cdot\text{m}^2/\text{s}$).
- $I$: Moment of inertia ($\text{kg}\cdot\text{m}^2$).
- $\vec{\omega}$: Angular velocity vector ($\text{rad/s}$).
- $\vec{\alpha}$: Angular acceleration vector ($\text{rad/s}^2$).
- $G$: Universal gravitational constant ($6.674 \times 10^{-11} \, \text{N}\cdot\text{m}^2/\text{kg}^2$).
- $r$: Distance between centers of mass ($\text{m}$).
- $\hat{r}$: Unit vector indicating direction.

## 8. Assumptions and approximations

- **Point Mass Approximation:** Extended objects are often treated as point masses located at their center of mass, ignoring internal structure and rotation.
- **Rigid Body Assumption:** In rotational dynamics, objects are assumed to not deform under stress, meaning the distance between any two points in the object remains constant.
- **Inertial Reference Frames:** Newton's laws strictly apply only in non-accelerating frames. In accelerating frames, "fictitious" forces (like the Coriolis or centrifugal force) must be introduced.
- **Non-Relativistic Speeds:** Classical mechanics assumes velocities are much less than the speed of light ($v \ll c$). At relativistic speeds, invariant mass remains the same while momentum and energy follow relativistic rather than Newtonian formulas.
- **Macroscopic Scale:** The models assume objects are large enough that quantum mechanical effects (like the uncertainty principle) are negligible.
- **Constant Gravity:** Near the Earth's surface, gravitational acceleration $g$ is often approximated as constant ($9.81 \, \text{m/s}^2$), ignoring the $1/r^2$ dependence.

## 9. Spatial and temporal scales

- **Spatial Scale:** Classical mechanics accurately describes phenomena ranging from the microscopic (e.g., dust particles, $\sim 10^{-6} \, \text{m}$) to the astronomical (e.g., planetary orbits, $\sim 10^{12} \, \text{m}$). It breaks down at the atomic scale ($\sim 10^{-10} \, \text{m}$).
- **Temporal Scale:** Applicable to events occurring over fractions of a second (e.g., a bat hitting a baseball, $\sim 10^{-3} \, \text{s}$) to billions of years (e.g., galactic rotation).

## 10. Common misconceptions

- **"Force is required to maintain motion."** (Aristotelian view). In reality, force is required to *change* motion. An object in motion will remain in motion indefinitely unless acted upon by a net external force (Newton's First Law).
- **"Heavier objects fall faster than lighter ones."** In a vacuum, all objects accelerate toward Earth at the same rate regardless of mass, because the gravitational force is proportional to mass, but acceleration is inversely proportional to mass, canceling the effect.
- **"Centrifugal force pulls objects outward in a circle."** Centrifugal force is a fictitious force perceived in a rotating reference frame. In an inertial frame, the only force is the *centripetal* force pulling the object *inward* to maintain circular motion.
- **"Astronauts in orbit are weightless because there is no gravity in space."** Gravity is very much present in low Earth orbit (only slightly weaker than at the surface). Astronauts feel weightless because they, and their spacecraft, are in continuous free-fall toward Earth.

## 11. Connections to other modules

- **03-mathematical-models:** Provides the calculus and vector algebra necessary to formulate kinematics and dynamics.
- **08-energy-thermodynamics:** Connects macroscopic mechanical energy to microscopic kinetic energy (heat) and introduces non-conservative forces like friction.
- **10-electricity-magnetism:** Introduces another fundamental force (electromagnetic) that obeys the same kinematic and dynamic frameworks but has different causal origins.
- **06-matter-quantum:** Defines the limits of classical mechanics at the atomic scale, where deterministic trajectories are replaced by probability amplitudes.

## Phase 7 review boundaries and validity limits

- Newton's second law is fundamentally ΣF_ext = dp/dt. The familiar ma form requires constant mass in an inertial frame.
- Mass is an invariant measure in modern relativity; relativistic momentum and energy, not “relativistic mass,” replace the low-speed formulas as speed approaches c.
- Moment of inertia is generally a tensor. Treating it as a scalar is valid only for rotation about a specified principal or fixed axis.
- Third-law force pairs act on different bodies. Momentum conservation follows from the external-force balance for the chosen system; internal-force cancellation must be justified for the model used.
- Newtonian gravity is an accurate weak-field, low-speed approximation. General relativity is required for strong fields, high precision, or relativistic motion.

## 12. Sources



1. OpenStax. *University Physics Volume 1*. https://openstax.org/details/books/university-physics-volume-1
2. MIT OpenCourseWare. *8.01SC Classical Mechanics*. https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/
3. NASA. *Basics of Space Flight: Gravity and Mechanics*. https://science.nasa.gov/learn/basics-of-space-flight/chapter3-4/
4. Feynman, R. P., Leighton, R. B., and Sands, M. *The Feynman Lectures on Physics, Volume I*. https://www.feynmanlectures.caltech.edu/
