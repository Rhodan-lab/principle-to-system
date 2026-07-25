---
title: "Sensors, Control, Automation, Robotics, Energy, and Infrastructure"
slug: 20-sensors-control-infrastructure
module: "Module 20"
domain: technology
status: reviewed
prerequisites: [10-electricity-magnetism, 11-waves-signals, 18-semiconductors-electronics, 19-software-ai]
connections: []
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Sensors, Control, Automation, Robotics, Energy, and Infrastructure

## 1. The central questions

How do engineered systems measure physical variables, estimate state, compute constrained actions, and affect their environment to meet stated objectives? How can we mathematically model and control dynamic systems to ensure stability and precision? Furthermore, how do these principles scale up to manage massive, distributed networks like the electrical power grid, ensuring resilience and reliability in the face of intermittent renewable energy sources and complex demand patterns?

## 2. Observable phenomena

In daily life, these principles manifest when a thermostat maintains a room's temperature, a drone stabilizes itself against wind gusts, or a robotic arm precisely welds a car chassis. On a larger scale, we observe the continuous availability of electricity despite fluctuating demand and the variable output of solar and wind farms. We see automated manufacturing lines producing goods with minimal human intervention, and smart grids rerouting power autonomously to isolate faults and prevent blackouts.

## 3. Essential concepts

**Measurement and transduction:** Sensors map physical variables to signals through mechanisms such as resistance, capacitance, charge, frequency, optical intensity, or digital state. This is not always a direct conversion of one energy form into another.

**Estimation:** Measurements are incomplete and noisy. Filters and observers combine data and models to estimate hidden state, bias, disturbance, and uncertainty.

**Feedback and feedforward:** Controllers use measurements, estimates, references, constraints, and forecasts to shape behavior. Objectives can include tracking, regulation, disturbance rejection, safety, efficiency, and constraint satisfaction—not merely minimising instantaneous error.

**Automation and robotics:** Physical autonomy integrates sensing, estimation, planning, control, actuation, communication, safety systems, operators, and maintenance.

**Infrastructure resilience:** Resilience concerns anticipation, absorption, adaptation, recovery, and learning across technical, human, organisational, and supply-chain layers. Reliability, resilience, safety, and security are related but distinct.

## 4. Mechanisms and causal chains

A more complete loop is **measure–condition–sample–estimate–decide–act–verify**. Sensors have calibration, bandwidth, noise, drift, and failure modes. Controllers operate on delayed and quantised data. Actuators have dynamics, dead zones, saturation, rate limits, and energy constraints. Independent protection, alarms, operators, and emergency systems may override normal control.

In an AC grid, active-power imbalance interacts with stored kinetic or electronic energy, frequency-sensitive demand, controls, network constraints, and protection. Frequency is an important indicator but not a complete state estimate. Primary response, inverter controls, storage, demand response, dispatch, reserves, and restoration act on different timescales. Protection must isolate faults without causing unnecessary cascading trips.

## 5. Important quantities

| Quantity | Unit | Boundary |
| :--- | :--- | :--- |
| Measurement error and uncertainty | sensor-specific | Separate bias, noise, resolution, calibration, and model uncertainty. |
| Sampling period and delay | s | Include computation, communication, actuator, and transport delay. |
| State estimate and covariance | mixed units | Defined by the state model and estimator. |
| Control input and saturation | actuator-specific | State amplitude and rate limits. |
| Stability margins | dB, degrees, or model-specific | Valid for a specified linearisation and loop. |
| Active power | W | Average real energy-transfer rate under stated waveform conditions. |
| Reactive power | var | Defined for AC models; interpretation depends on waveform and convention. |
| Frequency and rate of change | Hz, Hz/s | Local measurements influenced by dynamics and estimation. |
| Reliability and resilience metrics | event- and service-specific | Require service boundary, duration, severity, and consequence. |

## 6. Mathematical models and equations

An ideal continuous PID law is
$$u(t)=K_pe(t)+K_i\int_0^t e(\tau)d\tau+K_d\frac{de(t)}{dt}.$$
Derivative action responds to rate; it does not literally predict the future. Real implementations filter derivatives, discretise time, limit outputs, prevent integral windup, and handle setpoint changes and sensor noise.

A linear time-invariant state-space model is
$$\dot{\mathbf{x}}=A\mathbf{x}+B\mathbf{u}+E\mathbf{w},\qquad \mathbf{y}=C\mathbf{x}+D\mathbf{u}+\mathbf{v},$$
with disturbance $\mathbf{w}$ and measurement noise $\mathbf{v}$. Stability, controllability, observability, and estimator assumptions must be checked around a defined operating point.

For sinusoidal steady state in a single-phase convention,
$$\underline S=P+jQ=\underline V_{rms}\underline I_{rms}^{*},\quad P=V_{rms}I_{rms}\cos\phi,\quad Q=V_{rms}I_{rms}\sin\phi.$$
Three-phase, unbalanced, distorted, and converter-dominated systems require the appropriate convention and model.

## 7. Definitions of symbols and units

- $t$: Time, measured in seconds (s).
- $\tau$: Variable of integration for time, measured in seconds (s).
- $K_p, K_i, K_d$: Tuning parameters for a PID controller. Units depend on the specific process being controlled.
- $j$: The imaginary unit, where $j^2 = -1$.
- $V_{rms}$: Root-mean-square voltage, measured in Volts (V).
- $I_{rms}$: Root-mean-square current, measured in Amperes (A).

## 8. Assumptions and approximations

- **Linearity and time invariance:** Models usually apply near an operating point and over a stated frequency and amplitude range.
- **Sampling and delay:** Continuous equations omit discrete sampling, jitter, communication loss, computation time, and zero-order hold unless added.
- **Sensor and actuator limits:** Noise, drift, saturation, backlash, dead time, hysteresis, and rate constraints can destabilise or bias a loop.
- **Known model:** Parameters, disturbances, and topology change; robust, adaptive, or gain-scheduled methods still require boundaries.
- **Power-system phasors:** RMS and phasor models assume waveform and timescale conditions; electromagnetic and switching transients need faster models.
- **Human and organisational layer:** Procedures, interfaces, staffing, maintenance, markets, regulation, and cybersecurity affect technical outcomes.

## 9. Spatial and temporal scales

- **Temporal:** Control loops in robotics and power electronics operate at microsecond to millisecond scales. Mechanical systems (like heating a room) operate on scales of minutes to hours. Grid frequency control operates in milliseconds to seconds, while energy market dispatch operates in hours to days.
- **Spatial:** Sensors operate at the microscale (MEMS accelerometers). Robotics operate at the human scale (meters). Power grids span continental scales (thousands of kilometers).

## 10. Common misconceptions

- **“Derivative control predicts the future.”** It reacts to measured rate and often amplifies noise; filtered PI or other structures may be preferable.
- **“Integral action always removes steady-state error.”** This requires closed-loop stability, sufficient control authority, a suitable plant and disturbance model, and anti-windup handling.
- **“Renewables inherently destabilise or automatically strengthen a grid.”** Outcomes depend on penetration, location, network strength, controls, reserves, protection, forecasting, storage, demand, and grid-forming or grid-following behavior.
- **“Redundancy guarantees safety.”** Common-cause failure, shared software, incorrect sensors, maintenance, and voting logic can defeat redundant channels.
- **“Automation removes the human role.”** Humans design, authorise, supervise, maintain, recover, and remain affected by system decisions.

## 11. Connections to other modules

- **10-electricity-magnetism:** Provides the foundation for how sensors (like Hall effect sensors) and actuators (like electric motors) function.
- **11-waves-signals:** Essential for understanding signal conditioning, filtering noise from sensor data, and AC power transmission.
- **18-semiconductors-electronics:** Explains the microprocessors that execute control algorithms and the power electronics that drive actuators and interface renewable energy with the grid.
- **19-software-ai:** Modern control systems increasingly use machine learning for system identification, predictive maintenance, and complex decision-making in robotics.

## Phase 9 review boundaries and validity limits

- Closed-loop performance depends on sensing, estimation, delay, sampling, quantisation, communication, actuator saturation, disturbances, uncertainty, and model mismatch.
- Stability and safety are properties of a specified operating region and architecture; a controller that works in one regime may fail in another.
- Grid operation couples physics, protection, markets, communications, cybersecurity, regulation, operators, and restoration procedures.
- Cyber-physical and infrastructure designs require defence in depth, fail-safe or fail-operational analysis, human authority, testing, maintenance, and lifecycle governance.

## 12. Sources

1. WPILib Contributors. *Introduction to State-Space Control*. https://docs.wpilib.org/en/stable/docs/software/advanced-controls/state-space/state-space-intro.html
2. Peng, F. Z., et al. *Envisioning the Future Renewable and Resilient Energy Grids*. https://ieeexplore.ieee.org/abstract/document/10360247/
3. National Institute of Standards and Technology. *Framework for Cyber-Physical Systems: Volume 1, Overview*. https://www.nist.gov/publications/framework-cyber-physical-systems-volume-1-overview
4. National Institute of Standards and Technology. *SP 800-82 Rev. 2: Guide to Industrial Control Systems Security*. https://csrc.nist.gov/pubs/sp/800/82/r2/final
5. United States Department of Energy. *Grid Modernization Initiative*. https://www.energy.gov/gmi/grid-modernization-initiative
6. Filip, F. G., and Leiviskä, K. *Infrastructure and Complex Systems Automation*. https://link.springer.com/chapter/10.1007/978-3-030-96729-1_27
