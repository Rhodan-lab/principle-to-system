---
title: "Software, Information, Networks, and AI Foundations"
slug: 19-software-ai-technology
module: "Module 19"
domain: technology
status: reviewed
prerequisites: [04-probability-statistics, 05-computation-algorithms, 18-semiconductors-electronics]
connections: [20-sensors-control-infrastructure]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Software, Information, Networks, and AI Foundations

## 1. Scientific principles used

Information theory bounds compression and communication for stated probabilistic models. Probability, statistics, optimisation, numerical analysis, and experimental design support inference and evaluation but do not guarantee deployment validity. Logic, automata, complexity, programming-language semantics, distributed-systems models, cryptography, human factors, and semiconductor physics constrain different layers of a computing system.

## 2. The engineering problem

The problem is to provide a defined service under limits on correctness, availability, latency, throughput, privacy, security, safety, energy, cost, maintainability, and accountability despite hardware faults, software defects, hostile inputs, changing data, dependency failures, and human use. “Reliable,” “scalable,” and “intelligent” require measurable service-level and task definitions rather than being treated as intrinsic system properties.

## 3. Main components

- **Hardware and firmware:** Processors, memory, storage, accelerators, network interfaces, boot chains, and device controllers.
- **Operating system and runtime:** Scheduling, memory, files, isolation, drivers, identity, logging, and interfaces; security depends on design, configuration, implementation, hardware, updates, and operation.
- **Network services:** Links, routers, naming, addressing, transports, encryption, load balancing, and observability.
- **Data systems:** Schemas, storage engines, indexes, transactions, replication, recovery, access control, lineage, and retention.
- **ML lifecycle:** Data collection and governance, training, evaluation, deployment, monitoring, incident handling, model and prompt configuration, human review, and retirement.
- **Organisational controls:** Requirements, change management, threat modelling, privacy review, documentation, audit, procurement, and accountability.

## 4. How the components interact

Applications use operating-system and runtime interfaces, local libraries, storage, network transports, identity services, databases, queues, and external APIs according to a particular architecture. A request may use TCP, UDP, or QUIC; data may be relational, document, object, stream, graph, or file based. An AI-enabled service may combine retrieval, deterministic rules, one or more models, tools, policy checks, human review, logging, monitoring, and fallback. Interface contracts, authentication, schema, timing, retries, idempotency, provenance, and failure semantics must be explicit.

## 5. Matter, energy, force, or information flow

Information is represented by physical states and transformed through hardware and software abstractions. Data movement consumes energy and often dominates computation. During model training, activations, parameters, gradients, optimiser state, and checkpoints move through memory and networks; “information flowing backward” is a metaphor for derivative computation, not a substance. System boundaries should include users, data sources, operators, external services, electricity, cooling, and discarded hardware.

## 6. System architecture

Layering reduces local complexity but does not remove cross-layer effects. Internet protocols, operating systems, databases, cloud platforms, and ML services each use different architectures. A production AI service commonly includes data ingestion, retrieval, model inference, policy enforcement, authentication, rate limiting, logging, human escalation, monitoring, rollback, and incident response. Trust boundaries and failure containment must be explicit; a model is one component, not the whole system.


### Explicit Principle-to-System Chain

```text
physical information states, algorithms, logic, and probability
→ instruction execution, data representation, and protocol semantics
→ operating-system, network, storage, and model components
→ authenticated interfaces and distributed service architecture
→ monitoring, governance, human authority, fallback, and recovery
→ bounded user-facing software or AI-enabled service
```

## 7. Design constraints

- **Latency, throughput, and tail behavior:** Percentiles, queueing, and overload matter more than averages alone.
- **Consistency, availability, and partitions:** Distributed systems make context-dependent trade-offs; slogans do not replace a failure model.
- **Computation, memory, and communication:** Complexity classes inform scaling, but approximation, heuristics, preprocessing, hardware, and input size determine practical feasibility.
- **Security and privacy:** Least privilege, secure development, encryption, isolation, secrets management, data minimisation, consent, retention, and incident response impose constraints.
- **AI-specific constraints:** Data rights, representativeness, calibration, interpretability, robustness, misuse resistance, human factors, and monitoring must be designed rather than added later.

## 8. Performance and efficiency

Network and database systems require load, dataset, hardware, consistency, and percentile definitions. AI evaluation should include task validity, baselines, confidence intervals, calibration, subgroup results, robustness, abstention, latency, throughput, cost, energy, privacy, and human outcomes. Accuracy on one test set is insufficient. Efficiency claims must include data movement, utilisation, retraining, failed experiments, serving, and lifecycle boundaries.

## 9. Reliability and failure modes

Checksums detect only specified corruption patterns; TCP retransmission does not make an application exactly-once or deadline-safe. Write-ahead logging supports recovery only with correct ordering, durable storage assumptions, tested restoration, and transaction design. Replication can copy errors or attacks. ML systems can fail through distribution shift, data or label errors, prompt injection, insecure tool use, feedback loops, model updates, dependency outages, automation bias, and silent metric drift. Reliability therefore requires redundancy, diversity where appropriate, validation, observability, backups, rollback, chaos or fault testing, and rehearsed recovery.

## 10. Safety principles

Use a lifecycle risk process: define context and affected people, map hazards and misuse, measure with valid tests, manage residual risk, document limitations, monitor deployment, provide human authority and appeal, and respond to incidents. Security testing must remain authorised and non-destructive. Protect personal data through minimisation, purpose limitation, access control, retention limits, and review. High-impact decisions require domain-qualified human oversight, uncertainty communication, logging, fallback, and the ability to stop or reverse automation.

## 11. Environmental and lifecycle considerations

Computing impacts depend on device manufacture, hardware lifetime, electricity source, utilisation, cooling, water, data movement, software efficiency, retraining, serving, storage, network infrastructure, and end-of-life treatment. Data-centre and model claims require a stated facility, workload, location, time, and accounting boundary. Security updates can extend useful life, while unsupported software, incompatible requirements, or inefficient workloads can drive replacement. Repair, reuse, longer support, efficient algorithms, right-sized hardware, and responsible recycling involve technical and organisational trade-offs.

## 12. Connections to other technologies

- **Cloud and distributed computing:** Combine virtualisation or containers where useful with physical hosts, networks, storage, identity, orchestration, observability, and organisational controls.
- **Cyber-physical systems:** Couple software decisions to sensors, actuators, timing, protection, operators, and physical consequences.
- **Cryptography and security engineering:** Use mathematical constructions together with key management, implementation, protocols, identity, access control, usability, monitoring, and recovery.
- **Data and AI systems:** Depend on governance, provenance, evaluation, deployment controls, human oversight, and incident response as well as models and computation.

## Phase 9 review boundaries and validity limits

- Information-theory limits are asymptotic results for stated source and channel models; finite systems trade error, latency, energy, complexity, and cost.
- Protocol guarantees apply only under their specifications and assumptions; end-to-end service also depends on applications, networks, implementations, and failures.
- Machine-learning evaluation must address distribution shift, uncertainty, calibration, subgroup performance, robustness, privacy, security, misuse, monitoring, and human oversight.
- Model outputs are evidence requiring verification, not authoritative facts or proof of consciousness, intention, or understanding.

## 13. Sources

1. Shannon, C. E. *A Mathematical Theory of Communication*. https://doi.org/10.1002/j.1538-7305.1948.tb01338.x
2. Kurose, J. F., and Ross, K. W. *Computer Networking: A Top-Down Approach*. https://www.pearson.com/en-us/subject-catalog/p/computer-networking-a-top-down-approach/P200000013385
3. Goodfellow, I., Bengio, Y., and Courville, A. *Deep Learning*. http://www.deeplearningbook.org
4. Hellerstein, J. M., Stonebraker, M., and Hamilton, J. *Architecture of a Database System*. https://doi.org/10.1561/1900000002
5. National Institute of Standards and Technology. *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
6. National Institute of Standards and Technology. *AI RMF: Generative Artificial Intelligence Profile*. https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
7. Internet Engineering Task Force. *RFC 9293: Transmission Control Protocol*. https://www.rfc-editor.org/info/rfc9293/
