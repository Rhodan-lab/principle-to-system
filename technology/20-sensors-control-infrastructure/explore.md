---
title: "Exploring Control and Infrastructure"
slug: 20-sensors-control-infrastructure-explore
module: "Module 20"
domain: technology
status: reviewed
prerequisites: [10-electricity-magnetism, 11-waves-signals, 18-semiconductors-electronics, 19-software-ai]
connections: []
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Exploring Control and Infrastructure

## 1. Observation prompts

- Identify sensors only from normal public or household use. Do not open alarms, appliances, panels, meters, substations, cabinets, or restricted areas. Record measured variable, likely transduction principle, sampling, and possible failure modes.
- Observe power infrastructure only from a public safe distance. Never touch, climb, approach damaged equipment, enter fenced areas, or infer voltage solely from appearance. Use utility diagrams to distinguish transmission, distribution, substations, and transformers.
- Map an appliance's likely measure–estimate–decide–act–verify loop from manuals or animations rather than interfering with its operation.

## 2. Prediction questions

- In a simulated temperature loop, increase derivative gain while varying sensor noise, derivative filtering, door-disturbance size, sampling, and actuator saturation. Which outcomes are actually determined by $K_d$ alone?
- As rooftop solar increases, distinguish customer demand from grid net load. Predict midday and evening effects only after weather, orientation, storage, tariffs, feeder constraints, and geographic diversity are specified.
- For a simulated robotic arm carrying a payload, identify inertia, gravity, friction, compliance, resonance, actuator limits, structural loads, trajectory, uncertainty, and safety constraints before predicting overshoot.

## 3. Worked reasoning examples

**Scenario:** Conceptual cruise-control tuning in a simulation

1. Proportional action responds to current speed error. A constant hill or drag can leave offset depending on plant and gain.
2. Integral action accumulates error and can remove offset only if the loop remains stable and the actuator has authority. Saturation requires anti-windup.
3. Derivative action responds to rate and can add damping, but it amplifies measurement noise and does not literally anticipate a future hill.
4. Feedforward from estimated grade or requested acceleration can complement feedback.
5. Real vehicle control includes actuator limits, braking, traction, safety supervision, driver authority, and validated operating envelopes. This is a simulation exercise, not a driving or vehicle-modification instruction.

## 4. Thought experiments

- **Ideal rigid massless arm:** Removing inertia and flexibility also removes important energy storage and dynamics, potentially making the model singular or physically meaningless. Which controller questions disappear, and which limits—actuator, sensing, timing, geometry, and contact—remain?
- **Islanded power system:** Given a wind profile, battery power and energy limits, inverter controls, reserve policy, load priorities, and protection settings, trace several possible responses to lost wind. Why can no controller promise “no flicker” without adequate stored energy, power capacity, network support, and validated transitions?

## 5. Household and browser-based explorations

- **Low-energy feedback simulation:** Use a browser simulation of an inverted pendulum, temperature loop, or motor. Change delay, noise, sampling, gain, saturation, and disturbance; do not balance long objects near your face or other people.
- **Grid model:** Use an institutional educational simulator or public historical dataset. Separate energy adequacy, frequency response, network congestion, reserves, emissions, cost, and reliability; a 24-hour energy balance is not a full stability study.
- **Sensor calibration model:** Given a supplied table of reference and sensor readings, fit offset and scale, inspect residuals, and propagate uncertainty. Add a drift or stuck-sensor fault and design a diagnostic.

## 6. Model-building prompts

- Derive a mass–spring–damper state-space model after defining state order, input force, measured output, sign convention, and units. Check matrix dimensions, eigenvalues, controllability, and how parameter uncertainty changes predictions.
- Draw a drone-altitude architecture including reference, estimator, controller, motor drive, vehicle dynamics, altimeter, delay, disturbance, saturation, protection, operator authority, and emergency mode. Distinguish the error signal from the full estimated state.
- Build a grid-service diagram that separates energy adequacy, active-power balance, voltage, frequency, thermal limits, protection, communication, markets, operators, and restoration.

## 7. Self-explanation questions

- Explain the difference between an open-loop system and a closed-loop system using examples not mentioned in this module.
- Why is it difficult to control a system that has a long time delay between the actuator taking action and the sensor measuring the result?
- How does a smart inverter differ from a traditional generator in how it interacts with the power grid?

## 8. Transfer questions

- The principles of feedback control are used in engineering, but they also exist in biology. How does the human body use feedback loops to regulate internal temperature or blood sugar levels?
- How could the concept of "resilience" in electrical infrastructure be applied to other complex networks, such as global supply chains or the internet?

## 9. Suggested learning paths

- **To dive deeper into control theory:** Study classical control (Laplace transforms, root locus, Bode plots) before moving heavily into modern state-space control and optimal control (LQR).
- **To understand robotics:** Combine studies in kinematics (the geometry of motion), dynamics (forces and torques), and computer vision (advanced sensing).
- **To explore energy systems:** Study power electronics (how to efficiently convert DC to AC and change voltage levels) and power systems engineering (load flow analysis and fault protection).

## 10. Reasoning notes

Define the plant, controller, estimator, actuator, sensor, communication path, operator, protection system, environment, and service boundary. Track delay, sampling, saturation, uncertainty, common-cause failure, cybersecurity, maintenance, and recovery. A technically stable loop can still be unsafe, insecure, unfair, unaffordable, or difficult to operate. Conversely, resilience is not one component; it is the demonstrated ability of the whole socio-technical system to continue or recover an essential service.

## Phase 9 review boundaries and validity limits

- Closed-loop performance depends on sensing, estimation, delay, sampling, quantisation, communication, actuator saturation, disturbances, uncertainty, and model mismatch.
- Stability and safety are properties of a specified operating region and architecture; a controller that works in one regime may fail in another.
- Grid operation couples physics, protection, markets, communications, cybersecurity, regulation, operators, and restoration procedures.
- Cyber-physical and infrastructure designs require defence in depth, fail-safe or fail-operational analysis, human authority, testing, maintenance, and lifecycle governance.

## 11. Sources

1. WPILib Contributors. *Introduction to State-Space Control*. https://docs.wpilib.org/en/stable/docs/software/advanced-controls/state-space/state-space-intro.html
2. Peng, F. Z., et al. *Envisioning the Future Renewable and Resilient Energy Grids*. https://ieeexplore.ieee.org/abstract/document/10360247/
3. National Institute of Standards and Technology. *Framework for Cyber-Physical Systems: Volume 1, Overview*. https://www.nist.gov/publications/framework-cyber-physical-systems-volume-1-overview
4. National Institute of Standards and Technology. *SP 800-82 Rev. 2: Guide to Industrial Control Systems Security*. https://csrc.nist.gov/pubs/sp/800/82/r2/final
5. United States Department of Energy. *Grid Modernization Initiative*. https://www.energy.gov/gmi/grid-modernization-initiative
6. Filip, F. G., and Leiviskä, K. *Infrastructure and Complex Systems Automation*. https://link.springer.com/chapter/10.1007/978-3-030-96729-1_27
