---
title: "How Does Queueing Delay Grow Near Capacity?"
slug: investigation-queue-delay-near-capacity
domain: experience
experience_type: investigation
status: reviewed
artifact_revision: 1
release_status: draft
prerequisites: [03-mathematical-models, 04-probability-statistics, 05-computation-algorithms, 19-software-ai]
connections: [concept-patterns, concept-stability-and-change, system-dossier-web-service-request, failure-pattern-retry-storm-queue-collapse, design-challenge-resilient-school-information-service]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# How Does Queueing Delay Grow Near Capacity?

## 1. Question

How does response delay change as arrival rate approaches service capacity, and why can average utilization hide severe tail delay?

## 2. Why the answer is not obvious

Two systems with the same average arrival and service rates can have different delay because arrivals and service times vary. Short bursts create backlog even when the long-run average appears safe. A queue may also reject, retry, prioritize, or abandon work, changing which requests are observed.

## 3. Competing models

### Model A: no-queue capacity model

$$T=\frac{1}{\mu}$$

Every request takes one average service time and never waits. This is a useful lower bound, not a realistic overloaded-service model.

### Model B: simple M/M/1 mean-delay model

For Poisson arrivals and exponential service with $\lambda<\mu$,

$$W=\frac{1}{\mu-\lambda}$$

This predicts rapidly increasing mean time in system as utilization approaches one. Its assumptions are restrictive.

### Model C: finite-buffer simulation

Simulate arrivals, service times, a queue limit, rejection, deadlines, and optional retries. This permits realistic policies but makes conclusions conditional on the chosen distributions and rules.

## 4. Variables and units

| Quantity | Symbol | Unit |
| --- | --- | --- |
| Arrival rate | $\lambda$ | requests/s |
| Service rate | $\mu$ | requests/s |
| Utilization | $\rho=\lambda/\mu$ | dimensionless |
| Queue length | $B$ | requests |
| Waiting time | $W_q$ | s or ms |
| Total response time | $W$ | s or ms |
| Queue capacity | $B_{max}$ | requests |
| Rejection fraction | $p_r$ | dimensionless |
| Retry fraction | $p_{retry}$ | dimensionless |

## 5. Safe observation or simulation method

Use an offline spreadsheet or local simulation with synthetic requests. Generate arrival times and service durations from declared distributions, then compare utilization levels such as 0.3, 0.6, 0.8, 0.9, and 0.97.

Do not send automated traffic to a real website, school system, game server, API, account, network, or device. Do not bypass rate limits, authentication, or acceptable-use policies. The investigation must remain entirely synthetic or use an explicitly provided educational dataset.

## 6. Data-recording structure

| Scenario | $\lambda$ | $\mu$ | $\rho$ | Mean delay | 95th percentile | Maximum queue | Rejection fraction | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| A | 3 | 10 | 0.30 |  |  |  |  | low utilization |
| B | 6 | 10 | 0.60 |  |  |  |  | moderate |
| C | 8 | 10 | 0.80 |  |  |  |  | variable bursts matter |
| D | 9 | 10 | 0.90 |  |  |  | tail growth |
| E | 9.7 | 10 | 0.97 |  |  |  | near capacity |

Run multiple random seeds and record the number of completed, rejected, abandoned, and retried requests separately.

## 7. Uncertainty and confounders

Consider:

- arrival distribution and burst correlation;
- service-time distribution and heavy tails;
- warm-up period and simulation length;
- multiple workers or dependencies;
- caching and batching;
- finite queue and deadlines;
- retries that increase offered load;
- requests abandoned before measurement;
- priority classes;
- autoscaling delay;
- clock resolution and percentile estimation.

A short simulation near instability can appear healthy by chance. A long queue may also hide failure by delaying work rather than rejecting it.

## 8. Analysis method

Calculate utilization:

$$\rho=\frac{\lambda}{\mu}$$

and compare simulated mean delay with the simple M/M/1 prediction. Plot mean, median, 95th percentile, and rejection fraction against $\rho$.

Check Little’s Law for the stable observed interval:

$$L\approx\lambda_{completed}W$$

using a consistent boundary and completed-throughput rate. A mismatch can indicate measurement error, unstable accumulation, excluded requests, or inconsistent definitions.

Estimate uncertainty across repeated simulations. Inspect residuals rather than claiming the analytical model is correct because one average is close.

## 9. Interpretation limits

The M/M/1 relation does not represent every web service. Real systems have parallel servers, shared dependencies, caches, nonstationary traffic, rate limits, priorities, deadlines, failures, and control loops. Synthetic results do not predict a specific live service without validated parameters.

A percentile describes the measured population only. It may exclude users who abandoned requests, requests rejected before timing, or locations absent from the dataset.

## 10. Model revision

Revise the model when:

- delay grows faster than the analytical prediction;
- service times are heavy-tailed;
- bursts create long queues at moderate average utilization;
- finite buffers trade delay for rejection;
- retries increase arrival rate after errors;
- several service stages create interacting queues;
- capacity changes over time;
- priority traffic improves one class while harming another.

The next model should add the smallest mechanism needed to explain a residual pattern.

## 11. Transfer questions

- Why can 90% average utilization be riskier than it sounds?
- How do queue limits change failure visibility?
- Why might rejection protect overall service?
- How can retries shift a stable system into overload?
- Which metric best represents a user waiting in a tail event?
- How would several parallel workers change the model?
- What evidence distinguishes insufficient capacity from a slow dependency?

## 12. Sources and module links

- IETF, *RFC 9110: HTTP Semantics*: https://www.rfc-editor.org/rfc/rfc9110.html
- IETF, *RFC 6585: Additional HTTP Status Codes*: https://www.rfc-editor.org/rfc/rfc6585.html
- IETF, *RFC 9002: QUIC Loss Detection and Congestion Control*: https://www.rfc-editor.org/rfc/rfc9002.html
- [Mathematical Models](../foundations/03-mathematical-models/overview.md)
- [Probability and Statistics](../foundations/04-probability-statistics/overview.md)
- [Computation and Algorithms](../foundations/05-computation-algorithms/overview.md)
- [Software and AI](../technology/19-software-ai/overview.md)
- [A Web Request Through a Distributed Service](../system-dossiers/web-service-request.md)
