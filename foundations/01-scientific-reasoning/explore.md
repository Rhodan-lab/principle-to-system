---
title: "Exploring scientific reasoning and causality"
slug: 01-scientific-reasoning-explore
module: "Module 01"
domain: foundations
status: draft
prerequisites: []
connections: [02-measurement-uncertainty, 03-mathematical-models, 04-probability-statistics, 06-matter-quantum]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Exploring scientific reasoning and causality

## 1. Observation prompts

*   **The Correlation Hunt:** Spend a day observing news headlines or social media posts that claim a scientific finding. How many of these claims are based on observational correlations versus controlled experiments? Look for phrases like "linked to," "associated with," or "may cause."
*   **Everyday Confounding:** Observe a common phenomenon in your daily life, such as traffic congestion or your own energy levels. Identify at least three variables that might influence this phenomenon. Can you identify a potential confounding variable that affects both a suspected cause and the observed effect?
*   **Mechanism Mapping:** Choose a simple mechanical device (like a bicycle or a mechanical clock) or a biological process (like a plant growing towards light). Trace the causal chain from the initial input to the final output. What are the intermediate steps?

## 2. Prediction questions

*   If a new study finds a strong positive correlation between the number of books in a household and the academic performance of the children living there, does this mean that simply buying more books will improve a child's grades? What other factors might explain this correlation?
*   Suppose a pharmaceutical company develops a new drug for a disease and tests it only on patients who volunteer for the trial. If the drug shows a positive effect, can we confidently predict it will have the same effect on the general population? Why or why not?
*   If a scientific theory makes a prediction that is subsequently confirmed by observation, does this prove the theory is true? What if the theory makes a prediction that is contradicted by observation?

## 3. Worked reasoning examples

**Example: The Case of the Spurious Correlation**

*   **Observation:** A researcher notices a strong positive correlation between the number of storks nesting in a village and the number of human babies born in that village over a ten-year period.
*   **Hypothesis 1 (Causal):** Storks deliver babies. (This is a known myth, but we treat it as a hypothesis for the sake of the example).
*   **Hypothesis 2 (Confounding):** There is a common cause influencing both variables.
*   **Reasoning:** We must look for a confounding variable. Consider the size of the village. A larger village will have more houses (providing more nesting sites for storks) and a larger human population (resulting in more births).
*   **Conclusion:** The correlation is spurious. The size of the village is a confounding variable that causes both an increase in storks and an increase in babies. Controlling for village size would likely eliminate the correlation between storks and babies.

## 4. Thought experiments

*   **The Perfect Experiment:** Imagine you have unlimited resources and the ability to control any variable without ethical constraints. Design an experiment to definitively determine whether a specific diet causes a specific health outcome. What variables would you control? How would you assign participants? What would be the limitations of even this "perfect" experiment?
*   **The Counterfactual World:** Consider a major historical event (e.g., the invention of the printing press). Construct a counterfactual scenario: what would the world look like today if that event had not occurred? What causal chains would have been broken or altered? How does this exercise highlight the difficulty of establishing causality in complex historical or social systems?

## 5. Household and browser-based explorations

*   **Spurious Correlations Website:** Visit Tyler Vigen's "Spurious Correlations" website (or search for similar examples online). Examine the graphs showing strong correlations between completely unrelated variables (e.g., US spending on science and suicides by hanging). Use these examples to practice explaining why correlation does not equal causation.
*   **Simulating Confounding:** Use a spreadsheet program (like Excel or Google Sheets) to generate three columns of random numbers: A, B, and C. Make column A the "confounder." Create column B by adding column A to some random noise. Create column C by adding column A to some different random noise. Now, calculate the correlation between B and C. You will likely find a correlation, even though B does not cause C and C does not cause B.

## 6. Model-building prompts

*   **Draw a DAG:** Choose a complex social or biological issue (e.g., obesity, climate change, economic inequality). Draw a Directed Acyclic Graph (DAG) representing the potential causal relationships between at least five key variables. Identify any potential confounding variables or feedback loops.
*   **Formalise a Hypothesis:** Take a common belief (e.g., "drinking coffee improves concentration") and formalise it into a testable hypothesis. Define the variables clearly, specify the expected direction of the effect, and outline the conditions under which the hypothesis could be falsified.

## 7. Self-explanation questions

*   Explain the difference between a necessary cause and a sufficient cause, providing an example of each.
*   Why is randomisation considered the "gold standard" in experimental design? What specific problem does it solve?
*   In your own words, explain Karl Popper's concept of falsifiability. Why did he argue that it is the defining characteristic of science?

## 8. Transfer questions

*   How can the principles of causal inference be applied to improve the design of public policies or social interventions?
*   In the field of artificial intelligence, how might an understanding of causality improve the robustness and interpretability of machine learning models?
*   How do the challenges of establishing causality in medicine differ from the challenges in economics or sociology?

## 9. Suggested learning paths

*   **Path 1: The Philosophy of Science:** Dive deeper into the epistemological foundations of science. Read works by Karl Popper, Thomas Kuhn, and Imre Lakatos to understand how scientific theories are developed, tested, and sometimes overthrown.
*   **Path 2: The Mathematics of Causality:** Explore the formal frameworks for causal inference. Study Judea Pearl's work on Directed Acyclic Graphs (DAGs) and the *do*-calculus, or Donald Rubin's potential outcomes framework.
*   **Path 3: Experimental Design in Practice:** Learn how to design and analyse experiments in specific fields, such as clinical trials in medicine or A/B testing in software development.

## 10. Reasoning notes

When engaging with scientific claims, always ask:

1.  What is the specific causal claim being made?
2.  What is the evidence supporting this claim? Is it observational or experimental?
3.  Have potential confounding variables been adequately controlled for?
4.  Is the proposed mechanism plausible?
5.  Is the hypothesis falsifiable? What evidence would prove it wrong?

Remember that scientific knowledge is always provisional and subject to revision in light of new evidence. A healthy skepticism, combined with a rigorous understanding of causal inference, is the best defense against misinformation and flawed reasoning.
