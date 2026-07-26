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
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Feedback Instability

A feedback controller is intended to reduce error. Excessive gain, delay, saturation, or a poor model can create overshoot, sustained oscillation, growing oscillation, or runaway behaviour. These outcomes must not be collapsed into one label: **oscillation is a pattern of repeated change, whereas instability is a conclusion about how trajectories respond under a stated stability criterion**.

## 1. Normal operation

```text
target → comparison → controller → actuator → physical system → sensor → comparison
```

Negative feedback is stabilising only when correction direction, magnitude, and timing are appropriate. A stable controlled system may approach its target smoothly, approach it with decaying oscillation, or operate in a deliberately bounded cycle such as thermostat hysteresis.

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
→ repeated oscillation
```

The chain establishes a mechanism that can produce oscillation. It does not by itself establish instability. The resulting motion may decay, remain bounded, settle into a limit cycle, grow, or cross an operational limit depending on the plant, controller, nonlinearities, initial state, disturbance, and definition of stability.

## 5. Minimum model: continuous-time thermal plant

A thermal plant can be approximated by

$$C\frac{dT}{dt}=P-k(T-T_{env})$$

with proportional control

$$P=K_p(T_{set}-T).$$

If the controller acts on $T(t-\tau)$ rather than the current temperature, increasing gain $K_p$ or delay $\tau$ can reduce a stability margin. The exact boundary depends on the plant and controller. Observing oscillation is evidence about dynamic behaviour, but classifying the closed loop as stable or unstable requires an explicit criterion and analysis.

## 6. Exact delayed-correction recurrence boundary

The Atlas delayed-correction model referenced by the bridge candidate is

$$x_{t+1}=x_t-x_{t-1},\qquad x_0=1,\quad x_1=0.$$

It produces

```text
1, 0, -1, -1, 0, 1, 1, 0, ...
```

The ordered state pair returns after six steps, so the orbit is exactly periodic with period 6. It is also bounded. This model therefore demonstrates that delayed correction can generate oscillation; it does not demonstrate that the orbit is unstable, that delay always causes instability, or that a real physical system will follow this recurrence.

## 7. Detection delay and classification

Averages can hide oscillatory behaviour. Useful observations include amplitude, period, damping or growth rate, phase, operating limits, and response to a small perturbation.

- **Decaying oscillation:** repeated variation whose amplitude decreases toward an equilibrium.
- **Bounded sustained oscillation:** repeated variation with non-growing amplitude; it may be a designed cycle, a marginal case, or a stable nonlinear limit cycle.
- **Growing oscillation:** increasing amplitude that may indicate instability under the chosen criterion.
- **Operational failure:** a limit is crossed or service is unacceptable, even when the mathematical trajectory remains bounded.

Operators can worsen a loop by increasing gain when they mistake delay or bounded cycling for weak correction.

## 8. Threshold crossing and propagation

Oscillation becomes consequential when temperature, pressure, voltage, speed, inventory, or another state crosses a limit. Consequence and mathematical instability are related but distinct: a bounded oscillation can still violate a safety or quality requirement, while an unstable mode may be intercepted before a limit is crossed. Protective actions can add discontinuities and delays, creating a larger coupled problem.

## 9. Protective barriers

- conservative gain and rate limits;
- hysteresis or deadbands where bounded cycling is acceptable;
- anti-windup where integral control is used;
- independent high and low limit protection;
- delay-aware models;
- alarms based on amplitude, growth rate, frequency, and limit proximity;
- safe fallback modes.

## 10. Why barriers fail

Barriers may share the same sensor, software, model, communication link, or power supply. A protection function implemented only inside the failed controller is not fully independent. Tuning for one operating condition can also fail under different loads or environments.

## 11. Redesign options

| Redesign | Benefit | Trade-off |
| --- | --- | --- |
| Reduce gain | Can increase stability margin and reduce overshoot | Slower response |
| Improve sensor placement | Reduces misleading delay | Installation complexity |
| Add derivative action | Anticipates change | Noise sensitivity |
| Add predictive control | Handles constraints and delay | Model and computation burden |
| Add independent protection | Limits consequences | Cost and maintenance |

## 12. Transfer across domains

The pattern appears in thermostats, vehicle control, power grids, network congestion, supply chains, ecological management, and other delayed-response systems. The variables differ, but the structure—measurement, delay, correction, stored response, and overshoot—remains recognisable. Whether that structure produces a stable transient, a bounded cycle, or instability remains system-specific.

## 13. Questions for investigation

- Which delay dominates the loop?
- What state continues changing after the command changes?
- Is the observed oscillation decaying, bounded, or growing?
- What stability criterion and operating limits are being used?
- Are protective barriers genuinely independent?
- Is slower response safer or more efficient?

## 14. Sources and module links

- MIT OpenCourseWare, *Feedback Control Systems*: https://ocw.mit.edu/courses/16-30-feedback-control-systems-fall-2010/
- MIT OpenCourseWare, *Analysis and Design of Feedback Control Systems*: https://ocw.mit.edu/courses/2-14-analysis-and-design-of-feedback-control-systems-spring-2014/
- MIT OpenCourseWare, *Designing Control Systems*: https://ocw.mit.edu/courses/6-01sc-introduction-to-electrical-engineering-and-computer-science-i-spring-2011/45b4293fc23fa4731be9d0d59f4f212d_MIT6_01SCS11_lec06_handout.pdf
- [Mathematical Models](../foundations/03-mathematical-models/overview.md)
- [Sensors, Control, and Infrastructure](../technology/20-sensors-control-infrastructure/overview.md)
- [The Domestic Refrigerator](../system-dossiers/refrigerator.md)
- [Principia–Atlas bridge candidate](../integration/principia-atlas/README.md)
