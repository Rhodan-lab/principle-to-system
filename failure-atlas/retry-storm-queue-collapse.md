---
title: "Retry Storm and Queue Collapse"
slug: failure-pattern-retry-storm-queue-collapse
domain: experience
experience_type: failure-pattern
status: reviewed
artifact_revision: 1
release_status: draft
prerequisites: [03-mathematical-models, 04-probability-statistics, 05-computation-algorithms, 19-software-ai, 20-sensors-control-infrastructure]
connections: [concept-cause-and-effect, concept-stability-and-change, concept-systems-and-models, system-dossier-web-service-request, investigation-queue-delay-near-capacity, design-challenge-resilient-school-information-service]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Retry Storm and Queue Collapse

Retries are intended to recover from transient loss. They become a failure amplifier when many clients repeat work faster than a degraded service can complete or reject it.

## 1. Normal operation

```text
request → service → response
    ↘ timeout or transient error → bounded delayed retry
```

A healthy retry policy distinguishes safe-to-repeat operations, limits attempts, spreads retries over time, and respects server or protocol feedback.

## 2. Disturbance

A dependency slows, capacity drops, a deployment introduces errors, a network path degrades, or a shared service becomes unavailable. Some original requests remain in progress while clients reach their timeout.

## 3. Hidden condition

A timeout does not prove that the original operation failed. The server may still be working, the response may be delayed, or a downstream side effect may already have occurred. Meanwhile, monitoring may count retries as ordinary new demand.

## 4. Amplifying mechanism

```text
service slows
→ clients time out
→ retries add offered load
→ queues and connection pools grow
→ service becomes slower
→ more clients time out together
→ retry storm and broad queue collapse
```

Synchronized retry intervals create bursts. Unlimited queues preserve work that is already too old to be useful, consuming memory and delaying fresher high-priority requests.

## 5. Minimum model

Let external demand be $\lambda_0$ requests per second. If a fraction $p$ of attempts is retried once, an approximate offered load is

$$\lambda_{offered}=\lambda_0(1+p)$$

With repeated independent retries up to a large limit, a geometric approximation is

$$\lambda_{offered}\approx\lambda_0\sum_{j=0}^{n}p^j$$

but real retries are neither independent nor guaranteed to see the same failure probability.

Backlog $B$ evolves approximately as

$$\frac{dB}{dt}=\lambda_{offered}(t)-\mu(t)$$

while backlog is positive. When $\lambda_{offered}>\mu$, delay grows and can increase the retry probability, closing the positive-feedback loop.

## 6. Detection delay

The first signal may be tail latency rather than mean latency. Client timeouts can be shorter than server work, so repeated attempts arrive before the original completes. Metrics aggregated over one minute may hide sub-second synchronization. Autoscaling can react after queues have already consumed memory or dependency connections.

## 7. Threshold crossing and propagation

The incident spreads when:

- thread, process, connection, or memory limits are reached;
- retries cross service boundaries and multiply at each layer;
- non-idempotent operations are repeated;
- health checks compete with user traffic;
- logging and tracing amplify I/O load;
- cache expiry or reconnect behavior synchronizes many clients;
- one overloaded dependency causes several upstream services to fail;
- recovery admits the accumulated backlog all at once.

## 8. Protective barriers

- bounded attempts and total retry time;
- exponential or otherwise increasing backoff with random jitter;
- explicit idempotency or deduplication for state-changing work;
- server-advertised delay such as `Retry-After` where applicable;
- admission control and bounded queues;
- deadlines propagated across service boundaries;
- circuit breakers and load shedding;
- priority for health, recovery, and mission-essential work;
- separate limits for users, tenants, operations, and dependencies;
- observability that distinguishes original requests from retries;
- staged recovery that drains backlog safely.

## 9. Why barriers fail

Every service may implement a locally reasonable retry policy while the combined system retries several times at several layers. Jitter may use the same seed or narrow range. A circuit breaker may open only after a dependency pool is exhausted. Idempotency keys may expire before delayed work arrives. A server can send `Retry-After`, but clients may ignore it.

## 10. Redesign options

| Redesign | Benefit | Trade-off |
| --- | --- | --- |
| Retry at one designated layer | Prevents multiplicative attempts | Requires clear ownership |
| Bounded queue with rejection | Preserves resources and freshness | Some work fails earlier |
| Deadline propagation | Stops work that can no longer help | Clock and protocol complexity |
| Idempotency and deduplication | Limits repeated side effects | State, storage, and expiry design |
| Randomized backoff | Reduces synchronization | Slower individual recovery |
| Degraded local response | Preserves core service | Reduced freshness or functionality |
| Priority admission | Protects critical requests | Requires governance and fairness rules |

## 11. Transfer across domains

The pattern resembles panic buying, traffic rerouting, emergency-room crowding, repeated control commands, supply-chain overordering, and repeated alarm acknowledgement. In each case, a local recovery action increases demand on a constrained system and makes the original problem harder to resolve.

## 12. Questions for investigation

- Which layer owns retry decisions?
- Can the original operation succeed after the client has timed out?
- Which requests are safe to repeat?
- How large can the queue become before work is no longer useful?
- Do retries share synchronized timing or common configuration?
- Which metrics separate offered load, admitted load, completed work, and retries?
- How should recovery avoid releasing all deferred work at once?

## 13. Sources and module links

- IETF, *RFC 9110: HTTP Semantics*: https://www.rfc-editor.org/rfc/rfc9110.html
- IETF, *RFC 6585: Additional HTTP Status Codes*: https://www.rfc-editor.org/rfc/rfc6585.html
- IETF, *RFC 9002: QUIC Loss Detection and Congestion Control*: https://www.rfc-editor.org/rfc/rfc9002.html
- National Institute of Standards and Technology, *Developing Cyber-Resilient Systems*: https://csrc.nist.gov/pubs/sp/800/160/v2/r1/final
- [Mathematical Models](../foundations/03-mathematical-models/overview.md)
- [Probability and Statistics](../foundations/04-probability-statistics/overview.md)
- [Software and AI](../technology/19-software-ai/overview.md)
- [A Web Request Through a Distributed Service](../system-dossiers/web-service-request.md)
