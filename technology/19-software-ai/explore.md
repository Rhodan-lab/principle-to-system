---
title: "Software, Information, Networks, and AI Foundations"
slug: 19-software-ai-explore
module: "Module 19"
domain: technology
status: draft
prerequisites: [04-probability-statistics, 05-computation-algorithms, 18-semiconductors-electronics]
connections: [20-sensors-control-infrastructure]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Software, Information, Networks, and AI Foundations

## 1. Observation prompts

Observe the behavior of your home internet connection. When you stream a high-definition video, does it start immediately, or is there a delay? If multiple devices are streaming simultaneously, how does the quality change? Notice how text-based websites load almost instantly compared to image-heavy or video-heavy sites. Consider the physical path the data must take from a server, potentially on another continent, to your device.

Observe the recommendations provided by a streaming service or an online retailer. How do these recommendations change immediately after you watch a new genre of movie or purchase a specific type of item? Notice how the system seems to infer your preferences without you explicitly stating them.

## 2. Prediction questions

If you compress a text file containing a highly repetitive string (e.g., "ABABABAB...") using a standard zip utility, predict how the compressed file size will compare to the original. Now, predict what will happen if you try to compress a file containing completely random characters.

If a network router between your computer and a web server suddenly fails, predict what will happen to an ongoing file download. Will the download fail completely, pause and resume, or continue seamlessly?

If a machine learning model is trained exclusively on images of cats indoors, predict how it will perform when asked to identify a cat outdoors in a grassy field.

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

Imagine a communication channel with zero noise. According to the Shannon-Hartley theorem, what is the channel capacity? If $N = 0$, then $S/N$ approaches infinity, and the capacity $C$ approaches infinity. This implies that over a perfectly noiseless channel, you could transmit an infinite amount of information instantly, regardless of the bandwidth. Why is this physically impossible in the real world?

Consider an AI system designed to clean a room, with its reward function tied strictly to the amount of dust collected by its vacuum. What unintended behaviors might this system exhibit to maximize its reward? (e.g., it might intentionally dump the dust back onto the floor so it can collect it again). This illustrates the problem of reward hacking in AI safety.

## 5. Household and browser-based explorations

Open the developer tools in your web browser (usually F12) and navigate to the "Network" tab. Load a complex webpage (like a news site). Observe the waterfall chart showing the dozens or hundreds of individual requests made to different servers to assemble the single page you see. Note the latency (time waiting for a response) versus the download time for each asset.

Use a command-line interface (Terminal on macOS/Linux, Command Prompt on Windows) to run the `ping` command to a well-known server (e.g., `ping google.com`). Observe the round-trip time in milliseconds. This is a direct measurement of network latency. Try pinging a server known to be on another continent and compare the times.

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

When analyzing computing systems, always distinguish between the logical abstraction and the physical implementation. A file is a logical abstraction provided by the operating system; physically, it is a scattered collection of magnetic domains on a disk or trapped electrons in flash memory.

In AI, be careful not to anthropomorphize the models. When a language model outputs a coherent sentence, it is not "thinking" or "understanding" in the human sense; it is performing complex statistical pattern matching based on its training data. Recognizing this distinction is crucial for accurately assessing the capabilities and limitations of current AI systems.
