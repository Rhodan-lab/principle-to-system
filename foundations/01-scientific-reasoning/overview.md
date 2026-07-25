---
title: "Scientific reasoning, causality, and explanation"
slug: 01-scientific-reasoning
module: "Module 01"
domain: foundations
status: draft
prerequisites: []
connections: [02-measurement-uncertainty, 03-mathematical-models, 04-probability-statistics, 06-matter-quantum]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Scientific reasoning, causality, and explanation

## 1. The central questions

How do we reliably acquire knowledge about the natural world? What distinguishes a scientific explanation from a mere description or a post-hoc rationalisation? At the heart of scientific reasoning lie fundamental questions about causality, evidence, and the structure of theories. We must ask how observations can be used to infer underlying mechanisms, how we can distinguish causal relationships from mere correlations, and what it means for a hypothesis to be testable and falsifiable. Furthermore, we must consider the nature of scientific explanation itself: does explaining a phenomenon mean deducing it from universal laws, or does it require identifying the specific causal mechanisms that produced it?

## 2. Observable phenomena

The need for rigorous scientific reasoning arises from the complexity and ambiguity of observable phenomena. We observe regularities in nature—the sun rises every day, objects fall when dropped, specific diseases follow exposure to certain pathogens. However, we also observe exceptions, noise, and confounding factors. A patient may recover from an illness after taking a specific herb, but this single observation does not prove the herb caused the recovery; the patient might have recovered anyway, or another factor might be responsible. 

Similarly, we observe correlations that do not imply causation. For example, the sales of ice cream and the rate of drownings may both increase during the summer, but one does not cause the other; both are driven by a common cause (warmer weather). Scientific reasoning provides the tools to disentangle these complex observations, isolate variables, and identify the true causal structures underlying the phenomena we perceive.

## 3. Essential concepts

**Scientific Reasoning:** The systematic process of formulating hypotheses, designing experiments or observations to test them, and drawing conclusions based on empirical evidence. It involves both inductive reasoning (generalising from specific observations) and deductive reasoning (deriving specific predictions from general theories).

**Causality:** The relationship between cause and effect. In science, establishing causality requires more than just observing a correlation; it requires demonstrating that a change in one variable directly produces a change in another, often through a specific mechanism.

**Causal Inference:** The process of drawing conclusions about causal relationships from data. This often involves sophisticated statistical techniques and experimental designs to control for confounding variables.

**Falsifiability:** A concept introduced by Karl Popper, stating that for a hypothesis or theory to be considered scientific, it must be inherently disprovable. There must be some conceivable observation or experiment that could show the theory to be false.

**Experimental Design:** The careful planning of experiments to ensure that the results are valid, reliable, and capable of answering the research question. Key elements include control groups, randomisation, and blinding.

**Explanation vs. Description:** A description simply states *what* happens, while an explanation addresses *why* or *how* it happens. Scientific explanations often involve identifying the causal mechanisms or underlying laws that produce a phenomenon.

## 4. Mechanisms and causal chains

A causal mechanism is the step-by-step process by which a cause produces an effect. Identifying mechanisms is crucial for scientific explanation, as it moves beyond mere correlation to show exactly how a system operates. 

Consider the causal chain linking smoking to lung cancer. The initial cause (smoking) introduces carcinogens into the lungs. These carcinogens interact with the DNA in lung cells, causing mutations (the mechanism). Over time, accumulated mutations can lead to uncontrolled cell division, resulting in a tumour (the effect). 

Understanding this mechanism provides a much deeper explanation than simply observing a statistical correlation between smoking and cancer rates. It allows scientists to identify specific targets for intervention (e.g., developing drugs that block the effects of specific mutations) and to make more accurate predictions about the risks associated with different levels of exposure.

## 5. Important quantities

In the context of scientific reasoning and causal inference, several key quantities are used to measure the strength and reliability of evidence:

*   **P-value:** The probability of obtaining test results at least as extreme as the results actually observed, assuming that the null hypothesis is correct. A low p-value (typically < 0.05) suggests that the observed data are unlikely under the null hypothesis, leading to its rejection.
*   **Effect Size:** A quantitative measure of the magnitude of a phenomenon or the strength of a relationship between variables. Unlike p-values, which only indicate statistical significance, effect sizes provide information about practical significance.
*   **Confidence Interval:** A range of values that is likely to contain the true population parameter with a certain level of confidence (e.g., 95%). It provides a measure of the precision of an estimate.
*   **Correlation Coefficient ($r$):** A measure of the linear relationship between two variables, ranging from -1 (perfect negative correlation) to +1 (perfect positive correlation).

## 6. Mathematical models and equations

Mathematical models are essential tools for formalising scientific theories and making precise predictions. In causal inference, models are used to represent causal relationships and estimate the effects of interventions.

One common framework is the **Structural Causal Model (SCM)**, which uses directed acyclic graphs (DAGs) and structural equations to represent causal relationships. 

A simple linear structural equation might take the form:

$$ Y = \beta_0 + \beta_1 X + \epsilon $$

Where:
*   $Y$ is the outcome variable.
*   $X$ is the causal variable.
*   $\beta_0$ is the intercept.
*   $\beta_1$ is the causal effect of $X$ on $Y$.
*   $\epsilon$ represents unobserved error terms or confounding factors.

In experimental design, the **Average Treatment Effect (ATE)** is a key quantity, defined as the difference in the expected outcome between the treatment group and the control group:

$$ ATE = E[Y(1) - Y(0)] $$

Where:
*   $E[\cdot]$ denotes the expected value.
*   $Y(1)$ is the potential outcome if the subject receives the treatment.
*   $Y(0)$ is the potential outcome if the subject does not receive the treatment.

## 7. Definitions of symbols and units

*   $Y$: Outcome variable (units depend on the specific context, e.g., blood pressure in mmHg, crop yield in kg/ha).
*   $X$: Causal or treatment variable (often binary, 0 or 1, or continuous with specific units).
*   $\beta_1$: Causal effect coefficient (units are units of $Y$ per unit of $X$).
*   $\epsilon$: Error term (same units as $Y$).
*   $ATE$: Average Treatment Effect (same units as $Y$).

## 8. Assumptions and approximations

Scientific reasoning and causal inference rely on several critical assumptions:

*   **Causal Markov Condition:** A variable is independent of its non-descendants, conditional on its direct causes. This assumption is fundamental to using DAGs for causal inference.
*   **No Unmeasured Confounding:** In observational studies, estimating causal effects often requires assuming that all relevant confounding variables have been measured and controlled for. This is a strong assumption that is frequently violated in practice.
*   **Linearity:** Many statistical models assume linear relationships between variables. If the true relationship is non-linear, these models may produce biased estimates.
*   **Homogeneity of Treatment Effects:** The assumption that the treatment effect is the same for all individuals in the population. In reality, treatment effects often vary across different subgroups.

## 9. Spatial and temporal scales

Scientific reasoning applies across all spatial and temporal scales, from the subatomic realm of quantum mechanics to the cosmological scale of the universe. However, the specific methods and challenges vary depending on the scale.

At microscopic scales, causal mechanisms often involve the interactions of individual molecules or particles, requiring highly specialised equipment and statistical mechanics models. At macroscopic scales, such as ecology or climate science, causal relationships are often complex, non-linear, and subject to numerous confounding factors, making controlled experiments difficult or impossible.

Temporally, causal inference can be challenging when there are long delays between cause and effect, such as the decades-long latency period between asbestos exposure and mesothelioma. Longitudinal studies and sophisticated time-series analysis are required to establish causality in such cases.

## 10. Common misconceptions

*   **Correlation implies causation:** This is perhaps the most common fallacy in scientific reasoning. Just because two variables are correlated does not mean one causes the other; they may be linked by a common cause, or the correlation may be entirely spurious.
*   **Science proves theories to be true:** In reality, science cannot definitively prove a theory to be true; it can only fail to falsify it. Theories are always subject to revision or rejection in light of new evidence.
*   **A single experiment can definitively settle a scientific question:** Scientific consensus is built on the replication of results across multiple studies and independent research groups. A single anomalous result is rarely sufficient to overturn an established theory.
*   **Scientific models are exact representations of reality:** All models are simplifications of reality, based on assumptions and approximations. They are useful tools for understanding and predicting phenomena, but they are not perfect reflections of the natural world.

## 11. Connections to other modules

This module provides the foundational principles for all subsequent modules in the "Principle to System" repository. The concepts of causality, experimental design, and mathematical modelling are essential for understanding how scientific principles are discovered and how they are applied to engineer complex systems.

## 12. Sources

[1] Hempel, C. G., & Oppenheim, P. (1948). Studies in the Logic of Explanation. *Philosophy of Science*, 15(2), 135-175.
[2] Woodward, J. (2003). *Making Things Happen: A Theory of Causal Explanation*. Oxford University Press.
[3] Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press.
[4] Popper, K. (1959). *The Logic of Scientific Discovery*. Routledge.
[5] Craver, C. F. (2007). *Explaining the Brain: Mechanisms and the Mosaic Unity of Neuroscience*. Oxford University Press.
