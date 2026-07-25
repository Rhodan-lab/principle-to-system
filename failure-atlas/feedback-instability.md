---
title: "Feedback Instability"
slug: "failure-pattern-feedback-instability"
domain: "experience"
status: draft
prerequisites: [03-mathematical-models, 20-sensors-control-infrastructure]
connections: [concept-stability-and-change, concept-cause-and-effect, system-dossier-refrigerator]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# Feedback Instability

A feedback controller is meant to reduce error. Under the wrong conditions, the correction itself can create oscillation, overshoot, or runaway behaviour.

## 1. Normal operation

A sensor measures a system state. The controller compares it with a target and changes an actuator. The actuator changes the system, and the sensor observes the result.

```text
target
→ comparison
→ controller
→ actuator
→ physical system
→ sensor
→ comparison
```

Negative feedback is stabilising only when the correction has an appropriate direction, magnitude, and timing.

## 2. Disturbance

Suppose the measured state falls below the target. The controller increases the corrective input. In a slow system, the effect may not appear immediately.

## 3. Hidden condition

The controller sees the old state while the system is already responding internally. The measurement therefore understates how much correction has already been committed.

Sources of delay include:

- sensor response time;
- communication latency;
- actuator inertia;
- thermal or fluid transport time;
- averaging and filtering;
- computation and scheduling delay.

## 4. Amplifying mechanism

If controller gain is too high, it applies a large correction during the delay. By the time the measured state reaches the target, the system has enough momentum or stored energy to continue past it.

The controller then reverses direction, again too strongly and too late. The sequence repeats.

```text
small error
→ strong delayed correction
→ overshoot
→ reversed error
→ strong delayed reverse correction
→ larger overshoot
```

## 5. Minimum model

A simple controlled thermal system can be represented as

$$C\frac{dT}{dt}=P-k(T-T_{env})$$

where $C$ is effective heat capacity, $P$ is controller-supplied heating or cooling power, and $k(T-T_{env})$ is heat exchange with the environment.

A proportional controller might use

$$P=K_p(T_{set}-T)$$

With negligible delay, a suitable $K_p$ can reduce error smoothly. With delay $\tau$, the controller effectively acts on $T(t-\tau)$ rather than the current state. Increasing $K_p$ or $\tau$ can turn smooth convergence into oscillation.

The exact stability boundary depends on the plant model, but the causal lesson is general: gain and delay interact.

## 6. Detection delay

Instability may first appear as harmless hunting around a setpoint. Operators can misinterpret the oscillation as random disturbance and raise the gain, making the problem worse.

A dashboard that shows only averages may hide the oscillation entirely.

## 7. Threshold crossing and propagation

Oscillation becomes dangerous when it crosses a physical or operational limit:

- temperature exceeds a material rating;
- pressure activates a relief device;
- voltage protection disconnects equipment;
- inventory alternates between shortage and excess;
- traffic control creates stop-and-go waves;
- a human operator begins counteracting an automated controller.

Once protective systems activate, the system may gain additional discontinuities and delays, producing more complex behaviour.

## 8. Protective barriers

Useful barriers include:

- conservative controller gain;
- hysteresis or deadbands;
- rate limits on actuator commands;
- independent high and low limit protection;
- anti-windup for integral controllers;
- delay-aware models;
- alarms based on oscillation amplitude or frequency;
- safe fallback modes.

## 9. Why barriers fail

Barriers often fail because they share the same sensor, software, power supply, or incorrect model. A limit implemented in the same controller is not fully independent of that controller.

Another failure mode is optimisation under one operating condition. A controller tuned for an empty, warm refrigerator may behave differently when heavily loaded, frosted, or placed in a hotter room.

## 10. Redesign options

| Redesign | Benefit | New trade-off |
| --- | --- | --- |
| Reduce gain | Less overshoot | Slower response |
| Add derivative action | Anticipates change | Amplifies measurement noise |
| Add integral action carefully | Removes persistent offset | Can accumulate excessive command during saturation |
| Improve sensor placement | Reduces misleading delay | Installation complexity |
| Use predictive control | Accounts for future response and constraints | Requires a trustworthy model and more computation |
| Add independent protection | Limits consequences | Cost and maintenance burden |

## 11. Transfer across domains

The same pattern appears in:

- thermostats and refrigeration;
- vehicle steering and autopilot;
- power-grid frequency control;
- supply-chain ordering;
- network congestion control;
- medication dosing under delayed biological response;
- ecological management with slow population feedback.

The variables differ, but the structure remains: measurement, delay, correction, stored momentum, and overshoot.

## 12. Questions for investigation

- Which delay dominates the loop?
- What energy, inventory, or momentum continues changing after the command changes?
- Are protection systems genuinely independent?
- Does the controller remain stable across all expected loads and environments?
- Could a slower response be safer and more efficient?

## Module links

- [Mathematical Models](../foundations/03-mathematical-models/overview.md)
- [Sensors, Control, and Infrastructure](../technology/20-sensors-control-infrastructure/overview.md)
- [Stability and Change](../concepts/stability-and-change.md)
- [The Domestic Refrigerator](../system-dossiers/refrigerator.md)
