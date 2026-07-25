---
title: "Exploring probability, statistics, and data interpretation"
slug: 04-probability-statistics-explore
module: "Module 04"
domain: foundations
status: reviewed
prerequisites: [01-scientific-reasoning, 03-mathematical-models]
connections: [05-computation-algorithms, 15-ecosystems-complex-systems, 19-software-ai]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# Exploring probability, statistics, and data interpretation

## 1. Observation prompts

- Observe a stream of ordinary events such as vehicle colors from a safe location, bus-arrival intervals from a timetable app, or sizes of similar leaves. Which source of variation is being sampled, and what population would you want to describe?
- Find a chart in the news. Identify the unit of observation, time window, denominator, missing values, and whether the vertical axis or color scale could change the impression.
- Compare a convenience sample, such as responses from one online community, with a probability sample. Which groups might be absent or overrepresented?
- Find a claim using “average.” Is it a mean, median, expected value, rate, or average across groups with different sizes?

## 2. Prediction questions

- A fair coin lands heads ten times. Under the independent fair-coin model, what is the probability of heads on the next flip? How would your answer change if fairness were uncertain?
- A rare manufacturing defect occurs in 1 of 10,000 items. An inspection system detects 99% of defective items and correctly clears 99% of non-defective items. After one alarm, is a defect more likely than a false alarm?
- Which sample mean is generally more stable: one based on 100 independent representative observations or one based on 10,000? Can the larger sample still be badly biased?
- A model has excellent ranking performance but systematically predicts probabilities that are too high. Is it well calibrated?

## 3. Worked reasoning examples

### Base rates and conditional probability

Let $D$ mean an item is defective and $+$ mean the inspection raises an alarm.

$$P(D)=0.0001,$$

$$P(+\mid D)=0.99,$$

$$P(+\mid D^c)=0.01.$$

The total alarm probability is

$$P(+)=0.99(0.0001)+0.01(0.9999)=0.010098.$$

Bayes’ theorem gives

$$P(D\mid +)=\frac{0.99(0.0001)}{0.010098}\approx0.0098.$$

So only about 0.98% of alarmed items are expected to be defective under this model. The phrase “99% accurate” would have been ambiguous; sensitivity, specificity, prevalence, and positive predictive value are different quantities.

### A confidence-interval simulation

Generate many independent samples from a distribution with known mean $\mu$. For each sample, construct a nominal 95% confidence interval using the same procedure. Count the fraction of intervals containing $\mu$. The long-run fraction should be near 95% when the assumptions and implementation are adequate. Individual intervals do not each contain “95% of the parameter.”

## 4. Thought experiments

- **Optional stopping:** Repeatedly test a hypothesis and stop when $p<0.05$. How does this differ from one pre-specified test, and why can the false-positive rate increase?
- **Simpson’s paradox:** Construct two subgroups in which method A has a higher success rate than B, while the combined data favor B because group sizes and difficulty differ.
- **Unknown coin:** After ten heads, compare two models: a known fair coin and a coin with unknown bias. Which model makes the eleventh outcome independent of previous data?
- **Perfect prediction, poor intervention:** Imagine a variable that predicts failure because it is an early symptom. Would changing that variable necessarily prevent the failure?

## 5. Household and browser-based explorations

- **Running proportion:** Simulate or perform 50 safe coin flips. Plot the running proportion of heads. Repeat the whole experiment and compare paths; convergence is not smooth or guaranteed at every finite sample size.
- **Sampling bias:** Ask the same neutral question using two different recruitment methods. Do not collect sensitive personal information. Compare who had an opportunity to respond.
- **Central Limit Theorem:** In a spreadsheet, generate many groups of independent uniform random values. Calculate one mean per group and plot the distribution of means for group sizes 2, 10, and 30. Compare spread and shape.
- **Calibration:** Create synthetic forecasts such as 0.1, 0.3, 0.7, and 0.9 with simulated outcomes. Group forecasts into bins and compare stated probability with observed frequency.
- **Visualization audit:** Replot the same data with a truncated and a zero-based axis. Which representation answers the intended question more honestly?

## 6. Model-building prompts

- **Queue model:** Specify an arrival process, service-time distribution, number of servers, capacity, and queue discipline. Decide whether mean wait or tail probability matters most.
- **Plant-growth DAG:** Include sunlight, water, soil, variety, temperature, pests, and measured height. Mark common causes, mediators, and variables that should not be adjusted for without justification.
- **Reliability model:** Define component failure probabilities and whether failures are independent. Compare series and parallel architectures.
- **Survey estimator:** Define inclusion probabilities and weights for a stratified sample. What happens if non-response differs by stratum?

## 7. Self-explanation questions

- What is the difference between a parameter, statistic, estimator, and estimate?
- Why can a huge convenience sample be less useful than a smaller probability sample?
- What does a p-value condition on, and what does it not tell you?
- How should a frequentist 95% confidence interval be interpreted?
- What is the difference between discrimination and calibration?
- Why can regression adjustment increase bias when the wrong variable is controlled?

## 8. Transfer questions

- How do statistical process-control ideas transfer to server latency or sensor health monitoring?
- Why does a highly predictable aggregate not imply predictable individual events?
- How should a model be reevaluated after a sensor, policy, population, or data-collection rule changes?
- How can probability estimates be combined with costs and constraints to select an action?
- Why might the same false-positive rate produce different positive predictive values in different populations?

## 9. Suggested learning paths

- **Probability:** Conditional probability, independence, random variables, expectation, variance, and limit theorems.
- **Statistical inference:** Sampling, estimators, intervals, tests, regression, diagnostics, and resampling.
- **Bayesian inference:** Priors, likelihoods, posteriors, predictive checks, and decision theory.
- **Causal inference:** Randomization, potential outcomes, DAGs, identification, and sensitivity analysis.
- **Statistical engineering:** Designed experiments, measurement systems, reliability, and process control.

## 10. Reasoning notes

When interpreting a statistical result, ask:

1. What is the target population, process, parameter, or decision?
2. How were observations sampled, assigned, measured, and excluded?
3. Which observations are dependent or clustered?
4. Which model and assumptions generated the estimate and uncertainty?
5. What is the effect magnitude, not only statistical significance?
6. Were analyses and stopping rules specified before viewing outcomes?
7. How do missing data, multiple comparisons, and selection affect the result?
8. Is the output calibrated and evaluated on genuinely new data?
9. Is the conclusion predictive, descriptive, or causal?
10. What alternative analysis would most challenge it?

Formal probability does not replace judgment. It makes assumptions and consequences explicit enough to criticize, test, and improve.
