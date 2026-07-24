---
title: "Probability, Statistics, and Data Interpretation"
slug: "04-probability-statistics"
module: "Module 04"
domain: "foundations"
status: draft
prerequisites: ["01-scientific-reasoning", "03-mathematical-models"]
connections: ["05-information-theory", "06-systems-thinking"]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Probability, Statistics, and Data Interpretation

## 1. The central questions

How can we quantify uncertainty and make rational decisions when information is incomplete? How do we distinguish meaningful patterns from random noise in observational data? What is the mathematical foundation for inferring the properties of a vast population from a small, representative sample? Furthermore, how can we rigorously separate correlation—variables moving together—from causation, where one variable actively influences another?

## 2. Observable phenomena

In the physical and social worlds, deterministic predictability is rare. When a coin is flipped, the exact mechanics of its trajectory are too complex to measure in real-time, resulting in an outcome that appears random. In manufacturing, identical machines produce parts with slight variations in dimension. In medicine, patients with the same diagnosis respond differently to identical treatments. 

These phenomena exhibit variability. However, when observed in large aggregates, this variability often follows stable, predictable patterns. For instance, while the lifespan of a single lightbulb is highly uncertain, the average lifespan of ten thousand lightbulbs of the same model is highly predictable. This emergence of macro-level predictability from micro-level randomness is the phenomenon that probability and statistics seek to model and interpret.

## 3. Essential concepts

**Probability** is the mathematical language of uncertainty. It provides a framework for assigning numerical values between 0 (impossible) and 1 (certain) to the likelihood of events. It operates deductively, moving from a known model of the world to the expected outcomes.

**Statistics** is the inverse process. It operates inductively, moving from observed data back to the underlying model of the world. It involves collecting, analysing, and interpreting data to estimate parameters, test hypotheses, and quantify the confidence in those estimates.

**Random Variables** are mathematical functions that map the outcomes of a random process to numerical values. They can be discrete (taking specific, separate values, like the roll of a die) or continuous (taking any value within a range, like the exact height of a person).

**Probability Distributions** describe how the total probability of 1 is distributed across all possible values of a random variable. 

**Statistical Inference** is the process of drawing conclusions about a population based on a sample. It relies on the assumption that the sample is representative of the population.

**Correlation vs. Causation** is a fundamental distinction. Correlation indicates that two variables change together, but it does not imply that one causes the other. Causation requires a mechanism by which one variable directly influences the other, often established through controlled experiments or causal inference techniques.

## 4. Mechanisms and causal chains

The mechanism by which probability operates in the physical world often stems from sensitive dependence on initial conditions (chaos) or fundamental quantum indeterminacy. In macroscopic systems, what we model as "randomness" is usually a lack of complete information about the system's state.

In statistical inference, the causal chain begins with a **Population**, which possesses some true, unknown parameter (e.g., the true average height of all adults). A **Sampling Mechanism** selects a subset of this population. This mechanism must be random to avoid bias. The **Sample** yields a statistic (e.g., the average height of the sampled adults). Through the **Central Limit Theorem**, the distribution of this sample statistic is known, allowing us to construct a **Confidence Interval** or perform a **Hypothesis Test** to infer the true population parameter.

When interpreting data causally, the mechanism is often represented by a **Causal Diagram** (Directed Acyclic Graph). If variable $X$ causes variable $Y$, there is a directed path from $X$ to $Y$. Confounding occurs when a third variable $Z$ causes both $X$ and $Y$, creating a spurious correlation between them if $Z$ is not controlled for.

## 5. Important quantities

| Quantity | Symbol | Definition | SI Unit |
| :--- | :--- | :--- | :--- |
| Probability | $P(A)$ | The likelihood of event $A$ occurring. | Dimensionless (0 to 1) |
| Expected Value (Mean) | $\mu$ or $E[X]$ | The long-run average value of a random variable $X$. | Same as $X$ |
| Variance | $\sigma^2$ or $Var(X)$ | The expected squared deviation of a random variable from its mean. | $(\text{Unit of } X)^2$ |
| Standard Deviation | $\sigma$ | The square root of the variance, representing the typical spread of values. | Same as $X$ |
| Covariance | $Cov(X,Y)$ | A measure of the joint variability of two random variables. | $(\text{Unit of } X) \times (\text{Unit of } Y)$ |
| Correlation Coefficient | $\rho$ | A normalized measure of linear dependence between two variables. | Dimensionless (-1 to 1) |
| Sample Size | $n$ | The number of observations in a sample. | Dimensionless (integer) |
| p-value | $p$ | The probability of observing data as extreme as the sample, assuming the null hypothesis is true. | Dimensionless (0 to 1) |

## 6. Mathematical models and equations

### Kolmogorov's Axioms of Probability
The foundation of probability theory rests on three axioms for a sample space $\Omega$ and events $A$:
1. Non-negativity: $P(A) \ge 0$
2. Normalization: $P(\Omega) = 1$
3. Additivity for mutually exclusive events: If $A_1, A_2, \dots$ are disjoint, then $P(\bigcup_{i=1}^\infty A_i) = \sum_{i=1}^\infty P(A_i)$

### Bayes' Theorem
Bayes' theorem updates the probability of a hypothesis $H$ given new evidence $E$:
$$P(H|E) = \frac{P(E|H)P(H)}{P(E)}$$
Where $P(H|E)$ is the posterior probability, $P(E|H)$ is the likelihood, $P(H)$ is the prior probability, and $P(E)$ is the marginal probability of the evidence.

### The Normal (Gaussian) Distribution
The probability density function for a continuous random variable $X$ that is normally distributed with mean $\mu$ and variance $\sigma^2$:
$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}$$

### The Central Limit Theorem (CLT)
Let $X_1, X_2, \dots, X_n$ be independent and identically distributed random variables with mean $\mu$ and variance $\sigma^2$. As $n \to \infty$, the distribution of the sample mean $\bar{X} = \frac{1}{n}\sum_{i=1}^n X_i$ approaches a normal distribution:
$$\bar{X} \sim \mathcal{N}\left(\mu, \frac{\sigma^2}{n}\right)$$

### Linear Regression
A model assuming a linear relationship between an independent variable $X$ and a dependent variable $Y$, with an error term $\epsilon$:
$$Y = \beta_0 + \beta_1 X + \epsilon$$
Where $\beta_0$ is the intercept and $\beta_1$ is the slope.

## 7. Definitions of symbols and units

- $P(A)$: Probability of event $A$ (dimensionless, $0 \le P(A) \le 1$).
- $\Omega$: The sample space, the set of all possible outcomes.
- $H$: Hypothesis being tested or evaluated.
- $E$: Evidence or observed data.
- $\mu$: Population mean (units depend on the variable).
- $\sigma^2$: Population variance (units squared).
- $\sigma$: Population standard deviation (units depend on the variable).
- $n$: Sample size (dimensionless integer).
- $\bar{X}$: Sample mean (units depend on the variable).
- $\beta_0, \beta_1$: Regression coefficients (units depend on $Y$ and $X$).
- $\epsilon$: Error term or residual in a model (units depend on $Y$).

## 8. Assumptions and approximations

- **Independence:** Many statistical models (like the basic CLT or simple linear regression) assume that individual observations are independent of one another. In reality, data points (e.g., time series data or spatial data) are often correlated.
- **Identical Distribution:** The assumption that all data points are drawn from the same underlying probability distribution. This is often violated if the system generating the data changes over time.
- **Normality:** Hypothesis tests (like the t-test) often assume the underlying population is normally distributed. While the CLT helps for large samples, small samples from highly skewed distributions can invalidate these tests.
- **Linearity:** Linear regression assumes the relationship between variables is a straight line. If the true relationship is non-linear, the model will yield biased predictions.
- **No Unmeasured Confounders:** Causal inference from observational data heavily relies on the assumption that all variables influencing both the treatment and the outcome have been measured and controlled for.

## 9. Spatial and temporal scales

Probability and statistics are scale-independent mathematical frameworks, but their application varies drastically across scales:
- **Microscopic/Quantum Scale:** Probability is fundamental. The position of an electron is not deterministic but described by a probability density function (wavefunction).
- **Human Scale:** Statistics are used to understand populations, from the efficacy of a drug in a clinical trial (months/years, thousands of people) to the quality control of manufactured goods (hours/days, millions of parts).
- **Macroscopic/Cosmological Scale:** Statistical mechanics uses probability to explain the thermodynamic behavior of large ensembles of particles (e.g., gases), bridging the microscopic laws of physics to macroscopic observables like temperature and pressure.

## 10. Common misconceptions

- **The Gambler's Fallacy:** The belief that if an independent event occurs more frequently than normal in the past, it is less likely to occur in the future (e.g., "The coin has landed on heads five times, so tails is due"). Independent events have no memory.
- **Confusing Correlation with Causation:** Assuming that because ice cream sales and shark attacks increase together, one causes the other. Both are caused by a confounding variable: summer weather.
- **Misinterpreting the p-value:** The p-value is *not* the probability that the null hypothesis is true. It is the probability of observing the data, or something more extreme, *assuming* the null hypothesis is true.
- **The Law of Averages:** The false belief that a small sample must reflect the population distribution. The Law of Large Numbers only guarantees convergence as the sample size approaches infinity.

## 11. Connections to other modules

- **01-scientific-reasoning:** Statistics provides the formal mathematical tools for hypothesis testing and evaluating evidence, which are central to the scientific method.
- **03-mathematical-models:** Probability distributions are mathematical models of uncertainty. Regression is a method for fitting mathematical models to data.
- **05-information-theory:** Information theory is built entirely on probability. Entropy, a key concept in information theory, is a measure of the unpredictability of a random variable.
- **06-systems-thinking:** Statistical mechanics and complex systems rely on probabilistic models to understand how macroscopic properties emerge from the interactions of many microscopic components.

## 12. Sources

1. Blitzstein, J. K., & Hwang, J. (2019). *Introduction to Probability* (2nd ed.). CRC Press. [https://stat110.hsites.harvard.edu/](https://stat110.hsites.harvard.edu/)
2. Wasserman, L. (2004). *All of Statistics: A Concise Course in Statistical Inference*. Springer. [https://link.springer.com/book/10.1007/978-0-387-21736-9](https://link.springer.com/book/10.1007/978-0-387-21736-9)
3. Pearl, J., & Mackenzie, D. (2018). *The Book of Why: The New Science of Cause and Effect*. Basic Books.
4. Tufte, E. R. (2001). *The Visual Display of Quantitative Information* (2nd ed.). Graphics Press.
