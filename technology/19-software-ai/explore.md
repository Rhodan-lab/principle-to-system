---
title: "Software, Information, Networks, and AI Foundations"
slug: 19-software-ai-explore
module: "Module 19"
domain: technology
status: reviewed
prerequisites: [04-probability-statistics, 05-computation-algorithms, 18-semiconductors-electronics]
connections: [20-sensors-control-infrastructure]
last_reviewed: 2026-07-26
content_license: CC-BY-4.0
---

# Software, Information, Networks, and AI Foundations

## 1. Observation prompts

- Use browser or operating-system performance panels on your own device to compare page size, request count, latency, caching, and throughput. Do not infer physical route or server location from delay alone.
- Examine recommendation settings using a fictional profile or your own non-sensitive history. Record what the interface reveals, what remains unknown, and how privacy, exploration, popularity, and business objectives could shape outputs.
- Compare two model outputs on a low-stakes public question. Check sources, uncertainty, consistency, and failure modes instead of rating fluency as understanding.

## 2. Prediction questions

- Predict compression for repetitive, already-compressed, encrypted, and random-looking files. Why can headers make some compressed outputs larger?
- If one router or link fails, outcomes depend on routing convergence, transport timeout, application retry, resumable transfer, multipath support, and failure location. List competing outcomes rather than predicting seamless continuation.
- A classifier trained on indoor cats may fail outdoors because background, lighting, camera, breed, label, and sampling distributions changed. Which validation set would test the intended deployment?

## 3. Worked reasoning examples

**Problem:** Calculate the Shannon entropy of a fair coin toss and a biased coin toss (where heads has a 90% probability).

**Reasoning:**
For a fair coin, the probabilities are $P(Heads) = 0.5$ and $P(Tails) = 0.5$.
Using the entropy formula: $H = -(0.5 \log_2 0.5 + 0.5 \log_2 0.5)$
$H = -(-0.5 - 0.5) = 1$ bit.
This means one bit of information is required to communicate the result of a fair coin toss.

For the biased coin, $P(Heads) = 0.9$ and $P(Tails) = 0.1$.
$H = -(0.9 \log_2 0.9 + 0.1 \log_2 0.1)$
$H \approx -(0.9 \times -0.152 + 0.1 \times -3.32)$
$H \approx -(-0.1368 - 0.332) = 0.469$ bits.
The entropy is lower because the outcome is more predictable; we are less uncertain about the result before the toss occurs.

## 4. Thought experiments

- **Noiseless-channel limit:** The Shannon–Hartley equation assumes an idealised Gaussian channel model. Letting $N\to0$ while holding other abstractions fixed exposes a model limit, not a physical design for infinite instantaneous communication. Identify omitted constraints such as quantisation, timing, bandwidth definition, finite energy, hardware, and relativity.
- **Proxy objective failure:** A room-cleaning system rewarded only for measured dust could manipulate the sensor or repeatedly move dust. Redesign the system using multiple measurements, constraints, human review, shutdown authority, and tests for distribution shift.
- **Automation and appeal:** Imagine a model recommends access to a school resource. What evidence, uncertainty, privacy protection, explanation, human review, and appeal process are required before the recommendation affects a student?

## 5. Household and browser-based explorations

- **Network waterfall:** Use developer tools only on pages you are authorised to access. Record request timing, cache status, content type, and third-party domains without copying tokens, cookies, personal data, or credentials.
- **Latency measurement:** Use your operating system's connection diagnostics, your own router, or a reputable public measurement page. Do not probe private systems or interpret one round-trip value as geographic distance.
- **Model evaluation sheet:** Build a small fictional classification dataset with a held-out test set. Report confusion matrix, calibration bins, subgroup uncertainty, and examples where the model should abstain.
- **Compression experiment:** Compare original and compressed sizes for several non-sensitive files, including an already compressed image. Record algorithm, options, metadata overhead, and reproducibility.

## 6. Model-building prompts

Construct a simple physical model of a network using string and cups, but introduce a "router" (a person in the middle who must receive a message from one cup and pass it to another specific cup based on an address). How does adding more nodes and routers increase the complexity of ensuring the message reaches the correct destination?

Design a simple decision tree (a basic form of machine learning model) on paper to classify whether you should take an umbrella outside. What are the input features (e.g., is it cloudy? is the forecast calling for rain?), and what are the decision thresholds?

## 7. Self-explanation questions

Explain why a compressed file (like a .zip) cannot usually be compressed significantly a second time. Relate this to the concept of entropy.

Describe the difference between the Transport layer (TCP) and the Network layer (IP) in the internet protocol stack. Why are both necessary?

Explain the concept of "gradient descent" in neural network training using the analogy of a person trying to find the lowest point in a hilly landscape while blindfolded.

## 8. Transfer questions

How do the principles of error correction used in digital communication (adding redundancy) apply to human communication in a noisy environment (like a crowded room)?

The concept of caching (storing frequently accessed data closer to the processor to reduce latency) is fundamental in computer architecture. How is this concept applied in physical supply chains and logistics?

## 9. Suggested learning paths

To deepen your understanding of information theory, begin with Claude Shannon's original 1948 paper, "A Mathematical Theory of Communication." While mathematically dense, the introduction provides profound conceptual clarity.

For networking, explore the concept of packet switching versus circuit switching. Understand why the internet was designed around packet switching to ensure resilience.

To understand machine learning practically, explore introductory tutorials on building simple neural networks using Python libraries like TensorFlow or PyTorch. Focus on understanding the shape of the data as it passes through the layers.

## 10. Reasoning notes

Distinguish logical abstractions from physical implementation, specification from implementation, average from tail behavior, benchmark from deployment, and correlation from causal effect. Treat model outputs as fallible evidence. Avoid anthropomorphism in either direction: do not infer human-like consciousness from fluent behavior, and do not replace empirical capability analysis with the slogan “only pattern matching.” State the tested task, comparison, uncertainty, distribution, tools, and human context.

## Phase 9 review boundaries and validity limits

- Information-theory limits are asymptotic results for stated source and channel models; finite systems trade error, latency, energy, complexity, and cost.
- Protocol guarantees apply only under their specifications and assumptions; end-to-end service also depends on applications, networks, implementations, and failures.
- Machine-learning evaluation must address distribution shift, uncertainty, calibration, subgroup performance, robustness, privacy, security, misuse, monitoring, and human oversight.
- Model outputs are evidence requiring verification, not authoritative facts or proof of consciousness, intention, or understanding.

## 11. Sources

1. Shannon, C. E. *A Mathematical Theory of Communication*. https://doi.org/10.1002/j.1538-7305.1948.tb01338.x
2. Kurose, J. F., and Ross, K. W. *Computer Networking: A Top-Down Approach*. https://www.pearson.com/en-us/subject-catalog/p/computer-networking-a-top-down-approach/P200000013385
3. Goodfellow, I., Bengio, Y., and Courville, A. *Deep Learning*. http://www.deeplearningbook.org
4. Hellerstein, J. M., Stonebraker, M., and Hamilton, J. *Architecture of a Database System*. https://doi.org/10.1561/1900000002
5. National Institute of Standards and Technology. *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
6. National Institute of Standards and Technology. *AI RMF: Generative Artificial Intelligence Profile*. https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
7. Internet Engineering Task Force. *RFC 9293: Transmission Control Protocol*. https://www.rfc-editor.org/info/rfc9293/
