---
title: "Failure Atlas"
slug: failure-atlas
domain: experience
experience_type: index
status: reviewed
prerequisites: []
connections: [concept-cause-and-effect, concept-stability-and-change, concept-systems-and-models]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Failure Atlas

The Failure Atlas studies recurring failure structures rather than collecting dramatic accidents. Each entry traces how ordinary components, delays, hidden couplings, assumptions, and protective barriers interact to create failure.

## Required structure

1. Normal operation
2. Disturbance
3. Hidden condition
4. Amplifying mechanism
5. Minimum model
6. Detection delay
7. Threshold crossing and propagation
8. Protective barriers
9. Why barriers fail
10. Redesign options
11. Transfer across domains
12. Questions for investigation
13. Sources and module links

Use [`templates/failure-pattern.md`](../templates/failure-pattern.md).

## Reviewed patterns

- [Feedback Instability](feedback-instability.md) — thermal-control route
- [Protection Coordination Failure](protection-coordination.md) — resilient-energy route
- [Sensor Drift and Hidden Degradation](sensor-drift-hidden-degradation.md) — water-infrastructure route
- [Retry Storm and Queue Collapse](retry-storm-queue-collapse.md) — distributed-information route

Every authored pattern remains `release_status: draft` until Phase 12. The canonical four-route inventory is [`experiences/phase-11b-inventory.json`](../experiences/phase-11b-inventory.json).
