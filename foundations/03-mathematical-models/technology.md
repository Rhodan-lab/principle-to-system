---
title: "Engineering with mathematical models"
slug: 03-mathematical-models-technology
module: "Module 03"
domain: foundations
status: reviewed
prerequisites: [01-scientific-reasoning]
connections: [04-probability-statistics, 05-computation-algorithms, 06-matter-quantum, 08-energy-thermodynamics, 09-motion-forces, 10-electricity-magnetism, 11-waves-signals, 12-fluids-materials]
last_reviewed: 2026-07-25
content_license: CC-BY-4.0
---

# Engineering with mathematical models

## 1. Scientific principles used

Engineering models combine conservation laws, constitutive relations, geometry, probability, control, and empirical data. They translate a design question into quantities and constraints that can be analyzed before, during, and after physical testing. Dimensional analysis, similarity, linearization, sensitivity analysis, optimization, and uncertainty quantification help determine which effects dominate and which approximations are acceptable.

A model is trustworthy only relative to an intended use. A model adequate for choosing an early concept may be inadequate for certification, safety limits, or operation outside the tested range.

## 2. The engineering problem

Engineers must make decisions before every detail of a system is known. Building and testing every candidate can be slow, expensive, wasteful, or impractical. The challenge is to create a model that is simple enough to solve, detailed enough for the decision, connected to evidence, and explicit about uncertainty.

The model must answer a specific question such as maximum stress, cooling time, control stability, energy use, or probability of failure. “Model the entire system accurately” is not a usable requirement.

## 3. Main components

- **System boundary:** Defines what is included, excluded, and treated as an external input.
- **State variables:** Describe the evolving condition of the system.
- **Parameters and properties:** Represent geometry, materials, rates, and other quantities treated as fixed during a run.
- **Governing equations:** Encode conservation, force balance, transport, reaction, or empirical relationships.
- **Initial and boundary conditions:** Specify starting state and interaction with surroundings.
- **Observation model:** Connects internal state to quantities that sensors or tests can measure.
- **Uncertainty model:** Represents uncertain inputs, parameters, model discrepancy, and measurement effects.
- **Solver and implementation:** Produce analytical or numerical results.
- **Calibration, verification, and validation evidence:** Connect implementation and predictions to reference problems and physical observations.

## 4. How the components interact

For a structural component, loads and supports define boundary conditions. Geometry and material models determine stiffness. The governing equations relate displacement, strain, stress, and force balance. A solver approximates the state, and an observation model predicts strain-gauge or displacement measurements. Test data calibrate uncertain parameters and evaluate whether the model is adequate for the relevant load range.

```text
design question
→ system boundary and quantities
→ governing relationships
→ parameters and conditions
→ solution
→ predicted observables
→ comparison with tests
→ revised model or design decision
```

## 5. Matter, energy, force, or information flow

A mathematical model represents flows rather than replacing them. Conservation equations track matter, energy, momentum, charge, or information across a boundary. Constitutive relations describe how a material or component responds. Inputs and measurements carry information into calibration and validation, while model outputs carry information into design decisions.

A useful model preserves the balances and constraints essential to the decision. For example, a thermal model that predicts temperature without accounting for energy storage and transfer may fit one dataset but fail when geometry or operating conditions change.

## 6. System architecture

Large models are usually modular. An aircraft, building, power system, or manufacturing process may contain structural, thermal, fluid, electrical, control, and economic submodels. Coupling must specify which quantities cross subsystem boundaries, their units, update frequency, and whether feedback is solved simultaneously or sequentially.

Hierarchical models can use different fidelity at different stages:

- reduced-order models for screening and control;
- medium-fidelity models for trade studies;
- high-fidelity models for local mechanisms or final evidence;
- test data and monitoring models for operation.

The highest-fidelity model is not automatically the system authority. Model governance records purpose, version, data, assumptions, validation domain, and responsible reviewers.

## 7. Design constraints

- **Purpose and decision consequence:** Higher-consequence decisions require stronger evidence and margins.
- **Data availability:** Parameters may be poorly measured or non-identifiable.
- **Computational budget:** Resolution, model dimension, and number of scenarios compete for resources.
- **Coupling and stiffness:** Fast and slow processes can make equations difficult to solve reliably.
- **Uncertainty and variability:** Material properties, loads, environments, and human use may vary.
- **Extrapolation:** Predictions outside the calibration and validation domain carry greater model-form risk.
- **Standards and regulation:** Required load cases, factors, tests, and documentation may constrain acceptable models.

## 8. Performance and efficiency

Model performance should be evaluated using quantities tied to the intended decision:

- error or residuals for relevant outputs;
- conservation and consistency checks;
- parameter sensitivity and identifiability;
- uncertainty interval calibration;
- prediction on data not used for calibration;
- robustness across mesh, time step, solver, and model alternatives;
- computational cost and turnaround time.

A closer fit can result from overfitting or parameter compensation. It should not be used by itself to reduce safety margins. Margins, factors, and acceptance criteria require evidence, standards, uncertainty analysis, and engineering judgment.

## 9. Reliability and failure modes

- **Wrong boundary:** Important interactions are excluded or double-counted.
- **Incorrect constitutive relation:** A material or component model is used outside its range.
- **Parameter compensation:** Incorrect parameters cancel one another inside calibration data but fail elsewhere.
- **Non-identifiability:** Multiple parameter sets produce nearly identical outputs.
- **Numerical artifact:** Mesh, time step, solver tolerance, or implementation changes the result materially.
- **Extrapolation:** A fitted relationship is applied beyond observed conditions.
- **Coupling error:** Submodels exchange inconsistent units, timing, or state definitions.
- **Decision mismatch:** The validated output is not the quantity used in the final decision.

## 10. Safety principles

- State intended use, prohibited use, and validation domain.
- Preserve physical conservation and dimensional checks where applicable.
- Separate calibration data from validation evidence when possible.
- Compare multiple model forms for high-consequence predictions.
- Use sensitivity and uncertainty analysis to identify fragile conclusions.
- Retain appropriate engineering margins rather than treating model precision as certainty.
- Require physical tests or monitoring where model evidence alone is insufficient.
- Track model version, parameter source, solver configuration, and reviewer decisions.

## 11. Environmental and lifecycle considerations

Models can reduce physical prototypes, material waste, operating energy, and maintenance burden, but computation and data collection also consume resources. Lifecycle models should include manufacture, use, degradation, repair, replacement, and end-of-life rather than optimizing only initial performance.

A model may become invalid as materials age, software changes, operating conditions shift, or sensors drift. Lifecycle governance therefore includes revalidation, change control, archival of old versions, and criteria for retiring a model.

## 12. Connections to other technologies

- **Computer-aided engineering:** Implements structural, thermal, electromagnetic, and fluid models.
- **Digital twins:** Combine models with observations to estimate current state and forecast limited future behavior; they require continuous calibration and validation.
- **Control systems:** Reduced-order state-space models support estimation and feedback design.
- **Optimization:** Searches design variables subject to model equations and constraints.
- **Surrogate models:** Approximate expensive simulations but inherit the training domain and uncertainty of the source model.
- **Reliability engineering:** Combines physical models with probability distributions and failure criteria.

## 13. Sources

1. Meerschaert, M. M. (2013). *Mathematical Modeling* (4th ed.). Academic Press. https://www.sciencedirect.com/book/monograph/9780123869128/mathematical-modeling
2. Giordano, F. R., Fox, W. P., & Horton, S. B. (2013). *A First Course in Mathematical Modeling* (5th ed.). Cengage. https://www.cengage.com/c/a-first-course-in-mathematical-modeling-5e-giordano/9781285050904/
3. MIT OpenCourseWare. *Introduction to Modeling and Simulation*. https://ocw.mit.edu/courses/3-021j-introduction-to-modeling-and-simulation-spring-2012/
4. MIT OpenCourseWare. *Modeling and Simulation of Dynamic Systems*. https://ocw.mit.edu/courses/2-141-modeling-and-simulation-of-dynamic-systems-fall-2006/
