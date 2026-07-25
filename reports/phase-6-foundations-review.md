# Phase 6 Foundations Scientific Review

> Review date: 2026-07-25  
> Scope: Modules 01–05, all 15 learner-facing files  
> Status transition: Draft → Reviewed  
> Release status: Not Complete; independent review and later repository-wide release gates remain required.

## Review method

Each module was reviewed across `overview.md`, `technology.md`, and `explore.md`. The pass checked:

- factual and conceptual accuracy;
- definitions and scope conditions;
- equations, symbols, units, and mathematical interpretation;
- assumptions, approximations, identification conditions, and validity domains;
- common misconceptions and counterexamples;
- system architecture, failure modes, safety, and lifecycle claims;
- safe and age-appropriate learner activities;
- canonical module links and metadata;
- direct source links against the central source ledger.

A file was marked Reviewed only after all three files in its module were revised consistently.

## Module 01 — Scientific Reasoning

### Files reviewed

- `foundations/01-scientific-reasoning/overview.md`
- `foundations/01-scientific-reasoning/technology.md`
- `foundations/01-scientific-reasoning/explore.md`

### Scientific claims corrected

- Reframed falsifiability as an important testing principle rather than a complete definition of science.
- Distinguished evidence, hypothesis, model, association, prediction, causal effect, confounding, and mechanism.
- Corrected p-value and frequentist confidence-interval interpretations.
- Removed the assumption that a regression coefficient is causal merely because `X` is labelled a causal variable.
- Added potential outcomes, estimands, consistency, exchangeability, positivity, interference, measurement validity, and model adequacy.
- Distinguished computational reproducibility from replication with new data or an independently repeated study.
- Clarified that automated causal discovery depends on structural assumptions and often returns equivalence classes rather than one proven graph.

### Equations and units checked

- Expanded the structural equation to show measured and unmeasured background factors.
- Kept the ATE definition and added a randomized-difference estimator with interpretation limits.
- Defined coefficient units and marked causal interpretation as conditional on identification.

### Safety and exploration changes

- Replaced the “unlimited resources without ethical constraints” activity with an ethically constrained study-design task.
- Removed a self-harm-related spurious-correlation example.
- Added neutral confounding simulations, reproducibility exercises, estimand specification, and sensitivity prompts.

### Remaining caveats

- Philosophies of scientific explanation remain diverse; the module introduces major distinctions rather than settling them.
- Causal inference methods require deeper mathematical treatment in later material.

## Module 02 — Measurement and Uncertainty

### Files reviewed

- `foundations/02-measurement-uncertainty/overview.md`
- `foundations/02-measurement-uncertainty/technology.md`
- `foundations/02-measurement-uncertainty/explore.md`

### Scientific claims corrected

- Aligned measurement, measurand, measurement result, error, systematic error, random error, uncertainty, accuracy, trueness, precision, resolution, and traceability with VIM/GUM terminology.
- Removed the claim that uncertainty is simply an interval or the same as measurement error.
- Corrected thermodynamic temperature: it is not generally identical to average translational kinetic energy.
- Distinguished quantum-state limitations from metrological measurement uncertainty.
- Clarified that traceability is a property of a measurement result through a documented calibration chain.
- Added dynamic response, loading, sampling, aliasing, common-cause failure, metadata, and lifecycle controls.

### Equations and units checked

- Retained mean and sample-standard-deviation equations with independence and stability conditions.
- Added the full covariance terms to first-order uncertainty propagation.
- Added expanded uncertainty `U = k u_c(y)` with reporting requirements.
- Clarified when Monte Carlo propagation is preferable to first-order linearization.

### Safety and exploration changes

- Replaced an instruction to observe a speedometer while driving with passenger or recorded observation.
- Reframed water-volume comparison so one discrepancy is not falsely assigned to one instrument.
- Added safe response-time, ruler-comparison, uncertainty-budget, and sensor-model activities.

### Remaining caveats

- Conformity assessment and decision rules near specification limits require a later dedicated treatment.
- Field-specific calibration procedures differ and are not exhaustively covered.

## Module 03 — Mathematical Models

### Files reviewed

- `foundations/03-mathematical-models/overview.md`
- `foundations/03-mathematical-models/technology.md`
- `foundations/03-mathematical-models/explore.md`

### Scientific claims corrected

- Defined models as purpose-dependent representations with explicit boundaries and validity domains.
- Distinguished state variables, parameters, inputs, outputs, residuals, sensitivity, calibration, verification, validation, and identifiability.
- Corrected vector and tensor descriptions to emphasize coordinate transformation rules.
- Clarified that mathematical form or good fit does not establish a causal mechanism.
- Treated linearization as a local Taylor approximation rather than a universally accurate simplification.
- Added model discrepancy, competing models, out-of-sample validation, extrapolation risk, and model governance.
- Reframed the square–cube law as a starting constraint rather than a complete biological explanation.
- Removed the implication that greater model fidelity automatically justifies reduced safety margins.

### Equations and units checked

- Added general state-space equations and an observation model.
- Added Jacobian-based local linearization.
- Retained the pendulum model with radians and range-of-validity notes.
- Added weighted residual calibration and non-dimensionalization concepts.

### Safety and exploration changes

- Kept pendulum work optional and safe, with a simulation alternative and a clear-area requirement.
- Added model-comparison, residual, validation, state-space, and non-dimensionalization exercises.

### Remaining caveats

- Formal identifiability, inverse problems, and multi-scale coupling require more advanced modules.
- Domain-specific constitutive laws are deferred to science modules.

## Module 04 — Probability and Statistics

### Files reviewed

- `foundations/04-probability-statistics/overview.md`
- `foundations/04-probability-statistics/technology.md`
- `foundations/04-probability-statistics/explore.md`

### Scientific claims corrected

- Distinguished probability measures, empirical frequency, conditional probability, likelihood, posterior, sampling distributions, and estimators.
- Corrected the Central Limit Theorem: convergence applies to standardized sums or means under conditions, not to raw data or every sample of a fixed size.
- Corrected p-value and frequentist confidence-interval interpretations.
- Added sampling design, assignment, missingness, dependence, clustering, multiple analysis, and selection considerations.
- Corrected the quantum statement so probability density is related to `|ψ|²`, not the wavefunction itself.
- Distinguished discrimination, calibration, and decision-weighted performance.
- Removed universal probability thresholds and causal claims based only on predictive models.
- Clarified that more data reduce some variance but do not automatically remove bias.

### Equations and units checked

- Retained probability axioms and Bayes’ theorem with conditional-probability definitions.
- Added expected value and variance.
- Replaced the finite-sample CLT equality with convergence-in-distribution notation and a qualified approximation.
- Added a generic confidence-interval form and interpretation.
- Kept regression while explicitly limiting causal interpretation.

### Safety and exploration changes

- Replaced an ambiguous medical-test example with a rare manufacturing-defect example.
- Separated prevalence, sensitivity, specificity, false-positive rate, and positive predictive value.
- Added safe activities on sampling bias, optional stopping, calibration, visualization, and confidence-interval coverage.

### Remaining caveats

- No single module can cover all frequentist, Bayesian, design-based, robust, and causal approaches.
- High-stakes decision thresholds require domain-specific consequences and governance.

## Module 05 — Computation and Algorithms

### Files reviewed

- `foundations/05-computation-algorithms/overview.md`
- `foundations/05-computation-algorithms/technology.md`
- `foundations/05-computation-algorithms/explore.md`

### Scientific claims corrected

- Distinguished algorithm, complexity, numerical method, discretization, conditioning, stability, consistency, convergence, and floating-point arithmetic.
- Separated model-form, discretization, iterative, floating-point, sampling, implementation, hardware, and interpretation errors.
- Distinguished code verification, solution verification, and validation.
- Clarified that a small residual need not imply small solution error for an ill-conditioned problem.
- Qualified CFL conditions as equation- and scheme-specific rather than universally `Δt ≤ Δx/v`.
- Qualified Monte Carlo efficiency and its `N^{-1/2}` sampling-error rate.
- Corrected the Landauer statement: the theoretical limit concerns logically irreversible information erasure, not every generic bit flip.
- Removed unstable current-performance claims and replaced them with architecture-independent metrics.
- Clarified that mesh convergence does not prove model validity.

### Equations and units checked

- Added Taylor-based finite-difference error orders.
- Corrected the composite trapezoidal-rule expression.
- Added Monte Carlo standard error and assumptions.
- Added matrix conditioning and residual definitions.
- Added resolution-scaling and floating-point cancellation examples.

### Safety and exploration changes

- Distinguished display pixels from model resolution.
- Kept browser simulations optional and prohibited unsafe security-setting changes.
- Added reproducibility, random-seed, verification-case, and validation-plan exercises.

### Remaining caveats

- Computability theory, advanced numerical linear algebra, parallel algorithms, and formal software verification require later material.
- Application-specific V&V standards are not exhaustively catalogued.

## Sources opened and ledger reconciliation

The review used the normalized Phase 5 ledger and added six exact locators required by the revised files:

- GUM official DOI;
- GUM Supplement 1 on Monte Carlo propagation;
- VIM official DOI;
- MIT OpenCourseWare dynamic-systems modelling course;
- NIST/SEMATECH Engineering Statistics Handbook;
- NIST report on simulation verification and validation.

These records are maintained in `sources/foundations-review-sources.json` and applied deterministically by `scripts/apply_foundations_review_sources.py`.

## Status result

| Module | Overview | Technology | Explore | Aggregate status |
| --- | --- | --- | --- | --- |
| 01 Scientific Reasoning | Reviewed | Reviewed | Reviewed | Reviewed |
| 02 Measurement and Uncertainty | Reviewed | Reviewed | Reviewed | Reviewed |
| 03 Mathematical Models | Reviewed | Reviewed | Reviewed | Reviewed |
| 04 Probability and Statistics | Reviewed | Reviewed | Reviewed | Reviewed |
| 05 Computation and Algorithms | Reviewed | Reviewed | Reviewed | Reviewed |

Modules 06–20 remain Draft. Reviewed does not mean Complete: independent review, synthesis reconciliation, and repository-wide release validation remain outstanding.
