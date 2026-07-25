---
title: "Exploring scientific reasoning and causality"
slug: 01-scientific-reasoning-explore
module: "Module 01"
domain: foundations
status: reviewed
prerequisites: []
connections: [02-measurement-uncertainty, 03-mathematical-models, 04-probability-statistics, 06-matter-quantum]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# Exploring scientific reasoning and causality

## 1. Observation prompts

- **Claim-language audit:** Examine several science headlines. Classify phrases such as “associated with,” “predicts,” “increases,” and “causes.” Does the wording match the study design described in the article?
- **Everyday confounding:** Choose a familiar outcome such as travel time, plant growth, or classroom temperature. List variables that might influence both a suspected cause and the outcome.
- **Measurement-chain map:** Choose a thermometer, scale, bicycle brake, or other safe system. Trace how an input becomes an observation or output, and mark where information could be lost or distorted.
- **Alternative explanations:** For one observation, write at least three explanations that make different predictions. Identify an observation that would discriminate among them.

## 2. Prediction questions

- A study finds that households with more books tend to have children with higher school performance. What interventions could produce the association besides purchasing books?
- A voluntary online survey reports that a study method improves grades. How could self-selection, prior achievement, or incomplete follow-up affect the result?
- A theory correctly predicts one observation. What competing theories might make the same prediction, and what additional test could distinguish them?
- An experiment finds a small average effect. What information would you need before applying the result to a different population or setting?

## 3. Worked reasoning examples

### Example: a common-cause explanation

**Observation:** Larger towns have more public parks and more bus routes.

**Premature causal claim:** Adding bus routes creates parks.

**Alternative model:** Population size and municipal budget influence both the number of routes and the number of parks.

A simple DAG is

```text
population and budget → bus routes
population and budget → public parks
```

Comparing towns only by raw route and park counts mixes the variables of interest with town size. A better analysis might compare per-capita values, include relevant covariates, study a policy change, or use a design that creates a defensible comparison group. Even then, the target causal question must be stated precisely.

### Example: prediction is not intervention

A model may predict exam performance from previous scores, attendance, and study time. High predictive accuracy does not show that forcing every student to increase one measured variable will produce the model’s predicted change. The predictor may be a marker of other conditions, the intervention may be defined poorly, or the relationship may differ outside the observed range.

## 4. Thought experiments

- **Ethically constrained experiment:** Design the strongest ethical study you can for testing whether a new teaching technique improves understanding. Consider assignment, consent, comparison groups, outcome measurement, unequal access, and what should happen if early evidence suggests harm or clear benefit.
- **Counterfactual ambiguity:** Consider a historical technology such as the printing press. List several plausible pathways through which it affected society. Which counterfactual claims can be tested with historical evidence, and which remain too underdetermined?
- **Same data, different graphs:** Draw two causal graphs that could both generate a correlation between exercise and well-being. What additional measurement or design would distinguish them?

## 5. Household and browser-based explorations

- **Neutral spurious correlations:** Find two unrelated time series that both trend upward, such as the number of mobile subscriptions and the number of published digital photographs. Explain how common trends, changing population size, or time itself can create a high correlation.
- **Simulating confounding:** In a spreadsheet, generate a variable $A$. Create $B=A+\epsilon_B$ and $C=A+\epsilon_C$ using independent noise terms. Calculate the correlation between $B$ and $C$, then examine the correlation after accounting for $A$.
- **Reproducibility check:** Exchange a small spreadsheet analysis with a classmate using the same input data. Record every formula and processing step needed for both of you to obtain the same result.
- **Replication design:** Propose how a new group could collect fresh data to address the same question while avoiding dependence on the original dataset.

## 6. Model-building prompts

- **Draw a DAG:** Choose a manageable question about plant growth, traffic delay, or study habits. Include exposure, outcome, common causes, mediators, and possible selection variables. Do not include a feedback loop in one static DAG; represent time explicitly if feedback matters.
- **Specify an estimand:** Rewrite “Does coffee improve concentration?” as a precise comparison including population, amount, timing, comparator, outcome measure, and time horizon.
- **Competing mechanisms:** Build two mechanism diagrams for the same observation and list one expected observation unique to each model.
- **Sensitivity map:** Identify which unmeasured variable would most threaten a proposed conclusion and describe how strong its relationships would need to be to change the conclusion.

## 7. Self-explanation questions

- What is the difference between association, prediction, and a causal effect?
- Why can random assignment support a causal comparison, and what problems can remain after assignment?
- Why is falsifiability useful but insufficient as a complete definition of science?
- How do reproducibility and replicability differ?
- Why is a mechanism helpful for explanation but not a substitute for a valid comparison?

## 8. Transfer questions

- How should a public-policy team distinguish a forecasting model from a model of policy intervention?
- How could causal assumptions improve the design of an AI decision-support system?
- Why might an effect estimated in one school, ecosystem, or machine fail to transfer to another?
- How can measurement error create, weaken, or reverse an apparent causal relationship?

## 9. Suggested learning paths

- **Evidence and explanation:** Study competing accounts of scientific explanation, severe testing, mechanisms, and theory comparison.
- **Experimental and observational design:** Learn randomization, blocking, sampling, natural experiments, longitudinal studies, and sensitivity analysis.
- **Formal causality:** Study potential outcomes, causal DAGs, identification, and intervention notation.
- **Open and reproducible research:** Learn versioned analysis, transparent reporting, computational reproducibility, and independent replication.

## 10. Reasoning notes

When evaluating a scientific claim, ask:

1. What exactly is the population, intervention or exposure, comparator, outcome, and time horizon?
2. How were units selected, measured, included, and followed?
3. What alternative explanations are compatible with the data?
4. Which assumptions convert an association into a causal estimate?
5. What is the effect magnitude and uncertainty, not merely the p-value?
6. Can the computation be reproduced from the data and methods?
7. Has the question been examined with new data, different methods, or independent investigators?
8. What evidence would reduce confidence in the claim?

Scientific skepticism is not automatic rejection. It is the disciplined practice of matching confidence to evidence, assumptions, and uncertainty.
