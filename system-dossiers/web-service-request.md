---
title: "A Web Request Through a Distributed Service"
slug: system-dossier-web-service-request
domain: experience
experience_type: system-dossier
status: reviewed
artifact_revision: 1
release_status: draft
prerequisites: [05-computation-algorithms, 11-waves-signals, 18-semiconductors-electronics, 19-software-ai, 20-sensors-control-infrastructure]
connections: [concept-systems-and-models, concept-cause-and-effect, concept-stability-and-change, failure-pattern-retry-storm-queue-collapse, investigation-queue-delay-near-capacity, design-challenge-resilient-school-information-service]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# A Web Request Through a Distributed Service

A web page appears after a user selects a link, but the visible result is produced by a chain of devices, protocols, software processes, queues, data stores, policies, and organizations. A fast response is therefore a system outcome, not a property of one server.

## 1. Observable system

A user enters an address or activates a link. The interface may show a loading indicator, then content, an error, or a partial result. Behind this event, the client resolves a name, establishes network communication, sends an application request, traverses intermediaries, reaches one or more services, reads or changes data, and returns a response.

## 2. System boundary and environment

A useful boundary may include the user agent, local device, access network, name resolution, transport protocol, edge service, load balancer, application instances, caches, queues, databases, identity services, logging, monitoring, deployment system, and operators.

The environment includes user behavior, third-party dependencies, power, physical infrastructure, traffic changes, software updates, malicious input, regulation, organizational ownership, and upstream network policy. A service-level statement must identify which dependencies and user locations are included.

## 3. Inputs, outputs, stores, and flows

| Type | Examples |
| --- | --- |
| Inputs | Requests, configuration, code, data updates, credentials, operator actions |
| Outputs | Responses, errors, logs, metrics, notifications, side effects |
| Stores | Caches, databases, message queues, session state, configuration, audit records |
| Flows | Packets, requests, responses, state changes, replication, telemetry, human decisions |

A request can be retried, duplicated, reordered, delayed, or partially processed. The system must define which operations are safe to repeat and which require idempotency keys, transactions, or compensation.

## 4. Scientific principles

For a stable single-stage queue, Little’s Law relates average number in the system $L$, average arrival rate $\lambda$, and average time in system $W$:

$$L=\lambda W$$

The relation is a long-run accounting identity under stable conditions and consistent boundaries. It does not specify the distribution of delay or guarantee stability.

A simple utilization ratio is

$$\rho=\frac{\lambda}{\mu}$$

where $\mu$ is average service capacity. As $\rho$ approaches one, variability can make delay grow sharply. Real services include several queues, shared resources, caches, retries, timeouts, and changing capacity.

An end-to-end latency decomposition is

$$T_{total}=T_{dns}+T_{connect}+T_{network}+T_{queue}+T_{service}+T_{dependency}+T_{render}$$

with overlapping work and protocol reuse handled explicitly when relevant.

## 5. Components and functions

| Component | Function | Failure or limit |
| --- | --- | --- |
| User agent | Forms requests, validates responses, renders results | Cache state, compatibility, local resource limits |
| DNS resolver | Maps names to records | Stale data, outage, policy, poisoning defenses |
| Transport | Delivers application data with defined semantics | Loss, congestion, reordering, handshake cost |
| Edge or reverse proxy | Terminates connections, routes, caches, filters | Configuration, overload, certificate, shared dependency |
| Load balancer | Distributes work across instances | Health-check error, uneven load, stale membership |
| Application service | Implements business logic | Bugs, saturation, unsafe retries, state assumptions |
| Cache | Reduces repeated work | Staleness, invalidation, memory pressure |
| Queue | Buffers asynchronous work | Unbounded growth, duplicate work, delayed failure |
| Database | Stores durable state | Contention, replication lag, schema or transaction limits |
| Identity and authorization | Controls access | Central dependency, clock, policy, token handling |
| Observability system | Records evidence for operation | Sampling gaps, cardinality overload, privacy leakage |
| Deployment system | Changes code and configuration | Correlated failure, rollback difficulty, hidden drift |

## 6. Interaction architecture

```text
user agent
→ name resolution
→ connection and transport
→ edge routing
→ application service
→ cache / queue / database / identity dependencies
→ response

metrics + logs + traces + user reports
→ operators and automation
→ scaling, rollback, rate limits, routing, recovery
```

The data path and control path are distinct but coupled. A broken observability or deployment system can turn a manageable fault into a prolonged outage.

## 7. Quantitative model

For a simple queue with constant average rates, backlog changes approximately as

$$\frac{dB}{dt}=\lambda(t)-\mu(t)$$

while $B>0$, with $B\ge0$. If arrival rate exceeds service capacity for duration $\Delta t$, backlog grows by roughly $(\lambda-\mu)\Delta t$ before accounting for retries and dropped work.

A service objective should use a distribution, not only a mean. For example,

$$P(T_{total}\le T_{objective})\ge q$$

where $q$ is a stated fraction for a defined population, interval, and request class. A percentile can still hide excluded users, errors, or requests abandoned before measurement.

Availability over an interval may be represented by

$$A=1-\frac{T_{unavailable}}{T_{observed}}$$

but the definition of unavailable, partial service, planned maintenance, and user population must be explicit.

## 8. Control and feedback

Services use feedback through congestion control, autoscaling, admission control, cache policy, queue limits, health checks, circuit breakers, retries, and operator response. Delay can destabilize control: capacity may be added after demand has fallen, or failed instances may receive more work because health evidence is stale.

Retries need bounded attempts, delay, jitter, and a decision about whether the operation is safe to repeat. Overload control should reduce offered work before queues consume all memory, connections, threads, or dependency capacity.

## 9. Failure modes

- A dependency slows, causing upstream queues and timeouts.
- Clients retry together and multiply load.
- Health checks pass while user-facing work fails.
- Cache invalidation or expiry creates a synchronized demand spike.
- One deployment changes every instance at once.
- A database lock or connection pool becomes the actual bottleneck.
- An authentication or naming dependency becomes a common-mode failure.
- Metrics omit failed or abandoned requests.
- Logs expose sensitive content or overwhelm storage.
- Recovery restores capacity but repeats non-idempotent operations.
- A regional or provider failure affects supposedly independent replicas.

## 10. Efficiency and performance

Throughput, latency, error rate, resource use, energy, cost, privacy, and reliability interact. More caching can reduce latency and dependency work but complicate freshness. Larger queues absorb bursts but increase delay and stale work. More replicas can improve capacity but add coordination and consistency cost.

Optimization must distinguish user-perceived performance from internal processing time. A fast error is not successful service, and a high average throughput can coexist with severe tail latency.

## 11. Lifecycle consequences

The service depends on semiconductor hardware, data centers, networks, software supply chains, energy, cooling, replacement, operator labor, incident response, data governance, and long-term maintenance. Software that appears weightless still consumes physical resources and creates obligations for security updates, compatibility, data retention, and eventual decommissioning.

## 12. Alternative designs

- Monolithic application with one primary data store.
- Modular service architecture with explicit dependency contracts.
- Static or precomputed content with minimal dynamic processing.
- Queue-based asynchronous workflow for non-immediate tasks.
- Edge caching with origin fallback.
- Multi-zone or multi-region deployment with controlled failover.
- Offline-first client that preserves selected functions without continuous service.

Each alternative changes consistency, operational complexity, failure isolation, cost, and recovery behavior.

## 13. Principle-to-system chain

```text
binary representation and algorithms
→ electromagnetic signals and packet transport
→ protocol semantics
→ processes, queues, caches, and data stores
→ distributed coordination and identity
→ observability and control
→ overload management and recovery
→ user-facing service under stated objectives
```

## 14. Unresolved questions

- What request classes are load-bearing for the mission?
- Which dependencies are independent only in diagrams?
- Are retries safe for every operation?
- Which users or failures are absent from the metrics?
- How long can the service operate in a degraded local mode?
- Which data are truly necessary for operation and diagnosis?
- What evidence proves recovery rather than merely restored traffic?

## 15. Sources and module links

- IETF, *RFC 9110: HTTP Semantics*: https://www.rfc-editor.org/rfc/rfc9110.html
- IETF, *RFC 9002: QUIC Loss Detection and Congestion Control*: https://www.rfc-editor.org/rfc/rfc9002.html
- National Institute of Standards and Technology, *NIST Cloud Computing Reference Architecture*: https://www.nist.gov/publications/nist-cloud-computing-reference-architecture
- National Institute of Standards and Technology, *Developing Cyber-Resilient Systems*: https://csrc.nist.gov/pubs/sp/800/160/v2/r1/final
- [Computation and Algorithms](../foundations/05-computation-algorithms/overview.md)
- [Waves and Signals](../science/11-waves-signals/overview.md)
- [Software and AI](../technology/19-software-ai/overview.md)
- [Sensors, Control, and Infrastructure](../technology/20-sensors-control-infrastructure/overview.md)
