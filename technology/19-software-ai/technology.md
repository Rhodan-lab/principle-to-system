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

The engineering of modern computing systems relies on several foundational scientific principles. Information theory, specifically Shannon entropy and channel capacity, dictates the theoretical limits of data compression and transmission over noisy channels. The principles of probability and statistics underpin machine learning algorithms, allowing systems to infer patterns from noisy or incomplete data. Calculus, particularly the chain rule, is the mathematical engine behind backpropagation, enabling the optimization of complex neural networks. Finally, the physics of semiconductors governs the physical layer of all these systems, dictating the speed, power consumption, and miniaturization limits of the underlying hardware.

## 2. The engineering problem

The core engineering problem is how to build reliable, scalable, and intelligent systems out of inherently unreliable and limited physical components. Specifically, engineers must figure out how to transmit data across the globe without errors despite physical noise, how to allow multiple independent programs to share a single processor without interfering with each other, how to store and retrieve massive amounts of structured data efficiently, and how to design algorithms that can learn complex tasks from data rather than requiring explicit, brittle rules.

## 3. Main components

- **Hardware and firmware:** Processors, memory, storage, accelerators, network interfaces, boot chains, and device controllers.
- **Operating system and runtime:** Scheduling, memory, files, isolation, drivers, identity, logging, and interfaces; security depends on design, configuration, implementation, hardware, updates, and operation.
- **Network services:** Links, routers, naming, addressing, transports, encryption, load balancing, and observability.
- **Data systems:** Schemas, storage engines, indexes, transactions, replication, recovery, access control, lineage, and retention.
- **ML lifecycle:** Data collection and governance, training, evaluation, deployment, monitoring, incident handling, model and prompt configuration, human review, and retirement.
- **Organisational controls:** Requirements, change management, threat modelling, privacy review, documentation, audit, procurement, and accountability.

## 4. How the components interact

These components interact through well-defined interfaces and protocols. An application running on an operating system makes system calls to request resources (like opening a file or sending data over a network). When sending data, the OS network stack formats the data according to TCP/IP protocols, breaking it into packets. These packets are transmitted via physical network interfaces to routers, which use routing tables to forward the packets toward their destination. If the application is querying a database, it sends a SQL command over the network to the RDBMS, which parses the query, accesses the storage engine to retrieve the data, and sends the result back. In an AI context, an application might send data to a trained neural network model hosted on a server, which processes the input through its layers of weights and biases to return a prediction.

## 5. Matter, energy, force, or information flow

Information is represented by physical states and transformed through hardware and software abstractions. Data movement consumes energy and often dominates computation. During model training, activations, parameters, gradients, optimiser state, and checkpoints move through memory and networks; “information flowing backward” is a metaphor for derivative computation, not a substance. System boundaries should include users, data sources, operators, external services, electricity, cooling, and discarded hardware.

## 6. System architecture

Layering reduces local complexity but does not remove cross-layer effects. Internet protocols, operating systems, databases, cloud platforms, and ML services each use different architectures. A production AI service commonly includes data ingestion, retrieval, model inference, policy enforcement, authentication, rate limiting, logging, human escalation, monitoring, rollback, and incident response. Trust boundaries and failure containment must be explicit; a model is one component, not the whole system.

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

The environmental impact of computing is significant. Data centers consume massive amounts of electricity for computation and cooling. The manufacturing of semiconductors involves toxic chemicals and significant water usage. E-waste is a major global challenge, as hardware rapidly becomes obsolete. The lifecycle of software involves continuous updates and patching to address security vulnerabilities and changing requirements, requiring ongoing engineering effort long after the initial deployment.

## 12. Connections to other technologies

- **Cloud Computing:** Relies entirely on virtualization (OS concepts), networking, and distributed databases to provide scalable resources on demand.
- **Autonomous Vehicles:** Integrates real-time operating systems, computer vision (deep learning), and sensor networks to navigate physical environments.
- **Cryptography:** Uses complex algorithms and information theory to secure data transmission across public networks.

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
