---
title: "Feedback Instability"
slug: failure-pattern-feedback-instability
domain: experience
experience_type: failure-pattern
status: reviewed
artifact_revision: 1
release_status: draft
prerequisites: [03-mathematical-models, 20-sensors-control-infrastructure]
connections: [concept-stability-and-change, concept-cause-and-effect, concept-systems-and-models, system-dossier-refrigerator]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# Feedback Instability

A feedback controller is intended to reduce error. With excessive gain, delay, saturation, or a poor model, the correction can create oscillation, overshoot, or runaway behaviour.

## 1. Normal operation

```text
target → comparison → controller → actuator → physical system → sensor → comparison
```

Negative feedback is stabilising only when correction direction, magnitude, and timing are appropriate.

## 2. Disturbance

A measured state moves away from its target. The controller commands a corrective input, but the physical response may not be immediately visible.

## 3. Hidden condition

The system can already be storing momentum, heat, pressure, inventory, or an actuator command while the sensor still reports an old state. Sources of delay include sensor response, communication, filtering, computation, transport, and actuator inertia.

## 4. Amplifying mechanism

```text
small error
→ strong delayed correction
→ stored response continues
→ overshoot
→ reversed error
→ strong delayed reverse correction
→ oscillation
```

## 5. Minimum model

A thermal plant can be approximated by

$$C\frac{dT}{dt}=P-k(T-T_{env})$$

with proportional control

$$P=K_p(T_{set}-T)$$

If the controller acts on $T(t-\tau)$ rather than the current temperature, increasing gain $K_p$ or delay $\tau$ can reduce stability. The exact boundary depends on the plant and controller; the general causal lesson is that gain and delay interact.

## 6. Detection delay

Instability may begin as small hunting around a setpoint. Averages can hide the oscillation. Operators may mistakenly increase gain because they interpret the variation as weak correction.

## 7. Threshold crossing and propagation

Oscillation becomes consequential when temperature, pressure, voltage, speed, inventory, or another state crosses a limit. Protective actions can add more discontinuities and delays, creating a larger coupled problem.

## 8. Protective barriers

- conservative gain and rate limits;
- hysteresis or deadbands;
- anti-windup where integral control is used;
- independent high and low limit protection;
- delay-aware models;
- alarms based on oscillation amplitude or frequency;
- safe fallback modes.

## 9. Why barriers fail

Barriers may share the same sensor, software, model, communication link, or power supply. A protection function implemented only inside the failed controller is not fully independent. Tuning for one operating condition can also fail under different loads or environments.

## 10. Redesign options

| Redesign | Benefit | Trade-off |
| --- | --- | --- |
| Reduce gain | Less overshoot | Slower response |
| Improve sensor placement | Less misleading delay | Installation complexity |
| Add derivative action | Anticipates change | Noise sensitivity |
| Add predictive control | Handles constraints and delay | Model and computation burden |
| Add independent protection | Limits consequences | Cost and maintenance |

## 11. Transfer across domains

The pattern appears in thermostats, vehicle control, power grids, network congestion, supply chains, ecological management, and other delayed-response systems. The variables differ, but the structure—measurement, delay, correction, stored response, and overshoot—remains recognisable.

## 12. Questions for investigation

- Which delay dominates the loop?
- What state continues changing after the command changes?
- Are protective barriers genuinely independent?
- Is slower response safer or more efficient?

## 13. Sources and module links

- MIT OpenCourseWare, *Feedback Control Systems*: https://ocw.mit.edu/courses/16-30-feedback-control-systems-fall-2010/
- MIT OpenCourseWare, *Analysis and Design of Feedback Control Systems*: https://ocw.mit.edu/courses/2-14-analysis-and-design-of-feedback-control-systems-spring-2014/
- MIT OpenCourseWare, *Designing Control Systems*: https://ocw.mit.edu/courses/6-01sc-introduction-to-electrical-engineering-and-computer-science-i-spring-2011/45b4293fc23fa4731be9d0d59f4f212d_MIT6_01SCS11_lec06_handout.pdf
- [Mathematical Models](../foundations/03-mathematical-models/overview.md)
- [Sensors, Control, and Infrastructure](../technology/20-sensors-control-infrastructure/overview.md)
- [The Domestic Refrigerator](../system-dossiers/refrigerator.md)
