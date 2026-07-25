---
title: "Software, Information, Networks, and AI Foundations"
slug: 19-software-ai
module: "Module 19"
domain: technology
status: reviewed
prerequisites: [04-probability-statistics, 05-computation-algorithms, 18-semiconductors-electronics]
connections: [20-sensors-control-infrastructure]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Software, Information, Networks, and AI Foundations

## 1. The central questions

How can physical states encode and transform abstract information with stated reliability, latency, and resource use? How do independently operated systems communicate across trust and failure boundaries? How can data-driven models support defined tasks, and how should their validity, uncertainty, rights, security, human oversight, and social consequences be governed across deployment?

## 2. Observable phenomena

Lossless compression reduces some structured files but cannot shrink every input; already compressed or high-entropy data may stay similar or grow because of headers. Error-control coding can make communication highly reliable at rates and latencies allowed by a channel, code, hardware, and target error probability.

Internet paths are selected through distributed routing and forwarding state. Delay includes propagation, transmission, queueing, processing, retransmission, and endpoint work; “milliseconds across continents” is not one universal value.

Machine-learning performance can improve with data, computation, architecture, objectives, and training, but more examples do not guarantee better deployment performance. Apparent capabilities must be defined by reproducible evaluations and checked for contamination, prompting effects, distribution shift, and failure cases.

## 3. Essential concepts

**Information measures:** Shannon entropy quantifies uncertainty for a probability model. It does not measure truth, usefulness, semantic meaning, or human importance.

**Source and channel coding:** Compression and reliable communication have asymptotic limits under stated source and channel assumptions. Finite systems trade block length, error, delay, energy, computation, and implementation complexity.

**Protocols and layering:** Internet communication uses multiple protocols. IP provides best-effort packet delivery; TCP provides a reliable ordered byte stream between endpoints under its specification, while applications still handle identity, semantics, retries, security, and failure.

**Operating systems and databases:** Kernels mediate resources and isolation, but security depends on design, configuration, implementation, hardware, updates, and operation. Databases combine storage, concurrency, recovery, query processing, schemas, and distributed trade-offs.

**Machine learning:** Models estimate functions or distributions from data and objectives. Supervised, self-supervised, unsupervised, and reinforcement-learning methods have different feedback and evaluation structures.

**AI risk management:** Trustworthiness concerns include validity, reliability, safety, security, resilience, accountability, transparency, explainability, privacy, fairness, misuse, information integrity, monitoring, incident response, and human oversight across the lifecycle.

## 4. Mechanisms and causal chains

In coding, a source model informs compression and controlled redundancy supports error detection or correction. Shannon's theorems show existence results in limiting regimes; they do not supply a free practical code or promise zero error at finite delay.

In networking, applications may use TCP, UDP, QUIC, or other transports over IP. TCP numbers bytes, acknowledges data, manages retransmission and flow/congestion behavior, but TCP does not guarantee that an application request is semantically processed once, securely, or within a deadline.

In neural-network training, automatic differentiation applies the chain rule to a computational graph. An optimiser uses gradients or related estimates to update parameters. Success depends on objective, data, representation, regularisation, optimisation, randomisation, hardware numerics, and evaluation; gradient descent does not guarantee the global optimum for a general non-convex model.

## 5. Important quantities

| Quantity | Unit or form | Boundary |
| :--- | :--- | :--- |
| Entropy or cross-entropy | bits, nats, or task-specific average | Requires a probability distribution and log base. |
| Bandwidth | Hz or sometimes data-rate context | Frequency span is not identical to throughput. |
| Signal-to-noise ratio | dimensionless ratio; dB after logarithmic conversion | State measurement bandwidth and reference. |
| Capacity | bit/s | Defined for a channel model and reliability criterion. |
| Latency | s | Specify one-way, round-trip, percentile, and boundary. |
| Throughput or goodput | bit/s, requests/s, tokens/s | Specify useful payload and load. |
| Loss | task-dependent | Not simply “difference”; may be negative log likelihood, ranking, control cost, or another objective. |
| Calibration error | task-dependent | Compares predicted confidence with observed frequency under a protocol. |
| Energy and emissions | J, kWh, or lifecycle units | Require hardware, utilisation, location, and accounting boundary. |

## 6. Mathematical models and equations

For a discrete random variable,
$$H(X)=-\sum_x p(x)\log_2p(x).$$
For an ideal code over long sequences, expected length is bounded relative to entropy; entropy is not literally the exact file size of every finite message.

For a bandwidth-limited additive white Gaussian-noise channel,
$$C=B\log_2\left(1+\frac{S}{N}\right).$$
Here $S/N$ is a dimensionless power ratio over the stated bandwidth. The equation does not imply infinite physical throughput when a model parameter is set to an unphysical limit; finite power, noise, bandwidth, precision, timing, and implementation remain.

A parameter update may be written
$$\theta_{k+1}=\theta_k-\alpha_k\widehat{\nabla L}(\theta_k),$$
where the gradient can be stochastic or approximate and the learning rate can carry units depending on parameterisation and loss.

An artificial unit
$$y=f(\mathbf{w}^{\mathsf T}\mathbf{x}+b)$$
is a computational component, not a biological neuron model or evidence of cognition.

## 7. Definitions of symbols and units

- $H(X)$: Shannon entropy of random variable $X$, bits when base-2 logarithms are used.
- $p(x)$: probability mass assigned to outcome $x$, dimensionless.
- $C$: capacity of the stated channel model, bit/s.
- $B$: channel bandwidth in the Shannon–Hartley model, Hz.
- $S,N$: average signal and noise powers over the stated bandwidth, W; $S/N$ is dimensionless.
- $\theta_k$: parameter vector at iteration $k$; units depend on parameterisation.
- $\widehat{\nabla L}(\theta_k)$: exact, stochastic, or approximate loss-gradient estimate with units of loss per parameter.
- $\alpha_k$: step size; units must make the update dimensionally consistent.
- $\mathbf x,\mathbf w$: input and weight vectors with model-dependent units.
- $b$: bias or intercept with units compatible with $\mathbf w^{\mathsf T}\mathbf x$.
- $f$: activation or response function.
- $y$: model output with task-dependent units or interpretation.

## 8. Assumptions and approximations

- **Source and channel models:** Stationarity, memory, noise, feedback, synchronisation, and coding constraints must be stated.
- **Finite implementation:** Block length, numerical precision, queueing, congestion, deadlines, and energy prevent direct identification of theorem limits with product performance.
- **Data-generating process:** Training examples are rarely perfectly independent, identically distributed, representative, consented, or stable over time.
- **Objective adequacy:** Optimising a proxy can improve the measured score while harming the intended outcome.
- **Evaluation validity:** Test leakage, benchmark saturation, selection bias, subgroup size, multiple comparisons, and adaptive use can invalidate conclusions.
- **Deployment:** Distribution shift, feedback loops, adversaries, users, automation bias, and organisational context change system behaviour.

## 9. Spatial and temporal scales

Computing spans device and package dimensions, boards and data centres, local and wide-area networks, and global organisational dependencies. Time scales span hardware switching and propagation, operating-system scheduling, storage and network delay, user interaction, model training, deployment monitoring, patching, incident response, and archival retention. Values vary by technology and workload; neither transistor dimensions nor parameter count determines one universal latency or training duration.

## 10. Common misconceptions

- **“Information equals meaning.”** Shannon information measures uncertainty in a model, not semantics, truth, value, or wisdom.
- **“The internet has no central points of failure.”** It is a network of networks, yet services, naming, routing, clouds, cables, power, and organisations can create concentrated dependencies.
- **“More data always improves AI.”** Data quality, relevance, rights, representation, contamination, objectives, model capacity, and distribution shift matter.
- **“A fluent model output proves understanding or consciousness.”** Observable behaviour supports claims about tested capability only; internal experience or broad human-like understanding cannot be inferred from fluency.
- **“AI safety means only speculative catastrophic scenarios.”** It also includes measurable failures involving validity, bias, privacy, security, misuse, automation, monitoring, and human consequences.

## 11. Connections to other modules

- **04-probability-statistics:** Supports uncertainty models, estimation, experimental design, calibration, causal questions, and evaluation.
- **05-computation-algorithms:** Provides models of computation, complexity, numerical limits, data structures, optimisation, verification, and algorithm design.
- **18-semiconductors-electronics:** Describes much of the physical substrate of contemporary digital computing, memory, networking, and accelerators while leaving room for photonic, quantum, and other architectures.
- **20-sensors-control-infrastructure:** Connects software and AI to measurement, actuation, timing, safety, operational technology, and human authority in physical systems.

## Phase 9 review boundaries and validity limits

- Information-theory limits are asymptotic results for stated source and channel models; finite systems trade error, latency, energy, complexity, and cost.
- Protocol guarantees apply only under their specifications and assumptions; end-to-end service also depends on applications, networks, implementations, and failures.
- Machine-learning evaluation must address distribution shift, uncertainty, calibration, subgroup performance, robustness, privacy, security, misuse, monitoring, and human oversight.
- Model outputs are evidence requiring verification, not authoritative facts or proof of consciousness, intention, or understanding.

## 12. Sources

1. Shannon, C. E. *A Mathematical Theory of Communication*. https://doi.org/10.1002/j.1538-7305.1948.tb01338.x
2. Kurose, J. F., and Ross, K. W. *Computer Networking: A Top-Down Approach*. https://www.pearson.com/en-us/subject-catalog/p/computer-networking-a-top-down-approach/P200000013385
3. Goodfellow, I., Bengio, Y., and Courville, A. *Deep Learning*. http://www.deeplearningbook.org
4. Hellerstein, J. M., Stonebraker, M., and Hamilton, J. *Architecture of a Database System*. https://doi.org/10.1561/1900000002
5. National Institute of Standards and Technology. *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
6. National Institute of Standards and Technology. *AI RMF: Generative Artificial Intelligence Profile*. https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
7. Internet Engineering Task Force. *RFC 9293: Transmission Control Protocol*. https://www.rfc-editor.org/info/rfc9293/
