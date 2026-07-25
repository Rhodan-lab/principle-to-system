---
title: "Sensors, Control, Automation, Robotics, Energy, and Infrastructure"
slug: 20-sensors-control-infrastructure
module: "Module 20"
domain: technology
status: draft
prerequisites: [10-electricity-magnetism, 11-waves-signals, 18-semiconductors-electronics, 19-software-ai]
connections: []
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Sensors, Control, Automation, Robotics, Energy, and Infrastructure

## 1. The central questions

How do physical systems perceive their environment, make decisions, and act upon those decisions to achieve desired outcomes? How can we mathematically model and control dynamic systems to ensure stability and precision? Furthermore, how do these principles scale up to manage massive, distributed networks like the electrical power grid, ensuring resilience and reliability in the face of intermittent renewable energy sources and complex demand patterns?

## 2. Observable phenomena

In daily life, these principles manifest when a thermostat maintains a room's temperature, a drone stabilizes itself against wind gusts, or a robotic arm precisely welds a car chassis. On a larger scale, we observe the continuous availability of electricity despite fluctuating demand and the variable output of solar and wind farms. We see automated manufacturing lines producing goods with minimal human intervention, and smart grids rerouting power autonomously to isolate faults and prevent blackouts.

## 3. Essential concepts

**Transduction:** The process of converting one form of energy into another. Sensors are transducers that convert physical phenomena (temperature, pressure, light) into electrical signals. Actuators are transducers that convert electrical signals into physical action (motion, heat, fluid flow).

**Feedback Loop:** A system structure where the output is measured and compared to a desired reference value (setpoint). The difference (error) is used to adjust the system's input to minimize the error. This is the foundation of closed-loop control.

**Control Theory:** The mathematical study of how to manipulate the inputs of a dynamic system to achieve a desired output. It encompasses classical methods like PID (Proportional-Integral-Derivative) control and modern methods like state-space representation.

**Automation and Robotics:** The integration of sensors, control systems, and actuators to perform tasks with minimal human intervention. Robotics specifically involves programmable machines capable of complex physical actions.

**Grid Architecture:** The structure of the electrical power system, traditionally consisting of centralized generation, high-voltage transmission, and lower-voltage distribution. Modern architectures incorporate Distributed Energy Resources (DERs) like rooftop solar and local battery storage.

**Infrastructure Resilience:** The ability of critical systems (like the power grid) to anticipate, absorb, adapt to, and rapidly recover from disruptive events, such as extreme weather or cyberattacks [1].

## 4. Mechanisms and causal chains

The fundamental causal chain in automation is the **Sense-Think-Act** cycle:
1. **Sense:** A physical phenomenon alters the state of a sensor. For example, increased temperature changes the resistance of a thermistor. This change is converted into an analog electrical voltage, which is then digitized by an Analog-to-Digital Converter (ADC).
2. **Think:** A controller (a microprocessor or computer) receives the digital signal, compares it to a desired setpoint, and calculates an error value. Using a control algorithm (like PID or state-space), it computes a corrective command.
3. **Act:** The digital command is converted back to an analog signal via a Digital-to-Analog Converter (DAC) and amplified to drive an actuator. A motor spins, a valve opens, or a heater turns on, altering the physical environment. The cycle then repeats, closing the feedback loop.

In energy infrastructure, the causal chain of **Grid Balancing** is critical:
1. **Generation/Demand Fluctuation:** Solar output drops due to cloud cover, or industrial demand spikes.
2. **Frequency Deviation:** The imbalance between supply and demand causes the AC grid frequency (nominally 50 Hz or 60 Hz) to deviate.
3. **Sensing and Control:** Grid sensors (Phasor Measurement Units) detect the frequency change. Automated control systems signal fast-responding generators or battery storage systems to inject or absorb power.
4. **Restoration:** The balance is restored, and the grid frequency returns to nominal.

## 5. Important quantities

| Quantity | Symbol | SI Unit | Description |
| :--- | :---: | :---: | :--- |
| Error | $e(t)$ | Varies | The difference between the desired setpoint and the measured process variable. |
| Control Output | $u(t)$ | Varies | The signal sent to the actuator to correct the error. |
| State Vector | $\mathbf{x}(t)$ | Varies | A mathematical vector representing the internal state of a dynamic system. |
| Active Power | $P$ | Watt (W) | The rate at which electrical energy is transferred by an electric circuit. |
| Reactive Power | $Q$ | Volt-Ampere Reactive (VAR) | Power that oscillates back and forth in an AC circuit due to inductive and capacitive loads. |
| Grid Frequency | $f$ | Hertz (Hz) | The rate at which alternating current reverses direction. |

## 6. Mathematical models and equations

### PID Control

The Proportional-Integral-Derivative (PID) controller is the most widely used control algorithm in industry. It calculates the control output $u(t)$ based on the current error, the accumulation of past errors, and the predicted future error [2].

$$ u(t) = K_p e(t) + K_i \int_{0}^{t} e(\tau) d\tau + K_d \frac{de(t)}{dt} $$

Where:
- $u(t)$ is the control signal applied to the system.
- $e(t)$ is the error signal ($Setpoint - Measured Value$).
- $K_p$ is the proportional gain (reacts to current error).
- $K_i$ is the integral gain (eliminates steady-state error by accumulating past errors).
- $K_d$ is the derivative gain (dampens the system by predicting future error trends).

### State-Space Representation

Modern control theory uses state-space representation to model complex, multi-input multi-output (MIMO) systems. It describes a system using a set of first-order differential equations [3].

$$ \dot{\mathbf{x}}(t) = \mathbf{A}\mathbf{x}(t) + \mathbf{B}\mathbf{u}(t) $$
$$ \mathbf{y}(t) = \mathbf{C}\mathbf{x}(t) + \mathbf{D}\mathbf{u}(t) $$

Where:
- $\mathbf{x}(t)$ is the state vector (internal variables of the system).
- $\dot{\mathbf{x}}(t)$ is the time derivative of the state vector.
- $\mathbf{u}(t)$ is the input vector (control signals).
- $\mathbf{y}(t)$ is the output vector (measured variables).
- $\mathbf{A}$ is the system matrix (describes internal dynamics).
- $\mathbf{B}$ is the input matrix (describes how inputs affect states).
- $\mathbf{C}$ is the output matrix (describes how states map to outputs).
- $\mathbf{D}$ is the feedthrough matrix (describes direct input-to-output coupling, often zero).

### AC Power

In alternating current (AC) power grids, the relationship between apparent power ($S$), active power ($P$), and reactive power ($Q$) is modeled using complex numbers.

$$ S = P + jQ $$
$$ P = V_{rms} I_{rms} \cos(\phi) $$
$$ Q = V_{rms} I_{rms} \sin(\phi) $$

Where $V_{rms}$ and $I_{rms}$ are the root-mean-square voltage and current, and $\phi$ is the phase angle between them. $\cos(\phi)$ is known as the power factor.

## 7. Definitions of symbols and units

- $t$: Time, measured in seconds (s).
- $\tau$: Variable of integration for time, measured in seconds (s).
- $K_p, K_i, K_d$: Tuning parameters for a PID controller. Units depend on the specific process being controlled.
- $j$: The imaginary unit, where $j^2 = -1$.
- $V_{rms}$: Root-mean-square voltage, measured in Volts (V).
- $I_{rms}$: Root-mean-square current, measured in Amperes (A).

## 8. Assumptions and approximations

- **Linearity:** State-space models ($\dot{\mathbf{x}} = \mathbf{A}\mathbf{x} + \mathbf{B}\mathbf{u}$) assume the system is linear and time-invariant (LTI). Real systems are often non-linear, requiring linearization around an operating point or advanced non-linear control techniques.
- **Ideal Sensors and Actuators:** Basic control models often assume sensors have no noise or delay, and actuators have infinite bandwidth and no saturation limits. In reality, signal conditioning and anti-windup mechanisms are necessary.
- **Lumped Parameters:** Grid models often treat transmission lines as lumped parameters (resistors, inductors, capacitors) rather than distributed systems, which is a valid approximation for lines shorter than the wavelength of the AC signal.

## 9. Spatial and temporal scales

- **Temporal:** Control loops in robotics and power electronics operate at microsecond to millisecond scales. Mechanical systems (like heating a room) operate on scales of minutes to hours. Grid frequency control operates in milliseconds to seconds, while energy market dispatch operates in hours to days.
- **Spatial:** Sensors operate at the microscale (MEMS accelerometers). Robotics operate at the human scale (meters). Power grids span continental scales (thousands of kilometers).

## 10. Common misconceptions

- **"Derivative control is always necessary."** In many industrial processes (like temperature control), the derivative term ($K_d$) is set to zero because it amplifies high-frequency sensor noise, causing erratic actuator behavior. PI control is often sufficient.
- **"Renewable energy makes the grid inherently unstable."** While wind and solar are intermittent and lack the physical inertia of massive spinning turbines, modern power electronics (smart inverters) and grid-scale battery storage can provide synthetic inertia and rapid frequency response, potentially making the grid *more* resilient if managed correctly [4].
- **"Robots are just mechanical arms."** A robot is defined by its integration of sensing, computation, and actuation. A self-driving car or an autonomous drone is as much a robot as a factory arm.

## 11. Connections to other modules

- **10-electricity-magnetism:** Provides the foundation for how sensors (like Hall effect sensors) and actuators (like electric motors) function.
- **11-waves-signals:** Essential for understanding signal conditioning, filtering noise from sensor data, and AC power transmission.
- **18-semiconductors-electronics:** Explains the microprocessors that execute control algorithms and the power electronics that drive actuators and interface renewable energy with the grid.
- **19-software-ai:** Modern control systems increasingly use machine learning for system identification, predictive maintenance, and complex decision-making in robotics.

## 12. Sources

[1] Awad, H., & Bayoumi, E. H. E. (2026). Resilient Grid Architectures for High Renewable Penetration: Electrical Engineering Strategies for 2030 and Beyond. *Technologies*, 14(2), 112. https://www.mdpi.com/2227-7080/14/2/112
[2] WPILib Contributors. (2025). Introduction to State-Space Control. *FIRST Robotics Competition Documentation*. https://docs.wpilib.org/en/stable/docs/software/advanced-controls/state-space/state-space-intro.html
[3] Filip, F. G., & Leiviskä, K. (2023). Infrastructure and complex systems automation. In *Springer Handbook of Automation* (pp. 555-575). Springer.
[4] Peng, F. Z., Liu, C. C., Li, Y., Jain, A. K., et al. (2023). Envisioning the future renewable and resilient energy grids—A power grid revolution enabled by renewables, energy storage, and energy electronics. *IEEE Journal of Emerging and Selected Topics in Power Electronics*. https://ieeexplore.ieee.org/abstract/document/10360247/
